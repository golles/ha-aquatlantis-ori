"""Test light."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_RGBW_COLOR, SERVICE_TURN_OFF, SERVICE_TURN_ON, ColorMode
from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from aquatlantis_ori import LightOptions, ModeType, PowerType
from custom_components.ori.light import _convert_100_to_255, _convert_255_to_100

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


async def test_light(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(
        hass,
        "light.test_device_light",
        "on",
        {
            "color_mode": ColorMode.RGBW,
            "brightness": 204,
            "rgbw_color": (26, 51, 76, 102),  # Updated due to improved rounding
        },
    )

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_light_no_device(hass: HomeAssistant) -> None:
    """Test that no lights are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("light.test_device_light") is None

    await unload_integration(hass, config_entry)


async def test_light_color_mode_on_off(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light color mode is set to on/off for  when the device mode is set to automatic."""
    device = create_test_device({"mode": ModeType.AUTOMATIC.value})
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(hass, "light.test_device_light", "on", {"color_mode": ColorMode.ONOFF})

    await unload_integration(hass, config_entry)


async def test_light_turn_on(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light turn on."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with patch(
        "aquatlantis_ori.device.Device.set_light",
    ) as call:
        await hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {ATTR_ENTITY_ID: "light.test_device_light"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call.assert_called_once_with(PowerType.ON, LightOptions())

    await unload_integration(hass, config_entry)


async def test_light_turn_on_with_values(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light turn on with values."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with patch(
        "aquatlantis_ori.device.Device.set_light",
    ) as call:
        await hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: "light.test_device_light",
                ATTR_RGBW_COLOR: (255, 255, 255, 255),
                ATTR_BRIGHTNESS: 255,
            },
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call.assert_called_once_with(PowerType.ON, LightOptions(intensity=100, red=100, green=100, blue=100, white=100))

    await unload_integration(hass, config_entry)


async def test_light_turn_off(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light turn off."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with patch(
        "aquatlantis_ori.device.Device.set_power",
    ) as call:
        await hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_OFF,
            {ATTR_ENTITY_ID: "light.test_device_light"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call.assert_called_once_with(PowerType.OFF)

    await unload_integration(hass, config_entry)


@pytest.mark.parametrize(
    ("input_value", "expected_output"),
    [
        (0, 0),
        (26, 10),
        (51, 20),
        (76, 30),
        (102, 40),
        (128, 50),
        (204, 80),
        (255, 100),
    ],
)
def test_convert_255_to_100(input_value: int, expected_output: int) -> None:
    """Test conversion from 0-255 range to 0-100 range."""
    assert _convert_255_to_100(input_value) == expected_output


@pytest.mark.parametrize(
    ("input_value", "expected_output"),
    [
        (0, 0),
        (10, 26),
        (20, 51),
        (30, 76),
        (40, 102),
        (50, 128),
        (80, 204),
        (100, 255),
    ],
)
def test_convert_100_to_255(input_value: int, expected_output: int) -> None:
    """Test conversion from 0-100 range to 0-255 range."""
    assert _convert_100_to_255(input_value) == expected_output
