import socket
import threading
from collections import defaultdict

clients = defaultdict(lambda: {"ip": "", "port": ""})

def handle_client(conn, addr):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            data_str = data.decode('utf-8')
            print(f"Received data from {addr}: {data_str}")

            parts = data_str.split()
            command = parts[0]

            if command == "REGISTER" and len(parts) == 3:
                name, port = parts[1], parts[2]
                clients[name] = {'ip': addr[0], 'port': port}
                response = f"Registered {name} with IP {addr[0]} and port {port}"
                print(response)
                conn.sendall(response.encode('utf-8'))
            elif command == "UNREGISTER" and len(parts) == 2:
                name = parts[1]
                if name in clients:
                    del clients[name]
                    response = f"Unregistered {name}."
                    print(response)
                    conn.sendall(response.encode('utf-8'))
                else:
                    conn.sendall(f"{name} is not registered.".encode('utf-8'))
            elif command == "GET_IP" and len(parts) == 2:
                name = parts[1]
                ip = clients.get(name, {}).get('ip', "NOT FOUND")
                conn.sendall(ip.encode('utf-8'))
            elif command == "GET_PORT" and len(parts) == 2:
                name = parts[1]
                port = clients.get(name, {}).get('port', "NOT FOUND")
                conn.sendall(port.encode('utf-8'))
            elif command == "LIST_USERS":
                users_list = ", ".join(clients.keys())
                response = users_list if users_list else "No users online"
                conn.sendall(response.encode('utf-8'))
            else:
                conn.sendall("Invalid command".encode('utf-8'))
    except Exception as e:
        print(f"Error with client at {addr}: {e}")
    finally:
        conn.close()

def server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(('localhost', 65432))
        server_socket.listen()
        print("Server is listening for connections...")

        while True:
            conn, addr = server_socket.accept()
            print(f"New connection from {addr}")
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    server()
