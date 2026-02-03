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

import pytest
from unittest.mock import MagicMock, AsyncMock
import sys

# 1. Mock Home Assistant Modules BEFORE importing custom_components
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
mock_module("homeassistant.helpers.update_coordinator")
mock_module("homeassistant.helpers.device_registry") # Added this
mock_module("homeassistant.components", pkg=True)
mock_module("homeassistant.components.button")
mock_module("homeassistant.components.number")
mock_module("homeassistant.components.sensor") # Added this
mock_module("homeassistant.helpers.entity_platform")
mock_module("homeassistant.const")

# Fix inheritance for ButtonEntity and NumberEntity
# Fix inheritance for ButtonEntity, NumberEntity, SensorEntity, CoordinatorEntity
class MockEntity:
    def __init__(self, *args, **kwargs):
        pass

# Ensure all base classes used in inheritance chains are compatible (same MockEntity)
sys.modules["homeassistant.components.button"].ButtonEntity = MockEntity
sys.modules["homeassistant.components.number"].NumberEntity = MockEntity
sys.modules["homeassistant.components.sensor"].SensorEntity = MockEntity

# Mock CoordinatorEntity which EonEntity likely inherits from
sys.modules["homeassistant.helpers.update_coordinator"].CoordinatorEntity = MockEntity

sys.modules["homeassistant.helpers.entity"] = MagicMock()
sys.modules["homeassistant.helpers.entity"].Entity = MockEntity

# 2. NOW we can import custom_components
from custom_components.lejer_eonromania.button import TrimiteIndexButton
from custom_components.lejer_eonromania.const import DOMAIN, KEY_CITIREINDEX
from custom_components.lejer_eonromania.entity import EonEntity

# Patch EonEntity properties if needed, but inheritance is now safe
EonEntity.contract_data = property(lambda self: self.coordinator.data["data_per_contract"].get(self._cod_incasare, {}))


@pytest.mark.asyncio
async def test_button_reads_number():
    """Test that button reads from the correct number entity."""
    
    # Setup
    hass = MagicMock(spec=HomeAssistant)
    coordinator = MagicMock()
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    cod_incasare = "123456"
    
    # Mock Coordinator Data
    coordinator.data = {
        "data_per_contract": {
            cod_incasare: {
                KEY_CITIREINDEX: {
                    "indexDetails": {
                        "devices": [
                            {"indexes": [{"ablbelnr": "meter_id_999"}]}
                        ]
                    }
                }
            }
        }
    }
    
    # Initialize Button
    button = TrimiteIndexButton(coordinator, config_entry, cod_incasare)
    button.hass = hass
    button._cod_incasare = cod_incasare
    button.coordinator = coordinator
    
    # Mock State of Number Entity
    expected_index = 54321
    mock_state = MagicMock()
    mock_state.state = str(expected_index)
    
    # Configure hass.states.get to return our mock state when asked for the specific number entity
    def side_effect(entity_id):
        if entity_id == f"number.{DOMAIN}_index_input_{cod_incasare}":
            return mock_state
        return None
        
    hass.states.get.side_effect = side_effect
    
    # Call Press
    await button.async_press()
    
    # Assert
    coordinator.api_client.async_trimite_index.assert_called_once_with(
        account_contract=cod_incasare,
        ablbelnr="meter_id_999",
        index_value=expected_index
    )
