#  Copyright (c) 2026 tbutiu
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

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
            update_interval = user_input.get("update_interval", DEFAULT_UPDATE_INTERVAL)
            if not errors:
                session = async_get_clientsession(self.hass)
                api_client = EonApiClient(session, username, password)
                
                if await api_client.async_login():
                    await self.async_set_unique_id(username)
                    self._abort_if_unique_id_configured()
                    
                    return self.async_create_entry(
                        title=f"{username}",
                        data={
                            "username": username,
                            "password": password,
                            "update_interval": update_interval,
                        },
                    )
                else:
                    errors["base"] = "auth_failed"
                    _LOGGER.error("Auth failed for user %s", username)

        data_schema = vol.Schema({
            vol.Required("username"): str,
            vol.Required("password"): str,
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
            vol.Optional("update_interval", default=self.config_entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)): int,
        })

        return self.async_show_form(step_id="init", data_schema=data_schema)
