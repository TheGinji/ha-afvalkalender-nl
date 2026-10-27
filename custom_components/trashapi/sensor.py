"""Sensors for TrashAPI."""

from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

from .api import next_pickup
from .const import (
    API_DOCS_URL,
    CONF_HOUSE_NUMBER,
    CONF_ZIP_CODE,
    DEFAULT_ICON,
    DOMAIN,
    ICONS,
)
from .coordinator import TrashApiConfigEntry, TrashApiCoordinator

PARALLEL_UPDATES = 0

UPCOMING_LIMIT = 10


async def async_setup_entry(
    hass: HomeAssistant,
    entry: TrashApiConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    known: set[str] = set()

    @callback
    def _add_new_types() -> None:
        new = [name for name in coordinator.data if name not in known]
        if new:
            known.update(new)
            async_add_entities(TrashTypeSensor(coordinator, entry, n) for n in new)

    async_add_entities([NextPickupSensor(coordinator, entry)])
    _add_new_types()
    # A new waste type (e.g. Grofvuil) may show up later in the calendar
    entry.async_on_unload(coordinator.async_add_listener(_add_new_types))


class TrashBaseSensor(CoordinatorEntity[TrashApiCoordinator], SensorEntity):
    """Shared behaviour."""

    _attr_has_entity_name = True
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: TrashApiCoordinator, entry: TrashApiConfigEntry) -> None:
        super().__init__(coordinator)
        cfg = coordinator.config
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Afvalkalender {cfg[CONF_ZIP_CODE]} {cfg[CONF_HOUSE_NUMBER]}",
            manufacturer="TrashAPI",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=API_DOCS_URL,
        )
        self._entry_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        # Roll over to the next date right after midnight, without waiting for an API refresh
        self.async_on_remove(
            async_track_time_change(
                self.hass, self._handle_midnight, hour=0, minute=0, second=5
            )
        )

    @callback
    def _handle_midnight(self, _now: Any) -> None:
        self.async_write_ha_state()

    @staticmethod
    def _today() -> date:
        return dt_util.now().date()

    def _days_text(self, days: int | None) -> str | None:
        """Readable countdown: Vandaag / Morgen / Over N dagen (English when HA is not Dutch)."""
        if days is None:
            return None
        dutch = str(self.hass.config.language).lower().startswith("nl")
        if days <= 0:
            return "Vandaag" if dutch else "Today"
        if days == 1:
            return "Morgen" if dutch else "Tomorrow"
        return f"Over {days} dagen" if dutch else f"In {days} days"


class TrashTypeSensor(TrashBaseSensor):
    """Next pickup for one waste type (Restafval, Gft, Papier, ...)."""

    def __init__(
        self, coordinator: TrashApiCoordinator, entry: TrashApiConfigEntry, waste_type: str
    ) -> None:
        super().__init__(coordinator, entry)
        self._waste_type = waste_type
        self._attr_name = waste_type
        self._attr_unique_id = f"{entry.entry_id}_{slugify(waste_type)}"
        # Waste types come from the API, so their icons cannot live in icons.json
        self._attr_icon = ICONS.get(waste_type.lower(), DEFAULT_ICON)

    def _upcoming(self) -> list[date]:
        today = self._today()
        dates = (self.coordinator.data or {}).get(self._waste_type, [])
        return [d for d in dates if d >= today]

    @property
    def native_value(self) -> date | None:
        upcoming = self._upcoming()
        return upcoming[0] if upcoming else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        upcoming = self._upcoming()
        days = (upcoming[0] - self._today()).days if upcoming else None
        return {
            "waste_type": self._waste_type,
            "days_until": days,
            "days_text": self._days_text(days),
            "upcoming_dates": [d.isoformat() for d in upcoming[:UPCOMING_LIMIT]],
        }


class NextPickupSensor(TrashBaseSensor):
    """The next pickup of any waste type."""

    _attr_translation_key = "next_pickup"

    def __init__(self, coordinator: TrashApiCoordinator, entry: TrashApiConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_next_pickup"

    def _next(self) -> tuple[date | None, list[str]]:
        today = self._today()
        best: date | None = None
        types: list[str] = []
        for name, dates in (self.coordinator.data or {}).items():
            pickup = next_pickup(dates, today)
            if pickup is None:
                continue
            if best is None or pickup < best:
                best, types = pickup, [name]
            elif pickup == best:
                types.append(name)
        return best, sorted(types)

    @property
    def native_value(self) -> date | None:
        return self._next()[0]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        pickup, types = self._next()
        days = (pickup - self._today()).days if pickup else None
        return {
            "days_until": days,
            "days_text": self._days_text(days),
            "waste_types": types,
            "waste_types_text": ", ".join(types),
        }
