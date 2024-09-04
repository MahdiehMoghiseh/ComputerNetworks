import socket
import threading

class Client:
    def __init__(self, host, port, port_udp):
        self.host = host
        self.port = port
        self.port_udp = port_udp
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.dissconnected = False
        self.register_before = False

    def connect(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to the server.")
        response = ""
        while "has joined" not in response:
            username = input("Enter your username: ")
            self.client_socket.send(username.encode())
            password = input("Enter your password: ")
            self.client_socket.send(password.encode())
            response = self.client_socket.recv(1024).decode()
            print(response)
            
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        self.send_messages()
        
    def show_menu(self):
        print("1. Login")
        print("2. SignUp")
        print("3. Get User List")

        choice = input("Enter your choice: ")

        if choice == "1":
            self.logIn()
        elif choice == "2":
            self.connect()
        elif choice == "3":
            self.get_user_list()
            self.show_menu()
        else:
            print("Invalid choice!")
            self.show_menu()
    
    def logIn(self):
        username = input("Enter your username: ")
        self.client_socket.send(username.encode())
        password = input("Enter your password: ")
        self.client_socket.send(password.encode())
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()
        self.send_messages()


    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(message)
                if self.dissconnected:
                    if "has joined" in message:
                        self.dissconnected = False
                        self.send_messages()
                    else:
                        self.logIn()
            except ConnectionResetError:
                print("Disconnected from the server")
                break

    def send_messages(self):
        while not self.dissconnected:
            message = input()
            if message == "/exit":
                self.client_socket.send(message.encode())
                self.dissconnected = True
                self.show_menu()  # Show menu again
                break  # Exit the send_messages loop
            self.client_socket.send(message.encode())

    def get_user_list(self):
        self.client_socket_udp.sendto("/users".encode(), (self.host, self.port_udp))

        try:
            data, _ = self.client_socket_udp.recvfrom(1024)
            user_list = data.decode()
            print(user_list)
        except ConnectionResetError:
            print("Failed")

client = Client('127.0.0.1', 1234, 1235)
client.show_menu()
