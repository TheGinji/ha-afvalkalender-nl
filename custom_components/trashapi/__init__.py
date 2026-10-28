"""HA Dutch Trash Calendar integration."""

from __future__ import annotations

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.typing import ConfigType

from .const import ADDRESS_KEYS, DOMAIN, SETTING_KEYS
from .coordinator import (
    ISSUE_API,
    ISSUE_NO_DATA,
    TrashApiConfigEntry,
    TrashApiCoordinator,
    issue_id,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.CALENDAR, Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the dashboard card. The card is optional: errors here never block the integration."""
    try:
        from .card import async_register_card

        await async_register_card(hass)
    except Exception:  # noqa: BLE001
        _LOGGER.warning("Could not register the dashboard card", exc_info=True)
    return True


async def async_migrate_entry(hass: HomeAssistant, entry: TrashApiConfigEntry) -> bool:
    """Migrate old entries.

    Version 1 stored all settings in entry.data and, after using "Configureren",
    in entry.options as well (options won). Version 2 keeps the address in entry.data
    (Herconfigureren) and the API settings in entry.options (Configureren).
    """
    if entry.version > 2:
        return False  # created by a newer version: do not guess

    if entry.version == 1:
        merged = {**entry.data, **entry.options}
        hass.config_entries.async_update_entry(
            entry,
            data={key: merged[key] for key in ADDRESS_KEYS if key in merged},
            options={key: merged[key] for key in SETTING_KEYS if key in merged},
            version=2,
        )
        _LOGGER.debug("Migrated config entry to version 2")

    return True


async def async_setup_entry(hass: HomeAssistant, entry: TrashApiConfigEntry) -> bool:
    coordinator = TrashApiCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Reload when the options are changed ("Configureren" button)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: TrashApiConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: TrashApiConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_entry(hass: HomeAssistant, entry: TrashApiConfigEntry) -> None:
    """Remove repair notices together with the integration."""
    for key in (ISSUE_API, ISSUE_NO_DATA):
        ir.async_delete_issue(hass, DOMAIN, issue_id(key, entry.entry_id))
