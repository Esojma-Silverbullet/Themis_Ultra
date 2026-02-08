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


def _get_first_available_value(
    scale: BookooScale, names: tuple[str, ...]
) -> object | None:
    """Return the first existing attribute value on the scale."""
    for name in names:
        value = getattr(scale, name, None)
        if value is not None:
            return value
    if scale.device_state is None:
        return None
    for name in names:
        value = getattr(scale.device_state, name, None)
        if value is not None:
            return value
    return None


async def _async_call_first_available(
    scale: BookooScale, method_names: tuple[str, ...], value: object
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


def _normalize_buzzer_level(value: object | None) -> str | None:
    """Normalize buzzer/beeper levels to a string."""
    if value is None:
        return None
    try:
        numeric_level = int(value)
    except (TypeError, ValueError):
        return None
    if 0 <= numeric_level <= 5:
        return str(numeric_level)
    return None


def _flow_smoothing_current(value: object | None) -> str | None:
    """Normalize flow smoothing values to off/on strings."""
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.lower()
        if lowered in {"off", "on"}:
            return lowered
        try:
            numeric_value = int(value)
            return "on" if numeric_value else "off"
        except (TypeError, ValueError):
            return None
    return "on" if bool(value) else "off"


def _coerce_int_option(option: str) -> int:
    """Coerce a select option to int."""
    try:
        return int(option)
    except (TypeError, ValueError) as ex:
        raise HomeAssistantError("Ungültiger Wert für die Einstellung.") from ex


def _coerce_flow_smoothing(option: str) -> bool:
    """Coerce flow smoothing options to bool."""
    lowered = option.lower()
    if lowered in {"on", "1", "true", "yes"}:
        return True
    if lowered in {"off", "0", "false", "no"}:
        return False
    raise HomeAssistantError("Ungültiger Wert für Flow-Smoothing.")


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
    coerce_fn: Callable[[str], object] = lambda option: option


SELECTS: tuple[BookooSelectEntityDescription, ...] = (
    BookooSelectEntityDescription(
        key="beeper_level",
        translation_key="beeper_level",
        entity_category=EntityCategory.CONFIG,
        current_fn=lambda scale: _normalize_buzzer_level(
            _get_first_available_value(
                scale, ("beeper_level", "buzzer_level", "buzzer_gear")
            )
        ),
        options_fn=_beeper_options,
        setter_methods=("set_beep_level", "set_beeper_level", "set_buzzer_level"),
        coerce_fn=_coerce_int_option,
    ),
    BookooSelectEntityDescription(
        key="flow_smoothing",
        translation_key="flow_smoothing",
        entity_category=EntityCategory.CONFIG,
        current_fn=lambda scale: _flow_smoothing_current(
            _get_first_available_value(
                scale,
                ("flow_smoothing", "flow_smoothing_mode", "flow_rate_smoothing"),
            )
        ),
        options_fn=lambda scale: ["off", "on"],
        setter_methods=(
            "set_flow_rate_smoothing",
            "set_flow_smoothing",
            "set_flow_smoothing_mode",
            "set_flow_smoothing_enabled",
        ),
        coerce_fn=_coerce_flow_smoothing,
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
            self._scale,
            self.entity_description.setter_methods,
            self.entity_description.coerce_fn(option),
        )
        if not success:
            raise HomeAssistantError("Dieses Gerät unterstützt die Einstellung nicht.")
        self.async_write_ha_state()
