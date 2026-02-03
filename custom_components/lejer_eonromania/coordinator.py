import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant

from .api import EonApiClient
from .const import (
    KEY_CONTRACTS, KEY_USER_WALLET, KEY_DATEUSER, KEY_CITIREINDEX,
    KEY_CONVENTIECONSUM, KEY_COMPARAREANUALAGRAFIC, KEY_ARHIVA,
    KEY_FACTURASOLD, KEY_FACTURASOLD_PROSUM, KEY_PROSUMER_INVOICES,
    KEY_PAID_INVOICES, KEY_RESCHEDULING_PLANS, KEY_PAYMENT_NOTICES, KEY_PAYMENTS
)

_LOGGER = logging.getLogger(__name__)

class EonRomaniaCoordinator(DataUpdateCoordinator):
    """Coordinator handling all E-ON Romania data."""

    def __init__(
        self, 
        hass: HomeAssistant,
        api_client: EonApiClient,
        cod_incasare: str,
        update_interval: int,
    ):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EonRomaniaCoordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api_client = api_client
        self.cod_incasare = cod_incasare

    async def _async_update_data(self):
        """Fetch data from API using defined keys."""
        
        # 1. General Data
        contracts_data = await self.api_client.async_fetch_account_contracts_list(self.cod_incasare)
        user_wallet_data = await self.api_client.async_fetch_user_wallet()
        
        # 2. Specific Data
        dateuser_data = await self.api_client.async_fetch_dateuser_data(self.cod_incasare)
        citireindex_data = await self.api_client.async_fetch_citireindex_data(self.cod_incasare)
        conventieconsum_data = await self.api_client.async_fetch_conventieconsum_data(self.cod_incasare)
        comparareanualagrafic_data = await self.api_client.async_fetch_comparareanualagrafic_data(self.cod_incasare)
        arhiva_data = await self.api_client.async_fetch_arhiva_data(self.cod_incasare)
        
        # Invoices and Balances
        facturasold_data = await self.api_client.async_fetch_facturasold_data(self.cod_incasare)
        facturasold_prosum_data = await self.api_client.async_fetch_invoice_balance_prosum(self.cod_incasare)
        
        # Lists
        prosumer_invoices_list_data = await self.api_client.async_fetch_invoices_list_prosum(self.cod_incasare)
        paid_invoices_list_data = await self.api_client.async_fetch_invoices_list_paid(self.cod_incasare)

        # Plans and Notices
        rescheduling_plans_data = await self.api_client.async_fetch_rescheduling_plans(self.cod_incasare)
        payment_notices_data = await self.api_client.async_fetch_payment_notices(self.cod_incasare)

        # History
        payments_data = await self.api_client.async_fetch_payments_data(self.cod_incasare)

        return {
            KEY_CONTRACTS: contracts_data,
            KEY_USER_WALLET: user_wallet_data,
            KEY_DATEUSER: dateuser_data,
            KEY_CITIREINDEX: citireindex_data,
            KEY_CONVENTIECONSUM: conventieconsum_data,
            KEY_COMPARAREANUALAGRAFIC: comparareanualagrafic_data,
            KEY_ARHIVA: arhiva_data,
            KEY_FACTURASOLD: facturasold_data,
            KEY_FACTURASOLD_PROSUM: facturasold_prosum_data,
            KEY_PROSUMER_INVOICES: prosumer_invoices_list_data,
            KEY_PAID_INVOICES: paid_invoices_list_data,
            KEY_RESCHEDULING_PLANS: rescheduling_plans_data,
            KEY_PAYMENT_NOTICES: payment_notices_data,
            KEY_PAYMENTS: payments_data,
        }
