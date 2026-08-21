"""Tests für Firmware-4-Befehle und Zustandsübernahme."""

import pytest
from aiobookoo_ultra.bookooscale import BookooScale
from aiobookoo_ultra.const import CHARACTERISTIC_UUID_COMMAND, AutomaticModeEvent


def packet_with_checksum(data: list[int]) -> bytearray:
    """Ergänze die XOR-Prüfsumme eines 19-Byte-Paketkörpers."""
    assert len(data) == 19
    checksum = 0
    for byte in data:
        checksum ^= byte
    return bytearray([*data, checksum])


@pytest.mark.asyncio
async def test_set_powder_weight_builds_firmware_4_command() -> None:
    """Pulvergewicht wird mit Faktor zehn und Big-Endian übertragen."""
    scale = BookooScale("AA:BB:CC:DD:EE:FF")
    scale.connected = True

    await scale.set_powder_weight(20.1)

    characteristic, payload = scale._queue.get_nowait()
    assert characteristic == CHARACTERISTIC_UUID_COMMAND
    assert payload == bytearray([0x03, 0x0A, 0x0D, 0x00, 0xC9, 0xCD])


@pytest.mark.asyncio
@pytest.mark.parametrize("grams", [0.0, 999.1])
async def test_set_powder_weight_rejects_out_of_range_values(grams: float) -> None:
    """Nur der offiziell dokumentierte Bereich wird gesendet."""
    scale = BookooScale("AA:BB:CC:DD:EE:FF")
    scale.connected = True

    with pytest.raises(ValueError, match="between 0.1 and 999.0"):
        await scale.set_powder_weight(grams)


@pytest.mark.asyncio
async def test_shutdown_builds_firmware_4_command() -> None:
    """Der Ausschaltbefehl verwendet Kommando 15 und eine korrekte Prüfsumme."""
    scale = BookooScale("AA:BB:CC:DD:EE:FF")
    scale.connected = True

    await scale.shutdown()

    characteristic, payload = scale._queue.get_nowait()
    assert characteristic == CHARACTERISTIC_UUID_COMMAND
    assert payload == bytearray([0x03, 0x0A, 0x15, 0x00, 0x00, 0x1C])


@pytest.mark.asyncio
async def test_received_firmware_4_packets_update_scale_state() -> None:
    """Pulvergewicht und Automatikabschluss stehen Aufrufern sofort zur Verfügung."""
    notifications = 0

    def notify() -> None:
        nonlocal notifications
        notifications += 1

    scale = BookooScale("AA:BB:CC:DD:EE:FF", notify_callback=notify)
    powder_packet = packet_with_checksum(
        [0x03, 0x0F, 0x2B, 0x00, 0x07, 0xDA, *([0] * 13)]
    )
    automatic_packet = packet_with_checksum(
        [
            0x03,
            0x0D,
            0x00,
            0x00,
            0x71,
            0x48,
            0x2B,
            0x00,
            0x0F,
            0x13,
            0x2B,
            0x00,
            0xC0,
            *([0] * 6),
        ]
    )

    await scale.on_bluetooth_data_received(None, powder_packet)  # type: ignore[arg-type]
    await scale.on_bluetooth_data_received(None, automatic_packet)  # type: ignore[arg-type]

    assert scale.powder_weight == 20.1
    assert scale.automatic_mode_state is not None
    assert scale.automatic_mode_state.event is AutomaticModeEvent.STOPPED
    assert scale.automatic_mode_state.timer == 29.0
    assert scale.automatic_mode_state.weight == 38.59
    assert scale.automatic_mode_state.result == 1.92
    assert scale.automatic_mode_event_sequence == 1
    assert notifications == 2
