import socket
import threading
import hashlib
import datetime

class Message:
    def __init__(self, sender, content, time):
        self.sender = sender
        self.content = content
        self.time = time
        
class User:
    def __init__(self, username, password, client_socket):
        self.username = username
        self.client_socket = client_socket
        self.password = password
        self.dissconnected = True
        self.history = []
        self.status = "Available"

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
        password = client_socket.recv(1024).decode()
        while not self.check_username(username, client_socket):
            username = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
        
        with open("usernames.txt", "a") as user_file, open("passwords.txt", "a") as pass_file:
            user_file.write(username + "\n")
            pass_file.write(self.hash_password(password) + "\n")
            
        user = User(username, self.hash_password(password), client_socket)
        user.dissconnected = False
        self.clients.append(user)

        self.send_message_to_all(Message("Server", f"{username} has joined the chat",""))
        self.process(user)
            
    def process(self, user):
        while True:
            message = user.client_socket.recv(1024).decode()
            if message:
                if message.startswith("/private"):  # private chat
                    if user.status == "Busy":
                        user.client_socket.send(self.format_message(Message("Error ", "You can't send message in busy mode!","")).encode())
                    else: 
                        self.send_private_message(user.client_socket, message)
                elif message.startswith("/group"):
                    if user.status == "Busy":
                        user.client_socket.send(self.format_message(Message("Error ", "You can't send message in busy mode!","")).encode())
                    else:
                        self.send_group_messsage(user.client_socket, message)
                elif message == "/users":  # get users
                    self.send_user_list_tcp(user.client_socket)
                elif message == "/exit":
                    self.exit(user.client_socket)
                elif message == "/busy":
                    user.status = "Busy"
                    user.client_socket.send(self.format_message(Message("Server" , "Change status to busy!","")).encode())
                elif message == "/available":
                    user.status = "Available"
                    user.client_socket.send(self.format_message(Message("Server" , "Change status to available!","")).encode())
                else:  # public chat
                    if user.status == "Busy":
                        user.client_socket.send(self.format_message(Message("Error ", "You can't send message in busy mode!","")).encode())
                    else:
                        self.send_message_to_all(Message(user.username, message,""))
                user.history.append(message)
            
    def exit(self, client_socket):
        for client in self.clients:
            if client.client_socket == client_socket:
                client.dissconnected = True
                self.send_message_to_all(Message("Server", f"{client.username} has left the chat",""))
                self.login_again(client_socket)
                break
            
    def check_username(self, username, client_socket):
        with open("usernames.txt", "r") as file:
            usernames = file.read().splitlines()
            if username in usernames:
                client_socket.send(self.format_message(Message("Server", "This username is taken!", "")).encode())
                return False
        return True
    
    def show_history(self, user):
        histS = "\nHistory:\n"
        for hist in user.history:
            histS += "- " + hist + "\n"
        user.client_socket.send(self.format_message(Message("Server", histS,"")).encode())
            
    def login_again(self, client_socket):
        found = False
        wrong_pass = True
        while not found or wrong_pass:
            username = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
            username = client_socket.recv(1024).decode()
            password = client_socket.recv(1024).decode()
            with open("usernames.txt", "r") as user_file, open("passwords.txt", "r") as pass_file:
                usernames = user_file.read().splitlines()
                passwords = pass_file.read().splitlines()
            for i, u in enumerate(usernames):
                if username == u.username:
                    found = True
                    if self.check_password(password, passwords[i]):
                        u.dissconnected = False
                        wrong_pass = False
                        self.send_message_to_all(Message("Server", f"{username} has joined the chat",""))
                        self.show_history(u)
                        self.process(u)
                        break
                    else:
                        client_socket.send(self.format_message(Message("Server", "Invalid password, Try again!","")).encode())
                        break
            if not found:
                print("not found!")
                if not self.check_username(username, client_socket):
                    continue
                user = User(username, self.hash_password(password), client_socket)
                user.dissconnected = False
                self.clients.append(user)
                self.send_message_to_all(Message("Server", f"{username} has joined the chat",""))
                self.process(user)
                break
                
    def hash_password(self, password):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password.encode())
        return sha256_hash.hexdigest()

    def check_password(self, password, password_hash):
        sha256_hash = hashlib.sha256()
        sha256_hash.update(password.encode())
        hashed_password = sha256_hash.hexdigest()
        return hashed_password == password_hash

    def send_message_to_all(self, message):
        for client in self.clients:
            if (not client.dissconnected) and (client.status == "Available"):
                try:
                    client.client_socket.send(self.format_message(message).encode())
                except ConnectionResetError:
                    self.clients.remove(client)
                    client.client_socket.close()

    def send_group_messsage(self, sender_socket, message):
        # /group reci1,reci2 hello
        messageS = message.split(" ")
        reci_usernames = messageS[1]
        reci = reci_usernames.split(",")
        content = " ".join(messageS[2:])
        reci_clients = []
        
        for r in reci:
            for client in self.clients:  
                if client.username == r:
                    reci_clients.append(client)
                    break
        
        for client in self.clients:
            if client.client_socket == sender_socket:
                sender = client.username
                break
            
        for r in reci_clients:
            if r.status == "Busy":
                sender_socket.send(self.format_message(Message("Error ", "The reciever is busy!","")).encode())
            else:
                try:
                    r.client_socket.send(self.format_message(Message(sender, content, str(datetime.datetime.now().time()))).encode())
                    sender_socket.send(self.format_message(Message("Group Message: ", content, "")).encode())
                except ConnectionResetError:
                    self.clients.remove(r)
                    r.client_socket.close()
            
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
            if reci_client.status == "Busy":
                sender_socket.send(self.format_message(Message("Error ", "The reciever is busy!","")).encode())
            else:
                try:
                    reci_client.client_socket.send(self.format_message(Message(sender, content, str(datetime.datetime.now().strftime("%H:%M:%S")))).encode())
                    sender_socket.send(self.format_message(Message("Private to " + reci_username, content,"")).encode())
                except ConnectionResetError:
                    self.clients.remove(reci_client)
                    reci_client.client_socket.close()
        else:
            error_message = f"User '{reci_username}' not found."
            sender_socket.send(self.format_message(Message("Server", error_message,"")).encode())

    def send_user_list_tcp(self, client_socket):
        user_list = "Connected Users:\n"
        for client in self.clients:
            if not client.dissconnected:
                user_list += "- " + client.username + "\n"
        client_socket.send(self.format_message(Message("Server", user_list,"")).encode())

    def send_user_list_udp(self, client_address):
        user_list = "Connected Users:\n"
        for client in self.clients:
            if not client.dissconnected:
                user_list += "- " + client.username + "\n"
        self.server_socket_udp.sendto(user_list.encode(), client_address)

    def format_message(self, message):
        return f"[{message.sender}]: {message.content}  {message.time}"

server = Server('127.0.0.1', 1234, 1235) # 1234: tcp port, 1235: udp port
server.start()
