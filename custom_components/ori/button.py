"""Aquatlantis Ori button."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, PowerType

from .entity import OriEntity, OriEntityDescription

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0


@dataclass(kw_only=True, frozen=True)
class OriButtonEntityDescription(OriEntityDescription, ButtonEntityDescription):
    """Class describing Aquatlantis Ori button entities."""

    press_fn: Callable[[Device], None]


DESCRIPTIONS: list[OriButtonEntityDescription] = [
    OriButtonEntityDescription(
        key="custom1",
        translation_key="custom1",
        press_fn=lambda device: device.set_light(PowerType.ON, device.custom1),
        state_attributes_fn=lambda device: {
            "intensity": device.custom1.intensity if device.custom1 else None,
            "red": device.custom1.red if device.custom1 else None,
            "green": device.custom1.green if device.custom1 else None,
            "blue": device.custom1.blue if device.custom1 else None,
            "white": device.custom1.white if device.custom1 else None,
        },
    ),
    OriButtonEntityDescription(
        key="custom2",
        translation_key="custom2",
        press_fn=lambda device: device.set_light(PowerType.ON, device.custom2),
        state_attributes_fn=lambda device: {
            "intensity": device.custom2.intensity if device.custom2 else None,
            "red": device.custom2.red if device.custom2 else None,
            "green": device.custom2.green if device.custom2 else None,
            "blue": device.custom2.blue if device.custom2 else None,
            "white": device.custom2.white if device.custom2 else None,
        },
    ),
    OriButtonEntityDescription(
        key="custom3",
        translation_key="custom3",
        press_fn=lambda device: device.set_light(PowerType.ON, device.custom3),
        state_attributes_fn=lambda device: {
            "intensity": device.custom3.intensity if device.custom3 else None,
            "red": device.custom3.red if device.custom3 else None,
            "green": device.custom3.green if device.custom3 else None,
            "blue": device.custom3.blue if device.custom3 else None,
            "white": device.custom3.white if device.custom3 else None,
        },
    ),
    OriButtonEntityDescription(
        key="custom4",
        translation_key="custom4",
        press_fn=lambda device: device.set_light(PowerType.ON, device.custom4),
        state_attributes_fn=lambda device: {
            "intensity": device.custom4.intensity if device.custom4 else None,
            "red": device.custom4.red if device.custom4 else None,
            "green": device.custom4.green if device.custom4 else None,
            "blue": device.custom4.blue if device.custom4 else None,
            "white": device.custom4.white if device.custom4 else None,
        },
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori button entry."""
    entities: list[ButtonEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriButton(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriButton(OriEntity, ButtonEntity):
    """Representation of a Aquatlantis Ori button."""

    entity_description: OriButtonEntityDescription

    def press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Pressing button %s on device %s", self.entity_description.key, self._device.devid)
        self.entity_description.press_fn(self._device)
