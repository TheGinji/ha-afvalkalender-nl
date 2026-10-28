"""Tests for the calendar entity."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .common import entity_id


async def test_calendar_shows_the_next_pickup(hass: HomeAssistant, init_integration) -> None:
    state = hass.states.get(entity_id(hass, "calendar", init_integration, "calendar"))
    assert state.state == "off"
    assert state.attributes["message"] == "Gft"
    assert state.attributes["all_day"] is True


async def test_calendar_is_on_during_a_pickup_day(
    hass: HomeAssistant, init_integration, freezer
) -> None:
    freezer.move_to("2026-10-27 00:00:10+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id(hass, "calendar", init_integration, "calendar"))
    assert state.state == "on"
    assert state.attributes["message"] == "Gft"


async def test_calendar_without_upcoming_pickups(
    hass: HomeAssistant, init_integration, freezer
) -> None:
    freezer.move_to("2027-01-01 12:00:00+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    state = hass.states.get(entity_id(hass, "calendar", init_integration, "calendar"))
    assert state.state == "off"
    assert "message" not in state.attributes


async def test_calendar_get_events(hass: HomeAssistant, init_integration) -> None:
    calendar = entity_id(hass, "calendar", init_integration, "calendar")

    response = await hass.services.async_call(
        "calendar",
        "get_events",
        {
            "entity_id": calendar,
            "start_date_time": "2026-11-01T00:00:00+00:00",
            "end_date_time": "2026-11-30T00:00:00+00:00",
        },
        blocking=True,
        return_response=True,
    )

    events = response[calendar]["events"]
    assert [event["summary"] for event in events] == ["Restafval", "Gft", "Papier"]
    assert events[0]["start"] == "2026-11-03"
    assert events[0]["end"] == "2026-11-04"
