#!/usr/bin/env python3
import socket
import threading
import time
import json
import sys
import signal

class UDPGroupChatServer:
    def __init__(self, host="0.0.0.0", port=5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}  # {address: {"username": name, "last_seen": timestamp}}
        self.groups = {}   # {group_name: [client_addresses]}
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, sig, frame):
        """Handle Ctrl+C to shut down gracefully"""
        print("\nShutting down server...")
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        sys.exit(0)
    
    def start(self):
        """Start the server"""
        try:
            # Create UDP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind((self.host, self.port))
            
            print(f"UDP Group Chat Server started on {self.host}:{self.port}")
            self.running = True
            
            # Start maintenance thread
            maintenance_thread = threading.Thread(target=self.maintenance_task)
            maintenance_thread.daemon = True
            maintenance_thread.start()
            
            # Main server loop
            self.receive_messages()
            
        except Exception as e:
            print(f"Error starting server: {e}")
            if self.server_socket:
                self.server_socket.close()
    
    def receive_messages(self):
        """Receive and process incoming messages"""
        while self.running:
            try:
                # Receive message and client address
                data, client_address = self.server_socket.recvfrom(4096)
                
                # Process the message
                self.process_message(data, client_address)
                
            except Exception as e:
                print(f"Error receiving message: {e}")
    
    def process_message(self, data, client_address):
        """Process incoming messages"""
        try:
            # Decode and parse the message
            message = json.loads(data.decode('utf-8'))
            message_type = message.get('type', '')
            
            # Update client's last seen timestamp
            client_key = f"{client_address[0]}:{client_address[1]}"
            
            # Handle different message types
            if message_type == 'register':
                self.register_client(message, client_address)
            
            elif message_type == 'message':
                self.handle_message(message, client_address)
            
            elif message_type == 'join_group':
                self.join_group(message, client_address)
            
            elif message_type == 'leave_group':
                self.leave_group(message, client_address)
            
            elif message_type == 'list_groups':
                self.list_groups(client_address)
            
            elif message_type == 'list_users':
                self.list_users(message, client_address)
            
            elif message_type == 'heartbeat':
                self.update_client_timestamp(client_address)
            
            else:
                self.send_error(client_address, f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            self.send_error(client_address, "Invalid JSON format")
        except Exception as e:
            self.send_error(client_address, f"Error processing message: {str(e)}")
    
    def register_client(self, message, client_address):
        """Register a new client"""
        username = message.get('username', '')
        if not username:
            self.send_error(client_address, "Username is required")
            return
        
        # Check if username is already taken
        for addr, client_info in self.clients.items():
            if client_info['username'] == username and addr != client_address:
                self.send_error(client_address, "Username already taken")
                return
        
        # Register the client
        client_key = f"{client_address[0]}:{client_address[1]}"
        self.clients[client_address] = {
            'username': username,
            'last_seen': time.time()
        }
        
        # Send confirmation
        response = {
            'type': 'register_ack',
            'status': 'success',
            'message': f"Welcome {username}!"
        }
        self.server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)
        
        # Notify other clients
        self.broadcast_system_message(f"{username} has joined the chat")
    
    def handle_message(self, message, client_address):
        """Handle a chat message"""
        if client_address not in self.clients:
            self.send_error(client_address, "You are not registered")
            return
        
        content = message.get('content', '')
        target_type = message.get('target_type', 'broadcast')
        target = message.get('target', '')
        
        sender = self.clients[client_address]['username']
        
        # Update client's last seen timestamp
        self.update_client_timestamp(client_address)
        
        if target_type == 'broadcast':
            # Broadcast to all clients
            self.broadcast_message(sender, content)
            
        elif target_type == 'group':
            # Send to a specific group
            if target not in self.groups:
                self.send_error(client_address, f"Group '{target}' does not exist")
                return
                
            # Check if client is in the group
            if client_address not in self.groups[target]:
                self.send_error(client_address, f"You are not a member of group '{target}'")
                return
                
            self.group_message(sender, content, target)
            
        elif target_type == 'private':
            # Send to a specific user
            recipient_address = None
            for addr, client_info in self.clients.items():
                if client_info['username'] == target:
                    recipient_address = addr
                    break
                    
            if not recipient_address:
                self.send_error(client_address, f"User '{target}' not found")
                return
                
            self.private_message(sender, content, target, recipient_address)
            
        else:
            self.send_error(client_address, f"Unknown target type: {target_type}")
    
    def broadcast_message(self, sender, content):
        """Broadcast a message to all clients"""
        message = {
            'type': 'message',
            'sender': sender,
            'content': content,
            'timestamp': time.time()
        }
        
        # Send to all registered clients
        for client_address in self.clients:
            self.server_socket.sendto(json.dumps(message).encode('utf-8'), client_address)
    
    def group_message(self, sender, content, group_name):
        """Send a message to a specific group"""
        message = {
            'type': 'message',
            'sender': sender,
            'group': group_name,
            'content': content,
            'timestamp': time.time()
        }
        
        # Send to all members of the group
        for client_address in self.groups[group_name]:
            if client_address in self.clients:  # Make sure client is still registered
                self.server_socket.sendto(json.dumps(message).encode('utf-8'), client_address)
    
    def private_message(self, sender, content, recipient_name, recipient_address):
        """Send a private message to a specific user"""
        message = {
            'type': 'private_message',
            'sender': sender,
            'recipient': recipient_name,
            'content': content,
            'timestamp': time.time()
        }
        
        # Send to recipient
        self.server_socket.sendto(json.dumps(message).encode('utf-8'), recipient_address)
        
        # Send confirmation to sender
        sender_address = None
        for addr, client_info in self.clients.items():
            if client_info['username'] == sender:
                sender_address = addr
                break
                
        if sender_address:
            confirm_message = {
                'type': 'message_sent',
                'recipient': recipient_name,
                'timestamp': time.time()
            }
            self.server_socket.sendto(json.dumps(confirm_message).encode('utf-8'), sender_address)
    
    def join_group(self, message, client_address):
        """Add a client to a group"""
        if client_address not in self.clients:
            self.send_error(client_address, "You are not registered")
            return
            
        group_name = message.get('group', '')
        if not group_name:
            self.send_error(client_address, "Group name is required")
            return
            
        # Create group if it doesn't exist
        if group_name not in self.groups:
            self.groups[group_name] = []
            
        # Add client to group if not already a member
        if client_address not in self.groups[group_name]:
            self.groups[group_name].append(client_address)
            
        # Update client's last seen timestamp
        self.update_client_timestamp(client_address)
            
        # Send confirmation
        response = {
            'type': 'join_group_ack',
            'status': 'success',
            'group': group_name,
            'message': f"You have joined group '{group_name}'"
        }
        self.server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)
        
        # Notify group members
        username = self.clients[client_address]['username']
        group_message = {
            'type': 'system_message',
            'group': group_name,
            'content': f"{username} has joined the group",
            'timestamp': time.time()
        }
        
        for member_address in self.groups[group_name]:
            if member_address != client_address:  # Don't send to the client who just joined
                self.server_socket.sendto(json.dumps(group_message).encode('utf-8'), member_address)
    
    def leave_group(self, message, client_address):
        """Remove a client from a group"""
        if client_address not in self.clients:
            self.send_error(client_address, "You are not registered")
            return
            
        group_name = message.get('group', '')
        if not group_name:
            self.send_error(client_address, "Group name is required")
            return
            
        # Check if group exists
        if group_name not in self.groups:
            self.send_error(client_address, f"Group '{group_name}' does not exist")
            return
            
        # Check if client is in the group
        if client_address not in self.groups[group_name]:
            self.send_error(client_address, f"You are not a member of group '{group_name}'")
            return
            
        # Remove client from group
        self.groups[group_name].remove(client_address)
        
        # Update client's last seen timestamp
        self.update_client_timestamp(client_address)
        
        # Remove group if empty
        if not self.groups[group_name]:
            del self.groups[group_name]
            
        # Send confirmation
        response = {
            'type': 'leave_group_ack',
            'status': 'success',
            'group': group_name,
            'message': f"You have left group '{group_name}'"
        }
        self.server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)
        
        # Notify group members
        if group_name in self.groups:  # Group might have been deleted if empty
            username = self.clients[client_address]['username']
            group_message = {
                'type': 'system_message',
                'group': group_name,
                'content': f"{username} has left the group",
                'timestamp': time.time()
            }
            
            for member_address in self.groups[group_name]:
                self.server_socket.sendto(json.dumps(group_message).encode('utf-8'), member_address)
    
    def list_groups(self, client_address):
        """Send a list of available groups to a client"""
        if client_address not in self.clients:
            self.send_error(client_address, "You are not registered")
            return
            
        # Update client's last seen timestamp
        self.update_client_timestamp(client_address)
            
        # Prepare group list with member counts
        group_list = {}
        for group_name, members in self.groups.items():
            group_list[group_name] = len(members)
            
        # Send the list
        response = {
            'type': 'group_list',
            'groups': group_list,
            'timestamp': time.time()
        }
        self.server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)
    
    def list_users(self, message, client_address):
        """Send a list of users to a client"""
        if client_address not in self.clients:
            self.send_error(client_address, "You are not registered")
            return
            
        # Update client's last seen timestamp
        self.update_client_timestamp(client_address)
            
        group_name = message.get('group', '')
        
        if group_name:
            # List users in a specific group
            if group_name not in self.groups:
                self.send_error(client_address, f"Group '{group_name}' does not exist")
                return
                
            # Get usernames of group members
            users = []
            for member_address in self.groups[group_name]:
                if member_address in self.clients:
                    users.append(self.clients[member_address]['username'])
                    
            response = {
                'type': 'user_list',
                'group': group_name,
                'users': users,
                'timestamp': time.time()
            }
            
        else:
            # List all users
            users = []
            for addr, client_info in self.clients.items():
                users.append(client_info['username'])
                
            response = {
                'type': 'user_list',
                'users': users,
                'timestamp': time.time()
            }
            
        self.server_socket.sendto(json.dumps(response).encode('utf-8'), client_address)
    
    def send_error(self, client_address, error_message):
        """Send an error message to a client"""
        error = {
            'type': 'error',
            'message': error_message,
            'timestamp': time.time()
        }
        self.server_socket.sendto(json.dumps(error).encode('utf-8'), client_address)
    
    def broadcast_system_message(self, content):
        """Broadcast a system message to all clients"""
        message = {
            'type': 'system_message',
            'content': content,
            'timestamp': time.time()
        }
        
        # Send to all registered clients
        for client_address in self.clients:
            self.server_socket.sendto(json.dumps(message).encode('utf-8'), client_address)
    
    def update_client_timestamp(self, client_address):
        """Update a client's last seen timestamp"""
        if client_address in self.clients:
            self.clients[client_address]['last_seen'] = time.time()
    
    def maintenance_task(self):
        """Periodically check for inactive clients"""
        while self.running:
            current_time = time.time()
            inactive_clients = []
            
            # Find inactive clients (no activity for 60 seconds)
            for client_address, client_info in self.clients.items():
                if current_time - client_info['last_seen'] > 60:
                    inactive_clients.append(client_address)
            
            # Remove inactive clients
            for client_address in inactive_clients:
                username = self.clients[client_address]['username']
                
                # Remove from all groups
                for group_name in list(self.groups.keys()):
                    if client_address in self.groups[group_name]:
                        self.groups[group_name].remove(client_address)
                        
                    # Remove empty groups
                    if not self.groups[group_name]:
                        del self.groups[group_name]
                
                # Remove from clients list
                del self.clients[client_address]
                
                # Notify other clients
                self.broadcast_system_message(f"{username} has timed out")
            
            # Sleep for 10 seconds
            time.sleep(10)


if __name__ == "__main__":
    # Get port from command line if provided
    port = 5000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    # Start the server
    server = UDPGroupChatServer(port=port)
    server.start() 