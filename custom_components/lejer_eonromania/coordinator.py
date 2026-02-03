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

    async def _async_update_data(self):
        """Fetch data from API using defined keys."""
        
        # 1. General Data - Get all contracts
        contracts_data = await self.api_client.async_fetch_account_contracts_list()
        user_wallet_data = await self.api_client.async_fetch_user_wallet()
        
        if isinstance(contracts_data, list):
            contracts_list = contracts_data
        elif isinstance(contracts_data, dict):
            contracts_list = contracts_data.get("list", [])
        else:
            contracts_list = []
        
        data_per_contract = {}
        
        # 2. Iterate over each contract found (Flattening sub-contracts)
        processed_contracts = []
        for contract in contracts_list:
            # Check for subcontracts
            if sub_contracts := contract.get("subContracts"):
                # If subcontracts exist, this is likely a Collective/DUO contract.
                # Processing the parent usually results in API errors (3230 Collective Contract not permitted).
                # We should ONLY process the subcontracts.
                for sub in sub_contracts:
                     # Subcontracts usually have direct structure
                     processed_contracts.append(sub)
                
                # Do NOT append the parent contract if subcontracts were found
                continue
                     
            # Include the contract if it has no subcontracts (Standard contract)
            processed_contracts.append(contract)
            
        data_per_contract = {}

        for contract in processed_contracts:
            cod_incasare = None
            if "contractDetails" in contract:
                cod_incasare = contract["contractDetails"].get("accountContract")
            else:
                # Fallback for old structure or direct object from subcontracts
                cod_incasare = contract.get("contractId") or contract.get("accountContract")

            if not cod_incasare:
                 continue
                 
            # Skip if already processed (deduplication)
            if cod_incasare in data_per_contract:
                continue
                 
            # Specific Data per Contract
            dateuser_data = await self.api_client.async_fetch_dateuser_data(cod_incasare)
            citireindex_data = await self.api_client.async_fetch_citireindex_data(cod_incasare)
            conventieconsum_data = await self.api_client.async_fetch_conventieconsum_data(cod_incasare)
            comparareanualagrafic_data = await self.api_client.async_fetch_comparareanualagrafic_data(cod_incasare)
            arhiva_data = await self.api_client.async_fetch_arhiva_data(cod_incasare)
            
            # Invoices and Balances
            facturasold_data = await self.api_client.async_fetch_facturasold_data(cod_incasare)
            facturasold_prosum_data = await self.api_client.async_fetch_invoice_balance_prosum(cod_incasare)
            
            # Lists
            prosumer_invoices_list_data = await self.api_client.async_fetch_invoices_list_prosum(cod_incasare)
            paid_invoices_list_data = await self.api_client.async_fetch_invoices_list_paid(cod_incasare)

            # Plans and Notices
            rescheduling_plans_data = await self.api_client.async_fetch_rescheduling_plans(cod_incasare)
            payment_notices_data = await self.api_client.async_fetch_payment_notices(cod_incasare)

            # History
            payments_data = await self.api_client.async_fetch_payments_data(cod_incasare)
            
            data_per_contract[cod_incasare] = {
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

        return {
            KEY_CONTRACTS: contracts_list,
            KEY_USER_WALLET: user_wallet_data,
            "data_per_contract": data_per_contract
        }
