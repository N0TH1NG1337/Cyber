"""

Client BL       .py

last update:    17/02/2024

"""

#  region Libraries

from c_protocol_26 import *
from c_protocol_27 import *

#  endregion


#  region Client BL Class
class c_client_bl:

    def __init__(self, ip: str, port: int):
        # Here will be not only the init process of data
        # but also the connect event

        self._socket_obj: socket = None

        self.__protocol_26 = c_protocol_26()
        self.__protocol_27 = c_protocol_27()

        self.success = self.__connect(ip, port)

    def __connect(self, ip: str, port: int) -> bool:
        """
        Connect event on init client bl.
        In addition, set up the client socket.

        :param ip: server ip to connect
        :param port: server port to connect
        :return: True / False on success
        """

        try:
            # Create and connect socket
            self._socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_obj.connect((ip, port))

            # Log the data
            write_to_log(f"  Client    · {self._socket_obj.getsockname()} connected")

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            self._socket_obj = None
            write_to_log(f"  Client    · failed to connect client; ex:{e}")

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
            self.send_data(DISCONNECT_MSG, "")

            # Close client socket
            self._socket_obj.close()

            write_to_log(f"  Client    · the client closed")

            self._socket_obj = None

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · failed to disconnect : {e}")
            return False

    def send_data(self, cmd: str, args_string: str) -> bool:
        """
        Send data to the server

        :param cmd: command to send
        :param args_string: arguments as a string to send
        :return: True / False on success
        """

        try:
            type_protocol: int = check_cmd(cmd)

            if type_protocol == 2:
                # Protocol 2.7

                message: str = self.__protocol_27.create_request(cmd, args_string)
                encoded_msg: bytes = message.encode(FORMAT)

                self._socket_obj.send(encoded_msg)

                write_to_log(f"  Client    · send to server : {message}")

                return True

            # If our command is not related to protocol 2.7 at all
            # even if it is invalid one
            # we will use protocol 2.6
            message: str = self.__protocol_26.create_request(cmd)
            encoded_msg: bytes = message.encode(FORMAT)

            self._socket_obj.send(encoded_msg)

            write_to_log(f"  Client    · send to server : {message}")

            return True

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · failed to send to server {e}")
            return False

    def receive_data(self) -> str:
        """
        Receive data from the server

        :return: data received from the server
        """

        try:
            success, message = receive_buffer(self._socket_obj)

            if not success:
                raise Exception("failed to get buffer size")

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
                file_size = int(information[1])

                # Third argument is the new file name
                # We just don't want to get it to this
                # function as argument :)
                new_file_name = information[3]

                # Note ! We also get as second argument the original file name
                # Can be used for debugging if something will go wrong

                # -1 file size mean that the server didn't find the photo
                if information[1] == -1:
                    return "Failed to find photo"

                # If we found we want to receive it and get status based result
                status = self.__protocol_27.receive_photo(self._socket_obj, file_size, new_file_name)

                # Write to log the information
                write_to_log(f"  Client    · photo status : {status}")

                # Return the status
                return status

            # If we didn't want to receive the photo
            # Just log and return the regular information
            write_to_log(f"  Client    · received from server : {message}")

            return message

        except Exception as e:

            # Handle failure
            write_to_log(f"  Client    · failed to receive from server : {e}")
            return ""


#  endregion
