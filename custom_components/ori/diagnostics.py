"""Aquatlantis Ori diagnostics."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant

from aquatlantis_ori import AquatlantisOriClient

TO_REDACT = {CONF_EMAIL, CONF_PASSWORD, "title", "ssid"}


async def async_get_config_entry_diagnostics(_hass: HomeAssistant, config_entry: ConfigEntry[AquatlantisOriClient]) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    client = config_entry.runtime_data

    data: dict[str, Any] = {
        "config_entry": config_entry.as_dict(),
        "devices": [{field: getattr(device, field) for field in device.__dict__ if not field.startswith("_")} for device in client.get_devices()],
    }

    return async_redact_data(data, TO_REDACT)
