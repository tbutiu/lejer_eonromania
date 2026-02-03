import logging
from typing import Optional, Dict, List, Any
from aiohttp import ClientSession, ClientTimeout

from .const import (
    URLS, HEADERS_POST, 
    KEY_CITIREINDEX, KEY_CONVENTIECONSUM, KEY_COMPARAREANUALAGRAFIC, 
    KEY_ARHIVA, KEY_FACTURASOLD, KEY_FACTURASOLD_PROSUM, 
    KEY_PROSUMER_INVOICES, KEY_PAID_INVOICES, KEY_RESCHEDULING_PLANS,
    KEY_PAYMENT_NOTICES, KEY_PAYMENTS, KEY_DATEUSER
)

_LOGGER = logging.getLogger(__name__)

class EonApiClient:
    """Class for communicating with the E-ON Romania API."""

    def __init__(self, session: ClientSession, username: str, password: str):
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._token: Optional[str] = None

    async def async_login(self) -> bool:
        """Obtain a new authentication token."""
        payload = {
            "username": self._username,
            "password": self._password,
            "rememberMe": False
        }

        try:
            timeout = ClientTimeout(total=20)
            async with self._session.post(
                URLS["login"], json=payload, headers=HEADERS_POST, timeout=timeout
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("accessToken")
                    _LOGGER.debug("Token obtained successfully.")
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.error("Login error. Status=%s, Response=%s", resp.status, text)
                    self._token = None
                    return False
        except Exception as e:
            _LOGGER.error("Error connecting to auth API: %s", e)
            self._token = None
            return False

    async def async_fetch_dateuser_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch user contract data."""
        return await self._request_with_token(
            "GET",
            URLS["dateuser"].format(cod_incasare=cod_incasare),
            "Error fetching user data."
        )

    async def async_fetch_citireindex_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch current index data."""
        return await self._request_with_token(
            "GET",
            URLS["citireindex"].format(cod_incasare=cod_incasare),
            "Error fetching current index."
        )

    async def async_fetch_conventieconsum_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch consumption convention data."""
        return await self._request_with_token(
            "GET",
            URLS["conventieconsum"].format(cod_incasare=cod_incasare),
            "Error fetching consumption convention."
        )

    async def async_fetch_comparareanualagrafic_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch annual graphic comparison data."""
        return await self._request_with_token(
            "GET",
            URLS["comparareanualagrafic"].format(cod_incasare=cod_incasare),
            "Error fetching annual graphic comparison."
        )

    async def async_fetch_arhiva_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch archive data."""
        return await self._request_with_token(
            "GET",
            URLS["arhiva"].format(cod_incasare=cod_incasare),
            "Error fetching archive data."
        )

    async def async_fetch_facturasold_data(self, cod_incasare: str) -> Optional[dict]:
        """Fetch invoice balance data."""
        return await self._request_with_token(
            "GET",
            URLS["facturasold"].format(cod_incasare=cod_incasare),
            "Error fetching invoice balance."
        )

    async def async_fetch_account_contracts_list(self) -> Optional[dict]:
        """Fetch account contracts list using list-with-subcontracts."""
        return await self._request_with_token(
            "GET",
            URLS["account_contracts_list"],
            "Error fetching account contracts list."
        )

    async def async_fetch_unread_messages(self) -> Optional[dict]:
        """Fetch count of unread messages."""
        return await self._request_with_token(
            "GET",
            URLS["unread_messages"],
            "Error fetching unread messages count."
        )

    async def async_fetch_current_date(self) -> Optional[dict]:
        """Fetch current date from API."""
        return await self._request_with_token(
            "GET",
            URLS["current_date"],
            "Error fetching current date."
        )

    async def async_fetch_invoice_balance(self, cod_incasare: str) -> Optional[dict]:
        """Fetch invoice balance with subcontracts."""
        return await self._request_with_token(
            "GET",
            URLS["invoice_balance"].format(cod_incasare=cod_incasare),
            "Error fetching invoice balance (with subcontracts)."
        )

    async def async_fetch_invoice_balance_prosum(self, cod_incasare: str) -> Optional[dict]:
        """Fetch prosumer invoice balance."""
        return await self._request_with_token(
            "GET",
            URLS["invoice_balance_prosum"].format(cod_incasare=cod_incasare),
            "Error fetching prosumer balance."
        )

    async def async_fetch_invoices_list_paid(self, cod_incasare: str) -> Optional[dict]:
        """Fetch paid invoices list (page 1)."""
        return await self._request_with_token(
            "GET",
            URLS["invoices_list_paid"].format(cod_incasare=cod_incasare),
            "Error fetching paid invoices."
        )

    async def async_fetch_rescheduling_plans(self, cod_incasare: str) -> Optional[dict]:
        """Fetch rescheduling plans."""
        return await self._request_with_token(
            "GET",
            URLS["rescheduling_plans"].format(cod_incasare=cod_incasare),
            "Error fetching rescheduling plans."
        )

    async def async_fetch_invoices_list_prosum(self, cod_incasare: str) -> Optional[dict]:
        """Fetch prosumer invoices list."""
        return await self._request_with_token(
            "GET",
            URLS["invoices_list_prosum"].format(cod_incasare=cod_incasare),
            "Error fetching prosumer invoices."
        )
    
    async def async_fetch_payment_notices(self, cod_incasare: str) -> Optional[dict]:
        """Fetch payment notices."""
        return await self._request_with_token(
            "GET",
            URLS["payment_notices"].format(cod_incasare=cod_incasare),
            "Error fetching payment notices."
        )

    async def async_fetch_user_wallet(self) -> Optional[dict]:
        """Fetch user wallet data."""
        return await self._request_with_token(
            "GET",
            URLS["user_wallet"],
            "Error fetching user wallet."
        )

    async def async_fetch_payments_data(self, cod_incasare: str) -> List[dict]:
        """Fetch all payment records with manual pagination."""
        if not await self._ensure_token():
            return []

        results = []
        page = 1
        while True:
            url = URLS["payments_list"].format(cod_incasare=cod_incasare, page=page)
            
            data, status = await self._do_request("GET", url)
            
            if status == 401:
                 # Retry logic
                 if await self.async_login():
                     data, status = await self._do_request("GET", url)
                 else:
                     break
            
            if status != 200 or not data:
                break

            chunk = data.get("list", [])
            results.extend(chunk)

            if not data.get("hasNext", False):
                break
            page += 1

        return results

    async def async_trimite_index(self, account_contract: str, ablbelnr: str, index_value: int) -> Optional[dict]:
        """Send meter reading to API."""
        payload = {
            "accountContract": account_contract,
            "channel": "WEBSITE",
            "indexes": [{"ablbelnr": ablbelnr, "indexValue": index_value}],
        }
        return await self._request_with_token(
            "POST",
            URLS["trimite_index"],
            "Error sending index.",
            json_data=payload
        )

    async def async_get_invoice_pdf(self, cod_incasare: str, invoice_number: str) -> Optional[bytes]:
        """Download invoice PDF."""
        url = URLS["download_invoice"].format(cod_incasare=cod_incasare, invoice_number=invoice_number)
        
        if not await self._ensure_token():
            return None

        headers = {**HEADERS_POST}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.read()
                else:
                    _LOGGER.error("Error downloading PDF. Status=%s", resp.status)
                    return None
        except Exception as e:
            _LOGGER.error("Error downloading PDF: %s", e)
            return None

    async def _ensure_token(self) -> bool:
        """Ensure a valid token exists."""
        if self._token is None:
            return await self.async_login()
        return True

    async def _request_with_token(self, method: str, url: str, on_error: str, json_data: dict = None) -> Optional[Any]:
        """Execute request with automatic token refresh."""
        if not await self._ensure_token():
            return None

        # First attempt
        resp_data, status = await self._do_request(method, url, json_data)
        if status != 401:
            return resp_data

        # Retry logic for 401
        _LOGGER.debug("%s (Status 401) -> Refreshing token...", on_error)
        self._token = None
        if not await self.async_login():
            return None

        resp_data, status = await self._do_request(method, url, json_data)
        if status == 401:
            _LOGGER.error("%s (Status 401 persistent) -> Abort.", on_error)
            return None

        return resp_data

    async def _do_request(self, method: str, url: str, json_data: dict = None):
        """Perform the actual HTTP request."""
        headers = {**HEADERS_POST}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.request(method, url, headers=headers, json=json_data) as resp:
                if resp.status == 200:
                    try:
                        return (await resp.json()), resp.status
                    except Exception:
                        return (await resp.text()), resp.status
                else:
                    text = await resp.text()
                    if resp.status != 401:
                         _LOGGER.error("%s %s failed. Status=%s, Response=%s", method, url, resp.status, text)
                    return None, resp.status
        except Exception as e:
            _LOGGER.error("Request error %s %s: %s", method, url, e)
            return None, 0
