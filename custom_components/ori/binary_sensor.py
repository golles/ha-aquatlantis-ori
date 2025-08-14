"""Aquatlantis Ori binary sensor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, SensorType, SensorValidType, StatusType

from .entity import OriEntity, OriEntityDescription

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=10)


@dataclass(kw_only=True, frozen=True)
class OriBinarySensorEntityDescription(OriEntityDescription, BinarySensorEntityDescription):
    """Class describing Aquatlantis Ori binary sensor entities."""

    value_fn: Callable[[Device], bool]


DESCRIPTIONS: list[OriBinarySensorEntityDescription] = [
    OriBinarySensorEntityDescription(
        key="status",
        translation_key="status",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda device: device.status == StatusType.ONLINE,
    ),
    OriBinarySensorEntityDescription(
        key="water_temperature_problem",
        translation_key="water_temperature_problem",
        device_class=BinarySensorDeviceClass.PROBLEM,
        available_fn=lambda device: device.status == StatusType.ONLINE
        and device.sensor_valid == SensorValidType.VALID
        and device.water_temperature_thresholds is not None,
        value_fn=lambda device: (
            True
            if device.water_temperature_thresholds is None or device.water_temperature is None
            else not (device.water_temperature_thresholds.min_value <= device.water_temperature <= device.water_temperature_thresholds.max_value)
        ),
        is_supported_fn=lambda device: device.sensor_type == SensorType.TEMPERATURE and device.water_temperature_thresholds is not None,
        entity_registry_enabled_default_fn=lambda _: False,
        state_attributes_fn=lambda device: {
            "water_temperature": device.water_temperature,
            "min_value": device.water_temperature_thresholds.min_value if device.water_temperature_thresholds else None,
            "max_value": device.water_temperature_thresholds.max_value if device.water_temperature_thresholds else None,
            "app_notifications": device.app_notifications,
        },
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori binary sensor entry."""
    entities: list[BinarySensorEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriBinarySensor(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriBinarySensor(OriEntity, BinarySensorEntity):
    """Representation of a Aquatlantis Ori binary sensor."""

    entity_description: OriBinarySensorEntityDescription

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.value_fn(self._device)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Handle the case locally so the connectivity sensor is always available.
        return self.entity_description.available_fn(self._device)
