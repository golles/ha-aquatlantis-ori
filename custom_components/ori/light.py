"""Aquatlantis Ori light."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGBW_COLOR,
    ColorMode,
    LightEntity,
    LightEntityDescription,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from aquatlantis_ori import AquatlantisOriClient, Device, DynamicModeType, LightOptions, ModeType, PowerType

from .entity import OriEntity, OriEntityDescription

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=2)

EFFECT_MANUAL = "manual"
EFFECT_AUTOMATIC = "automatic"
EFFECT_DYNAMIC = "dynamic"
EFFECT_LIST = [EFFECT_MANUAL, EFFECT_AUTOMATIC, EFFECT_DYNAMIC]


def _effect_name(device: Device) -> str:
    """Get the effect name for the device."""
    if device.mode == ModeType.AUTOMATIC:
        return EFFECT_AUTOMATIC
    if device.dynamic_mode == DynamicModeType.ON:
        return EFFECT_DYNAMIC

    return EFFECT_MANUAL


def _schedule(device: Device) -> dict[str, dict[str, int]] | None:
    """Get the light schedule for the device."""
    if device.timecurve is None:
        return None

    schedule: dict[str, dict[str, int]] = {}
    for curve in device.timecurve:
        schedule[f"{curve.hour:>02}:{curve.minute:>02}"] = {
            "intensity": curve.intensity,
            "red": curve.red,
            "green": curve.green,
            "blue": curve.blue,
            "white": curve.white,
        }

    return schedule


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
        state_attributes_fn=lambda device: {
            "light_mode": _effect_name(device),
            "schedule": _schedule(device),
        },
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

    def __init__(
        self,
        config_entry: ConfigEntry[AquatlantisOriClient],
        description: OriEntityDescription,
        device: Device,
    ) -> None:
        """Initialize light."""
        super().__init__(config_entry, description, device)
        self._attr_effect_list = EFFECT_LIST
        self._attr_supported_features |= LightEntityFeature.EFFECT

    def turn_on(self, **kwargs: Any) -> None:  # noqa: ANN401
        """Turn the entity on."""
        _LOGGER.info("Turning on, or changing light %s on device %s", self.entity_description.key, self._device.devid)
        options = LightOptions()

        if ATTR_EFFECT in kwargs:
            effect = kwargs[ATTR_EFFECT]
            if effect == EFFECT_MANUAL:
                self._device.set_mode(ModeType.MANUAL)
                self._device.set_dynamic_mode(DynamicModeType.OFF)
            elif effect == EFFECT_AUTOMATIC:
                self._device.set_mode(ModeType.AUTOMATIC)
                self._device.set_dynamic_mode(DynamicModeType.OFF)
                return  # No need to continue, automatic mode does not require RGBW settings and changing power
            elif effect == EFFECT_DYNAMIC:
                self._device.set_mode(ModeType.MANUAL)
                self._device.set_dynamic_mode(DynamicModeType.ON)

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
        self._device.set_mode(ModeType.MANUAL)
        self._device.set_power(PowerType.OFF)

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        return _effect_name(self._device)

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
        return self._device.is_light_on

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
