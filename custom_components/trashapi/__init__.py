"""HA Dutch Trash Calendar integration."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import TrashApiConfigEntry, TrashApiCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]

CARD_FILE = Path(__file__).parent / "www" / "trash-containers-card.js"
CARD_URL = f"/{DOMAIN}_static/trash-containers-card.js"


def _file_digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()[:10]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Serve the dashboard card and load it in the frontend.

    The card is optional: if anything goes wrong here the integration still works.
    """
    try:
        from homeassistant.components import frontend
        from homeassistant.components.http import StaticPathConfig

        digest = await hass.async_add_executor_job(_file_digest, CARD_FILE)
        await hass.http.async_register_static_paths(
            [StaticPathConfig(CARD_URL, str(CARD_FILE), False)]
        )
        frontend.add_extra_js_url(hass, f"{CARD_URL}?v={digest}")
    except Exception:  # noqa: BLE001
        _LOGGER.warning("Could not register the dashboard card", exc_info=True)
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
