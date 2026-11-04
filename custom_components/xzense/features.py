"""Feature registry for Xzense.

The registry separates verified live mappings from candidates. Only features
marked ``write_ready`` are exposed as controls. Read-only candidate metadata is
kept for diagnostics, without creating unusable Home Assistant controls.
Legacy keys for functional entities are retained to preserve unique IDs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FeatureState = Literal["verified_read", "write_ready", "id_known", "mapping_pending"]


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    key: str
    name: str
    kind: Literal[
        "sensor",
        "binary_sensor",
        "button",
        "switch",
        "number",
        "select",
        "update",
        "virtual",
    ]
    state: FeatureState
    global_id: int | None = None
    packet_type: int | None = None
    notes: str = ""


FEATURES: tuple[FeatureSpec, ...] = (
    # Live/status reads.
    FeatureSpec(
        "chimney_temperature",
        "Chimney temperature",
        "sensor",
        "verified_read",
        global_id=0x1E,
        notes="Live calibrated: signed tenths of °C.",
    ),
    FeatureSpec(
        "inside_temperature",
        "Inside temperature",
        "sensor",
        "id_known",
        global_id=0x1C,
        notes="Strong live mapping: signed tenths of °C.",
    ),
    FeatureSpec(
        "outside_temperature",
        "Outside temperature",
        "sensor",
        "id_known",
        global_id=0x1D,
        notes="Strong live mapping: signed tenths of °C.",
    ),
    FeatureSpec(
        "fan_speed",
        "Actual fan speed",
        "sensor",
        "verified_read",
        global_id=0x1F,
        notes="Live A/B verified at 10% and 100%.",
    ),
    FeatureSpec(
        "pressure",
        "Air pressure",
        "sensor",
        "verified_read",
        global_id=0x1B,
        notes="User-confirmed live value: raw 1011 = 1011 hPa.",
    ),
    FeatureSpec(
        "state_timer",
        "Time in current state",
        "sensor",
        "verified_read",
        global_id=0x1A,
        notes="Seconds; observed to increment approximately once per second.",
    ),
    FeatureSpec("signal_strength", "Radio link signal strength", "sensor", "id_known", global_id=0x05,
                notes="GLOBAL 0x05 SIGNAL_STRENGTH, inferred 0–3 panel↔power-unit bars; not BLE RSSI."),
    FeatureSpec(
        "battery",
        "Panel battery level",
        "sensor",
        "id_known",
        global_id=0x04,
        notes="GLOBAL 0x04 correlates with panel icon (100→90). Percent inference, requires future calibration.",
    ),
    FeatureSpec(
        "device_state",
        "Device state",
        "sensor",
        "verified_read",
        global_id=0x19,
        notes=(
            "Xzense 4.10 RC2 operating states: 1=Setup, 2=Ready for lighting, "
            "3=Boosting, 4=Operation, 5=Burnout, 6=Afterrun, "
            "7=Refueling/Reheating, 8=Ventilation, 9=Error, 10=Upgrading."
        ),
    ),

    # Interface settings.  Legacy keys are retained to preserve entity unique IDs.
    FeatureSpec(
        "volume_raw",
        "Sound",
        "number",
        "write_ready",
        global_id=0x32,
        notes="Live A/B correlation: changing panel Sound 12→24 changed GLOBAL 0x32 12→24.",
    ),
    FeatureSpec(
        "contrast_raw",
        "Contrast",
        "number",
        "write_ready",
        global_id=0x33,
        notes="Live panel correlation: Contrast 75 -> GLOBAL 0x33 value 75.",
    ),
    FeatureSpec(
        "brightness_raw",
        "Brightness",
        "number",
        "write_ready",
        global_id=0x34,
        notes="Live panel correlation: Brightness 68 -> GLOBAL 0x34 value 68.",
    ),
    # App-visible operating controls.
    FeatureSpec(
        "start_fire",
        "Start lighting",
        "button",
        "write_ready",
        packet_type=0x08,
        notes="Ready (2) or Afterrun (6): send BOOST/REQ start=1. Afterrun restart acceptance requires physical validation.",
    ),
    FeatureSpec(
        "stop_fire",
        "Stop firing",
        "button",
        "write_ready",
        global_id=0x19,
        notes=(
            "4.10 RC2 firmware-derived action: BOOST/REQ start=0 in Boosting/Reheating; "
            "Operation or Burnout transitions to Afterrun via GLOBAL 0x19=6."
        ),
    ),
    FeatureSpec(
        "refuel",
        "Refuel",
        "button",
        "write_ready",
        packet_type=0x08,
        notes="Firmware 4.10_RC2: Refuel is available only in Burnout (external state 5), using BOOST/REQ start=1. The controller enters Refueling (state 7) for GLOBAL 0x59 seconds (typically 180 s). The same command in Operation (state 4) instead triggers ordinary Boost for GLOBAL 0x4D seconds.",
    ),
    FeatureSpec(
        "boost",
        "Boost",
        "switch",
        "write_ready",
        packet_type=0x08,
        notes="BOOST 0x08 start/stop; actual state from STATUS 3 (state 7 unresolved).",
    ),
    FeatureSpec(
        "ventilation",
        "Ventilation",
        "switch",
        "write_ready",
        packet_type=0x09,
        notes="Firmware-derived VENTILATION/REQ with one-byte start/stop flag; first live write still pending.",
    ),
    FeatureSpec(
        "user_fan_speed",
        "Fan speed",
        "number",
        "write_ready",
        global_id=0x50,
        notes=(
            "GLOBAL 0x50 is the fan-speed setpoint in both Operation (state 4) and "
            "Ventilation (state 8). Live Ventilation capture showed 10→16% while "
            "STATUS reported 16%; direct-percent coding is retained."
        ),
    ),
    FeatureSpec(
        "boost_fan_speed",
        "Boost speed",
        "number",
        "write_ready",
        global_id=0x4F,
        notes="Live panel correlation: Boost speed 100% -> GLOBAL 0x4F value 100.",
    ),
    FeatureSpec(
        "system_control",
        "System control",
        "select",
        "write_ready",
        global_id=0x55,
        notes="Xzense 4.10 RC2 SystemManager UI binds the mode selector to GLOBAL 0x55: 0=Manual, 1=eXotelligence, 2=Pressure controlled.",
    ),

    # Setup/service settings directly correlated against the controller.
    FeatureSpec(
        "auto_start_temperature",
        "Start temperature",
        "number",
        "write_ready",
        global_id=0x4B,
        notes="Tenths of °C on wire; 50.2 °C -> raw 502.",
    ),
    FeatureSpec(
        "auto_stop_temperature",
        "Stop temperature",
        "number",
        "write_ready",
        global_id=0x4C,
        notes="Tenths of °C on wire; 39.8 °C -> raw 398.",
    ),
    FeatureSpec(
        "boost_time",
        "Boost time",
        "number",
        "write_ready",
        global_id=0x4D,
        notes="Seconds on wire; 15 min -> raw 900.",
    ),
    FeatureSpec(
        "afterrun_time",
        "Afterrun time",
        "number",
        "write_ready",
        global_id=0x4E,
        notes="Seconds on wire; 30 min -> raw 1800.",
    ),
    FeatureSpec(
        "boost_stop_temperature",
        "Boost stop temperature",
        "number",
        "write_ready",
        global_id=0x52,
        notes="Tenths of °C on wire; 60.0 °C -> raw 600.",
    ),
    FeatureSpec(
        "wanted_draft",
        "Pipetrekk",
        "number",
        "write_ready",
        global_id=0x53,
        notes="Configured installation draught in Pa, not live measured pressure (no XTP fitted). 26 Pa -> raw 26.",
    ),
    FeatureSpec(
        "minimum_fan_voltage",
        "Minimum fan voltage",
        "number",
        "write_ready",
        global_id=0x54,
        notes="Direct volts; live value 105 V -> raw 105.",
    ),

    # Remaining candidates are intentionally read-only / unavailable as controls.
    # External start (0x57) and External fan speed (0x5A) are intentionally
    # deferred: no HA entities or feature_matrix records. Raw GLOBAL data is
    # still decoded and retained for future protocol research.
    FeatureSpec(
        "temperature_sensor",
        "Temperature probe",
        "switch",
        "write_ready",
        global_id=0x56,
        notes=(
            "Experimental: GLOBAL 0x56 maps to the Xzense Temperature sensor On/Off setting. "
            "0=Off / 1=On is inferred, not yet confirmed by a live HA write/readback. "
            "Turning it off disables automatic temperature-based start/stop."
        ),
    ),
    # Firmware v4.10 RC2 descriptor: 150–500°C (manual: 150–400°C).
    FeatureSpec(
        "alarm_setpoint",
        "Alarm temperature",
        "number",
        "write_ready",
        global_id=0x58,
        notes="Firmware v4.10: 150–500°C; Norwegian manual: 150–400°C; raw 2500=250.0°C. Live HA write/ACK still untested.",
    ),
    # User confirmed that 0x59/0x5B are editable on the Xzense panel.
    # Seconds-to-minutes scaling is based on observed raw=180/300 matching
    # 3 and 5 minutes; controller accepted write/readback not yet tested.
    # Firmware setup descriptors now verified: 0x59 0–45 min, 0x5B 1–200 min.
    FeatureSpec(
        "refire_time",
        "Refire / Reboost time",
        "number",
        "write_ready",
        global_id=0x59,
        notes="Firmware setup: 0–2700 seconds. Raw 180 seconds=3 minutes; write/ACK untested.",
    ),
    FeatureSpec(
        "burnout_time",
        "Burnout timeout",
        "number",
        "write_ready",
        global_id=0x5B,
        notes="Firmware setup: 60–12000 seconds. Raw 300 seconds=5 minutes; write/ACK untested.",
    ),

    # CONNECT/ACK-sourced firmware version; other history/log data remains
    # available for future FILE_TRANSFER research, not as empty HA entities.
    FeatureSpec(
        "firmware_version",
        "Firmware version",
        "sensor",
        "verified_read",
        notes="CONNECT ACK version; observed raw 410 is rendered as firmware 4.10.",
    ),
)

FEATURE_BY_KEY = {feature.key: feature for feature in FEATURES}
