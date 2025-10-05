"""Aquatlantis Ori entity."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription

from aquatlantis_ori import AquatlantisOriClient, Device, StatusType

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(kw_only=True, frozen=True)
class OriEntityDescription(EntityDescription):
    """Class describing Aquatlantis Ori entities."""

    available_fn: Callable[[Device], bool] = lambda _: True
    entity_registry_enabled_default_fn: Callable[[Device], bool] = lambda _: True
    is_supported_fn: Callable[[Device], bool] = lambda _: True
    state_attributes_fn: Callable[[Device], dict[str, Any]] = lambda _: {}


class OriEntity(Entity):
    """Representation of a Aquatlantis Ori entity."""

    entity_description: OriEntityDescription

    _attr_has_entity_name = True

    def __init__(
        self,
        config_entry: ConfigEntry[AquatlantisOriClient],
        description: OriEntityDescription,
        device: Device,
    ) -> None:
        """Initialize the Aquatlantis Ori entity."""
        _LOGGER.info("Creating entity %s for device %s", description.key, device.devid)
        self.entity_description = description

        self._attr_entity_registry_enabled_default = description.entity_registry_enabled_default_fn(device)
        self._attr_unique_id = f"{device.id}_{description.key}".lower()
        self._config_entry = config_entry
        self._device = device
        self._attr_device_info = DeviceInfo(
            name=device.name,
            identifiers={(DOMAIN, str(device.id))},
            connections={(CONNECTION_NETWORK_MAC, device.mac)},
            manufacturer=device.brand,
            model="Ori",
            model_id=device.light_type.name if device.light_type is not None else device.devid,
            sw_version=device.version,
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.status == StatusType.ONLINE and self.entity_description.available_fn(self._device)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        return self.entity_description.state_attributes_fn(self._device)
