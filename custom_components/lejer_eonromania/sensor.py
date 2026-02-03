"""Sensor platform for E-ON Romania."""

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

import logging
from datetime import datetime
from collections import defaultdict

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.sensor import SensorEntity

from .const import (
    DOMAIN, ATTRIBUTION, MONTHS_RO,
    KEY_DATEUSER, KEY_CITIREINDEX, KEY_CONVENTIECONSUM, 
    KEY_COMPARAREANUALAGRAFIC, KEY_ARHIVA, KEY_FACTURASOLD, 
    KEY_FACTURASOLD_PROSUM, KEY_USER_WALLET, KEY_RESCHEDULING_PLANS, 
    KEY_PAYMENT_NOTICES, KEY_PAYMENTS
)
from .entity import EonEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the E-ON Romania sensors."""
    data = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = data["coordinator"]

    sensors = [
        DateContractSensor(coordinator, config_entry),
        ConventieConsumSensor(coordinator, config_entry),
        FacturaRestantaSensor(coordinator, config_entry),
    ]

    # Citire Index Data
    citireindex_data = coordinator.data.get(KEY_CITIREINDEX)
    if citireindex_data:
        devices = citireindex_data.get("indexDetails", {}).get("devices", [])
        if devices:
            seen_devices = set()
            for device in devices:
                device_number = device.get("deviceNumber", "unknown")
                if device_number not in seen_devices:
                    sensors.append(CitireIndexSensor(coordinator, config_entry, device_number))
                    sensors.append(CitirePermisaSensor(coordinator, config_entry, device_number))
                    seen_devices.add(device_number)
        else:
             # Fallback if no devices found
             sensors.append(CitireIndexSensor(coordinator, config_entry, None))
             sensors.append(CitirePermisaSensor(coordinator, config_entry, None))

    # Archive Data (History)
    arhiva_data = coordinator.data.get(KEY_ARHIVA)
    if arhiva_data:
        history_list = arhiva_data.get("history", [])
        for item in history_list:
            if year := item.get("year"):
                sensors.append(ArhivaSensor(coordinator, config_entry, year))

    # Payments History
    payments_data = coordinator.data.get(KEY_PAYMENTS, {})
    payments_list = payments_data.get("list", []) if payments_data else []
    
    if payments_list:
        payments_by_year = defaultdict(list)
        for payment in payments_list:
            if raw_date := payment.get("paymentDate"):
                try:
                    year = int(raw_date.split("-")[0])
                    payments_by_year[year].append(payment)
                except ValueError:
                    continue
        
        for year in payments_by_year:
            sensors.append(ArhivaPlatiSensor(coordinator, config_entry, year))

    # Annual Comparison
    comp_data = coordinator.data.get(KEY_COMPARAREANUALAGRAFIC, {})
    if "consumption" in comp_data:
        yearly_data = defaultdict(dict)
        for item in comp_data["consumption"]:
            year = item.get("year")
            month = item.get("month")
            if year and month:
                yearly_data[year][month] = {
                    "consumptionValue": item.get("consumptionValue"),
                    "consumptionValueDayValue": item.get("consumptionValueDayValue")
                }
        
        for year, monthly_values in yearly_data.items():
             sensors.append(ArhivaComparareConsumAnualGraficSensor(coordinator, config_entry, year, monthly_values))

    # Prosumer Balance
    if coordinator.data.get(KEY_FACTURASOLD_PROSUM):
        sensors.append(EonInvoiceBalanceProsumSensor(coordinator, config_entry))

    # Wallet
    if (wallet := coordinator.data.get(KEY_USER_WALLET)) and wallet.get("balance") is not None:
        sensors.append(EonUserWalletSensor(coordinator, config_entry))

    # Rescheduling Plans
    if coordinator.data.get(KEY_RESCHEDULING_PLANS):
        sensors.append(EonReschedulingPlanSensor(coordinator, config_entry))

    # Payment Notices
    if coordinator.data.get(KEY_PAYMENT_NOTICES):
        sensors.append(EonPaymentNoticeSensor(coordinator, config_entry))

    async_add_entities(sensors)


class DateContractSensor(EonEntity, SensorEntity):
    """Sensor for contract data."""
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Date contract"
        self._attr_unique_id = f"{DOMAIN}_date_contract_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_date_contract_{self._cod_incasare}"
        self._attr_icon = "mdi:file-document-edit-outline"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_DATEUSER)
        return data.get("accountContract") if data else None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(KEY_DATEUSER)
        if not data:
            return {}

        prices = data.get("supplierAndDistributionPrice", {})
        price_comps = prices.get("priceComponents", {})

        attrs = super().extra_state_attributes
        attrs.update({
            "Cod încasare": data.get("accountContract"),
            "Cod loc de consum (NLC)": data.get("consumptionPointCode"),
            "CLC": data.get("pod"),
            "Operator Distribuție": data.get("distributorName"),
            "Preț final (fără TVA)": f"{prices.get('contractualPrice')} lei",
            "Preț final (cu TVA)": f"{prices.get('contractualPriceWithVat')} lei",
            "Preț furnizare": f"{price_comps.get('supplierPrice')} lei/kWh",
            "Tarif distribuție": f"{price_comps.get('distributionPrice')} lei/kWh",
            "Tarif transport": f"{price_comps.get('transportPrice')} lei/kWh",
            "PCS": str(prices.get("pcs")),
            "Verificare instalație": data.get("verificationExpirationDate"),
            "Revizie tehnică": data.get("revisionExpirationDate"),
        })
        return attrs


class CitireIndexSensor(EonEntity, SensorEntity):
    """Sensor for current meter index."""

    def __init__(self, coordinator, config_entry, device_number):
        super().__init__(coordinator, config_entry)
        self.device_number = device_number
        self._attr_name = "Index curent"
        self._attr_unique_id = f"{DOMAIN}_index_curent_{config_entry.entry_id}_{device_number if device_number else 'main'}"
        self._attr_entity_id = f"sensor.{DOMAIN}_index_curent_{self._cod_incasare}_{device_number if device_number else 'main'}"
        self._attr_state_class = "total_increasing"  # For Energy Dashboard
        
        # Determine device type (Gas vs Electric)
        self._device_type = self._determine_device_type()
        if self._device_type == "electric":
            self._attr_device_class = "energy"
            self._attr_native_unit_of_measurement = "kWh"
            self._attr_icon = "mdi:lightning-bolt"
        else:
            self._attr_device_class = "gas"
            self._attr_native_unit_of_measurement = "m³"
            self._attr_icon = "mdi:fire"

    def _determine_device_type(self):
        """Guess device type based on metadata."""
        data = self.coordinator.data.get(KEY_CITIREINDEX)
        if not data: return "gas" # default

        devices = data.get("indexDetails", {}).get("devices", [])
        for dev in devices:
            if self.device_number and dev.get("deviceNumber") != self.device_number:
                continue
            
            # Check for unit, series code, or description if available
            # This is a heuristic; API exploration might be needed for precise field
            # For now, default to gas unless we see "kWh" or specific flags
            if dev.get("deviceType") == "ELECTRIC": 
                return "electric"
            
            # Checking indexes for unit of measurement if available
            indexes = dev.get("indexes", [])
            for idx in indexes:
                if idx.get("unit") == "KWH":
                    return "electric"
        
        return "gas"

    @property
    def native_value(self):
        data = self.coordinator.data.get(KEY_CITIREINDEX)
        if not data: return None
        
        devices = data.get("indexDetails", {}).get("devices", [])
        for dev in devices:
            if self.device_number and dev.get("deviceNumber") != self.device_number:
                continue
            
            indexes = dev.get("indexes", [])
            if indexes:
                return int(indexes[0].get("currentValue") or indexes[0].get("oldValue") or 0)
        return None

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(KEY_CITIREINDEX)
        if not data: return {}

        devices = data.get("indexDetails", {}).get("devices", [])
        reading_period = data.get("readingPeriod", {})
        
        attrs = super().extra_state_attributes
        for dev in devices:
            if self.device_number and dev.get("deviceNumber") != self.device_number:
                continue

            if indexes := dev.get("indexes", []):
                idx = indexes[0]
                attrs.update({
                    "Număr dispozitiv": dev.get("deviceNumber"),
                    "Tip": self._device_type,
                    "ID Citire": idx.get("ablbelnr"),
                    "Start citire": reading_period.get("startDate"),
                    "Final citire": reading_period.get("endDate"),
                    "Permis citire": "Da" if reading_period.get("allowedReading") else "Nu",
                    "Permis modificare": "Da" if reading_period.get("allowChange") else "Nu",
                    "Index propus": idx.get("currentValue"),
                    "Ultima citire": idx.get("oldValue"),
                })
                return attrs
        return attrs


class CitirePermisaSensor(EonEntity, SensorEntity):
    """Sensor indicating if reading submission is allowed."""

    def __init__(self, coordinator, config_entry, device_number):
        super().__init__(coordinator, config_entry)
        self.device_number = device_number
        self._attr_name = "Citire permisă"
        self._attr_unique_id = f"{DOMAIN}_citire_permisa_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_citire_permisa_{self._cod_incasare}"
        self._attr_icon = "mdi:calendar-check"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_CITIREINDEX)
        if not data: return "Indisponibil"
        allowed = data.get("readingPeriod", {}).get("allowedReading")
        return "Da" if allowed else "Nu"


class FacturaRestantaSensor(EonEntity, SensorEntity):
    """Sensor for unpaid invoices."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Factură restantă"
        self._attr_unique_id = f"{DOMAIN}_factura_restanta_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_factura_restanta_{self._cod_incasare}"
        self._attr_icon = "mdi:invoice-text-arrow-left"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_FACTURASOLD)
        if not data or not isinstance(data, list):
            return "Nu"
        return "Da" if any(item.get("issuedValue", 0) > 0 for item in data) else "Nu"

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data.get(KEY_FACTURASOLD)
        attrs = super().extra_state_attributes
        if not data or not isinstance(data, list):
            attrs["Total neachitat"] = "0.00 lei"
            return attrs

        total = 0.0
        for i, item in enumerate(data, 1):
            val = float(item.get("issuedValue", 0))
            bal = float(item.get("balanceValue", 0))
            display = val if val == bal else bal
            
            if display > 0:
                total += display
                due_date = item.get("maturityDate", "N/A")
                attrs[f"Factură {i}"] = f"{display:.2f} lei (Scadentă: {due_date})"

        attrs["Total neachitat"] = f"{total:.2f} lei"
        return attrs


class ConventieConsumSensor(EonEntity, SensorEntity):
    """Sensor for consumption convention."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Convenție consum"
        self._attr_unique_id = f"{DOMAIN}_conventie_consum_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_conventie_consum_{self._cod_incasare}"
        self._attr_icon = "mdi:chart-box-outline"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_CONVENTIECONSUM)
        if not data or not isinstance(data, list) or not data:
            return 0
        
        convention = data[0].get("conventionLine", {})
        if not convention:
            return 0
            
        # Count months with non-zero value
        count = 0
        for i in range(1, 13):
            if convention.get(f"valueMonth{i}", 0) > 0:
                count += 1
        return count

    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes
        data = self.coordinator.data.get(KEY_CONVENTIECONSUM)
        
        if data and isinstance(data, list) and data:
            convention = data[0].get("conventionLine", {})
            if convention:
                for i in range(1, 13):
                    val = convention.get(f"valueMonth{i}", 0)
                    if val > 0:
                        # Use a fixed month name mapping or simpler approach
                        month_key = f"valueMonth{i}"
                        month_name = datetime(2000, i, 1).strftime("%B")
                        # Try to use RO names if imported, else fallback
                        month_ro = MONTHS_RO.get(month_name, month_name)
                        attrs[f"Convenție {month_ro}"] = f"{val} mc"
        return attrs


class ArhivaSensor(EonEntity, SensorEntity):
    """Sensor for archive data by year."""

    def __init__(self, coordinator, config_entry, year):
        super().__init__(coordinator, config_entry)
        self._year = year
        self._attr_name = f"Arhivă index - {year}"
        self._attr_unique_id = f"{DOMAIN}_arhiva_index_{config_entry.entry_id}_{year}"
        self._attr_entity_id = f"sensor.{DOMAIN}_arhiva_index_{self._cod_incasare}_{year}"
        self._attr_icon = "mdi:clipboard-text-clock"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_ARHIVA, {})
        for y in data.get("history", []):
            if y.get("year") == self._year:
                if meters := y.get("meters", []):
                    if indexes := meters[0].get("indexes", []):
                        return len(indexes[0].get("readings", []))
        return 0


class ArhivaPlatiSensor(EonEntity, SensorEntity):
    """Sensor for payment history by year."""

    def __init__(self, coordinator, config_entry, year):
        super().__init__(coordinator, config_entry)
        self._year = year
        self._attr_name = f"Arhivă plăți - {year}"
        self._attr_unique_id = f"{DOMAIN}_arhiva_plati_{config_entry.entry_id}_{year}"
        self._attr_entity_id = f"sensor.{DOMAIN}_arhiva_plati_{self._cod_incasare}_{year}"
        self._attr_icon = "mdi:cash-register"

    @property
    def state(self):
        return len(self._get_payments())

    def _get_payments(self):
        data = self.coordinator.data.get(KEY_PAYMENTS, {})
        if not data: return []
        payments = data.get("list", [])
        return [p for p in payments
                if p.get("paymentDate", "").startswith(str(self._year))]


class ArhivaComparareConsumAnualGraficSensor(EonEntity, SensorEntity):
    """Sensor for annual consumption comparison."""
    
    def __init__(self, coordinator, config_entry, year, monthly_values):
        super().__init__(coordinator, config_entry)
        self._year = year
        self._monthly_values = monthly_values
        self._attr_name = f"Arhivă consum - {year}"
        self._attr_unique_id = f"{DOMAIN}_arhiva_consum_{config_entry.entry_id}_{year}"
        self._attr_entity_id = f"sensor.{DOMAIN}_arhiva_consum_{self._cod_incasare}_{year}"
        self._attr_icon = "mdi:chart-bar"

    @property
    def state(self):
        return sum(v["consumptionValue"] for v in self._monthly_values.values())

    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes
        attrs["An"] = self._year
        for month, vals in self._monthly_values.items():
             attrs[f"Luna {month}"] = f"{vals['consumptionValue']} mc"
        return attrs


class EonInvoiceBalanceProsumSensor(EonEntity, SensorEntity):
    """Sensor for Prosumer Balance."""
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Sold Prosumator"
        self._attr_unique_id = f"{DOMAIN}_sold_prosum_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_sold_prosum_{self._cod_incasare}"
        self._attr_icon = "mdi:solar-power"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_FACTURASOLD_PROSUM)
        if not data or not isinstance(data, list): return "Nu"
        return "Da" if any(item.get("balanceValue", 0) > 0 for item in data) else "Nu"


class EonUserWalletSensor(EonEntity, SensorEntity):
    """Sensor for User Wallet."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Portofel Utilizator"
        self._attr_unique_id = f"{DOMAIN}_user_wallet_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_user_wallet_{self._cod_incasare}"
        self._attr_icon = "mdi:wallet"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_USER_WALLET)
        return data.get("balance") if data else None

    @property
    def unit_of_measurement(self):
        return "RON"
    
    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes
        if data := self.coordinator.data.get(KEY_USER_WALLET):
            attrs["Sumă nealocată"] = f"{data.get('unallocatedAmount', 0)} RON"
            attrs["Actualizat"] = data.get("updatedAt")
        return attrs


class EonReschedulingPlanSensor(EonEntity, SensorEntity):
    """Sensor for Rescheduling Plans."""
    
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Planuri eșalonare"
        self._attr_unique_id = f"{DOMAIN}_rescheduling_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_rescheduling_{self._cod_incasare}"
        self._attr_icon = "mdi:calendar-clock"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_RESCHEDULING_PLANS, [])
        return len(data) if data else 0


class EonPaymentNoticeSensor(EonEntity, SensorEntity):
    """Sensor for Payment Notices."""

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator, config_entry)
        self._attr_name = "Notificări de plată"
        self._attr_unique_id = f"{DOMAIN}_payment_notices_{config_entry.entry_id}"
        self._attr_entity_id = f"sensor.{DOMAIN}_payment_notices_{self._cod_incasare}"
        self._attr_icon = "mdi:alert-circle"

    @property
    def state(self):
        data = self.coordinator.data.get(KEY_PAYMENT_NOTICES, [])
        return len(data) if data else 0
