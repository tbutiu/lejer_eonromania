"""Constante pentru integrarea EON România."""

DOMAIN = "lejer_eonromania"

# Config default
DEFAULT_USER = "username"
DEFAULT_PASS = "password"
DEFAULT_UPDATE_INTERVAL = 3600  # Interval de actualizare în secunde (1 oră)

# Headere pentru requesturi HTTP
# Headere pentru requesturi HTTP
HEADERS_POST = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Key": "674e9032df9d456fa371e17a4097a5b8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"8\", \"Chromium\";v=\"144\", \"Google Chrome\";v=\"144\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "Origin": "https://www.eon.ro",
    "Referer": "https://www.eon.ro/myline/facturile-mele",
}

# URL-uri pentru API-ul E-ON
URLS = {
    "login": "https://api2.eon.ro/users/v1/userauth/login",
    "dateuser": "https://api2.eon.ro/partners/v2/account-contracts/{cod_incasare}",
    "citireindex": "https://api2.eon.ro/meterreadings/v1/meter-reading/{cod_incasare}/index",
    "conventieconsum": "https://api2.eon.ro/meterreadings/v1/consumption-convention/{cod_incasare}",
    "comparareanualagrafic": "https://api2.eon.ro/invoices/v1/invoices/graphic-consumption/{cod_incasare}",
    "arhiva": "https://api2.eon.ro/meterreadings/v1/meter-reading/{cod_incasare}/history",
    "facturasold": "https://api2.eon.ro/invoices/v1/invoices/list?accountContract={cod_incasare}&status=unpaid&includeSubcontracts=true",
    "trimite_index": "https://api2.eon.ro/meterreadings/v1/meter-reading/index",
    
    # Endpoints noi
    "account_contracts_list": "https://api2.eon.ro/partners/v2/account-contracts/list",
    "current_date": "https://api2.eon.ro/utils/v2/date/current?timeZone=Europe/Bucharest&pattern=yyyy-MM-dd",
    "invoice_balance": "https://api2.eon.ro/invoices/v1/invoices/invoice-balance?accountContract={cod_incasare}&includeSubcontracts=true",
    "invoice_balance_prosum": "https://api2.eon.ro/invoices/v1/invoices/invoice-balance-prosum?accountContract={cod_incasare}&includeSubcontracts=true",
    "invoices_list_paid": "https://api2.eon.ro/invoices/v1/invoices/list-paid?accountContract={cod_incasare}&status=paid&includeSubcontracts=true&page=1",
    "invoices_list_unpaid": "https://api2.eon.ro/invoices/v1/invoices/list?accountContract={cod_incasare}&status=unpaid&includeSubcontracts=true",
    "rescheduling_plans": "https://api2.eon.ro/invoices/v1/rescheduling-plans?accountContract={cod_incasare}&includeSubcontracts=true",
    "invoices_list_prosum": "https://api2.eon.ro/invoices/v1/invoices/list-prosum?accountContract={cod_incasare}&includeSubcontracts=true&page=1",
    "payment_notices": "https://api2.eon.ro/invoices/v1/payment-notices?accountContract={cod_incasare}&status=unpaid",
    "user_wallet": "https://api2.eon.ro/users/v1/users/user-wallet"
}

# Atribuție
ATTRIBUTION = "Date furnizate de E-ON România"
