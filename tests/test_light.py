"""Test light."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.light import ATTR_BRIGHTNESS, ATTR_EFFECT, ATTR_RGBW_COLOR, SERVICE_TURN_OFF, SERVICE_TURN_ON, ColorMode
from homeassistant.components.light import (
    DOMAIN as LIGHT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from aquatlantis_ori import DynamicModeType, LightOptions, ModeType, PowerType
from custom_components.ori.light import EFFECT_AUTOMATIC, EFFECT_DYNAMIC, EFFECT_MANUAL, _convert_100_to_255, _convert_255_to_100

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


async def test_light_turn_on_with_rgbw(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light turn on with RGBW values."""
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
            },
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call.assert_called_once_with(PowerType.ON, LightOptions(red=100, green=100, blue=100, white=100))

    await unload_integration(hass, config_entry)


async def test_light_turn_on_with_brightness(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test light turn on with brightness values."""
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
                ATTR_BRIGHTNESS: 255,
            },
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call.assert_called_once_with(PowerType.ON, LightOptions(intensity=100))

    await unload_integration(hass, config_entry)


@pytest.mark.parametrize(
    ("effect", "mode", "dynamic"),
    [
        (EFFECT_MANUAL, ModeType.MANUAL, DynamicModeType.OFF),
        (EFFECT_AUTOMATIC, ModeType.AUTOMATIC, DynamicModeType.OFF),
        (EFFECT_DYNAMIC, ModeType.MANUAL, DynamicModeType.ON),
    ],
)
async def test_light_turn_on_with_effect(
    hass: HomeAssistant, mock_aquatlantis_client: AsyncMock, effect: str, mode: ModeType, dynamic: DynamicModeType
) -> None:
    """Test light turn on with effect."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with (
        patch("aquatlantis_ori.device.Device.set_light") as call_light,
        patch("aquatlantis_ori.device.Device.set_mode") as call_mode,
        patch("aquatlantis_ori.device.Device.set_dynamic_mode") as call_dynamic,
    ):
        await hass.services.async_call(
            LIGHT_DOMAIN,
            SERVICE_TURN_ON,
            {
                ATTR_ENTITY_ID: "light.test_device_light",
                ATTR_EFFECT: effect,
            },
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the light change was sent to the device
    call_mode.assert_called_once_with(mode)
    call_dynamic.assert_called_once_with(dynamic)
    call_light.assert_called_once_with(PowerType.ON, LightOptions())

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
    ("mode", "dynamic", "effect"),
    [
        (ModeType.MANUAL, DynamicModeType.OFF, EFFECT_MANUAL),
        (ModeType.AUTOMATIC, DynamicModeType.OFF, EFFECT_AUTOMATIC),
        (ModeType.MANUAL, DynamicModeType.ON, EFFECT_DYNAMIC),
    ],
)
async def test_light_effect(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock, mode: ModeType, dynamic: DynamicModeType, effect: str) -> None:
    """Test light effect."""
    device = create_test_device(
        {
            "mode": mode.value,
            "dynamic_mode": dynamic.value,
        }
    )
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(
        hass,
        "light.test_device_light",
        "on",
        {
            "effect": effect,
        },
    )

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
