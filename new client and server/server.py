""" Server.py

Ex : 2.6
Author : Michael Sokolov
Date : 23.11

"""

import socket
from protocol import *

IP = "0.0.0.0"


def main():
    # Socket initialization ..
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    write_to_log("[Server] - server is up and running")

    (client_socket, client_address) = server_socket.accept()
    write_to_log("[Server] - client connected : {}".format(client_address))

    while True:
        response = ""
        # 1. Get message from socket and check it
        valid_msg, cmd = get_msg(client_socket)

        # 2. Save to log
        write_to_log("[Server] - received from client : ".format(cmd))

        # if command valid
        if valid_msg:
            # 3. If command belongs to TIME, NAME, RAND or EXIT
            if check_cmd(cmd):
                # 4. Create response
                response = create_response_msg(cmd)
            else:
                response = "Wrong command"
        else:
            response = "Wrong protocol"
            # client_socket.recv(1024)  # Attempt to empty the socket from possible garbage

        # 5. Save to log
        write_to_log("[Server] - server send : ".format(response))

        # 6. Send response to the client
        client_socket.send(response.encode())

        # Handle EXIT command, no need to respond to the client
        if cmd == "EXIT":
            client_socket.close()
            write_to_log("[Server] - closing client socket")
            break

    server_socket.close()
    write_to_log("[Server] - closing server socket")


if __name__ == "__main__":
    main()
