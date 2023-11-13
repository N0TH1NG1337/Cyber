
# steps
# 1. Create a socket
# 2. Bind to an IP address and port
# 3. Listen for incoming connections
# 4. Accept incoming connections
# 5. Receive and send data to clients
# 6. Close the connection with the client
# 7. Close the socket

import socket  # Import socket library

# Create a TCP socket object using the IPv4 protocol family
# Arg : socket.AF_INET - use ip protocol (connect between 2 ips)
# Arg : socket.SOCK_STREAM - use tcp protocol (safe data transaction)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to the IP address 0.0.0.0 and port 8822.
# "0.0.0.0" - the server will be able to receive connections from any client on the network.
server_socket.bind(("0.0.0.0", 8823))

# Start listening for incoming connections.
server_socket.listen()

# Print a message to the console indicating that the server is up and running.
print("The server is up and running")

# Accept an incoming connection and return the client socket object and the client's IP address and port.
(client_socket, client_address) = server_socket.accept()

# Print a message to the console indicating that a client has connected.
print("Client connected")

# Just for test
# print("Client Data : " + str(client_address))

# Keep running until the client sends the "Quit" message.
while True:

    # Receive data from the client and decode it.
    data = client_socket.recv(1024).decode()

    # Print the data received from the client to the console.
    print("Client sent: " + data)

    # If the client sent the "Quit" message, break out of the loop.
    if data == "Quit":
        print("closing client socket now...")
        client_socket.send("Bye".encode())
        break

    # Send the data back to the client.
    client_socket.send(data.encode())

# Close the client socket.
client_socket.close()

# Close the server socket.
server_socket.close()
