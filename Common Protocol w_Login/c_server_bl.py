"""
    Server BL   .py

    date :      07/03/2024

    TODO :

"""

#  region Libraries

from c_protocol import *
from select import select
import threading

#  endregion

#  region Clear Log file

with open(LOG_FILE, "wb") as file:
    pass

#  endregion

#  region Client Business Layer


class c_server_bl:

    def __init__(self, ip: str, port: int):

        self._server_info: dir = {
            "ip": ip,
            "port": port
        }

        # server socket object
        self._server_socket: socket = None

        # server running flag
        self._server_running_flag: bool = False

        # protocols handler
        self._protocols = {
            "2.6": c_protocol_26(),
            "2.7": c_protocol_27(),
            "login": c_protocol_login()
        }

        # event manager initialize
        self._event_manager = c_event("receive", "client_connect", "client_disconnect")

        # Active Clients sockets list
        self._clients_list = {}

        self._last_error = ""
        self._success = self.__start_server()

    #  region Server Operators

    def __start_server(self) -> bool:
        """
        Start server event on init server bl.
        In addition, set up the server socket.


        :return: True / False on success
        """

        write_to_log("  Server    · starting")

        try:
            # Create and connect socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((self._server_info["ip"], self._server_info["port"]))

            self._event_manager.register("client_connect",
                                         self.__update_client_information,
                                         "bl_update_client")

            self._event_manager.register("client_disconnect",
                                         self.__update_client_information,
                                         "bl_delete_client")

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            self._server_socket = None
            write_to_log(f"  Server    · failed to start up sever : {e}")

            self._last_error = f"An error occurred in server bl [start_server function]\nError : {e}"

            return False

    def server_process(self):
        """
        Handles the server listen and connect client process,
        runs within a different thread to avoid conflict with gui
        """

        try:

            self._server_running_flag = True

            # listen for clients
            self._server_socket.listen()

            write_to_log(f"  Server    · listening on {self._server_info['ip']}")

            while self._server_running_flag:

                # Use time_out function for .accept() to close thread on no need
                client_socket, client_addr = self.__timeout_accept(0.5)

                # Note ! We can check only for client_socket since
                # client_addr comes with it, but without the check for both
                # pycharm will cry with warnings
                if client_socket and client_addr:

                    client_info = (client_socket, client_addr)

                    # Start a new thread for a new client
                    new_client_thread = threading.Thread(target=self.__handle_client, args=client_info)
                    new_client_thread.start()

                    self._event_manager.call_event("client_connect", client_addr, client_socket)

                    write_to_log(f"  Server    · active connection {threading.active_count() - 2}")

            # Our server stopped

            # Close server socket on server end
            self._server_socket.close()

            write_to_log("  Server    · closed")

            # Everything went without any problems
            # and we can close the server
            self._server_socket = None

        except Exception as e:

            write_to_log(f"  Server    · failed to set up server {e}")

            self._last_error = f"An error occurred in server bl [server_process function]\nError : {e}"

    def stop_server_process(self):

        self._server_running_flag = False

        for index in self._clients_list:

            self.kick_client(index)

    def __handle_client(self, client_socket, client_addr):
        """
        Client handle function, will receive everything from client,
        and send back

        :param client_socket: client socket object
        :param client_addr: client address
        """

        # This code run in separate for every client
        write_to_log(f"  Server    · new connection : {client_addr} connected")

        client_info: dir = {
            "connected": True,
            "logged": False,
            "username": str(client_addr),
            "key": None,
        }

        while client_info["connected"]:

            # Get message from  client
            (success, msg) = receive_buffer(client_socket)

            if success:

                # if we managed to get the message :
                write_to_log(f"  Server    · received from client : {client_addr} - {msg}")

                # Parse from buffer
                cmd, args = convert_data(msg)

                self._event_manager.call_event("receive", cmd, args, client_info["username"])

                # If the client wants to disconnect
                if cmd == DISCONNECT_MSG:
                    client_info["connected"] = False
                else:

                    write_to_log(f"  Server    · client requested : {cmd} - {args}")

                    if not client_info["logged"]:
                        return_msg = self._protocols["login"].create_response(cmd, args)

                        if self._protocols["login"].get_last_success():

                            raw_key = return_msg.split(">")[2]

                            client_info["key"] = Fernet(raw_key.encode())

                            client_info["username"] = args[0]
                            client_info["logged"] = True

                        write_to_log(f"  Server    · send to client : {return_msg}")

                        # Send the response
                        client_socket.send(return_msg.encode(FORMAT))

                        continue

                    # If the client logged in

                    # Get the protocol version
                    type_protocol: int = check_cmd(cmd)
                    protocols_enum = {
                        1: "2.6",
                        2: "2.7",
                        -1: "2.6"
                    }
                    selected_protocol = protocols_enum[type_protocol]

                    # Call our protocol version .create_response(...)
                    return_msg = self._protocols[selected_protocol].create_response(cmd, args, client_socket)

                    # If one of our protocols returned None
                    # Its mean the server doesn't need to send anything
                    if return_msg is not None:

                        write_to_log(f"  Server    · send to client : {return_msg}")

                        # Send the response
                        client_socket.send(return_msg.encode(FORMAT))

        self._event_manager.call_event("client_disconnect", client_addr, None)

        client_socket.close()
        write_to_log(f"  Server    · closed client {client_addr}")

    def kick_client(self, client_addr) -> str:

        try:

            if type(client_addr) == tuple:
                index = self.__get_index_from_addr(client_addr)
            else:
                index = client_addr

            socket_obj = self._clients_list[index]

            if socket_obj:
                socket_obj.send(format_data(DISCONNECT_MSG).encode())

            return ""

        except Exception as e:

            return str(e)

    #  endregion

    #  region Server Helpers

    def get_server_flag(self) -> bool:
        return self._server_running_flag

    def set_server_flag(self, new_flag: bool):
        self._server_running_flag = new_flag

    def __update_client_information(self, client_addr: tuple, client_socket: socket) -> bool:
        """
        Add / Update the client socket on certain index
        """

        try:

            index = self.__get_index_from_addr(client_addr)

            if client_socket is None:
                self._clients_list.pop(index)
            else:
                self._clients_list[index] = client_socket

            return True

        except Exception as e:

            return False

    def __get_index_from_addr(self, addr: tuple) -> str:
        return f"{addr[0]}->{addr[1]}"

    def __timeout_accept(self, time) -> any:
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

    def register_callback(self, event_name: str, function: any, function_name: str):
        self._event_manager.register(event_name, function, function_name)

    #  endregion

    def get_success(self) -> bool:
        return self._success

    def get_last_error(self) -> str:
        return self._last_error

#  endregion


#  region Debug Entry Point

if __name__ == "__main__":
    c_server_bl("?.?.?.?", 8822)

#  endregion
