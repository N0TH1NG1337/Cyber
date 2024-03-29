"""

Server BL       .py

last update:    28/02/2024

"""

#  region Libraries

from c_protocol_26 import *
from c_protocol_27 import *

from select import select
import threading

#  endregion


#  region Server BL Class

class c_server_bl:
    def __init__(self,
                 ip: str,
                 port: int,
                 receive_callback,
                 client_connect_callback,
                 client_disconnect_callback):

        self.__ip: str = ip

        self.__protocol_26 = c_protocol_26()
        self.__protocol_27 = c_protocol_27()

        self._server_socket: socket = None
        self.__server_running_flag: bool = False

        self._receive_callback = receive_callback
        self._client_connect_callback = client_connect_callback
        self._client_disconnect_callback = client_disconnect_callback

        # Active Clients sockets list
        self._clients_list = {}

        self._last_error = ""
        self._success = self.__start_server(ip, port)

    def __start_server(self, ip: str, port: int) -> bool:
        """
        Start server event on init server bl.
        In addition, set up the server socket.

        :param ip: ip to listen
        :param port: server port to connect
        :return: True / False on success
        """

        write_to_log("  Server    · starting")

        try:
            # Create and connect socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((ip, port))

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            self._server_socket = None
            write_to_log(f"  Server    · failed to start up sever : {e}")

            self._last_error = f"An error occurred in server bl [start_server function]\nError : {e}"

            return False

    def __time_accept(self, time: int):
        """
            Timeout function for server to accept clients,
            Much better solution than setting a timeout
            and catching an exception
            """

        try:
            self._server_socket.settimeout(time)

            ready, _, _ = select([self._server_socket], [], [], time)

            if ready:
                return self._server_socket.accept()

            return None, None
        except Exception as e:
            return None, None

    def server_process(self) -> bool:
        """
        Handles the server listen and connect client process,
        runs within a different thread to avoid conflict with gui

        :return: success on exit
        """

        try:
            self.__server_running_flag = True

            self._server_socket.listen()  # listen for clients

            write_to_log(f"  Server    · listening on {self.__ip}")

            while self.__server_running_flag:

                # Use time_out function for .accept() to close thread on no need
                client_socket, client_addr = self.__time_accept(5)

                # Check if we didn't time out
                if client_socket:

                    client_info = (client_socket, client_addr)

                    # Start a new thread for a new client
                    new_client_thread = threading.Thread(target=self.__handle_client, args=client_info)
                    new_client_thread.start()

                    self._client_connect_callback(client_addr)

                    self.__update_client_information(client_addr, client_socket)

                    write_to_log(f"  Server    · active connection {threading.active_count() - 2}")

            # Close server socket on server end
            self._server_socket.close()
            write_to_log("  Server    · closed")

            # Everything went without any problems
            # and we can close the server
            self._server_socket = None

            return True

        except Exception as e:

            # Handle failure
            write_to_log(f"  Server    · failed to set up server {e}")

            self._last_error = f"An error occurred in server bl [server_process function]\nError : {e}"

            return False

    def __handle_client(self, client_socket, client_addr):
        """
        Client handle function, will receive everything from client,
        and send back

        :param client_socket: client socket object
        :param client_addr: client address
        :return: nothing
        """

        # This code run in separate for every client
        write_to_log(f"  Server    · new connection : {client_addr} connected")

        connected = True

        while connected:

            # Get message from  client
            (success, msg) = receive_buffer(client_socket)

            if success:
                # if we managed to get the message :
                write_to_log(f"  Server    · received from client : {client_addr} - {msg}")

                if self._receive_callback is not None:
                    self._receive_callback(f"{client_addr} - {msg}")

                # Parse from buffer
                cmd, args = convert_data(msg)

                # If the client wants to disconnect
                if cmd == DISCONNECT_MSG:
                    connected = False
                else:
                    write_to_log(f"  Server    · client requested : {cmd} - {args}")

                    type_cmd = check_cmd(cmd)

                    if type_cmd == 2:
                        # Protocol 2.7

                        return_msg = self.__protocol_27.create_response(cmd, args, client_socket)

                        if cmd != "SEND_PHOTO":
                            # We don't want to send something while sending photo
                            # It will interrupt the data

                            write_to_log(f"  Server    · send to client : {return_msg}")

                            # Send the response
                            client_socket.send(return_msg.encode(FORMAT))

                    else:
                        return_msg = self.__protocol_26.create_response(cmd)

                        write_to_log(f"  Server    · send to client : {return_msg}")

                        # Send the response
                        client_socket.send(return_msg.encode(FORMAT))

        if self._client_disconnect_callback is not None:
            self._client_disconnect_callback(client_addr)

        self.__delete_client_information(client_addr)

        # Close client socket
        client_socket.close()
        write_to_log(f"  Server    · closed client {client_addr}")

    def __update_client_information(self, client_addr: tuple, client_socket: socket):
        """
        Add / Update the client socket on certain index
        """

        index = f"{client_addr[0]}-{client_addr[1]}"
        self._clients_list[index] = client_socket

    def __delete_client_information(self, client_addr: tuple) -> bool:
        """
        Delete the client socket object from our list
        """

        try:
            index = f"{client_addr[0]}-{client_addr[1]}"
            self._clients_list[index] = None

            return True
        except Exception as e:
            return False

    def kick_client(self, client_addr: tuple) -> bool:
        """
        Force the client to preform a disconnection from the server
        """

        try:
            index = f"{client_addr[0]}-{client_addr[1]}"
            socket_obj = self._clients_list[index]

            if socket_obj:
                socket_obj.send(format_data(DISCONNECT_MSG).encode())

            return True

        except Exception:
            return False

    def get_server_flag(self) -> bool:
        return self.__server_running_flag

    def update_server_flag(self, flag: bool):
        self.__server_running_flag = flag

    def get_success(self):
        return self._success

    def get_last_error(self):
        return self._last_error

#  endregion
