"""Tests for the "pickup today / tomorrow" binary sensors."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from .common import entity_id


async def test_pickup_tomorrow_and_today(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration

    tomorrow = hass.states.get(entity_id(hass, "binary_sensor", entry, "pickup_tomorrow"))
    assert tomorrow.state == "on"
    assert tomorrow.attributes["waste_types"] == ["Gft", "Papier"]
    assert tomorrow.attributes["waste_types_text"] == "Gft, Papier"

    today = hass.states.get(entity_id(hass, "binary_sensor", entry, "pickup_today"))
    assert today.state == "off"
    assert today.attributes["waste_types"] == []
    assert today.attributes["waste_types_text"] == ""


async def test_binary_sensors_roll_over_at_midnight(
    hass: HomeAssistant, init_integration, freezer
) -> None:
    entry = init_integration

    freezer.move_to("2026-10-27 00:00:10+00:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()

    today = hass.states.get(entity_id(hass, "binary_sensor", entry, "pickup_today"))
    assert today.state == "on"
    assert today.attributes["waste_types"] == ["Gft", "Papier"]

    tomorrow = hass.states.get(entity_id(hass, "binary_sensor", entry, "pickup_tomorrow"))
    assert tomorrow.state == "off"
