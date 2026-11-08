"""Bluetooth client for Xzense."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Awaitable
from dataclasses import asdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
import logging
import time

from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store

from .const import (
    BOOST_WRITES_ENABLED,
    CONTROL_WRITES_ENABLED,
    NOTIFY_UUID,
    WRITE_UUID,
    VENTILATION_WRITES_ENABLED,
)
from .features import FEATURE_BY_KEY
from .proxy_selection import rank_proxy_candidates
from .timing import XzenseTiming, format_hms
from .protocol import (
    XzenseStatusData,
    PACKET_BOOST,
    PACKET_GLOBAL,
    PACKET_STATUS,
    PACKET_VENTILATION,
    PROTOCOL_ACK,
    PROTOCOL_NACK,
    XzenseFrame,
    XzenseFrameParser,
    XzenseStatusData,
    build_boost_request,
    build_connect_request,
    build_global_request,
    build_status_request,
    build_ventilation_request,
    decode_global_data,
    decode_status_data,
    global_name,
)

_LOGGER = logging.getLogger(__name__)

Listener = Callable[[], None]

NOTIFY_TIMEOUT = 10.0
ADVERTISEMENT_WAIT_TIMEOUT = 45.0
ADAPTER_COLLECTION_WINDOW = 3.0  # conservative window, unchanged
FAST_ADAPTER_COLLECTION_WINDOW = 0.8
FAST_ADAPTER_MIN_RSSI = -75  # only an already successful, strong source

RECENT_SOURCE_FAILURE_SECONDS = 120.0
CACHED_SOURCE_SCAN_SECONDS = 3.0  # short live scan before per-scanner cache fallback
DISCONNECT_HISTORY_LIMIT = 20
APPLICATION_CLIENT_NAME = "HomeAssistant"

# Bounded multi-proxy fallback: try a source once per connection round.
# Do not continuously reconnect on a failed source: periodic scheduling and
# 120s cache cooldown stay in effect.
MAX_SOURCE_ATTEMPTS_PER_ROUND = 6
STATUS_POLL_INTERVAL = 10.0
PACKET_HISTORY_LIMIT = 20

# Hybrid / on-demand mode. 0 = original continuously connected behaviour.
DEFAULT_UPDATE_INTERVAL_MINUTES = 5
DEFAULT_ACTIVE_INTERVAL_SECONDS = 0
ACTIVE_STATES = frozenset({3, 4, 5, 6, 7, 8})  # includes ventilation
COMMAND_HOLD_SECONDS = 15.0
SNAPSHOT_WAIT_SECONDS = 12.0
APPLICATION_AUTH_TIMEOUT = 12.0



def _utc_now() -> str:
    """Return an ISO-8601 UTC timestamp for diagnostics."""
    return datetime.now(UTC).isoformat(timespec="milliseconds")


@dataclass(slots=True)
class _BleSourceCandidate:
    """A source-specific BLEDevice with an RSSI and provenance.

    Fresh raw advertisements and per-adapter HA cache records use the same
    connection path. Do not cache these BLEDevice handles across attempts.
    """

    source: str
    rssi: int
    device: object
    origin: str  # fresh_raw_advertisement | per_scanner_cache


@dataclass(slots=True)
class XzenseState:
    """Runtime state for Xzense Bluetooth, telemetry and controls."""

    connected: bool = False
    ble_link_connected: bool = False
    notifications_active: bool = False
    phase: str = "idle"
    phase_changed_at: str | None = None
    ble_connected_at: str | None = None
    notify_started_at: str | None = None
    notify_active_at: str | None = None
    last_notification_at: str | None = None
    last_disconnect_at: str | None = None

    # Alpha 0.5.15: per-BLE-session tracking (no claims about remote initiator).
    active_session_source: str | None = None
    active_session_rssi: int | None = None
    preferred_source: str | None = None
    last_successful_source: str | None = None
    last_disconnect_source: str | None = None
    last_disconnect_kind: str | None = None
    last_disconnect_session_seconds: float | None = None
    last_disconnect_authenticated: bool | None = None
    last_disconnect_last_status_request_at: str | None = None
    last_disconnect_last_status_response_at: str | None = None
    disconnect_history: list[dict[str, object]] = field(default_factory=list)

    packet_count: int = 0
    notification_count: int = 0
    last_notification: bytes = b""
    last_frame: XzenseFrame | None = None
    last_error: str | None = None
    discarded_bytes: int = 0
    invalid_frames: int = 0
    crc_errors: int = 0
    connection_attempts: int = 0
    disconnect_count: int = 0

    # Fresh-advertisement connection diagnostics (v0.2.5+).
    advertisement_count: int = 0
    advertisement_waits: int = 0
    advertisement_timeouts: int = 0
    last_advertisement_at: str | None = None
    last_advertisement_rssi: int | None = None
    last_advertisement_source: str | None = None
    last_advertisement_name: str | None = None
    last_advertisement_connectable: bool | None = None

    # Multi-adapter/source selection diagnostics (v0.2.6).
    candidate_source_count: int = 0
    candidate_sources: str = ""
    selected_source: str | None = None
    selected_source_rssi: int | None = None
    source_connection_attempts: int = 0
    source_fallbacks: int = 0
    last_failed_source: str | None = None
    source_discovery_method: str | None = None
    candidate_details: list[dict[str, object]] = field(default_factory=list)
    fresh_scanner_count: int = 0
    cached_scanner_count: int = 0
    cached_sources_without_fresh_count: int = 0

    # Kept for backwards-compatible diagnostics while BLE pairing is disabled.
    pairing_attempts: int = 0
    pairing_success: bool = False
    pairing_last_error: str | None = None
    authorization_retries: int = 0

    # TX/application session diagnostics (v0.2.7).
    tx_count: int = 0
    tx_chunk_count: int = 0
    last_tx: bytes = b""
    last_tx_at: str | None = None
    tx_write_mode: str | None = None
    tx_chunk_size: int | None = None

    application_auth_state: str = "not_started"
    application_connect_attempts: int = 0
    application_auth_success_count: int = 0
    handshake_sent_at: str | None = None
    handshake_response_at: str | None = None
    handshake_last_error: str | None = None
    session_id: int | None = None
    connect_ack_version: int | None = None
    connect_ack_flag: int | None = None

    # Read-only live status polling (v0.3.0).
    status_polling_active: bool = False
    status_request_count: int = 0
    status_response_count: int = 0
    status_nack_count: int = 0
    status_request_errors: int = 0
    last_status_request_at: str | None = None
    last_status_response_at: str | None = None
    last_status_payload: bytes = b""
    status: XzenseStatusData | None = None

    # Alpha 0.5.16: monotonic logical timer/cycle (persisted in HA .storage).
    state_timer_unsigned_raw: int | None = None
    state_timer_elapsed_seconds: int | None = None
    state_timer_display: str | None = None
    state_timer_rollovers: int = 0
    state_timer_continuity: str = "not_observed"
    state_timer_observed_at: str | None = None
    fire_duration_seconds: int = 0
    fire_duration_display: str = "00:00:00"
    fire_started_at: str | None = None
    fire_quality: str = "not_started"
    last_fire_duration_seconds: int | None = None
    last_fire_quality: str | None = None

    # GLOBAL/DATA cache. Reads are passive; control writes remain safety-gated.
    globals: dict[int, int] = field(default_factory=dict)
    global_update_count: int = 0
    last_global_id: int | None = None
    last_global_name: str | None = None
    last_global_value: int | None = None
    last_global_at: str | None = None

    # Write diagnostics. Normal GLOBAL setting writes stay gated; v0.4.4 enables
    # only the firmware-recovered BOOST packet as a live test.
    global_write_request_count: int = 0
    global_write_ack_count: int = 0
    global_write_nack_count: int = 0
    last_global_write_id: int | None = None
    last_global_write_value: int | None = None
    last_global_write_request_at: str | None = None
    last_global_write_response: str | None = None
    last_global_write_response_at: str | None = None
    boost_request_count: int = 0
    boost_ack_count: int = 0
    boost_nack_count: int = 0
    last_boost_action: str | None = None
    last_boost_request_at: str | None = None
    last_boost_response: str | None = None
    last_boost_response_at: str | None = None
    ventilation_request_count: int = 0
    ventilation_ack_count: int = 0
    ventilation_nack_count: int = 0
    last_ventilation_action: str | None = None
    last_ventilation_request_at: str | None = None
    last_ventilation_response: str | None = None
    last_ventilation_response_at: str | None = None
    ventilation_pending_value: bool | None = None
    ventilation_is_on: bool | None = None
    boost_is_on: bool | None = None
    last_mode_status_at: str | None = None

    # Short validated-frame history for diagnostics/reverse engineering.
    packet_history: list[dict[str, object]] = field(default_factory=list)
    last_tx_kind: str | None = None

    # 0.5.19 hybrid transport diagnostics. Cached values are explicitly stale.
    last_data_at: str | None = None
    update_interval_minutes: float = DEFAULT_UPDATE_INTERVAL_MINUTES  # effective, compatibility
    update_interval_seconds: int = DEFAULT_UPDATE_INTERVAL_MINUTES * 60
    idle_update_interval_minutes: int = DEFAULT_UPDATE_INTERVAL_MINUTES
    active_update_interval_seconds: int = DEFAULT_ACTIVE_INTERVAL_SECONDS
    active_update_interval_minutes: float = 0.0  # legacy diagnostic compatibility
    interval_profile: str = "idle"
    periodic_poll_count: int = 0
    local_periodic_disconnect_count: int = 0
    fast_connect_attempts: int = 0
    fast_connect_fallbacks: int = 0
    adaptive_short_window_count: int = 0
    adaptive_full_window_count: int = 0
    adaptive_fallbacks: int = 0
    adapter_collection_last_seconds: float | None = None
    pending_commands: int = 0
    last_command_at: str | None = None
    next_poll_at: str | None = None


class XzenseClient:
    """Maintain the BLE/app session and read live Xzense status.

    The client preserves the fresh-advertisement connection strategy and recovered
    CONNECT/PIN handshake proven on the real controller. After CONNECT/ACK it
    sends the official read-only STATUS/REQ every 10 seconds. v0.4.1 introduced the
    live 14-byte STATUS/ACK decoder; v0.4.2 calibrated fan speed and temperature
    positions. v0.4.3 confirms state timer and air pressure. v0.4.4 removes the
    earlier generic write probes and adds the firmware-recovered BOOST on/off
    request. Alpha 0.5.6 adds only application-level firing/ventilation actions
    and keeps the proven BLE connection/reconnect/session path unchanged.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        address: str,
        name: str,
        pin: str,
    ) -> None:
        self.hass = hass
        self.entry = entry
        self.address = address
        self.name = name
        self.pin = pin
        # Local HA-only motor selection. Must never write a voltage to the
        # controller just because the user enables this restriction.
        self._rs009_41_motor = bool(entry.options.get("rs009_41_motor", False))
        self.state = XzenseState()
        self._parser = XzenseFrameParser()
        self._listeners: set[Listener] = set()
        self._status_listeners: set[Callable[[int], None]] = set()
        self._client: BleakClientWithServiceCache | None = None
        self._runner: asyncio.Task[None] | None = None
        self._status_runner: asyncio.Task[None] | None = None
        self._wake = asyncio.Event()
        self._session_ready = asyncio.Event()
        self._tx_lock = asyncio.Lock()
        self._stopping = False
        self._preferred_source: str | None = None
        self._source_failure_at: dict[str, float] = {}
        self._last_scan_was_adaptive = False
        self._planned_disconnects: dict[int, str] = {}
        self._active_ble_started_monotonic: float | None = None
        self._timing = XzenseTiming()
        self._timing_store: Store[dict[str, object]] = Store(
            hass, 1, f"xzense.timing_{entry.entry_id}"
        )
        self._last_timing_save_schedule = 0.0
        # Preserve old option/unique ID for the idle slider when upgrading.
        idle_option = entry.options.get(
            "idle_update_interval_minutes",
            entry.options.get("update_interval_minutes", DEFAULT_UPDATE_INTERVAL_MINUTES),
        )
        # The previous release stored the active interval in minutes.  Only
        # convert that legacy option on upgrade; the new setting uses seconds.
        old_active_minutes = entry.options.get("active_update_interval_minutes", 0)
        if "active_update_interval_seconds" in entry.options:
            active_option = entry.options["active_update_interval_seconds"]
        else:
            try:
                active_option = int(old_active_minutes) * 60
            except (TypeError, ValueError):
                active_option = DEFAULT_ACTIVE_INTERVAL_SECONDS
        try:
            self.idle_interval_minutes = max(0, min(120, int(idle_option)))
        except (TypeError, ValueError):
            self.idle_interval_minutes = DEFAULT_UPDATE_INTERVAL_MINUTES
        try:
            self.active_interval_seconds = max(0, min(600, int(active_option)))
        except (TypeError, ValueError):
            self.active_interval_seconds = DEFAULT_ACTIVE_INTERVAL_SECONDS
        self.state.idle_update_interval_minutes = self.idle_interval_minutes
        self.state.active_update_interval_seconds = self.active_interval_seconds
        self.state.active_update_interval_minutes = self.active_interval_seconds / 60
        self._update_effective_interval()
        self._next_poll_monotonic = 0.0
        self._connect_requested = False
        self._pending_commands = 0
        self._keep_connected_until = 0.0
        self._fresh_status_event = asyncio.Event()
        self._command_lock = asyncio.Lock()
        self._cache_store: Store[dict[str, object]] = Store(
            hass, 1, f"xzense.cache_{entry.entry_id}"
        )

    @callback
    def async_add_listener(self, listener: Listener) -> Callable[[], None]:
        self._listeners.add(listener)

        @callback
        def remove_listener() -> None:
            self._listeners.discard(listener)

        return remove_listener

    @callback
    def async_add_status_listener(
        self, listener: Callable[[int], None]
    ) -> Callable[[], None]:
        """Observe valid live STATUS device codes; excludes restored cache."""
        self._status_listeners.add(listener)

        @callback
        def remove_listener() -> None:
            self._status_listeners.discard(listener)

        return remove_listener

    @callback
    def _notify_listeners(self) -> None:
        for listener in tuple(self._listeners):
            listener()

    @property
    def rs009_41_motor(self) -> bool:
        return self._rs009_41_motor

    async def async_set_rs009_41_motor(self, enabled: bool) -> None:
        """Persist local voltage UI bounds without touching Bluetooth."""
        from .const import CONF_RS009_41_MOTOR
        self._rs009_41_motor = bool(enabled)
        self.hass.config_entries.async_update_entry(
            self.entry, options={**self.entry.options, CONF_RS009_41_MOTOR: self._rs009_41_motor}
        )
        self._notify_listeners()

    def _set_phase(self, phase: str) -> None:
        """Update the connection phase and expose it immediately."""
        if self.state.phase == phase:
            return
        self.state.phase = phase
        self.state.phase_changed_at = _utc_now()
        _LOGGER.debug("Xzense %s phase: %s", self.address, phase)
        self._notify_listeners()

    async def async_initialize_timing(self) -> None:
        """Load prior verified timer/cycle checkpoints before BLE starts."""
        try:
            saved = await self._timing_store.async_load()
            if isinstance(saved, dict):
                self._timing = XzenseTiming.restore(saved)
                self._sync_timing_state()
        except Exception:
            _LOGGER.warning("Unable to restore saved Xzense timing state", exc_info=True)

    async def async_initialize_cache(self) -> None:
        """Restore last verified data for offline display after HA restart."""
        try:
            saved = await self._cache_store.async_load()
            if not isinstance(saved, dict):
                return
            self.state.globals = {
                int(k): int(v) for k, v in saved.get("globals", {}).items()
            }
            status = saved.get("status")
            if isinstance(status, dict) and isinstance(status.get("raw"), str):
                payload = dict(status)
                payload["raw"] = bytes.fromhex(payload["raw"])
                if len(payload["raw"]) == 14:
                    self.state.status = XzenseStatusData(**payload)
            self.state.last_data_at = saved.get("last_data_at")
            self.state.last_status_response_at = saved.get("last_status_response_at")
            self.state.last_global_at = saved.get("last_global_at")
            self.state.connect_ack_version = saved.get("connect_ack_version")
            self.state.boost_is_on = saved.get("boost_is_on")
            self.state.ventilation_is_on = saved.get("ventilation_is_on")
            self._notify_listeners()
        except (ValueError, TypeError, KeyError, OSError):
            _LOGGER.warning("Unable to restore Xzense cached values", exc_info=True)

    def _cache_snapshot(self) -> dict[str, object]:
        """No PIN, BLE address, session ID or connection state is persisted."""
        status = asdict(self.state.status) if self.state.status else None
        if status is not None:
            status["raw"] = status["raw"].hex()
        return {
            "status": status,
            "globals": {str(k): v for k, v in self.state.globals.items()},
            "last_data_at": self.state.last_data_at,
            "last_status_response_at": self.state.last_status_response_at,
            "last_global_at": self.state.last_global_at,
            "connect_ack_version": self.state.connect_ack_version,
            "boost_is_on": self.state.boost_is_on,
            "ventilation_is_on": self.state.ventilation_is_on,
        }

    def _save_cache_soon(self) -> None:
        self._cache_store.async_delay_save(self._cache_snapshot, 15.0)

    @property
    def interval_minutes(self) -> float:
        """Effective interval in minutes; fractional for active second intervals."""
        return (self.active_interval_seconds / 60 if self._is_active_state() else
                self.idle_interval_minutes)

    @property
    def interval_seconds(self) -> int:
        """Exact effective scheduling interval (0 = continuous)."""
        return (self.active_interval_seconds if self._is_active_state() else
                self.idle_interval_minutes * 60)

    def _is_active_state(self) -> bool:
        # Cached status is useful for choosing the next interval across
        # disconnects, but verified STATUS always refreshes it on reconnect.
        return self.current_device_state() in ACTIVE_STATES

    def _update_effective_interval(self) -> bool:
        """Publish active/idle profile, and wake manager on a mode transition."""
        active = self._is_active_state()
        seconds = self.active_interval_seconds if active else self.idle_interval_minutes * 60
        changed = (self.state.update_interval_seconds != seconds or
                   self.state.interval_profile != ("active" if active else "idle"))
        self.state.interval_profile = "active" if active else "idle"
        self.state.update_interval_seconds = seconds
        self.state.update_interval_minutes = seconds / 60
        if changed:
            self._next_poll_monotonic = 0.0
            self.state.next_poll_at = None
            self._wake.set()
        return changed

    async def async_set_interval(self, value: int, *, active: bool = False) -> None:
        """Update idle in minutes (0–120) or active in seconds (0–600)."""
        limit = 600 if active else 120
        unit = "seconds" if active else "minutes"
        if not 0 <= value <= limit:
            raise HomeAssistantError(f"Bluetooth interval must be 0–{limit} {unit}")
        attr = "active_interval_seconds" if active else "idle_interval_minutes"
        if getattr(self, attr) == value:
            return
        setattr(self, attr, value)
        self.state.active_update_interval_seconds = self.active_interval_seconds
        self.state.active_update_interval_minutes = self.active_interval_seconds / 60
        self.state.idle_update_interval_minutes = self.idle_interval_minutes
        effective_changed = self._update_effective_interval()
        key = "active_update_interval_seconds" if active else "idle_update_interval_minutes"
        options = {**self.entry.options, key: value}
        if not active:
            options["update_interval_minutes"] = value  # backwards-compatible option
        self.hass.config_entries.async_update_entry(self.entry, options=options)
        if effective_changed:
            self._wake.set()
        self._notify_listeners()

    @property
    def controls_available(self) -> bool:
        """Offline controls can request a connection in periodic mode."""
        return not self._stopping and (
            self.interval_minutes > 0 or self.state.application_auth_state == "connected"
        )

    async def async_run_control(self, action: Callable[[], Awaitable[None]]) -> None:
        """Serialize on-demand commands; never replay a write after an uncertain ACK."""
        self._pending_commands += 1
        self.state.pending_commands = self._pending_commands
        self._wake.set()
        try:
            async with self._command_lock:
                if self.interval_minutes > 0 and not self._session_ready.is_set():
                    self._connect_requested = True
                    self._wake.set()
                    try:
                        await asyncio.wait_for(self._session_ready.wait(), timeout=65.0)
                    except TimeoutError as err:
                        raise HomeAssistantError("Xzense connection timed out; no command sent") from err
                if not self._session_ready.is_set() or not self._client or not self._client.is_connected:
                    raise HomeAssistantError("Xzense is not authenticated; no command sent")
                # Before acting on a possibly stale mode/temperature, demand one
                # fresh verified STATUS when a new on-demand session was opened.
                if self.interval_minutes > 0 and not self._fresh_status_event.is_set():
                    try:
                        await asyncio.wait_for(self._fresh_status_event.wait(), timeout=SNAPSHOT_WAIT_SECONDS)
                    except TimeoutError as err:
                        raise HomeAssistantError("Xzense did not return fresh status; no command sent") from err
                await action()
                self.state.last_command_at = _utc_now()
        finally:
            self._pending_commands -= 1
            if self._pending_commands == 0:
                self._connect_requested = False
            self.state.pending_commands = self._pending_commands
            self._keep_connected_until = time.monotonic() + COMMAND_HOLD_SECONDS
            self._wake.set()
            self._notify_listeners()

    async def async_control_feature(self, feature_key: str, value: object | None = None) -> None:
        """Dispatch existing firmware-verified commands after authentication."""
        # Capture HA button dispatch time *before* waiting for an on-demand
        # Bluetooth session. Do not treat it as a fire start until verified.
        requested_at = time.time() if feature_key == "start_fire" else None
        async def _execute() -> None:
            if feature_key in {"start_fire", "refuel"}:
                state = self.current_device_state()
                if state not in ({2, 6} if feature_key == "start_fire" else {5}):
                    raise HomeAssistantError("Xzense state changed; action not allowed")
                if feature_key == "start_fire" and state == 2:
                    assert requested_at is not None
                    self._timing.note_start_request(requested_at)
                    self._timing_store.async_delay_save(self._timing.snapshot, 1.0)
                try:
                    await self.async_set_boost(True)
                except Exception:
                    if feature_key == "start_fire" and state == 2:
                        self._timing.cancel_start_request()
                    raise
            elif feature_key == "stop_fire":
                state = self.current_device_state()
                if state in {3, 7}:
                    await self.async_set_boost(False)
                elif state in {4, 5}:
                    await self.async_execute_feature("stop_fire", 6)
                else:
                    raise HomeAssistantError("Stop firing is not valid in current state")
            elif feature_key == "boost":
                await self.async_set_boost(bool(value))
            elif feature_key == "ventilation":
                await self.async_set_ventilation(bool(value))
            else:
                await self.async_execute_feature(feature_key, value)
        await self.async_run_control(_execute)

    def _sync_timing_state(self) -> None:
        from .timing import utc_iso
        track = self._timing
        state = self.state
        state.state_timer_unsigned_raw = track.raw_unsigned
        state.state_timer_elapsed_seconds = track.state_elapsed
        state.state_timer_display = format_hms(track.state_elapsed)
        state.state_timer_rollovers = track.rollovers
        state.state_timer_continuity = track.state_continuity
        state.state_timer_observed_at = utc_iso(track.last_seen_epoch)
        state.fire_duration_seconds = track.fire_duration
        state.fire_duration_display = format_hms(track.fire_duration) or "00:00:00"
        state.fire_started_at = utc_iso(track.fire_started_epoch)
        state.fire_quality = track.fire_quality
        state.last_fire_duration_seconds = track.last_fire_duration
        state.last_fire_quality = track.last_fire_quality

    def _update_timing(self, device_state: int, raw_timer: int) -> None:
        important = self._timing.observe(device_state, raw_timer, time.time())
        self._sync_timing_state()
        self._update_effective_interval()
        now = time.monotonic()
        # Schedule checkpoints without resetting the deadline on each
        # 10-second status notification. On state transitions save promptly.
        if important or now - self._last_timing_save_schedule >= 30.0:
            self._timing_store.async_delay_save(self._timing.snapshot, 1.0 if important else 15.0)
            self._last_timing_save_schedule = now

    async def async_start(self) -> None:
        """Start the connection manager without blocking config-entry setup."""
        if self._runner and not self._runner.done():
            return
        self._stopping = False
        self._set_phase("starting")
        self._runner = self.entry.async_create_background_task(
            self.hass, self._connection_loop(), f"xzense-{self.address}"
        )
        self._status_runner = self.entry.async_create_background_task(
            self.hass, self._status_loop(), f"xzense-status-{self.address}"
        )

    async def async_stop(self) -> None:
        """Stop reconnects, notifications and the BLE connection."""
        self._stopping = True
        self._wake.set()
        self._session_ready.clear()

        runner = self._runner
        self._runner = None
        if runner:
            runner.cancel()
            try:
                await runner
            except asyncio.CancelledError:
                pass

        status_runner = self._status_runner
        self._status_runner = None
        self._session_ready.clear()
        if status_runner:
            status_runner.cancel()
            try:
                await status_runner
            except asyncio.CancelledError:
                pass

        client = self._client
        self._client = None
        if client and client.is_connected:
            if self.state.notifications_active:
                try:
                    await client.stop_notify(NOTIFY_UUID)
                except Exception:  # best-effort during unload
                    pass
            self._planned_disconnects[id(client)] = "local_shutdown"
            try:
                await client.disconnect()
            except Exception:  # best-effort during unload
                pass

        self.state.connected = False
        self.state.ble_link_connected = False
        self.state.notifications_active = False
        try:
            await self._timing_store.async_save(self._timing.snapshot())
            await self._cache_store.async_save(self._cache_snapshot())
        except Exception:
            _LOGGER.warning("Unable to persist Xzense timing state", exc_info=True)
        self._set_phase("stopped")
        self._notify_listeners()

    async def _connection_loop(self) -> None:
        """Switch modes without restarting HA; continuous uses the 0.5.17 loop."""
        try:
            while not self._stopping:
                if self.interval_minutes == 0:
                    await self._continuous_connection_loop()
                else:
                    await self._periodic_connection_loop()
                # Scheduling boundary: prevents a CPU spin if a mode changes
                # while a sub-loop returns early on disconnect/state changes.
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            raise

    async def _continuous_connection_loop(self) -> None:
        """Original 0.5.17 reconnection mechanism, unchanged in continuous mode."""
        try:
            while not self._stopping and self.interval_minutes == 0:
                if not self._client or not self._client.is_connected:
                    connected = await self._connect_once()
                    if not connected:
                        # A failed cached connection must not cause tight
                        # reconnect loops that overload the HA event loop.
                        self._wake.clear()
                        try:
                            await asyncio.wait_for(self._wake.wait(), timeout=10.0)
                        except TimeoutError:
                            pass
                        continue

                # Do not lose a disconnect callback fired while CONNECT/REQ was
                # still being sent. It may have set _wake before this loop.
                if not self._client or not self._client.is_connected:
                    continue
                # A pending wake may belong to a disconnect callback that
                # arrived during CONNECT/REQ. If the client remains connected,
                # consume the stale wake before awaiting the next event.
                # NEVER `continue` merely because _wake is set: that creates
                # a synchronous busy loop which starves Home Assistant's
                # shared asyncio event loop and can freeze all of HA.
                self._wake.clear()
                # Guard against a disconnect in the short window above: its
                # callback sets _wake again, so the wait exits immediately.
                if not self._client or not self._client.is_connected:
                    continue
                if self.interval_minutes > 0:
                    return  # STATUS switched active -> Ready; periodic loop releases BLE
                await self._wake.wait()
        except asyncio.CancelledError:
            raise

    async def _periodic_connection_loop(self) -> None:
        """Take a single fresh snapshot, release BLE, sleep until next interval.

        Every sleep awaits asyncio: never spin on a set wake flag (0.5.15 bug).
        """
        try:
            while not self._stopping and self.interval_minutes > 0:
                client = self._client
                if not client or not client.is_connected:
                    seconds = self._next_poll_monotonic - time.monotonic()
                    if seconds > 0 and not self._connect_requested:
                        self._set_phase("periodic_sleep")
                        self._wake.clear()
                        try:
                            await asyncio.wait_for(self._wake.wait(), timeout=seconds)
                        except TimeoutError:
                            pass
                        continue

                    fast = bool(self._connect_requested)
                    connected = await self._connect_once(fast=fast)
                    if not connected:
                        # Bounded retry delay: no CPU-saturating reconnect spin.
                        self._next_poll_monotonic = time.monotonic() + 10.0
                        await asyncio.sleep(1.0)
                        continue
                    self._connect_requested = False
                    client = self._client
                    self.state.periodic_poll_count += 1
                    self._notify_listeners()

                if not client or not client.is_connected:
                    await asyncio.sleep(0.2)
                    continue

                # The authenticated application session and status response
                # must be new; never use restored/cached STATUS to decide expiry.
                try:
                    await asyncio.wait_for(self._session_ready.wait(), timeout=APPLICATION_AUTH_TIMEOUT)
                    await asyncio.wait_for(self._fresh_status_event.wait(), timeout=SNAPSHOT_WAIT_SECONDS)
                except TimeoutError:
                    _LOGGER.warning("Xzense periodic session timed out waiting for authentication/STATUS")

                # Give GLOBAL/DATA messages time to arrive after initial STATUS.
                settle_until = time.monotonic() + 2.0
                while (not self._stopping and self.interval_minutes > 0 and
                       client is self._client and client.is_connected):
                    deadline = max(settle_until, self._keep_connected_until)
                    if self._pending_commands == 0 and time.monotonic() >= deadline:
                        break
                    await asyncio.sleep(0.25)

                if self._stopping or self.interval_minutes == 0:
                    return
                if client is self._client and client.is_connected:
                    self._planned_disconnects[id(client)] = "local_periodic_poll"
                    try:
                        await client.disconnect()
                    except Exception:
                        _LOGGER.debug("Xzense periodic release failed", exc_info=True)
                    if self._client is client:
                        # Bleak does not guarantee callback ordering; retire
                        # the client even when a callback arrives late.
                        self._client = None
                        self.state.connected = False
                        self.state.ble_link_connected = False
                        self.state.notifications_active = False
                        self._session_ready.clear()
                        self.state.application_auth_state = "disconnected_after_ack"
                    self.state.local_periodic_disconnect_count += 1
                self._next_poll_monotonic = time.monotonic() + self.interval_seconds
                self.state.next_poll_at = datetime.fromtimestamp(
                    time.time() + self.interval_seconds, UTC
                ).isoformat(timespec="seconds")
                self._notify_listeners()
        except asyncio.CancelledError:
            raise

    def _record_advertisement(
        self, service_info: bluetooth.BluetoothServiceInfoBleak
    ) -> None:
        """Record a live Xzense advertisement for diagnostics."""
        self.state.advertisement_count += 1
        self.state.last_advertisement_at = _utc_now()
        self.state.last_advertisement_rssi = service_info.rssi
        self.state.last_advertisement_source = service_info.source
        self.state.last_advertisement_name = service_info.name
        self.state.last_advertisement_connectable = service_info.connectable
        _LOGGER.debug(
            "Fresh Xzense advertisement #%d from %s: RSSI=%s source=%s connectable=%s",
            self.state.advertisement_count,
            self.address,
            service_info.rssi,
            service_info.source,
            service_info.connectable,
        )
        # A stream of raw advertisements must not cause every HA entity to
        # rewrite its state. Selected source and RSSI are published at the end
        # of the collection round (or via a later phase update).

    @staticmethod
    def _source_key(service_info: bluetooth.BluetoothServiceInfoBleak) -> str:
        """Return a stable source key for one HA Bluetooth adapter/proxy."""
        return service_info.source or "unknown"

    @staticmethod
    def _rssi_value(service_info: bluetooth.BluetoothServiceInfoBleak) -> int:
        """Normalize an optional RSSI for deterministic sorting."""
        return service_info.rssi if service_info.rssi is not None else -999

    def _publish_candidates(self, candidates: list[_BleSourceCandidate]) -> None:
        """Expose the ranked candidates and whether they were freshly observed."""
        self.state.candidate_source_count = len(candidates)
        self.state.candidate_sources = " | ".join(
            f"{info.source}:{info.rssi} dBm ({info.origin})"
            for info in candidates
        )
        self.state.candidate_details = [
            {"source": info.source, "rssi": info.rssi, "origin": info.origin}
            for info in candidates
        ]
        self.state.fresh_scanner_count = sum(
            info.origin == "fresh_raw_advertisement" for info in candidates
        )
        self.state.cached_scanner_count = sum(
            info.origin == "per_scanner_cache" for info in candidates
        )
        self._notify_listeners()

    def _cached_source_candidates(self) -> list[_BleSourceCandidate]:
        """Read each connectable adapter's BLEDevice, not the HA best-source view.

        Per-adapter cached sightings may be older than fresh raw packets. They
        are labelled accordingly, and a fresh candidate from the same source
        always replaces the cache entry. A cached source may fail and fall
        through to other candidates; cache entries are not held across rounds.
        """
        devices = bluetooth.async_scanner_devices_by_address(
            self.hass, self.address, connectable=True
        )
        out: list[_BleSourceCandidate] = []
        for item in devices:
            device = item.ble_device
            if device is None:
                continue
            scanner = item.scanner
            source = getattr(scanner, "source", None)
            if not source:
                continue
            advertisement = item.advertisement
            rssi = getattr(advertisement, "rssi", None)
            if rssi is None:
                continue
            out.append(
                _BleSourceCandidate(
                    source=str(source), rssi=int(rssi), device=device,
                    origin="per_scanner_cache",
                )
            )
        return out

    async def _collect_fresh_advertisements(self, *, force_full_window: bool = False) -> list[_BleSourceCandidate]:
        """Collect raw per-scanner ads, then supplement from HA's adapter list.

        async_register_callback filters unchanged advertisements and may drop
        an advertisement from an adapter that is not HA's preferred scanner.
        async_register_advertisement_callback sees every packet from every
        scanner, including such filtered advertisements. A per-adapter snapshot
        also surfaces currently visible connectable sources that happened not
        to advertise during the 3-second collection window.
        """
        self.state.advertisement_waits += 1
        self._last_scan_was_adaptive = False
        self._set_phase("waiting_for_adapter_candidates")

        bluetooth.async_clear_advertisement_history(self.hass, self.address)

        first_seen = asyncio.Event()
        fresh: dict[str, _BleSourceCandidate] = {}

        @callback
        def _async_raw_advertisement(
            service_info: bluetooth.BluetoothServiceInfoBleak,
        ) -> None:
            if not service_info.connectable or service_info.device is None:
                return
            self._record_advertisement(service_info)
            key = self._source_key(service_info)
            rssi = self._rssi_value(service_info)
            # Prefer the strongest packet from each source within this round.
            previous = fresh.get(key)
            if previous is None or rssi > previous.rssi:
                fresh[key] = _BleSourceCandidate(
                    source=key, rssi=rssi, device=service_info.device,
                    origin="fresh_raw_advertisement",
                )
            first_seen.set()

        @callback
        def _async_filtered_advertisement(
            service_info: bluetooth.BluetoothServiceInfoBleak,
            _change: bluetooth.BluetoothChange,
        ) -> None:
            _async_raw_advertisement(service_info)

        # The per-packet API exists in modern HA and preserves scanner identity
        # even for packets ignored by normal Bluetooth advertisement de-dup.
        if hasattr(bluetooth, "async_register_advertisement_callback"):
            cancel_callback = bluetooth.async_register_advertisement_callback(
                self.hass, _async_raw_advertisement, self.address,
            )
            self.state.source_discovery_method = "raw_per_scanner_and_snapshot"
        else:
            cancel_callback = bluetooth.async_register_callback(
                self.hass, _async_filtered_advertisement,
                {"address": self.address, "connectable": True},
                bluetooth.BluetoothScanningMode.ACTIVE,
                replay=bluetooth.BluetoothCallbackReplay.DISABLED,
            )
            self.state.source_discovery_method = "filtered_callback_and_snapshot_fallback"

        scan_task = self.hass.async_create_task(
            bluetooth.async_request_active_scan(
                ADVERTISEMENT_WAIT_TIMEOUT + ADAPTER_COLLECTION_WINDOW
            )
        )

        try:
            # A source-specific HA cache handle can be tried even when no new
            # advertisement arrives. Never borrow HA's global best-source
            # BLEDevice, since that would conceal which adapter was used.
            cached_on_entry = self._cached_source_candidates()
            now = time.monotonic()
            eligible_cached = [
                item for item in cached_on_entry
                if now - self._source_failure_at.get(item.source, float("-inf"))
                >= RECENT_SOURCE_FAILURE_SECONDS
            ]
            scan_budget = (
                CACHED_SOURCE_SCAN_SECONDS if eligible_cached
                else ADVERTISEMENT_WAIT_TIMEOUT
            )
            try:
                async with asyncio.timeout(scan_budget):
                    await first_seen.wait()
            except TimeoutError:
                cached = rank_proxy_candidates(
                    item for item in self._cached_source_candidates()
                    if time.monotonic() - self._source_failure_at.get(
                        item.source, float("-inf")
                    ) >= RECENT_SOURCE_FAILURE_SECONDS
                )
                if cached:
                    self.state.cached_sources_without_fresh_count += 1
                    self.state.source_discovery_method = "multi_proxy_cache_without_fresh_advertisement"
                    self.state.adapter_collection_last_seconds = scan_budget
                    self._publish_candidates(cached)
                    self._set_phase("cached_adapter_candidates_ready")
                    _LOGGER.info(
                        "No fresh Xzense advertisement after %.1fs; trying %d "
                        "per-scanner cached sources (one attempt per source)",
                        scan_budget, len(cached),
                    )
                    return cached
                self.state.advertisement_timeouts += 1
                self._set_phase("advertisement_timeout")
                self._set_error(
                    f"No fresh Xzense advertisement or eligible per-scanner "
                    f"BLEDevice after {scan_budget:.0f}s"
                )
                return []

            self._set_phase("fresh_advertisement_ready")
            # Only shorten scanning when THIS scan saw the same proxy as a
            # previous successful session with a strong fresh signal. We
            # deliberately never trust a cached RSSI for the fast decision.
            last_good = fresh.get(self.state.last_successful_source or "")
            last_failure = self._source_failure_at.get(
                self.state.last_successful_source or "", float("-inf")
            )
            use_short_window = (
                not force_full_window
                and last_good is not None
                and last_good.rssi >= FAST_ADAPTER_MIN_RSSI
                and time.monotonic() - last_failure >= RECENT_SOURCE_FAILURE_SECONDS
            )
            window = (FAST_ADAPTER_COLLECTION_WINDOW if use_short_window
                      else ADAPTER_COLLECTION_WINDOW)
            self._last_scan_was_adaptive = use_short_window
            self.state.adapter_collection_last_seconds = window
            if use_short_window:
                self.state.adaptive_short_window_count += 1
            else:
                self.state.adaptive_full_window_count += 1
            await asyncio.sleep(window)
            # Query HA's *per scanner* cache, not async_last_service_info,
            # which only exposes a single best adapter.
            # Cool down failed CACHE sources only. A new live packet from a
            # source remains eligible so newly installed proxies are discovered.
            now = time.monotonic()
            merged = {
                item.source: item for item in self._cached_source_candidates()
                if now - self._source_failure_at.get(item.source, float("-inf"))
                >= RECENT_SOURCE_FAILURE_SECONDS
            }
            merged.update(fresh)  # fresh wins over cached for the same adapter
            candidates = rank_proxy_candidates(merged.values())
            self.state.preferred_source = self._preferred_source
            _LOGGER.info(
                "Xzense BLE candidates by true RSSI %s; selected=%s",
                [(info.source, info.rssi, info.origin) for info in candidates],
                candidates[0].source if candidates else None,
            )
            self._publish_candidates(candidates)
            self._set_phase("adapter_candidates_ready")
            return candidates
        finally:
            cancel_callback()
            scan_task.cancel()

    async def _establish_source_connection(
        self, service_info: _BleSourceCandidate
    ) -> BleakClientWithServiceCache:
        """Connect once through the BLEDevice belonging to one live source."""
        ble_device = service_info.device
        if ble_device is None:
            raise RuntimeError("Xzense source candidate did not include a BLEDevice")

        source = service_info.source
        rssi = service_info.rssi
        self.state.selected_source = source
        self.state.selected_source_rssi = rssi
        self.state.source_connection_attempts += 1
        self.state.connection_attempts += 1
        self._set_phase("connecting_selected_source")
        _LOGGER.info(
            "Connecting Xzense %s via Bluetooth source %s at %s dBm",
            self.address,
            source,
            rssi,
        )

        client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            ble_device.name or self.name,
            self._disconnected,
            max_attempts=1,
        )
        self._client = client
        self.state.ble_link_connected = bool(client.is_connected)
        self.state.ble_connected_at = _utc_now()
        self.state.active_session_source = source
        self.state.active_session_rssi = rssi
        self._active_ble_started_monotonic = time.monotonic()
        self._set_phase("ble_connected")
        return client

    async def _write_application_frame(
        self,
        client: BleakClientWithServiceCache,
        frame: bytes,
        kind: str,
    ) -> None:
        """Serialize one application frame over the DSPS write characteristic."""
        characteristic = client.services.get_characteristic(WRITE_UUID)
        if characteristic is None:
            raise RuntimeError(f"Xzense write characteristic {WRITE_UUID} not found")

        properties = set(characteristic.properties or [])
        if "write-without-response" in properties:
            response = False
            try:
                chunk_size = int(characteristic.max_write_without_response_size)
            except Exception:
                chunk_size = 20
            chunk_size = max(1, min(chunk_size, 512))
            write_mode = "write_without_response"
        elif "write" in properties:
            response = True
            chunk_size = 512
            write_mode = "write_with_response"
        else:
            raise RuntimeError(
                f"Xzense write characteristic has unsupported properties: {sorted(properties)}"
            )

        async with self._tx_lock:
            self.state.tx_write_mode = write_mode
            self.state.tx_chunk_size = chunk_size
            self.state.last_tx = frame
            self.state.last_tx_at = _utc_now()
            self.state.last_tx_kind = kind
            _LOGGER.debug(
                "Xzense TX %s: %s",
                kind,
                "<redacted>" if kind == "CONNECT/REQ" else frame.hex(),
            )

            for offset in range(0, len(frame), chunk_size):
                chunk = frame[offset : offset + chunk_size]
                await client.write_gatt_char(characteristic, chunk, response=response)
                self.state.tx_chunk_count += 1
                if offset + chunk_size < len(frame):
                    await asyncio.sleep(0.01)
            self.state.tx_count += 1
            self._notify_listeners()

    async def _send_application_connect(
        self, client: BleakClientWithServiceCache
    ) -> None:
        """Send the recovered Xzense CONNECT/REQ application handshake."""
        frame = build_connect_request(self.pin, APPLICATION_CLIENT_NAME)
        self.state.application_connect_attempts += 1
        self.state.application_auth_state = "sending_connect"
        self.state.handshake_last_error = None
        self._set_phase("sending_application_connect")

        _LOGGER.info(
            "Sending Xzense CONNECT/REQ #%d (%d bytes) to %s",
            self.state.application_connect_attempts,
            len(frame),
            self.address,
        )

        # Set this before writing because the controller may ACK immediately.
        self.state.handshake_sent_at = _utc_now()
        try:
            await self._write_application_frame(client, frame, "CONNECT/REQ")
        except Exception as err:
            self.state.application_auth_state = "connect_write_failed"
            self.state.handshake_last_error = f"{type(err).__name__}: {err}"
            self._set_phase("application_connect_write_failed")
            self._notify_listeners()
            raise

        if self.state.application_auth_state == "sending_connect":
            self.state.application_auth_state = "connect_sent"
            self._set_phase("application_connect_sent")
        self._notify_listeners()

    async def _send_status_request(
        self, client: BleakClientWithServiceCache, session_id: int
    ) -> None:
        """Send the captured read-only STATUS/REQ for the active session."""
        frame = build_status_request(session_id)
        self.state.status_request_count += 1
        self.state.last_status_request_at = _utc_now()
        try:
            await self._write_application_frame(client, frame, "STATUS/REQ")
        except Exception as err:
            self.state.status_request_errors += 1
            self.state.last_error = f"STATUS/REQ {type(err).__name__}: {err}"
            self._notify_listeners()
            raise

    async def _status_loop(self) -> None:
        """Poll live read-only status while an authenticated session is active."""
        try:
            while not self._stopping:
                await self._session_ready.wait()
                if self._stopping:
                    return

                self.state.status_polling_active = True
                self._notify_listeners()
                # Keep polling until disconnect clears the session event.
                while self._session_ready.is_set() and not self._stopping:
                    client = self._client
                    session_id = self.state.session_id
                    if not client or not client.is_connected or session_id is None:
                        break
                    try:
                        await self._send_status_request(client, session_id)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        _LOGGER.debug(
                            "Xzense STATUS/REQ failed for %s", self.address, exc_info=True
                        )
                        if not client.is_connected:
                            break

                    if self.interval_minutes > 0:
                        # One STATUS per periodic session; do not send further
                        # requests until a new authenticated connection.
                        while (self._session_ready.is_set() and not self._stopping
                               and self.interval_minutes > 0):
                            await asyncio.sleep(0.25)
                    else:
                        await asyncio.sleep(STATUS_POLL_INTERVAL)

                self.state.status_polling_active = False
                self._notify_listeners()
                # The event may have been set again by a very fast reconnect.
                if self._session_ready.is_set():
                    await asyncio.sleep(0)
        except asyncio.CancelledError:
            raise
        finally:
            self.state.status_polling_active = False

    async def _connect_once(self, fast: bool = False, *, force_full_window: bool = False) -> bool:
        # Always collect source-specific observations, including on demand.
        # A fast cached-only shortcut could prevent a newly installed proxy
        # from ever being considered when older cached adapters exist.
        if fast:
            self.state.fast_connect_attempts += 1
        candidates = await self._collect_fresh_advertisements(
            force_full_window=force_full_window
        )
        if not candidates or self._stopping:
            return False

        # Bound the work in every round even if HA exposes many scanners.
        candidates = candidates[:MAX_SOURCE_ATTEMPTS_PER_ROUND]

        last_error: Exception | None = None

        # Strongest source first. If it fails, immediately try the next source
        # observed during the same fresh scan window before waiting for new ads.
        for index, service_info in enumerate(candidates):
            if self._stopping:
                return False

            client: BleakClientWithServiceCache | None = None
            source = service_info.source
            try:
                if index:
                    self.state.source_fallbacks += 1
                    self._set_phase("trying_next_adapter_source")

                client = await self._establish_source_connection(service_info)
                self._parser.reset()
                self._session_ready.clear()
                self._fresh_status_event.clear()
                self.state.status_polling_active = False
                self.state.session_id = None
                # Preserve last VERIFIED status/global values during reconnection.
                # A new authenticated STATUS overwrites them when it arrives.
                self.state.last_status_request_at = None
                self.state.application_auth_state = "not_started"

                self.state.notify_started_at = _utc_now()
                self._set_phase("enabling_notifications")
                try:
                    await asyncio.wait_for(
                        client.start_notify(NOTIFY_UUID, self._notification),
                        timeout=NOTIFY_TIMEOUT,
                    )
                except Exception as notify_err:
                    if self._is_authorization_error(notify_err):
                        self.state.authorization_retries += 1
                    raise

                self.state.notifications_active = True
                self.state.notify_active_at = _utc_now()
                self.state.connected = True
                self.state.ble_link_connected = bool(client.is_connected)
                self.state.last_error = None
                self._set_phase("notifications_active")
                self._notify_listeners()

                # The controller sends no unsolicited data and closes the BLE link
                # after about 20 seconds unless the application session is opened.
                # Send only the recovered, non-control CONNECT/REQ handshake.
                await self._send_application_connect(client)

                _LOGGER.info(
                    "Connected Xzense protocol monitor to %s via %s (%s dBm); application CONNECT sent",
                    self.address,
                    source,
                    service_info.rssi,
                )
                return True

            except Exception as err:
                last_error = err
                self.state.last_failed_source = source
                self._source_failure_at[source] = time.monotonic()
                if client and client.is_connected:
                    self._planned_disconnects[id(client)] = "local_setup_failure_cleanup"
                    try:
                        await client.disconnect()
                    except Exception:
                        pass
                self._client = None
                self.state.active_session_source = None
                self.state.active_session_rssi = None
                self._active_ble_started_monotonic = None
                self.state.connected = False
                self.state.ble_link_connected = False
                self.state.notifications_active = False
                self._set_error(f"{type(err).__name__}: {err}")
                _LOGGER.debug(
                    "Unable to connect/subscribe Xzense %s via source %s",
                    self.address,
                    source,
                    exc_info=True,
                )

        self._set_phase("all_adapter_sources_failed")
        if last_error is not None:
            self._set_error(f"{type(last_error).__name__}: {last_error}")
        bluetooth.async_clear_advertisement_history(self.hass, self.address)
        # A round has already tried each candidate once. Avoid recursive
        # rescans/retries (which previously could overload Home Assistant).
        return False

    @staticmethod
    def _is_authorization_error(err: Exception) -> bool:
        """Return True for the GATT authorization failure seen on Xzense."""
        message = str(err).lower()
        return (
            "insufficient authorization" in message
            or "authorization (8)" in message
            or "gatterrorresponse: insufficient authorization" in message
        )

    def _disconnected(self, _client: BleakClientWithServiceCache) -> None:
        """Record the BLE callback without pretending it identifies the initiator."""
        local_reason = self._planned_disconnects.pop(id(_client), None)
        # A callback delayed past client replacement must NEVER tear down the
        # new BLE session, even if the old client was locally disconnected.
        # Local cleanup was already classified when we initiated disconnect().
        if _client is not self._client:
            _LOGGER.debug(
                "Ignoring stale Xzense BLE disconnect callback (local_reason=%s)",
                local_reason,
            )
            return

        kind = local_reason or (
            "local_shutdown" if self._stopping else "unexpected_ble_callback"
        )
        now = _utc_now()
        seconds = (
            round(max(0.0, time.monotonic() - self._active_ble_started_monotonic), 2)
            if self._active_ble_started_monotonic is not None else None
        )
        source = self.state.active_session_source or self.state.selected_source
        authenticated = self.state.application_auth_state == "connected"
        event: dict[str, object] = {
            "at": now,
            "source": source,
            "rssi_at_connect": self.state.active_session_rssi,
            "duration_seconds": seconds,
            "classification": kind,
            "authenticated": authenticated,
            "last_status_request_at": self.state.last_status_request_at,
            "last_status_response_at": self.state.last_status_response_at,
            "last_notification_at": self.state.last_notification_at,
        }
        self.state.disconnect_history.append(event)
        del self.state.disconnect_history[:-DISCONNECT_HISTORY_LIMIT]
        self.state.last_disconnect_kind = kind
        self.state.last_disconnect_source = source
        self.state.last_disconnect_session_seconds = seconds
        self.state.last_disconnect_authenticated = authenticated
        self.state.last_disconnect_last_status_request_at = self.state.last_status_request_at
        self.state.last_disconnect_last_status_response_at = self.state.last_status_response_at
        if kind == "unexpected_ble_callback" and source:
            self._source_failure_at[source] = time.monotonic()

        _LOGGER.warning(
            "Xzense BLE disconnected: classification=%s source=%s rssi_at_connect=%s "
            "duration=%ss authenticated=%s last_status_req=%s last_status_ack=%s "
            "(initiator/reason not provided by Bleak callback)",
            kind, source, self.state.active_session_rssi, seconds,
            authenticated, self.state.last_status_request_at,
            self.state.last_status_response_at,
        )
        if _client is self._client:
            self._client = None
        self.state.active_session_source = None
        self.state.active_session_rssi = None
        self._active_ble_started_monotonic = None
        self.state.connected = False
        self.state.ble_link_connected = False
        self.state.notifications_active = False
        self.state.status_polling_active = False
        self._session_ready.clear()
        if hasattr(self, "_fresh_status_event"):
            self._fresh_status_event.clear()
        self.state.disconnect_count += 1
        self.state.last_disconnect_at = now
        if authenticated:
            self.state.application_auth_state = "disconnected_after_ack"
        elif self.state.application_auth_state in ("connect_sent", "sending_connect"):
            self.state.application_auth_state = "disconnected_before_ack"
        self._set_phase("disconnected")
        self._notify_listeners()
        self._wake.set()

    def _record_frame_history(self, frame: XzenseFrame) -> None:
        """Keep a compact history of validated protocol frames."""
        self.state.packet_history.append(
            {
                "at": _utc_now(),
                "packet": frame.packet_type_name,
                "protocol": frame.protocol_type_name,
                "frame": frame.hex,
                "application_payload": frame.application_payload.hex(),
            }
        )
        if len(self.state.packet_history) > PACKET_HISTORY_LIMIT:
            del self.state.packet_history[:-PACKET_HISTORY_LIMIT]

    def _notification(
        self, _characteristic: BleakGATTCharacteristic, data: bytearray
    ) -> None:
        payload = bytes(data)
        self.state.notification_count += 1
        self.state.last_notification = payload
        self.state.last_notification_at = _utc_now()

        _LOGGER.debug(
            "Xzense raw RX notification #%d: %s",
            self.state.notification_count,
            payload.hex(),
        )

        frames = self._parser.feed(payload)
        self.state.discarded_bytes = self._parser.discarded_bytes
        self.state.invalid_frames = self._parser.invalid_frames
        self.state.crc_errors = self._parser.crc_errors

        for frame in frames:
            self.state.packet_count += 1
            self.state.last_frame = frame
            self._record_frame_history(frame)
            _LOGGER.debug(
                "Xzense RX frame #%d: %s outer=%02x packet=%s protocol=%s payload=%s crc=%04x",
                self.state.packet_count,
                frame.hex,
                frame.outer_type,
                frame.packet_type_name,
                frame.protocol_type_name,
                frame.payload_hex or "<empty>",
                frame.checksum,
            )

            if frame.is_connect_ack:
                # The ACK is the first proof that the selected proxy carried a
                # valid Xzense session. Avoid counting duplicate ACKs as new picks.
                if self.state.application_auth_state != "connected":
                    source = self.state.active_session_source
                    if source:
                        self._preferred_source = source
                        self.state.preferred_source = source
                        self.state.last_successful_source = source
                        self._source_failure_at.pop(source, None)
                self.state.application_auth_state = "connected"
                self.state.application_auth_success_count += 1
                self.state.handshake_response_at = _utc_now()
                self.state.handshake_last_error = None
                self.state.session_id = frame.session_id
                self.state.connect_ack_version = frame.connect_version
                self.state.connect_ack_flag = frame.connect_flag
                self._set_phase("application_connected")
                self._session_ready.set()
                _LOGGER.info(
                    "Xzense application CONNECT/ACK received: session=%08X version=%s flag=%s",
                    frame.session_id or 0,
                    frame.connect_version,
                    frame.connect_flag,
                )
            elif frame.is_connect_nack:
                self.state.application_auth_state = "nack"
                self.state.handshake_response_at = _utc_now()
                self.state.handshake_last_error = "CONNECT/NACK received (PIN rejected or request invalid)"
                self._session_ready.clear()
                self._set_phase("application_connect_nack")
                _LOGGER.warning("Xzense CONNECT/NACK received")

            status = decode_status_data(frame, self.state.session_id)
            if status is not None:
                self.state.status = status
                for observer in tuple(self._status_listeners):
                    try:
                        observer(status.device_state)
                    except Exception:
                        _LOGGER.exception("Xzense STATUS observer raised an exception")
                self._update_timing(status.device_state, status.state_timer)
                self._update_mode_switches(status.device_state)
                self.state.status_response_count += 1
                self.state.last_status_response_at = _utc_now()
                self.state.last_status_payload = status.raw
                self.state.last_data_at = self.state.last_status_response_at
                self._fresh_status_event.set()
                self._save_cache_soon()
                _LOGGER.debug(
                    "Xzense STATUS: state=%s timer=%ss fan=%s chimney=%.1fC outside=%.1fC inside=%.1fC pressure=%shPa flags=%s raw=%s",
                    status.device_state,
                    status.state_timer,
                    status.fan_speed,
                    status.chimney_temperature,
                    status.outside_temperature,
                    status.inside_temperature,
                    status.air_pressure_hpa,
                    status.flags,
                    status.raw.hex(),
                )
            elif frame.packet_type == PACKET_STATUS and frame.protocol_type == PROTOCOL_NACK:
                self.state.status_nack_count += 1
                _LOGGER.warning("Xzense STATUS/NACK received")

            if frame.packet_type == PACKET_GLOBAL and frame.protocol_type == PROTOCOL_ACK:
                self.state.global_write_ack_count += 1
                self.state.last_global_write_response = f"ACK:{frame.application_payload.hex()}"
                self.state.last_global_write_response_at = _utc_now()
                _LOGGER.info("Xzense GLOBAL/ACK received: %s", frame.application_payload.hex())
            elif frame.packet_type == PACKET_GLOBAL and frame.protocol_type == PROTOCOL_NACK:
                self.state.global_write_nack_count += 1
                self.state.last_global_write_response = f"NACK:{frame.application_payload.hex()}"
                self.state.last_global_write_response_at = _utc_now()
                _LOGGER.warning("Xzense GLOBAL/NACK received: %s", frame.application_payload.hex())

            if frame.packet_type == PACKET_BOOST and frame.protocol_type == PROTOCOL_ACK:
                self.state.boost_ack_count += 1
                self.state.last_boost_response = f"ACK:{frame.application_payload.hex()}"
                self.state.last_boost_response_at = _utc_now()
                _LOGGER.info("Xzense BOOST/ACK received: %s", frame.application_payload.hex())
            elif frame.packet_type == PACKET_BOOST and frame.protocol_type == PROTOCOL_NACK:
                self._timing.cancel_start_request()
                self.state.boost_nack_count += 1
                self.state.last_boost_response = f"NACK:{frame.application_payload.hex()}"
                self.state.last_boost_response_at = _utc_now()
                _LOGGER.warning("Xzense BOOST/NACK received: %s", frame.application_payload.hex())

            if frame.packet_type == PACKET_VENTILATION and frame.protocol_type == PROTOCOL_ACK:
                self.state.ventilation_ack_count += 1
                self.state.last_ventilation_response = f"ACK:{frame.application_payload.hex()}"
                self.state.last_ventilation_response_at = _utc_now()
                self.state.ventilation_pending_value = None
                _LOGGER.info("Xzense VENTILATION/ACK received: %s", frame.application_payload.hex())
            elif frame.packet_type == PACKET_VENTILATION and frame.protocol_type == PROTOCOL_NACK:
                self.state.ventilation_nack_count += 1
                self.state.last_ventilation_response = f"NACK:{frame.application_payload.hex()}"
                self.state.last_ventilation_response_at = _utc_now()
                self.state.ventilation_pending_value = None
                _LOGGER.warning("Xzense VENTILATION/NACK received: %s", frame.application_payload.hex())

            global_values = decode_global_data(frame, self.state.session_id)
            if global_values is not None:
                for global_id, value in global_values.items():
                    self.state.globals[global_id] = value
                    self.state.global_update_count += 1
                    self.state.last_global_id = global_id
                    self.state.last_global_name = global_name(global_id)
                    self.state.last_global_value = value
                    self.state.last_global_at = _utc_now()
                    self.state.last_data_at = self.state.last_global_at
                    self._save_cache_soon()
                    _LOGGER.debug(
                        "Xzense GLOBAL/DATA %s (0x%02X)=%s",
                        global_name(global_id),
                        global_id,
                        value,
                    )

        self._notify_listeners()

    def _update_mode_switches(self, device_state: int) -> None:
        """Update switches only from an authenticated, decoded STATUS frame.

        Existing values intentionally survive reconnections until fresh STATUS
        arrives. State 7 is not yet verified as Boost on or off, so we retain
        its previous Boost value rather than guessing.
        """
        if device_state == 3:
            self.state.boost_is_on = True
        elif device_state != 7:
            self.state.boost_is_on = False
        self.state.ventilation_is_on = device_state == 8
        self.state.last_mode_status_at = _utc_now()

    def current_device_state(self) -> int | None:
        """Return the best current operating-state value."""
        if self.state.status is not None:
            return self.state.status.device_state
        return self.state.globals.get(0x19)

    def ventilation_available(self) -> bool:
        """Return True when a VENTILATION request can be formed."""
        return bool(
            VENTILATION_WRITES_ENABLED
            and self.state.application_auth_state == "connected"
            and self._client
            and self._client.is_connected
            and self.state.session_id is not None
        )

    async def async_set_ventilation(self, enabled: bool) -> None:
        """Send the firmware-recovered VENTILATION start/stop request."""
        if not self.ventilation_available():
            raise HomeAssistantError(
                "Xzense Ventilation is unavailable until the application session is connected"
            )
        assert self._client is not None
        assert self.state.session_id is not None
        frame = build_ventilation_request(self.state.session_id, enabled)
        action = "on" if enabled else "off"
        self.state.ventilation_request_count += 1
        self.state.last_ventilation_action = action
        self.state.last_ventilation_request_at = _utc_now()
        self.state.last_ventilation_response = None
        self.state.last_ventilation_response_at = None
        self.state.ventilation_pending_value = enabled
        self._notify_listeners()
        await self._write_application_frame(self._client, frame, f"VENTILATION/REQ {action}")
        await asyncio.sleep(0.35)
        if self._client.is_connected and self.state.session_id is not None:
            try:
                await self._write_application_frame(
                    self._client,
                    build_status_request(self.state.session_id),
                    f"STATUS/REQ after VENTILATION {action}",
                )
            except Exception:
                _LOGGER.debug("Immediate STATUS after VENTILATION failed", exc_info=True)

    def _current_inside_temp_raw(self) -> int | None:
        """Return the raw inside-temperature value required by BOOST/REQ."""
        # Use a fresh STATUS snapshot rather than a retained GLOBAL value
        # when a control is queued after an offline period.
        if self._fresh_status_event.is_set() and self.state.status is not None:
            return self.state.status.inside_temperature_raw
        value = self.state.globals.get(0x1C)
        if value is not None:
            return value
        if self.state.status is not None:
            return self.state.status.inside_temperature_raw
        return None

    def boost_available(self) -> bool:
        """Return True when a BOOST request can be formed for the active session."""
        return bool(
            BOOST_WRITES_ENABLED
            and self.state.application_auth_state == "connected"
            and self._client
            and self._client.is_connected
            and self.state.session_id is not None
            and self._current_inside_temp_raw() is not None
        )

    async def async_set_boost(self, enabled: bool) -> None:
        """Send the firmware-recovered BOOST start/stop request.

        The controller firmware itself validates whether Boost is allowed in the
        current operating state and returns BOOST/ACK or BOOST/NACK. No extra
        Home Assistant state/temperature gate is imposed here.
        """
        if not self.boost_available():
            raise HomeAssistantError(
                "Xzense Boost is unavailable until the application session is connected "
                "and an inside-temperature value has been received"
            )
        assert self._client is not None
        assert self.state.session_id is not None
        inside_temp_raw = self._current_inside_temp_raw()
        assert inside_temp_raw is not None
        frame = build_boost_request(self.state.session_id, enabled, inside_temp_raw)
        action = "on" if enabled else "off"
        self.state.boost_request_count += 1
        self.state.last_boost_action = action
        self.state.last_boost_request_at = _utc_now()
        self.state.last_boost_response = None
        self.state.last_boost_response_at = None
        self._notify_listeners()
        await self._write_application_frame(
            self._client, frame, f"BOOST/REQ {action} inside_temp_raw={inside_temp_raw}"
        )
        # Ask for a fresh runtime state shortly after the control request. The
        # normal 10-second polling continues regardless.
        await asyncio.sleep(0.35)
        if self._client.is_connected and self.state.session_id is not None:
            try:
                await self._write_application_frame(
                    self._client,
                    build_status_request(self.state.session_id),
                    f"STATUS/REQ after BOOST {action}",
                )
            except Exception:
                _LOGGER.debug("Immediate STATUS after BOOST failed", exc_info=True)

    async def async_execute_feature(self, feature_key: str, value: object | None = None) -> None:
        """Execute a verified control; candidate features remain write-locked."""
        feature = FEATURE_BY_KEY.get(feature_key)
        if feature is None:
            raise HomeAssistantError(f"Unknown Xzense feature: {feature_key}")
        if not CONTROL_WRITES_ENABLED or feature.state != "write_ready":
            raise HomeAssistantError(
                f"{feature.name} is not write-enabled; the Xzense protocol mapping is pending"
            )
        if (
            self.state.application_auth_state != "connected"
            or not self._client
            or not self._client.is_connected
            or self.state.session_id is None
        ):
            raise HomeAssistantError("Xzense application session is not connected")

        if feature.global_id is not None and isinstance(value, (bool, int, float)):
            raw_value = int(value)
            if feature_key in {"auto_start_temperature", "auto_stop_temperature", "minimum_fan_voltage"}:
                from .settings import validate_raw_setting
                try:
                    validate_raw_setting(feature_key, raw_value, self.state.globals,
                                         rs009_41=self.rs009_41_motor)
                except ValueError as err:
                    raise HomeAssistantError(str(err)) from err
            frame = build_global_request(self.state.session_id, feature.global_id, raw_value)
            self.state.global_write_request_count += 1
            self.state.last_global_write_id = feature.global_id
            self.state.last_global_write_value = raw_value
            self.state.last_global_write_request_at = _utc_now()
            self.state.last_global_write_response = None
            self.state.last_global_write_response_at = None
            self._notify_listeners()
            await self._write_application_frame(
                self._client, frame, f"GLOBAL/REQ {feature.key} raw={raw_value}"
            )
            return

        raise HomeAssistantError(
            f"{feature.name} is marked write-ready but its packet handler is not installed"
        )

    def _set_error(self, message: str) -> None:
        if self.state.last_error != message:
            self.state.last_error = message
            self.state.connected = False
            self._notify_listeners()
