"""
Server Business Layer.py

author : 
date : 14.12
"""

# Import everything we need
from Protocol import *
from select import select
import threading

# Constants
SRV_IP = "0.0.0.0"
SRV_ADDR = (SRV_IP, DEFAULT_PORT)
SRV_RUNNING = True


def set_server_running_flag(flag: bool):
    """ Set Server running Flag a new value """
    global SRV_RUNNING
    SRV_RUNNING = flag


def time_accept(server_socket: socket, time: int):
    """ Timeout function for server to accept clients, need this to
        close the server on closing window """

    try:
        server_socket.settimeout(time)

        ready, _, _ = select([server_socket], [], [], time)

        if ready:
            return server_socket.accept()

        return None, None
    except Exception as e:
        return None, None


def start_server():
    """ Start server, create socket and accepts clients """
    set_server_running_flag(True)
    write_to_log("[Server] server is starting")

    try:
        # Create and connect socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(SRV_ADDR)
        server_socket.listen()

        write_to_log(f"[Server] server is listening on {SRV_IP}")

        while SRV_RUNNING:
            # Use time_out function for .accept() to close thread on no need
            client_socket, client_addr = time_accept(server_socket, 5)

            # Check if we didn't time out
            if client_socket:

                # Start a new thread for a new client
                thread = threading.Thread(target=handle_client, args=(client_socket, client_addr))
                thread.start()

                write_to_log(f"[Server] active connection {threading.active_count() - 2}")

        # Close server socket on server end
        server_socket.close()
        write_to_log("[Server] the server is closed")

    except Exception as e:

        # Handle failure
        write_to_log(f"[Server] failed to set up server {e}")


def handle_client(client_socket, client_addr):
    """ Client handle function, will receive everything from client,
        and send back """
    # This code run in separate for every client
    write_to_log(f"[Server] new connection : {client_addr} connected")

    connected = True

    while connected:

        # Get message from  client
        success, msg = get_msg(client_socket)  # client_socket.recv(1024).decode(FORMAT)

        if success:
            # if we managed to get the message :
            write_to_log(f"[Server] received from client : {client_addr} - {msg}")

            # Create a correct response message for the client
            return_msg = create_response_msg(msg)

            # Send it
            client_socket.send(return_msg.encode(FORMAT))

            # If the client wants to disconnect
            if msg == DISCONNECT_MSG:
                connected = False

    # Close client socket
    client_socket.close()
    write_to_log(f"[Server] closed client {client_addr}")
