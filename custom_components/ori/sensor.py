"""Aquatlantis Ori sensor."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass, StateType
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, SensorType, SensorValidType

from .entity import OriEntity, OriEntityDescription

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=10)


@dataclass(kw_only=True, frozen=True)
class OriSensorEntityDescription(OriEntityDescription, SensorEntityDescription):
    """Class describing Aquatlantis Ori sensor entities."""

    value_fn: Callable[[Device], StateType | datetime]


DESCRIPTIONS: list[OriSensorEntityDescription] = [
    # Regular sensors
    OriSensorEntityDescription(
        key="water_temperature",
        translation_key="water_temperature",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda device: device.water_temperature,
        available_fn=lambda device: device.sensor_valid == SensorValidType.VALID,
        is_supported_fn=lambda device: device.sensor_type == SensorType.TEMPERATURE,
        entity_registry_enabled_default_fn=lambda device: device.sensor_valid == SensorValidType.VALID and device.water_temperature is not None,
    ),
    # Diagnostic sensors
    OriSensorEntityDescription(
        key="bluetooth_mac",
        translation_key="bluetooth_mac",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.bluetooth_mac,
    ),
    OriSensorEntityDescription(
        key="ip",
        translation_key="ip",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.ip,
        state_attributes_fn=lambda device: {
            "port": str(device.port) if device.port else None,
        },
    ),
    OriSensorEntityDescription(
        key="mac",
        translation_key="mac",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.mac,
    ),
    OriSensorEntityDescription(
        key="rssi",
        translation_key="rssi",
        entity_category=EntityCategory.DIAGNOSTIC,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.rssi,
    ),
    OriSensorEntityDescription(
        key="ssid",
        translation_key="ssid",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.ssid,
    ),
    OriSensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_registry_enabled_default_fn=lambda _: False,
        value_fn=lambda device: device.online_time,
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori sensor entry."""
    entities: list[SensorEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriSensor(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriSensor(OriEntity, SensorEntity):
    """Representation of a Aquatlantis Ori sensor."""

    entity_description: OriSensorEntityDescription

    @property
    def native_value(self) -> StateType | datetime:
        """Return the value reported by the sensor."""
        return self.entity_description.value_fn(self._device)
