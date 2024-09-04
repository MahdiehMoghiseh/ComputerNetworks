import socket

tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_address = ('localhost', 1300)

tcp_client_socket.connect(tcp_server_address)

while True:  
    message = input('Enter your message TCP client : ') 
    tcp_client_socket.sendall(message.encode('utf-8'))
    data = tcp_client_socket.recv(1024)
    print(f"Received TCP message from server: {data.decode('utf-8')}") 
    if message == 'exit server':
        break

tcp_client_socket.close()
