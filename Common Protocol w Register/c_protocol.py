"""
    Protocol.py - general protocol file

    last update : 05/04/2024
"""

#  region Libraries

from cryptography.fernet import Fernet
from abc import ABC, abstractmethod

import logging
import shutil
import socket

#  endregion


#  region Constants

DISCONNECT_MSG = "EXIT"  # Default Exit Msg

LOG_FILE: str = "LogFile.log"  # Log File Name
FORMAT: str = "utf-8"  # Format

PORT: int = 12345  # Default Port
BUFFER_SIZE: int = 1024  # Default full Buffer Read Size
HEADER_SIZE = 4  # Template Header Size

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(message)s')

#  endregion


#  region Common Functions

def format_data(data: str) -> str:
    """
        Formats raw string into template for protocols,
        [DataLength][Raw_Data],

        This way is much better to extract later the data from the buffer
    """

    return f"{len(data):04d}{data}"


def receive_raw_buffer(socket_obj: socket) -> (bool, str):
    """
        Pop from the Buffer Information,
        Return False on error / fail
    """

    if socket_obj is None:
        return False, ""

    try:
        socket_obj.settimeout(10)

        buffer_size = int(socket_obj.recv(HEADER_SIZE).decode())
        logging.info(f"  Protocol  · Buffer Size : {buffer_size}")

        raw_buffer = socket_obj.recv(buffer_size).decode()
        logging.info(f"  Protocol  · Buffer Raw : {raw_buffer}")

        return True, raw_buffer

    except socket.timeout:

        return False, "socket_timeout"

    except Exception as e:

        return False, e


def parse_data(raw_data: str) -> any:
    """
        Parse raw data into information,

        1 option : cmd with arguments
        2 option : just cmd
        3 option : (like option 2) anything without arguments
    """

    try:

        data_list = raw_data.split(">")  # CMD > Args

        # Now we assume that we have arguments attached
        cmd = data_list[0]
        args = data_list[1].strip('[]').split(",")

        return cmd, args

    except Exception as e:

        return raw_data, None


def try_to_get_key(data: dir) -> any:
    """
        Will try to find the encryption key and return it
    """

    try:

        key = data["key"]
        return key

    except Exception as e:

        return None


def encrypt_data(to_change: str, data: dir) -> str:

    key = try_to_get_key(data)

    if key is None:
        return to_change

    return key.encrypt(to_change.encode()).decode()


def encrypt_bytes(to_change: bytes, data: dir) -> bytes:

    key = try_to_get_key(data)

    if key is None:
        return to_change

    return key.encrypt(to_change)


def decrypt_data(to_change: str, data: dir) -> str:

    key = try_to_get_key(data)

    if key is None:
        return to_change

    return key.decrypt(to_change.encode()).decode()


def decrypt_bytes(to_change: bytes, data: dir) -> bytes:

    key = try_to_get_key(data)

    if key is None:
        return to_change

    return key.decrypt(to_change)


def write_to_log(anything: any) -> None:
    """
        Log and Print any data we pass
    """

    print(anything)
    logging.info(anything)

#  endregion


#  region Abstract Class Protocol

class c_protocol(ABC):

    @abstractmethod
    def create_request(self, cmd: str, args: str, data: dir) -> str:  # Virtual Function
        """
            Creates a request message by formatting the command and arguments.
        """

        pass

    @abstractmethod
    def create_response(self, cmd: str, args: list, data: dir) -> str:  # Virtual Function
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        pass

#  endregion
