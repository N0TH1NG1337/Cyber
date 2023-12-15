"""
Protocol.py

author : 
date : 14.12
"""

# import libs
import socket
import random
import logging
from datetime import datetime

# Constants
DEFAULT_PORT: int = 8825  # Default port
BUFFER_SIZE: int = 1024
HEADER_SIZE: int = 2  # 16-bits
VALID_COMMANDS: list = ["RAND", "NAME", "TIME"]  # All possible commands
FORMAT: str = "utf-8"  # encode and decode format
DISCONNECT_MSG: str = "DISCONNECT"

# Configure logging
logging.basicConfig(filename="File_Log.log", level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def correct_length(data):
    """Correcting the data length,
        since the first digit numbers are only 1 char length,
        and we need to fill 2 chars """

    length = len(data)
    if length < 10:
        length = "0" + str(length)

    return length


def check_cmd(data):
    """Check if the command is defined in the protocol (e.g RAND, NAME, TIME, EXIT)"""

    if data in VALID_COMMANDS:
        return True

    return False


def create_request_msg(data):
    """Create a valid protocol message, will be sent by client, with length field"""

    length = correct_length(data)

    return f"{length}{data}"


def create_response_msg(data):
    """Create a valid protocol message, will be sent by server, with length field"""
    res = "ErrorResponse"

    if data == "TIME":
        res = str(datetime.now())
    elif data == "NAME":
        res = str(socket.gethostname())
    elif data == "RAND":
        res = str(random.randint(1, 10))
    else:
        res = data

    length = correct_length(res)

    return f"{length}{res}"


def get_msg(my_socket: socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """

    buffer_size = int(my_socket.recv(HEADER_SIZE).decode())
    logging.info("Buffer size : {}".format(buffer_size))

    buffer = my_socket.recv(buffer_size).decode()
    logging.info("Buffer data : {}".format(buffer))

    return True, buffer


def write_to_log(msg):
    """Prints data and logging it"""
    logging.info(msg)
    print(msg)
