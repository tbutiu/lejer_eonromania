"""ConfigFlow for E-ON Romania integration."""

import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, DEFAULT_USER, DEFAULT_PASS
from .api import EonApiClient

_LOGGER = logging.getLogger(__name__)

class EonRomaniaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle ConfigFlow for E-ON Romania."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            username = user_input["username"]
            password = user_input["password"]
            cod_incasare = user_input["cod_incasare"]
            update_interval = user_input["update_interval"]

            # Validate cod_incasare length
            if len(cod_incasare) < 12:
                cod_incasare = cod_incasare.zfill(12)
            elif len(cod_incasare) > 12:
                errors["cod_incasare"] = "invalid_cod_incasare"

            if not errors:
                session = async_get_clientsession(self.hass)
                api_client = EonApiClient(session, username, password)
                
                if await api_client.async_login():
                    return self.async_create_entry(
                        title=f"E-ON România ({cod_incasare})",
                        data={
                            "username": username,
                            "password": password,
                            "cod_incasare": cod_incasare,
                            "update_interval": update_interval,
                        },
                    )
                else:
                    errors["base"] = "auth_failed"
                    _LOGGER.error("Auth failed for user %s", username)

        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
            vol.Required("cod_incasare"): str,
            vol.Optional("update_interval", default=DEFAULT_UPDATE_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return EonRomaniaOptionsFlow(config_entry)


class EonRomaniaOptionsFlow(config_entries.OptionsFlow):
    """Handle OptionsFlow for E-ON Romania."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            # We can only update 'options' here directly via async_create_entry 
            # or we enforce new data via async_update_entry if we want to change credentials too.
            updated_data = {
                "username": user_input["username"],
                "password": user_input["password"],
                "cod_incasare": user_input["cod_incasare"],
            }
            updated_options = {
                "update_interval": user_input["update_interval"]
            }
            
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=updated_data,
                options=updated_options
            )
            return self.async_create_entry(title="", data={})

        data_schema = vol.Schema({
            vol.Optional("username", default=self.config_entry.data.get("username", "")): str,
            vol.Optional("password", default=self.config_entry.data.get("password", "")): str,
            vol.Optional("cod_incasare", default=self.config_entry.data.get("cod_incasare", "")): str,
            vol.Optional("update_interval", default=self.config_entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)): int,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
