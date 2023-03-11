import socket

# Set the server address and port
SERVER_ADDR = 'localhost'
SERVER_PORT = 20251

# Create a TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_ADDR, SERVER_PORT))

# Send a request to the server
request = b'GET /finalhtml/Home.html HTTP/1.1\r\nHost: localhost\r\n\r\n'
client_socket.sendall(request)

# Receive a response from the server
response = b''
while True:
    data = client_socket.recv(1024)
    if not data:
        break
    response += data

# Check if the response includes headers
if b'\r\n\r\n' in response:
    headers, content = response.split(b'\r\n\r\n', 1)
    print(content.decode())
else:
    # If the response does not include headers, assume that the entire response is the content
    print(response.decode())

# Close the socket
print('Closing socket...')
client_socket.close()
