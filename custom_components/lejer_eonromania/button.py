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

"""Button platform for E-ON Romania."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN, KEY_CITIREINDEX
from .entity import EonEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the E-ON Romania buttons."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]

    async_add_entities([TrimiteIndexButton(coordinator, config_entry)])

class TrimiteIndexButton(EonEntity, ButtonEntity):
    """Button to send meter reading."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Trimite index"
        self._attr_unique_id = f"{DOMAIN}_trimite_index_{config_entry.entry_id}"
        self._attr_entity_id = f"button.{DOMAIN}_trimite_index_{self._cod_incasare}"
        self._attr_icon = "mdi:counter"

    async def async_press(self):
        """Send the index to E-ON."""
        try:
            # Get index value from input_number
            input_entity = "input_number.gas_meter_reading"
            if not (state := self.hass.states.get(input_entity)):
                _LOGGER.error("Entity %s not found.", input_entity)
                return

            try:
                index_value = int(float(state.state))
            except ValueError:
                _LOGGER.error("Invalid value in %s: %s", input_entity, state.state)
                return

            # Get internal meter ID (ablbelnr)
            ablbelnr = None
            if data := self.coordinator.data.get(KEY_CITIREINDEX):
                if devices := data.get("indexDetails", {}).get("devices", []):
                    for device in devices:
                        if indexes := device.get("indexes", []):
                            ablbelnr = indexes[0].get("ablbelnr")
                            break
            
            if not ablbelnr:
                _LOGGER.error("Internal meter ID (ablbelnr) not found.")
                return

            # Call API
            await self.coordinator.api_client.async_trimite_index(
                account_contract=self._cod_incasare,
                ablbelnr=ablbelnr,
                index_value=index_value,
            )

            await self.coordinator.async_request_refresh()
            _LOGGER.info("Index sent successfully for account %s", self._cod_incasare)

        except Exception as e:
            _LOGGER.error("Error sending index: %s", e)
