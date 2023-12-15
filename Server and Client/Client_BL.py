"""
Client Business Layer.py

author : 
date : 14.12
"""

# Import protocol file
from Protocol import *

# No need because we get from the GUI
# CL_IP = socket.gethostbyname(socket.gethostname())
# CL_ADDR = (CL_IP, DEFAULT_PORT)


def connect(server_ip: str, port: int) -> socket:
    """ Connect client to the server, receive server ip and port, and return a socket """

    try:
        # Create and connect socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, port))

        # Log data
        write_to_log(f"[Client] {client_socket.getsockname()} connected")

        # Return client socket object
        return client_socket

    except Exception as e:

        # Handle failure
        write_to_log(f"[Client] failed to connect client; ex:{e}")
        return None


def disconnect(my_socket: socket) -> bool:
    """ Disconnect the client from the server, return True on success """

    try:
        write_to_log(f"[Client] {my_socket.getsockname()} closing")
        send(my_socket, DISCONNECT_MSG)
        my_socket.close()

        return True

    except Exception as e:

        # Handle failure
        write_to_log(f"[Client] failed to disconnect {e}")
        return False


def send(sock: socket, msg: str) -> bool:
    """ Send data to the server, return True on success """

    try:
        # Create and send message
        message = create_request_msg(msg).encode(FORMAT)
        sock.send(message)

        # Log it
        write_to_log(f"[Client] send to server {message}")

        return True

    except Exception as e:

        # Handle failure
        write_to_log(f"[Client] failed to send to server {e}")
        return False


def receive(sock: socket) -> str:
    """ Receive data from the server, return True on success """

    try:
        # message = sock.recv(1024).decode(FORMAT)
        success, message = get_msg(sock)
        if not success:
            raise Exception("failed to get msg")

        write_to_log(f"[Client] received from server {message}")

        return message

    except Exception as e:

        # Handle failure
        write_to_log(f"[Client] failed to receive from server {e}")
        return ""
