"""Test diagnostics."""

from unittest.mock import AsyncMock

import pytest
from homeassistant.components.diagnostics import REDACTED
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.components.diagnostics import get_diagnostics_for_config_entry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from tests import setup_integration, unload_integration

from .test_helpers import create_test_device


@pytest.mark.usefixtures("mock_pycares_thread")
async def test_diagnostics(hass: HomeAssistant, hass_client: ClientSessionGenerator, mock_aquatlantis_client: AsyncMock) -> None:
    """Test config entry diagnostics."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]
    config_entry = await setup_integration(hass)

    result = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert result["config_entry"]["data"]["email"] == REDACTED
    assert result["config_entry"]["data"]["password"] == REDACTED
    assert result["devices"][0]["ssid"] == REDACTED

    await unload_integration(hass, config_entry)


@pytest.mark.usefixtures("mock_aquatlantis_client")
@pytest.mark.usefixtures("mock_pycares_thread")
async def test_diagnostics_no_device(hass: HomeAssistant, hass_client: ClientSessionGenerator) -> None:
    """Test config diagnostics when no device is available."""
    config_entry = await setup_integration(hass)

    result = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    assert result["config_entry"]["data"]["email"] == REDACTED
    assert result["config_entry"]["data"]["password"] == REDACTED
    assert result["devices"] == []

    await unload_integration(hass, config_entry)
