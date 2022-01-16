"""Support for HOHO related things."""
import logging
import os.path
from typing import List

from smb.SMBConnection import NotConnectedError
from smb.SMBConnection import SMBConnection

from .ncmdump import dump

# noinspection PyBroadException
_LOGGER = logging.getLogger(__name__)


class HohoSmbUtil:
    def __init__(self, netbios: str, ip: str, username: str, password: str, root_folder: str, path: str) -> None:
        self._netbios = netbios
        self._ip = ip
        self._username = username
        self._password = password
        self._root_folder = root_folder
        self._path = path
        self._conn = SMBConnection(self._username, self._password, "HohoChromecastMediaCenter", self._netbios)
        self._conn.connect(self._ip)

    @staticmethod
    def test_connection(netbios: str, ip: str, username: str, password: str, root_folder: str, path: str) -> str:
        conn = SMBConnection(username, password, "HohoChromecastMediaCenter", netbios)
        try:
            conn.connect(ip)
            if not conn.auth_result:
                return "pwd_error"
            try:
                files = conn.listPath(root_folder, path)
                if len(files) == 0:
                    return "no_files"
            except Exception as err:
                return "path_error"
        except NotConnectedError as err:
            return "unable_to_connect_or_netbios_name_error"
        except Exception as err:
            return "unknown"
        finally:
            if conn is not None and conn.has_authenticated:
                conn.close()
        return "success"

    def findNcmFiles(self) -> List[str]:
        conn = SMBConnection(self._username, self._password, "HohoChromecastMediaCenter", self._netbios)
        conn.connect(self._ip)
        return self.findNcmFilesLoop(self._path)

    def findNcmFilesLoop(self, folder: str) -> List[str]:
        files = self._conn.listPath(self._root_folder, folder)
        if not folder.endswith("/") and not folder.endswith("\\"):
            folder = folder + "\\"
        ret_val: List[str] = []
        for file in files:
            if file.filename == "." or file.filename == ".." or file is None or file.filename is None:
                continue
            if file.isDirectory:
                sub_files = self.findNcmFilesLoop(folder + file.filename)
                ret_val.extend(sub_files)
            else:
                file_name: str = file.filename
                full_file_name: str = folder + file_name
                if file_name.endswith(".ncm"):
                    ret_val.append(folder + file_name)
        return ret_val

    def convertAndUpdate(self, files: List[str], temp_folder: str):
        path_mp3 = temp_folder + "/" + 'hoho_chromecast_temp.mp3'
        path_flac = temp_folder + "/" + 'hoho_chromecast_temp.flac'
        if os.path.exists(path_mp3):
            os.remove(path_mp3)
        if os.path.exists(path_flac):
            os.remove(path_flac)
        for file in files:
            temp_file_name = temp_folder + "/" + 'hoho_chromecast_temp.ncm'
            _LOGGER.info("downloading %s for converting...", file)
            with open(temp_file_name, 'wb') as fp:
                self._conn.retrieveFile(self._root_folder, file, fp)
            dump(temp_file_name, )
            _LOGGER.info("file %s converted locally.", file)
            if os.path.exists(path_mp3):
                with open(path_mp3, 'rb') as fp:
                    renamed_file_name = file.replace(".ncm", ".mp3")
                    _LOGGER.info("file %s converted to mp3 file, uploading and delete ncm file...", file)
                    self._conn.storeFile(self._root_folder, renamed_file_name, fp, 120)
                    self._conn.deleteFiles(self._root_folder, file)
                    _LOGGER.info("file %s uploaded.", renamed_file_name)
                    os.remove(path_mp3)
            if os.path.exists(path_flac):
                with open(path_flac, 'rb') as fp:
                    renamed_file_name = file.replace(".ncm", ".flac")
                    _LOGGER.info("file %s converted to mp3 file, uploading and delete ncm file...", file)
                    self._conn.storeFile(self._root_folder, renamed_file_name, fp, 120)
                    self._conn.deleteFiles(self._root_folder, file)
                    _LOGGER.info("file %s uploaded.", renamed_file_name)
                    os.remove(path_flac)
