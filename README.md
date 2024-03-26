# P2Psocketcommunication

README for Chat Application
Overview
This chat application enables real-time text communication between clients through a centralized server. It supports features such as user registration, sending and receiving messages, listing online users, blocking/unblocking users, and handling offline messages.

Server
The server acts as the central node for client discovery and message forwarding. It maintains a list of online users along with their IP addresses and listening ports.

Running the Server
To start the server, run server.py:

bash
Copy code
python server.py
The server listens on localhost port 65432 for incoming connections from clients.

Client
Clients can register with the server, send messages to other clients, and control their availability for receiving messages.

Features
User Registration: Clients must register with the server to be discoverable by other clients.
Send and Receive Messages: Clients can send messages to other registered clients. If the target client is offline, the message is saved and will be sent when the target client becomes available.
List Online Users: Clients can request a list of currently online users from the server.
Blocking/Unblocking Users: Clients can block specific users to prevent receiving messages from them. Blocked messages are silently discarded.
Offline Messages: Messages sent to offline users are stored locally and synchronized when both the sender and the receiver are online.
Starting a Client
Run client.py and follow the prompts to enter a client name or quit to exit:

bash
Copy code
python client.py
Commands
REGISTER: Register the client with the discovery server.
SEND <PeerName> <Message>: Send a message to another user.
BLOCK <UserName>: Block messages from a specific user.
UNBLOCK <UserName>: Unblock a previously blocked user.
LIST: List all online users.
EXIT: Exit the chat application.
Implementation Details
Language: Python
Networking: Uses Python's socket library for TCP connections.
Concurrency: Uses threading for handling multiple client connections simultaneously.
Dependencies
Python 3.x
No external libraries required.
Example Usage
Start the server: python server.py
Start a client: python client.py, enter a unique client name.
Register the client by typing REGISTER and pressing Enter.
List online users by typing LIST.
Send a message to another user: SEND username message.
Block a user: BLOCK username.
Unblock a user: UNBLOCK username.
Exit the client: EXIT.
Notes
Ensure the server is running before starting clients.
Clients need to be on the same network as the server or have a routable address if running on different networks.
This README provides a basic guide to getting started with the chat application. Further customization and feature enhancements can be implemented as needed.
