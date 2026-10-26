"""Shared base entity for the extra platforms (calendar, binary sensors)."""

from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import API_DOCS_URL, CONF_HOUSE_NUMBER, CONF_ZIP_CODE, DOMAIN
from .coordinator import TrashApiConfigEntry, TrashApiCoordinator


class TrashEntity(CoordinatorEntity[TrashApiCoordinator]):
    """Entity that follows the pickup calendar and rolls over right after midnight."""

    _attr_has_entity_name = True

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

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
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
