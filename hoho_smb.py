"""Support for HOHO related things."""
from smb.SMBConnection import NotConnectedError
from smb.SMBConnection import SMBConnection


# noinspection PyBroadException
class HohoSmbUtil:
    def __init__(self) -> None:
        pass

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
