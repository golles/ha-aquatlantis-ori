"""The Aquatlantis Ori component."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from aquatlantis_ori import AquatlantisOriClient, AquatlantisOriError

from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SENSOR,
    Platform.UPDATE,
]


async def async_setup(hass: HomeAssistant, _config: ConfigType) -> bool:
    """Set up service actions."""
    async_setup_services(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry[AquatlantisOriClient]) -> bool:
    """Setup a config entry."""
    email = config_entry.data[CONF_EMAIL]
    password = config_entry.data[CONF_PASSWORD]
    client = AquatlantisOriClient(email, password, async_get_clientsession(hass))
    config_entry.runtime_data = client

    try:
        await client.connect()
        _LOGGER.debug("Waiting for devices to be ready...")
        # After connecting it takes a little bit of time (<0.5sec) for the device data to be fully populated.
        # While waiting isn't the best solution, this will make sure all sensors will have data available.
        # This is important so we can initialize the entities correctly, eg. light type.
        await client.wait_for_data(interval=0.2, max_wait=2)
        _LOGGER.debug("Devices are ready")
    except TimeoutError:
        _LOGGER.warning("Data wasn't available during setup, it should be available soon")
    except AquatlantisOriError as exception:
        raise ConfigEntryNotReady from exception

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry[AquatlantisOriClient]) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS):
        await config_entry.runtime_data.close()

    return unload_ok
