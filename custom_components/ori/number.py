"""Aquatlantis Ori number."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, DynamicModeType, ModeType

from .entity import OriEntity, OriEntityDescription

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=2)


@dataclass(kw_only=True, frozen=True)
class OriNumberDescription(OriEntityDescription, NumberEntityDescription):
    """Class describing Aquatlantis Ori number entities."""

    value_fn: Callable[[Device], int | None]
    set_fn: Callable[[Device, int], None]


DESCRIPTIONS: list[OriNumberDescription] = [
    OriNumberDescription(
        key="intensity",
        translation_key="intensity",
        native_min_value=0.0,
        native_max_value=100.0,
        native_step=1.0,
        value_fn=lambda device: device.intensity if device.intensity is not None else None,
        set_fn=lambda device, value: device.set_intensity(value),
        entity_registry_enabled_default_fn=lambda _: False,
        available_fn=lambda device: device.mode == ModeType.MANUAL and device.dynamic_mode == DynamicModeType.OFF,
    ),
    OriNumberDescription(
        key="red",
        translation_key="red",
        native_min_value=0.0,
        native_max_value=100.0,
        native_step=1.0,
        value_fn=lambda device: device.red if device.red is not None else None,
        set_fn=lambda device, value: device.set_red(value),
        entity_registry_enabled_default_fn=lambda _: False,
        available_fn=lambda device: device.mode == ModeType.MANUAL and device.dynamic_mode == DynamicModeType.OFF,
    ),
    OriNumberDescription(
        key="green",
        translation_key="green",
        native_min_value=0.0,
        native_max_value=100.0,
        native_step=1.0,
        value_fn=lambda device: device.green if device.green is not None else None,
        set_fn=lambda device, value: device.set_green(value),
        entity_registry_enabled_default_fn=lambda _: False,
        available_fn=lambda device: device.mode == ModeType.MANUAL and device.dynamic_mode == DynamicModeType.OFF,
    ),
    OriNumberDescription(
        key="blue",
        translation_key="blue",
        native_min_value=0.0,
        native_max_value=100.0,
        native_step=1.0,
        value_fn=lambda device: device.blue if device.blue is not None else None,
        set_fn=lambda device, value: device.set_blue(value),
        entity_registry_enabled_default_fn=lambda _: False,
        available_fn=lambda device: device.mode == ModeType.MANUAL and device.dynamic_mode == DynamicModeType.OFF,
    ),
    OriNumberDescription(
        key="white",
        translation_key="white",
        native_min_value=0.0,
        native_max_value=100.0,
        native_step=1.0,
        value_fn=lambda device: device.white if device.white is not None else None,
        set_fn=lambda device, value: device.set_white(value),
        entity_registry_enabled_default_fn=lambda _: False,
        available_fn=lambda device: device.mode == ModeType.MANUAL and device.dynamic_mode == DynamicModeType.OFF,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori number entry."""
    entities: list[NumberEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriNumber(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriNumber(OriEntity, NumberEntity):
    """Representation of a Aquatlantis Ori number entity."""

    entity_description: OriNumberDescription

    @property
    def native_value(self) -> float | None:
        """Return the value reported by the number."""
        return self.entity_description.value_fn(self._device)

    def set_native_value(self, value: float) -> None:
        """Set new value."""
        self.entity_description.set_fn(self._device, int(value))
