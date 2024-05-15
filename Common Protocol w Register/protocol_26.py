"""
    c_protocol_26.py - Protocol Version 2.6 File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol import *
from utils import *

from datetime import datetime
import random

#  endregion


#  region @ Protocol Functions

def get_time() -> str:
    """
        Get current time
    """

    return str(datetime.now())


def get_name() -> str:
    """
        Get current host name
    """

    return str(socket.gethostname())


def get_random() -> str:
    """
        Get random number
    """

    return str(random.randint(1, 10))

#  endregion


#  region @ Protocol 2.6 Class

class c_protocol_26(c_protocol, ABC):

    def __init__(self):

        # Current protocol commands
        self._valid_cmds = {
            "TIME": get_time,
            "RAND": get_random,
            "NAME": get_name
        }

    def create_request(self, cmd: str, args: str, data: dict) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        cmd = c_encryption(data).encrypt(cmd).decode()  # encrypt cmd request

        return c_protocol.format_value(cmd)

    def create_response(self, cmd: str, args: list, data: dict) -> str:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        # Default invalid response
        response = "None Supported CMD"

        # Check and get response based on command
        if cmd in self._valid_cmds:
            response = self._valid_cmds[cmd]()

        # Log before encryption
        write_to_log(f"  Protocol 2.6  - response : {response}")

        # Return formatted and encrypted response
        return c_protocol.format_value(c_encryption(data).encrypt(response).decode())

    def get_cmds(self) -> list:
        """
            Returns valid cmds for current protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

#  endregion
