"""
    Client BL   .py

    date :      06/03/2024

    TODO :

"""

#  region Libraries

from c_protocol import *
import threading


#  endregion

#  region Client Business Layer


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

        # protocols handler
        self._protocols = {
            "2.6": c_protocol_26(),
            "2.7": c_protocol_27(),
            "login": c_protocol_login()
        }

        # event manager initialize
        self._event_manager = c_event("receive", "disconnect", "login")

        self._last_error = ""
        self._success = self.__connect()

        if self._success:
            threading.Thread(target=self.__handle_responses).start()

    def __connect(self) -> bool:
        """
        Connect event on init client bl.
        In addition, set up the client socket.

        :return: True / False on success
        """

        try:
            # Create and connect socket
            self._socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_obj.connect((self._client_info["ip"], self._client_info["port"]))

            # Log the data
            write_to_log(f"  Client    · {self._socket_obj.getsockname()} connected")

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            self._socket_obj = None
            write_to_log(f"  Client    · failed to connect client; ex:{e}")

            self._last_error = f"An error occurred in client bl [connect function]\nError : {e}"

            return False

    def disconnect(self) -> bool:
        """
        Disconnect the client from server

        :return: True / False on success
        """

        try:

            # Start the disconnect process
            write_to_log(f"  Client    · {self._socket_obj.getsockname()} closing")

            # Alert the server we're closing this client
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

            # Handle failure
            write_to_log(f"  Client    · failed to disconnect : {e}")
            self._last_error = f"An error occurred in client bl [disconnect function]\nError : {e}"

            return False

    def send_data(self, cmd: str, arguments: str) -> bool:
        """
        Send data to the server

        :param cmd: command to send
        :param arguments: arguments as a string to send
        :return: True / False on success
        """

        try:

            # Get Protocol version that we need to use
            type_protocol: int = check_cmd(cmd)

            if type_protocol == 2 and arguments is None:
                raise Exception("Please Enter valid arguments")

            protocols_enum = {
                0: "2.6",
                1: "2.6",
                2: "2.7",
                3: "login"
            }

            # Get the protocol version
            selected_protocol = protocols_enum[type_protocol]
            message: str = ""

            # Get Message based on Protocol
            if selected_protocol:
                message = self._protocols[selected_protocol].create_request(cmd, arguments)
            else:
                message = format_data(cmd)

            # Encode message
            encoded_msg: bytes = message.encode(FORMAT)

            # Send message
            self._socket_obj.send(encoded_msg)

            write_to_log(f"  Client    · send to server : {message}")

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · failed to send to server {e}")
            self._last_error = f"An error occurred in client bl [send_data function]\nError : {e}"

            return False

    def __receive(self) -> any:
        """
        Receive data from the server

        :return: data received from the server
        """

        try:

            success, message = receive_buffer(self._socket_obj)

            if not success:
                return None

            if message.startswith("REGISTRATION_INFO"):
                # We get information from the server before the photo data
                information = message.split('>')

                self._client_info["key"] = Fernet(information[2].encode())

                self._event_manager.call_event("login", information[1])

                # We don't need to call anything since our login event manager
                # will handle everything
                return None

            if message.startswith("PHOTO_INFORMATION"):
                """
                We will receive a photo from the server,

                In old version it contained only a true or false
                state for the photo, therefore we had to wait
                until the socket will time out.

                Here will get the file size and receive it by that.

                """

                # We get information from the server before the photo data
                information = message.split('>')

                # First argument is the file size
                file_size = -1
                try:
                    file_size = int(information[1])
                except Exception as e:
                    return "error on casting file size"

                # Note ! We also get as second argument the original file name
                # Can be used for debugging if something will go wrong

                # -1 file size mean that the server didn't find the photo
                if file_size == -1:
                    return "Failed to find photo"

                # -2 file size mean that the server didn't receive the new file name
                if file_size == -2:
                    return "Invalid new file name"

                # Third argument is the new file name
                # We just don't want to get it to this
                # function as argument :)
                new_file_name = information[2]

                # If we found we want to receive it and get status based result
                status = self._protocols["2.7"].receive_photo(self._socket_obj, file_size, new_file_name)

                # Write to log the information
                write_to_log(f"  Client    · photo status : {status}")

                # Return the status
                return status

            # Just log and return the regular information
            write_to_log(f"  Client    · received from server : {message}")

            return message

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · failed to receive from server : {e}")
            self._last_error = f"An error occurred in client bl [receive_data function]\nError : {e}"

            return None

    def __handle_responses(self):
        """
        We want to process every server response,
        even if we didn't send to it anything.
        """

        while self._socket_obj is not None:

            message = self.__receive()

            if message == DISCONNECT_MSG:
                self._event_manager.call_event("disconnect")
            else:
                self._event_manager.call_event("receive", message)

    def get_success(self) -> bool:
        return self._success

    def get_last_error(self) -> str:
        return self._last_error

    def register_client(self, data):
        contact_information = f"{data['username']},{data['password']}"
        self.send_data("REGISTER", contact_information)

    def login_client(self, data):
        contact_information = f"{data['username']},{data['password']}"
        self.send_data("LOGIN", contact_information)

    def register_callback(self, event_name: str, function: any, function_name: str):
        self._event_manager.register(event_name, function, function_name)


#  endregion


#  region Debug Entry Point

if __name__ == "__main__":
    c_client_bl("?.?.?.?", 8822)

#  endregion
