"""Data coordinator for TrashAPI."""

from __future__ import annotations

from datetime import date, timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TrashApiError, async_fetch_pickups
from .const import (
    API_DOCS_URL,
    CONF_HOUSE_NUMBER,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_ZIP_CODE,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

TrashApiConfigEntry = ConfigEntry["TrashApiCoordinator"]

ISSUE_API = "api_unavailable"
ISSUE_NO_DATA = "no_data"
FAILURES_BEFORE_ISSUE = 2


def get_config(entry: ConfigEntry) -> dict:
    """Options (when set) override the data entered during setup."""
    return {**entry.data, **entry.options}


def issue_id(key: str, entry_id: str) -> str:
    return f"{key}_{entry_id}"


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
        self._failures = 0

    @callback
    def _raise_issue(self, key: str, **placeholders: str) -> None:
        address = f"{self.config.get(CONF_ZIP_CODE, '')} {self.config.get(CONF_HOUSE_NUMBER, '')}"
        ir.async_create_issue(
            self.hass,
            DOMAIN,
            issue_id(key, self.config_entry.entry_id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=key,
            translation_placeholders={"address": address.strip(), **placeholders},
            learn_more_url=API_DOCS_URL,
        )

    @callback
    def _clear_issue(self, key: str) -> None:
        ir.async_delete_issue(self.hass, DOMAIN, issue_id(key, self.config_entry.entry_id))

    async def _async_update_data(self) -> dict[str, list[date]]:
        try:
            data = await async_fetch_pickups(self._session, self.config)
        except TrashApiError as err:
            self._failures += 1
            if self._failures >= FAILURES_BEFORE_ISSUE:
                self._raise_issue(ISSUE_API, error=str(err))
            raise UpdateFailed(
                translation_domain=DOMAIN,
                translation_key="api_error",
                translation_placeholders={"error": str(err)},
            ) from err

        self._failures = 0
        self._clear_issue(ISSUE_API)

        if not data:
            self._raise_issue(ISSUE_NO_DATA)
            if self.data:
                return self.data  # keep showing the last known calendar
            raise UpdateFailed(translation_domain=DOMAIN, translation_key="no_data")

        self._clear_issue(ISSUE_NO_DATA)
        return data
