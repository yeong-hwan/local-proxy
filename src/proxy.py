import socket
from threading import Thread
import re
import sys
import time
from urllib.parse import parse_qs


def handle_client(client_socket, port, count):
    request_data = client_socket.recv(4096)

    # Extracting the destination host from the request'
    host_data = request_data.decode().splitlines()[1]
    host_pattern = re.compile(r'Host:\s*(.+)')
    match = host_pattern.search(host_data)

    destination_host = match.group(1)

    request_from_client = request_data.decode().splitlines()[0]
    request_client_pattern = re.compile(r'HTTP/.*')
    request_client_info = re.sub(request_client_pattern, '', request_from_client)

    # Check for Image Filtering
    global image_filter
    if 'image_off' in request_client_info:
        image_filter = "O" 

    if 'image_on' in request_client_info:
        image_filter = "X" 

    # Check for URL Filtering
    url_filter = "O" if 'korea' in request_client_info else "X"

    # print(request_data.decode())p
    request_data_dict = {}
    for line in request_data.decode().splitlines():
        try:
            title, content = line.split(": ")
            request_data_dict[title] = content
        except:
            pass

    response_user_agent = request_data_dict['User-Agent']
    end_index = response_user_agent.find(")")
    cleaned_user_agent = response_user_agent[:end_index+1].replace("User-Agent: ", "")

    # Connect to the destination server
    server_socket = None
    response_data = None

    try: 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if url_filter == "O":
            destination_host = "mnet.yonsei.ac.kr"
        server_socket.connect((destination_host,  80))
    except Exception as e:
        print("\nServer socket error: " + str(e))
        

    server_socket.sendall(request_data)
    

    # Print log for the received request
    print("-----------------------------------------------")
    print(f"{count} [{url_filter}] Redirected [{image_filter}] Image filter")
    print(f"[CLI connected to {client_socket.getpeername()[0]}:{client_socket.getpeername()[1]}]")

    # Print log for the request and response
    print(f"[CLI ==> PRX --- SRV]")
    print(f" > {request_client_info}")
    print(f" > {cleaned_user_agent}")
    print(f"[SRV connected to {destination_host}:{server_socket.getpeername()[1]}]")    

    print(f"[CLI --- PRX ==> SRV]")
    request_server_info = request_client_info
    prefix = "GET "
    
    if url_filter == "O":
        request_server_info = prefix + destination_host

    print(f" > {request_server_info}")
    print(f" > {cleaned_user_agent}")

    # Receive the response from the server
    print(f"[CLI --- PRX <== SRV]")
    response_data = server_socket.recv(4096)
    response_lines = response_data.decode('iso-8859-1').splitlines()

    response_data_dict = {}
    for line in response_lines:
        try:
            title, content = line.split(": ")
            response_data_dict[title] = content
        except:
            pass
    
    # status
    response_status = response_lines[0]
    cleaned_status = re.sub(r'HTTP/1\.\d\s', '', response_status)

    # content, bytes
    response_content = response_data_dict['Content-Type']
    response_bytes = response_data_dict['Content-Length']

    print(f" > {cleaned_status}")
    print(f" > {response_content} {response_bytes}bytes")
    
    # Print log for the received response
    print(f"[CLI <== PRX --- SRV]")

    if image_filter == "O":
        if response_content.startswith("image"):
            print(f" > 404 Not Found")
        else:
            print(f" > {cleaned_status}")
            print(f" > {response_content} {response_bytes}bytes")
            client_socket.sendall(response_data)
    else:
        print(f" > {cleaned_status}")
        print(f" > {response_content} {response_bytes}bytes")

        # Forward the modified response to the client
        client_socket.sendall(response_data)

    # Close the connections
    client_socket.close()
    print("[CLI disconnected]")

    server_socket.close()
    print("[SRV disconnected]")

def start_proxy(port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    LOCAL_HOST = '127.0.0.1'
    proxy_socket.bind((LOCAL_HOST, port))
    proxy_socket.listen(10)
    
    print(f"Starting proxy server on port {port}")

    # image filter flag
    global image_filter
    image_filter = "X"

    count = 1
    while True:
        client_socket, addr = proxy_socket.accept()
        handle_client(client_socket, port, count)
        count += 1

    proxy_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 prx.py <port>")
        sys.exit(1)

    port_number = int(sys.argv[1])

    try:
        start_proxy(port_number)
    except KeyboardInterrupt:
        print("\nProxy server terminated by CTRL + C")

        try:
            proxy_socket.shutdown(socket.SHUT_RDWR)
            proxy_socket.close()
        except:
            pass

        sys.exit()