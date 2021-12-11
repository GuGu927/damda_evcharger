"""Config flow for Damda EV integration."""
from __future__ import annotations
from urllib.parse import quote_plus, unquote
import voluptuous as vol

# import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries
from homeassistant.core import callback

# from homeassistant.components.person import DOMAIN as PERSON_DOMAIN

from .const import (
    CONF_EV,
    DOMAIN,
    CONF_API,
    OPTION_LIST,
    # CONF_NEAR, CONF_PERSON,
)

STEP_USER_DATA_SCHEMA = {
    vol.Required(CONF_API): str,
    vol.Optional(CONF_EV, default=""): str,
}


def make_unique(i):
    """Make unique_id."""
    key = i.get(CONF_API)
    return f"{key}_{i[CONF_EV]}"


def check_key(i):
    """Check input data is valid and return data."""
    i_key = i[CONF_API].strip()
    k_dec = unquote(i_key)
    if i_key == k_dec:
        i[CONF_API] = quote_plus(i_key)
    return i


def int_between(min_int, max_int):
    """Return an integer between 'min_int' and 'max_int'."""
    return vol.All(vol.Coerce(int), vol.Range(min=min_int, max=max_int))


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Damda Weather."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            user_input = check_key(user_input)
            await self.async_set_unique_id(make_unique(user_input))
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_EV],
                data=user_input,
            )

        user_data = STEP_USER_DATA_SCHEMA.copy()
        # all_person = self.hass.states.async_entity_ids(PERSON_DOMAIN)
        # user_data[vol.Optional(CONF_PERSON, default=[])] = cv.multi_select(
        #     sorted(all_person)
        # )
        # user_data[vol.Optional(CONF_NEAR, default=1)] = int_between(1, 10)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(user_data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle a option flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for Damda Pad."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        conf = self.config_entry
        if conf.source == config_entries.SOURCE_IMPORT:
            return self.async_show_form(step_id="init", data_schema=None)
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = {}
        data_list = [CONF_API]
        data_opt = []
        for name, default, validation in OPTION_LIST:
            to_default = conf.options.get(name, default)
            if name in data_list and conf.options.get(name, default) == default:
                to_default = conf.data.get(name, default)
            key = (
                vol.Optional(name, default=to_default)
                if name in data_opt
                else vol.Required(name, default=to_default)
            )
            options_schema[key] = validation
        return self.async_show_form(
            step_id="init", data_schema=vol.Schema(options_schema)
        )
