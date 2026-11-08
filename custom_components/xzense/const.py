"""Constants for the Xzense integration."""

from __future__ import annotations

import re

DOMAIN = "xzense"
NAME = "Xzense"
VERSION = "0.5.28.6"

# Dialog/Renesas DSPS (Serial Port Service) UUIDs recovered from Xzense 5.0.2.
SERVICE_UUID = "0783b03e-8535-b5a0-7140-a304d2495cb7"
NOTIFY_UUID = "0783b03e-8535-b5a0-7140-a304d2495cb8"  # Server TX -> phone/HA
WRITE_UUID = "0783b03e-8535-b5a0-7140-a304d2495cba"   # Server RX <- phone/HA

CONF_NAME = "name"
CONF_PIN = "pin"
CONF_BURNOUT_NOTIFY_ENABLED = "burnout_notification_enabled"
CONF_BURNOUT_NOTIFY_TARGET = "burnout_notification_target"
CONF_RS009_41_MOTOR = "rs009_41_motor"
DEFAULT_NAME = "Xzense"

PIN_PATTERN = re.compile(r"^[0-9A-F]{4}$")

# GLOBAL writes are enabled only for features explicitly marked
# write_ready. The number platform converts HA-native units to the verified wire
# encoding before the client sends the signed-int16 GLOBAL value. No unverified
# enum conversion is applied.
CONTROL_WRITES_ENABLED = True
EXPERIMENTAL_GLOBAL_WRITES_ENABLED = True

# BOOST remains the separately verified packet-type 0x08 control.
BOOST_WRITES_ENABLED = True

# VENTILATION packet 0x09 start/stop payload recovered from controller firmware.
# It is statically verified but still awaits the first live write test on this controller.
VENTILATION_WRITES_ENABLED = True

def normalize_pin(value: str) -> str | None:
    """Normalize a Xzense PIN, returning None if it is not four hex digits."""
    pin = value.strip().upper()
    return pin if PIN_PATTERN.fullmatch(pin) else None
