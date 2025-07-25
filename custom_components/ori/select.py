"""Aquatlantis Ori select."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, DynamicModeType, ModeType

from .entity import OriEntity, OriEntityDescription

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=2)


@dataclass(kw_only=True, frozen=True)
class OriSelectEntityDescription(OriEntityDescription, SelectEntityDescription):
    """Class describing Aquatlantis Ori select entities."""

    value_fn: Callable[[Device], str | None]
    set_fn: Callable[[Device, str], None]


DESCRIPTIONS: list[OriSelectEntityDescription] = [
    OriSelectEntityDescription(
        key="dynamic_mode",
        translation_key="dynamic_mode",
        options=[item.name for item in DynamicModeType],
        value_fn=lambda device: DynamicModeType(device.dynamic_mode).name if device.dynamic_mode is not None else None,
        set_fn=lambda device, value: device.set_dynamic_mode(DynamicModeType[value]),
        available_fn=lambda device: device.mode == ModeType.MANUAL,
    ),
    OriSelectEntityDescription(
        key="mode",
        translation_key="mode",
        options=[item.name for item in ModeType],
        value_fn=lambda device: ModeType(device.mode).name if device.mode is not None else None,
        set_fn=lambda device, value: device.set_mode(ModeType[value]),
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori select entry."""
    entities: list[SelectEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriSelect(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriSelect(OriEntity, SelectEntity):
    """Representation of a Aquatlantis Ori select entity."""

    entity_description: OriSelectEntityDescription

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self.entity_description.value_fn(self._device)

    def select_option(self, option: str) -> None:
        """Change the selected option."""
        _LOGGER.info("Changing select %s to %s on device %s", self.entity_description.key, option, self._device.devid)
        self.entity_description.set_fn(self._device, option)
