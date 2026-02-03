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
