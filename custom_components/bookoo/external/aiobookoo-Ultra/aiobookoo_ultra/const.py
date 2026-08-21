"""Konstanten des Themis-Ultra-Protokolls."""

from enum import IntEnum, StrEnum
from typing import Final

SCALE_START_NAMES: Final = ["BOOKOO"]
SERVICE_UUID = "00000ffe-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_WEIGHT = "0000ff11-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID_COMMAND = "0000ff12-0000-1000-8000-00805f9b34fb"
CMD_BYTE1_PRODUCT_NUMBER = 0x03  # Command Data BYTE1
CMD_BYTE2_TYPE = 0x0A  # Command Data BYTE2
WEIGHT_BYTE1 = 0x03
WEIGHT_BYTE2 = 0x0B
AUTOMATIC_MODE_BYTE2 = 0x0D
POWDER_WEIGHT_BYTE2 = 0x0F
MESSAGE_LENGTH = 20


class UnitMass(StrEnum):
    """Unterstützte Maßeinheiten."""

    GRAMS = "grams"
    OUNCES = "ounces"


class AutomaticModeEvent(IntEnum):
    """Von der Waage gemeldete Zustände des Automatikmodus."""

    STOPPED = 0x00
    STARTED = 0x01
    READY = 0x02
    EXIT_READY = 0x03
    EXIT_DONE = 0x04


__all__ = [
    "AUTOMATIC_MODE_BYTE2",
    "CHARACTERISTIC_UUID_COMMAND",
    "CHARACTERISTIC_UUID_WEIGHT",
    "CMD_BYTE1_PRODUCT_NUMBER",
    "CMD_BYTE2_TYPE",
    "MESSAGE_LENGTH",
    "POWDER_WEIGHT_BYTE2",
    "SCALE_START_NAMES",
    "SERVICE_UUID",
    "WEIGHT_BYTE1",
    "WEIGHT_BYTE2",
    "AutomaticModeEvent",
    "UnitMass",
]
