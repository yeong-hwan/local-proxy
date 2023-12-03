import socket
import threading
import re
import sys

def handle_client(client_socket):
    request_data = client_socket.recv(1024)
    
    # Extracting the destination host from the request
    dest_host = re.search(r'Host: (.+?)\r\n', request_data.decode()).group(1)
    
    # Print log for the received request
    print("-----------------------------------------------")
    print(f"[CLI connected to {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}]")
    
    # Connect to the destination server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((dest_host, 80))
    
    # Forward the request to the server
    server_socket.send(request_data)
    
    # Receive the response from the server
    response_data = server_socket.recv(4096)
    
    # Print log for the request and response
    print(f"[CLI ==> PRX --- SRV]")
    print(f" > {request_data.decode().splitlines()[0]}")
    print(f" > {request_data.decode().splitlines()[1]}")
    
    print(f"[CLI --- PRX ==> SRV]")
    if response_data:
        print(f" > {response_data.decode().splitlines()[0]}")
        print(f" > {response_data.decode().splitlines()[1]}")
    
    # Check for URL Filtering
    if 'korea' in request_data.decode():
        print("[O] Redirected [X] Image filter")
        # Modify the response to redirect to a specific URL
        response_data = response_data.replace(b'200 OK', b'302 Found')
        response_data = response_data.replace(b'Location: http://' + dest_host.encode(), b'Location: http://mnet.yonsei.ac.kr/')
    
    # Check for Image Filtering
    if 'image_off' in request_data.decode():
        print("[X] Redirected [O] Image filter")
        # Drop all requests for images
        response_data = b''
    
    # Forward the modified response to the client
    client_socket.send(response_data)
    
    # Print log for the received response
    print(f"[CLI <== PRX --- SRV]")
    if response_data:
        print(f" > {response_data.decode().splitlines()[0]}")
        print(f" > {response_data.decode().splitlines()[1]}")
    
    # Close the connections
    client_socket.close()
    server_socket.close()
    
    print("[CLI disconnected]")
    print("[SRV disconnected]")
    print("-----------------------------------------------")

def start_proxy(port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(('0.0.0.0', port))
    proxy_socket.listen(5)
    
    print(f"Starting proxy server on port {port}")
    print("-----------------------------------------------")
    
    while True:
        client_socket, addr = proxy_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 prx.py <port>")
        sys.exit(1)

    try:
        port_number = int(sys.argv[1])
        start_proxy(port_number)
    except KeyboardInterrupt:
        print("\nProxy server terminated by CTRL + C")