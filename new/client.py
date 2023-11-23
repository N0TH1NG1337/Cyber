""" Client.py

Ex : 2.6
Author : Michael Sokolov
Date : 23.11

"""

# Import library and protocol file
import socket
from protocol import *

# Default values
IP = "-"


def main():
    # socket initialization..
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    while True:
        # Ask "Enter command"
        cmd = input("Enter your command : ")

        # Check if user entered a valid command as defined in protocol
        valid_cmd = check_cmd(cmd)

        # If the command is valid:
        if valid_cmd:
            # 1. Create request
            msg = create_request_msg(cmd)

            # 2. Send it to the server
            my_socket.send(msg.encode())

            # 3. save to log
            write_to_log("[Client] send to server - {}".format(msg))

            # 4. Get server's response
            success, buffer = get_msg(my_socket)

            # 5. Save response to log
            write_to_log("[Client] received from server - {}".format(buffer))

            # 6. If command is EXIT, break from while loop
            if buffer == "Bye":

                # Close socket
                my_socket.close()
                break


if __name__ == "__main__":
    main()
