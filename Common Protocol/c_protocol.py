"""

Class Protocol  .py
- main protocol file

last update:    12/02/2024

"""

#  region Libraries

from abc import ABC, abstractmethod
from datetime import datetime
import subprocess
import pyautogui
import logging
import random
import shutil
import socket
import glob
import os

#  endregion

#  region Constants

VALID_COMMANDS_27 = ["DIR", "DELETE", "COPY", "EXECUTE", "TAKE_SCREENSHOT", "SEND_PHOTO"]
VALID_COMMANDS_26 = ["TIME", "RAND", "NAME"]
VALID_COMMANDS_REGISTER = ["REGISTER", "LOGIN"]
DISCONNECT_MSG = "EXIT"

LOG_FILE: str = "LogFile.log"
FORMAT: str = "utf-8"

PORT: int = 12345
BUFFER_SIZE: int = 1024
HEADER_SIZE = 4

#  endregion

#  Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', encoding=FORMAT)

#  region default protocol functions


def check_cmd(cmd: str) -> int:
    """
    Check for possible command,
    for every type of protocol,

    the int number of return is the type of command,
    and where it belongs
    """

    if cmd == DISCONNECT_MSG:
        return 0

    if cmd in VALID_COMMANDS_26:
        return 1

    if cmd in VALID_COMMANDS_27:
        return 2

    if cmd in VALID_COMMANDS_REGISTER:
        return 3

    return -1


def convert_data(buffer: str) -> (str, list):
    """
    convert received string to information
    """

    try:
        data = buffer.split(">")
        return data[0], data[1].strip('[]').split(",")
    except Exception as e:

        # In case our data is only a message without arguments
        return buffer, None


def receive_buffer(my_socket: socket) -> (bool, str):
    """
    Extracts a message from the socket and handles potential errors.
    """

    try:
        buffer_size = int(my_socket.recv(HEADER_SIZE).decode())
        logging.info("  Protocol  · Buffer size : {}".format(buffer_size))

        buffer = my_socket.recv(buffer_size).decode()
        logging.info("  Protocol  · Buffer data : {}".format(buffer))

        return True, buffer
    except Exception as e:

        # On buffer size convert fail
        return False, "Error"


def format_data(data: str) -> str:
    """
    Formats data by prepending its length with leading zeros.
    """

    data_length = len(data)
    num_str = str(data_length)
    padding = "0" * (HEADER_SIZE - len(num_str))

    return f"{padding + num_str}{data}"


def write_to_log(data):
    """
    Print and write to log data
    """
    logging.info(data)
    print(data)


#  endregion

#  region abstract class protocol
class c_protocol(ABC):

    @abstractmethod
    def create_request(self, cmd: str, args: str) -> str:
        """
        Creates a request message by formatting the command.
        """
        pass

    @abstractmethod
    def create_response(self, cmd: str, args: list, skt: socket) -> str:
        """
        Create valid response information, will be sent by server,
        with length field. In case unsupported request "Non-supported cmd" will be sent back
        """
        pass

#  endregion
