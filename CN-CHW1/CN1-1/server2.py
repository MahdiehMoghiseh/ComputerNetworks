import socket
import threading

class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content
        
class User:
    def __init__(self, username, client_socket):
        self.username = username
        self.client_socket = client_socket

class Server:
    def __init__(self, host, tcp_port, udp_port):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.clients = []  # list of users

    def start(self):
        self.server_socket_tcp.bind((self.host, self.tcp_port))
        self.server_socket_tcp.listen(5)
        print(f"TCP Server started on {self.host}:{self.tcp_port}")

        self.server_socket_udp.bind((self.host, self.udp_port))
        print(f"UDP Server started on {self.host}:{self.udp_port}")

        tcp_thread = threading.Thread(target=self.tcp_listen)
        tcp_thread.start()

        udp_thread = threading.Thread(target=self.udp_listen)
        udp_thread.start()

    def tcp_listen(self):
        while True:
            client_socket, client_address = self.server_socket_tcp.accept()
            print(f"New TCP connection from {client_address}")


            thread = threading.Thread(target=self.handle_client_tcp, args=(client_socket,))
            thread.start()

    def udp_listen(self):
        while True:
            data, client_address = self.server_socket_udp.recvfrom(1024)
            message = data.decode()

            if message == "/users":
                self.send_user_list_udp(client_address)

    def handle_client_tcp(self, client_socket):
        username = client_socket.recv(1024).decode()
        user = User(username, client_socket)
        self.clients.append(user)

        self.send_message_to_all(Message("Server", f"{username} has joined the chat"))

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    if message.startswith("/private"):  # private chat
                        self.send_private_message(client_socket, message)
                    elif message == "/users":  # get users
                        self.send_user_list_tcp(client_socket)
                    else:  # public chat
                        self.send_message_to_all(Message(username, message))
                else:
                    self.clients.remove(user)
                    self.send_message_to_all(Message("Server", f"{username} has left the chat"))
                    client_socket.close()
                    break
            except ConnectionResetError:
                self.clients.remove(user)
                self.send_message_to_all(Message("Server", f"{username} has left the chat"))
                client_socket.close()
                break

    def send_message_to_all(self, message):
        for client in self.clients:
            try:
                client.client_socket.send(self.format_message(message).encode())
            except ConnectionResetError:
                self.clients.remove(client)
                client.client_socket.close()

    def send_private_message(self, sender_socket, message):
        messageS = message.split(" ")
        reci_username = messageS[1]
        content = " ".join(messageS[2:])
        reci_client = None
        
        for client in self.clients:  
            if client.username == reci_username:
                reci_client = client
                break
        
        for client in self.clients:
            if client.client_socket == sender_socket:
                sender = client.username
                break
        
        if reci_client:
            try:
                reci_client.client_socket.send(self.format_message(Message(sender, content)).encode())
                sender_socket.send(self.format_message(Message("Private to " + reci_username, content)).encode())
            except ConnectionResetError:
                self.clients.remove(reci_client)
                reci_client.client_socket.close()
        else:
            error_message = f"User '{reci_username}' not found."
            sender_socket.send(self.format_message(Message("Server", error_message)).encode())

    def send_user_list_tcp(self, client_socket):
        user_list = "Connected Users:\n"
        for client in self.clients:
            user_list += "- " + client.username + "\n"
        client_socket.send(self.format_message(Message("Server", user_list)).encode())

    def send_user_list_udp(self, client_address):
        user_list = "Connected Users:\n"
        for client in self.clients:
            user_list += "- " + client.username + "\n"
        self.server_socket_udp.sendto(user_list.encode(), client_address)

    def format_message(self, message):
        return f"[{message.sender}]: {message.content}"

server = Server('127.0.0.1', 1234, 1235) # 1234: tcp port, 1235: udp port
server.start()