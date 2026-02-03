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

"""The E-ON Romania integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL
from .api import EonApiClient
from .coordinator import EonRomaniaCoordinator
from . import sensor, button


CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Configurează integrarea globală EON România, dacă e necesar."""
    _LOGGER.debug("Inițializarea globală a integrării %s", DOMAIN)
    return True

PLATFORMS = ["sensor", "button", "binary_sensor", "number"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Configurează integrarea pentru o anumită intrare (config entry)."""
    _LOGGER.debug("Configurarea intrării pentru %s", DOMAIN)
    hass.data.setdefault(DOMAIN, {})

    # Creăm clientul API
    session = async_get_clientsession(hass)
    username = entry.data["username"]
    password = entry.data["password"]
    cod_incasare = entry.data["cod_incasare"]
    update_interval = entry.options.get("update_interval", DEFAULT_UPDATE_INTERVAL)

    api_client = EonApiClient(session, username, password)

    # Creăm un singur DataUpdateCoordinator pentru toate datele
    coordinator = EonRomaniaCoordinator(
        hass,
        api_client=api_client,
        cod_incasare=cod_incasare,
        update_interval=update_interval,
    )

    # Facem prima actualizare
    await coordinator.async_config_entry_first_refresh()

    # Salvăm coordinatorul în hass.data
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api_client": api_client,
    }

    # Încărcăm platformele
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Configurare servicii
    await async_setup_services(hass, entry)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Descărcarea intrării din config_entries."""
    _LOGGER.debug("Descărcarea intrării pentru %s", DOMAIN)
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

    await async_setup_entry(hass, entry)

async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry):
    """Set up custom services."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    
    async def get_last_invoice(call):
        """Download the last invoice."""
        _LOGGER.debug("Service download_last_invoice called.")
        
        # 1. Identify last invoice from paid list (usually most relevant)
        invoices = coordinator.data.get("paid_invoices_list", [])
        if not invoices:
            _LOGGER.warning("No paid invoices found.")
            return

        # Sort by date descending if needed, but API usually returns recent first
        # Assuming first item is latest
        last_invoice = invoices[0]
        invoice_number = last_invoice.get("invoiceNumber")
        
        if not invoice_number:
            _LOGGER.error("Could not determine invoice number.")
            return

        # 2. Download PDF
        pdf_content = await coordinator.api_client.async_get_invoice_pdf(
            cod_incasare=coordinator.cod_incasare,
            invoice_number=invoice_number
        )

        if not pdf_content:
            _LOGGER.error("Failed to download PDF content.")
            return

        # 3. Save to disk (in /config/www/invoices or similar)
        # We'll save to <config_dir>/www/eon_invoices/
        output_dir = hass.config.path("www", "eon_invoices")
        import os
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        filename = f"{output_dir}/factura_{invoice_number}.pdf"
        
        def save_file():
            with open(filename, "wb") as f:
                f.write(pdf_content)
        
        await hass.async_add_executor_job(save_file)
        _LOGGER.info("Invoice saved to %s", filename)
        
        # Notification (optional)
        hass.components.persistent_notification.create(
            f"Factura {invoice_number} a fost descărcată în {filename}",
            title="E-ON Factura Descărcată"
        )

    hass.services.async_register(DOMAIN, "download_last_invoice", get_last_invoice)
