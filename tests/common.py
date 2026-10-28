"""Shared test data and helpers."""

from __future__ import annotations

from datetime import date

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.trashapi.const import DOMAIN

ADDRESS = {"location": "Leeuwarden", "zip_code": "1234AB", "house_number": "12"}
SETTINGS = {
    "show_whole_year": True,
    "get_cleanprofs_data": True,
    "ignore_cache": False,
    "scan_interval_hours": 6,
}
PICKUPS = {
    "Gft": [date(2026, 10, 27), date(2026, 11, 12)],
    "Papier": [date(2026, 10, 27), date(2026, 11, 16)],
    "Restafval": [date(2026, 11, 3)],
}

FETCH_COORDINATOR = "custom_components.trashapi.coordinator.async_fetch_pickups"
FETCH_FLOW = "custom_components.trashapi.config_flow.async_fetch_pickups"
CARD = "custom_components.trashapi.card.async_register_card"
SETUP_ENTRY = "custom_components.trashapi.async_setup_entry"


def make_entry(**overrides: object) -> MockConfigEntry:
    """Create a config entry for the default test address."""
    kwargs: dict[str, object] = {
        "domain": DOMAIN,
        "title": "Afvalkalender 1234AB 12",
        "unique_id": "1234ab_12",
        "version": 2,
        "data": dict(ADDRESS),
        "options": dict(SETTINGS),
    }
    kwargs.update(overrides)
    return MockConfigEntry(**kwargs)


def entity_id(hass: HomeAssistant, domain: str, entry: MockConfigEntry, key: str) -> str:
    """Look up an entity of the integration by the key in its unique id."""
    found = er.async_get(hass).async_get_entity_id(domain, DOMAIN, f"{entry.entry_id}_{key}")
    assert found is not None, f"no {domain} entity with key {key}"
    return found
