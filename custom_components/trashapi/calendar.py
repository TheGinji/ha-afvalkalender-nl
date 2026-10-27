"""Calendar entity with all pickup days."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .coordinator import TrashApiConfigEntry, TrashApiCoordinator
from .entity import TrashEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TrashApiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([TrashCalendar(entry.runtime_data, entry)])


class TrashCalendar(TrashEntity, CalendarEntity):
    """Every pickup is an all-day event named after the waste type."""

    _attr_translation_key = "pickup_calendar"

    def __init__(self, coordinator: TrashApiCoordinator, entry: TrashApiConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_calendar"

    def _events(self) -> list[CalendarEvent]:
        events: list[CalendarEvent] = []
        for name, dates in (self.coordinator.data or {}).items():
            for pickup in dates:
                events.append(
                    CalendarEvent(
                        start=pickup,
                        end=pickup + timedelta(days=1),
                        summary=name,
                        uid=f"{self.unique_id}_{name}_{pickup.isoformat()}",
                    )
                )
        events.sort(key=lambda event: (event.start, event.summary))
        return events

    @property
    def event(self) -> CalendarEvent | None:
        """The pickup that is happening today or comes next."""
        today = self._today()
        for event in self._events():
            if event.end > today:
                return event
        return None

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        start = dt_util.as_local(start_date).date()
        end = dt_util.as_local(end_date).date()
        return [
            event for event in self._events() if event.start < end and event.end > start
        ]
