"""Tests for the registration of the dashboard card."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import homeassistant.components as ha_components
import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
from homeassistant.core import CoreState

from custom_components.trashapi import card

CURRENT = f"{card.CARD_URL}?v=current"
OLD = f"{card.CARD_URL}?v=old"


def make_resources(items=None, loaded=True) -> MagicMock:
    resources = MagicMock()
    resources.loaded = loaded
    resources.async_load = AsyncMock()
    resources.async_items = MagicMock(return_value=items or [])
    resources.async_create_item = AsyncMock()
    resources.async_update_item = AsyncMock()
    return resources


def make_hass(resources=None, state=CoreState.running) -> MagicMock:
    hass = MagicMock()
    hass.state = state
    hass.data = {"lovelace": {"resources": resources}} if resources is not None else {}
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    hass.http.async_register_static_paths = AsyncMock()
    return hass


def test_get_resources_supports_old_and_new_home_assistant() -> None:
    resources = object()
    assert card._get_resources(SimpleNamespace(data={})) is None
    assert card._get_resources(SimpleNamespace(data={"lovelace": {"resources": resources}})) is resources
    assert (
        card._get_resources(SimpleNamespace(data={"lovelace": SimpleNamespace(resources=resources)}))
        is resources
    )
    assert card._get_resources(SimpleNamespace(data={"lovelace": SimpleNamespace()})) is None


async def test_resource_is_not_added_when_it_cannot_be_managed() -> None:
    assert await card._async_register_resource(make_hass(), CURRENT) is False

    yaml_mode = SimpleNamespace(data={"lovelace": {"resources": SimpleNamespace()}})
    assert await card._async_register_resource(yaml_mode, CURRENT) is False


async def test_resource_is_created_after_loading_the_collection() -> None:
    resources = make_resources(loaded=False)
    assert await card._async_register_resource(make_hass(resources), CURRENT) is True
    resources.async_load.assert_awaited_once()
    resources.async_create_item.assert_awaited_once_with({"res_type": "module", "url": CURRENT})


async def test_resource_with_an_old_version_is_updated() -> None:
    resources = make_resources(
        items=[{"id": "other", "url": "/other.js"}, {"id": "abc", "url": OLD}]
    )
    assert await card._async_register_resource(make_hass(resources), CURRENT) is True
    resources.async_update_item.assert_awaited_once_with(
        "abc", {"res_type": "module", "url": CURRENT}
    )
    resources.async_create_item.assert_not_awaited()


async def test_resource_that_is_up_to_date_is_left_alone() -> None:
    resources = make_resources(items=[{"id": "abc", "url": CURRENT}])
    assert await card._async_register_resource(make_hass(resources), CURRENT) is True
    resources.async_update_item.assert_not_awaited()
    resources.async_create_item.assert_not_awaited()


async def test_register_card_serves_and_registers_the_script() -> None:
    resources = make_resources()
    hass = make_hass(resources)
    frontend = MagicMock()

    with patch.object(ha_components, "frontend", frontend, create=True):
        await card.async_register_card(hass)

    hass.http.async_register_static_paths.assert_awaited_once()
    config = hass.http.async_register_static_paths.await_args.args[0][0]
    assert config.url_path == card.CARD_URL
    assert config.path == str(card.CARD_FILE)
    frontend.add_extra_js_url.assert_called_once()
    assert frontend.add_extra_js_url.call_args.args[1].startswith(f"{card.CARD_URL}?v=")
    resources.async_create_item.assert_awaited_once()
    hass.bus.async_listen_once.assert_not_called()


async def test_register_card_waits_for_start_when_lovelace_is_not_ready() -> None:
    hass = make_hass(None, state=CoreState.starting)

    with patch.object(ha_components, "frontend", MagicMock(), create=True):
        await card.async_register_card(hass)

    hass.bus.async_listen_once.assert_called_once()
    event, callback = hass.bus.async_listen_once.call_args.args
    assert event == EVENT_HOMEASSISTANT_STARTED

    resources = make_resources()
    hass.data["lovelace"] = {"resources": resources}
    await callback(None)
    resources.async_create_item.assert_awaited_once()


async def test_register_card_does_not_wait_when_home_assistant_is_running() -> None:
    hass = make_hass(None, state=CoreState.running)
    with patch.object(ha_components, "frontend", MagicMock(), create=True):
        await card.async_register_card(hass)
    hass.bus.async_listen_once.assert_not_called()


async def test_register_card_survives_resource_errors(caplog: pytest.LogCaptureFixture) -> None:
    resources = make_resources()
    resources.async_create_item.side_effect = RuntimeError("boom")
    hass = make_hass(resources, state=CoreState.starting)

    with patch.object(ha_components, "frontend", MagicMock(), create=True):
        await card.async_register_card(hass)

    assert "Could not add the dashboard card as a resource" in caplog.text
    hass.bus.async_listen_once.assert_not_called()
