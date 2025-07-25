"""Test sensor."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


@pytest.mark.usefixtures("enable_all_entities")
async def test_sensors(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test sensors."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(hass, "sensor.test_device_water_temperature", "25.0")
    check_state_value(hass, "sensor.test_device_bluetooth_mac_address", "00:11:22:33:44:66")
    check_state_value(hass, "sensor.test_device_ip_address", "192.168.1.100", {"port": "8080"})
    check_state_value(hass, "sensor.test_device_wifi_mac_address", "00:11:22:33:44:55")
    check_state_value(hass, "sensor.test_device_wifi_signal", "-70")
    check_state_value(hass, "sensor.test_device_ssid", "TestWiFi")
    check_state_value(hass, "sensor.test_device_uptime", "2024-06-26T11:06:40+00:00")

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_sensor_no_device(hass: HomeAssistant) -> None:
    """Test that no sensors are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("sensor.test_device_water_temperature") is None
    assert hass.states.get("sensor.test_device_bluetooth_mac_address") is None
    assert hass.states.get("sensor.test_device_ip_address") is None
    assert hass.states.get("sensor.test_device_wifi_mac_address") is None
    assert hass.states.get("sensor.test_device_wifi_signal") is None
    assert hass.states.get("sensor.test_device_ssid") is None
    assert hass.states.get("sensor.test_device_uptime") is None

    await unload_integration(hass, config_entry)


async def test_sensor_no_temperature(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test sensor when no valid temperature."""
    device = create_test_device(
        {
            "sensor_valid": 0,
            "water_temperature": None,
        }
    )
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    assert hass.states.get("sensor.offline_device_water_temperature") is None

    await unload_integration(hass, config_entry)
