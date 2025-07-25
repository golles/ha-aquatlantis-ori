"""Aquatlantis Ori update."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient

from .entity import OriEntity, OriEntityDescription

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=10)


@dataclass(kw_only=True, frozen=True)
class OriUpdateEntityDescription(OriEntityDescription, UpdateEntityDescription):
    """Class describing Aquatlantis Ori update entities."""


DESCRIPTIONS: list[OriUpdateEntityDescription] = [
    OriUpdateEntityDescription(
        key="firmware",
        translation_key="firmware",
        device_class=UpdateDeviceClass.FIRMWARE,
        state_attributes_fn=lambda device: {
            "filename": device.firmware_name,
            "download_url": device.firmware_path,
        },
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori update entry."""
    entities: list[UpdateEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriUpdate(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriUpdate(OriEntity, UpdateEntity):
    """Representation of a Aquatlantis Ori update entity."""

    entity_description: OriUpdateEntityDescription

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        return self._device.version

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        return str(self._device.latest_firmware_version)
