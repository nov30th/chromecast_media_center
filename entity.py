"""HOHO Media Center entities."""

from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN


class HohoMediaCenterEntity(Entity):
    """Representation of a Broadlink entity."""

    _attr_should_poll = False

    def __init__(self, config_entry):
        """Initialize the entity."""
        self._config_entry = config_entry
        self.config_entry = config_entry

    async def async_added_to_hass(self):
        """Call when the entity is added to hass."""
        # self.async_on_remove(self._coordinator.async_add_listener(self._recv_data))
        pass

    async def async_update(self):
        """Update the state of the entity."""
        # await self._coordinator.async_request_refresh()
        pass

    def _recv_data(self):
        """Receive data from the update coordinator.

        This event listener should be called by the coordinator whenever
        there is an update available.

        It works as a template for the _update_state() method, which should
        be overridden by child classes in order to update the state of the
        entities, when applicable.
        """
        # if self._coordinator.last_update_success:
        #     self._update_state(self._coordinator.data)
        self.async_write_ha_state()

    def _update_state(self, data):
        """Update the state of the entity.

        This method should be overridden by child classes in order to
        internalize state and attributes received from the coordinator.
        """

    @property
    def available(self):
        """Return True if the entity is available."""
        # return self._device.available
        return True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        config_entry = self._config_entry

        return DeviceInfo(  # connections={(dr.CONNECTION_NETWORK_MAC, device.mac_address)},
            identifiers={(DOMAIN, config_entry.domain)}, manufacturer="HOHO``", model="Chromecast Speakers",
            name="HOHO Chromecast Media Center", default_name="HOHO Chromecast Media Center", )
