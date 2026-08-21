"""Dekodierung der Nachrichten des Themis-Ultra-Protokolls."""

import logging
from dataclasses import dataclass

from .const import (
    AUTOMATIC_MODE_BYTE2,
    MESSAGE_LENGTH,
    POWDER_WEIGHT_BYTE2,
    WEIGHT_BYTE1,
    WEIGHT_BYTE2,
    AutomaticModeEvent,
    UnitMass,
)
from .exceptions import BookooMessageError, BookooMessageTooLong, BookooMessageTooShort

_LOGGER = logging.getLogger("aiobookoo_ultra")


def _validate_checksum(payload: bytearray) -> None:
    """Prüfe die XOR-Prüfsumme eines vollständigen Pakets."""
    checksum = 0
    for byte in payload[:-1]:
        checksum ^= byte
    if checksum != payload[-1]:
        raise BookooMessageError(payload, "Checksum mismatch")


def _decode_sign(payload: bytearray, index: int, value_name: str) -> int:
    """Dekodiere ein Vorzeichenbyte des Ultra-Protokolls."""
    if payload[index] in (0x2B, 0x00):
        return 1
    if payload[index] == 0x2D:
        return -1
    raise BookooMessageError(payload, f"Unsupported {value_name} sign byte")


@dataclass
class BookooMessage:
    """Inhalt eines laufenden Gewichtspakets der Bookoo Themis Ultra."""

    timer: float
    unit: UnitMass
    weight: float
    flow_rate: float
    battery: int
    standby_time: float
    buzzer_gear: int
    flow_rate_smoothing: int

    def __init__(self, payload: bytearray) -> None:
        """Initialisiere eine laufende Gewichtsnachricht."""
        _validate_checksum(payload)

        self.timer = int.from_bytes(payload[2:5], byteorder="big") / 1000.0
        if payload[5] == 0x01:
            self.unit = UnitMass.GRAMS
        elif payload[5] == 0x02:
            self.unit = UnitMass.OUNCES
        else:
            raise BookooMessageError(payload, "Unsupported unit byte")

        weight_sign = _decode_sign(payload, 6, "weight")
        self.weight = (
            int.from_bytes(payload[7:10], byteorder="big") / 100.0 * weight_sign
        )

        flow_sign = _decode_sign(payload, 10, "flow")
        self.flow_rate = (
            int.from_bytes(payload[11:13], byteorder="big") / 100.0 * flow_sign
        )
        self.battery = payload[13]
        self.standby_time = int.from_bytes(payload[14:16], byteorder="big") / 10.0
        self.buzzer_gear = payload[16]
        self.flow_rate_smoothing = payload[17]


@dataclass
class BookooPowderWeightMessage:
    """Von der Waage gemeldetes Pulvergewicht."""

    powder_weight: float

    def __init__(self, payload: bytearray) -> None:
        """Initialisiere eine Pulvergewichtsnachricht."""
        _validate_checksum(payload)
        sign = _decode_sign(payload, 2, "powder weight")
        self.powder_weight = (
            int.from_bytes(payload[3:6], byteorder="big") / 100.0 * sign
        )


@dataclass
class BookooAutomaticModeMessage:
    """Ereignis- und Abschlussdaten des Automatikmodus."""

    event: AutomaticModeEvent
    timer: float
    weight: float
    result: float

    def __init__(self, payload: bytearray) -> None:
        """Initialisiere eine Automatikmodus-Nachricht."""
        _validate_checksum(payload)
        try:
            self.event = AutomaticModeEvent(payload[2])
        except ValueError as ex:
            raise BookooMessageError(
                payload, "Unsupported automatic mode event byte"
            ) from ex

        self.timer = int.from_bytes(payload[3:6], byteorder="big") / 1000.0
        weight_sign = _decode_sign(payload, 6, "weight")
        self.weight = (
            int.from_bytes(payload[7:10], byteorder="big") / 100.0 * weight_sign
        )
        result_sign = _decode_sign(payload, 10, "result")
        self.result = (
            int.from_bytes(payload[11:13], byteorder="big") / 100.0 * result_sign
        )


BookooDecodedMessage = (
    BookooMessage | BookooPowderWeightMessage | BookooAutomaticModeMessage
)


def decode(byte_msg: bytearray) -> tuple[BookooDecodedMessage | None, bytearray]:
    """Dekodiere genau ein vollständiges Ultra-Protokollpaket."""
    if len(byte_msg) < MESSAGE_LENGTH:
        raise BookooMessageTooShort(byte_msg)
    if len(byte_msg) > MESSAGE_LENGTH:
        raise BookooMessageTooLong(byte_msg)

    if byte_msg[0] != WEIGHT_BYTE1:
        _LOGGER.debug("Full message: %s", byte_msg)
        return (None, byte_msg)

    message_type = byte_msg[1]
    if message_type == WEIGHT_BYTE2:
        return (BookooMessage(byte_msg), bytearray())
    if message_type == POWDER_WEIGHT_BYTE2:
        return (BookooPowderWeightMessage(byte_msg), bytearray())
    if message_type == AUTOMATIC_MODE_BYTE2:
        return (BookooAutomaticModeMessage(byte_msg), bytearray())

    _LOGGER.debug("Full message: %s", byte_msg)
    return (None, byte_msg)


__all__ = [
    "BookooAutomaticModeMessage",
    "BookooDecodedMessage",
    "BookooMessage",
    "BookooPowderWeightMessage",
    "decode",
]
