"""Test sensor."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


@pytest.mark.usefixtures("enable_all_entities")
async def test_binary_sensors(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test binary sensors."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(hass, "binary_sensor.test_device_connectivity", "on")
    check_state_value(
        hass,
        "binary_sensor.test_device_water_temperature",
        "off",
        {
            "water_temperature": 25.0,
            "min_value": 20.0,
            "max_value": 30.0,
            "app_notifications": False,
        },
    )

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_binary_sensors_no_device(hass: HomeAssistant) -> None:
    """Test that no binary_sensors are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("binary_sensor.test_device_connectivity") is None
    assert hass.states.get("binary_sensor.test_device_water_temperature") is None

    await unload_integration(hass, config_entry)
