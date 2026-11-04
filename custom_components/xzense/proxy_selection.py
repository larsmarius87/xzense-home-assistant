"""Pure ranking of HA Bluetooth source candidates by actual signal strength."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol, TypeVar


class _Advertisement(Protocol):
    source: str | None
    rssi: int | None


T = TypeVar("T", bound=_Advertisement)


def rank_proxy_candidates(
    candidates: Iterable[T],
    *,
    preferred_source: str | None = None,
    recent_failed_sources: set[str] | None = None,
) -> list[T]:
    """Strict RSSI descending. Old preference fields do not affect the result.

    Source key is a deterministic tiebreaker, not a signal bonus. If the
    strongest source fails, XzenseClient attempts the other ranked sources.
    """
    return sorted(
        candidates,
        key=lambda item: (
            -(item.rssi if item.rssi is not None else -999),
            item.source or "unknown",
        ),
    )
