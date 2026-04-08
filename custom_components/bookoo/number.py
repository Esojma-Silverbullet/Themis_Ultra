"""Number entities for Bookoo scales."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

from aiobookoo_ultra.bookooscale import BookooScale
from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
)
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
        adjusted_value = (
            int(value * 60)
            if "seconds" in method_name
            else int(value)
        )
        result = method(adjusted_value)
        if inspect.isawaitable(result):
            await result
        return True
    return False


def _get_auto_off_minutes(scale: BookooScale) -> float | None:
    """Return the auto-off duration in minutes."""
    for source in (scale, scale.device_state):
        if source is None:
            continue
        for name in ("auto_off_time", "auto_off_duration", "auto_off", "auto_off_seconds"):
            if not hasattr(source, name):
                continue
            value = getattr(source, name)
            if value is None:
                continue
            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                continue
            if name == "auto_off_seconds":
                return numeric_value / 60.0
            return numeric_value
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
        native_unit_of_measurement=UnitOfTime.MINUTES,
        native_step=1,
        native_min_value=5,
        native_max_value=30,
        entity_category=EntityCategory.CONFIG,
        value_fn=_get_auto_off_minutes,
        setter_methods=(
            "set_auto_off_duration",
            "set_auto_off_time",
            "set_auto_off",
            "set_auto_off_seconds",
        ),
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
