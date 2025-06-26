#!/usr/bin/env python3
"""
Common utilities and constants for the Remote Control application.
Shared between client and server components.
"""

import json
import os
import socket
import ssl
import struct
import sys
import logging
from enum import Enum, auto
from typing import Any, Dict, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Default settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 9999
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_CERT_DIR = os.path.join(os.path.dirname(__file__), 'certs')
DEFAULT_CERT_FILE = os.path.join(DEFAULT_CERT_DIR, 'server.crt')
DEFAULT_KEY_FILE = os.path.join(DEFAULT_CERT_DIR, 'server.key')

# Command types
class CommandType(Enum):
    AUTHENTICATE = auto()
    EXECUTE = auto()
    UPLOAD = auto()
    DOWNLOAD = auto()
    SCREENSHOT = auto()
    SYSINFO = auto()
    PROCESSES = auto()
    TERMINATE = auto()
    DISCONNECT = auto()

# Response status codes
class StatusCode(Enum):
    SUCCESS = auto()
    ERROR = auto()
    AUTH_REQUIRED = auto()
    AUTH_FAILED = auto()
    AUTH_SUCCESS = auto()
    FILE_NOT_FOUND = auto()
    PERMISSION_DENIED = auto()
    INVALID_COMMAND = auto()

def create_ssl_context(is_server: bool = False, 
                      cert_file: str = DEFAULT_CERT_FILE, 
                      key_file: str = DEFAULT_KEY_FILE) -> ssl.SSLContext:
    """
    Create an SSL context for secure communication.
    
    Args:
        is_server: Whether this is for server or client
        cert_file: Path to the certificate file
        key_file: Path to the key file (server only)
        
    Returns:
        An SSL context configured for client or server
    """
    context = ssl.create_default_context(
        ssl.Purpose.CLIENT_AUTH if is_server else ssl.Purpose.SERVER_AUTH
    )
    
    if is_server:
        context.verify_mode = ssl.CERT_OPTIONAL
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    else:
        # For development/testing, we can use this to accept self-signed certs
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    
    return context

def send_message(sock: socket.socket, data: Dict[str, Any]) -> bool:
    """
    Send a message over the socket with a length prefix.
    
    Args:
        sock: Socket to send data through
        data: Dictionary to be sent as JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert dictionary to JSON string
        json_data = json.dumps(data)
        
        # Convert JSON string to bytes
        message = json_data.encode('utf-8')
        
        # Prefix with message length (4-byte integer)
        message_len = len(message)
        prefix = struct.pack('!I', message_len)
        
        # Send the prefix followed by the message
        sock.sendall(prefix + message)
        return True
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return False

def receive_message(sock: socket.socket) -> Optional[Dict[str, Any]]:
    """
    Receive a message from the socket with a length prefix.
    
    Args:
        sock: Socket to receive data from
        
    Returns:
        Received dictionary or None if an error occurred
    """
    try:
        # Receive the 4-byte length prefix
        prefix = sock.recv(4)
        if not prefix:
            return None
        
        # Unpack the prefix to get the message length
        message_len = struct.unpack('!I', prefix)[0]
        
        # Receive the message in chunks
        chunks = []
        bytes_received = 0
        while bytes_received < message_len:
            chunk = sock.recv(min(DEFAULT_BUFFER_SIZE, message_len - bytes_received))
            if not chunk:
                return None
            chunks.append(chunk)
            bytes_received += len(chunk)
        
        # Combine chunks and decode
        message = b''.join(chunks).decode('utf-8')
        
        # Parse JSON
        return json.loads(message)
    except Exception as e:
        logging.error(f"Error receiving message: {e}")
        return None

def send_file(sock: socket.socket, file_path: str) -> bool:
    """
    Send a file over the socket.
    
    Args:
        sock: Socket to send data through
        file_path: Path to the file to send
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if file exists
        if not os.path.isfile(file_path):
            return False
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Send file size
        sock.sendall(struct.pack('!Q', file_size))
        
        # Send file content
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(DEFAULT_BUFFER_SIZE)
                if not data:
                    break
                sock.sendall(data)
        
        return True
    except Exception as e:
        logging.error(f"Error sending file: {e}")
        return False

def receive_file(sock: socket.socket, file_path: str) -> bool:
    """
    Receive a file from the socket.
    
    Args:
        sock: Socket to receive data from
        file_path: Path where to save the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Receive file size
        size_data = sock.recv(8)
        if not size_data:
            return False
        
        file_size = struct.unpack('!Q', size_data)[0]
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        # Receive and write file content
        with open(file_path, 'wb') as f:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = sock.recv(min(DEFAULT_BUFFER_SIZE, file_size - bytes_received))
                if not chunk:
                    return False
                f.write(chunk)
                bytes_received += len(chunk)
        
        return True
    except Exception as e:
        logging.error(f"Error receiving file: {e}")
        if os.path.exists(file_path):
            os.remove(file_path)  # Clean up partial file
        return False

def create_command(command_type: CommandType, **kwargs) -> Dict[str, Any]:
    """
    Create a command dictionary.
    
    Args:
        command_type: Type of command
        **kwargs: Additional command parameters
        
    Returns:
        Command dictionary
    """
    command = {
        'type': command_type.name,
        'timestamp': import_time_module().time()
    }
    command.update(kwargs)
    return command

def create_response(status: StatusCode, message: str = "", data: Any = None) -> Dict[str, Any]:
    """
    Create a response dictionary.
    
    Args:
        status: Status code
        message: Response message
        data: Additional response data
        
    Returns:
        Response dictionary
    """
    return {
        'status': status.name,
        'message': message,
        'data': data,
        'timestamp': import_time_module().time()
    }

def import_time_module():
    """Import time module dynamically to avoid circular imports."""
    import time
    return time

def get_platform_info() -> Dict[str, str]:
    """
    Get platform information.
    
    Returns:
        Dictionary with platform information
    """
    import platform
    
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'python_version': platform.python_version()
    }

def is_admin() -> bool:
    """
    Check if the current process has administrator/root privileges.
    
    Returns:
        True if running with admin/root privileges, False otherwise
    """
    try:
        if os.name == 'nt':  # Windows
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:  # Unix/Linux/Mac
            return os.geteuid() == 0
    except:
        return False 