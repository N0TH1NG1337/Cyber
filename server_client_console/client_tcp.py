
# steps
# 1. Create a socket
# 2. Connect to the server
# 3. Send data to the server
# 4. Receive data from the server
# 5. Close the socket

import socket  # Import socket library

# Create a TCP socket object
# Arg : socket.AF_INET - use ip protocol (connect between 2 ips)
# Arg : socket.SOCK_STREAM - use tcp protocol (safe data transaction)
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
my_socket.connect(("192.168.1.185", 8823))

# Initialize the data handler
data = ""

# Keep running until the user wants to stop
while data != "Bye":

    # Get the user input
    msg = input("Enter your message : ")

    # Send the user input to the server
    my_socket.send(msg.encode())

    # Receive data from the server and decode it
    data = my_socket.recv(1024).decode()

    # Print the data to the console
    print("The server sent: " + data)

# Close the socket
my_socket.close()
