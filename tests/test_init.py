"""Tests for setup, unload, removal and migration of the config entry."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.helpers import issue_registry as ir

from custom_components.trashapi.api import TrashApiConnectionError
from custom_components.trashapi.const import DOMAIN

from .common import ADDRESS, CARD, PICKUPS, SETTINGS, make_entry

ALL_IN_DATA = {**ADDRESS, **SETTINGS}


async def test_setup_and_unload(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration
    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.data == PICKUPS

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED


async def test_setup_retries_when_the_api_is_down(
    hass: HomeAssistant, config_entry, mock_fetch, mock_card
) -> None:
    mock_fetch.side_effect = TrashApiConnectionError("down")
    config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_retries_without_data_and_raises_an_issue(
    hass: HomeAssistant, config_entry, mock_fetch, mock_card
) -> None:
    mock_fetch.return_value = {}
    config_entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.SETUP_RETRY
    assert ir.async_get(hass).async_get_issue(DOMAIN, f"no_data_{config_entry.entry_id}")


async def test_removing_the_entry_clears_repair_issues(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration
    registry = ir.async_get(hass)
    for key in ("api_unavailable", "no_data"):
        ir.async_create_issue(
            hass,
            DOMAIN,
            f"{key}_{entry.entry_id}",
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key=key,
            translation_placeholders={"address": "1234AB 12", "error": "x"},
        )
    assert registry.async_get_issue(DOMAIN, f"no_data_{entry.entry_id}")

    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()

    assert registry.async_get_issue(DOMAIN, f"no_data_{entry.entry_id}") is None
    assert registry.async_get_issue(DOMAIN, f"api_unavailable_{entry.entry_id}") is None


async def test_card_registration_failure_does_not_break_setup(
    hass: HomeAssistant, config_entry, mock_fetch, caplog: pytest.LogCaptureFixture
) -> None:
    config_entry.add_to_hass(hass)
    with patch(CARD, new_callable=AsyncMock, side_effect=RuntimeError("no frontend")):
        assert await hass.config_entries.async_setup(config_entry.entry_id)
    assert config_entry.state is ConfigEntryState.LOADED
    assert "Could not register the dashboard card" in caplog.text


@pytest.mark.parametrize(
    ("data", "options", "expected_data", "expected_options"),
    [
        (ALL_IN_DATA, {}, ADDRESS, SETTINGS),
        (
            ALL_IN_DATA,
            {"zip_code": "9999ZZ", "house_number": "5", "scan_interval_hours": 12},
            {"location": "Leeuwarden", "zip_code": "9999ZZ", "house_number": "5"},
            {**SETTINGS, "scan_interval_hours": 12},
        ),
        (ADDRESS, {}, ADDRESS, {}),
    ],
)
async def test_migration_from_version_1(
    hass: HomeAssistant,
    mock_fetch,
    mock_card,
    data: dict,
    options: dict,
    expected_data: dict,
    expected_options: dict,
) -> None:
    entry = make_entry(version=1, data=data, options=options)
    entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(entry.entry_id)

    assert entry.version == 2
    assert entry.data == expected_data
    assert entry.options == expected_options
    assert entry.unique_id == "1234ab_12"


async def test_migration_refuses_entries_from_a_newer_version(
    hass: HomeAssistant, mock_fetch, mock_card
) -> None:
    entry = make_entry(version=3)
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.MIGRATION_ERROR
