"""Event platform for Bookoo firmware 4 automatic-mode events."""

from typing import ClassVar

from aiobookoo_ultra.const import AutomaticModeEvent
from homeassistant.components.event import EventEntity, EventEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import BookooConfigEntry, BookooCoordinator
from .entity import BookooEntity

PARALLEL_UPDATES = 0

EVENT_TYPE_BY_STATE = {
    AutomaticModeEvent.STOPPED: "stopped",
    AutomaticModeEvent.STARTED: "started",
    AutomaticModeEvent.READY: "ready",
    AutomaticModeEvent.EXIT_READY: "exit_ready",
    AutomaticModeEvent.EXIT_DONE: "exit_done",
}

AUTOMATIC_MODE_EVENT_DESCRIPTION = EventEntityDescription(
    key="automatic_mode",
    translation_key="automatic_mode",
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: BookooConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Bookoo automatic-mode event entity."""
    async_add_entities(
        [
            BookooAutomaticModeEvent(
                entry.runtime_data,
                AUTOMATIC_MODE_EVENT_DESCRIPTION,
            )
        ]
    )


class BookooAutomaticModeEvent(BookooEntity, EventEntity):
    """Represent automatic-mode events emitted by firmware 4."""

    _attr_event_types: ClassVar[list[str]] = list(EVENT_TYPE_BY_STATE.values())

    def __init__(
        self,
        coordinator: BookooCoordinator,
        entity_description: EventEntityDescription,
    ) -> None:
        """Initialize the automatic-mode event entity."""
        super().__init__(coordinator, entity_description)
        self._last_sequence = self._scale.automatic_mode_event_sequence

    @callback
    def _handle_coordinator_update(self) -> None:
        """Publish each new automatic-mode packet exactly once."""
        sequence = self._scale.automatic_mode_event_sequence
        state = self._scale.automatic_mode_state
        if sequence != self._last_sequence and state is not None:
            self._last_sequence = sequence
            self._trigger_event(
                EVENT_TYPE_BY_STATE[state.event],
                {
                    "timer_seconds": state.timer,
                    "weight_grams": state.weight,
                    "result": state.result,
                },
            )
        super()._handle_coordinator_update()
