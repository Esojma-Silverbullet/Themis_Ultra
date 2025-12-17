"""Button entities for Bookoo scales."""

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from aiobookoo.bookooscale import BookooScale

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BookooConfigEntry
from .entity import BookooEntity

PARALLEL_UPDATES = 0


@dataclass(kw_only=True, frozen=True)
class BookooButtonEntityDescription(ButtonEntityDescription):
    """Description for bookoo button entities."""

    press_fn: Callable[[BookooScale], Coroutine[Any, Any, None]]


BUTTONS: tuple[BookooButtonEntityDescription, ...] = (
    BookooButtonEntityDescription(
        key="tare",
        translation_key="tare",
        press_fn=lambda scale: scale.tare(),
    ),
    BookooButtonEntityDescription(
        key="reset_timer",
        translation_key="reset_timer",
        press_fn=lambda scale: scale.reset_timer(),
    ),
    BookooButtonEntityDescription(
        key="start",
        translation_key="start",
        press_fn=lambda scale: scale.start_timer(),
    ),
    BookooButtonEntityDescription(
        key="stop",
        translation_key="stop",
        press_fn=lambda scale: scale.stop_timer(),
    ),
    BookooButtonEntityDescription(
        key="tare_and_start",
        translation_key="tare_and_start",
        press_fn=lambda scale: scale.tare_and_start_timer(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up button entities and services."""

    coordinator = entry.runtime_data
    async_add_entities(
        BookooButton(coordinator, description) for description in BUTTONS
    )


class BookooButton(BookooEntity, ButtonEntity):
    """Representation of an Bookoo button."""

    entity_description: BookooButtonEntityDescription

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self._scale)
