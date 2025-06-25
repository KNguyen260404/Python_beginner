#!/usr/bin/env python3
import socket
import threading
import json
import time

class ChatServer:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # {client_socket: username}
        self.groups = {}   # {group_name: [client_sockets]}
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address} has been established!")
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()
    
    def handle_client(self, client_socket, address):
        try:
            # Get username from client
            username_data = client_socket.recv(1024).decode('utf-8')
            username = json.loads(username_data)['username']
            self.clients[client_socket] = username
            
            # Send welcome message
            welcome_msg = {
                "type": "system",
                "message": f"Welcome {username}! You are now connected to the chat server.",
                "sender": "Server",
                "timestamp": time.time()
            }
            client_socket.send(json.dumps(welcome_msg).encode('utf-8'))
            
            # Broadcast new user joined
            self.broadcast_message({
                "type": "system",
                "message": f"{username} has joined the chat!",
                "sender": "Server",
                "timestamp": time.time()
            }, exclude=client_socket)
            
            # Send current online users
            online_users = list(self.clients.values())
            user_list_msg = {
                "type": "user_list",
                "users": online_users,
                "timestamp": time.time()
            }
            client_socket.send(json.dumps(user_list_msg).encode('utf-8'))
            
            # Main client handling loop
            while True:
                try:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    message = json.loads(data)
                    message["sender"] = username
                    message["timestamp"] = time.time()
                    
                    if message["type"] == "group_message":
                        group_name = message["group"]
                        if group_name in self.groups:
                            self.group_broadcast(message, group_name)
                        else:
                            # Create new group if it doesn't exist
                            self.groups[group_name] = [client_socket]
                            self.send_message(client_socket, {
                                "type": "system",
                                "message": f"Created new group: {group_name}",
                                "sender": "Server",
                                "timestamp": time.time()
                            })
                    elif message["type"] == "join_group":
                        group_name = message["group"]
                        if group_name in self.groups:
                            if client_socket not in self.groups[group_name]:
                                self.groups[group_name].append(client_socket)
                            self.send_message(client_socket, {
                                "type": "system",
                                "message": f"Joined group: {group_name}",
                                "sender": "Server",
                                "timestamp": time.time()
                            })
                        else:
                            self.groups[group_name] = [client_socket]
                            self.send_message(client_socket, {
                                "type": "system",
                                "message": f"Created and joined new group: {group_name}",
                                "sender": "Server",
                                "timestamp": time.time()
                            })
                    elif message["type"] == "private_message":
                        target_user = message["target"]
                        target_socket = None
                        for sock, user in self.clients.items():
                            if user == target_user:
                                target_socket = sock
                                break
                        
                        if target_socket:
                            self.send_message(target_socket, message)
                            # Also send a copy to the sender
                            self.send_message(client_socket, message)
                        else:
                            self.send_message(client_socket, {
                                "type": "error",
                                "message": f"User {target_user} not found or offline",
                                "sender": "Server",
                                "timestamp": time.time()
                            })
                    else:  # Regular broadcast message
                        self.broadcast_message(message)
                        
                except json.JSONDecodeError:
                    print(f"Invalid JSON from client {username}")
                    break
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            # Client disconnected
            if client_socket in self.clients:
                username = self.clients[client_socket]
                del self.clients[client_socket]
                
                # Remove from all groups
                for group_name in list(self.groups.keys()):
                    if client_socket in self.groups[group_name]:
                        self.groups[group_name].remove(client_socket)
                    # Remove empty groups
                    if not self.groups[group_name]:
                        del self.groups[group_name]
                
                # Broadcast user left
                self.broadcast_message({
                    "type": "system",
                    "message": f"{username} has left the chat!",
                    "sender": "Server",
                    "timestamp": time.time()
                })
            
            client_socket.close()
    
    def send_message(self, client_socket, message):
        try:
            client_socket.send(json.dumps(message).encode('utf-8'))
        except:
            # If sending fails, client is likely disconnected
            if client_socket in self.clients:
                del self.clients[client_socket]
    
    def broadcast_message(self, message, exclude=None):
        for client_socket in list(self.clients.keys()):
            if client_socket != exclude:
                self.send_message(client_socket, message)
    
    def group_broadcast(self, message, group_name):
        if group_name in self.groups:
            for client_socket in self.groups[group_name]:
                self.send_message(client_socket, message)

if __name__ == "__main__":
    server = ChatServer()
    server.start() 