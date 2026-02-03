import logging
from aiohttp import ClientSession, ClientTimeout
from .const import HEADERS_POST, URLS

_LOGGER = logging.getLogger(__name__)

class EonApiClient:
    """Clasă pentru comunicarea cu API-ul EON România."""

    def __init__(self, session: ClientSession, username: str, password: str):
        """Inițializează clientul API cu o sesiune de tip ClientSession."""
        self._session = session
        self._username = username
        self._password = password
        self._token = None

    async def async_login(self) -> bool:
        """Obține un token nou de autentificare."""
        payload = {
            "username": self._username,
            "password": self._password,
            "rememberMe": False
        }

        try:
            # Folosim un timeout scurt pentru login
            timeout = ClientTimeout(total=20)
            async with self._session.post(URLS["login"], json=payload, headers=HEADERS_POST, timeout=timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._token = data.get("accessToken")
                    _LOGGER.debug("Token obținut cu succes.")
                    return True
                else:
                    text = await resp.text()
                    _LOGGER.error(
                        "Eroare la login. Status=%s, Răspuns=%s",
                        resp.status,
                        text
                    )
                    self._token = None
                    return False
        except Exception as e:
            _LOGGER.error("Eroare la conectarea cu API-ul pentru autentificare: %s", e)
            self._token = None
            return False

    async def async_fetch_dateuser_data(self, cod_incasare: str):
        """Obține datele utilizatorului (contract)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["dateuser"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea datelor utilizator."
        )

    async def async_fetch_citireindex_data(self, cod_incasare: str):
        """Obține datele despre indexul curent."""
        return await self._request_with_token(
            method="GET",
            url=URLS["citireindex"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea indexului curent."
        )

    async def async_fetch_conventieconsum_data(self, cod_incasare: str):
        """Obține datele despre convenție consum."""
        return await self._request_with_token(
            method="GET",
            url=URLS["conventieconsum"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea convenție consum."
        )

    async def async_fetch_comparareanualagrafic_data(self, cod_incasare: str):
        """Obține datele despre comparare anuala grafic."""
        return await self._request_with_token(
            method="GET",
            url=URLS["comparareanualagrafic"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea comparare anuala grafic."
        )

    async def async_fetch_arhiva_data(self, cod_incasare: str):
        """Obține date istorice (arhiva)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["arhiva"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea datelor din arhivă."
        )

    async def async_fetch_facturasold_data(self, cod_incasare: str):
        """Obține datele despre soldul facturilor."""
        # Se folosește URL-ul invoices_list_unpaid (echivalent cu facturasold dar cu subcontracts=true)
        # sau URLS["facturasold"] care a fost updatat.
        return await self._request_with_token(
            method="GET",
            url=URLS["facturasold"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea soldului facturilor."
        )

    # --- Endpoints Noi ---

    async def async_fetch_account_contracts_list(self, cod_incasare: str):
        """
        Obține lista contractelor asociate contului (POST). 
        Folosind 'collectiveContract' ca parametrul cod_incasare.
        """
        payload = {"collectiveContract": cod_incasare, "limit": -1}
        return await self._request_with_token(
            method="POST",
            url=URLS["account_contracts_list"],
            json_data=payload,
            on_error="Eroare la obținerea listei de contracte."
        )

    async def async_fetch_current_date(self):
        """Obține data curentă de la API (check de sistem)."""
        # Acest endpoint pare să nu necesite autentificare în curl, dar verificăm.
        # Curl-ul are header Ocp-Apim dar nu are Authorization Bearer.
        # Totuși, metoda generică _request_with_token adaugă Bearer. 
        # API-ul probabil acceptă și cu Bearer.
        return await self._request_with_token(
            method="GET",
            url=URLS["current_date"],
            on_error="Eroare la obținerea datei curente."
        )

    async def async_fetch_invoice_balance(self, cod_incasare: str):
        """Obține balanța totală facturi (cu subcontracts)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["invoice_balance"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea balanței facturilor."
        )

    async def async_fetch_invoice_balance_prosum(self, cod_incasare: str):
        """Obține balanța prosumator."""
        return await self._request_with_token(
            method="GET",
            url=URLS["invoice_balance_prosum"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea balanței prosumator."
        )

    async def async_fetch_invoices_list_paid(self, cod_incasare: str):
        """Obține lista facturilor plătite (prima pagină)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["invoices_list_paid"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea listei de facturi plătite."
        )

    async def async_fetch_rescheduling_plans(self, cod_incasare: str):
        """Obține planurile de reeșalonare."""
        return await self._request_with_token(
            method="GET",
            url=URLS["rescheduling_plans"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea planurilor de reeșalonare."
        )

    async def async_fetch_invoices_list_prosum(self, cod_incasare: str):
        """Obține lista facturilor prosumator (prima pagină)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["invoices_list_prosum"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea listei de facturi prosumator."
        )
    
    async def async_fetch_payment_notices(self, cod_incasare: str):
        """Obține notificările de plată (unpaid)."""
        return await self._request_with_token(
            method="GET",
            url=URLS["payment_notices"].format(cod_incasare=cod_incasare),
            on_error="Eroare la obținerea notificărilor de plată."
        )

    async def async_fetch_user_wallet(self):
        """Obține portofelul utilizatorului."""
        return await self._request_with_token(
            method="GET",
            url=URLS["user_wallet"],
            on_error="Eroare la obținerea portofelului utilizator."
        )

    # --- Gestionare Plăți (paginare manuală păstrată) ---

    async def async_fetch_payments_data(self, cod_incasare: str):
        """
        Obține toate înregistrările de plăți (paginate) pentru un cont dat.
        Returnează o listă unică, cumulând datele de pe toate paginile.
        """
        if not await self._ensure_token():
            return None

        results = []
        page = 1
        while True:
            url = (
                f"https://api2.eon.ro/invoices/v1/payments/payment-list"
                f"?accountContract={cod_incasare}&page={page}"
            )
            
            # Request manual pentru a gestiona paginarea specifică
            data, status = await self._do_request("GET", url)
            
            if status == 401:
                 # Re-try logic simplificat (deja handled in _request_with_token dar aici e bucla manuala)
                 # Pentru consistență, folosim logica de token refresh
                 if await self.async_login():
                     data, status = await self._do_request("GET", url)
                 else:
                     break
            
            if status != 200 or not data:
                break

            chunk = data.get("list", [])
            results.extend(chunk)

            has_next = data.get("hasNext", False)
            if not has_next:
                break
            page += 1

        return results

    async def async_trimite_index(self, account_contract: str, ablbelnr: str, index_value: int):
        """Trimite indexul către API-ul E-ON."""
        payload = {
            "accountContract": account_contract,
            "channel": "WEBSITE",
            "indexes": [{"ablbelnr": ablbelnr, "indexValue": index_value}],
        }
        return await self._request_with_token(
            method="POST",
            url=URLS["trimite_index"],
            json_data=payload,
            on_error="Eroare la trimiterea indexului."
        )

    # --- Helpers ---

    async def _ensure_token(self) -> bool:
        """Asigură că avem un token valid, inițiind login dacă e necesar."""
        if self._token is None:
            return await self.async_login()
        return True

    async def _request_with_token(self, method: str, url: str, on_error: str, json_data: dict = None):
        """
        Metodă auxiliară care face un request folosind token-ul.
        Dacă token-ul nu există, face login. Dacă primim 401, reîncearcă o dată.
        """
        if not await self._ensure_token():
            return None

        # Prima încercare
        resp_data, status = await self._do_request(method, url, json_data)
        if status != 401:
            return resp_data

        # Dacă e 401, înseamnă invalid_token; încercăm re-login și re-request
        _LOGGER.debug("%s (Status 401) -> Re-autentificare...", on_error)
        self._token = None
        if not await self.async_login():
            return None

        # Token obținut, refacem cererea
        resp_data, status = await self._do_request(method, url, json_data)
        if status == 401:
            _LOGGER.error("%s (Status 401 persistent) -> Abandon.", on_error)
            return None

        return resp_data

    async def _do_request(self, method: str, url: str, json_data: dict = None):
        """
        Efectuează o cerere (GET/POST) cu token-ul curent (dacă există).
        Returnează tuple (resp_data, status).
        """
        headers = {**HEADERS_POST}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        try:
            async with self._session.request(method, url, headers=headers, json=json_data) as resp:
                if resp.status == 200:
                    try:
                        return (await resp.json()), resp.status
                    except Exception:
                        # Unele endpoint-uri pot returna text simplu sau gol
                        return (await resp.text()), resp.status
                else:
                    text = await resp.text()
                    if resp.status != 401:
                         _LOGGER.error("%s %s eșuat. Status=%s, Răspuns=%s", method, url, resp.status, text)
                    return None, resp.status
        except Exception as e:
            _LOGGER.error("Eroare request %s %s: %s", method, url, e)
            return None, 0
