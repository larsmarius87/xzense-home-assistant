"""Xzense application protocol framing recovered from the bundled controller firmware.

Wire format (before escaping)::

    0x23 | size_le16 | network=0x00 | outer_type | payload | crc16_le | 0x24

``size`` is the length of ``network + outer_type + payload``.  CRC-16/CCITT-FALSE
(poly 0x1021, init 0xFFFF) is calculated over those same bytes.  Reserved bytes
0x23 ('#'), 0x24 ('$') and 0x27 (escape) are escaped in payload/CRC as
``0x27, byte | 0x80``.  The fixed five-byte header is not escaped.

The Xzense application packet carried in outer type 0x06 starts with two bytes:
packet type and protocol type.  The first client message used to open a session is
CONNECT/REQ (0x02/0x0B); a successful controller response is CONNECT/ACK
(0x02/0x0A).
"""

from __future__ import annotations

from dataclasses import dataclass

START_BYTE = 0x23  # '#'
END_BYTE = 0x24  # '$'
ESCAPE_BYTE = 0x27  # "'"
NETWORK_PROTOCOL = 0x00
OUTER_TYPE_APPLICATION = 0x06

PACKET_CONNECT = 0x02
PACKET_GLOBAL = 0x06
PACKET_STATUS = 0x07
PACKET_BOOST = 0x08
PACKET_VENTILATION = 0x09
PROTOCOL_DATA = 0x08
PROTOCOL_NACK = 0x09
PROTOCOL_ACK = 0x0A
PROTOCOL_REQ = 0x0B

# GLOBAL identifiers. Runtime/control mappings below use live 4.10 observations
# plus direct Xzense v4.10_RC2 UI-code bindings. The firmware's legacy debug
# name lookup is stale for several shifted setup IDs, so it is not used alone
# as the source of truth. Values are signed 16-bit little-endian on the wire.
GLOBAL_NAMES: dict[int, str] = {
    # These early GLOBAL IDs were labelled using an obsolete firmware debug
    # lookup. Their runtime semantics are not verified for controller 4.10.
    0x00: "UNKNOWN_00",
    0x01: "UNKNOWN_01",
    0x02: "UNKNOWN_02",
    0x03: "UNKNOWN_03",
    0x04: "PANEL_BATTERY_PERCENT_INFERRED",
    0x05: "SIGNAL_STRENGTH_POWER_UNIT_INFERRED",
    0x18: "MY_STATE_UNVERIFIED",
    0x19: "DEVICE_STATE",
    0x1A: "STATE_TIMER",
    0x1B: "AIR_PRESSURE",
    0x1C: "INSIDE_TEMP",
    0x1D: "OUTSIDE_TEMP",
    0x1E: "CHIMNEY_TEMP",
    0x1F: "FAN_SPEED",
    0x20: "UNKNOWN_20",
    # Interface settings correlated directly against the physical panel.
    0x32: "SOUND",
    0x33: "CONTRAST",
    0x34: "BRIGHTNESS",
    0x35: "UNKNOWN_35",
    0x36: "UNKNOWN_36",
    # Setup/service settings correlated directly against panel values.
    0x4B: "START_TEMP",
    0x4C: "STOP_TEMP",
    0x4D: "BOOST_TIME",
    0x4E: "AFTERRUN_TIME",
    0x4F: "BOOST_SPEED",
    0x50: "USER_FAN_SPEED",
    0x51: "ACTUAL_DRAFT",
    0x52: "BOOST_STOP_TEMP",
    0x53: "CHIMNEY_DRAFT_SETPOINT",
    0x54: "MIN_FAN_VOLTAGE",
    0x55: "SYSTEM_CONTROL",
    0x56: "TEMPERATURE_SENSOR",
    0x57: "EXTERN_START",
    0x58: "ALARM_SETPOINT",
    0x59: "REBOOST_TIME",
    0x5A: "EXTERN_FAN_SPEED",
    0x5B: "BURNOUT_TIMEOUT",
}

# Generous safety bound; real Xzense messages are much smaller.
MAX_BODY_SIZE = 4096

_PACKET_NAMES = {
    0x00: "DISCOVER",
    0x01: "EXT_DISCOVER",
    0x02: "CONNECT",
    0x03: "EXT_CONNECT",
    0x04: "DISCONNECT",
    0x05: "ALIVE",
    0x06: "GLOBAL",
    0x07: "STATUS",
    0x08: "BOOST",
    0x09: "VENTILATION",
    0x0A: "RANGETEST",
    0x0B: "FACTORY_RESET",
    0x0C: "FILE_TRANSFER",
    0x0D: "TIMESYNC",
    0x0E: "CONNECTED_PEERS",
}

_PROTOCOL_NAMES = {
    0x06: "TIMEOUT",
    0x07: "TYPE_7",
    0x08: "DATA",
    0x09: "NACK",
    0x0A: "ACK",
    0x0B: "REQ",
}


def crc16_ccitt_false(data: bytes) -> int:
    """Return CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF)."""
    crc = 0xFFFF
    for value in data:
        crc ^= value << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def _escape(data: bytes) -> bytes:
    """Escape reserved bytes as implemented by the Xzense firmware."""
    encoded = bytearray()
    for value in data:
        if value in (START_BYTE, END_BYTE, ESCAPE_BYTE):
            encoded.extend((ESCAPE_BYTE, value | 0x80))
        else:
            encoded.append(value)
    return bytes(encoded)


def build_frame(outer_type: int, payload: bytes) -> bytes:
    """Build one complete Xzense BLE serial frame."""
    if not 0 <= outer_type <= 0xFF:
        raise ValueError("outer_type must fit in one byte")

    body = bytes((NETWORK_PROTOCOL, outer_type)) + bytes(payload)
    if len(body) > 0xFFFF:
        raise ValueError("Xzense body is too large")

    checksum = crc16_ccitt_false(body)
    # Firmware escapes only the application payload and CRC.  The fixed header
    # (network + outer type) is emitted directly.
    escaped_tail = _escape(bytes(payload) + checksum.to_bytes(2, "little"))
    return (
        bytes((START_BYTE,))
        + len(body).to_bytes(2, "little")
        + bytes((NETWORK_PROTOCOL, outer_type))
        + escaped_tail
        + bytes((END_BYTE,))
    )


def build_connect_request(pin: str, client_name: str = "HomeAssistant") -> bytes:
    """Build the application CONNECT/REQ frame.

    The first payload field is the four-hex-digit Xzense application PIN as a
    little-endian 16-bit integer.  The following 32-bit time field is deliberately
    zero in this experimental client so connecting Home Assistant cannot change
    the controller clock.  We also omit the optional trailing time word.
    """
    try:
        pin_value = int(pin, 16)
    except (TypeError, ValueError) as err:
        raise ValueError("PIN must be four hexadecimal digits") from err
    if not 0 <= pin_value <= 0xFFFF or len(pin) != 4:
        raise ValueError("PIN must be four hexadecimal digits")

    name = client_name.encode("ascii", errors="strict")
    if len(name) > 0xFF:
        raise ValueError("client_name is too long")

    inner = (
        bytes((PACKET_CONNECT, PROTOCOL_REQ))
        + pin_value.to_bytes(2, "little")
        + b"\x00\x00\x00\x00"  # time field disabled/safe
        + bytes((len(name),))
        + name
    )
    return build_frame(OUTER_TYPE_APPLICATION, inner)


def build_global_request(session_id: int, global_id: int, value: int) -> bytes:
    """Build a GLOBAL/REQ write frame.

    The exact shape is corroborated by the public Xzense BLE capture: packet
    GLOBAL (0x06), protocol REQ (0x0B), session-id LE32, global-id U8 and
    signed value I16 little-endian.  This helper only encodes the transport;
    individual feature mappings remain disabled until their semantics/scaling
    are verified.
    """
    if not 0 <= session_id <= 0xFFFFFFFF:
        raise ValueError("session_id must fit in 32 bits")
    if not 0 <= global_id <= 0xFF:
        raise ValueError("global_id must fit in one byte")
    if not -32768 <= value <= 32767:
        raise ValueError("GLOBAL value must fit signed int16")
    inner = (
        bytes((PACKET_GLOBAL, PROTOCOL_REQ))
        + session_id.to_bytes(4, "little")
        + bytes((global_id,))
        + value.to_bytes(2, "little", signed=True)
    )
    return build_frame(OUTER_TYPE_APPLICATION, inner)


def build_boost_request(session_id: int, enabled: bool, inside_temp_raw: int) -> bytes:
    """Build a BOOST/REQ frame recovered from the bundled controller firmware.

    Static firmware analysis proves packet type 0x08 is BOOST. Its request handler
    reads a one-byte start/stop flag followed by a signed 16-bit inside-temperature
    value, and updates the same inside-temperature global (0x1C) before processing
    the request. The common application request prefix is packet/protocol followed
    by the active little-endian session ID, as already verified for STATUS/GLOBAL.

    The exact BOOST request was subsequently live-verified on the physical controller.
    """
    if not 0 <= session_id <= 0xFFFFFFFF:
        raise ValueError("session_id must fit in 32 bits")
    if not -32768 <= inside_temp_raw <= 32767:
        raise ValueError("inside_temp_raw must fit signed int16")
    inner = (
        bytes((PACKET_BOOST, PROTOCOL_REQ))
        + session_id.to_bytes(4, "little")
        + bytes((1 if enabled else 0,))
        + inside_temp_raw.to_bytes(2, "little", signed=True)
    )
    return build_frame(OUTER_TYPE_APPLICATION, inner)


def build_ventilation_request(session_id: int, enabled: bool) -> bytes:
    """Build the firmware-recovered VENTILATION/REQ start/stop frame.

    Static controller-firmware analysis identifies packet type 0x09 as
    VENTILATION and its request payload as the active session ID followed by a
    one-byte start/stop flag. The controller returns ACK/NACK and remains the
    authority for whether ventilation is allowed in the current state.
    """
    if not 0 <= session_id <= 0xFFFFFFFF:
        raise ValueError("session_id must fit in 32 bits")
    inner = (
        bytes((PACKET_VENTILATION, PROTOCOL_REQ))
        + session_id.to_bytes(4, "little")
        + bytes((1 if enabled else 0,))
    )
    return build_frame(OUTER_TYPE_APPLICATION, inner)


SYSTEM_CONTROL_VALUE_TO_NAME: dict[int, str] = {
    0: "Manual",
    1: "eXotelligence",
    2: "Pressure controlled",
}
SYSTEM_CONTROL_NAME_TO_VALUE: dict[str, int] = {
    name: value for value, name in SYSTEM_CONTROL_VALUE_TO_NAME.items()
}


def build_status_request(session_id: int) -> bytes:
    """Build the read-only STATUS/REQ frame used by the official client.

    The request is packet type STATUS (0x07), protocol REQ (0x0B), followed by
    the four-byte little-endian application session ID returned by CONNECT/ACK.
    This exact shape is corroborated by a public Xzense Bluetooth capture.
    """
    if not 0 <= session_id <= 0xFFFFFFFF:
        raise ValueError("session_id must fit in 32 bits")
    inner = bytes((PACKET_STATUS, PROTOCOL_REQ)) + session_id.to_bytes(4, "little")
    return build_frame(OUTER_TYPE_APPLICATION, inner)


@dataclass(frozen=True, slots=True)
class XzenseStatusData:
    """Decoded fields from the verified 14-byte STATUS/ACK payload.

    v0.4.3 incorporates the third synchronized live snapshot, taken while the
    controller was explicitly confirmed to be in Afterrun, plus the user's
    direct confirmation that the trailing value 1011 is ambient air pressure
    in hPa. The second field reset at the state transition and then counted up
    roughly once per second, proving it is time in the current state.

    Layout::

        u8   device_state        == GLOBAL 0x19 DEVICE_STATE
        i16  state_timer         == GLOBAL 0x1A STATE_TIMER
        i16  fan_speed           == GLOBAL 0x1F FAN_SPEED
        i16  chimney_temp_x10    == GLOBAL 0x1E CHIMNEY_TEMP
        i16  outside_temp_x10    == GLOBAL 0x1D OUTSIDE_TEMP
        i16  inside_temp_x10     == GLOBAL 0x1C INSIDE_TEMP
        i16  air_pressure_hpa    == GLOBAL 0x1B AIR_PRESSURE
        u8   flags               meaning not yet identified

    GLOBAL 0x20 remains deliberately unidentified.
    """

    raw: bytes
    device_state: int
    state_timer: int
    fan_speed: int
    chimney_temperature_raw: int
    outside_temperature_raw: int
    inside_temperature_raw: int
    air_pressure_hpa: int
    flags: int

    @property
    def state_selector(self) -> int:
        return self.device_state

    @property
    def auxiliary_raw(self) -> int:
        return self.state_timer

    @property
    def flag(self) -> int:
        return self.flags

    @property
    def chimney_temperature(self) -> float:
        return self.chimney_temperature_raw / 10.0

    @property
    def outside_temperature(self) -> float:
        return self.outside_temperature_raw / 10.0

    @property
    def inside_temperature(self) -> float:
        return self.inside_temperature_raw / 10.0


DEVICE_STATE_NAMES: dict[int, str] = {
    # Xzense v4.10_RC2 chimney-state UI dispatch, combined with live states.
    # State 3 (Boosting) and 6 (Afterrun) are additionally live-verified.
    0: "Offline",
    1: "Setup",
    2: "Ready for lighting",
    3: "Boosting",
    4: "Operation",
    5: "Burnout",
    6: "Afterrun",
    7: "Refueling",
    8: "Ventilation",
    9: "Error",
    10: "Upgrading",
}


def device_state_name(value: int | None) -> str | None:
    """Return a friendly operating-state name where the mapping is known."""
    if value is None:
        return None
    return DEVICE_STATE_NAMES.get(value, f"Unknown ({value})")


def decode_status_data(
    frame: "XzenseFrame", session_id: int | None = None
) -> XzenseStatusData | None:
    """Decode the verified 14-byte STATUS/DATA or STATUS/ACK payload."""
    if (
        frame.outer_type != OUTER_TYPE_APPLICATION
        or frame.packet_type != PACKET_STATUS
        or frame.protocol_type not in (PROTOCOL_DATA, PROTOCOL_ACK)
    ):
        return None

    data = frame.application_payload
    # Some firmware variants may prefix the application session ID. Accept that
    # conservatively; the live controller capture has no such prefix.
    if (
        session_id is not None
        and len(data) >= 18
        and int.from_bytes(data[:4], "little") == session_id
    ):
        data = data[4:]
    if len(data) < 14:
        return None

    body = bytes(data[:14])

    def i16(offset: int) -> int:
        return int.from_bytes(body[offset : offset + 2], "little", signed=True)

    return XzenseStatusData(
        raw=body,
        device_state=body[0],
        state_timer=i16(1),
        fan_speed=i16(3),
        chimney_temperature_raw=i16(5),
        outside_temperature_raw=i16(7),
        inside_temperature_raw=i16(9),
        air_pressure_hpa=i16(11),
        flags=body[13],
    )


def decode_global_data(
    frame: "XzenseFrame", session_id: int | None = None
) -> dict[int, int] | None:
    """Decode GLOBAL/DATA entries as ``global_id -> signed int16 value``.

    Controller firmware packs each global as exactly three bytes: one ID byte
    followed by a signed little-endian 16-bit value. Some variants may prefix a
    four-byte session ID, so that form is accepted as well.
    """
    if (
        frame.outer_type != OUTER_TYPE_APPLICATION
        or frame.packet_type != PACKET_GLOBAL
        or frame.protocol_type != PROTOCOL_DATA
    ):
        return None

    data = frame.application_payload
    if (
        session_id is not None
        and len(data) >= 4
        and (len(data) - 4) % 3 == 0
        and int.from_bytes(data[:4], "little") == session_id
    ):
        data = data[4:]
    if len(data) % 3:
        return None

    result: dict[int, int] = {}
    for offset in range(0, len(data), 3):
        global_id = data[offset]
        value = int.from_bytes(data[offset + 1 : offset + 3], "little", signed=True)
        result[global_id] = value
    return result


def global_name(global_id: int) -> str:
    """Return a stable human-readable name for one global identifier."""
    return GLOBAL_NAMES.get(global_id, f"GLOBAL_0x{global_id:02X}")


@dataclass(frozen=True, slots=True)
class XzenseFrame:
    """A CRC-validated Xzense wire frame."""

    raw: bytes
    size: int
    network_protocol: int
    outer_type: int
    payload: bytes
    checksum: int

    @property
    def hex(self) -> str:
        return self.raw.hex()

    @property
    def payload_hex(self) -> str:
        return self.payload.hex()

    @property
    def packet_type(self) -> int | None:
        return self.payload[0] if len(self.payload) >= 1 else None

    @property
    def protocol_type(self) -> int | None:
        return self.payload[1] if len(self.payload) >= 2 else None

    @property
    def application_payload(self) -> bytes:
        return self.payload[2:] if len(self.payload) >= 2 else b""

    @property
    def packet_type_name(self) -> str | None:
        value = self.packet_type
        return _PACKET_NAMES.get(value, f"0x{value:02X}") if value is not None else None

    @property
    def protocol_type_name(self) -> str | None:
        value = self.protocol_type
        return _PROTOCOL_NAMES.get(value, f"0x{value:02X}") if value is not None else None

    @property
    def is_connect_ack(self) -> bool:
        return (
            self.outer_type == OUTER_TYPE_APPLICATION
            and self.packet_type == PACKET_CONNECT
            and self.protocol_type == PROTOCOL_ACK
            and len(self.application_payload) >= 8
        )

    @property
    def is_connect_nack(self) -> bool:
        return (
            self.outer_type == OUTER_TYPE_APPLICATION
            and self.packet_type == PACKET_CONNECT
            and self.protocol_type == PROTOCOL_NACK
        )

    @property
    def session_id(self) -> int | None:
        if not self.is_connect_ack:
            return None
        return int.from_bytes(self.application_payload[0:4], "little")

    @property
    def connect_version(self) -> int | None:
        if not self.is_connect_ack:
            return None
        return int.from_bytes(self.application_payload[4:6], "little")

    @property
    def connect_flag(self) -> int | None:
        if not self.is_connect_ack:
            return None
        return self.application_payload[6]


class XzenseFrameParser:
    """Incremental parser for the escaped serial stream carried over BLE."""

    def __init__(self) -> None:
        self._buffer = bytearray()
        self.discarded_bytes = 0
        self.invalid_frames = 0
        self.crc_errors = 0

    def reset(self) -> None:
        self._buffer.clear()
        self.discarded_bytes = 0
        self.invalid_frames = 0
        self.crc_errors = 0

    def _drop_start(self) -> None:
        self.invalid_frames += 1
        self.discarded_bytes += 1
        del self._buffer[0]

    def feed(self, data: bytes) -> list[XzenseFrame]:
        """Feed one notification fragment and return every complete valid frame."""
        if data:
            self._buffer.extend(data)

        frames: list[XzenseFrame] = []

        while self._buffer:
            try:
                start = self._buffer.index(START_BYTE)
            except ValueError:
                self.discarded_bytes += len(self._buffer)
                self._buffer.clear()
                break

            if start:
                self.discarded_bytes += start
                del self._buffer[:start]

            # SOT + size(2) + network + outer type
            if len(self._buffer) < 5:
                break

            size = int.from_bytes(self._buffer[1:3], "little")
            if size < 2 or size > MAX_BODY_SIZE:
                self._drop_start()
                continue

            # Body contains two fixed bytes (network + outer type).  The
            # remaining payload and the two CRC bytes may be escaped.  We decode
            # exactly size+2 bytes from raw offset 3 before expecting EOT.
            decoded = bytearray()
            raw_pos = 3
            incomplete = False
            while len(decoded) < size + 2:
                if raw_pos >= len(self._buffer):
                    incomplete = True
                    break
                value = self._buffer[raw_pos]

                # Only bytes after the fixed network/type header are escaped.
                if len(decoded) >= 2 and value == ESCAPE_BYTE:
                    if raw_pos + 1 >= len(self._buffer):
                        incomplete = True
                        break
                    decoded.append(self._buffer[raw_pos + 1] & 0x7F)
                    raw_pos += 2
                else:
                    decoded.append(value)
                    raw_pos += 1

            if incomplete:
                break

            if raw_pos >= len(self._buffer):
                break
            if self._buffer[raw_pos] != END_BYTE:
                self._drop_start()
                continue

            raw_end = raw_pos + 1
            raw_frame = bytes(self._buffer[:raw_end])
            del self._buffer[:raw_end]

            body = bytes(decoded[:size])
            received_crc = int.from_bytes(decoded[size : size + 2], "little")
            calculated_crc = crc16_ccitt_false(body)
            if received_crc != calculated_crc:
                self.invalid_frames += 1
                self.crc_errors += 1
                continue

            network_protocol = body[0]
            if network_protocol != NETWORK_PROTOCOL:
                self.invalid_frames += 1
                continue

            frames.append(
                XzenseFrame(
                    raw=raw_frame,
                    size=size,
                    network_protocol=network_protocol,
                    outer_type=body[1],
                    payload=body[2:],
                    checksum=received_crc,
                )
            )

        return frames
