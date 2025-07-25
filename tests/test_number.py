"""Test number."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.number import (
    ATTR_VALUE,
    SERVICE_SET_VALUE,
)
from homeassistant.components.number import (
    DOMAIN as NUMBER_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


@pytest.mark.usefixtures("enable_all_entities")
async def test_numbers(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test numbers."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(hass, "number.test_device_intensity", "80")
    check_state_value(hass, "number.test_device_red", "10")
    check_state_value(hass, "number.test_device_green", "20")
    check_state_value(hass, "number.test_device_blue", "30")
    check_state_value(hass, "number.test_device_white", "40")

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_numbers_no_device(hass: HomeAssistant) -> None:
    """Test that no numbers are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("number.test_device_intensity") is None
    assert hass.states.get("number.test_device_red") is None
    assert hass.states.get("number.test_device_green") is None
    assert hass.states.get("number.test_device_blue") is None
    assert hass.states.get("number.test_device_white") is None

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("enable_all_entities")
async def test_number_set(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test a number entity limits and setting values."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with patch(
        "aquatlantis_ori.device.Device.set_intensity",
    ) as call:
        await hass.services.async_call(
            NUMBER_DOMAIN,
            SERVICE_SET_VALUE,
            {ATTR_ENTITY_ID: "number.test_device_intensity", ATTR_VALUE: 50},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the number change was sent to the device
    call.assert_called_once_with(50)

    await unload_integration(hass, config_entry)
