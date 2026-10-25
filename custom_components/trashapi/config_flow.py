"""Config flow for TrashAPI: every API parameter can be set (and changed later)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import (
    TrashApiConnectionError,
    TrashApiDataError,
    async_fetch_pickups,
)
from .const import (
    CONF_GET_CLEANPROFS_DATA,
    CONF_HOUSE_NUMBER,
    CONF_IGNORE_CACHE,
    CONF_LOCATION,
    CONF_SCAN_INTERVAL_HOURS,
    CONF_SHOW_WHOLE_YEAR,
    CONF_ZIP_CODE,
    DEFAULT_GET_CLEANPROFS_DATA,
    DEFAULT_IGNORE_CACHE,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DEFAULT_SHOW_WHOLE_YEAR,
    DOMAIN,
)


def _schema(defaults: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_LOCATION, default=defaults.get(CONF_LOCATION, "")): str,
            vol.Required(CONF_ZIP_CODE, default=defaults.get(CONF_ZIP_CODE, "")): str,
            vol.Required(
                CONF_HOUSE_NUMBER, default=defaults.get(CONF_HOUSE_NUMBER, "")
            ): str,
            vol.Required(
                CONF_SHOW_WHOLE_YEAR,
                default=defaults.get(CONF_SHOW_WHOLE_YEAR, DEFAULT_SHOW_WHOLE_YEAR),
            ): bool,
            vol.Required(
                CONF_GET_CLEANPROFS_DATA,
                default=defaults.get(
                    CONF_GET_CLEANPROFS_DATA, DEFAULT_GET_CLEANPROFS_DATA
                ),
            ): bool,
            vol.Required(
                CONF_IGNORE_CACHE,
                default=defaults.get(CONF_IGNORE_CACHE, DEFAULT_IGNORE_CACHE),
            ): bool,
            vol.Required(
                CONF_SCAN_INTERVAL_HOURS,
                default=defaults.get(
                    CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS
                ),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=48)),
        }
    )


def _normalize(user_input: Mapping[str, Any]) -> dict[str, Any]:
    data = dict(user_input)
    data[CONF_LOCATION] = str(data[CONF_LOCATION]).strip()
    data[CONF_ZIP_CODE] = str(data[CONF_ZIP_CODE]).replace(" ", "").upper()
    data[CONF_HOUSE_NUMBER] = str(data[CONF_HOUSE_NUMBER]).strip()
    return data


async def _async_validate(hass: HomeAssistant, data: Mapping[str, Any]) -> str | None:
    """Try the API with these settings. Returns an error key or None."""
    try:
        pickups = await async_fetch_pickups(async_get_clientsession(hass), data)
    except TrashApiConnectionError:
        return "cannot_connect"
    except TrashApiDataError:
        return "invalid_response"
    if not pickups:
        return "no_data"
    return None


class TrashApiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the initial setup."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TrashApiOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            data = _normalize(user_input)
            await self.async_set_unique_id(
                f"{data[CONF_ZIP_CODE]}_{data[CONF_HOUSE_NUMBER]}".lower()
            )
            self._abort_if_unique_id_configured()

            if (error := await _async_validate(self.hass, data)) is None:
                return self.async_create_entry(
                    title=f"Afvalkalender {data[CONF_ZIP_CODE]} {data[CONF_HOUSE_NUMBER]}",
                    data=data,
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(user_input or {}),
            errors=errors,
        )


class TrashApiOptionsFlow(OptionsFlow):
    """Change any parameter afterwards via the 'Configureren' button."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current = {**self.config_entry.data, **self.config_entry.options}

        if user_input is not None:
            data = _normalize(user_input)
            if (error := await _async_validate(self.hass, data)) is None:
                return self.async_create_entry(title="", data=data)
            errors["base"] = error
            current = data

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
        )
