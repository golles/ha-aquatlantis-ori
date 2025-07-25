"""Config flow for Aquatlantis Ori integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import SOURCE_RECONFIGURE, ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig, TextSelectorType

from aquatlantis_ori import (
    AquatlantisOriClient,
    AquatlantisOriConnectionError,
    AquatlantisOriError,
    AquatlantisOriLoginError,
    AquatlantisOriTimeoutError,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): TextSelector(TextSelectorConfig(type=TextSelectorType.EMAIL)),
        vol.Required(CONF_PASSWORD): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
    },
)


class OriConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aquatlantis Ori."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors = {}
        user_input = user_input or {}

        if user_input:
            email = user_input[CONF_EMAIL]
            password = user_input[CONF_PASSWORD]

            try:
                client = AquatlantisOriClient(email, password, async_get_clientsession(self.hass))
                await client.connect()
            except AquatlantisOriLoginError:
                errors["base"] = "invalid_auth"
            except AquatlantisOriTimeoutError:
                errors["base"] = "timeout"
            except AquatlantisOriConnectionError:
                errors["base"] = "cannot_connect"
            except AquatlantisOriError:
                _LOGGER.exception("Error connecting to Aquatlantis Ori")
                errors["base"] = "unknown_error"
            else:
                if self.source == SOURCE_RECONFIGURE:
                    return self.async_update_reload_and_abort(
                        self._get_reconfigure_entry(),
                        title=user_input[CONF_EMAIL],
                        data=user_input,
                    )
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=user_input,
                )
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(CONFIG_SCHEMA, user_input),
            errors=errors,
        )

    async def async_step_reconfigure(self, _: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle reconfiguration."""
        data = self._get_reconfigure_entry().data.copy()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(CONFIG_SCHEMA, data),
        )
