"""Test update."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.core import HomeAssistant

from . import setup_integration, unload_integration
from .test_helpers import check_state_value, create_test_device


async def test_update_no_update(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test update."""
    device = create_test_device(
        {
            "version": 10,
            "firmwareVersion": 10,
            "firmwareName": "testpkey_V10.bin",
            "firmwarePath": "https://example.com/testpkey_V10.bin",
        }
    )
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(
        hass,
        "update.test_device_firmware",
        "off",
        {
            "filename": "testpkey_V10.bin",
            "download_url": "https://example.com/testpkey_V10.bin",
        },
    )

    await unload_integration(hass, config_entry)


async def test_update_has_update(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test update sensor with available firmware update."""
    device = create_test_device(
        {
            "version": 10,
            "firmwareVersion": 11,
            "firmwareName": "testpkey_V11.bin",
            "firmwarePath": "https://example.com/testpkey_V11.bin",
        }
    )
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    check_state_value(
        hass,
        "update.test_device_firmware",
        "on",
        {
            "filename": "testpkey_V11.bin",
            "download_url": "https://example.com/testpkey_V11.bin",
        },
    )

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
async def test_update_no_device(hass: HomeAssistant) -> None:
    """Test that no update are created when there is no device."""
    config_entry = await setup_integration(hass)

    assert hass.states.get("update.test_device_firmware") is None

    await unload_integration(hass, config_entry)
