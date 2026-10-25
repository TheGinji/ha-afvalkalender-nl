"""Data coordinator for TrashAPI."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TrashApiError, async_fetch_pickups
from .const import CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS, DOMAIN

_LOGGER = logging.getLogger(__name__)

TrashApiConfigEntry = ConfigEntry["TrashApiCoordinator"]


def get_config(entry: ConfigEntry) -> dict:
    """Options (when set) override the data entered during setup."""
    return {**entry.data, **entry.options}


class TrashApiCoordinator(DataUpdateCoordinator[dict[str, list[date]]]):
    """Fetches the pickup calendar."""

    config_entry: TrashApiConfigEntry

    def __init__(self, hass: HomeAssistant, entry: TrashApiConfigEntry) -> None:
        self.config = get_config(entry)
        hours = int(self.config.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS))
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(hours=hours),
        )
        self._session = async_get_clientsession(hass)

    async def _async_update_data(self) -> dict[str, list[date]]:
        try:
            return await async_fetch_pickups(self._session, self.config)
        except TrashApiError as err:
            raise UpdateFailed(f"Error talking to TrashAPI: {err}") from err
