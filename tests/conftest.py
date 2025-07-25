"""Global fixtures for the custom component."""

from collections.abc import Generator
from unittest.mock import AsyncMock, Mock, PropertyMock, patch

import pytest

from aquatlantis_ori import AquatlantisOriClient


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: Generator) -> Generator[None]:
    """Enable custom integrations."""
    return enable_custom_integrations


@pytest.fixture(name="enable_all_entities")
def fixture_enable_all_entities() -> Generator[None]:
    """Make sure all entities are enabled."""
    with patch(
        "homeassistant.helpers.entity.Entity.entity_registry_enabled_default",
        PropertyMock(return_value=True),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_async_get_clientsession() -> Generator[None]:
    """Mock async_get_clientsession to avoid aiohttp client session issues in tests."""
    with (
        patch("custom_components.ori.async_get_clientsession"),
        patch("custom_components.ori.config_flow.async_get_clientsession"),
    ):
        yield


@pytest.fixture(autouse=True, name="mock_aquatlantis_client")
def fixture_mock_aquatlantis_client() -> Generator[AsyncMock]:
    """Auto-patch AquatlantisOriClient in all tests and return the mock for configuration."""
    mock_client = AsyncMock(spec=AquatlantisOriClient)
    # Set up default behavior - tests can override this
    mock_client.get_devices.return_value = []

    mock_client_class = Mock(return_value=mock_client)

    with (
        patch("custom_components.ori.AquatlantisOriClient", mock_client_class),
        patch("custom_components.ori.config_flow.AquatlantisOriClient", mock_client_class),
    ):
        yield mock_client


@pytest.fixture(name="mock_pycares_thread")
def fixture_mock_pycares_thread() -> Generator[None]:
    """Mock pycares to prevent threading issues in tests."""
    # Mock the pycares Channel class to prevent DNS resolver threads
    with patch("pycares.Channel") as mock_channel:
        # Configure the mock to not create any threads
        mock_channel_instance = Mock()
        mock_channel_instance.gethostbyname = Mock()
        mock_channel_instance.cancel = Mock()
        mock_channel.return_value = mock_channel_instance
        yield
