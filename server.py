import socket
import threading
import sqlite3
import os
from collections import defaultdict

db_path = 'userinformation.db'

def check_or_create_database():
    db_exists = os.path.exists(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if not db_exists:
        print("Creating database and table...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                ip TEXT,
                port TEXT,
                password TEXT,
                isonline INTEGER DEFAULT 0
            )
            ''')
    else:
        
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if "isonline" not in columns:
            print("Adding isonline column to existing table...")
            cursor.execute("ALTER TABLE users ADD COLUMN isonline INTEGER DEFAULT 0")

    conn.commit()
    return conn



conn = check_or_create_database()
cursor = conn.cursor()


clients = defaultdict(lambda: {"ip": "", "port": "", "password": ""})


def handle_client(conn, addr):
    current_username = None
    conn_db = sqlite3.connect(db_path)
    cursor = conn_db.cursor()

    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break

            data_str = data.decode('utf-8')
            print(f"Received data from {addr}: {data_str}")

            parts = data_str.split()
            command = parts[0]

            if command == "REGISTER" and len(parts) == 4:
                name, password, port = parts[1], parts[2], parts[3]
                ip = addr[0]  
                cursor.execute("SELECT username FROM users WHERE username=?", (name,))
                if cursor.fetchone():
                    response = f"Username {name} is already taken."
                else:

                    cursor.execute("INSERT INTO users (username, password, ip, port, isonline) VALUES (?, ?, ?, ?, 0)",
                                   (name, password, ip, port))
                    conn_db.commit()
                    response = f"Registered {name} successfully."
                conn.sendall(response.encode('utf-8'))
            elif command == "GET_IP" and len(parts) == 2:
                name = parts[1]
                cursor.execute("SELECT ip FROM users WHERE username=?", (name,))
                row = cursor.fetchone()
                ip = row[0] if row else "NOT FOUND"
                print(f"GET_IP request for {name}: returning {ip}")  # 添加日志记录
                conn.sendall(ip.encode('utf-8'))

            elif command == "GET_PORT" and len(parts) == 2:
                name = parts[1]
                cursor.execute("SELECT port FROM users WHERE username=?", (name,))
                row = cursor.fetchone()
                port = row[0] if row else "NOT FOUND"
                print(f"GET_PORT request for {name}: returning {port}")  # 添加日志记录
                conn.sendall(port.encode('utf-8'))




            elif command == "LOGIN" and len(parts) == 4:

                name, password, port = parts[1], parts[2], parts[3]

                cursor.execute("SELECT username FROM users WHERE username=? AND password=?", (name, password))

                row = cursor.fetchone()

                if row:

                    current_username = name  

                    client_ip = addr[0]  



                    cursor.execute("UPDATE users SET isonline = 1, ip = ?, port = ? WHERE username=?",

                                   (client_ip, port, current_username))

                    conn_db.commit()

                    conn.sendall("Login successful.".encode('utf-8'))

                else:

                    conn.sendall("Login failed.".encode('utf-8'))




            elif command == "UNREGISTER" and len(parts) == 2:

                name = parts[1]

                cursor.execute("DELETE FROM users WHERE username=?", (name,))

                if cursor.rowcount > 0:

                    conn_db.commit()

                    response = f"Unregistered {name}."

                else:

                    response = f"{name} is not registered."

                print(response)

                conn.sendall(response.encode('utf-8'))


            elif command == "LIST_USERS":
                cursor.execute("SELECT username FROM users")
                users_list = ", ".join([row[0] for row in cursor.fetchall()])
                response = users_list if users_list else "No users online"
                conn.sendall(response.encode('utf-8'))
            elif command == "EXIT" and current_username:
                
                cursor.execute("UPDATE users SET isonline = 0 WHERE username = ?", (current_username,))
                conn_db.commit()
                print(f"User {current_username} set to offline.")
                conn.sendall("You are now logged out.".encode('utf-8'))
                break  

            else:
                conn.sendall("Invalid command".encode('utf-8'))

    except Exception as e:
        print(f"Error with client at {addr}: {e}")

    finally:
        conn.close()
        conn_db.close()

def start_server():
    server_ip = '127.0.0.1'
    server_port = 12345
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_ip, server_port))
    server_socket.listen()

    print(f"Server listening on {server_ip}:{server_port}")
    try:
        while True:

            conn, addr = server_socket.accept()
            print(f"Connected to {addr}")

            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()

