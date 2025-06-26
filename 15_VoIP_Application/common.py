"""
Common utilities and settings for the VoIP application.
"""
import socket
import pickle
import struct

# Audio settings
CHUNK = 1024
FORMAT = 'int16'
CHANNELS = 1
RATE = 44100

# Network settings
DEFAULT_PORT = 5000
BUFFER_SIZE = 4096
HEADER_SIZE = 10

# Message types
CONNECT = 'CONNECT'
DISCONNECT = 'DISCONNECT'
AUDIO_DATA = 'AUDIO_DATA'
TEXT_MESSAGE = 'TEXT_MESSAGE'
USER_LIST = 'USER_LIST'

def send_msg(sock, msg_type, data):
    """
    Send a message with a header containing the message size.
    
    Args:
        sock: Socket to send data through
        msg_type: Type of message being sent
        data: Data to send
    """
    message = {
        'type': msg_type,
        'data': data
    }
    
    # Serialize the message
    msg = pickle.dumps(message)
    
    # Create a header with the message size
    header = struct.pack("!I", len(msg))
    
    # Send the header followed by the message
    try:
        sock.sendall(header + msg)
        return True
    except (ConnectionResetError, BrokenPipeError):
        print("Connection lost")
        return False

def recv_msg(sock):
    """
    Receive a message with a header containing the message size.
    
    Args:
        sock: Socket to receive data from
        
    Returns:
        Tuple of (message_type, data) or None if error
    """
    try:
        # Receive the header containing the message size
        header = sock.recv(4)
        if not header or len(header) < 4:
            return None
        
        # Unpack the header to get the message size
        msg_size = struct.unpack("!I", header)[0]
        
        # Receive the message
        data = b""
        remaining = msg_size
        while remaining > 0:
            chunk = sock.recv(min(remaining, BUFFER_SIZE))
            if not chunk:
                return None
            data += chunk
            remaining -= len(chunk)
        
        # Deserialize the message
        message = pickle.loads(data)
        return message['type'], message['data']
    
    except (ConnectionResetError, struct.error, pickle.UnpicklingError):
        return None 