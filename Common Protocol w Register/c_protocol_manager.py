"""
    Protocol_Manager.py - protocol manager file

    last update : 05/04/2024
"""

#  region Libraries

from c_protocol import *

from c_protocol_26 import c_protocol_26
from c_protocol_27 import c_protocol_27, receive_photo
from c_protocol_db import c_protocol_db

#  endregion


#  region Protocol Manager

class c_protocol_manager(c_protocol, ABC):

    def __init__(self):

        self._protocols = {
            1: c_protocol_26(),
            2: c_protocol_27(),
            3: c_protocol_db()
        }

        self._last_error = ""

    def get_protocol_type(self, cmd: str) -> int:
        """
            Gets Protocol Enum based on cmd
        """

        if cmd == DISCONNECT_MSG:
            return 0

        if cmd in self._protocols[1].get_cmds():
            return 1

        if cmd in self._protocols[2].get_cmds():
            return 2

        if cmd in self._protocols[3].get_cmds():
            return 3

        return -1  # Failed

    def create_request(self, cmd: str, args: str, data: dir) -> any:
        """
            Creates a request message by formatting the command.
        """

        e_protocol_type = self.get_protocol_type(cmd)

        if e_protocol_type == -1:
            self._last_error = "Invalid Command"
            return None

        if e_protocol_type == 2 and args is None:
            self._last_error = "Invalid Arguments"
            return None

        if e_protocol_type == 0:
            # Our Disconnect Message need to be handled manually
            # Since there is no protocol that handles it

            return format_data(encrypt_data(DISCONNECT_MSG, data))

        value = self._protocols[e_protocol_type].create_request(cmd, args, data)

        return value

    def create_response(self, cmd: str, args: list, data: dir) -> any:
        """
            Create valid response information, will be sent by server,
            with length field. In case unsupported request "Non-supported cmd" will be sent back
        """

        e_protocol_type = self.get_protocol_type(cmd)

        if e_protocol_type == -1:
            self._last_error = "Invalid Command"
            return None

        if e_protocol_type == 2 and args is None:
            self._last_error = "Invalid Arguments"
            return None

        return self._protocols[e_protocol_type].create_response(cmd, args, data)

    def get_last_error(self) -> str:
        """
            Returns last error occurred
        """

        return self._last_error

    def call(self, name: str) -> any:
        """
            Returns Protocol Pointer based on version name
        """

        if name == "2.6":
            return self._protocols[1]

        if name == "2.7":
            return self._protocols[2]

        if name == "database":
            return self._protocols[3]

        return None

#  endregion