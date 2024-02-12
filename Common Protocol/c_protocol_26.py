"""

Protocol 2.6    .py

last update:    12/02/2024

"""

#  region Libraries

from c_protocol import *

#  endregion


#  region class protocol

class c_protocol_26(c_protocol, ABC):

    def __init__(self):
        super().__init__()

    def create_request(self, cmd: str, args: str = None) -> str:
        """
        Creates a request message by formatting the command.
        """
        return format_data(cmd)

    def create_response(self, cmd: str, args: list = None, skt: socket = None) -> str:
        """
        Create valid response information, will be sent by server,
        with length field. In case unsupported request "Non-supported cmd" will be sent back
        """
        response = "None Supported CMD"

        valid_cmds = {
            "TIME": self._get_time,
            "RAND": self._get_random,
            "NAME": self._get_name
        }

        if cmd in valid_cmds:
            response = valid_cmds[cmd]()

        write_to_log(f"  Protocol 2.6  · response to client : {response} ")

        return format_data(response)

    def _get_time(self) -> str:
        return str(datetime.now())

    def _get_name(self) -> str:
        return str(socket.gethostname())

    def _get_random(self) -> str:
        return str(random.randint(1, 10))

#  endregion
