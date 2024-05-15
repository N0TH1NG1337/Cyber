"""
    c_server_bl.py - Server Business Layer File

    last update : 15/05/2024
"""

#  region @ Libraries

from protocol_manager import *

from select import select
import threading
import time

#  endregion


#  region @ Clear Log File

with open(LOG_FILE, "wb") as file:
    pass

#  endregion


#  region @ Client Handle

class c_client_handle:

    def __init__(self):

        # Client information
        self._client_info: dict = {}

        # Protocol manager
        self._protocols = c_protocol_manager()

        # Events handler
        self._events = {
            "receive": c_event(),       # received message event
            "disconnect": c_event(),    # client disconnected event
            "logged_in": c_event()      # client logged in event
        }

    #  region Client Communication Handle

    def setup_handle(self, addr: tuple, socket_obj: socket):
        """
            Setup client handle
        """

        self._client_info["connected"] = True
        self._client_info["logged_in"] = False

        # Client general information
        self._client_info["ip"] = addr[0]
        self._client_info["port"] = addr[1]
        self._client_info["socket"] = socket_obj

        # Setup thread for requests handle
        self._client_info["thread"] = threading.Thread(target=self.__main_handle)
        self._client_info["thread"].start()

    def __main_handle(self):
        """
            Handle function for requests.
        """

        # Setup default username for each client
        # While they are still not logged in
        self._client_info["username"] = f"{self._client_info['ip']} ({self._client_info['port']})"

        # Work until the client close connection
        while self._client_info["connected"]:

            # Get, Decrypt and Parse data
            command, arguments = self.__handle_requests()

            if command is None and arguments is None:
                continue

            # Check if the client wants to disconnect
            if command == DISCONNECT_MSG:
                self._client_info["connected"] = False
                continue

            # Prepare a response message
            response_msg = self._protocols.create_response(command, arguments, self._client_info)

            # Check if the client is not logged in
            if not self._client_info["logged_in"]:

                # Run handle login to check if the client logged in
                self._client_info["logged_in"] = self.__handle_login(response_msg, arguments)

            # Check if response is valid
            if response_msg is not None:

                # Log response
                write_to_log(f"  Server        - send to client : {response_msg}")

                # Send the response
                self._client_info["socket"].send(response_msg.encode())

        # Close connection
        self.close_connection()

    def __handle_requests(self) -> (str, str):
        """
            Handle client's requests.
            Returns ready command and arguments.
        """

        # Pop from buffer raw-data
        result, message = c_protocol.get_raw_from_buffer(self._client_info["socket"])

        # Check if valid
        if not result:
            return None, None

        # Try to decrypt if can
        message = c_encryption(self._client_info).decrypt(message).decode()

        # Parse to command and arguments
        command, arguments = c_protocol.parse(message)

        # Log
        write_to_log(f"  Server        - received from {self._client_info['username']} : {command}, {arguments}")

        # Prepare and call receive event
        self._events["receive"] + ("command", command)
        self._events["receive"] + ("arguments", arguments)
        self._events["receive"] + ("username", self._client_info['username'])
        self._events["receive"]()

        # Return ready command and arguments
        return command, arguments

    def __handle_login(self, response, arguments) -> bool:
        """
            Handle client's login result.
            Return if the client logged in/registered.
        """

        # Get database protocol ptr
        database_protocol: c_protocol_db = self._protocols("database")

        # Check if the last register / login was Successful.
        if not database_protocol("last_success"):
            return False

        # Just extract information
        _, raw_args = c_protocol.parse(response)

        # Save the encryption key and username
        self._client_info["key"] = database_protocol("last_key")
        self._client_info["username"] = arguments[0]

        # Prepare and call log in event
        self._events["logged_in"] + ("username", arguments[0])
        self._events["logged_in"] + ("address", (self._client_info['ip'], self._client_info['port']))
        self._events["logged_in"]()

        return True

    def close_connection(self):
        """
            Handle close connection process
        """

        # Close socket
        self._client_info["socket"].close()

        # Log
        write_to_log(f"  Server        - closed client {self._client_info['username']}")

        # Setup and call disconnect event
        self._events["disconnect"] + ("index", self._client_info["client_index"])
        self._events["disconnect"] + ("client_addr", (self._client_info['ip'], self._client_info['port']))
        self._events["disconnect"]()

    def force_disconnect(self) -> bool:
        """
            Force the client to disconnect
        """

        # All the idea here to call and force the client
        # to close the connection from his side.
        # By that the server can handle it.

        # Check if socket is initialized otherwise we don't need to close
        if utils.extract(self._client_info, "socket") is None:
            return False

        # Prepare message to call the client to disconnect
        call_for_disconnect = self._protocols.create_request(DISCONNECT_MSG, None, self._client_info)
        if call_for_disconnect is None:
            return False

        # Send message
        self._client_info["socket"].send(call_for_disconnect.encode())

        return True

    #  endregion

    def is_valid(self) -> bool:
        """
            Is client handle valid
        """

        return self("ip") is not None and self("port") is not None

    def get(self, index) -> any:
        """
            Get any information from the client handle
        """

        return utils.extract(self._client_info, index)

    def set(self, index, value):
        """
            Add or Update any information on the client handle
        """

        self._client_info[index] = value

    def __call__(self, index) -> any:
        """
            Access events or client handle data
        """

        if index in self._events:
            return self._events[index]

        return self.get(index)

    def __add__(self, information: tuple):
        """
            Just wrap function for .set(...)
        """

        return self.set(information[0], information[1])

    def __eq__(self, other: any) -> bool:
        """
            Compare current client handle to other
        """

        # Check if current is valid
        if not self.is_valid():
            return False

        other_type = type(other)

        # Let's compare between current handle and tuple with ip and port
        if other_type == c_client_handle:
            return self == (other("ip"), other("port"))

        # Some other type ?
        if other_type != tuple:
            raise Exception("invalid compare item")

        # Check if same ip and port
        is_same_ip = self._client_info["ip"] == other[0]
        is_same_port = str(self._client_info["port"]) == str(other[1])

        # Return result
        return is_same_ip and is_same_port

#  endregion


#  region @ Server BL Class

class c_server_bl:

    def __init__(self):

        # Server information
        self._server_info = {
            "last_error": "",
            "success": False,

            "running": False
        }

        # Server socket object
        self._server_socket = None

        # Protocols manager
        self._protocols = c_protocol_manager()

        # Events handler
        self._events = {
            "server_receive": c_event(),     # General receive event
            "client_connect": c_event(),     # Client connects to server event
            "client_disconnect": c_event(),  # Client disconnects to server event
            "client_log_in": c_event()       # Client logs in to server event
        }

        # List of active clients
        self._clients = []

    #  region Server Setup

    def setup_server(self, ip: str, port: int):
        """
            Setup server business layer
        """

        write_to_log(f"  Server        - Server starting up")

        try:
            # Preallocate important information
            self._server_info["ip"] = ip
            self._server_info["port"] = port

            # Setup server socket
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.bind((ip, port))

            # Setup event client_connect function
            self._events["client_connect"] + (self.__on_event_client_connect, "bl_client_connect", True)

            # Update server init status
            self._server_info["success"] = True

        except Exception as e:

            # Handle failure
            self._server_socket = None

            write_to_log(f"  Server        - failed to start up sever : {e}")
            self._server_info["last_error"] = f"Error\nfunction:start_server()\nError : {e}"

            self._server_info["success"] = False

    def start_server(self):
        """
            Start server process
        """

        try:

            # Update running flag
            self._server_info["running"] = True

            # Listen
            self._server_socket.listen()
            write_to_log(f"  Server        - listening on {self._server_info['ip']}")

            # Work until shutdown
            while self._server_info["running"]:

                # Accept new client
                client_socket, client_addr = self.__timeout_accept(0.5)

                if client_socket and client_addr:

                    # Prepare and call client connect event
                    self._events["client_connect"] + ("address", client_addr)
                    self._events["client_connect"] + ("socket", client_socket)
                    self._events["client_connect"]()

        except Exception as e:

            # Stop the server
            self.stop_server()

            write_to_log(f"  Server        - error occurred in the server connection process {e}")
            self._server_info["last_error"] = f"An error occurred in server bl [server_process function]\nError : {e}"

    def stop_server(self):
        """
            Stop server process
        """

        write_to_log(f"  Server        - closing")

        # Update running flag
        self._server_info["running"] = False

        # disconnect the remaining clients
        for client in self._clients:
            client.force_disconnect()

        # Close server socket
        if self._server_socket is not None:
            self._server_socket.close()

        # Delete it
        self._server_socket = None

        write_to_log(f"  Server        - closed")

    #  endregion

    #  region Events

    def __on_event_client_connect(self, event):
        """
            Client connect event
        """

        # Create new client handle
        new_client = c_client_handle()

        # Add client handle to list
        self._clients.append(new_client)

        # Save current client index in the list
        new_client + ("client_index", self._clients.index(new_client))

        # Register callback functions
        new_client("disconnect") + (self.__on_event_client_disconnect, "bl_client_disconnect", True)
        new_client("receive") + (self.__on_event_server_receive, "bl_server_receive", True)
        new_client("logged_in") + (self.__on_event_client_logs_in, "bl_client_logs_in", True)

        # Finish setup and start the request handle process
        new_client.setup_handle(event("address"), event("socket"))

    def __on_event_client_disconnect(self, event):
        """
            Client disconnect event
        """

        # Get client Index
        index = event("index")

        self._events["client_disconnect"] + ("client_addr", event("client_addr"))
        self._events["client_disconnect"]()

        del self._clients[index]

    def __on_event_client_logs_in(self, event):
        """
            Client logged in event
        """

        self._events["client_log_in"] + ("username", event("username"))
        self._events["client_log_in"] + ("address", event("address"))

        self._events["client_log_in"]()

    def __on_event_server_receive(self, event):
        """
            Server receive request event
        """

        self._events["server_receive"] + ("command", event("command"))
        self._events["server_receive"] + ("arguments", event("arguments"))
        self._events["server_receive"] + ("username", event("username"))

        self._events["server_receive"]()

    #  endregion

    #  region Utils

    def __timeout_accept(self, time: float) -> any:
        """
            Timeout function for server to accept clients.
        """

        # Much better solution than setting a timeout
        # and catching an exception

        if self._server_socket is None:
            return None, None

        try:
            # Set timeout
            self._server_socket.settimeout(time)

            # Get status if anything is ready
            ready, _, _ = select([self._server_socket], [], [], time)

            # If ready call .accept()
            if ready:
                return self._server_socket.accept()

            return None, None
        except Exception as e:

            # If timed out
            return None, None

    def kick_client(self, client_addr: tuple) -> bool:
        """
            Force specific client to disconnect
        """

        try:

            # Find the client we want to disconnect
            for client_ptr in self._clients:
                client_handle: c_client_handle = client_ptr

                if client_handle == client_addr:
                    client_handle.force_disconnect()
                    return True

            return False

        except Exception as e:

            # Catch any error
            return False

    def __call__(self, index):
        """
            Access any events or server bl data
        """

        if index in self._events:
            return self._events[index]

        return utils.extract(self._server_info, index)

    #  endregion

#  endregion
