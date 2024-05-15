"""
    c_protocol.py - General Protocol File

    last update : 15/05/2024
"""

#  region @ Libraries

from abc import ABC, abstractmethod

import logging
import socket

#  endregion


#  region @ Constants

DISCONNECT_MSG = "EXIT"     # Default Exit Msg
HELP_CMD_MSG = "HELP"       # Default Help with commands Msg
SUCCESS_CMD = "success"     # Default Login/Register success CMD

LOG_FILE: str = "LogFile.log"  # Log File Name
FORMAT: str = "utf-8"          # Format

DEFAULT_PORT: int = 8822    # Default Port Number
BUFFER_SIZE: int = 1024     # Default full Buffer Read Size
HEADER_SIZE: int = 4        # Template Header Size

logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(message)s')

#  endregion


#  region @ Common Functions

def write_to_log(message: any):
    """
        Write to log file and print
    """

    logging.info(message)
    print(message)

#  endregion


#  region @ Protocol Class

class c_protocol(ABC):

    @abstractmethod
    def create_request(self, cmd: str, args: str, data: dict) -> str:  # Virtual Function
        """
            Creates a request message by formatting the command and arguments.
        """

        pass

    @abstractmethod
    def create_response(self, cmd: str, args: list, data: dict) -> str:  # Virtual Function
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        pass

    @abstractmethod
    def get_cmds(self) -> any:  # Virtual Function
        """
            Returns valid cmds for current protocol
        """

        pass

    @staticmethod
    def format_value(value: str) -> str:
        """
            Formats ant string type Value into format

            [4 bytes length][value]
        """

        return f"{len(value):04d}{value}"

    @staticmethod
    def parse(raw: str) -> any:
        """
            Parse raw data into information,

            1 option : cmd with arguments
            2 option : just cmd
            3 option : (like option 2) anything without arguments
        """

        try:

            data_list = raw.split(">")  # Command > Arguments

            # Now we assume that we have arguments attached
            cmd = data_list[0]

            # Try to get the arguments
            args = data_list[1].strip('[]').split(",")

            return cmd, args

        except Exception:

            # On fail / If we have only command
            return raw, None

    @staticmethod
    def get_raw_from_buffer(socket_obj: socket) -> (bool, str):
        """
            Pop from the buffer information
            Return false on error / fail
        """

        # Just in case
        if socket_obj is None:
            return False, ""

        try:
            # Timeout, lower number for more frequent 'updates'
            socket_obj.settimeout(10)

            # Get current data size
            buffer_size = int(socket_obj.recv(HEADER_SIZE).decode())
            logging.info(f"  Protocol      - Buffer Size : {buffer_size}")

            # Receive the data based on size
            raw_buffer = socket_obj.recv(buffer_size).decode()
            logging.info(f"  Protocol      - Buffer Raw : {raw_buffer}")

            # Return True as Result and the data we got
            return True, raw_buffer

        except Exception as e:

            # Failed / Timeout
            return False, str(e)

#  endregion
