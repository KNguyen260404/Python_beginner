#!/usr/bin/env python3
"""
Remote Control Server

This script runs a server that allows remote clients to connect and control
this computer, execute commands, transfer files, and monitor system information.
"""

import argparse
import base64
import hashlib
import io
import os
import socket
import ssl
import subprocess
import sys
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil module not available. System monitoring features will be limited.")

try:
    from PIL import ImageGrab
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("Warning: PIL module not available. Screenshot functionality will be disabled.")

# Import common utilities
from common import (
    CommandType, StatusCode, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_CERT_FILE, DEFAULT_KEY_FILE,
    create_ssl_context, send_message, receive_message, send_file, receive_file,
    create_response, get_platform_info, is_admin
)

class RemoteControlServer:
    """Server for remote control functionality."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                password: str = None, cert_file: str = DEFAULT_CERT_FILE,
                key_file: str = DEFAULT_KEY_FILE):
        """
        Initialize the server.
        
        Args:
            host: Host address to bind to
            port: Port to listen on
            password: Password for authentication
            cert_file: Path to SSL certificate file
            key_file: Path to SSL key file
        """
        self.host = host
        self.port = port
        self.password_hash = self._hash_password(password) if password else None
        self.cert_file = cert_file
        self.key_file = key_file
        self.server_socket = None
        self.running = False
        self.clients = {}  # Dictionary to track connected clients
        self.client_counter = 0  # Counter for assigning client IDs
        
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        return hashlib.sha256(password.encode()).hexdigest()
        
    def start(self):
        """Start the server and listen for connections."""
        try:
            # Create a socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to host and port
            self.server_socket.bind((self.host, self.port))
            
            # Start listening
            self.server_socket.listen(5)
            self.running = True
            
            print(f"Server started on {self.host}:{self.port}")
            print(f"Running with {'admin' if is_admin() else 'regular'} privileges")
            
            # Accept connections in a loop
            while self.running:
                try:
                    # Accept a connection
                    client_socket, client_address = self.server_socket.accept()
                    
                    # Wrap socket with SSL
                    ssl_context = create_ssl_context(is_server=True, 
                                                   cert_file=self.cert_file, 
                                                   key_file=self.key_file)
                    client_socket = ssl_context.wrap_socket(client_socket, server_side=True)
                    
                    print(f"Connection from {client_address[0]}:{client_address[1]}")
                    
                    # Increment client counter and assign ID
                    self.client_counter += 1
                    client_id = self.client_counter
                    
                    # Store client information
                    self.clients[client_id] = {
                        'socket': client_socket,
                        'address': client_address,
                        'authenticated': False,
                        'last_activity': time.time(),
                        'connected_since': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_id,),
                        daemon=True
                    )
                    client_thread.start()
                    
                except ssl.SSLError as e:
                    print(f"SSL error: {e}")
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the server and close all connections."""
        self.running = False
        
        # Close all client connections
        for client_id in list(self.clients.keys()):
            try:
                self.clients[client_id]['socket'].close()
            except:
                pass
            del self.clients[client_id]
            
        # Close server socket
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            
        print("Server stopped")
        
    def _handle_client(self, client_id: int):
        """
        Handle communication with a client.
        
        Args:
            client_id: ID of the client to handle
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        client_address = client['address']
        
        try:
            # Send authentication request if password is set
            if self.password_hash:
                send_message(client_socket, create_response(
                    StatusCode.AUTH_REQUIRED,
                    "Authentication required"
                ))
            else:
                # No password set, client is automatically authenticated
                self.clients[client_id]['authenticated'] = True
                send_message(client_socket, create_response(
                    StatusCode.AUTH_SUCCESS,
                    "Authentication successful"
                ))
                
            # Process commands from client
            while self.running:
                # Receive command
                command = receive_message(client_socket)
                if not command:
                    break
                    
                # Update last activity timestamp
                self.clients[client_id]['last_activity'] = time.time()
                
                # Process command
                self._process_command(client_id, command)
                
        except Exception as e:
            print(f"Error handling client {client_address[0]}:{client_address[1]}: {e}")
        finally:
            # Clean up
            try:
                client_socket.close()
            except:
                pass
                
            # Remove client from dictionary
            if client_id in self.clients:
                del self.clients[client_id]
                
            print(f"Client {client_address[0]}:{client_address[1]} disconnected")
            
    def _process_command(self, client_id: int, command: Dict[str, Any]):
        """
        Process a command from a client.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        command_type = command.get('type')
        
        # Handle authentication
        if command_type == CommandType.AUTHENTICATE.name:
            if not self.password_hash:
                # No password set, client is already authenticated
                send_message(client_socket, create_response(
                    StatusCode.AUTH_SUCCESS,
                    "Authentication successful"
                ))
                return
                
            password = command.get('password', '')
            password_hash = self._hash_password(password)
            
            if password_hash == self.password_hash:
                # Authentication successful
                self.clients[client_id]['authenticated'] = True
                send_message(client_socket, create_response(
                    StatusCode.AUTH_SUCCESS,
                    "Authentication successful"
                ))
            else:
                # Authentication failed
                send_message(client_socket, create_response(
                    StatusCode.AUTH_FAILED,
                    "Authentication failed"
                ))
                
            return
            
        # Check if client is authenticated
        if not client.get('authenticated', False) and self.password_hash:
            send_message(client_socket, create_response(
                StatusCode.AUTH_REQUIRED,
                "Authentication required"
            ))
            return
            
        # Process other commands
        if command_type == CommandType.EXECUTE.name:
            self._handle_execute(client_id, command)
        elif command_type == CommandType.UPLOAD.name:
            self._handle_upload(client_id, command)
        elif command_type == CommandType.DOWNLOAD.name:
            self._handle_download(client_id, command)
        elif command_type == CommandType.SCREENSHOT.name:
            self._handle_screenshot(client_id, command)
        elif command_type == CommandType.SYSINFO.name:
            self._handle_sysinfo(client_id, command)
        elif command_type == CommandType.PROCESSES.name:
            self._handle_processes(client_id, command)
        elif command_type == CommandType.TERMINATE.name:
            self._handle_terminate(client_id, command)
        elif command_type == CommandType.DISCONNECT.name:
            # Client wants to disconnect
            client_socket.close()
            if client_id in self.clients:
                del self.clients[client_id]
        else:
            # Invalid command
            send_message(client_socket, create_response(
                StatusCode.INVALID_COMMAND,
                f"Invalid command: {command_type}"
            ))
            
    def _handle_execute(self, client_id: int, command: Dict[str, Any]):
        """
        Handle command execution.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        cmd = command.get('command', '')
        
        try:
            # Execute command
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Get output
            stdout, stderr = process.communicate(timeout=30)
            exit_code = process.returncode
            
            # Send response
            send_message(client_socket, create_response(
                StatusCode.SUCCESS if exit_code == 0 else StatusCode.ERROR,
                f"Command executed with exit code {exit_code}",
                {
                    'stdout': stdout,
                    'stderr': stderr,
                    'exit_code': exit_code
                }
            ))
            
        except subprocess.TimeoutExpired:
            # Command timed out
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                "Command execution timed out"
            ))
        except Exception as e:
            # Error executing command
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error executing command: {e}"
            ))
            
    def _handle_upload(self, client_id: int, command: Dict[str, Any]):
        """
        Handle file upload from client to server.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        remote_path = command.get('remote_path', '')
        
        try:
            # Send acknowledgment to start file transfer
            send_message(client_socket, create_response(
                StatusCode.SUCCESS,
                "Ready to receive file"
            ))
            
            # Receive file
            if receive_file(client_socket, remote_path):
                send_message(client_socket, create_response(
                    StatusCode.SUCCESS,
                    f"File uploaded successfully to {remote_path}"
                ))
            else:
                send_message(client_socket, create_response(
                    StatusCode.ERROR,
                    "Error receiving file"
                ))
                
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error handling upload: {e}"
            ))
            
    def _handle_download(self, client_id: int, command: Dict[str, Any]):
        """
        Handle file download from server to client.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        remote_path = command.get('remote_path', '')
        
        try:
            # Check if file exists
            if not os.path.isfile(remote_path):
                send_message(client_socket, create_response(
                    StatusCode.FILE_NOT_FOUND,
                    f"File not found: {remote_path}"
                ))
                return
                
            # Check if we have permission to read the file
            if not os.access(remote_path, os.R_OK):
                send_message(client_socket, create_response(
                    StatusCode.PERMISSION_DENIED,
                    f"Permission denied: {remote_path}"
                ))
                return
                
            # Send acknowledgment to start file transfer
            send_message(client_socket, create_response(
                StatusCode.SUCCESS,
                "Starting file transfer"
            ))
            
            # Send file
            if send_file(client_socket, remote_path):
                print(f"File {remote_path} sent successfully")
            else:
                print(f"Error sending file {remote_path}")
                
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error handling download: {e}"
            ))
            
    def _handle_screenshot(self, client_id: int, command: Dict[str, Any]):
        """
        Handle screenshot request.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        
        if not SCREENSHOT_AVAILABLE:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                "Screenshot functionality not available. Install PIL (Pillow)."
            ))
            return
            
        try:
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            screenshot.save(img_byte_arr, format='PNG')
            img_bytes = img_byte_arr.getvalue()
            
            # Encode as base64
            img_base64 = base64.b64encode(img_bytes).decode('utf-8')
            
            # Send response
            send_message(client_socket, create_response(
                StatusCode.SUCCESS,
                "Screenshot captured",
                {
                    'image': img_base64,
                    'format': 'PNG',
                    'width': screenshot.width,
                    'height': screenshot.height,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ))
            
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error capturing screenshot: {e}"
            ))
            
    def _handle_sysinfo(self, client_id: int, command: Dict[str, Any]):
        """
        Handle system information request.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        
        try:
            # Get platform information
            platform_info = get_platform_info()
            
            # Get system information using psutil if available
            if PSUTIL_AVAILABLE:
                # CPU information
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_count = psutil.cpu_count(logical=True)
                cpu_freq = psutil.cpu_freq()
                
                # Memory information
                memory = psutil.virtual_memory()
                
                # Disk information
                disk = psutil.disk_usage('/')
                
                # Network information
                net_io = psutil.net_io_counters()
                
                # Battery information
                battery = None
                if hasattr(psutil, 'sensors_battery'):
                    battery_info = psutil.sensors_battery()
                    if battery_info:
                        battery = {
                            'percent': battery_info.percent,
                            'power_plugged': battery_info.power_plugged,
                            'secsleft': battery_info.secsleft
                        }
                
                # Combine all information
                sysinfo = {
                    'platform': platform_info,
                    'cpu': {
                        'percent': cpu_percent,
                        'count': cpu_count,
                        'freq': {
                            'current': cpu_freq.current if cpu_freq else None,
                            'min': cpu_freq.min if cpu_freq else None,
                            'max': cpu_freq.max if cpu_freq else None
                        }
                    },
                    'memory': {
                        'total': memory.total,
                        'available': memory.available,
                        'percent': memory.percent,
                        'used': memory.used,
                        'free': memory.free
                    },
                    'disk': {
                        'total': disk.total,
                        'used': disk.used,
                        'free': disk.free,
                        'percent': disk.percent
                    },
                    'network': {
                        'bytes_sent': net_io.bytes_sent,
                        'bytes_recv': net_io.bytes_recv,
                        'packets_sent': net_io.packets_sent,
                        'packets_recv': net_io.packets_recv
                    },
                    'battery': battery,
                    'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Limited information without psutil
                sysinfo = {
                    'platform': platform_info,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            # Send response
            send_message(client_socket, create_response(
                StatusCode.SUCCESS,
                "System information retrieved",
                sysinfo
            ))
            
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error retrieving system information: {e}"
            ))
            
    def _handle_processes(self, client_id: int, command: Dict[str, Any]):
        """
        Handle process list request.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        
        if not PSUTIL_AVAILABLE:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                "Process listing not available. Install psutil."
            ))
            return
            
        try:
            # Get process information
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_percent', 'cpu_percent', 'create_time']):
                try:
                    pinfo = proc.info
                    pinfo['create_time'] = datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    processes.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            # Send response
            send_message(client_socket, create_response(
                StatusCode.SUCCESS,
                f"Retrieved {len(processes)} processes",
                {
                    'processes': processes,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            ))
            
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error retrieving process list: {e}"
            ))
            
    def _handle_terminate(self, client_id: int, command: Dict[str, Any]):
        """
        Handle process termination request.
        
        Args:
            client_id: ID of the client that sent the command
            command: Command dictionary
        """
        client = self.clients.get(client_id)
        if not client:
            return
            
        client_socket = client['socket']
        pid = command.get('pid')
        
        if not PSUTIL_AVAILABLE:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                "Process termination not available. Install psutil."
            ))
            return
            
        if pid is None:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                "No PID specified"
            ))
            return
            
        try:
            # Try to terminate the process
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()
            
            # Wait for process to terminate
            gone, alive = psutil.wait_procs([process], timeout=3)
            
            if process in gone:
                send_message(client_socket, create_response(
                    StatusCode.SUCCESS,
                    f"Process {pid} ({process_name}) terminated successfully"
                ))
            else:
                # Try to kill the process if termination failed
                process.kill()
                send_message(client_socket, create_response(
                    StatusCode.SUCCESS,
                    f"Process {pid} ({process_name}) killed forcefully"
                ))
                
        except psutil.NoSuchProcess:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"No such process: {pid}"
            ))
        except psutil.AccessDenied:
            send_message(client_socket, create_response(
                StatusCode.PERMISSION_DENIED,
                f"Permission denied to terminate process {pid}"
            ))
        except Exception as e:
            send_message(client_socket, create_response(
                StatusCode.ERROR,
                f"Error terminating process {pid}: {e}"
            ))

def main():
    """Main function to parse arguments and start the server."""
    parser = argparse.ArgumentParser(description="Remote Control Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host address to bind to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to listen on")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--cert", default=DEFAULT_CERT_FILE, help="Path to SSL certificate file")
    parser.add_argument("--key", default=DEFAULT_KEY_FILE, help="Path to SSL key file")
    
    args = parser.parse_args()
    
    # Check if certificate and key files exist
    cert_dir = os.path.dirname(args.cert)
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir, exist_ok=True)
        
    if not os.path.isfile(args.cert) or not os.path.isfile(args.key):
        print("SSL certificate or key file not found.")
        print(f"Please run 'python certs/generate_cert.py' to generate them.")
        print(f"Expected certificate at: {args.cert}")
        print(f"Expected key at: {args.key}")
        return
        
    # Create and start server
    server = RemoteControlServer(
        host=args.host,
        port=args.port,
        password=args.password,
        cert_file=args.cert,
        key_file=args.key
    )
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server.stop()

if __name__ == "__main__":
    main() 