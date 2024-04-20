"""
    Client_BL.py - Client Business Layer

    last update : 20/04/2024
"""
import os.path

#  region Libraries

from c_protocol_manager import *
from c_event_manager import *
import json

import threading

#  endregion


#  region Client_BL Class

class c_client_bl:

    def __init__(self, ip: str, port: int):

        # Client Information [will be extended]
        self._client_info: dir = {
            "ip": ip,
            "port": port
        }

        # client socket object
        self._socket_obj: socket = None

        # managers init
        self._protocol_manager = c_protocol_manager()
        self._event_manager = c_event_manager("disconnect",  # Client disconnect event
                                              "receive",  # Client received event
                                              "login"  # Client Logged in event
                                              )

        self._last_error = ""  # Last Error that occurred in ClientBL
        self._success = self.__connect()  # Run Connect and get status

        self._thread_handle = None  # May use it later
        if self._success:
            self._thread_handle = threading.Thread(target=self.__handle_responses).start()

        # Client Information File
        self._save_file: str = "client_json.txt"
        self.__create_users_file()  # Init the file

    #  region client connections

    def __connect(self) -> bool:
        """
            Connect event to the server.
            In addition, set up the client socket

            Returns False/True on success
        """

        try:

            # Create and connect socket
            self._socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_obj.connect((self._client_info["ip"], self._client_info["port"]))

            # Log the data
            write_to_log(f"  Client    · {self._socket_obj.getsockname()} connected")

            return True  # Return on success

        except Exception as e:

            # Handle failure
            self._socket_obj = None

            write_to_log(f"  Client    · failed to connect client;\nexception:{e}")
            self._last_error = f"Error in Client BL.py :\nfunction:connect(),\nexception:{e}"

            return False

    def disconnect(self) -> bool:
        """
            Disconnects the client from the server
        """

        try:

            write_to_log(f"  Client    · {self._socket_obj.getsockname()} closing")

            if not self.send_data(DISCONNECT_MSG, ""):
                raise Exception(self._last_error)

            # Close client socket
            self._socket_obj.close()

            # Log it
            write_to_log(f"  Client    · the client closed")

            # Release the socket object
            self._socket_obj = None

            # Return on success
            return True

        except Exception as e:

            write_to_log(f"  Client    · failed to disconnect client;\nexception:{e}")
            self._last_error = f"Error in Client BL.py :\nfunction:disconnect(),\nexception:{e}"

            return False

    #  endregion

    #  region client data usage

    def send_data(self, cmd: str, arguments: str) -> bool:
        """
            Sends Requests to the server
        """

        try:

            # Receives ready to send message formatted and encrypted if needed by Protocol Manager.
            message = self._protocol_manager.create_request(cmd,
                                                            arguments,
                                                            self._client_info)

            # If our message is None,
            # Something went wrong
            if message is None:

                error = self._protocol_manager.get_last_error()

                # We don't really want to pop up a messageBox in case
                # of invalid command
                if error == "Invalid Command":
                    self.__update_field(error)
                    return True

                # Raise the last error that happened in Protocol Manager
                raise Exception(error)

            # Encode message
            encoded_msg: bytes = message.encode()

            # Send message
            self._socket_obj.send(encoded_msg)

            # Note ! will print / log nonsense since we get from the .create_requests encrypted data
            # TODO ! Log and write before the encryption .
            # TODO ! Or, encrypted only after the log operation
            write_to_log(f"  Client    · send to server : {message}")

            # Return on success
            return True

        except Exception as e:

            write_to_log(f"  Client    · failed to send data;\nexception:{e}")
            self._last_error = f"Error in Client BL.py :\nfunction:send_data(),\nexception:{e}"

            return False

    def __receive(self) -> any:
        """
            Receive Data from the server and convert it
        """

        try:

            success, message = receive_raw_buffer(self._socket_obj)

            if not success:
                return None  # for debug return message, it will contain error

            # Now we have our message. However, it can be encrypted
            # In any case of fail, our message will be untouched
            message = decrypt_data(message, self._client_info)

            # Get Command and arguments received separated
            cmd, args = parse_data(message)

            if cmd == "REGISTRATION_INFO":
                # Log in / Register Information
                # NOTE ! only Register returns key, login need to extract from client_info file

                # In this case we have 2 options to get the key
                # [1] - From Received Data
                # [2] - From client_json.txt
                # In any other case we receive None as key
                key_value = try_to_extract(args, 3)
                if key_value is None:
                    key_value = try_to_extract(self.get_user_field(args[2]), "key")

                if args[0] == "success":

                    # Update client's Encryption / Decryption Key
                    self._client_info["key"] = (key_value is None) and None or Fernet(key_value.encode())

                login_event_data = c_event()
                login_event_data.add("success", args[0])
                login_event_data.add("type", args[1])
                login_event_data.add("username", args[2])
                login_event_data.add("key", key_value)

                self._event_manager.call_event("login", login_event_data)

                # We don't need to call anything since our login event manager
                # will handle everything
                return None

            if cmd == "PHOTO_INFORMATION":

                data = {
                    "socket": self._socket_obj,
                    "arguments": args,
                    "key": try_to_get_key(self._client_info)  # None of fail
                }

                # Call the wrapping function for receive photo operation
                status = receive_photo(data)

                # Write to log the information
                write_to_log(f"  Client    · photo status : {status}")

                return status

            # Just log and return the regular information
            write_to_log(f"  Client    · received from server : {message}")

            return message

        except Exception as e:

            write_to_log(f"  Client    · failed to receive;\nexception:{e}")
            self._last_error = f"Error in Client BL.py :\nfunction:receive(),\nexception:{e}"

            return None

    def __handle_responses(self) -> None:
        """
            We want to process every server response,
            even if we didn't send anything.
        """

        while self._socket_obj is not None:

            message = self.__receive()

            if message == DISCONNECT_MSG:
                self._event_manager.call_event("disconnect", None)
            else:
                self.__update_field(message)

    #  endregion

    #  region client helpers

    def register_callback(self, event_name: str, function: any, function_name: str, get_args: bool = True):
        self._event_manager.register(event_name, function, function_name, get_args)

    def __update_field(self, message):
        receive_event = c_event()
        receive_event.add("message", message)

        self._event_manager.call_event("receive", receive_event)

    def __create_users_file(self):

        # Avoid recreate new file
        # if exist
        if os.path.exists(self._save_file):
            return

        data = {"version": "2.0"}  # will use to validate

        with open(self._save_file, 'w') as file:
            json.dump(data, file)

    def add_user_field(self, index, value):

        with open(self._save_file, 'r') as f:
            data = json.load(f)

        data[index] = value

        with open(self._save_file, 'w') as f:
            json.dump(data, f)

    def get_user_field(self, index) -> any:
        result = None

        with open(self._save_file, 'r') as f:
            data = json.load(f)

            result = try_to_extract(data, index)

        return result

    #  endregion

    #  region extra functions

    def get_success(self) -> bool:
        return self._success

    def get_last_error(self) -> str:
        return self._last_error

    #  endregion

#  endregion
