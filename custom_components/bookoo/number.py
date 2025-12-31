"""Number entities for Bookoo scales."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

from aiobookoo_ultra.bookooscale import BookooScale
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberEntityDescription
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BookooConfigEntry
from .entity import BookooEntity

PARALLEL_UPDATES = 0


async def _async_call_first_available(
    scale: BookooScale, method_names: tuple[str, ...], value: float
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


def _get_first_available_value(scale: BookooScale, names: tuple[str, ...]) -> float | None:
    """Return the first available numeric value."""
    for source in (scale, scale.device_state):
        if source is None:
            continue
        for name in names:
            if not hasattr(source, name):
                continue
            value = getattr(source, name)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue
    return None


@dataclass(kw_only=True, frozen=True)
class BookooNumberEntityDescription(NumberEntityDescription):
    """Description for Bookoo number entities."""

    value_fn: Callable[[BookooScale], float | None]
    setter_methods: tuple[str, ...]


NUMBERS: tuple[BookooNumberEntityDescription, ...] = (
    BookooNumberEntityDescription(
        key="auto_off_seconds",
        translation_key="auto_off_seconds",
        device_class=NumberDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        native_step=5,
        native_min_value=0,
        native_max_value=1800,
        entity_category=EntityCategory.CONFIG,
        value_fn=lambda scale: _get_first_available_value(
            scale, ("auto_off_seconds", "auto_off_time", "auto_off")
        ),
        setter_methods=("set_auto_off_seconds", "set_auto_off", "set_auto_off_time"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities."""

    coordinator = entry.runtime_data
    async_add_entities(
        BookooNumber(coordinator, description) for description in NUMBERS
    )


class BookooNumber(BookooEntity, NumberEntity):
    """Representation of a Bookoo number entity."""

    entity_description: BookooNumberEntityDescription

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        return self.entity_description.value_fn(self._scale)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value."""
        success = await _async_call_first_available(
            self._scale, self.entity_description.setter_methods, value
        )
        if not success:
            raise HomeAssistantError("Dieses Gerät unterstützt die Einstellung nicht.")
        self.async_write_ha_state()
