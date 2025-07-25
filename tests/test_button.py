"""Test button."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


async def test_buttons(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test buttons."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(
        hass,
        "button.test_device_preset_1",
        "unknown",
        {"intensity": 75, "red": 255, "green": 128, "blue": 64, "white": 200},
    )
    check_state_value(
        hass,
        "button.test_device_preset_2",
        "unknown",
        {"intensity": 50, "red": 200, "green": 100, "blue": 50, "white": 150},
    )
    check_state_value(
        hass,
        "button.test_device_preset_3",
        "unknown",
        {"intensity": None, "red": None, "green": None, "blue": None, "white": None},
    )
    check_state_value(
        hass,
        "button.test_device_preset_4",
        "unknown",
        {"intensity": None, "red": None, "green": None, "blue": None, "white": None},
    )

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_button_no_device(hass: HomeAssistant) -> None:
    """Test that no buttons are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("button.test_device_preset_1") is None
    assert hass.states.get("button.test_device_preset_2") is None
    assert hass.states.get("button.test_device_preset_3") is None
    assert hass.states.get("button.test_device_preset_4") is None

    await unload_integration(hass, config_entry)


async def test_button_press(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test button press."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    now = dt_util.utcnow()
    with (
        patch("homeassistant.core.dt_util.utcnow", return_value=now),
    ):
        await hass.services.async_call(
            BUTTON_DOMAIN,
            SERVICE_PRESS,
            {ATTR_ENTITY_ID: "button.test_device_preset_1"},
            blocking=True,
        )
        await hass.async_block_till_done()

    check_state_value(hass, "button.test_device_preset_1", now.isoformat())

    await unload_integration(hass, config_entry)
