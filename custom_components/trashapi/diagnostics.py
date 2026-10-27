"""Diagnostics for HA Dutch Trash Calendar."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from .const import CONF_HOUSE_NUMBER, CONF_LOCATION, CONF_ZIP_CODE
from .coordinator import TrashApiConfigEntry

TO_REDACT = {CONF_HOUSE_NUMBER, CONF_LOCATION, CONF_ZIP_CODE}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: TrashApiConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry (address details are redacted)."""
    coordinator = entry.runtime_data
    last_exception = coordinator.last_exception

    return {
        "entry": {
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "update_interval": str(coordinator.update_interval),
            "last_exception": repr(last_exception) if last_exception else None,
        },
        "waste_types": {
            name: {
                "pickups_known": len(dates),
                "next_pickups": [d.isoformat() for d in dates[:3]],
            }
            for name, dates in (coordinator.data or {}).items()
        },
    }
