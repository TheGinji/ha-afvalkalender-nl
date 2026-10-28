"""Shared fixtures."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .common import CARD, FETCH_COORDINATOR, PICKUPS, make_entry


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Let Home Assistant load the integration from custom_components."""


@pytest.fixture
def mock_card() -> Generator[AsyncMock]:
    """Do not register the dashboard card (needs the real frontend)."""
    with patch(CARD, new_callable=AsyncMock) as mock:
        yield mock


@pytest.fixture
def mock_fetch() -> Generator[AsyncMock]:
    """Replace the API call of the coordinator."""
    with patch(FETCH_COORDINATOR, new_callable=AsyncMock, return_value=PICKUPS) as mock:
        yield mock


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """A config entry for the default test address."""
    return make_entry()


@pytest.fixture
async def init_integration(hass, config_entry, mock_fetch, mock_card, freezer) -> MockConfigEntry:
    """Set the integration up on a fixed day (2026-10-26, UTC)."""
    await hass.config.async_set_time_zone("UTC")
    freezer.move_to("2026-10-26 12:00:00+00:00")
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry
