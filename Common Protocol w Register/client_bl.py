"""
    c_client_bl.py - Client Business Layer File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol_manager import *

import json
import threading
import os.path
import socket

#  endregion


#  region @ Client BL Class

class c_client_bl:

    def __init__(self, ip: str, port: int):

        # Client information
        self._client_info: dict = {
            "ip": ip,
            "port": port
        }

        # client socket object
        self._socket_obj: socket = None

        # Protocol manager
        self._protocols = c_protocol_manager()

        # Events handler
        self._events = {}

        self._last_error: str = ""

        # Save client information file
        self._save_file: str = "client_json.txt"

        # Start the connection
        self._success: bool = self.__start_connection()

        # Handle messages function thread
        self._messages_thread = None

        # Setup everything else
        self.__setup_events()
        self.__setup_file()

        # Setup thread
        if self._success:
            self._messages_thread = threading.Thread(target=self.__handle_servers_messages)
            self._messages_thread.start()

    #  region Client Setup

    def __setup_events(self):
        """
            Create events for the client
        """

        self._events["disconnect"] = c_event()
        self._events["receive"] = c_event()
        self._events["login"] = c_event()

    def __setup_file(self):
        """
            Setup users file for the client
        """

        # Avoid recreate new file
        # if exist
        if os.path.exists(self._save_file):
            return

        data = {"version": "1.0"}  # just insert any value

        with open(self._save_file, 'w') as file:
            json.dump(data, file)

    #  endregion

    #  region Client Connection

    def __start_connection(self) -> bool:
        """
            Init socket and connect to server
        """

        try:

            # Create and connect socket
            self._socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_obj.connect((self._client_info["ip"], self._client_info["port"]))

            # Log the data
            write_to_log(f"  Client        - {self._socket_obj.getsockname()} connected")

            return True  # Return on success

        except Exception as e:

            # Handle fail
            self._socket_obj = None

            write_to_log(f"  Client        - Failed to start the connection.\nexception:{e}")
            self._last_error = f"Error in client_bl.py :\nexception:\n{e}"

            return False

    def stop_connection(self) -> bool:
        """
            Close connection and inform the server
        """

        try:

            # Log
            write_to_log(f"  Client        - {self._socket_obj.getsockname()} closing")

            # Inform the server about closing the connection
            if not self.send_message(DISCONNECT_MSG, ""):
                raise Exception(self._last_error)

            # Close socket
            self._socket_obj.close()

            # Log
            write_to_log(f"  Client        - the client closed")

            # Delete socket object
            self._socket_obj = None

            return True  # Return on success

        except Exception as e:

            # Handle fail
            write_to_log(f"  Client        - Failed to close the connection.\nexception:{e}")
            self._last_error = f"Error in client_bl.py :\nexception:\n{e}"

            return False

    #  endregion

    #  region Client Communication

    def send_message(self, cmd: str, arguments: str) -> bool:
        """
            Send message to the server
        """

        try:

            # Create request message
            message: str = self._protocols.create_request(cmd, arguments, self._client_info)

            # Check if valid
            if message is None:
                raise Exception(self._protocols("last_error"))

            # Encode message
            encoded: bytes = message.encode()

            # Send
            self._socket_obj.send(encoded)

            # Log the message
            write_to_log(f"  Client        - send to server : {message}")

            # Return on success
            return True

        except Exception as e:

            # Handle fail
            write_to_log(f"  Client        - Failed to send message to server.\nexception:{e}")
            self._last_error = f"Error in client_bl.py :\nexception:\n{e}"

            return False  # Return on fail

    def __receive_message(self) -> any:
        """
            Call and receive the first message in buffer
        """

        try:

            # Try to pop something from buffer
            result, raw_message = c_protocol.get_raw_from_buffer(self._socket_obj)

            # Check if valid
            if not result:
                return None

            # Decrypt if can
            message = c_encryption(self._client_info).decrypt(raw_message).decode()

            # Parse into command and arguments (if possible)
            command, arguments = c_protocol.parse(message)

            # Check if it's related to log in Process
            if command == self._protocols("database")("register_header"):
                return self.__handle_login(arguments)

            # Check if it's related to receiving photo process
            if command == self._protocols("2.7")("photo_header"):
                return self.__handle_receive_photo(arguments)

            # Just log and return the regular information
            write_to_log(f"  Client        - received from server : {message}")

            # Return message
            return message

        except Exception as e:

            # Handle fail
            write_to_log(f"  Client        - Failed to receive message from server.\nexception:{e}")
            self._last_error = f"Error in client_bl.py :\nexception:\n{e}"

            return None  # Return on fail

    def __handle_login(self, arguments) -> None:
        """
            Handle all the login / register process result
        """

        # Try to get the key from the response
        key_value = utils.extract(arguments, 3)

        # If failed to find, search in file base on username
        if key_value is None:
            username = utils.extract(arguments, 2)

            if username:
                key_value = utils.find_key(self.access_user_field(username))

        # Prepare login event data
        self._events["login"] + ("success", arguments[0])

        # Check if we successfully logged in
        if arguments[0] == SUCCESS_CMD:
            self._client_info["key"] = key_value

            self._events["login"] + ("type", arguments[1])
            self._events["login"] + ("username", arguments[2])

        self._events["login"] + ("key", key_value)

        # Call login event
        self._events["login"]()

        return None  # Avoid continuing in the __receive_message()

    def __handle_receive_photo(self, arguments) -> str:
        """
            Handle the receiving photo process
        """

        # Prepare data that will be used
        data = {
            "socket": self._socket_obj,
            "arguments": arguments,
            "key": utils.find_key(self._client_info)
        }

        # Call the function from Protocol 2.7 file
        status = receive_photo(data)

        # Write to log the information
        write_to_log(f"  Client        - photo status : {status}")

        # Return result of the operation
        return status

    def __handle_servers_messages(self) -> None:
        """
            Handle every server message received
        """

        # Work while connected
        while self._socket_obj is not None:

            # Always try to receive something
            message = self.__receive_message()

            # Manual check if the server wants us to disconnect
            if message == DISCONNECT_MSG:
                self._events["disconnect"]()
                continue

            # Otherwise, just prepare and call Receive message event
            self._events["receive"] + ("message", message)  # Update event message
            self._events["receive"]()

    #  endregion

    #  region Client Utils

    def __call__(self, index: str):
        """
            Access in client data / events
        """

        if index == "success":
            return self._success

        if index == "last_error":
            return self._last_error

        if index in self._events:
            return self._events[index]

        return None

    def change_user_field(self, index, value):
        """
            Access the client file to change or add to any user value
        """

        with open(self._save_file, 'r') as file:
            data = json.load(file)

        data[index] = value

        with open(self._save_file, 'w') as file:
            json.dump(data, file)

    def access_user_field(self, index) -> any:
        """
            Get user values by his Index
        """

        with open(self._save_file, 'r') as file:
            data = json.load(file)

            result = utils.extract(data, index)

        return result

    #  endregion

#  endregion
