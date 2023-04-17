import socket

# Set up the server address and port
SERVER_ADDR = ''
SERVER_PORT = 8080

# Set up the maximum segment size for the connection
MSS = 1024

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_ADDR, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(1)

# Print a message to indicate that the server is listening for incoming connections
print(f'Redirect server listening on port {SERVER_PORT}...')

while True:
    # Accept incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive the client's request
    request_data = client_socket.recv(MSS).decode('utf-8')

    # Extract the requested filename from the request
    filename = request_data.split()[1][1:]

    # If the requested filename is the homepage, open it in the default web browser
    if filename == 'home.html':
        import webbrowser
        homepage_filename = 'https://mayacs.biz/'
        webbrowser.open(homepage_filename)

    # Send a response to the client
    response_data = 'HTTP/1.1 200 OK\nContent-Type: text/plain\n\nRedirect successful!'
    client_socket.sendall(response_data.encode('utf-8'))

    # Close the client socket
    print(f'Closed connection with {client_address}')
    client_socket.close()

# Close the server socket
print('Server shutting down...')
server_socket.close()
