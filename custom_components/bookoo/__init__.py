"""Initialize the Bookoo component."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import BookooConfigEntry, BookooCoordinator

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: BookooConfigEntry) -> bool:
    """Set up bookoo as config entry."""

    coordinator = BookooCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: BookooConfigEntry) -> bool:
    """Unload a config entry."""

    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
