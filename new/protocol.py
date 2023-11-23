""" Protocol.py

Ex : 2.6
Author : Michael Sokolov
Date : 23.11

"""

# import libraries
from datetime import datetime
import socket
import random
import logging

# Default values
PORT = 8822
HEADER_SIZE = 2  # 16-bits
VALID_COMMANDS = ["RAND", "NAME", "TIME", "EXIT"]

# configure logging
logging.basicConfig(filename='debugging.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def check_cmd(data):
    """Check if the command is defined in the protocol (e.g RAND, NAME, TIME, EXIT)"""

    if data in VALID_COMMANDS:
        return True

    return False


def create_request_msg(data):
    """Create a valid protocol message, will be sent by client, with length field"""

    length = len(data)
    if length < 10:
        length = "0" + str(length)

    return f"{length}{data}"


def create_response_msg(data):
    """Create a valid protocol message, will be sent by server, with length field"""
    res = "ErrorRespone"

    if data == "TIME":
        res = str(datetime.now())
    elif data == "NAME":
        res = str(socket.gethostname())
    elif data == "RAND":
        res = str(random.randint(1, 10))
    elif data == "EXIT":
        res = "Bye"

    length = len(res)
    if length < 10:
        length = "0" + str(length)

    return f"{length}{res}"


def get_msg(my_socket: socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """

    buffer_size = int(my_socket.recv(2).decode())
    logging.info("Buffer size : {}".format(buffer_size))
    buffer = my_socket.recv(buffer_size).decode()
    logging.info("Buffer data : {}".format(buffer))

    return True, buffer


def write_to_log(msg):
    logging.info(msg)
    print(msg)
