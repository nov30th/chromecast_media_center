import logging
import os
from typing import Any, Dict, Optional

import requests as req
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from .const import *
from .hoho_smb import HohoSmbUtil

_LOGGER = logging.getLogger(__name__)

HOHO_DEFAULT_CONF_DICT = {"speaker": "media_player.home_group", "cover_temp_file_path": "config/www1",
                          "cover_temp_file_url": "http://127.0.0.1:8123/local1", "file_exts_filter": "mp3;flac",
                          "fix_ha_media_player": True, "rich_info_support": True,
                          "reset_ordered_index_once_stop_playing": True, "shuffle": True, "netbios": "HOSTNAME",
                          "ip_address": "IP", "username": "USER", "password": "PWD", "root_folder": "FOLDER NAME",
                          "path": "/", }


def fillEmptyFields(source: Dict):
    for key in HOHO_DEFAULT_CONF_DICT.keys():
        if key not in source.keys():
            source[key] = HOHO_DEFAULT_CONF_DICT[key]


class UserInputUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def page1(data: Dict, media_players: Dict) -> Dict:
        result = {vol.Required(CONF_RECEIVER, default=data[CONF_RECEIVER]): vol.In(media_players),
                  vol.Required(CONF_ALBUM_COVER_TEMP_FILE, default=data[CONF_ALBUM_COVER_TEMP_FILE], ): str,
                  vol.Required(CONF_ALBUM_COVER_TEMP_URL, default=data[CONF_ALBUM_COVER_TEMP_URL], ): str,
                  vol.Required(CONF_FILE_EXTS_FILTER, default=data[CONF_FILE_EXTS_FILTER]): str,
                  vol.Required(CONF_BOOL_FIX_HA_MEDIA_PLAYER,
                               default=data[CONF_BOOL_FIX_HA_MEDIA_PLAYER], ): vol.Coerce(bool),
                  vol.Required(CONF_BOOL_RICH_INFO_SUPPORT, default=data[CONF_BOOL_RICH_INFO_SUPPORT], ): vol.Coerce(
                      bool), vol.Required(CONF_BOOL_RESET_ORDERED_INDEX_ONCE_STOP_PLAYING,
                                          default=data[CONF_BOOL_RESET_ORDERED_INDEX_ONCE_STOP_PLAYING], ): vol.Coerce(
                bool), vol.Required(CONF_BOOL_SHUFFLE, default=data[CONF_BOOL_SHUFFLE]): vol.Coerce(bool), }
        return result

    @staticmethod
    def page2(data: Dict) -> Dict:
        result = {vol.Required(CONF_NETBIOS, default=data[CONF_NETBIOS]): str,
                  vol.Required(CONF_IP_ADDR, default=data[CONF_IP_ADDR], ): str,
                  vol.Required(CONF_USERNAME, default=data[CONF_USERNAME], ): str,
                  vol.Required(CONF_PASSWORD, default=data[CONF_PASSWORD]): str,
                  vol.Required(CONF_ROOT_FOLDER, default=data[CONF_ROOT_FOLDER]): str,
                  vol.Required(CONF_PATH, default=data[CONF_PATH]): str, }
        return result


class HohoChromecastMediaCenterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def get_media_players(self):
        all_media_player = dict()
        all_entities = await self.hass.async_add_executor_job(self.hass.states.all)
        for e in all_entities:
            if e.entity_id.startswith("media_player."):
                all_media_player.update({e.entity_id: e.name})
        return all_media_player

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):

        data = HOHO_DEFAULT_CONF_DICT

        if self.hass.data.get(DOMAIN) is not None:
            return self.async_abort(reason="one_instance_only")

        return self.async_show_form(step_id="hoho",
                                    data_schema=vol.Schema(UserInputUtils.page1(data, await self.get_media_players())))

    async def async_step_hoho(self, user_input=None, error=None):
        fillEmptyFields(user_input)
        if not os.path.exists(user_input[CONF_ALBUM_COVER_TEMP_FILE]):
            os.mkdir(user_input[CONF_ALBUM_COVER_TEMP_FILE])
        if not os.path.exists(user_input[CONF_ALBUM_COVER_TEMP_FILE]):
            _LOGGER.warning("local path does not exist.")
            return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                UserInputUtils.page1(user_input, await self.get_media_players())), errors={"base": "path_not_exist"})
        _LOGGER.info("local path exist, next step...")
        try:
            _LOGGER.info("writing file to local path testing...")
            content = await self.testing_mapping(user_input[CONF_ALBUM_COVER_TEMP_FILE],
                                                 user_input[CONF_ALBUM_COVER_TEMP_URL])
            _LOGGER.info("got response from web address, verifying...")
            if content != "TESTING":
                _LOGGER.warning("content different! verifying failed! got %s", content)
                return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                    UserInputUtils.page1(user_input, await self.get_media_players())),
                                            errors={"base": "mapping_incorrect"})
        except Exception as err:
            _LOGGER.error(err)
            return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                UserInputUtils.page1(user_input, await self.get_media_players())),
                                        errors={"base": "path_or_web-address_incorrect"})
        return self.async_show_form(step_id="smb", data_schema=vol.Schema(UserInputUtils.page2(user_input)), )

    async def async_step_smb(self, user_input=None):
        fillEmptyFields(user_input)
        _LOGGER.info("verify SMB...")
        result = HohoSmbUtil.test_connection(user_input[CONF_NETBIOS], user_input[CONF_IP_ADDR],
                                             user_input[CONF_USERNAME], user_input[CONF_PASSWORD],
                                             user_input[CONF_ROOT_FOLDER], user_input[CONF_PATH], )
        if result != "success":
            _LOGGER.error("verify SMB error:%s", result)
            errors: Dict[str, str] = {"base": result}
            return self.async_show_form(step_id="smb", data_schema=vol.Schema(UserInputUtils.page2(user_input)),
                                        errors=errors, )
        _LOGGER.info("verify SMB success")
        return self.async_create_entry(title="Hoho Media Center", data=user_input)

    async def testing_mapping(self, local: str, remote: str) -> str:
        file_test = open(local + "/HohoMediaWriteableTest.txt", "w")
        file_test.write("TESTING")
        file_test.close()
        _LOGGER.info("file wrote done, testing web http address mapping...")
        resp = await self.hass.async_add_executor_job(req.get, remote + "/HohoMediaWriteableTest.txt")
        os.remove(local + "/HohoMediaWriteableTest.txt")
        return resp.content.decode('utf-8')

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
        self.data = HOHO_DEFAULT_CONF_DICT
        self.data.update(config_entry.data.items())

    async def get_media_players(self):
        all_media_player = dict()
        all_entities = await self.hass.async_add_executor_job(self.hass.states.all)
        for e in all_entities:
            if e.entity_id.startswith("media_player."):
                all_media_player.update({e.entity_id: e.name})
        return all_media_player

    async def async_step_init(self, user_input=None):
        """Manage the options."""

        all_media_player: Dict = dict()
        all_entities = await self.hass.async_add_executor_job(self.hass.states.all)
        for e in all_entities:
            if e.entity_id.startswith("media_player."):
                all_media_player.update({e.entity_id: e.name})

        if len(all_media_player) > 0 and self.data[CONF_RECEIVER] not in all_media_player.keys():
            _LOGGER.warning("Old media player %s not found, please re-select.", self.data[CONF_RECEIVER], )
            self.data[CONF_RECEIVER] = all_media_player[0].value

        return self.async_show_form(step_id="hoho",
                                    data_schema=vol.Schema(UserInputUtils.page1(self.data, all_media_player)), )

    async def async_step_hoho(self, user_input=None):
        self.data.update(user_input.items())
        if not os.path.exists(self.data[CONF_ALBUM_COVER_TEMP_FILE]):
            os.mkdir(self.data[CONF_ALBUM_COVER_TEMP_FILE])
        if not os.path.exists(self.data[CONF_ALBUM_COVER_TEMP_FILE]):
            _LOGGER.warning("local path does not exist.")
            return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                UserInputUtils.page1(self.data, await self.get_media_players())), errors={"base": "path_not_exist"})
        _LOGGER.info("local path exist, next step...")
        try:
            _LOGGER.info("writing file to local path testing...")
            content = await self.testing_mapping(self.data[CONF_ALBUM_COVER_TEMP_FILE],
                                                 self.data[CONF_ALBUM_COVER_TEMP_URL])
            _LOGGER.info("got response from web address, verifying...")
            if content != "TESTING":
                _LOGGER.warning("content different! verifying failed! got %s", content)
                return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                    UserInputUtils.page1(self.data, await self.get_media_players())),
                                            errors={"base": "mapping_incorrect"})
        except Exception as err:
            _LOGGER.error(err)
            return self.async_show_form(step_id="hoho", data_schema=vol.Schema(
                UserInputUtils.page1(self.data, await self.get_media_players())),
                                        errors={"base": "path_or_web-address_incorrect"})
        return self.async_show_form(step_id="smb", data_schema=vol.Schema(UserInputUtils.page2(self.data)), )

    async def testing_mapping(self, local: str, remote: str) -> str:
        file_test = open(local + "/HohoMediaWriteableTest.txt", "w")
        file_test.write("TESTING")
        file_test.close()
        _LOGGER.info("file wrote done, testing web http address mapping...")
        resp = await self.hass.async_add_executor_job(req.get, remote + "/HohoMediaWriteableTest.txt")
        os.remove(local + "/HohoMediaWriteableTest.txt")
        return resp.content.decode('utf-8')

    async def async_step_smb(self, user_input=None):
        self.data.update(user_input.items())
        _LOGGER.info("verify SMB...")
        result = HohoSmbUtil.test_connection(self.data[CONF_NETBIOS], self.data[CONF_IP_ADDR], self.data[CONF_USERNAME],
                                             self.data[CONF_PASSWORD], self.data[CONF_ROOT_FOLDER],
                                             self.data[CONF_PATH], )
        if result != "success":
            _LOGGER.error("verify SMB error:%s", result)
            errors: Dict[str, str] = {"base": result}
            return self.async_show_form(step_id="smb", data_schema=vol.Schema(UserInputUtils.page2(self.data)),
                                        errors=errors, )
        _LOGGER.info("verify SMB success")
        return self.async_create_entry(title="Hoho Media Center", data=self.data)
