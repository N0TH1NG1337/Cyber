"""
    Server_BL.py - Server Business Layer

    last update : 20/04/2024
"""
import time

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


#  region Client Handle

class c_client_handle:
    # Note ! it is better to use get(...) class function
    # since it will return None on fail. Otherwise, it will raise an Exception on fail

    def __init__(self, protocol_manager):
        self._client_info = {}

        self._event_manager = c_event_manager("receive", "disconnect")
        self._protocol_manager: c_protocol_manager = protocol_manager

    #  region Client Communication handle

    def setup_handle(self, addr: tuple, socket_obj: socket):

        self._client_info["connected"] = True
        self._client_info["logged_in"] = False

        self._client_info["ip"] = addr[0]
        self._client_info["port"] = addr[1]
        self._client_info["socket"] = socket_obj

        self._client_info["thread"] = threading.Thread(target=self.__process_handle)
        self._client_info["thread"].start()

    def __process_handle(self):
        """
            Client Process Handle,
            Returns Is Client Active.

            Note ! Called inside thread
        """

        self._client_info["username"] = f"{self._client_info['ip']} ({self._client_info['port']})"

        while self._client_info["connected"]:
            success, message = receive_raw_buffer(self._client_info["socket"])

            if success:
                message = decrypt_data(message, self._client_info)

                # Manual handles
                cmd, args = parse_data(message)

                write_to_log(f"  Server    · received from {self._client_info['username']} : {cmd}, {args}")

                receive_event = c_event()
                receive_event.add("cmd", cmd)
                receive_event.add("args", args)
                receive_event.add("username", self._client_info["username"])

                self._event_manager.call_event("receive", receive_event)

                if cmd == DISCONNECT_MSG:
                    self._client_info["connected"] = False
                    continue

                return_msg = self._protocol_manager.create_response(cmd, args, self._client_info)

                if not self._client_info["logged_in"]:
                    database_protocol: c_protocol_db = self._protocol_manager.call("database")
                    if database_protocol.get_last_success():

                        _, raw_args = parse_data(return_msg)

                        self._client_info["key"] = Fernet(database_protocol.get_last_key().encode())

                        self._client_info["username"] = args[0]
                        self._client_info["logged_in"] = True

                if return_msg is not None:
                    write_to_log(f"  Server    · send to client : {return_msg}")

                    # Send the response
                    self._client_info["socket"].send(return_msg.encode(FORMAT))

        # Disconnected
        self._client_info["socket"].close()
        write_to_log(f"  Server    · closed client {self._client_info['username']}")

        disconnect_event = c_event()
        disconnect_event.add("client_index", self._client_info["client_index"])
        disconnect_event.add("client_addr", (self._client_info['ip'], self._client_info['port']))

        self._event_manager.call_event("disconnect", disconnect_event)

    def force_disconnect(self) -> bool:
        """
            Call the client to disconnect from the server
        """

        call_for_disconnect = self._protocol_manager.create_request(DISCONNECT_MSG, None, self._client_info)
        if call_for_disconnect is None:
            return False

        self._client_info["socket"].send(call_for_disconnect.encode(FORMAT))
        return True

    #  endregion

    def is_valid(self) -> bool:
        """
            Checks if Current Client Handle is not Value
        """

        # TODO ! Add checks for socket / thread
        return self.get("ip") is not None and self.get("port")

    def is_this_client(self, addr: tuple) -> bool:
        """
            Compares current client to other information
        """

        # Avoid checking invalid client
        if not self.is_valid():
            return False

        is_same_ip = self._client_info["ip"] == addr[0]
        is_same_port = self._client_info["port"] = addr[1]

        return is_same_ip and is_same_port

    def get(self, index) -> any:
        """
            Returns Client Information based index name
        """

        return try_to_extract(self._client_info, index)

    def set(self, index, value) -> None:
        """
            Create/Update client information
        """

        self._client_info[index] = value

    def register_callback(self, event_name: str, function: any, function_name: str, get_args: bool = True):
        self._event_manager.register(event_name, function, function_name, get_args)

#  endregion


#  region Server BL

class c_server_bl:

    def __init__(self):

        self._server_info = {}

        self._server_socket: socket = None

        self._protocol_manager = c_protocol_manager()
        self._event_manager = c_event_manager("server_receive",  # General Receive event
                                              "client_connect",  # Client connects to Server event
                                              "client_disconnect"  # Client disconnects to Server event
                                              )

        self._clients = []  # list of active clients

        self._last_error: str = ""
        self._success: bool = False

    def setup_server(self, ip: str, port: int) -> None:
        """
            Setup Server Business Layer
        """

        write_to_log(f"  Server    · Server starting up")

        try:

            # preallocate important information
            self._server_info["ip"] = ip
            self._server_info["port"] = port
            self._server_info["running"] = False

            # setup server socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((ip, port))

            # register client connection callback function
            self._event_manager.register("client_connect",
                                         self.__on_event_client_connect,
                                         "bl_client_connect", True)

            # success on end
            self._success = True

        except Exception as e:

            # handle failure
            self._server_socket = None

            # log error
            write_to_log(f"  Server    · failed to start up sever : {e}")
            self._last_error = f"Error\nfunction:start_server()\nError : {e}"

            self._success = False

    def start_server(self) -> None:
        """
            Start Server Process
        """

        try:

            # set server status for running
            self._server_info["running"] = True

            # listen for clients
            self._server_socket.listen()

            write_to_log(f"  Server    · listening on {self._server_info['ip']}")

            while self._server_info["running"]:

                # accept new client / timeout listen if needed
                client_socket, client_addr = self.__timeout_accept(0.5)

                # if some client connected
                if client_socket and client_addr:

                    # create and call client connect event
                    client_connect = c_event()
                    client_connect.add("address", client_addr)
                    client_connect.add("socket", client_socket)

                    self._event_manager.call_event("client_connect", client_connect)

        except Exception as e:

            # handle failure and stop the server
            self.stop_server()

            write_to_log(f"  Server    · failed to set up server {e}")
            self._last_error = f"An error occurred in server bl [server_process function]\nError : {e}"

    def stop_server(self) -> None:
        """
            Stop Server Process
        """

        write_to_log(f"  Server    · closing")

        # set server running status for False
        self._server_info["running"] = False

        # disconnect every connect client
        for client in self._clients:
            client.force_disconnect()

        # close socket
        if self._server_socket is not None:
            self._server_socket.close()

        # deallocate socket object
        self._server_socket = None

        write_to_log(f"  Server    · closed")

    def __on_event_client_connect(self, event):
        """
            Client Connected
        """

        # create new client handle object
        new_client = c_client_handle(self._protocol_manager)

        # add to our clients list the new client
        self._clients.append(new_client)

        # save in the client handle, the current object index
        new_client.set("client_index", self._clients.index(new_client))

        # register callback functions
        new_client.register_callback("disconnect",
                                     self.__on_event_client_disconnect,
                                     "bl_client_disconnect", True)

        new_client.register_callback("receive",
                                     self.__on_event_server_receive,
                                     "bl_server_receive", True)

        # finish the setup handle and start the process of receiving data from client
        new_client.setup_handle(event.get("address"), event.get("socket"))

    def __on_event_client_disconnect(self, event):
        """
            Client Disconnected Event
        """

        # receive client index in the list
        index = event.get("client_index")

        # create and call the client disconnect event
        disconnect_event = c_event()
        disconnect_event.add("client_addr", event.get("client_addr"))

        self._event_manager.call_event("client_disconnect", disconnect_event)

        # delete the client from list
        del self._clients[index]

    def __on_event_server_receive(self, event):
        """
            Server Received Event
        """

        # call and pass the event object of server receive event
        self._event_manager.call_event("server_receive", event)

    def kick_client(self, client_addr: tuple) -> bool:
        """
            Force the client to disconnect
        """

        try:
            compare_data = (client_addr[0], int(client_addr[1]))

            for client_ptr in self._clients:
                client_handle: c_client_handle = client_ptr  # get hints :P

                if client_handle.is_valid() and client_handle.is_this_client(compare_data):
                    client_handle.force_disconnect()
                    return True

            return False

        except Exception as e:
            return False

    def __timeout_accept(self, time: float) -> any:
        """
            Timeout function for server to accept clients,
            Much better solution than setting a timeout
            and catching an exception
        """

        try:
            # set timeout
            self._server_socket.settimeout(time)

            # get status if anything is ready
            ready, _, _ = select([self._server_socket], [], [], time)

            # if ready call .accept()
            if ready:
                return self._server_socket.accept()

            return None, None
        except Exception as e:

            # if timed out
            return None, None

    def register_callback(self, event_name: str, function: any, function_name: str, get_args: bool = True):
        self._event_manager.register(event_name, function, function_name, get_args)

    def get_last_error(self) -> str:
        return self._last_error

    def get_success(self) -> bool:
        return self._success

#  endregion
