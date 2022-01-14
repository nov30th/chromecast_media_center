import logging

from homeassistant import core
from .const import *

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
    """Set up the Chromecast Media Center component."""
    # @TODO: Add setup code.

    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI/YAML."""
    config_entry.add_update_listener(update_listener)
    if config_entry.data is None:
        _LOGGER.error("NO CONFIGURATION OF CHROMECAST MEDIA CENTER!")
    else:
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][config_entry.entry_id] = {}

        for platform in PLATFORMS:
            hass.async_add_job(hass.config_entries.async_forward_entry_setup(config_entry, platform))
        return True


async def update_listener(hass, entry):
    """Update listener."""
    entry.data = entry.options
    for platform in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, platform)
        hass.async_add_job(hass.config_entries.async_forward_entry_setup(entry, platform))
