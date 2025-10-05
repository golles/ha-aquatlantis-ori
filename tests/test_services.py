"""Test services."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers.device_registry import DeviceRegistry
from ori.const import DOMAIN
from ori.services import ATTR_SCHEDULE, SERVICE_SET_SCHEDULE, get_config

from custom_components.ori.services import get_device, get_device_entry, parse_timecurves, validate_curve

from . import setup_integration, unload_integration
from .test_helpers import create_test_device


@pytest.mark.usefixtures("enable_all_entities")
async def test_service_set_schedule(hass: HomeAssistant, device_registry: DeviceRegistry, mock_aquatlantis_client: AsyncMock) -> None:
    """Test set_schedule service."""
    device = create_test_device()
    mock_aquatlantis_client.get_devices.return_value = [device]

    config_entry = await setup_integration(hass)

    ha_device = device_registry.async_get_device(identifiers={(DOMAIN, str(device.id))})
    assert ha_device

    with patch("aquatlantis_ori.device.Device.set_timecurve") as call:
        await hass.services.async_call(
            DOMAIN,
            SERVICE_SET_SCHEDULE,
            {ATTR_DEVICE_ID: ha_device.id, ATTR_SCHEDULE: ["12,30,50,60,70,80,90"]},
            blocking=True,
        )
        await hass.async_block_till_done()

    # Test that the schedule change was sent to the device
    call.assert_called_once()

    await unload_integration(hass, config_entry)


def test_validate_curve_valid() -> None:
    """Test validate_curve with valid input."""
    assert validate_curve("12,30,50,60,70,80,90") is True


@pytest.mark.parametrize(
    ("curve"),
    [
        ("12,30,50,60,70,80"),  # Only 6 numbers
        ("12,30,50,60,70,80,90,100"),  # 8 numbers
        ("a,b,c,d,e,f,g"),  # Non-integer
        ("24,30,50,60,70,80,90"),  # hour > 23
        ("12,60,50,60,70,80,90"),  # minute > 59
        ("12,30,101,60,70,80,90"),  # intensity > 100
        ("12,30,-1,60,70,80,90"),  # intensity < 0
    ],
)
def test_validate_curve_invalid(curve: str) -> None:
    """Test validate_curve with invalid format."""
    assert not validate_curve(curve)


def test_parse_timecurves_valid() -> None:
    """Test parse_timecurves with valid curves."""
    curves = ["12,30,50,60,70,80,90", "0,0,0,0,0,0,0"]
    result = parse_timecurves(curves)
    assert len(result) == 2
    assert result[0].hour == 12
    assert result[1].hour == 0


def test_parse_timecurves_invalid() -> None:
    """Test parse_timecurves with invalid curve raises error."""
    curves = ["12,30,50,60,70,80,90", "99,99,99,99,99,99,99"]
    with pytest.raises(ServiceValidationError):
        parse_timecurves(curves)


def test_get_device_entry_device_not_found(hass: HomeAssistant) -> None:
    """Test get_device_entry raises error when device not found."""
    fake_device_id = "nonexistent"
    call = ServiceCall(hass=hass, domain="ori", service="set_schedule", data={"device_id": fake_device_id})

    mock_registry = Mock()
    mock_registry.async_get.return_value = None
    with (
        patch("custom_components.ori.services.dr.async_get", return_value=mock_registry),
        pytest.raises(ServiceValidationError) as exc,
    ):
        get_device_entry(hass, call)
    assert exc.value.translation_key == "device_entry_not_found"


def test_get_config_entry_not_found() -> None:
    """Test get_config raises error when config entry not found."""
    hass = Mock(spec=HomeAssistant)
    hass.config_entries = Mock()
    hass.config_entries.async_get_entry = Mock(return_value=None)
    device_entry = Mock()
    device_entry.config_entries = ["entry_id_1", "entry_id_2"]

    with pytest.raises(ServiceValidationError) as exc:
        get_config(hass, device_entry)
    assert exc.value.translation_key == "config_entry_not_found"


def test_get_device_not_found() -> None:
    """Test get_device raises error when device not found."""
    device_entry = Mock()
    device_entry.identifiers = {(DOMAIN, "missing_id")}
    config = Mock()
    # Simulate runtime_data.get_devices() returns devices with different IDs
    config.runtime_data.get_devices.return_value = [
        Mock(id="other_id"),
        Mock(id="another_id"),
    ]

    with pytest.raises(ServiceValidationError) as exc:
        get_device(device_entry, config)
    assert exc.value.translation_key == "device_not_found"
