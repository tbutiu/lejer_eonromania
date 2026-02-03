"""Constants for the E-ON Romania integration."""
from typing import Final

DOMAIN: Final = "lejer_eonromania"

# Default Config
DEFAULT_USER: Final = "username"
DEFAULT_PASS: Final = "password"
DEFAULT_UPDATE_INTERVAL: Final = 3600

# API URLs
BASE_URL: Final = "https://api2.eon.ro"
URLS: Final = {
    "login": f"{BASE_URL}/users/v1/userauth/login",
    "dateuser": f"{BASE_URL}/partners/v2/account-contracts/{{cod_incasare}}",
    "citireindex": f"{BASE_URL}/meterreadings/v1/meter-reading/{{cod_incasare}}/index",
    "conventieconsum": f"{BASE_URL}/meterreadings/v1/consumption-convention/{{cod_incasare}}",
    "comparareanualagrafic": f"{BASE_URL}/invoices/v1/invoices/graphic-consumption/{{cod_incasare}}",
    "arhiva": f"{BASE_URL}/meterreadings/v1/meter-reading/{{cod_incasare}}/history",
    "download_invoice": f"{BASE_URL}/invoices/v1/invoices/download/{{invoice_number}}?accountContract={{cod_incasare}}",
    "facturasold": f"{BASE_URL}/invoices/v1/invoices/list?accountContract={{cod_incasare}}&status=unpaid&includeSubcontracts=true",
    "trimite_index": f"{BASE_URL}/meterreadings/v1/meter-reading/index",
    "account_contracts_list": f"{BASE_URL}/partners/v2/account-contracts/list",
    "current_date": f"{BASE_URL}/utils/v2/date/current?timeZone=Europe/Bucharest&pattern=yyyy-MM-dd",
    "invoice_balance": f"{BASE_URL}/invoices/v1/invoices/invoice-balance?accountContract={{cod_incasare}}&includeSubcontracts=true",
    "invoice_balance_prosum": f"{BASE_URL}/invoices/v1/invoices/invoice-balance-prosum?accountContract={{cod_incasare}}&includeSubcontracts=true",
    "invoices_list_paid": f"{BASE_URL}/invoices/v1/invoices/list-paid?accountContract={{cod_incasare}}&status=paid&includeSubcontracts=true&page=1",
    "invoices_list_unpaid": f"{BASE_URL}/invoices/v1/invoices/list?accountContract={{cod_incasare}}&status=unpaid&includeSubcontracts=true",
    "rescheduling_plans": f"{BASE_URL}/invoices/v1/rescheduling-plans?accountContract={{cod_incasare}}&includeSubcontracts=true",
    "invoices_list_prosum": f"{BASE_URL}/invoices/v1/invoices/list-prosum?accountContract={{cod_incasare}}&includeSubcontracts=true&page=1",
    "payment_notices": f"{BASE_URL}/invoices/v1/payment-notices?accountContract={{cod_incasare}}&status=unpaid",
    "user_wallet": f"{BASE_URL}/users/v1/users/user-wallet",
    "payments_list": f"{BASE_URL}/invoices/v1/payments/payment-list?accountContract={{cod_incasare}}&page={{page}}",
}

# API Headers
HEADERS_POST: Final = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": "674e9032df9d456fa371e17a4097a5b8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Origin": "https://www.eon.ro",
    "Referer": "https://www.eon.ro/myline/facturile-mele",
}

# Data Keys
KEY_CONTRACTS: Final = "contracts"
KEY_USER_WALLET: Final = "user_wallet"
KEY_DATEUSER: Final = "dateuser"
KEY_CITIREINDEX: Final = "citireindex"
KEY_CONVENTIECONSUM: Final = "conventieconsum"
KEY_COMPARAREANUALAGRAFIC: Final = "comparareanualagrafic"
KEY_ARHIVA: Final = "arhiva"
KEY_FACTURASOLD: Final = "facturasold"
KEY_FACTURASOLD_PROSUM: Final = "facturasold_prosum"
KEY_PROSUMER_INVOICES: Final = "prosumer_invoices_list"
KEY_PAID_INVOICES: Final = "paid_invoices_list"
KEY_RESCHEDULING_PLANS: Final = "rescheduling_plans"
KEY_PAYMENT_NOTICES: Final = "payment_notices"
KEY_PAYMENTS: Final = "payments"

# Attribution
ATTRIBUTION: Final = "Date furnizate de E-ON România"

# Month Mapping
MONTHS_RO: Final = {
    "January": "ianuarie",
    "February": "februarie",
    "March": "martie",
    "April": "aprilie",
    "May": "mai",
    "June": "iunie",
    "July": "iulie",
    "August": "august",
    "September": "septembrie",
    "October": "octombrie",
    "November": "noiembrie",
    "December": "decembrie",
}
