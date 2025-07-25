"""Aquatlantis Ori light."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_RGBW_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, DynamicModeType, LightOptions, ModeType, PowerType

from .entity import OriEntity, OriEntityDescription

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=2)


def _convert_255_to_100(value: int) -> int:
    """Convert value from 0-255 range to 0-100 range."""
    return round((value * 100) / 255)


def _convert_100_to_255(value: int) -> int:
    """Convert value from 0-100 range to 0-255 range."""
    return round((value * 255) / 100)


@dataclass(kw_only=True, frozen=True)
class OriLightEntityDescription(OriEntityDescription, LightEntityDescription):
    """Class describing Aquatlantis Ori light entities."""


DESCRIPTIONS: list[OriLightEntityDescription] = [
    OriLightEntityDescription(
        key="light",
        translation_key="light",
    ),
]


async def async_setup_entry(
    _hass: HomeAssistant,
    config_entry: ConfigEntry[AquatlantisOriClient],
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up a Aquatlantis Ori light entry."""
    entities: list[LightEntity] = []

    client = config_entry.runtime_data

    for device in client.get_devices():
        entities.extend(
            [
                OriLightEntity(
                    config_entry,
                    description,
                    device,
                )
                for description in DESCRIPTIONS
                if description.is_supported_fn(device)
            ]
        )

    async_add_entities(entities)


class OriLightEntity(OriEntity, LightEntity):
    """Representation of a Aquatlantis Ori light."""

    entity_description: OriLightEntityDescription

    def turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity on."""
        _LOGGER.info("Turning on, or changing light %s on device %s", self.entity_description.key, self._device.devid)
        options = LightOptions()

        if ATTR_RGBW_COLOR in kwargs:
            rgbw = kwargs[ATTR_RGBW_COLOR]
            options.red = _convert_255_to_100(rgbw[0])
            options.green = _convert_255_to_100(rgbw[1])
            options.blue = _convert_255_to_100(rgbw[2])
            options.white = _convert_255_to_100(rgbw[3])
        if ATTR_BRIGHTNESS in kwargs:
            options.intensity = _convert_255_to_100(kwargs.get(ATTR_BRIGHTNESS, 0))

        self._device.set_light(PowerType.ON, options)

    def turn_off(self, **_kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity off."""
        _LOGGER.info("Turning off light %s on device %s", self.entity_description.key, self._device.devid)
        self._device.set_power(PowerType.OFF)

    @property
    def color_mode(self) -> ColorMode | str | None:
        """Return the color mode of the light."""
        if self._device.mode == ModeType.AUTOMATIC or self._device.dynamic_mode == DynamicModeType.ON:
            # If the device is in automatic mode or dynamic mode is on, it only supports ON/OFF
            return ColorMode.ONOFF
        return ColorMode.RGBW

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        """Flag supported color modes."""
        if self._device.mode == ModeType.AUTOMATIC or self._device.dynamic_mode == DynamicModeType.ON:
            # If the device is in automatic mode or dynamic mode is on, it only supports ON/OFF
            return {ColorMode.ONOFF}
        return {ColorMode.RGBW}

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._device.power == PowerType.ON or self._device.mode == ModeType.AUTOMATIC

    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        intensity = getattr(self._device, "intensity", 0)

        return _convert_100_to_255(intensity)

    @property
    def rgbw_color(self) -> tuple[int, int, int, int] | None:
        """Return the rgbw color value [int, int, int, int]."""
        red = getattr(self._device, "red", 0)
        green = getattr(self._device, "green", 0)
        blue = getattr(self._device, "blue", 0)
        white = getattr(self._device, "white", 0)

        return (
            _convert_100_to_255(red),
            _convert_100_to_255(green),
            _convert_100_to_255(blue),
            _convert_100_to_255(white),
        )
