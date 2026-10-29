"""Tests for the refresh button."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from custom_components.trashapi.api import TrashApiConnectionError

from .common import entity_id


async def test_button_refreshes_without_the_api_cache(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    button = entity_id(hass, "button", entry, "refresh")

    mock_fetch.reset_mock()
    await hass.services.async_call("button", "press", {"entity_id": button}, blocking=True)

    mock_fetch.assert_awaited_once()
    assert mock_fetch.await_args.args[1]["ignore_cache"] is True

    # The next scheduled refresh uses the normal setting again
    mock_fetch.reset_mock()
    await entry.runtime_data.async_refresh()
    assert mock_fetch.await_args.args[1]["ignore_cache"] is False


async def test_button_stays_available_and_recovers_after_a_failure(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    button = entity_id(hass, "button", entry, "refresh")
    gft = entity_id(hass, "sensor", entry, "gft")

    mock_fetch.side_effect = TrashApiConnectionError("down")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(gft).state == "unavailable"
    assert hass.states.get(button).state != "unavailable"

    mock_fetch.side_effect = None
    await hass.services.async_call("button", "press", {"entity_id": button}, blocking=True)
    await hass.async_block_till_done()
    assert hass.states.get(gft).state == "2026-10-27"
