"""Test select."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.components.select import (
    ATTR_OPTION,
    SERVICE_SELECT_OPTION,
)
from homeassistant.components.select import (
    DOMAIN as SELECT_DOMAIN,
)
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant

from aquatlantis_ori import DynamicModeType

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


async def test_select(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test select."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(hass, "select.test_device_dynamic_mode", "off")
    check_state_value(hass, "select.test_device_light_mode", "manual")

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_selects_no_device(hass: HomeAssistant) -> None:
    """Test that no selects are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("select.test_device_dynamic_mode") is None
    assert hass.states.get("select.test_device_light_mode") is None

    await unload_integration(hass, config_entry)


async def test_select_select(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test select select."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    with patch(
        "aquatlantis_ori.device.Device.set_dynamic_mode",
    ) as call:
        await hass.services.async_call(
            SELECT_DOMAIN,
            SERVICE_SELECT_OPTION,
            {ATTR_ENTITY_ID: "select.test_device_dynamic_mode", ATTR_OPTION: "on"},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the select change was sent to the device
    call.assert_called_once_with(DynamicModeType.ON)

    await unload_integration(hass, config_entry)
