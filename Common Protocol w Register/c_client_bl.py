"""
    Client_BL.py - Client Business Layer

    last update : 05/04/2024
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

        # Here will be not only the init process of data
        # but also the connect event

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

        self._last_error = ""
        self._success = self.__connect()

        self._thread_handle = None
        if self._success:
            self._thread_handle = threading.Thread(target=self.__handle_responses).start()

        self._save_file: str = "client_json.txt"
        self.__create_users_file()

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

            message = self._protocol_manager.create_request(cmd,
                                                            arguments,
                                                            self._client_info)
            if message is None:
                # The Create_Request function should not return None at any case
                raise Exception(self._protocol_manager.get_last_error())

            # Encode message
            encoded_msg: bytes = message.encode()

            # Send message
            self._socket_obj.send(encoded_msg)

            # Note ! will print / log nonsense since we get from the .create_requests
            # encrypted data
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

            # Manual handles
            cmd, args = parse_data(message)

            if cmd == "REGISTRATION_INFO":
                # Log in / Register Information
                # Contains Key and response

                if args[0] == "success":
                    try:
                        self._client_info["key"] = Fernet(args[4].encode())
                    except Exception as e:
                        self._client_info["key"] = None

                login_event_data = c_event()
                login_event_data.add("success", args[0])
                login_event_data.add("type", args[1])
                login_event_data.add("username", args[2])
                login_event_data.add("password", args[3])
                login_event_data.add("key", args[4])

                self._event_manager.call_event("login", login_event_data)

                # We don't need to call anything since our login event manager
                # will handle everything
                return None

            if cmd == "PHOTO_INFORMATION":

                data = {
                    "socket": self._socket_obj,
                    "arguments": args,
                    "key": try_to_get_key(self._client_info)
                }

                print(data)

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
                receive_event = c_event()
                receive_event.add("message", message)

                self._event_manager.call_event("receive", receive_event)

    #  endregion

    #  region client helpers

    def register_callback(self, event_name: str, function: any, function_name: str, get_args: bool = True):
        self._event_manager.register(event_name, function, function_name, get_args)

    def __create_users_file(self):

        # Avoid recreate new file
        # if exist
        if os.path.exists(self._save_file):
            return

        data = {"version": "2.0"}

        with open(self._save_file, 'w') as file:
            json.dump(data, file)

    def add_user_field(self, index, value):

        with open(self._save_file, 'r') as f:
            data = json.load(f)

        data[index] = value

        with open(self._save_file, 'w') as f:
            json.dump(data, f)

    def get_user_field(self, index) -> any:
        pass

    #  endregion

    #  region extra functions

    def get_success(self) -> bool:
        return self._success

    def get_last_error(self) -> str:
        return self._last_error

    #  endregion

#  endregion