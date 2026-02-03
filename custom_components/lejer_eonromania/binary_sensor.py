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
"""Binary Sensor platform for E-ON Romania."""

import logging
from datetime import datetime
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from .const import DOMAIN, KEY_CITIREINDEX, KEY_FACTURASOLD
from .entity import EonEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the E-ON Romania binary sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]
    
    contracts_list = coordinator.data.get(KEY_CONTRACTS, [])
    sensors = []
    
    for contract in contracts_list:
        cod_incasare = None
        if "contractDetails" in contract:
            cod_incasare = contract["contractDetails"].get("accountContract")
        else:
            cod_incasare = contract.get("contractId") or contract.get("accountContract")

        if not cod_incasare:
            continue
            
        sensors.extend([
            EonWindowOpenBinarySensor(coordinator, config_entry, cod_incasare),
            EonInvoiceDueBinarySensor(coordinator, config_entry, cod_incasare),
        ])

    async_add_entities(sensors)

class EonWindowOpenBinarySensor(EonEntity, BinarySensorEntity):
    """Binary sensor indicating if index submission is allowed."""

    def __init__(self, coordinator, config_entry, cod_incasare):
        super().__init__(coordinator, config_entry, cod_incasare)
        self._attr_name = "Perioadă transmitere index"
        self._attr_unique_id = f"{DOMAIN}_window_open_{config_entry.entry_id}_{cod_incasare}"
        self._attr_entity_id = f"binary_sensor.{DOMAIN}_window_open_{cod_incasare}"
        self._attr_device_class = BinarySensorDeviceClass.WINDOW  # Metaphorical window

    @property
    def is_on(self):
        data = self.contract_data.get(KEY_CITIREINDEX)
        if not data: return False
        return data.get("readingPeriod", {}).get("allowedReading", False)

    @property
    def icon(self):
        return "mdi:calendar-check" if self.is_on else "mdi:calendar-remove"


class EonInvoiceDueBinarySensor(EonEntity, BinarySensorEntity):
    """Binary sensor indicating if an invoice is due soon (within 3 days) or overdue."""

    def __init__(self, coordinator, config_entry, cod_incasare):
        super().__init__(coordinator, config_entry, cod_incasare)
        self._attr_name = "Scadență factură"
        self._attr_unique_id = f"{DOMAIN}_invoice_due_{config_entry.entry_id}_{cod_incasare}"
        self._attr_entity_id = f"binary_sensor.{DOMAIN}_invoice_due_{cod_incasare}"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self):
        data = self.contract_data.get(KEY_FACTURASOLD)
        if not data or not isinstance(data, list):
            return False
            
        now = datetime.now()
        for item in data:
            if item.get("balanceValue", 0) > 0:
                raw_date = item.get("maturityDate")
                if raw_date:
                    try:
                        # Assuming date format is dd.mm.YYYY
                        due_date = datetime.strptime(raw_date, "%d.%m.%Y")
                        days_until = (due_date - now).days
                        if days_until <= 3: # Due soon or overdue
                            return True
                    except ValueError:
                         continue
        return False
