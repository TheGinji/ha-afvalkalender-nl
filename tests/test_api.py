"""Tests for the TrashAPI client."""

from __future__ import annotations

from datetime import date
import re

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.trashapi import api

URL = re.compile(r"https://trashapi\.azurewebsites\.net/Trash.*")
CONFIG = {"location": "Leeuwarden", "zip_code": "1234AB", "house_number": "12"}


def test_build_params_uses_defaults() -> None:
    assert api.build_params(CONFIG) == {
        "Location": "Leeuwarden",
        "ZipCode": "1234AB",
        "HouseNumber": "12",
        "ShowWholeYear": "true",
        "GetCleanprofsData": "true",
        "IgnoreCache": "false",
    }


def test_build_params_respects_flags() -> None:
    params = api.build_params(
        {**CONFIG, "show_whole_year": False, "get_cleanprofs_data": False, "ignore_cache": True}
    )
    assert params["ShowWholeYear"] == "false"
    assert params["GetCleanprofsData"] == "false"
    assert params["IgnoreCache"] == "true"


def test_parse_pickups_groups_sorts_and_skips_bad_items() -> None:
    payload = [
        {"date": "2026-11-12T00:00:00", "name": "Gft"},
        {"date": "2026-10-29T00:00:00", "name": " Gft "},
        {"date": "2026-10-29T00:00:00", "name": "Gft"},
        {"date": "2026-11-03T00:00:00", "name": "Restafval"},
        {"date": "not-a-date", "name": "Papier"},
        {"name": "Papier"},
        {"date": "2026-11-16T00:00:00", "name": "  "},
        "garbage",
    ]
    assert api.parse_pickups(payload) == {
        "Gft": [date(2026, 10, 29), date(2026, 11, 12)],
        "Restafval": [date(2026, 11, 3)],
    }


@pytest.mark.parametrize("payload", [{"a": 1}, "text", None])
def test_parse_pickups_rejects_non_list(payload: object) -> None:
    with pytest.raises(api.TrashApiDataError):
        api.parse_pickups(payload)


def test_next_pickup() -> None:
    dates = [date(2026, 10, 27), date(2026, 11, 12)]
    assert api.next_pickup(dates, date(2026, 10, 1)) == date(2026, 10, 27)
    assert api.next_pickup(dates, date(2026, 10, 27)) == date(2026, 10, 27)
    assert api.next_pickup(dates, date(2026, 10, 28)) == date(2026, 11, 12)
    assert api.next_pickup(dates, date(2026, 11, 13)) is None
    assert api.next_pickup([], date(2026, 10, 1)) is None


async def test_fetch_pickups(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, json=[{"date": "2026-10-29T00:00:00", "name": "Gft"}])
    result = await api.async_fetch_pickups(async_get_clientsession(hass), CONFIG)
    assert result == {"Gft": [date(2026, 10, 29)]}
    assert aioclient_mock.call_count == 1


async def test_fetch_http_error(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, status=500)
    with pytest.raises(api.TrashApiConnectionError):
        await api.async_fetch_pickups(async_get_clientsession(hass), CONFIG)


async def test_fetch_timeout(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, exc=TimeoutError)
    with pytest.raises(api.TrashApiConnectionError):
        await api.async_fetch_pickups(async_get_clientsession(hass), CONFIG)


async def test_fetch_invalid_json(hass: HomeAssistant, aioclient_mock) -> None:
    aioclient_mock.get(URL, text="not json")
    with pytest.raises(api.TrashApiDataError):
        await api.async_fetch_pickups(async_get_clientsession(hass), CONFIG)
