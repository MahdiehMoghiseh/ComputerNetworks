import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('localhost', 1200)

while True:
    message = input('Enter your message UDP client : ')
    client_socket.sendto(message.encode('utf-8'), server_address)
    data, _ = client_socket.recvfrom(1024)
    print(f"Received message from server: {data.decode('utf-8')}")   
    if message == 'exit server':
        break


client_socket.close()
