"""
    c_protocol_manager.py - Protocol Manager File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol import *
from utils import *

from protocol_26 import c_protocol_26
from protocol_27 import c_protocol_27, receive_photo
from protocol_db import c_protocol_db

#  endregion


#  region @ Protocol Manager Class

class c_protocol_manager(c_protocol, ABC):

    def __init__(self):

        # Protocols list based on numbers
        self._protocols = {
            1: c_protocol_26(),
            2: c_protocol_27(),
            3: c_protocol_db()
        }

        # Protocol names and their numbers
        self._protocols_names = {
            "2.6": 1,
            "2.7": 2,
            "database": 3
        }

        self._last_error: str = ""

    def get_protocol_type(self, cmd: str) -> int:
        """
            Gets protocol enum based on command
        """

        if cmd == DISCONNECT_MSG or cmd == HELP_CMD_MSG:
            return 0

        for i in range(3):
            protocol_index = i + 1

            if cmd in self._protocols[protocol_index].get_cmds():
                return protocol_index

        return -1  # fail

    def create_request(self, cmd: str, args: str, data: dict) -> any:
        """
            Creates a request message by formatting the command.
        """

        # Get protocol type
        e_protocol_type = self.get_protocol_type(cmd)

        if e_protocol_type == -1:
            self._last_error = "Invalid Command"
            return None

        if e_protocol_type == 2 and args is None:
            self._last_error = "Invalid Arguments"
            return None

        if e_protocol_type == 0:
            # Our Disconnect / Help Message need to be handled manually
            # Since there is no protocol that handles it
            cmd = c_encryption(data).encrypt(cmd).decode()

            return c_protocol.format_value(cmd)

        # Use correct protocol to create a request based on type
        value = self._protocols[e_protocol_type].create_request(cmd, args, data)

        # Return the request
        return value

    def create_response(self, cmd: str, args: list, data: dict) -> any:
        """
            Create valid response information, will be sent by server,
            with length field. In case unsupported request "Non-supported cmd" will be sent back
        """

        # Get protocol type
        e_protocol_type = self.get_protocol_type(cmd)

        # Some checks
        if e_protocol_type == -1:
            self._last_error = "Invalid Command"
            return None

        if e_protocol_type == 2 and args is None:
            self._last_error = "Invalid Arguments"
            return None

        if e_protocol_type == 0:
            # Help Msg - since Disconnect MSG is handled before this call
            result = "Possible commands :\n"

            # TODO !
            result = result + "\n".join(self.get_cmds())

            result = c_encryption(data).encrypt(result).decode()
            return c_protocol.format_value(result)

        # Return a ready to send response message
        return self._protocols[e_protocol_type].create_response(cmd, args, data)

    def get_cmds(self) -> any:
        """
            Returns valid cmds for every protocol.

            Note ! Return Dict
        """

        result = {}

        for name in self._protocols_names:
            protocol_index = self._protocols_names[name]

            result[name] = self._protocols[protocol_index].get_cmds()

        return result

    def __call__(self, index) -> any:

        if index in self._protocols_names:
            return self._protocols[self._protocols_names[index]]

        if index == "last_error":
            return self._last_error

        return None

#  endregion

