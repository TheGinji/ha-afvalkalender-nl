"""Tests for the sensors."""

from __future__ import annotations

from datetime import date

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.trashapi.api import TrashApiConnectionError

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
