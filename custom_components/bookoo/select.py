"""Select entities for Bookoo scales."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

from aiobookoo_ultra.bookooscale import BookooScale
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BookooConfigEntry
from .entity import BookooEntity

PARALLEL_UPDATES = 0


def _get_first_available_value(scale: BookooScale, names: tuple[str, ...]) -> str | None:
    """Return the first existing attribute value on the scale."""
    for name in names:
        value = getattr(scale, name, None)
        if value is not None:
            return str(value)
    if scale.device_state is None:
        return None
    for name in names:
        value = getattr(scale.device_state, name, None)
        if value is not None:
            return str(value)
    return None


async def _async_call_first_available(
    scale: BookooScale, method_names: tuple[str, ...], value: str
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


def _beeper_options(scale: BookooScale) -> list[str]:
    """Return supported beeper levels, fallback to six levels (0-5)."""
    if scale.device_state is not None:
        supported = getattr(scale.device_state, "supported_beeper_levels", None)
        if supported:
            levels: list[str] = []
            for level in supported:
                try:
                    numeric_level = int(level)
                except (TypeError, ValueError):
                    continue
                if 0 <= numeric_level <= 5:
                    levels.append(str(numeric_level))
            if levels:
                return levels
    return [str(level) for level in range(0, 6)]


def _has_supported_setter(
    scale: BookooScale, setter_methods: tuple[str, ...]
) -> bool:
    """Check if any setter exists on the scale."""
    return any(callable(getattr(scale, method, None)) for method in setter_methods)


@dataclass(kw_only=True, frozen=True)
class BookooSelectEntityDescription(SelectEntityDescription):
    """Description for Bookoo select entities."""

    current_fn: Callable[[BookooScale], str | None]
    options_fn: Callable[[BookooScale], list[str]]
    setter_methods: tuple[str, ...]


SELECTS: tuple[BookooSelectEntityDescription, ...] = (
    BookooSelectEntityDescription(
        key="beeper_level",
        translation_key="beeper_level",
        entity_category=EntityCategory.CONFIG,
        current_fn=lambda scale: _get_first_available_value(
            scale, ("beeper_level", "buzzer_level")
        ),
        options_fn=_beeper_options,
        setter_methods=("set_beeper_level", "set_buzzer_level"),
    ),
    BookooSelectEntityDescription(
        key="flow_smoothing",
        translation_key="flow_smoothing",
        entity_category=EntityCategory.CONFIG,
        current_fn=lambda scale: _get_first_available_value(
            scale, ("flow_smoothing", "flow_smoothing_mode")
        ),
        options_fn=lambda scale: _get_first_available_value(
            scale, ("flow_smoothing_options",)
        )
        or ["off", "on"],
        setter_methods=(
            "set_flow_smoothing",
            "set_flow_smoothing_mode",
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up select entities."""

    coordinator = entry.runtime_data
    entities = [
        BookooSelect(coordinator, description)
        for description in SELECTS
        if _has_supported_setter(coordinator.scale, description.setter_methods)
    ]
    if entities:
        async_add_entities(entities)


class BookooSelect(BookooEntity, SelectEntity):
    """Representation of a Bookoo select."""

    entity_description: BookooSelectEntityDescription

    @property
    def current_option(self) -> str | None:
        """Return the currently selected option."""
        return self.entity_description.current_fn(self._scale)

    @property
    def options(self) -> list[str]:
        """Return available options."""
        return self.entity_description.options_fn(self._scale)

    async def async_select_option(self, option: str) -> None:
        """Select a new option."""
        success = await _async_call_first_available(
            self._scale, self.entity_description.setter_methods, option
        )
        if not success:
            raise HomeAssistantError("Dieses Gerät unterstützt die Einstellung nicht.")
        self.async_write_ha_state()
