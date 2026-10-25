"""Small client for https://trashapi.azurewebsites.net."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

import aiohttp

from .const import (
    API_URL,
    CONF_GET_CLEANPROFS_DATA,
    CONF_HOUSE_NUMBER,
    CONF_IGNORE_CACHE,
    CONF_LOCATION,
    CONF_SHOW_WHOLE_YEAR,
    CONF_ZIP_CODE,
    DEFAULT_GET_CLEANPROFS_DATA,
    DEFAULT_IGNORE_CACHE,
    DEFAULT_SHOW_WHOLE_YEAR,
)


class TrashApiError(Exception):
    """Base error."""


class TrashApiConnectionError(TrashApiError):
    """Could not reach the API."""


class TrashApiDataError(TrashApiError):
    """The API answered with something unexpected."""


def _bool(value: Any) -> str:
    return "true" if value else "false"


def build_params(config: Mapping[str, Any]) -> dict[str, str]:
    """Translate the config into the query parameters of the API."""
    return {
        "Location": str(config[CONF_LOCATION]),
        "ZipCode": str(config[CONF_ZIP_CODE]),
        "HouseNumber": str(config[CONF_HOUSE_NUMBER]),
        "ShowWholeYear": _bool(config.get(CONF_SHOW_WHOLE_YEAR, DEFAULT_SHOW_WHOLE_YEAR)),
        "GetCleanprofsData": _bool(
            config.get(CONF_GET_CLEANPROFS_DATA, DEFAULT_GET_CLEANPROFS_DATA)
        ),
        "IgnoreCache": _bool(config.get(CONF_IGNORE_CACHE, DEFAULT_IGNORE_CACHE)),
    }


def parse_pickups(payload: Any) -> dict[str, list[date]]:
    """Turn the API answer into {waste type: sorted unique pickup dates}."""
    if not isinstance(payload, list):
        raise TrashApiDataError("Unexpected response from the API")

    result: dict[str, set[date]] = {}
    for item in payload:
        try:
            name = str(item["name"]).strip()
            pickup = datetime.fromisoformat(str(item["date"])).date()
        except (KeyError, TypeError, ValueError):
            continue
        if name:
            result.setdefault(name, set()).add(pickup)

    return {name: sorted(dates) for name, dates in result.items()}


def next_pickup(dates: list[date], today: date) -> date | None:
    """First pickup that is today or later."""
    for pickup in dates:
        if pickup >= today:
            return pickup
    return None


async def async_fetch_pickups(
    session: aiohttp.ClientSession, config: Mapping[str, Any]
) -> dict[str, list[date]]:
    """Call the API and return the parsed pickups."""
    try:
        async with session.get(
            API_URL,
            params=build_params(config),
            headers={"accept": "*/*"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            response.raise_for_status()
            payload = await response.json(content_type=None)
    except (aiohttp.ClientError, TimeoutError) as err:
        raise TrashApiConnectionError(str(err)) from err
    except ValueError as err:
        raise TrashApiDataError("Response is not valid JSON") from err

    return parse_pickups(payload)
