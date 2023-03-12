import socket
import os

# Set up the server address and port
SERVER_ADDR = ''
SERVER_PORT = 20251
REDIRECT_SERVER_ADDR = 'localhost'
REDIRECT_SERVER_PORT = 8080

# Set up the maximum segment size for the connection
MSS = 1024

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_ADDR, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(1)

# Print a message to indicate that the server is listening for incoming connections
print(f'Server listening on port {SERVER_PORT}...')

while True:
    # Accept incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive the client's request
    request_data = client_socket.recv(MSS).decode('utf-8')

    # Extract the requested filename from the request
    filename = request_data.split()[1][1:]

    # If the requested filename is empty, serve the homepage
    if filename == '':
        filename = 'home.html'

        # Send a request to the redirect server to open the homepage
        redirect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        redirect_socket.connect((REDIRECT_SERVER_ADDR, REDIRECT_SERVER_PORT))
        redirect_socket.sendall(f'GET /{filename} HTTP/1.1\nHost: {REDIRECT_SERVER_ADDR}:{REDIRECT_SERVER_PORT}\n\n'.encode('utf-8'))
        redirect_socket.close()

    # If the requested file exists, serve its contents to the client
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            file_contents = f.read()

        # Send the response headers
        response_headers = f'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: {len(file_contents)}\n\n'
        client_socket.sendall(response_headers.encode('utf-8'))

        # Send the file contents
        client_socket.sendall(file_contents)

        print(f'Sent response to {client_address}')

    # Close the client socket
    client_socket.close()

# Close the server socket
server_socket.close()


