"""Support for HOHO switches."""
from __future__ import annotations

import logging

from homeassistant.components.select import (SelectEntity, )
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import *
from .entity import HohoMediaCenterEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry,
                            async_add_entities: AddEntitiesCallback, ) -> None:
    """Set up the HohoMediaCenter playlist."""
    # device = hass.data[DOMAIN].devices[config_entry.entry_id]
    # noinspection PyListCreation
    selects: list[HohoMediaCenterEntity] = []

    selects.append(HohoMediaCenterPlaylistSelectEntity(config_entry))
    selects.append(HohoMediaCenterMediaPlayerSelectEntity(config_entry))

    async_add_entities(selects)


class HohoMediaCenterPlaylistSelectEntity(HohoMediaCenterEntity, SelectEntity):
    """Playlist Select Entity."""

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        # self.entity_description = "Music Folders"
        self._attr_name = "Playlist"
        self._attr_unique_id = ENTITY_PLAYLIST
        self._attr_icon = "mdi:cards-heart"
        self._attr_options = ["MP3", "Favorite"]

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""  # Raw value

    def select_option(self, option: str) -> None:
        """Change the selected option."""


class HohoMediaCenterMediaPlayerSelectEntity(HohoMediaCenterEntity, SelectEntity):
    """Playlist Select Entity."""

    def __init__(self, config_entry):
        """Initialize the switch."""
        super().__init__(config_entry)
        # self.entity_description = "Music Folders"
        self._attr_name = "Media Player"
        self._attr_unique_id = ENTITY_MEDIA_PLAYER
        self._attr_icon = "mdi:disc-player"
        self._attr_options = []

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""  # Raw value

    def select_option(self, option: str) -> None:
        """Change the selected option."""
