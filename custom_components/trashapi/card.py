"""Serve the dashboard card and make sure Home Assistant loads it before dashboards render."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState, Event, HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

CARD_FILE = Path(__file__).parent / "www" / "trash-containers-card.js"
CARD_URL = f"/{DOMAIN}_static/trash-containers-card.js"


def _file_digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes(), usedforsecurity=False).hexdigest()[:10]


def _get_resources(hass: HomeAssistant):
    """Return the Lovelace resource collection (works for old and new Home Assistant)."""
    data = hass.data.get("lovelace")
    if data is None:
        return None
    if isinstance(data, dict):
        return data.get("resources")
    return getattr(data, "resources", None)


async def _async_register_resource(hass: HomeAssistant, url: str) -> bool:
    """Add (or update) the card as a Lovelace resource. Only possible in storage mode."""
    resources = _get_resources(hass)
    if resources is None or not hasattr(resources, "async_create_item"):
        return False  # not loaded yet, or YAML mode where resources cannot be managed

    if not getattr(resources, "loaded", True):
        await resources.async_load()
        resources.loaded = True

    for item in list(resources.async_items()):
        if str(item.get("url", "")).split("?")[0] == CARD_URL:
            if item.get("url") != url:
                await resources.async_update_item(
                    item["id"], {"res_type": "module", "url": url}
                )
            return True

    await resources.async_create_item({"res_type": "module", "url": url})
    return True


async def async_register_card(hass: HomeAssistant) -> None:
    """Serve the JS file and register it in the two ways Home Assistant offers."""
    from homeassistant.components import frontend
    from homeassistant.components.http import StaticPathConfig

    digest = await hass.async_add_executor_job(_file_digest, CARD_FILE)
    url = f"{CARD_URL}?v={digest}"

    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(CARD_FILE), False)]
    )
    # Fallback for YAML dashboards (the card script is guarded against loading twice)
    frontend.add_extra_js_url(hass, url)

    async def _register(_event: Event | None = None) -> bool:
        try:
            return await _async_register_resource(hass, url)
        except Exception:  # noqa: BLE001 - the card is optional
            _LOGGER.warning("Could not add the dashboard card as a resource", exc_info=True)
            return True  # do not retry

    # As a Lovelace resource the card loads before any dashboard renders, which avoids
    # "Custom element doesn't exist" on page loads.
    if not await _register() and hass.state is not CoreState.running:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register)
