"""
    Server_BL.py - Server Business Layer

    last update : 05/04/2024
"""

#  region Libraries

from c_protocol_manager import *
from c_event_manager import *

from select import select

import threading

#  endregion


#  region Clear Log File

with open(LOG_FILE, "wb") as file:
    pass

#  endregion


#  region Client Object

class c_client:

    def __init__(self, ip, port):
        self._ip: str = ip or ""
        self._port: int = port or -1

        self._socket = None
        self._key = None

    def set_socket(self, new_socket):
        self._socket = new_socket

    def set_key(self, new_key):
        self._key = new_key

    def get_addr(self) -> tuple:
        return self._ip, self._port

    def get_socket(self):
        return self._socket

    def get_key(self):
        return self._key

    def is_this_client(self, ip, port):
        return self._ip == ip and self._port == port

    def is_valid(self):
        return self._ip != "" and self._port != -1

#  endregion


#  region Server_BL Class

class c_server_bl:

    def __init__(self, ip: str, port: int):

        self._server_info: dir = {
            "ip": ip,
            "port": port,
            "run_flag": False
        }

        # server socket object
        self._socket_obj = None

        # managers init
        self._protocol_manager = c_protocol_manager()
        self._event_manager = c_event_manager("receive",  # General Receive event
                                              "client_connect",  # Client connects to Server event
                                              "client_disconnect"  # Client disconnects to Server event
                                              )

        # Active Clients objects list
        self._clients_list = []

        self._last_error = ""
        self._success = self.__start_server()

    #  region Server BL Setup and Handle

    def __start_server(self) -> bool:
        write_to_log("  Server    · starting")

        try:
            # Create and connect socket
            self._socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket_obj.bind((self._server_info["ip"], self._server_info["port"]))

            self._event_manager.register("client_connect",
                                         self.__on_event_client_connect,
                                         "bl_client_update", True)

            self._event_manager.register("client_disconnect",
                                         self.__on_event_client_disconnect,
                                         "bl_client_delete", True)

            # Return on success
            return True

        except Exception as e:

            # Handle failure
            self._socket_obj = None
            write_to_log(f"  Server    · failed to start up sever : {e}")

            self._last_error = f"Error\nfunction:start_server()\nError : {e}"

            return False

    def process_server(self):

        try:

            self._server_info["run_flag"] = True

            # listen for clients
            self._socket_obj.listen()

            write_to_log(f"  Server    · listening on {self._server_info['ip']}")

            while self._server_info["run_flag"]:

                # Use time_out function for .accept() to close thread on no need
                client_socket, client_addr = self.__timeout_accept(0.5)

                if client_socket and client_addr:

                    client_info = (client_socket, client_addr)

                    client_connect_event = c_event()
                    client_connect_event.add("client_socket", client_socket)
                    client_connect_event.add("client_addr", client_addr)
                    # client_connect_event.add("client_thread", new_client_thread)

                    self._event_manager.call_event("client_connect", client_connect_event)

                    # Start a new thread for a new client
                    new_client_thread = threading.Thread(target=self.__handle_client, args=client_info)
                    new_client_thread.start()

            self._socket_obj.close()

            write_to_log("  Server    · closed")
            self._socket_obj = None

        except Exception as e:

            write_to_log(f"  Server    · failed to set up server {e}")
            self._last_error = f"An error occurred in server bl [server_process function]\nError : {e}"

    def stop_server_process(self):
        self._server_info["run_flag"] = False

    def __handle_client(self, client_socket, client_addr):

        # This code run in separate for every client
        write_to_log(f"  Server    · new connection : {client_addr} connected")

        client_info: dir = {
            "connected": True,
            "logged": False,
            "username": str(client_addr),
            "socket": client_socket
        }

        while client_info["connected"]:

            success, message = receive_raw_buffer(client_info["socket"])

            if success:
                message = decrypt_data(message, client_info)

                # Manual handles
                cmd, args = parse_data(message)

                write_to_log(f"  Server    · received from {client_addr} : {cmd}, {args}")

                receive_event = c_event()
                receive_event.add("cmd", cmd)
                receive_event.add("args", args)
                receive_event.add("username", client_info["username"])

                self._event_manager.call_event("receive", receive_event)

                if cmd == DISCONNECT_MSG:
                    client_info["connected"] = False
                    continue

                return_msg = self._protocol_manager.create_response(cmd, args, client_info)

                if not client_info["logged"]:

                    if self._protocol_manager.call("database").get_last_success():

                        _, raw_args = parse_data(return_msg)

                        client_info["key"] = Fernet(raw_args[4].encode())

                        client_info["username"] = args[0]
                        client_info["logged"] = True

                # If the client logged in

                if return_msg is not None:
                    write_to_log(f"  Server    · send to client : {return_msg}")

                    # Send the response
                    client_socket.send(return_msg.encode(FORMAT))

        disconnect_event = c_event()
        disconnect_event.add("client_addr", client_addr)

        self._event_manager.call_event("client_disconnect", disconnect_event)

        client_socket.close()
        write_to_log(f"  Server    · closed client {client_addr}")

    def kick_client(self, client_addr) -> bool:
        """
            This function doesn't really Kicks the client.

            It only requests from the client to disconnect
        """

        try:
            result = self.__find_client(client_addr[0], client_addr[1])

            if result:

                client = self._clients_list[result]

                client_socket = client.get_socket()
                client_key = client.get_key()

                if client_socket:
                    client_socket.send(format_data(encrypt_data(DISCONNECT_MSG, {"key": client_key})))

                return True

            raise Exception("")

        except Exception as e:

            return False

    #  endregion

    #  region Server Events

    def __on_event_client_connect(self, event):
        """
            Add client information to Client_List
        """

        (ip, port), socket_obj = event.get("client_addr"), event.get("client_socket")

        new_client = c_client(ip, port)
        new_client.set_socket(socket_obj)

        self._clients_list.append(new_client)

    def __on_event_client_disconnect(self, event):
        """
            Delete client from Client_List by indexing ip and port
        """

        (ip, port) = event.get("client_addr")

        result = self.__find_client(ip, port)

        if result:
            self._clients_list.pop(result)

    #  endregion

    #  region Server helpers

    def __timeout_accept(self, time: float) -> any:
        """
            Timeout function for server to accept clients,
            Much better solution than setting a timeout
            and catching an exception
        """

        try:
            self._socket_obj.settimeout(time)

            ready, _, _ = select([self._socket_obj], [], [], time)

            if ready:
                return self._socket_obj.accept()

            return None, None
        except Exception as e:
            return None, None

    def __find_client(self, ip, port) -> any:
        for index in range(len(self._clients_list)):
            client = self._clients_list[index]

            if client and client.is_this_client(ip, port):
                return index

        return None

    def register_callback(self, event_name: str, function: any, function_name: str, get_args: bool = True):
        self._event_manager.register(event_name, function, function_name, get_args)

    def get_last_error(self) -> str:
        return self._last_error

    def get_success(self) -> bool:
        return self._success

    #  endregion

#  endregion
