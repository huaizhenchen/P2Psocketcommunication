import socket
import sys
import threading
import os
import time
from collections import defaultdict

class Client:
    def __init__(self, name, discovery_server=('localhost', 65432)):
        self.blocked_users = set()
        self.name = name
        self.discovery_server = discovery_server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.messages_socket.bind(('localhost', 0))
        self.listen_port = self.messages_socket.getsockname()[1]
        self.is_active = True
        self.offline_messages = defaultdict(list)
        self.is_registered = False
    def listen_for_messages(self):
        self.messages_socket.listen()
        print(f"{self.name} is listening for messages on {self.listen_port}.")

        while self.is_active:
            try:
                conn, addr = self.messages_socket.accept()
                threading.Thread(target=self.handle_incoming_connection, args=(conn,)).start()
            except Exception as e:
                print(f"Error accepting connections: {e}")

    def handle_incoming_connection(self, conn):
        with conn:
            while self.is_active:
                data = conn.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                sender = message.split(':')[0]
                if sender in self.blocked_users:
                    print(f"\nMessage from {sender} blocked.\n")
                else:
                    print(f"\n{self.name} received message: {message}\n")
                print(
                    f"{self.name}, enter your command (REGISTER, SEND <PeerName> <Message>, BLOCK <UserName>, UNBLOCK <UserName>, LIST, EXIT): ",
                    end='')

    def save_message_to_file(self, message):
        with open(f"{self.name}_messages.txt", "a") as file:
            file.write(message + "\n")

    def send_message(self, peer_name, message):
        try:
            peer_ip = self.get_peer_ip(peer_name)
            if peer_ip == "NOT FOUND":
                raise ConnectionError(f"{peer_name} is offline.")

            peer_port = self.get_peer_port(peer_name)
            if not peer_port:
                raise ConnectionError(f"{peer_name}'s port not found.")

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((peer_ip, peer_port))
                s.sendall(message.encode('utf-8'))
                print(f"Message sent to {peer_name} successfully.")

            self.send_offline_messages(peer_name, peer_ip)

        except ConnectionError as e:
            print(e)
            self.offline_messages[peer_name].append(message)

    def send_online_message(self, peer_name, peer_ip, message):
        peer_port = self.get_peer_port(peer_name)
        if peer_port:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((peer_ip, peer_port))
                    s.sendall(message.encode('utf-8'))
                    print(f"Message sent to {peer_name} successfully.")
            except Exception as e:
                print(f"Error: Could not send message to {peer_name}. {e}")

    def send_offline_messages(self, peer_name, peer_ip):
        if peer_name in self.offline_messages:
            for msg in self.offline_messages[peer_name]:
                print(f"Sending stored message to {peer_name}: {msg}")
                self.send_online_message(peer_name, peer_ip, msg)
            del self.offline_messages[peer_name]

    def get_peer_ip(self, peer_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            sock.sendall(f"GET_IP {peer_name}".encode('utf-8'))
            peer_ip = sock.recv(1024).decode('utf-8')
        if peer_ip == "NOT FOUND":
            print(f"{peer_name}'s IP not found on discovery server.")
            return None
        else:
            return peer_ip

    def list_online_users(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            sock.sendall("LIST_USERS".encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
        print("Online users:", response)
    def get_peer_port(self, peer_name):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            sock.sendall(f"GET_PORT {peer_name}".encode('utf-8'))
            port = sock.recv(1024).decode('utf-8')
        if port.isdigit():
            return int(port)
        else:
            print(f"Error: {peer_name}'s port not found on discovery server.")
            return None

    def register_with_discovery_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(self.discovery_server)
            register_command = f"REGISTER {self.name} {self.listen_port}"
            sock.sendall(register_command.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            print(f"{self.name}: {response}")
            if "Registered" in response:
                self.is_registered = True
            else:
                print("Error: Registration failed.")

    def command_line_interface(self):
        self.is_active = True  # 控制命令行界面循环
        while self.is_active:
            command_input = input(f"{self.name}, enter your command (REGISTER, SEND <PeerName> <Message>, LIST, EXIT): ").strip()
            commands = command_input.split(maxsplit=2)
            if commands[0] == "BLOCK":
                if len(commands) < 2:
                    print("Error: BLOCK command format is 'BLOCK <UserName>'.")
                else:
                    self.blocked_users.add(commands[1])
                    print(f"User {commands[1]} is now blocked.")
            elif commands[0] == "UNBLOCK":
                if len(commands) < 2:
                    print("Error: UNBLOCK command format is 'UNBLOCK <UserName>'.")
                else:
                    self.blocked_users.discard(commands[1])
                    print(f"User {commands[1]} is now unblocked.")
            elif commands[0] == "REGISTER":
                self.register_with_discovery_server()
            elif commands[0] == "SEND":
                if len(commands) < 3:
                    print("Error: SEND command format is 'SEND <PeerName> <Message>'.")
                    continue
                _, peer_name, message = commands
                self.send_message(peer_name, message)
            elif commands[0] == "LIST":
                self.list_online_users()
            elif commands[0] == "EXIT":
                self.is_active = False
            else:
                print("Unknown command or incorrect format.")

    def start(self):
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        self.register_with_discovery_server()
        self.command_line_interface()

    def stop(self):
        self.is_active = False
        self.messages_socket.close()
        self.socket.close()

while True:
    client_name = input("Enter client name or type 'quit' to exit: ")
    if client_name.lower() == 'quit':
        break
    client = Client(client_name)
    client.start()
    client.stop()

