"""
    c_protocol_27.py - Protocol Version 2.7 File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol import *
from utils import *

import subprocess
import pyautogui
import shutil
import glob
import os

#  endregion


#  region @ Protocol Utils

PHOTO_INFORMATION_COMMAND: str = "PHOTO_INFORMATION"


def dir_command(data: dict) -> str:
    """
        Get list of files in a specific path
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive path"

    current_dir: str = str(arguments[0]) + "\\" + "*.*"
    directory_list = glob.glob(current_dir)

    return str(", ".join(directory_list))


def delete_command(data: dict) -> str:
    """
        Delete a specific file
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    file_path = arguments[0]

    # Check if we have the file to delete
    if not os.path.exists(file_path):
        return f"File {file_path} was not deleted"

    # Delete it
    os.remove(file_path)

    # Check if it got deleted
    if not os.path.exists(file_path):
        return f"File {file_path} was deleted"

    return f"File {file_path} was not deleted"


def copy_command(data: dict) -> str:
    """
        Copy file from One path to other path
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    file_path_from = arguments[0]
    file_path_to = arguments[1]

    if os.path.exists(file_path_from):
        shutil.copy(file_path_from, file_path_to)

        return f"Copy file from {file_path_from} to {file_path_to}"

    return f"Failed to copy file from {file_path_from}"


def execute_command(data: dict) -> str:
    """
        Execute command
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    command = arguments[0]
    result = subprocess.call(command)

    if result == 0:
        return f"Failed to execute {command}"

    return f"Successfully executed {command}"


def screenshot_command(data: dict) -> str:
    """
        Take ScreenShot
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    file_name = arguments[0]
    image = pyautogui.screenshot()
    image.save(file_name)

    if os.path.exists(file_name):
        return "Screenshot was taken"

    return "Failed to take screenshot"


def send_photo_command(data: dict) -> any:
    """
        Send photo file
    """

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    socket_obj: socket = utils.extract(data, "socket")
    if not socket_obj:
        return "Failed to find socket object"

    # Get original file name
    file_name = arguments[0]

    # Try to get new file name
    new_file_name = utils.extract(arguments, 1)
    if not new_file_name:
        return f"{PHOTO_INFORMATION_COMMAND}>{-2},{file_name}"

    # If our target photo file is invalid
    if not os.path.exists(file_name):
        return f"{PHOTO_INFORMATION_COMMAND}>{-1},{file_name}"

    # Get file size
    file_size = os.path.getsize(file_name)

    # Get photo bytes
    raw_data = b''
    with open(file_name, 'rb') as file:
        raw_data = c_encryption(data).encrypt(file.read())  # encrypt_bytes(file.read(), data)  # Encrypt if you need

    # Get length of the raw data
    raw_size = len(raw_data)

    # Inform the client
    alart_message: str = f"{PHOTO_INFORMATION_COMMAND}>{file_size},{raw_size},{new_file_name}"
    alart_message = c_encryption(data).encrypt(alart_message).decode()
    alart_message = c_protocol.format_value(alart_message)
    socket_obj.send(alart_message.encode())

    # Now we can send the photo raw data
    total_sent = 0

    while total_sent < raw_size:
        remaining = raw_data[total_sent:]
        size = min(BUFFER_SIZE, len(remaining))
        chunk = remaining[:size]

        socket_obj.send(chunk)
        total_sent = total_sent + size

    return None  # Avoid interrupting with the data flow


def receive_photo(data: dict) -> any:
    """
        Receive photo file
    """

    # Small operations and millions of checks

    arguments = utils.extract(data, "arguments")
    if not arguments:
        return "Failed to receive arguments"

    socket_obj: socket = utils.extract(data, "socket")
    if not socket_obj:
        return "Failed to find socket object"

    # Try to get file size
    file_size = utils.extract(arguments, 0, int)
    if not file_size:
        return "Failed to get file size"

    if file_size == -1:
        return "Failed to find photo"

    if file_size == -2:
        return "Invalid new file name"

    # Get new file name and the raw bytes length
    new_file_name = utils.extract(arguments, 2)
    raw_data_size = utils.extract(arguments, 1, int)
    if not raw_data_size:
        return "Failed to get raw data size"

    # Receive the photo data in chunks based on file size
    received_raw_data = b''
    while len(received_raw_data) < raw_data_size:
        chunk_data = socket_obj.recv(min(raw_data_size - len(received_raw_data), BUFFER_SIZE))
        received_raw_data += chunk_data

    # Decrypt the received bytes
    received_data = c_encryption(data).decrypt(received_raw_data)

    # Write the received data to the file
    with open(new_file_name, 'wb') as file:
        file.write(received_data)

    # Check if the new file created
    if not os.path.exists(new_file_name):
        return "Failed to create new Photo File"

    # Check if the new file is the same as the original
    if os.path.getsize(new_file_name) != file_size:
        return "Failed to transfer Photo file; different File Size"

    # Completed the photo file transfer successfully
    return "Photo received"


#  endregion


#  region @ Protocol 2.7 Class

class c_protocol_27(c_protocol, ABC):

    def __init__(self):

        # Current protocol commands
        self._valid_cmds = {
            "DIR": dir_command,
            "DELETE": delete_command,
            "COPY": copy_command,
            "EXECUTE": execute_command,
            "TAKE_SCREENSHOT": screenshot_command,
            "SEND_PHOTO": send_photo_command
        }

        # We want to access the photo information header from outside using the class object
        self._photo_information_header = PHOTO_INFORMATION_COMMAND

    def create_request(self, cmd: str, args: str, data: dict) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        value: str = "Command not supported"  # predefine invalid cmd

        if cmd in self._valid_cmds:
            value = cmd + ">" + args

        value = c_encryption(data).encrypt(value).decode()  # encrypt data

        return c_protocol.format_value(value)

    def create_response(self, cmd: str, args: list, data: dict) -> any:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned,
            In case of ignore response will return None
        """

        response: any = "None Supported CMD"

        data_copy = data.copy()  # No need to interact with the original dict we received
        data_copy["arguments"] = args  # Insert Arguments since we pass only data

        # Check and get response based on command
        if cmd in self._valid_cmds:
            response = self._valid_cmds[cmd](data_copy)

        # Ignore current response
        if response is None:
            return None

        # Log before encryption
        write_to_log(f"  Protocol 2.7  - response : {response}")

        # Encrypt, format and return result
        response = c_encryption(data_copy).encrypt(response).decode()
        return c_protocol.format_value(response)

    def get_cmds(self) -> list:
        """
            Returns valid cmds for current protocol
        """

        result = []

        for cmd_name in self._valid_cmds:
            result.append(cmd_name)

        return result

    def __call__(self, value_name: str):

        if value_name == "photo_header":
            return self._photo_information_header

        return None


#  endregion
