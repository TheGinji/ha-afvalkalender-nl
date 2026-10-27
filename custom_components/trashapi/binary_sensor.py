"""Binary sensors: is there a pickup today / tomorrow?"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import TrashApiConfigEntry, TrashApiCoordinator
from .entity import TrashEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TrashApiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        [
            TrashPickupBinarySensor(coordinator, entry, "pickup_today", 0),
            TrashPickupBinarySensor(coordinator, entry, "pickup_tomorrow", 1),
        ]
    )


class TrashPickupBinarySensor(TrashEntity, BinarySensorEntity):
    """On when at least one container is collected on the given day."""

    def __init__(
        self,
        coordinator: TrashApiCoordinator,
        entry: TrashApiConfigEntry,
        key: str,
        offset_days: int,
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_translation_key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._offset_days = offset_days

    def _types(self) -> list[str]:
        target = self._today() + timedelta(days=self._offset_days)
        return sorted(
            name
            for name, dates in (self.coordinator.data or {}).items()
            if target in dates
        )

    @property
    def is_on(self) -> bool:
        return bool(self._types())

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        types = self._types()
        return {"waste_types": types, "waste_types_text": ", ".join(types)}
