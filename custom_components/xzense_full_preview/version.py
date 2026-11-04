"""Version helpers for Xzense."""

from __future__ import annotations


def format_firmware_version(raw: int | None) -> str | None:
    """Format the CONNECT ACK version as the Xzense firmware version.

    The installed system reports raw 410 while both the control panel and
    Power Unit show firmware 4.10. For values >= 100, the last two decimal
    digits are treated as the minor version (407 -> 4.7, 410 -> 4.10).
    """
    if raw is None or raw < 0:
        return None
    if raw >= 100:
        return f"{raw // 100}.{raw % 100}"
    if raw >= 10:
        return f"{raw // 10}.{raw % 10}"
    return str(raw)
