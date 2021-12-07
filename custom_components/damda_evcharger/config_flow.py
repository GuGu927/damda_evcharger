"""Config flow for Damda EV integration."""
from __future__ import annotations
from urllib.parse import quote_plus, unquote
import voluptuous as vol

# import homeassistant.helpers.config_validation as cv

from homeassistant import config_entries

# from homeassistant.components.person import DOMAIN as PERSON_DOMAIN

from .const import (
    CONF_EV,
    DOMAIN,
    CONF_API,
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
