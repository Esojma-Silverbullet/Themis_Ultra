"""Offizielles Package für das Bookoo-Themis-Ultra-Protokoll."""

from .bookooscale import BookooAutomaticModeState, BookooDeviceState, BookooScale
from .const import (
    AUTOMATIC_MODE_BYTE2,
    CHARACTERISTIC_UUID_COMMAND,
    CHARACTERISTIC_UUID_WEIGHT,
    CMD_BYTE1_PRODUCT_NUMBER,
    CMD_BYTE2_TYPE,
    MESSAGE_LENGTH,
    POWDER_WEIGHT_BYTE2,
    SCALE_START_NAMES,
    SERVICE_UUID,
    WEIGHT_BYTE1,
    WEIGHT_BYTE2,
    AutomaticModeEvent,
    UnitMass,
)
from .decode import (
    BookooAutomaticModeMessage,
    BookooDecodedMessage,
    BookooMessage,
    BookooPowderWeightMessage,
    decode,
)
from .exceptions import (
    BookooDeviceNotFound,
    BookooError,
    BookooMessageError,
    BookooMessageTooLong,
    BookooMessageTooShort,
    BookooScaleException,
    BookooUnknownDevice,
)
from .helpers import find_bookoo_devices, is_bookoo_scale, scan

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
    "BookooAutomaticModeMessage",
    "BookooAutomaticModeState",
    "BookooDecodedMessage",
    "BookooDeviceNotFound",
    "BookooDeviceState",
    "BookooError",
    "BookooMessage",
    "BookooMessageError",
    "BookooMessageTooLong",
    "BookooMessageTooShort",
    "BookooPowderWeightMessage",
    "BookooScale",
    "BookooScaleException",
    "BookooUnknownDevice",
    "UnitMass",
    "decode",
    "find_bookoo_devices",
    "is_bookoo_scale",
    "scan",
]
