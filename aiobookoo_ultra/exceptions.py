"""Ausnahmen für das Ultra-Protokoll."""

from bleak.exc import BleakDeviceNotFoundError, BleakError


class BookooScaleException(Exception):
    """Basisklasse für Ausnahmen des Moduls."""


class BookooDeviceNotFound(BleakDeviceNotFoundError):
    """Exception wenn kein Gerät gefunden wurde."""


class BookooError(BleakError):
    """Exception für allgemeine BLE-Fehler."""


class BookooUnknownDevice(Exception):
    """Exception für unbekannte Geräte."""


class BookooMessageError(Exception):
    """Exception für Nachrichtenfehler."""

    def __init__(self, bytes_recvd: bytearray, message: str) -> None:
        super().__init__()
        self.message = message
        self.bytes_recvd = bytes_recvd


class BookooMessageTooShort(BookooMessageError):
    """Exception für zu kurze Nachrichten."""

    def __init__(self, bytes_recvd: bytearray) -> None:
        super().__init__(bytes_recvd, "Message too short")


class BookooMessageTooLong(BookooMessageError):
    """Exception für zu lange Nachrichten."""

    def __init__(self, bytes_recvd: bytearray) -> None:
        super().__init__(bytes_recvd, "Message too long")


__all__ = [
    "BookooScaleException",
    "BookooDeviceNotFound",
    "BookooError",
    "BookooUnknownDevice",
    "BookooMessageError",
    "BookooMessageTooShort",
    "BookooMessageTooLong",
]
