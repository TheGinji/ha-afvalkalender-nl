"""Config flow for TrashAPI.

* Setup asks for the address and the API settings.
* "Herconfigureren" changes the address (stored in entry.data).
* "Configureren" changes the settings (stored in entry.options).
"""

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
    ADDRESS_KEYS,
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
    SETTING_KEYS,
)


def _address_fields(defaults: Mapping[str, Any]) -> dict[Any, Any]:
    return {
        vol.Required(CONF_LOCATION, default=defaults.get(CONF_LOCATION, "")): str,
        vol.Required(CONF_ZIP_CODE, default=defaults.get(CONF_ZIP_CODE, "")): str,
        vol.Required(CONF_HOUSE_NUMBER, default=defaults.get(CONF_HOUSE_NUMBER, "")): str,
    }


def _setting_fields(defaults: Mapping[str, Any]) -> dict[Any, Any]:
    return {
        vol.Required(
            CONF_SHOW_WHOLE_YEAR,
            default=defaults.get(CONF_SHOW_WHOLE_YEAR, DEFAULT_SHOW_WHOLE_YEAR),
        ): bool,
        vol.Required(
            CONF_GET_CLEANPROFS_DATA,
            default=defaults.get(CONF_GET_CLEANPROFS_DATA, DEFAULT_GET_CLEANPROFS_DATA),
        ): bool,
        vol.Required(
            CONF_IGNORE_CACHE,
            default=defaults.get(CONF_IGNORE_CACHE, DEFAULT_IGNORE_CACHE),
        ): bool,
        vol.Required(
            CONF_SCAN_INTERVAL_HOURS,
            default=defaults.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
        ): vol.All(vol.Coerce(int), vol.Range(min=1, max=48)),
    }


def _normalize_address(user_input: Mapping[str, Any]) -> dict[str, Any]:
    return {
        CONF_LOCATION: str(user_input[CONF_LOCATION]).strip(),
        CONF_ZIP_CODE: str(user_input[CONF_ZIP_CODE]).replace(" ", "").upper(),
        CONF_HOUSE_NUMBER: str(user_input[CONF_HOUSE_NUMBER]).strip(),
    }


def _unique_id(address: Mapping[str, Any]) -> str:
    return f"{address[CONF_ZIP_CODE]}_{address[CONF_HOUSE_NUMBER]}".lower()


def _title(address: Mapping[str, Any]) -> str:
    return f"Afvalkalender {address[CONF_ZIP_CODE]} {address[CONF_HOUSE_NUMBER]}"


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
    """Handle the initial setup and reconfiguration of the address."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TrashApiOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            address = _normalize_address(user_input)
            settings = {key: user_input[key] for key in SETTING_KEYS}

            await self.async_set_unique_id(_unique_id(address))
            self._abort_if_unique_id_configured()

            if (error := await _async_validate(self.hass, {**address, **settings})) is None:
                return self.async_create_entry(
                    title=_title(address), data=address, options=settings
                )
            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {**_address_fields(user_input or {}), **_setting_fields(user_input or {})}
            ),
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the address (for example after moving house)."""
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}

        if user_input is not None:
            address = _normalize_address(user_input)
            unique_id = _unique_id(address)

            if any(
                other.unique_id == unique_id and other.entry_id != entry.entry_id
                for other in self._async_current_entries()
            ):
                errors["base"] = "already_configured"
            elif (
                error := await _async_validate(self.hass, {**entry.options, **address})
            ) is None:
                self.hass.config_entries.async_update_entry(
                    entry,
                    title=_title(address),
                    unique_id=unique_id,
                    data={**entry.data, **address},
                )
                # The update listener in __init__ reloads the entry when something changed
                return self.async_abort(reason="reconfigure_successful")
            else:
                errors["base"] = error

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(_address_fields(user_input or entry.data)),
            errors=errors,
        )


class TrashApiOptionsFlow(OptionsFlow):
    """Change the API settings via the 'Configureren' button."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        current: Mapping[str, Any] = self.config_entry.options

        if user_input is not None:
            if (
                error := await _async_validate(
                    self.hass, {**self.config_entry.data, **user_input}
                )
            ) is None:
                return self.async_create_entry(title="", data=user_input)
            errors["base"] = error
            current = user_input

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(_setting_fields(current)),
            errors=errors,
        )
