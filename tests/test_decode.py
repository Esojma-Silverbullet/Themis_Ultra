"""Tests für die Firmware-4-Paketdekodierung."""

import pytest
from aiobookoo_ultra.const import AutomaticModeEvent, UnitMass
from aiobookoo_ultra.decode import (
    BookooAutomaticModeMessage,
    BookooMessage,
    BookooPowderWeightMessage,
    decode,
)
from aiobookoo_ultra.exceptions import (
    BookooMessageError,
    BookooMessageTooLong,
    BookooMessageTooShort,
)


def packet_with_checksum(data: list[int]) -> bytearray:
    """Ergänze die XOR-Prüfsumme eines 19-Byte-Paketkörpers."""
    assert len(data) == 19
    checksum = 0
    for byte in data:
        checksum ^= byte
    return bytearray([*data, checksum])


def test_decode_weight_packet_firmware_4() -> None:
    """Einheit, Standby-Skalierung und laufende Messwerte werden korrekt gelesen."""
    payload = packet_with_checksum(
        [
            0x03,
            0x0B,
            0x00,
            0x30,
            0x39,  # 12.345 s
            0x01,  # Gram in firmware 4.0.0
            0x2B,
            0x00,
            0x0F,
            0x13,  # 38.59 g
            0x2B,
            0x00,
            0x7B,  # 1.23 ml/s
            87,
            0x00,
            0x96,  # 15.0 min (Wert * 10)
            3,
            1,
            0,
        ]
    )

    message, remaining = decode(payload)

    assert isinstance(message, BookooMessage)
    assert remaining == bytearray()
    assert message.timer == 12.345
    assert message.unit is UnitMass.GRAMS
    assert message.weight == 38.59
    assert message.flow_rate == 1.23
    assert message.battery == 87
    assert message.standby_time == 15.0
    assert message.buzzer_gear == 3
    assert message.flow_rate_smoothing == 1


def test_decode_ounce_display_unit_keeps_gram_weight_value() -> None:
    """Das Einheit-Byte 02 meldet Ounce, der Zahlenwert bleibt laut Protokoll Gramm."""
    payload = packet_with_checksum(
        [0x03, 0x0B, 0, 0, 0, 0x02, 0x2B, 0, 0, 100, 0x2B, 0, 0, 50, 0, 50, 0, 0, 0]
    )

    message, _ = decode(payload)

    assert isinstance(message, BookooMessage)
    assert message.unit is UnitMass.OUNCES
    assert message.weight == 1.0


def test_decode_powder_weight_packet() -> None:
    """Pulvergewicht aus Pakettyp 0F wird in Gramm dekodiert."""
    payload = packet_with_checksum([0x03, 0x0F, 0x2B, 0x00, 0x07, 0xDA, *([0] * 13)])

    message, remaining = decode(payload)

    assert isinstance(message, BookooPowderWeightMessage)
    assert remaining == bytearray()
    assert message.powder_weight == 20.1


@pytest.mark.parametrize(
    ("event_byte", "event"),
    [
        (0x00, AutomaticModeEvent.STOPPED),
        (0x01, AutomaticModeEvent.STARTED),
        (0x02, AutomaticModeEvent.READY),
        (0x03, AutomaticModeEvent.EXIT_READY),
        (0x04, AutomaticModeEvent.EXIT_DONE),
    ],
)
def test_decode_automatic_mode_packet(
    event_byte: int, event: AutomaticModeEvent
) -> None:
    """Alle dokumentierten Automatikereignisse samt Abschlusswerten werden gelesen."""
    payload = packet_with_checksum(
        [
            0x03,
            0x0D,
            event_byte,
            0x00,
            0x71,
            0x48,  # 29.000 s
            0x2B,
            0x00,
            0x0F,
            0x13,  # 38.59 g
            0x2B,
            0x00,
            0xC0,  # 1.92 Ergebnis
            *([0] * 6),
        ]
    )

    message, remaining = decode(payload)

    assert isinstance(message, BookooAutomaticModeMessage)
    assert remaining == bytearray()
    assert message.event is event
    assert message.timer == 29.0
    assert message.weight == 38.59
    assert message.result == 1.92


def test_decode_rejects_invalid_checksum() -> None:
    """Beschädigte bekannte Pakete werden nicht als Messwerte übernommen."""
    payload = packet_with_checksum([0x03, 0x0F, 0x2B, 0, 0, 100, *([0] * 13)])
    payload[-1] ^= 0xFF

    with pytest.raises(BookooMessageError, match="Checksum mismatch"):
        decode(payload)


def test_decode_rejects_wrong_lengths() -> None:
    """Das Protokoll akzeptiert ausschließlich vollständige 20-Byte-Pakete."""
    with pytest.raises(BookooMessageTooShort):
        decode(bytearray(19))
    with pytest.raises(BookooMessageTooLong):
        decode(bytearray(21))


def test_decode_returns_unknown_packet_unchanged() -> None:
    """Unbekannte Pakettypen werden ohne erfundene Daten weitergereicht."""
    payload = bytearray([0x03, 0x7F, *([0] * 18)])

    message, remaining = decode(payload)

    assert message is None
    assert remaining == payload
