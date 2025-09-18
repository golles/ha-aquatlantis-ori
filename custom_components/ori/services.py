"""Aquatlantis Ori services."""

from __future__ import annotations

import logging
import re

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig

from aquatlantis_ori import AquatlantisOriClient, Device, TimeCurve

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

ATTR_SCHEDULE = "schedule"

SERVICE_SET_SCHEDULE = "set_schedule"
SERVICE_SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): str,
        vol.Required(ATTR_SCHEDULE): TextSelector(TextSelectorConfig(multiple=True)),
    }
)


def get_device_entry(hass: HomeAssistant, call: ServiceCall) -> dr.DeviceEntry:
    """Get the device entry related to a service call."""
    device_id = call.data[ATTR_DEVICE_ID]
    device_registry = dr.async_get(hass)
    if (device_entry := device_registry.async_get(device_id)) is None:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="device_entry_not_found",
        )

    return device_entry


def get_config(hass: HomeAssistant, device_entry: dr.DeviceEntry) -> ConfigEntry[AquatlantisOriClient]:
    """Get the config entry related to a device entry."""
    config_entry: ConfigEntry[AquatlantisOriClient] | None = None
    for entry_id in device_entry.config_entries:
        if (entry := hass.config_entries.async_get_entry(entry_id)) and entry.domain == DOMAIN:
            config_entry = entry

    if config_entry is None:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="config_entry_not_found",
        )

    return config_entry


def get_device(device_entry: dr.DeviceEntry, config: ConfigEntry[AquatlantisOriClient]) -> Device:
    """Get the device data for a config entry."""
    device_data: Device | None = None
    for device in config.runtime_data.get_devices():
        if device_entry.identifiers == {(DOMAIN, device.id)}:
            device_data = device

    if device_data is None:
        raise ServiceValidationError(
            translation_domain=DOMAIN,
            translation_key="device_not_found",
        )

    return device_data


def validate_curve(curve: str) -> bool:
    """Validate a single time curve string."""
    last_hour = 23
    last_minute = 59
    min_percentage = 0
    max_percentage = 100

    if not re.fullmatch(r"\d+(,\d+){6}", curve):  # Match exactly 7 integer numbers separated by commas
        return False

    parts = list(map(int, curve.split(",")))
    if not 0 <= parts[0] <= last_hour:
        return False
    if not 0 <= parts[1] <= last_minute:
        return False
    return not any(not (min_percentage <= p <= max_percentage) for p in parts[2:])


def parse_timecurves(timecurves: list[str]) -> list[TimeCurve]:
    """Parse time curves from a list of strings."""
    parsed_timecurves = []
    for curve in timecurves:
        normalized_curve = curve.replace(" ", "")

        if not validate_curve(normalized_curve):
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key="invalid_time_curve",
                translation_placeholders={"curve": curve},
            )

        parts = normalized_curve.split(",")

        parsed_timecurves.append(
            TimeCurve(
                hour=int(parts[0]),
                minute=int(parts[1]),
                intensity=int(parts[2]),
                red=int(parts[3]),
                green=int(parts[4]),
                blue=int(parts[5]),
                white=int(parts[6]),
            )
        )

    return parsed_timecurves


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services."""

    def set_schedule(call: ServiceCall) -> None:
        """Set schedule."""
        schedule = parse_timecurves(call.data[ATTR_SCHEDULE])
        device_entry = get_device_entry(hass, call)
        config = get_config(hass, device_entry)
        device = get_device(device_entry, config)

        _LOGGER.debug("Setting new schedule: %s", schedule)

        device.set_timecurve(schedule)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SCHEDULE,
        set_schedule,
        SERVICE_SET_SCHEDULE_SCHEMA,
    )
