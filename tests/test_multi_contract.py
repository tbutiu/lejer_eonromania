
import sys
from unittest.mock import MagicMock

# Mock HA modules before importing custom_components
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

# Fix inheritance
class MockClass:
    def __init__(self, *args, **kwargs):
        pass

sys.modules["homeassistant.helpers.update_coordinator"].DataUpdateCoordinator = MockClass
sys.modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = MockClass
sys.modules["homeassistant.components.sensor"].SensorEntity = MockClass
sys.modules["homeassistant.components.binary_sensor"].BinarySensorEntity = MockClass
sys.modules["homeassistant.components.button"].ButtonEntity = MockClass
sys.modules["homeassistant.helpers.entity"].Entity = MockClass

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import logging
from custom_components.lejer_eonromania.coordinator import EonRomaniaCoordinator
from custom_components.lejer_eonromania.const import (
    KEY_CONTRACTS, KEY_DATEUSER, KEY_CITIREINDEX, KEY_FACTURASOLD
)
from homeassistant.core import HomeAssistant

# Constants for mocking
MOCK_CONTRACT_1 = "0001111111"
MOCK_CONTRACT_2 = "0002222222"

MOCK_CONTRACTS_LIST = [
    {
        "contractDetails": {
            "accountContract": MOCK_CONTRACT_1,
            "consumptionPointAddress": {}
        }
    },
    {
        "contractDetails": {
            "accountContract": MOCK_CONTRACT_2,
            "consumptionPointAddress": {}
        }
    }
]

MOCK_DATEUSER = {"accountContract": MOCK_CONTRACT_1, "consumptionPointCode": "123"}
MOCK_CITIRE = {"indexDetails": {"devices": []}}
MOCK_INVOICES = []

@pytest.mark.asyncio
async def test_coordinator_multi_contract():
    """Test that coordinator correctly splits data for multiple contracts."""
    
    # Mock HASS
    hass = MagicMock(spec=HomeAssistant)
    
    # Mock API Client
    api_client = MagicMock()
    api_client.async_fetch_account_contracts_list = AsyncMock(return_value=MOCK_CONTRACTS_LIST)
    api_client.async_fetch_user_wallet = AsyncMock(return_value={})
    
    # Generic generic mocks for specific contract calls
    api_client.async_fetch_dateuser_data = AsyncMock(return_value=MOCK_DATEUSER)
    api_client.async_fetch_citireindex_data = AsyncMock(return_value=MOCK_CITIRE)
    api_client.async_fetch_conventieconsum_data = AsyncMock(return_value={})
    api_client.async_fetch_comparareanualagrafic_data = AsyncMock(return_value={})
    api_client.async_fetch_arhiva_data = AsyncMock(return_value={})
    api_client.async_fetch_facturasold_data = AsyncMock(return_value=MOCK_INVOICES)
    api_client.async_fetch_invoice_balance_prosum = AsyncMock(return_value={})
    api_client.async_fetch_invoices_list_prosum = AsyncMock(return_value={})
    api_client.async_fetch_invoices_list_paid = AsyncMock(return_value={})
    api_client.async_fetch_rescheduling_plans = AsyncMock(return_value={})
    api_client.async_fetch_payment_notices = AsyncMock(return_value={})
    api_client.async_fetch_payments_data = AsyncMock(return_value={})

    # Initialize Coordinator
    coordinator = EonRomaniaCoordinator(hass, api_client, update_interval=3600)
    
    # Trigger update
    result = await coordinator._async_update_data()
    
    # Assertions
    assert KEY_CONTRACTS in result
    assert result[KEY_CONTRACTS] == MOCK_CONTRACTS_LIST
    
    assert "data_per_contract" in result
    contract_data = result["data_per_contract"]
    
    # Check if both contracts are present
    assert MOCK_CONTRACT_1 in contract_data
    assert MOCK_CONTRACT_2 in contract_data
    
    # Check if calls were made for EACH contract
    assert api_client.async_fetch_dateuser_data.call_count == 2
    api_client.async_fetch_dateuser_data.assert_any_call(MOCK_CONTRACT_1)
    api_client.async_fetch_dateuser_data.assert_any_call(MOCK_CONTRACT_2)
