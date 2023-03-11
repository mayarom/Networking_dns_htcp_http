import socket
import os
import webbrowser

# Set up the server address and port
SERVER_ADDR = ''
SERVER_PORT = 20251
CLIENT_PORT = 20881

# Set up the maximum segment size for the connection
MSS = 1024

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((SERVER_ADDR, SERVER_PORT))

# Get the server IP
server_ip = socket.gethostbyname(socket.gethostname())
print(f'Server listening on {server_ip}:{SERVER_PORT}...')

# Listen for incoming connections
server_socket.listen(1)

while True:
    # Accept incoming connections
    client_socket, client_address = server_socket.accept()

    # Receive the client's request
    request_data = client_socket.recv(MSS).decode('utf-8')

    # Extract the requested filename from the request
    filename = request_data.split()[1][1:]

    # If the requested filename is empty, serve the homepage
    if filename == '':
        filename = 'finalhtml/Home.html'

    # Check if the requested file is the old website name
    if filename == 'old_website.html':
        # Send a redirect response to the client
        redirect_url = f'http://localhost:{CLIENT_PORT}/new_website.html'
        redirect_message = f'Redirecting to {redirect_url}'
        response_data = f'HTTP/1.1 301 Moved Permanently\nLocation: {redirect_url}\nContent-Type: text/plain\nContent-Length: {len(redirect_message)}\n\n{redirect_message}'
        client_socket.sendall(response_data.encode('utf-8'))

        print(f'Sent redirect response to {client_address}')
    else:
        # If the requested file exists, serve its contents to the client
        if os.path.isfile(filename):
            with open(filename, 'rb') as f:
                file_contents = f.read()

            # Send the response headers
            response_headers = f'HTTP/1.1 200 OK\nContent-Type: text/html\nContent-Length: {len(file_contents)}\n\n'
            client_socket.sendall(response_headers.encode('utf-8'))

            # Send the file contents
            client_socket.sendall(file_contents)

            print(f'Sent file {filename} to {client_address}')

            # Open the file in the default web browser
            webbrowser.open(filename)

        # If the requested file does not exist, send a 404 error response to the client
        else:
            error_message = f'Error 404: File not found: {filename}'
            response_data = f'HTTP/1.1 404 Not Found\nContent-Type: text/plain\nContent-Length: {len(error_message)}\n\n{error_message}'
            client_socket.sendall(response_data.encode('utf-8'))

            print(f'Sent error response to {client_address}')

    # Close the client socket
    print(f'Closed connection with {client_address}')
    client_socket.close()

# Close the server socket
print('Server shutting down...')
server_socket.close()
