"""
VoIP Server
Handles client connections and routes audio data between clients.
"""
import socket
import threading
import time
import sys
import signal
import logging
from common import (
    DEFAULT_PORT, BUFFER_SIZE, send_msg, recv_msg,
    CONNECT, DISCONNECT, AUDIO_DATA, TEXT_MESSAGE, USER_LIST
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VoIPServer:
    def __init__(self, host='0.0.0.0', port=DEFAULT_PORT):
        """
        Initialize the VoIP server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.clients = {}  # {client_address: (socket, username)}
        self.rooms = {}    # {room_name: [client_addresses]}
        
    def start(self):
        """Start the server."""
        try:
            # Create the server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Start the accept thread
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Start the user list update thread
            update_thread = threading.Thread(target=self._update_user_list)
            update_thread.daemon = True
            update_thread.start()
            
            # Wait for keyboard interrupt
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Server stopping...")
        except Exception as e:
            logger.error(f"Error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the server."""
        self.running = False
        
        # Close all client connections
        for client_addr in list(self.clients.keys()):
            self._disconnect_client(client_addr)
            
        # Close the server socket
        if self.server_socket:
            self.server_socket.close()
            
        logger.info("Server stopped")
        
    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                client_socket, client_addr = self.server_socket.accept()
                client_addr = f"{client_addr[0]}:{client_addr[1]}"
                
                logger.info(f"New connection from {client_addr}")
                
                # Start a thread to handle the client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except OSError:
                break
                
    def _handle_client(self, client_socket, client_addr):
        """
        Handle a client connection.
        
        Args:
            client_socket: Socket for the client connection
            client_addr: Address of the client
        """
        username = None
        room = "default"  # Default room
        
        try:
            # Wait for the initial connect message
            msg = recv_msg(client_socket)
            if not msg or msg[0] != CONNECT:
                logger.warning(f"Invalid initial message from {client_addr}")
                client_socket.close()
                return
                
            # Extract username from connect message
            username = msg[1].get('username', f"User_{client_addr}")
            requested_room = msg[1].get('room', room)
            
            # Add client to clients dict and room
            self.clients[client_addr] = (client_socket, username)
            
            # Create room if it doesn't exist
            if requested_room not in self.rooms:
                self.rooms[requested_room] = []
                
            # Add client to room
            self.rooms[requested_room].append(client_addr)
            room = requested_room
            
            logger.info(f"{username} ({client_addr}) joined room {room}")
            
            # Send confirmation to client
            send_msg(client_socket, CONNECT, {
                'status': 'connected',
                'room': room
            })
            
            # Broadcast user list to all clients in the room
            self._broadcast_user_list(room)
            
            # Handle client messages
            while self.running:
                msg = recv_msg(client_socket)
                if not msg:
                    break
                    
                msg_type, data = msg
                
                if msg_type == DISCONNECT:
                    logger.info(f"{username} ({client_addr}) disconnected")
                    break
                    
                elif msg_type == AUDIO_DATA:
                    # Forward audio data to all other clients in the same room
                    self._forward_audio(client_addr, data, room)
                    
                elif msg_type == TEXT_MESSAGE:
                    # Forward text message to all clients in the same room
                    self._forward_text_message(client_addr, username, data, room)
                    
        except Exception as e:
            logger.error(f"Error handling client {client_addr}: {e}")
            
        finally:
            # Disconnect client
            self._disconnect_client(client_addr, room)
            
    def _disconnect_client(self, client_addr, room=None):
        """
        Disconnect a client.
        
        Args:
            client_addr: Address of the client to disconnect
            room: Room the client is in (if known)
        """
        if client_addr in self.clients:
            # Get client info
            client_socket, username = self.clients[client_addr]
            
            # Remove from clients dict
            del self.clients[client_addr]
            
            # Close the socket
            try:
                client_socket.close()
            except:
                pass
                
            # Find and remove from room
            for r_name, clients in self.rooms.items():
                if client_addr in clients:
                    clients.remove(client_addr)
                    room = r_name
                    break
                    
            # Remove empty rooms
            if room and room in self.rooms and not self.rooms[room]:
                del self.rooms[room]
                
            logger.info(f"{username} ({client_addr}) removed from room {room}")
            
            # Broadcast updated user list
            if room:
                self._broadcast_user_list(room)
                
    def _forward_audio(self, sender_addr, audio_data, room):
        """
        Forward audio data to all clients in a room except the sender.
        
        Args:
            sender_addr: Address of the sender
            audio_data: Audio data to forward
            room: Room to forward to
        """
        if room not in self.rooms:
            return
            
        for client_addr in self.rooms[room]:
            if client_addr != sender_addr and client_addr in self.clients:
                client_socket, _ = self.clients[client_addr]
                send_msg(client_socket, AUDIO_DATA, audio_data)
                
    def _forward_text_message(self, sender_addr, sender_name, message, room):
        """
        Forward a text message to all clients in a room.
        
        Args:
            sender_addr: Address of the sender
            sender_name: Name of the sender
            message: Message to forward
            room: Room to forward to
        """
        if room not in self.rooms:
            return
            
        msg_data = {
            'sender': sender_name,
            'message': message,
            'timestamp': time.time()
        }
        
        for client_addr in self.rooms[room]:
            if client_addr in self.clients:
                client_socket, _ = self.clients[client_addr]
                send_msg(client_socket, TEXT_MESSAGE, msg_data)
                
    def _broadcast_user_list(self, room):
        """
        Broadcast the user list to all clients in a room.
        
        Args:
            room: Room to broadcast to
        """
        if room not in self.rooms:
            return
            
        # Build user list
        users = []
        for client_addr in self.rooms[room]:
            if client_addr in self.clients:
                _, username = self.clients[client_addr]
                users.append({
                    'username': username,
                    'address': client_addr
                })
                
        # Send to all clients in the room
        for client_addr in self.rooms[room]:
            if client_addr in self.clients:
                client_socket, _ = self.clients[client_addr]
                send_msg(client_socket, USER_LIST, {
                    'room': room,
                    'users': users
                })
                
    def _update_user_list(self):
        """Periodically update the user list for all rooms."""
        while self.running:
            for room in list(self.rooms.keys()):
                self._broadcast_user_list(room)
            time.sleep(30)  # Update every 30 seconds

def signal_handler(sig, frame):
    """Handle Ctrl+C."""
    print("\nShutting down server...")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse command line arguments
    port = DEFAULT_PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
            
    # Start the server
    server = VoIPServer(port=port)
    server.start() 