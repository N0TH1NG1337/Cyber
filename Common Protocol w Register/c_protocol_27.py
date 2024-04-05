"""
    Protocol_27.py - protocol version 2.7 file

    last update : 05/04/2024
"""

#  region Libraries

from c_protocol import *

import subprocess
import pyautogui
import glob
import os

#  endregion


#  region Protocol functions

def dir_command(data: dir) -> str:
    """
        get the list of files in a directory
    """

    args = data["args"]  # Extract arguments from other information

    current_dir: str = str(args[0]) + "\\" + "*.*"
    directory_list = glob.glob(current_dir)

    # write_to_log(f"  Protocol 2.7  · prepare directory file list {directory_list} - {current_dir}")

    return str(", ".join(directory_list))


def delete_command(data: dir) -> str:
    """
        delete the file
    """

    args = data["args"]  # Extract arguments from other information

    file_path = args[0]

    if os.path.exists(file_path):
        os.remove(file_path)

        if not os.path.exists(file_path):
            return f"File {file_path} was deleted"

    return f"File {file_path} was not deleted"


def copy_command(data: dir) -> str:
    """
        copy file to other path
    """

    args = data["args"]  # Extract arguments from other information

    file_path_from = args[0]
    file_path_for = args[1]

    if os.path.exists(file_path_from):
        shutil.copy(file_path_from, file_path_for)

        return f"Copy file from {file_path_from} to {file_path_for}"

    return f"Failed to copy file from {file_path_from}"


def execute_command(data: dir) -> str:
    """
        run process / programm
    """

    args = data["args"]  # Extract arguments from other information

    command = args[0]
    result = subprocess.call(command)

    if result == 0:
        return command + " - successfully executed"

    return command + " - was not executed"


def screenshot_command(data: dir) -> str:
    """
    take screenshot and saves it
    """

    args = data["args"]  # Extract arguments from other information

    file_name = args[0]
    image = pyautogui.screenshot()
    image.save(file_name)

    if os.path.exists(file_name):
        return "Screenshot was taken"

    return "Failed to take screenshot"


def send_photo_command(data: dir) -> any:
    """
        Send Photo
    """

    args = data["args"]  # Extract arguments from other information
    socket_obj = data["socket"]

    file_name = args[0]

    try:

        # if second argument is invalid
        # we will get error
        new_file_name = args[1]

    except Exception as e:

        return f"PHOTO_INFORMATION>{-2},{file_name}"

    # If our target photo file is invalid
    if not os.path.exists(file_name):
        return f"PHOTO_INFORMATION>{-1},{file_name}"

    # photo exist
    # Get file size
    file_size = os.path.getsize(file_name)

    # First get the file data encrypted
    # Note ! We use try_to_get_key in case we call the function without encryption key

    raw_data = b''
    with open(file_name, 'rb') as file:
        raw_data = encrypt_bytes(file.read(), data)

    raw_size = len(raw_data)

    # Alart the client that we will send data now
    socket_obj.send(format_data(encrypt_data(
        f"PHOTO_INFORMATION>{file_size},{raw_size},{new_file_name}",
        data)).encode())

    # Send the data
    total_sent = 0
    while total_sent < raw_size:
        remaining = raw_data[total_sent:]
        size = min(BUFFER_SIZE, len(remaining))
        chunk = remaining[:size]

        socket_obj.send(chunk)
        total_sent = total_sent + size

    return None  # Avoid interrupting with the data flow


def receive_photo(data: dir) -> str:
    """
        Receive Photo
    """

    my_socket = data["socket"]
    args = data["arguments"]

    try:

        # First argument is the file size
        file_size = int(args[0])

        # Note ! We also get as second argument the original file name
        # Can be used for debugging if something will go wrong

        # -1 file size mean that the server didn't find the photo
        if file_size == -1:
            return "Failed to find photo"

        # -2 file size mean that the server didn't receive the new file name
        if file_size == -2:
            return "Invalid new file name"

        try:

            new_file_name = args[2]
            raw_data_len = int(args[1])
        except Exception as e:
            return "Received Invalid Format of confirmation"

        my_socket.settimeout(10)  # Set a timeout

        # Receive the photo data in chunks based on file size
        received_raw_data = b""
        while len(received_raw_data) < raw_data_len:
            _data = my_socket.recv(min(raw_data_len - len(received_raw_data), BUFFER_SIZE))
            received_raw_data += _data

        received_data = decrypt_bytes(received_raw_data, data)
        # print(received_data)

        # Write the received data to the file
        with open(new_file_name, 'wb') as file:
            file.write(received_data)

        if not os.path.exists(new_file_name):
            raise Exception("cannot find new file")

        if os.path.getsize(new_file_name) != file_size:
            raise Exception("not the same filesize")

        return "Photo received"

    except Exception as e:

        return f"Photo couldn't be received : {e}"

#  endregion


#  region Protocol 2.7

class c_protocol_27(c_protocol, ABC):

    def __init__(self):
        self._valid_cmds = {
            "DIR": dir_command,
            "DELETE": delete_command,
            "COPY": copy_command,
            "EXECUTE": execute_command,
            "TAKE_SCREENSHOT": screenshot_command,
            "SEND_PHOTO": send_photo_command
        }

    def create_request(self, cmd: str, args: str, data: dir) -> str:
        """
            Creates a request message by formatting the command and arguments.
        """

        value: str = "Command not supported"

        if cmd in self._valid_cmds or cmd == DISCONNECT_MSG:
            value = cmd + ">" + args

        return format_data(encrypt_data(value, data))

    def create_response(self, cmd: str, args: list, data: dir) -> any:
        """
            Create valid response information,

            In case unsupported request "Non-supported cmd" will be returned,
            In case of ignore response will return None
        """

        response: any = "None Supported CMD"

        data["args"] = args  # Insert arguments into data

        if cmd in self._valid_cmds:
            response = self._valid_cmds[cmd](data)

        if response is None:
            return None

        write_to_log(f"  Protocol 2.7  · response : {response}")

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
