"""
    Protocol    .py

    date :      06/03/2024

    TODO :

"""

#  region Libraries

from cryptography.fernet import Fernet
from abc import ABC, abstractmethod
from datetime import datetime
import subprocess
import pyautogui
import sqlite3
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
# Note ! encoding=FORMAT cause problem (worked before)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


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

    if my_socket is None:
        return False, ""

    try:
        # If I don't use this socket timeout
        # my server cannot receive the DISCONNECT_MSG,
        # and it's just getting stack
        my_socket.settimeout(10)

        buffer_size = int(my_socket.recv(HEADER_SIZE).decode())
        logging.info("  Protocol  · Buffer size : {}".format(buffer_size))

        buffer = my_socket.recv(buffer_size).decode()
        logging.info("  Protocol  · Buffer data : {}".format(buffer))

        return True, buffer

    except socket.timeout:
        return False, ""

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

#  region Abstract Class Protocol
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


#  region Protocol 2.6


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

    #  region class protocol functions

    def _get_time(self) -> str:
        return str(datetime.now())

    def _get_name(self) -> str:
        return str(socket.gethostname())

    def _get_random(self) -> str:
        return str(random.randint(1, 10))

    #  endregion


#  endregion


#  region Protocol 2.7


class c_protocol_27(c_protocol, ABC):

    def __init__(self):
        super().__init__()

    def create_request(self, cmd: str, args: str) -> str:
        """
        Creates a request message by formatting the command.
        """

        valid_value = check_cmd(cmd)
        request = (valid_value == 2 or valid_value == 0) and (cmd + ">" + args) or "Command not supported"
        return format_data(request)

    def create_response(self, cmd: str, args: list, skt: socket) -> str:
        """
        Create valid response information, will be sent by server,
        with length field. In case unsupported request "Non-supported cmd" will be sent back
        """

        response = "None Supported CMD"

        valid_cmds = {
            "DIR": self._dir_command,
            "DELETE": self._delete_command,
            "COPY": self._copy_command,
            "EXECUTE": self._execute_command,
            "TAKE_SCREENSHOT": self._screenshot_command,
            "SEND_PHOTO": self._send_photo_command,
        }

        if cmd in valid_cmds:
            response = valid_cmds[cmd](args, skt)

        write_to_log(f"  Protocol 2.7  · response to client : {response} ")

        return format_data(response)

    #  region class protocol functions

    def _dir_command(self, args: list, my_socket: socket) -> str:
        """
        get the list of files in a directory

        :param args: the directory to list
        :param my_socket: none since no need
        :return: a list of the files in the directory
        """

        current_dir: str = str(args[0]) + "\\" + "*.*"
        directory_list = glob.glob(current_dir)
        write_to_log(f"  Protocol  · prepare directory file list {directory_list} - {current_dir}")

        return str(", ".join(directory_list))

    def _delete_command(self, args: list, my_socket: socket) -> str:
        """
        delete the file

        :param args: the name of the file to delete
        :param my_socket: none since no need
        :return: result as a string
        """

        file_path = args[0]

        if os.path.exists(file_path):
            os.remove(file_path)
            return f"File {file_path} was deleted"

        return f"File {file_path} was not deleted"

    def _copy_command(self, args: list, my_socket: socket) -> str:
        """
        copy file to other path

        :param args: path of the file, path of the end location
        :param my_socket: none since no need
        :return: success or failure
        """

        file_path_from = args[0]
        file_path_for = args[1]

        if os.path.exists(file_path_from):
            shutil.copy(file_path_from, file_path_for)

            return f"Copy file from {file_path_from} to {file_path_for}"

        return f"Failed to copy file from {file_path_from}"

    def _execute_command(self, args: list, my_socket: socket) -> str:
        """
        run process / programm

        :param args: path and name of the executing program
        :param my_socket: none since no need
        :return: status as a string
        """

        file_path = args[0]

        res = subprocess.call(file_path)
        if res == 0:
            return file_path + " - successfully executed"

        return file_path + " - was not executed"

    def _screenshot_command(self, args: list, my_socket: socket) -> str:
        """
        take screenshot and saves it

        :param args: screenshot name
        :param my_socket: none since no need
        :return: successful
        """

        file_name = args[0]

        image = pyautogui.screenshot()
        image.save(file_name)

        if os.path.exists(file_name):
            return "Screenshot was taken"

        return "Failed to take screenshot"

    def _send_photo_command(self, args: list, my_socket: socket) -> str:
        """
        send photo file

        :param args: file name \ path
        :param my_socket: client socket to send to
        :return: nothing
        """

        file_name = args[0]

        try:
            # if second argument is invalid
            # we will get error
            new_file_name = args[1]
        except Exception as e:
            my_socket.send(format_data(f"PHOTO_INFORMATION>{-2}>{file_name}").encode(FORMAT))
            return ""

        if os.path.exists(file_name):
            # photo exist

            # Get file size
            file_size = os.path.getsize(file_name)

            # Send conformation for the client to wait for data
            my_socket.send(format_data(f"PHOTO_INFORMATION>{file_size}>{new_file_name}").encode(FORMAT))

            # Send the data
            with open(file_name, 'rb') as file:
                while True:
                    image_data = file.read(BUFFER_SIZE)
                    if not image_data:
                        break  # reached end of the file

                    my_socket.send(image_data)
        else:
            # photo doesn't exist
            # Send cancel to client
            my_socket.send(format_data(f"PHOTO_INFORMATION>{-1}>{file_name}").encode(FORMAT))

        return ""  # we just lose it since we don't need it

    def receive_photo(self, my_socket: socket, file_size: int, file_name: str):
        """
        receive photo from server

        :param my_socket: client socket to receive
        :param file_size: the waited file size
        :param file_name: new file name
        :return: successful or failure
        """

        try:
            my_socket.settimeout(10)  # Set a timeout

            # Receive the photo data in chunks based on file size
            received_data = b''
            while len(received_data) < file_size:
                data = my_socket.recv(min(file_size - len(received_data), BUFFER_SIZE))
                received_data += data

            # Write the received data to the file
            with open(file_name, 'wb') as file:
                file.write(received_data)

            if not os.path.exists(file_name):
                raise socket.timeout()

            return "Photo received"

        except socket.timeout:

            return "Photo couldn't be received"

    #  endregion


#  endregion


#  region Protocol Login


class c_protocol_login(c_protocol, ABC):

    def __init__(self):
        self._last_error = ""
        self._last_success = False

        self._create_table()

    def create_request(self, cmd: str, args: str) -> str:
        """
        Creates a request message by formatting the command.
        """

        req = f"{cmd}>{args}"
        return format_data(req)

    def create_response(self, cmd: str, args: list, skt: socket = None) -> str:
        """
        Create valid response information, will be sent by server,
        with length field. In case unsupported request "Non-supported cmd" will be sent back
        """

        # VALID_COMMANDS_REGISTER = ["REGISTER", "LOGIN"]
        response = "None Supported CMD"
        key = ""

        valid_cmds = {
            "REGISTER": self._register_user,
            "LOGIN": self._login_user
        }

        if cmd in valid_cmds:
            self._last_success, key = valid_cmds[cmd](args)

            if self._last_success:
                response = "user_successfully_logged_in"
            else:
                response = self._last_error

        write_to_log(f"  Protocol Login  · response to client : {response} ")

        return format_data(f"REGISTRATION_INFO>{response}>{key}")

    def _create_table(self):
        connection = sqlite3.connect("Users.db")
        cursor = connection.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        key TEXT NOT NULL);
        """)

        connection.commit()
        connection.close()

    def _register_user(self, information) -> (bool, str):

        connection = None
        success = False

        key = Fernet.generate_key().decode()

        try:
            connection = sqlite3.connect("Users.db")
            cursor = connection.cursor()

            cursor.execute("""
            INSERT INTO users (username, password, key) VALUES (?, ?, ?);
            """, (information[0], information[1], key))

            success = True
        except Exception as e:
            self._last_error = str(e)
            success = False

        if connection:
            connection.commit()
            connection.close()

        return success, key

    def _login_user(self, information) -> (bool, str):

        connection = None
        success = False
        received_key = ""

        try:
            connection = sqlite3.connect("Users.db")
            cursor = connection.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (information[0],))

            received_data = cursor.fetchone()

            if received_data:
                password_raw = received_data[2]
                if password_raw == information[1]:
                    received_key = received_data[3]
                    success = True
                else:
                    raise Exception("incorrect password")
            else:
                raise Exception("user not found")

        except Exception as e:
            self._last_error = str(e)
            success = False

        if connection:
            connection.close()

        return success, received_key

    def get_last_error(self):
        return self._last_error

    def get_last_success(self):
        return self._last_success


#  endregion


#  region Class Events
class c_event:

    def __init__(self, *args):
        self._events_handler = {}

        for event_name in list(args):
            self._events_handler[event_name] = {}

    def add_event(self, event_name):
        self._events_handler[event_name] = {}

    def register(self, event_name: str, function: any, function_name: str) -> bool:
        # function()

        self._events_handler[event_name][function_name] = function
        return True

    def unregister(self, event_name, function_name):
        pass

    def call_event(self, event_name: str, *args) -> bool:
        if not self._events_handler[event_name]:
            return False

        for name in self._events_handler[event_name]:
            self._events_handler[event_name][name](*args)

        return True

#  endregion
