"""Support for HOHO switches."""
from __future__ import annotations

import logging
from abc import ABC

from homeassistant.components.switch import (SwitchDeviceClass, SwitchEntity, )
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (STATE_ON, )
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from .const import *
from .entity import HohoMediaCenterEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback, ) -> None:
    """Set up the HohoMediaCenter switch."""
    # device = hass.data[DOMAIN].devices[config_entry.entry_id]
    # noinspection PyListCreation
    switches: list[HohoMediaCenterEntity] = []

    switches.append(HohoMediaCenterPowerSwitch(config_entry))
    switches.append(HohoMediaCenterFavoriteSwitch(config_entry))
    switches.append(HohoMediaCenterDeleteSwitch(config_entry))
    switches.append(HohoMediaCenterShuffleMusicSwitch(config_entry))
    async_add_entities(switches)


class HohoMediaCenterPowerSwitch(HohoMediaCenterEntity, SwitchEntity, RestoreEntity, ABC):
    """Representation of a HohoMediaCenter switch."""

    _attr_assumed_state = False
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        # self._attr_name = f"{device.name} Power"
        self._attr_name = "HOHO Chromecast Media Power"
        self._attr_unique_id = SWITCH_POWER
        self._attr_icon = "mdi:play"

    async def async_added_to_hass(self):
        """Call when the switch is added to hass."""
        state = await self.async_get_last_state()
        self._attr_is_on = state is not None and state.state == STATE_ON
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        # if await self._async_send_packet(self._command_on):
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        # if await self._async_send_packet(self._command_off):
        self._attr_is_on = False
        self.async_write_ha_state()


class HohoMediaCenterFavoriteSwitch(HohoMediaCenterEntity, SwitchEntity, RestoreEntity, ABC):
    """Representation of a HohoMediaCenter switch."""

    _attr_assumed_state = False
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        self._attr_name = "Favorite Song"
        self._attr_unique_id = SWITCH_FAVORITE
        self._attr_icon = "mdi:cards-heart"

    async def async_added_to_hass(self):
        """Call when the switch is added to hass."""
        state = await self.async_get_last_state()
        self._attr_is_on = state is not None and state.state == STATE_ON
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        # if await self._async_send_packet(self._command_on):
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        # if await self._async_send_packet(self._command_off):
        self._attr_is_on = False
        self.async_write_ha_state()


class HohoMediaCenterDeleteSwitch(HohoMediaCenterEntity, SwitchEntity, RestoreEntity, ABC):
    """Representation of a HohoMediaCenter switch."""

    _attr_assumed_state = False
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        self._attr_name = "Delete Song"
        self._attr_unique_id = SWITCH_DELETE
        self._attr_icon = "mdi:delete"

    async def async_added_to_hass(self):
        """Call when the switch is added to hass."""
        state = await self.async_get_last_state()
        self._attr_is_on = state is not None and state.state == STATE_ON
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        # if await self._async_send_packet(self._command_on):
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        # if await self._async_send_packet(self._command_off):
        self._attr_is_on = False
        self.async_write_ha_state()


class HohoMediaCenterShuffleMusicSwitch(HohoMediaCenterEntity, SwitchEntity, RestoreEntity, ABC):
    """Representation of a HohoMediaCenter switch."""

    _attr_assumed_state = False
    _attr_device_class = SwitchDeviceClass.SWITCH

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        self._attr_name = "Shuffle Music"
        self._attr_unique_id = SWITCH_SHUFFLE
        self._attr_icon = "mdi:shuffle-variant"

    async def async_added_to_hass(self):
        """Call when the switch is added to hass."""
        state = await self.async_get_last_state()
        self._attr_is_on = state is not None and state.state == STATE_ON
        await super().async_added_to_hass()

    async def async_turn_on(self, **kwargs):
        """Turn on the switch."""
        # if await self._async_send_packet(self._command_on):
        self._attr_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn off the switch."""
        # if await self._async_send_packet(self._command_off):
        self._attr_is_on = False
        self.async_write_ha_state()
