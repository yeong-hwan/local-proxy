import socket
from threading import Thread
import re
import sys
import time

def handle_client(client_socket, port):
    request_data = client_socket.recv(1024)

    # Extracting the destination host from the request'
    host_data = request_data.decode().splitlines()[1]
    host_pattern = re.compile(r'Host:\s*(.+)')
    match = host_pattern.search(host_data)

    destination_host = match.group(1)

    # print("\n---------------- destination - s --------------")
    # # print(request_data.decode())
    # print("- - - - - - - - - - - - - - - - - - - - - - - ")
    # print(destination_host)
    # print("---------------- destination - e --------------\n")

    # Print log for the received request
    print("-----------------------------------------------")
    print(f"[CLI connected to {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}]")
    

    # Print log for the request and response
    print(f"[CLI ==> PRX --- SRV]")

    request_from_client = request_data.decode().splitlines()[0]
    request_client_pattern = re.compile(r'HTTP/.*')
    request_client_info = re.sub(request_client_pattern, '', request_from_client)

    print(f" > {request_client_info}")
    print(f" > {request_data.decode().splitlines()[5]}")
    
    print(f"[CLI --- PRX ==> SRV]")
    # if response_data:
    #     print(f" > {response_data.decode().splitlines()[0]}")
    #     print(f" > {response_data.decode().splitlines()[1]}")
    
    # # Check for URL Filtering
    # if 'korea' in request_data.decode():
    #     print("[O] Redirected [X] Image filter")
    #     # Modify the response to redirect to a specific URL
    #     response_data = response_data.replace(b'200 OK', b'302 Found')
    #     response_data = response_data.replace(b'Location: http://' + dest_host.encode(), b'Location: http://mnet.yonsei.ac.kr/')
    
    # # Check for Image Filtering
    # if 'image_off' in request_data.decode():
    #     print("[X] Redirected [O] Image filter")
    #     # Drop all requests for images
    #     response_data = b''

    # Connect to the destination server
    server_socket = None
    response_data = None

    try: 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_socket.connect((destination_host, 80))
        server_socket.connect(('https://www.google.com/', 80))

    except Exception as e:
        print("Error 1: " + str(e))


    while True:
        if request_data:
            server_socket.sendall(request_data)
        else:
            break

    # Receive the response from the server
    try:
        response_data = server_socket.recv(4096)
    except Exception as e:
        print("Error 2: " + str(e))
    
    # # Forward the request to the server
    # try: 
    #     server_socket.send(request_data)
    # except Exception as e:
    #     print("Error 3: " + str(e))
    
    # Forward the modified response to the client
    client_socket.send(response_data)
    
    print(f"[CLI --- PRX <== SRV]")

    # Print log for the received response
    print(f"[CLI <== PRX --- SRV]")
    # if response_data:
    #     print(f" > {response_data.decode().splitlines()[0]}")
    #     print(f" > {response_data.decode().splitlines()[1]}")
    
    # Close the connections
    client_socket.close()
    print("[CLI disconnected]")

    server_socket.close()
    print("[SRV disconnected]")

def start_proxy(port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind(('localhost', port))
    proxy_socket.listen(5)
    
    print(f"Starting proxy server on port {port}")

    i = 0
    while True:
        # time.sleep(1)
        print(f"\n[{i}]\n")
        i += 1
        client_socket, addr = proxy_socket.accept()
        print(0)
        client_handler = Thread(target=handle_client, args=(client_socket, port))
        print(1)
        client_handler.start()
        print(2)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 prx.py <port>")
        sys.exit(1)

    try:
        port_number = int(sys.argv[1])
        start_proxy(port_number)
    except KeyboardInterrupt:
        print("\nProxy server terminated by CTRL + C")