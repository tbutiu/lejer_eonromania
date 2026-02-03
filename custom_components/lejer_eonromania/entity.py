"""Base entity class for E-ON Romania integration."""
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

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import DeviceEntryType

from .const import DOMAIN, ATTRIBUTION

class EonEntity(CoordinatorEntity):
    """Base class for E-ON Romania entities."""

    def __init__(self, coordinator, config_entry):
        """Initialize the base entity."""
        super().__init__(coordinator)
        self.config_entry = config_entry
        self._cod_incasare = config_entry.data.get("cod_incasare")

    @property
    def device_info(self):
        """Return device information."""
        data = self.coordinator.data.get("dateuser", {})
        address_obj = data.get("consumptionPointAddress", {})
        street_obj = address_obj.get("street", {})
        
        street_type = street_obj.get("streetType", {}).get("label", "Strada")
        street_name = street_obj.get("streetName", "Necunoscută")
        street_no = address_obj.get("streetNumber", "N/A")
        apartment = address_obj.get("apartment", "N/A")
        locality_name = address_obj.get("locality", {}).get("localityName", "Necunoscut")

        full_address = f"{street_type} {street_name} {street_no} ap. {apartment}, {locality_name}"

        return {
            "identifiers": {(DOMAIN, self._cod_incasare)},
            "name": f"E-ON România - {full_address} ({self._cod_incasare})",
            "manufacturer": "E Victor Teodor Butiu ( tbutiu )",
            "model": "E-ON România",
            "entry_type": DeviceEntryType.SERVICE,
        }

    @property
    def extra_state_attributes(self):
        """Return common attributes."""
        return {
            "attribution": ATTRIBUTION,
        }
