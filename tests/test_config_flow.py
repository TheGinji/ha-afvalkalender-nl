"""Tests for the config, reconfigure and options flows."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.trashapi.api import TrashApiConnectionError, TrashApiDataError
from custom_components.trashapi.const import DOMAIN

from .common import ADDRESS, FETCH_FLOW, PICKUPS, SETTINGS, SETUP_ENTRY, make_entry

USER_INPUT = {**ADDRESS, **SETTINGS}
NEW_ADDRESS = {"location": "Sneek", "zip_code": "8601 ab", "house_number": "7"}


async def _start_user_flow(hass: HomeAssistant):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )


async def test_user_flow_creates_entry(hass: HomeAssistant) -> None:
    result = await _start_user_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with (
        patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)),
        patch(SETUP_ENTRY, return_value=True) as setup,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {**USER_INPUT, "zip_code": "1234 ab", "house_number": " 12 "}
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Afvalkalender 1234AB 12"
    assert result["data"] == ADDRESS
    assert result["options"] == SETTINGS
    assert result["result"].unique_id == "1234ab_12"
    assert len(setup.mock_calls) == 1


async def test_user_flow_aborts_for_known_address(hass: HomeAssistant) -> None:
    make_entry().add_to_hass(hass)
    result = await _start_user_flow(hass)
    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.parametrize(
    ("fetch", "error"),
    [
        (AsyncMock(side_effect=TrashApiConnectionError("down")), "cannot_connect"),
        (AsyncMock(side_effect=TrashApiDataError("bad")), "invalid_response"),
        (AsyncMock(return_value={}), "no_data"),
    ],
)
async def test_user_flow_errors_and_recovery(hass: HomeAssistant, fetch: AsyncMock, error: str) -> None:
    result = await _start_user_flow(hass)
    with patch(FETCH_FLOW, fetch):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    with (
        patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)),
        patch(SETUP_ENTRY, return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], USER_INPUT)
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_reconfigure_changes_the_address(hass: HomeAssistant) -> None:
    entry = make_entry()
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], NEW_ADDRESS)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.title == "Afvalkalender 8601AB 7"
    assert entry.unique_id == "8601ab_7"
    assert entry.data == {"location": "Sneek", "zip_code": "8601AB", "house_number": "7"}
    assert entry.options == SETTINGS


async def test_reconfigure_rejects_address_of_another_entry(hass: HomeAssistant) -> None:
    entry = make_entry()
    entry.add_to_hass(hass)
    make_entry(unique_id="8601ab_7").add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], NEW_ADDRESS)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "already_configured"}
    assert entry.unique_id == "1234ab_12"


async def test_reconfigure_api_error_then_success(hass: HomeAssistant) -> None:
    entry = make_entry()
    entry.add_to_hass(hass)

    result = await entry.start_reconfigure_flow(hass)
    with patch(FETCH_FLOW, AsyncMock(return_value={})):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], NEW_ADDRESS)
    assert result["errors"] == {"base": "no_data"}

    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], NEW_ADDRESS)
    assert result["type"] is FlowResultType.ABORT
    assert entry.unique_id == "8601ab_7"


async def test_reconfigure_reloads_a_running_entry(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration

    result = await entry.start_reconfigure_flow(hass)
    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        await hass.config_entries.flow.async_configure(result["flow_id"], NEW_ADDRESS)
    await hass.async_block_till_done()

    assert entry.state is ConfigEntryState.LOADED
    assert entry.runtime_data.config["zip_code"] == "8601AB"


async def test_options_flow_updates_settings(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    new_options = {
        "show_whole_year": False,
        "get_cleanprofs_data": True,
        "ignore_cache": True,
        "scan_interval_hours": 3,
    }
    with patch(FETCH_FLOW, AsyncMock(return_value=PICKUPS)):
        result = await hass.config_entries.options.async_configure(result["flow_id"], new_options)
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == new_options
    assert entry.runtime_data.update_interval == timedelta(hours=3)


async def test_options_flow_api_error(hass: HomeAssistant, init_integration) -> None:
    entry = init_integration
    result = await hass.config_entries.options.async_init(entry.entry_id)
    with patch(FETCH_FLOW, AsyncMock(side_effect=TrashApiConnectionError("down"))):
        result = await hass.config_entries.options.async_configure(result["flow_id"], SETTINGS)
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
    assert entry.options == SETTINGS
