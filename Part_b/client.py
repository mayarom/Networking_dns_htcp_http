import socket

# Set up the server address and port
SERVER_ADDR = 'localhost'
SERVER_PORT = 20251

# Set up the maximum segment size for the connection
MSS = 1024

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the server address and port
client_socket.connect((SERVER_ADDR, SERVER_PORT))

# Send a request to the server for the homepage
request = 'GET / HTTP/1.1\r\nHost: localhost\r\n\r\n'
client_socket.send(request.encode('utf-8'))

# Receive the server's response
response = client_socket.recv(MSS).decode('utf-8')

# Print the response
print(response)

# Close the socket
client_socket.close()
