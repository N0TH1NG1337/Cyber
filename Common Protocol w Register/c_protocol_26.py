"""
    Protocol_26.py - protocol version 2.6 file

    last update : 05/04/2024
"""

#  region Libraries

from c_protocol import *

from datetime import datetime
import random


#  endregion


#  region Protocol Functions

def get_time() -> str:
    return str(datetime.now())


def get_name() -> str:
    return str(socket.gethostname())


def get_random() -> str:
    return str(random.randint(1, 10))


#  endregion


#  region Protocol 2.6

class c_protocol_26(c_protocol, ABC):

    def __init__(self):
        self._valid_cmds = {
            "TIME": get_time,
            "RAND": get_random,
            "NAME": get_name
        }

    def create_request(self, cmd: str, args: str, data: dir) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        return format_data(encrypt_data(cmd, data))

    def create_response(self, cmd: str, args: list, data: dir) -> str:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned
        """

        response = "None Supported CMD"

        if cmd in self._valid_cmds:
            response = self._valid_cmds[cmd]()

        write_to_log(f"  Protocol 2.6  · response : {response}")

        return format_data(encrypt_data(response, data))

    def get_cmds(self) -> list:
        """
            Returns valid cmds for Current Protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

#  endregion
