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
"""Number platform for E-ON Romania."""

import logging
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, KEY_CONTRACTS
from .entity import EonEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the E-ON Romania numbers."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    
    contracts_list = coordinator.data.get(KEY_CONTRACTS, [])
    entities = []
    
    for contract in contracts_list:
        cod_incasare = None
        if "contractDetails" in contract:
            cod_incasare = contract["contractDetails"].get("accountContract")
        else:
            cod_incasare = contract.get("contractId") or contract.get("accountContract")

        if not cod_incasare:
            continue
            
        entities.append(EonIndexInput(coordinator, config_entry, cod_incasare))

    async_add_entities(entities)

class EonIndexInput(EonEntity, NumberEntity):
    """Number entity to input the index value."""

    def __init__(self, coordinator, config_entry, cod_incasare):
        super().__init__(coordinator, config_entry, cod_incasare)
        self._attr_name = "Index de transmis"
        self._attr_unique_id = f"{DOMAIN}_index_input_{config_entry.entry_id}_{cod_incasare}"
        self._attr_entity_id = f"number.{DOMAIN}_index_input_{cod_incasare}"
        self._attr_icon = "mdi:counter"
        
        # Configuration
        self._attr_native_min_value = 0
        self._attr_native_max_value = 999999
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        
        # Restore state
        self._attr_native_value = 0

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self._attr_native_value = value
        self.async_write_ha_state()

    @property
    def native_value(self) -> float:
        """Return the value reported by the number."""
        return self._attr_native_value
