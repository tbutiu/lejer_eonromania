import logging
from datetime import timedelta
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant
from .api import EonApiClient

_LOGGER = logging.getLogger(__name__)

class EonRomaniaCoordinator(DataUpdateCoordinator):
    """Coordinator care se ocupă de toate datele E-ON România."""

    def __init__(
        self, 
        hass: HomeAssistant,
        api_client: EonApiClient,
        cod_incasare: str,
        update_interval: int,
    ):
        """Inițializează coordinatorul cu parametrii necesari."""
        super().__init__(
            hass,
            _LOGGER,
            name="EonRomaniaCoordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api_client = api_client
        self.cod_incasare = cod_incasare

    async def _async_update_data(self):
        """Obține date de la API."""
        # Apelam metodele din api_client pentru a popula toate datele necesare

        # 1. Date generale (client, contracte)
        contracts_data = await self.api_client.async_fetch_account_contracts_list(self.cod_incasare)
        user_wallet_data = await self.api_client.async_fetch_user_wallet()
        
        # 2. Date specifice codului de incasare
        dateuser_data = await self.api_client.async_fetch_dateuser_data(self.cod_incasare)
        citireindex_data = await self.api_client.async_fetch_citireindex_data(self.cod_incasare)
        conventieconsum_data = await self.api_client.async_fetch_conventieconsum_data(self.cod_incasare)
        comparareanualagrafic_data = await self.api_client.async_fetch_comparareanualagrafic_data(self.cod_incasare)
        arhiva_data = await self.api_client.async_fetch_arhiva_data(self.cod_incasare)
        
        # Facturi si solduri
        # Folosim facturasold pt sold normal
        facturasold_data = await self.api_client.async_fetch_facturasold_data(self.cod_incasare)
        # Folosim invoice_balance_prosum pt sold prosumator
        facturasold_prosum_data = await self.api_client.async_fetch_invoice_balance_prosum(self.cod_incasare)
        
        # Liste de facturi (pentru interfață sau istoric)
        # facturasold conține deja lista facturilor neplătite standard (cf. endpoint-ului nou)
        # prosumer list:
        prosumer_invoices_list_data = await self.api_client.async_fetch_invoices_list_prosum(self.cod_incasare)
        paid_invoices_list_data = await self.api_client.async_fetch_invoices_list_paid(self.cod_incasare)

        # Planuri esalonare si notificari plata
        rescheduling_plans_data = await self.api_client.async_fetch_rescheduling_plans(self.cod_incasare)
        payment_notices_data = await self.api_client.async_fetch_payment_notices(self.cod_incasare)

        # Plati (istoric)
        payments_data = await self.api_client.async_fetch_payments_data(self.cod_incasare)

        return {
            "contracts": contracts_data,
            "user_wallet": user_wallet_data,
            "dateuser": dateuser_data,
            "citireindex": citireindex_data,
            "conventieconsum": conventieconsum_data,
            "comparareanualagrafic": comparareanualagrafic_data,
            "arhiva": arhiva_data,
            "facturasold": facturasold_data,
            "facturasold_prosum": facturasold_prosum_data,
            "prosumer_invoices_list": prosumer_invoices_list_data,
            "paid_invoices_list": paid_invoices_list_data,
            "rescheduling_plans": rescheduling_plans_data,
            "payment_notices": payment_notices_data,
            "payments": payments_data,
        }
