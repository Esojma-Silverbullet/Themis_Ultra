"""Diagnostics support for Bookoo."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.core import HomeAssistant

from . import BookooConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    scale = coordinator.scale

    # collect all data sources
    return {
        "model": scale.model,
        "device_state": (
            asdict(scale.device_state) if scale.device_state is not None else ""
        ),
        "mac": scale.mac,
        "last_disconnect_time": scale.last_disconnect_time,
        "timer": scale.timer,
        "weight": scale.weight,
        "flow_rate": scale.flow_rate,
        "powder_weight": scale.powder_weight,
        "automatic_mode_state": (
            asdict(scale.automatic_mode_state)
            if scale.automatic_mode_state is not None
            else ""
        ),
    }
