"""Switch entities for Bookoo scales."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

from aiobookoo_ultra.bookooscale import BookooScale
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BookooConfigEntry
from .entity import BookooEntity

PARALLEL_UPDATES = 0


async def _async_call_first_available(
    scale: BookooScale, method_names: tuple[str, ...], value: bool
) -> bool:
    """Call the first available setter on the scale."""
    for method_name in method_names:
        method = getattr(scale, method_name, None)
        if method is None:
            continue
        result = method(value)
        if inspect.isawaitable(result):
            await result
        return True
    return False


def _get_first_available_bool(
    scale: BookooScale, names: tuple[str, ...]
) -> bool | None:
    """Return the first existing boolean value on the scale/device state."""
    for source in (scale, scale.device_state):
        if source is None:
            continue
        for name in names:
            if not hasattr(source, name):
                continue
            value = getattr(source, name)
            if value is not None:
                return bool(value)
    return None


@dataclass(kw_only=True, frozen=True)
class BookooSwitchEntityDescription(SwitchEntityDescription):
    """Description for Bookoo switch entities."""

    is_on_fn: Callable[[BookooScale], bool | None]
    setter_methods: tuple[str, ...]


SWITCHES: tuple[BookooSwitchEntityDescription, ...] = (
    BookooSwitchEntityDescription(
        key="flow_smoothing_enabled",
        translation_key="flow_smoothing_enabled",
        entity_category=EntityCategory.CONFIG,
        is_on_fn=lambda scale: _get_first_available_bool(
            scale, ("flow_smoothing_enabled", "flow_smoothing")
        ),
        setter_methods=("set_flow_smoothing_enabled", "set_flow_smoothing"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switch entities."""

    coordinator = entry.runtime_data
    async_add_entities(
        BookooFlowSmoothingSwitch(coordinator, description)
        for description in SWITCHES
    )


class BookooFlowSmoothingSwitch(BookooEntity, SwitchEntity):
    """Representation of a Bookoo switch."""

    entity_description: BookooSwitchEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return switch state."""
        return self.entity_description.is_on_fn(self._scale)

    async def async_turn_on(self, **kwargs: object) -> None:
        """Turn the switch on."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs: object) -> None:
        """Turn the switch off."""
        await self._async_set_state(False)

    async def _async_set_state(self, value: bool) -> None:
        success = await _async_call_first_available(
            self._scale, self.entity_description.setter_methods, value
        )
        if not success:
            raise HomeAssistantError("Dieses Gerät unterstützt die Einstellung nicht.")
        self.async_write_ha_state()
