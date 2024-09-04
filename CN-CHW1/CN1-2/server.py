import socket

from utils import tcp_str, udp_str

def udp_handler():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_server_address = ('localhost', 1200)
    udp_socket.bind(udp_server_address)

    print(f"UDP Server listening on {udp_server_address}") 

    while True: 
        data, client_address = udp_socket.recvfrom(1024) 
        data = data.decode('utf-8') 

        if data == 'exit server': 
            data = 'UDP sever is exiting ...' 
            udp_socket.sendto(data.encode('utf-8'), client_address) 
            print('UDP Exited') 
            return

        print(f"Received UDP message from {client_address}: {data}")

        data = udp_str(data)
        udp_socket.sendto(data.encode('utf-8'), client_address) 

def tcp_handler():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_address = ('localhost', 1300)
    tcp_socket.bind(tcp_server_address)

    tcp_socket.listen()

    print(f"TCP Server listening on {tcp_server_address}")

    tcp_client_socket, tcp_client_address = tcp_socket.accept()
    print(f"Accepted TCP connection from {tcp_client_address}")

    while True:

        data = tcp_client_socket.recv(1024) 
        data = data.decode('utf-8') 

        if data == 'exit server':   
            data = 'TCP server is exiting ...' 
            tcp_client_socket.sendall(data.encode('utf-8'))  
            tcp_client_socket.close() 
            print('TCP Exited')
            return


        print(f"Received TCP message from {tcp_client_address}: {data}")
        data = tcp_str(data)
        tcp_client_socket.sendall(data.encode('utf-8'))

