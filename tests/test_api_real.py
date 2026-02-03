import pytest
import os
import sys
# Add project root to sys.path to allow imports from custom_components
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# MOCK homeassistant to avoid ModuleNotFoundError when importing custom_components
# MOCK homeassistant to avoid ModuleNotFoundError when importing custom_components
from unittest.mock import MagicMock
import sys

def mock_module(name, pkg=False):
    m = MagicMock()
    if pkg:
        m.__path__ = []
    sys.modules[name] = m
    return m

mock_module("homeassistant", pkg=True)
mock_module("homeassistant.config_entries")
mock_module("homeassistant.core")
mock_module("homeassistant.helpers", pkg=True)
mock_module("homeassistant.helpers.aiohttp_client")
mock_module("homeassistant.helpers.config_validation")
mock_module("homeassistant.helpers.update_coordinator")
mock_module("homeassistant.helpers.entity")
mock_module("homeassistant.helpers.entity_platform")
mock_module("homeassistant.helpers.typing")
mock_module("homeassistant.helpers.discovery")
mock_module("homeassistant.helpers.service")
mock_module("homeassistant.helpers.device_registry")
mock_module("homeassistant.helpers.entity_registry")
mock_module("homeassistant.helpers.area_registry")
mock_module("homeassistant.helpers.issue_registry")
mock_module("homeassistant.const")
mock_module("homeassistant.exceptions")
mock_module("homeassistant.components", pkg=True)
mock_module("homeassistant.components.sensor")
mock_module("homeassistant.components.binary_sensor")
mock_module("homeassistant.components.button")
mock_module("homeassistant.util", pkg=True)


mock_module("homeassistant.components.button")
mock_module("homeassistant.util", pkg=True)

# Fix inheritance: Assign a real class to base classes
class MockClass:
    def __init__(self, *args, **kwargs):
        pass

sys.modules["homeassistant.helpers.update_coordinator"].DataUpdateCoordinator = MockClass
sys.modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = MockClass
sys.modules["homeassistant.components.sensor"].SensorEntity = MockClass
sys.modules["homeassistant.components.binary_sensor"].BinarySensorEntity = MockClass
sys.modules["homeassistant.components.button"].ButtonEntity = MockClass
sys.modules["homeassistant.helpers.entity"].Entity = MockClass

import logging
import asyncio
import json
import aiohttp
from dotenv import load_dotenv

from custom_components.lejer_eonromania.api import EonApiClient
from custom_components.lejer_eonromania.const import (
    KEY_CONTRACTS, KEY_DATEUSER, KEY_FACTURASOLD
)

# Load environment variables
load_dotenv()

USERNAME = os.getenv("EON_USERNAME")
PASSWORD = os.getenv("EON_PASSWORD")
DELAY_SECONDS = int(os.getenv("EON_API_DELAY", 5))
COD_INCASARE = os.getenv("EON_COD_INCASARE")

# Configure logging to see output
logging.basicConfig(level=logging.DEBUG)
_LOGGER = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_real_login_and_fetch():
    """Test real login and data fetching."""
    
    if not USERNAME or not PASSWORD:
        pytest.skip("EON_USERNAME or EON_PASSWORD not set in .env")

    _LOGGER.info("Starting real API test for user: %s", USERNAME)

    async with aiohttp.ClientSession() as session:
        # Create a subclass to capture login response data
        class DebugApiClient(EonApiClient):
            def __init__(self, session, username, password):
                super().__init__(session, username, password)
                self.login_data = None

            async def async_login(self) -> bool:
                """Obtain a new authentication token and capture data."""
                payload = {
                    "username": self._username,
                    "password": self._password,
                    "rememberMe": False
                }
                try:
                    from aiohttp import ClientTimeout
                    timeout = ClientTimeout(total=20)
                    # We need to access the URL from the base class or const
                    # Since URLS is imported in api.py, we can access it via const import in test
                    from custom_components.lejer_eonromania.const import URLS, HEADERS_POST
                    
                    async with self._session.post(
                        URLS["login"], json=payload, headers=HEADERS_POST, timeout=timeout
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            self.login_data = data # CAPTURE DATA
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

        api = DebugApiClient(session, USERNAME, PASSWORD)

        # 1. Test Login
        login_success = await api.async_login()
        assert login_success is True, "Login failed"
        assert api._token is not None, "Token is missing"
        _LOGGER.info("Login successful!")
        
        # 2. DISCOVERY FROM LOGIN DATA
        _LOGGER.info("Inspecting Login Response for Contracts...")
        login_data = api.login_data
        _LOGGER.debug("Login Data Keys: %s", login_data.keys() if login_data else "None")
        
        discovered_codes = set()
        
        # Try to find contracts/partners in login data
        # Common patterns: 'partners', 'contracts', 'accounts'
        if login_data:
            # Check for direct keys
            if "partners" in login_data:
                for p in login_data["partners"]:
                    if "accountContract" in p:
                         discovered_codes.add(str(p["accountContract"]))
            
            # Recursive search string for 10-digit codes if structure is unknown
            import json
            import re
            json_str = json.dumps(login_data)
            # Look for 10 digit numbers starting with 1 or 2 (EON codes usually)
            # But let's be more specific first.
            
            # If no obvious keys, let's log the structure deeply
            # _LOGGER.info("Login Data Content: %s", json_str) # CAUTION: PII
            
            pass

        # Fallback to wallet if login data didn't help (or try wallet again)
        # But previous wallet check showed only cards.
        
        if not discovered_codes:
             _LOGGER.info("No codes found in Login Data. Checking if there is a 'user' object...")
             # Maybe make a dedicated 'get_profile' call if one exists?
             pass

        # Use ENV code as fallback
        if COD_INCASARE:
            discovered_codes.add(COD_INCASARE)
            
        if not discovered_codes:
            _LOGGER.warning("No codes discovered. Cannot proceed.")
            # Print keys to help user debug
            if login_data:
                 _LOGGER.info("Login Data Keys available: %s", list(login_data.keys()))
            return

        _LOGGER.info("Starting validation for %d discovered codes: %s", len(discovered_codes), discovered_codes)

        for code in discovered_codes:
            _LOGGER.info("--------------------------------------------------")
            _LOGGER.info("VALIDATING ENDPOINTS FOR CODE: %s", code)
            _LOGGER.info("--------------------------------------------------")

            # A. Contracts List using this code (Discovery of sub-contracts)
            await asyncio.sleep(DELAY_SECONDS)
            contracts = await api.async_fetch_account_contracts_list()
            if contracts:
                _LOGGER.info("[OK] Contracts List (Sub-contracts found): %s", json.dumps(contracts, indent=2))
            else:
                _LOGGER.error("[FAIL] Contracts List")

            # B. Date User
            await asyncio.sleep(DELAY_SECONDS)
            date_user = await api.async_fetch_dateuser_data(code)
            if date_user:
                _LOGGER.info("[OK] Date User: %s", json.dumps(date_user, indent=2))
            else:
                _LOGGER.error("[FAIL] Date User")
            
            # C. Invoices (Unpaid)
            await asyncio.sleep(DELAY_SECONDS)
            invoices = await api.async_fetch_facturasold_data(code)
            if invoices:
                 _LOGGER.info("[OK] Invoices (Unpaid): %s", json.dumps(invoices, indent=2))
            else:
                 _LOGGER.error("[FAIL] Invoices (Unpaid)")

            # D. Paid Invoices
            await asyncio.sleep(DELAY_SECONDS)
            invoices_paid = await api.async_fetch_invoices_list_paid(code)
            if invoices_paid:
                 _LOGGER.info("[OK] Invoices (Paid): %s", json.dumps(invoices_paid, indent=2))
            else:
                 _LOGGER.error("[FAIL] Invoices (Paid)")

            # E. Index Reading
            await asyncio.sleep(DELAY_SECONDS)
            index = await api.async_fetch_citireindex_data(code)
            if index:
                 _LOGGER.info("[OK] Index Reading: %s", json.dumps(index, indent=2))
            else:
                 _LOGGER.error("[FAIL] Index Reading")
            
            # F. Consumption Convention
            await asyncio.sleep(DELAY_SECONDS)
            conv = await api.async_fetch_conventieconsum_data(code)
            if conv:
                 _LOGGER.info("[OK] Consumption Convention: %s", json.dumps(conv, indent=2))
            else:
                 _LOGGER.error("[FAIL] Consumption Convention")

            # G. Consumption Graphic
            await asyncio.sleep(5)
            graph = await api.async_fetch_comparareanualagrafic_data(code)
            if graph:
                 _LOGGER.info("[OK] Consumption Graphic: %s", json.dumps(graph, indent=2))
            else:
                 _LOGGER.error("[FAIL] Consumption Graphic")

if __name__ == "__main__":
    # Allow running this file directly if pytest is installed
    import sys
    try:
        sys.exit(pytest.main(["-v", "-s", __file__]))
    except ImportError:
        print("Please install pytest, pytest-asyncio, and python-dotenv")
