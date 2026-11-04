"""Xzense fire-cycle and unsigned 16-bit state-timer accounting.

This module is independent of Home Assistant and BLE and can be regression
-tested with synthetic STATUS events. The wire timer is a 16-bit counter and
is decoded as signed int16 by the legacy protocol decoder. It counts modulo
65536; tracking across reconnects is conditional on the elapsed wall time.

A cycle starts when the last *observed* state was Ready and new STATUS
confirms active firing, or as a conservative partial cycle if already active
at startup. Afterrun is part of the same fire cycle, even when lighting is
restarted from it. A button press from Ready provides a provisional timestamp
that is only adopted after a verified active STATUS.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

TIMER_MODULUS = 65536
READY_STATE = 2
FIRING_STATES = frozenset({3, 4, 5, 6, 7})


def format_hms(seconds: int | float | None) -> str | None:
    """Convert nonnegative durations to HH:MM:SS, including >24h."""
    if seconds is None:
        return None
    total = max(0, int(seconds))
    return f"{total // 3600:02d}:{(total // 60) % 60:02d}:{total % 60:02d}"


def utc_iso(epoch: float | None) -> str | None:
    return datetime.fromtimestamp(epoch, UTC).isoformat(timespec="seconds") if epoch is not None else None


@dataclass
class XzenseTiming:
    state_id: int | None = None
    raw_unsigned: int | None = None
    state_elapsed: int | None = None
    rollovers: int = 0
    last_seen_epoch: float | None = None
    state_continuity: str = "not_observed"
    fire_started_epoch: float | None = None
    fire_duration: int = 0
    last_fire_duration: int | None = None
    fire_quality: str = "not_started"
    last_fire_quality: str | None = None
    last_fire_end_epoch: float | None = None
    pending_ready_start_epoch: float | None = None

    @classmethod
    def restore(cls, data: dict[str, Any]) -> "XzenseTiming":
        """Read only the known schema; malformed/missing state is ignored."""
        valid = {name for name in cls.__dataclass_fields__}
        try:
            restored = cls(**{k: v for k, v in data.items() if k in valid})
            if restored.raw_unsigned is not None and not 0 <= restored.raw_unsigned < TIMER_MODULUS:
                return cls()
            if restored.state_elapsed is not None and restored.state_elapsed < 0:
                return cls()
            if restored.last_seen_epoch is not None and restored.last_seen_epoch <= 0:
                return cls()
            return restored
        except (TypeError, ValueError):
            return cls()

    def snapshot(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in self.__dataclass_fields__}

    def note_start_request(self, at_epoch: float) -> None:
        """Remember a Ready->start button press, without starting an unverified fire."""
        if self.state_id == READY_STATE:
            self.pending_ready_start_epoch = at_epoch

    def cancel_start_request(self) -> None:
        """Discard provisional timestamp if sending fails or controller NACKs."""
        self.pending_ready_start_epoch = None

    def observe(self, device_state: int, signed_timer: int, at_epoch: float) -> bool:
        """Ingest verified STATUS; return True for major cycle/state transitions.

        For the same state across a long gap, infer complete modulo wraps only
        when the counter delta agrees with wall elapsed time. Otherwise, reset
        conservatively and mark continuity uncertain. A long observation gap
        can conceal complete fire cycles even if the state is unchanged.
        """
        raw = signed_timer & 0xFFFF
        old_state = self.state_id
        old_raw = self.raw_unsigned
        old_epoch = self.last_seen_epoch
        previous_elapsed = self.state_elapsed
        gap = None if old_epoch is None else max(0.0, at_epoch - old_epoch)
        changed = old_state != device_state

        if changed or old_raw is None or previous_elapsed is None or gap is None:
            self.state_elapsed = raw
            self.rollovers = 0
            self.state_continuity = "new_state" if changed else "initial"
        else:
            modulo_delta = (raw - old_raw) % TIMER_MODULUS
            # Find the number of additional complete turns consistent with
            # elapsed wall time; never infer them solely from raw delta.
            wraps = max(0, round((gap - modulo_delta) / TIMER_MODULUS))
            delta = modulo_delta + wraps * TIMER_MODULUS
            tolerance = max(25.0, min(120.0, gap * 0.02))
            if abs(delta - gap) <= tolerance and (gap <= 0 or delta < gap + tolerance):
                self.state_elapsed = previous_elapsed + delta
                self.rollovers = self.state_elapsed // TIMER_MODULUS
                self.state_continuity = "observed" if gap <= 40 else "inferred_across_gap"
            else:
                self.state_elapsed = raw
                self.rollovers = 0
                self.state_continuity = "timer_reset_or_missed_transition"

        self.state_id = device_state
        self.raw_unsigned = raw
        self.last_seen_epoch = at_epoch

        was_firing = old_state in FIRING_STATES
        is_firing = device_state in FIRING_STATES
        # Do not trust a pending button press indefinitely across lost sessions.
        button_start = self.pending_ready_start_epoch
        if button_start is not None and (button_start > at_epoch + 5 or
                                         at_epoch - button_start > 900):
            button_start = None
            self.pending_ready_start_epoch = None

        if old_state == READY_STATE and is_firing:
            # Read the counter *only* to infer start across Ready -> active.
            # Stage 3 gives the ignition time; stage 4 can follow an unobserved
            # Boosting phase, so its timer is merely a lower-bound estimate.
            timer_start = at_epoch - raw
            plausible_timer = (gap is not None and
                               timer_start >= old_epoch - 25 and
                               raw <= gap + 25)
            valid_button = (button_start is not None and old_epoch is not None and
                            old_epoch - 5 <= button_start <= at_epoch)
            if device_state == 3 and plausible_timer:
                start = max(old_epoch, timer_start)
                quality = "inferred_ready_boost_timer" if gap > 40 else "observed_start"
            elif valid_button:
                start = button_start
                quality = "confirmed_from_ready_button"
            elif plausible_timer and device_state in {4, 7}:
                start = max(old_epoch, timer_start)
                quality = "estimated_from_operation_timer"
            else:
                start = at_epoch
                quality = "partial_observation"
            self.fire_started_epoch = start
            self.fire_duration = max(0, int(at_epoch - start))
            self.fire_quality = quality
            self.pending_ready_start_epoch = None
        elif is_firing and not was_firing:
            # Unknown first state (or an uncaught transition). Do not claim
            # precise start without a previously observed Ready.
            if self.fire_started_epoch is None:
                self.fire_started_epoch = at_epoch
                self.fire_quality = "partial_observation"
            self.fire_duration = max(0, int(at_epoch - self.fire_started_epoch))
            self.pending_ready_start_epoch = None
        elif device_state == READY_STATE and old_state != READY_STATE:
            # Afterrun -> Ready ends the same session; other active -> Ready
            # also indicates completion. Never split on Afterrun -> Boosting.
            if self.fire_started_epoch is not None:
                self.fire_duration = max(0, int(at_epoch - self.fire_started_epoch))
                self.last_fire_duration = self.fire_duration
                self.last_fire_quality = self.fire_quality
                if gap is not None and gap > 40:
                    self.last_fire_quality = "estimated_end_after_gap"
                self.last_fire_end_epoch = at_epoch
            self.fire_started_epoch = None
            self.fire_duration = 0
            self.fire_quality = "not_active"
            self.pending_ready_start_epoch = None
        elif is_firing:
            # This includes Afterrun -> Boosting/Operation/Refuel: same fire.
            if self.fire_started_epoch is None:
                self.fire_started_epoch = at_epoch
                self.fire_quality = "partial_observation"
            self.fire_duration = max(0, int(at_epoch - self.fire_started_epoch))
            if gap is not None and gap > 40 and self.fire_quality == "observed_start":
                self.fire_quality = "estimated_after_gap"
        elif device_state == READY_STATE:
            self.fire_duration = 0
            self.fire_started_epoch = None
            self.fire_quality = "not_active"
            # The panel may still be Ready immediately after a valid BOOST ACK;
            # hold the provisional timestamp until active, timeout, or NACK.
        elif self.fire_started_epoch is not None:
            # Unknown/intermediate states do not finalize a cycle. Only Ready
            # is a reliable cycle boundary in the requested workflow.
            self.fire_duration = max(0, int(at_epoch - self.fire_started_epoch))
        else:
            self.fire_duration = 0
            self.fire_quality = "not_active"

        return changed or self.state_continuity == "timer_reset_or_missed_transition"
