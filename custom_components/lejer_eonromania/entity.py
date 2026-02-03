"""Base entity class for E-ON Romania integration."""
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
