"""Tests for the diagnostics download."""

from __future__ import annotations

from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant

from custom_components.trashapi.api import TrashApiConnectionError
from custom_components.trashapi.diagnostics import async_get_config_entry_diagnostics

from .common import SETTINGS


async def test_diagnostics_redact_the_address(hass: HomeAssistant, init_integration) -> None:
    diagnostics = await async_get_config_entry_diagnostics(hass, init_integration)

    assert diagnostics["entry"]["data"] == {
        "location": REDACTED,
        "zip_code": REDACTED,
        "house_number": REDACTED,
    }
    assert diagnostics["entry"]["options"] == SETTINGS
    assert diagnostics["coordinator"]["last_update_success"] is True
    assert diagnostics["coordinator"]["update_interval"] == "6:00:00"
    assert diagnostics["coordinator"]["last_exception"] is None
    assert diagnostics["waste_types"]["Gft"] == {
        "pickups_known": 2,
        "next_pickups": ["2026-10-27", "2026-11-12"],
    }


async def test_diagnostics_report_the_last_error(
    hass: HomeAssistant, init_integration, mock_fetch
) -> None:
    mock_fetch.side_effect = TrashApiConnectionError("down")
    await init_integration.runtime_data.async_refresh()

    diagnostics = await async_get_config_entry_diagnostics(hass, init_integration)
    assert diagnostics["coordinator"]["last_update_success"] is False
    assert diagnostics["coordinator"]["last_exception"] is not None
