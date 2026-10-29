"""Button to refresh the pickup calendar right now."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import TrashApiConfigEntry, TrashApiCoordinator
from .entity import TrashEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TrashApiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities([TrashRefreshButton(entry.runtime_data, entry)])


class TrashRefreshButton(TrashEntity, ButtonEntity):
    """Fetches the calendar now, skipping the cache of the API."""

    _attr_translation_key = "refresh"

    def __init__(self, coordinator: TrashApiCoordinator, entry: TrashApiConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_refresh"

    @property
    def available(self) -> bool:
        # Stay usable after a failed update: that is exactly when you want to try again
        return True

    async def async_press(self) -> None:
        await self.coordinator.async_refresh_now()
