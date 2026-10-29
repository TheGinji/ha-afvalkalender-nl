"""Tests for the sensors."""

from __future__ import annotations

from datetime import date

from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.trashapi.api import TrashApiConnectionError
from custom_components.trashapi.const import DOMAIN

from .common import PICKUPS, entity_id


async def test_waste_type_sensor_states(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration

    gft = hass.states.get(entity_id(hass, "sensor", entry, "gft"))
    assert gft.state == "2026-10-27"
    assert gft.attributes["device_class"] == "date"
    assert gft.attributes["waste_type"] == "Gft"
    assert gft.attributes["days_until"] == 1
    assert gft.attributes["days_text"] == "Tomorrow"
    assert gft.attributes["upcoming_dates"] == ["2026-10-27", "2026-11-12"]
    assert gft.attributes["icon"] == "mdi:leaf"

    restafval = hass.states.get(entity_id(hass, "sensor", entry, "restafval"))
    assert restafval.state == "2026-11-03"
    assert restafval.attributes["days_until"] == 8
    assert restafval.attributes["days_text"] == "In 8 days"


async def test_next_pickup_sensor(hass: HomeAssistant, init_integration) -> None:
    state = hass.states.get(entity_id(hass, "sensor", init_integration, "next_pickup"))
    assert state.state == "2026-10-27"
    assert state.attributes["days_until"] == 1
    assert state.attributes["days_text"] == "Tomorrow"
    assert state.attributes["waste_types"] == ["Gft", "Papier"]
    assert state.attributes["waste_types_text"] == "Gft, Papier"


async def test_texts_are_dutch_when_home_assistant_is_dutch(
    hass: HomeAssistant, init_integration
) -> None:
    entry = init_integration
    hass.config.language = "nl"
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    gft = hass.states.get(entity_id(hass, "sensor", entry, "gft"))
    restafval = hass.states.get(entity_id(hass, "sensor", entry, "restafval"))
    assert gft.attributes["days_text"] == "Morgen"
    assert restafval.attributes["days_text"] == "Over 8 dagen"


async def test_sensors_roll_over_at_midnight(hass: HomeAssistant, init_integration, freezer) -> None:
    entry = init_integration

    freezer.move_to("2026-10-27 00:00:10+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    gft = hass.states.get(entity_id(hass, "sensor", entry, "gft"))
    assert gft.state == "2026-10-27"
    assert gft.attributes["days_until"] == 0
    assert gft.attributes["days_text"] == "Today"

    next_pickup = hass.states.get(entity_id(hass, "sensor", entry, "next_pickup"))
    assert next_pickup.attributes["days_until"] == 0


async def test_sensors_without_upcoming_pickups(
    hass: HomeAssistant, init_integration, freezer
) -> None:
    entry = init_integration

    freezer.move_to("2027-01-01 12:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    gft = hass.states.get(entity_id(hass, "sensor", entry, "gft"))
    assert gft.state == "unknown"
    assert gft.attributes["days_until"] is None
    assert gft.attributes["days_text"] is None
    assert gft.attributes["upcoming_dates"] == []

    next_pickup = hass.states.get(entity_id(hass, "sensor", entry, "next_pickup"))
    assert next_pickup.state == "unknown"
    assert next_pickup.attributes["waste_types"] == []


async def test_new_waste_type_gets_a_sensor(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    mock_fetch.return_value = {
        **PICKUPS,
        "Grofvuil": [date(2026, 12, 14)],
        "Mystery": [date(2026, 12, 15)],
    }
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    grofvuil = hass.states.get(entity_id(hass, "sensor", entry, "grofvuil"))
    assert grofvuil.state == "2026-12-14"
    assert grofvuil.attributes["icon"] == "mdi:sofa"

    mystery = hass.states.get(entity_id(hass, "sensor", entry, "mystery"))
    assert mystery.attributes["icon"] == "mdi:delete-empty"


async def test_sensors_are_unavailable_when_the_api_fails(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    mock_fetch.side_effect = TrashApiConnectionError("down")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id(hass, "sensor", entry, "gft")).state == "unavailable"

    mock_fetch.side_effect = None
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id(hass, "sensor", entry, "gft")).state == "2026-10-27"


async def test_last_update_sensor_is_hidden_by_default(
    hass: HomeAssistant, init_integration
) -> None:
    registry = er.async_get(hass)
    entry = registry.async_get(entity_id(hass, "sensor", init_integration, "last_update"))
    assert entry.disabled_by is er.RegistryEntryDisabler.INTEGRATION
    assert entry.entity_category is EntityCategory.DIAGNOSTIC


async def test_last_update_sensor_shows_the_last_success(
    hass: HomeAssistant, config_entry, mock_fetch, mock_card, freezer
) -> None:
    await hass.config.async_set_time_zone("UTC")
    freezer.move_to("2026-10-26 12:00:00+00:00")
    config_entry.add_to_hass(hass)
    # Enable the (by default hidden) sensor before the integration is set up
    er.async_get(hass).async_get_or_create(
        "sensor",
        DOMAIN,
        f"{config_entry.entry_id}_last_update",
        config_entry=config_entry,
        disabled_by=None,
    )
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    sensor = entity_id(hass, "sensor", config_entry, "last_update")
    state = hass.states.get(sensor)
    assert state.state == "2026-10-26T12:00:00+00:00"
    assert state.attributes["device_class"] == "timestamp"

    # A failed update keeps the time of the last success, and the sensor stays available
    freezer.move_to("2026-10-26 13:00:00+00:00")
    mock_fetch.side_effect = TrashApiConnectionError("down")
    await config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(sensor).state == "2026-10-26T12:00:00+00:00"

    mock_fetch.side_effect = None
    await config_entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(sensor).state == "2026-10-26T13:00:00+00:00"
