"""Test config flow."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from aquatlantis_ori import AquatlantisOriConnectionError, AquatlantisOriError, AquatlantisOriLoginError, AquatlantisOriTimeoutError
from custom_components.ori.const import DOMAIN

from . import get_mock_config_data, setup_integration


@pytest.fixture(autouse=True, name="bypass_setup")
def fixture_bypass_setup_fixture() -> Generator[None]:
    """Prevent actual setup of the integration during tests."""
    with patch("custom_components.ori.async_setup_entry", return_value=True):
        yield


async def test_successful_config_flow(hass: HomeAssistant) -> None:
    """Test a successful config flow."""
    config_data = get_mock_config_data()
    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to fill in all fields, it would result in this function call
    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=config_data)

    # Check that the config flow is complete and a new entry is created with
    # the input data
    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == config_data[CONF_EMAIL]
    assert result2["data"] == config_data
    assert result2["result"]


@pytest.mark.parametrize(
    ("side_effect", "error"),
    [
        (AquatlantisOriLoginError, "invalid_auth"),
        (AquatlantisOriTimeoutError, "timeout"),
        (AquatlantisOriConnectionError, "cannot_connect"),
        (AquatlantisOriError, "unknown_error"),
    ],
)
async def test_unsuccessful_config_flow(side_effect: Exception, error: str, hass: HomeAssistant, mock_aquatlantis_client: AsyncMock) -> None:
    """Test an unsuccessful config flow ."""
    config_data = get_mock_config_data()
    mock_aquatlantis_client.connect.side_effect = side_effect

    # Initialize a config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    # Check that the config flow shows the user form as the first step
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # If a user were to fill in an incomplete form, it would result in this function call
    result2 = await hass.config_entries.flow.async_configure(result["flow_id"], user_input=config_data)

    # Check that the config flow returns an error due to missing email
    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": error}


async def test_step_reconfigure(hass: HomeAssistant) -> None:
    """Test for reconfigure step."""
    updated_data = {
        CONF_EMAIL: "example@test.com",
        CONF_PASSWORD: "ssapp",
    }
    config_entry = await setup_integration(hass)

    result = await config_entry.start_reconfigure_flow(hass)
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        updated_data,
    )
    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"

    assert config_entry.title == updated_data[CONF_EMAIL]
    assert config_entry.data == {**updated_data}
