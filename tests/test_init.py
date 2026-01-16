"""Test setup."""

from unittest.mock import AsyncMock

import pytest
from _pytest.logging import LogCaptureFixture
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from aquatlantis_ori import AquatlantisOriClient, AquatlantisOriError
from custom_components.ori import async_setup_entry

from . import get_mock_config_entry, setup_integration, unload_integration


async def test_setup_and_unload_entry(hass: HomeAssistant) -> None:
    """Test entry setup and unload."""
    config_entry = await setup_integration(hass)

    # Check that the client is stored as runtime_data
    assert isinstance(config_entry.runtime_data, AquatlantisOriClient)

    # Unload the entry
    await unload_integration(hass, config_entry)


async def test_setup_entry_exception(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test setup entry raises ConfigEntryNotReady on connection error."""
    # Configure the mock to raise an error on connect
    mock_aquatlantis_client.connect.side_effect = AquatlantisOriError()

    # Create config entry but don't set it up through HA's system
    config_entry = get_mock_config_entry()
    config_entry.add_to_hass(hass)

    # This should raise ConfigEntryNotReady due to connection error
    with pytest.raises(ConfigEntryNotReady):
        await async_setup_entry(hass, config_entry)


async def test_setup_entry_timeout_exception(hass: HomeAssistant, mock_aquatlantis_client: AsyncMock, caplog: LogCaptureFixture) -> None:
    """Test setup entry does not raise exception on timeout."""
    # Configure the mock to simulate a timeout
    mock_aquatlantis_client.connect.side_effect = TimeoutError("Connection timed out")

    with caplog.at_level("WARNING"):
        config_entry = await setup_integration(hass)
        await unload_integration(hass, config_entry)

    assert "Data wasn't available during setup, it should be available soon" in caplog.text
