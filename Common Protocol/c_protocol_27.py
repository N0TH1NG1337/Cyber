"""

Protocol 2.6    .py

last update:    09/02/2024

"""

#  region Libraries

from c_protocol import *

#  endregion


#  region class protocol

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

    def create_response(self, cmd: str, args: str, skt: socket) -> str:
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
            response = valid_cmds[cmd](args.split(','), skt)

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

        if os.path.exists(file_name):
            # photo exist

            # Send conformation for the client to wait for data
            my_socket.send(format_data(f"PHOTO_EXISTS>{file_name}").encode(FORMAT))

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
            my_socket.send(format_data(f"PHOTO_NOT_FOUND>{file_name}").encode(FORMAT))

        return "d"  # we just lose it since we don't need it

    def receive_photo(self, my_socket: socket, file_name: str):
        """
        receive photo from server

        :param my_socket: client socket to receive
        :param file_name: new file name
        :return: successful or failure
        """

        with open(file_name, 'wb') as file:
            try:
                my_socket.settimeout(10)  # Set a timeout

                # Just try to get data and then exit on exception
                # if the server will send slower than the time-out
                # we will lose data

                while True:
                    data = my_socket.recv(BUFFER_SIZE)
                    file.write(data)

            except socket.timeout:

                # Check for success file creation
                if os.path.exists(file_name):
                    return "Photo received"

                return "Photo couldn't be received"

    #  endregion

#  endregion
