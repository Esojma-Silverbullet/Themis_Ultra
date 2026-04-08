"""Dekodierung der Gewichtsnachrichten des Ultra-Protokolls."""

from dataclasses import dataclass
import logging

from .const import UnitMass, WEIGHT_BYTE1, WEIGHT_BYTE2
from .exceptions import BookooMessageError, BookooMessageTooLong, BookooMessageTooShort

_LOGGER = logging.getLogger("aiobookoo_ultra")


@dataclass
class BookooMessage:
    """Inhalt eines Gewichtspakets der Bookoo Themis Ultra."""

    def __init__(self, payload: bytearray) -> None:
        """Initialisiere eine Nachricht des Ultra-Protokolls."""

        self.timer: float | None = (
            int.from_bytes(
                payload[2:5],
                byteorder="big",  # time in milliseconds
            )
            / 1000.0  # time in seconds
        )
        self.unit: UnitMass
        if payload[5] == 0x01:
            self.unit = UnitMass.OUNCES
        elif payload[5] == 0x02:
            self.unit = UnitMass.GRAMS
        else:
            raise BookooMessageError(payload, "Unsupported unit byte")

        weight_sign = 1 if payload[6] in (0x2B, 0x00) else -1 if payload[6] == 0x2D else None
        if weight_sign is None:
            raise BookooMessageError(payload, "Unsupported weight sign byte")
        self.weight = (
            int.from_bytes(payload[7:10], byteorder="big") / 100.0 * weight_sign
        )  # Convert to grams

        flow_sign = 1 if payload[10] in (0x2B, 0x00) else -1 if payload[10] == 0x2D else None
        if flow_sign is None:
            raise BookooMessageError(payload, "Unsupported flow sign byte")
        self.flow_rate = (
            int.from_bytes(payload[11:13], byteorder="big") / 100.0 * flow_sign
        )  # Convert to ml
        self.battery = payload[13]  # battery level in percent
        self.standby_time = int.from_bytes(payload[14:16], byteorder="big")  # minutes
        self.buzzer_gear = payload[16]
        self.flow_rate_smoothing = payload[17]  # 0 = off, 1 = on
        self.stop_condition = payload[18]

        # Verify checksum
        checksum = 0
        for byte in payload[:-1]:
            checksum ^= byte
        if checksum != payload[-1]:
            raise BookooMessageError(payload, "Checksum mismatch")

        # _LOGGER.debug(
        #     "Bookoo Message: unit=%s, weight=%s, time=%s, battery=%s, flowRate=%s, standbyTime=%s, buzzerGear=%s, flowRateSmoothing=%s",
        #     self.unit,
        #     self.weight,
        #     self.timer,
        #     self.battery,
        #     self.flow_rate,
        #     self.standby_time,
        #     self.buzzer_gear,
        #     self.flow_rate_smoothing,
        # )


def decode(byte_msg: bytearray):
    """Return a tuple - first element is the message, or None.

    The second element is the remaining bytes of the message.

    """

    if len(byte_msg) < 20:
        raise BookooMessageTooShort(byte_msg)

    if len(byte_msg) > 20:
        raise BookooMessageTooLong(byte_msg)

    if byte_msg[0] == WEIGHT_BYTE1 and byte_msg[1] == WEIGHT_BYTE2:
        # _LOGGER.debug("Found valid weight Message")
        return (BookooMessage(byte_msg), bytearray())

    _LOGGER.debug("Full message: %s", byte_msg)
    return (None, byte_msg)


__all__ = ["BookooMessage", "decode"]
