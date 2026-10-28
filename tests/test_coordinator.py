"""Tests for the coordinator: refreshing and repair issues."""

from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from custom_components.trashapi.api import TrashApiConnectionError
from custom_components.trashapi.const import DOMAIN
from custom_components.trashapi.coordinator import get_config

from .common import ADDRESS, PICKUPS, make_entry


def test_get_config_lets_options_override_data() -> None:
    entry = make_entry(data=dict(ADDRESS), options={"scan_interval_hours": 2})
    assert get_config(entry) == {**ADDRESS, "scan_interval_hours": 2}


async def test_repair_issue_after_repeated_failures(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    coordinator = entry.runtime_data
    registry = ir.async_get(hass)
    issue_id = f"api_unavailable_{entry.entry_id}"

    mock_fetch.side_effect = TrashApiConnectionError("down")
    await coordinator.async_refresh()
    assert not coordinator.last_update_success
    assert registry.async_get_issue(DOMAIN, issue_id) is None

    await coordinator.async_refresh()
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    mock_fetch.side_effect = None
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert registry.async_get_issue(DOMAIN, issue_id) is None


async def test_empty_response_keeps_the_last_data(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    entry = init_integration
    coordinator = entry.runtime_data
    registry = ir.async_get(hass)
    issue_id = f"no_data_{entry.entry_id}"

    mock_fetch.return_value = {}
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data == PICKUPS
    assert registry.async_get_issue(DOMAIN, issue_id) is not None

    mock_fetch.return_value = PICKUPS
    await coordinator.async_refresh()
    assert registry.async_get_issue(DOMAIN, issue_id) is None
