#!/usr/bin/env python3
"""
Remote Control Client

This script provides a client interface to connect to a remote control server
and perform various operations like executing commands, transferring files,
and monitoring system information.
"""

import argparse
import base64
import cmd
import getpass
import io
import os
import socket
import ssl
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

try:
    from PIL import Image
    IMAGE_AVAILABLE = True
except ImportError:
    IMAGE_AVAILABLE = False
    print("Warning: PIL module not available. Screenshot viewing will be disabled.")

# Import common utilities
from common import (
    CommandType, StatusCode, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_CERT_FILE,
    create_ssl_context, send_message, receive_message, send_file, receive_file,
    create_command
)

class RemoteControlClient(cmd.Cmd):
    """Interactive command-line interface for remote control client."""
    
    intro = """
Remote Control Client
Type 'help' or '?' to list commands.
Type 'exit' or 'quit' to exit.
"""
    prompt = "> "
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                cert_file: str = DEFAULT_CERT_FILE):
        """
        Initialize the client.
        
        Args:
            host: Host address to connect to
            port: Port to connect to
            cert_file: Path to SSL certificate file
        """
        super().__init__()
        self.host = host
        self.port = port
        self.cert_file = cert_file
        self.socket = None
        self.authenticated = False
        self.download_dir = "downloads"
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        
    def connect(self) -> bool:
        """
        Connect to the server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Wrap socket with SSL
            ssl_context = create_ssl_context(is_server=False, cert_file=self.cert_file)
            self.socket = ssl_context.wrap_socket(self.socket, server_hostname=self.host)
            
            # Connect to server
            self.socket.connect((self.host, self.port))
            
            print(f"Connected to {self.host}:{self.port}")
            
            # Check if authentication is required
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                self.disconnect()
                return False
                
            if response.get('status') == StatusCode.AUTH_REQUIRED.name:
                # Authentication required
                return self._authenticate()
            elif response.get('status') == StatusCode.AUTH_SUCCESS.name:
                # No authentication required
                self.authenticated = True
                print("Authentication not required")
                return True
            else:
                # Unexpected response
                print(f"Error: Unexpected response from server: {response.get('message', 'Unknown error')}")
                self.disconnect()
                return False
                
        except ConnectionRefusedError:
            print(f"Error: Connection refused by {self.host}:{self.port}")
            return False
        except ssl.SSLError as e:
            print(f"SSL error: {e}")
            return False
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
            
    def _authenticate(self) -> bool:
        """
        Authenticate with the server.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Prompt for password
            password = getpass.getpass("Password: ")
            
            # Send authentication command
            send_message(self.socket, create_command(
                CommandType.AUTHENTICATE,
                password=password
            ))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                self.disconnect()
                return False
                
            if response.get('status') == StatusCode.AUTH_SUCCESS.name:
                # Authentication successful
                self.authenticated = True
                print("Authentication successful")
                return True
            else:
                # Authentication failed
                print("Authentication failed")
                self.disconnect()
                return False
                
        except Exception as e:
            print(f"Error during authentication: {e}")
            self.disconnect()
            return False
            
    def disconnect(self):
        """Disconnect from the server."""
        if self.socket:
            try:
                # Send disconnect command if authenticated
                if self.authenticated:
                    send_message(self.socket, create_command(CommandType.DISCONNECT))
                
                # Close socket
                self.socket.close()
            except:
                pass
            finally:
                self.socket = None
                self.authenticated = False
                
        print("Disconnected from server")
        
    def _check_connected(self) -> bool:
        """
        Check if client is connected and authenticated.
        
        Returns:
            True if connected and authenticated, False otherwise
        """
        if not self.socket:
            print("Not connected to server. Use 'connect' command first.")
            return False
            
        if not self.authenticated:
            print("Not authenticated. Use 'connect' command first.")
            return False
            
        return True
        
    def do_connect(self, arg):
        """Connect to the server."""
        if self.socket:
            print("Already connected. Disconnect first.")
            return
            
        self.connect()
        
    def do_disconnect(self, arg):
        """Disconnect from the server."""
        self.disconnect()
        
    def do_exit(self, arg):
        """Exit the client."""
        self.disconnect()
        return True
        
    def do_quit(self, arg):
        """Exit the client."""
        return self.do_exit(arg)
        
    def do_execute(self, arg):
        """
        Execute a command on the server.
        Usage: execute <command>
        """
        if not self._check_connected():
            return
            
        if not arg:
            print("Usage: execute <command>")
            return
            
        try:
            # Send execute command
            send_message(self.socket, create_command(
                CommandType.EXECUTE,
                command=arg
            ))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Process response
            status = response.get('status')
            message = response.get('message', '')
            data = response.get('data', {})
            
            if status == StatusCode.SUCCESS.name or status == StatusCode.ERROR.name:
                # Print command output
                stdout = data.get('stdout', '')
                stderr = data.get('stderr', '')
                exit_code = data.get('exit_code', -1)
                
                if stdout:
                    print(stdout, end='')
                if stderr:
                    print(stderr, end='')
                    
                if exit_code != 0:
                    print(f"Command exited with code {exit_code}")
            else:
                # Error
                print(f"Error: {message}")
                
        except Exception as e:
            print(f"Error executing command: {e}")
            
    def do_upload(self, arg):
        """
        Upload a file to the server.
        Usage: upload <local_path> <remote_path>
        """
        if not self._check_connected():
            return
            
        args = arg.split()
        if len(args) != 2:
            print("Usage: upload <local_path> <remote_path>")
            return
            
        local_path, remote_path = args
        
        # Check if local file exists
        if not os.path.isfile(local_path):
            print(f"Error: Local file not found: {local_path}")
            return
            
        try:
            # Send upload command
            send_message(self.socket, create_command(
                CommandType.UPLOAD,
                remote_path=remote_path
            ))
            
            # Wait for server to be ready
            response = receive_message(self.socket)
            if not response or response.get('status') != StatusCode.SUCCESS.name:
                print(f"Error: Server not ready to receive file: {response.get('message', 'Unknown error')}")
                return
                
            # Send file
            if send_file(self.socket, local_path):
                # Get final response
                response = receive_message(self.socket)
                if response and response.get('status') == StatusCode.SUCCESS.name:
                    print(response.get('message', 'File uploaded successfully'))
                else:
                    print(f"Error uploading file: {response.get('message', 'Unknown error')}")
            else:
                print("Error sending file")
                
        except Exception as e:
            print(f"Error uploading file: {e}")
            
    def do_download(self, arg):
        """
        Download a file from the server.
        Usage: download <remote_path> [local_path]
        If local_path is not specified, the file will be saved in the downloads directory.
        """
        if not self._check_connected():
            return
            
        args = arg.split()
        if len(args) < 1 or len(args) > 2:
            print("Usage: download <remote_path> [local_path]")
            return
            
        remote_path = args[0]
        
        # Determine local path
        if len(args) == 2:
            local_path = args[1]
        else:
            filename = os.path.basename(remote_path)
            local_path = os.path.join(self.download_dir, filename)
            
        try:
            # Send download command
            send_message(self.socket, create_command(
                CommandType.DOWNLOAD,
                remote_path=remote_path
            ))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Check if file exists on server
            status = response.get('status')
            message = response.get('message', '')
            
            if status != StatusCode.SUCCESS.name:
                print(f"Error: {message}")
                return
                
            # Receive file
            if receive_file(self.socket, local_path):
                print(f"File downloaded to {local_path}")
            else:
                print("Error receiving file")
                
        except Exception as e:
            print(f"Error downloading file: {e}")
            
    def do_screenshot(self, arg):
        """
        Take a screenshot of the remote computer.
        Usage: screenshot [save_path]
        If save_path is specified, the screenshot will be saved to that path.
        Otherwise, it will be displayed (if PIL is available) or saved to the downloads directory.
        """
        if not self._check_connected():
            return
            
        save_path = arg.strip() if arg else None
        
        try:
            # Send screenshot command
            send_message(self.socket, create_command(CommandType.SCREENSHOT))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Check if screenshot was captured
            status = response.get('status')
            message = response.get('message', '')
            data = response.get('data', {})
            
            if status != StatusCode.SUCCESS.name:
                print(f"Error: {message}")
                return
                
            # Get image data
            img_base64 = data.get('image')
            if not img_base64:
                print("Error: No image data received")
                return
                
            # Decode image
            img_bytes = base64.b64decode(img_base64)
            
            if save_path:
                # Save to specified path
                with open(save_path, 'wb') as f:
                    f.write(img_bytes)
                print(f"Screenshot saved to {save_path}")
            elif IMAGE_AVAILABLE:
                # Display image
                img = Image.open(io.BytesIO(img_bytes))
                img.show()
                
                # Also save a copy
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.download_dir, f"screenshot_{timestamp}.png")
                img.save(save_path)
                print(f"Screenshot saved to {save_path}")
            else:
                # Save to downloads directory
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.download_dir, f"screenshot_{timestamp}.png")
                with open(save_path, 'wb') as f:
                    f.write(img_bytes)
                print(f"Screenshot saved to {save_path}")
                
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            
    def do_sysinfo(self, arg):
        """
        Get system information from the remote computer.
        Usage: sysinfo
        """
        if not self._check_connected():
            return
            
        try:
            # Send sysinfo command
            send_message(self.socket, create_command(CommandType.SYSINFO))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Check if system information was retrieved
            status = response.get('status')
            message = response.get('message', '')
            data = response.get('data', {})
            
            if status != StatusCode.SUCCESS.name:
                print(f"Error: {message}")
                return
                
            # Print system information
            platform = data.get('platform', {})
            print("\n=== System Information ===")
            print(f"System: {platform.get('system', 'Unknown')}")
            print(f"Release: {platform.get('release', 'Unknown')}")
            print(f"Version: {platform.get('version', 'Unknown')}")
            print(f"Machine: {platform.get('machine', 'Unknown')}")
            print(f"Processor: {platform.get('processor', 'Unknown')}")
            print(f"Hostname: {platform.get('hostname', 'Unknown')}")
            print(f"Python Version: {platform.get('python_version', 'Unknown')}")
            
            # Print CPU information
            cpu = data.get('cpu', {})
            if cpu:
                print("\n=== CPU Information ===")
                print(f"CPU Usage: {cpu.get('percent', 'Unknown')}%")
                print(f"CPU Count: {cpu.get('count', 'Unknown')}")
                
                freq = cpu.get('freq', {})
                if freq and freq.get('current'):
                    print(f"CPU Frequency: {freq.get('current', 0) / 1000:.2f} GHz")
                    
            # Print memory information
            memory = data.get('memory', {})
            if memory:
                print("\n=== Memory Information ===")
                total_gb = memory.get('total', 0) / (1024 ** 3)
                used_gb = memory.get('used', 0) / (1024 ** 3)
                free_gb = memory.get('free', 0) / (1024 ** 3)
                print(f"Total Memory: {total_gb:.2f} GB")
                print(f"Used Memory: {used_gb:.2f} GB")
                print(f"Free Memory: {free_gb:.2f} GB")
                print(f"Memory Usage: {memory.get('percent', 'Unknown')}%")
                
            # Print disk information
            disk = data.get('disk', {})
            if disk:
                print("\n=== Disk Information ===")
                total_gb = disk.get('total', 0) / (1024 ** 3)
                used_gb = disk.get('used', 0) / (1024 ** 3)
                free_gb = disk.get('free', 0) / (1024 ** 3)
                print(f"Total Disk: {total_gb:.2f} GB")
                print(f"Used Disk: {used_gb:.2f} GB")
                print(f"Free Disk: {free_gb:.2f} GB")
                print(f"Disk Usage: {disk.get('percent', 'Unknown')}%")
                
            # Print network information
            network = data.get('network', {})
            if network:
                print("\n=== Network Information ===")
                bytes_sent_mb = network.get('bytes_sent', 0) / (1024 ** 2)
                bytes_recv_mb = network.get('bytes_recv', 0) / (1024 ** 2)
                print(f"Bytes Sent: {bytes_sent_mb:.2f} MB")
                print(f"Bytes Received: {bytes_recv_mb:.2f} MB")
                print(f"Packets Sent: {network.get('packets_sent', 'Unknown')}")
                print(f"Packets Received: {network.get('packets_recv', 'Unknown')}")
                
            # Print battery information
            battery = data.get('battery')
            if battery:
                print("\n=== Battery Information ===")
                print(f"Battery Level: {battery.get('percent', 'Unknown')}%")
                print(f"Power Plugged: {'Yes' if battery.get('power_plugged') else 'No'}")
                
                secs_left = battery.get('secsleft')
                if secs_left and secs_left != -1:  # -1 means power plugged or no battery
                    hours = secs_left // 3600
                    minutes = (secs_left % 3600) // 60
                    print(f"Battery Time Left: {hours}h {minutes}m")
                    
            # Print boot time
            boot_time = data.get('boot_time')
            if boot_time:
                print(f"\nBoot Time: {boot_time}")
                
            print(f"\nTimestamp: {data.get('timestamp', 'Unknown')}")
            
        except Exception as e:
            print(f"Error retrieving system information: {e}")
            
    def do_processes(self, arg):
        """
        List processes running on the remote computer.
        Usage: processes
        """
        if not self._check_connected():
            return
            
        try:
            # Send processes command
            send_message(self.socket, create_command(CommandType.PROCESSES))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Check if process list was retrieved
            status = response.get('status')
            message = response.get('message', '')
            data = response.get('data', {})
            
            if status != StatusCode.SUCCESS.name:
                print(f"Error: {message}")
                return
                
            # Get process list
            processes = data.get('processes', [])
            
            # Print process list
            print(f"\n{'PID':<10} {'CPU%':<8} {'MEM%':<8} {'USER':<15} {'NAME':<30}")
            print("-" * 71)
            
            for proc in sorted(processes, key=lambda p: p.get('memory_percent', 0), reverse=True):
                pid = proc.get('pid', 'N/A')
                name = proc.get('name', 'Unknown')[:30]
                username = proc.get('username', 'Unknown')[:15]
                mem_percent = proc.get('memory_percent', 0)
                cpu_percent = proc.get('cpu_percent', 0)
                
                print(f"{pid:<10} {cpu_percent:<8.1f} {mem_percent:<8.1f} {username:<15} {name:<30}")
                
            print(f"\nTotal processes: {len(processes)}")
            print(f"Timestamp: {data.get('timestamp', 'Unknown')}")
            
        except Exception as e:
            print(f"Error retrieving process list: {e}")
            
    def do_terminate(self, arg):
        """
        Terminate a process on the remote computer.
        Usage: terminate <pid>
        """
        if not self._check_connected():
            return
            
        if not arg:
            print("Usage: terminate <pid>")
            return
            
        try:
            pid = int(arg)
        except ValueError:
            print("Error: PID must be a number")
            return
            
        try:
            # Send terminate command
            send_message(self.socket, create_command(
                CommandType.TERMINATE,
                pid=pid
            ))
            
            # Get response
            response = receive_message(self.socket)
            if not response:
                print("Error: No response from server")
                return
                
            # Check if process was terminated
            status = response.get('status')
            message = response.get('message', '')
            
            if status == StatusCode.SUCCESS.name:
                print(message)
            else:
                print(f"Error: {message}")
                
        except Exception as e:
            print(f"Error terminating process: {e}")
            
    def do_help(self, arg):
        """Show help message."""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            # Show general help
            print("\nAvailable commands:")
            print("  connect      - Connect to the server")
            print("  disconnect   - Disconnect from the server")
            print("  execute      - Execute a command on the server")
            print("  upload       - Upload a file to the server")
            print("  download     - Download a file from the server")
            print("  screenshot   - Take a screenshot of the remote computer")
            print("  sysinfo      - Get system information from the remote computer")
            print("  processes    - List processes running on the remote computer")
            print("  terminate    - Terminate a process on the remote computer")
            print("  exit/quit    - Exit the client")
            print("  help         - Show this help message")
            print("\nFor help on a specific command, type: help <command>")

def main():
    """Main function to parse arguments and start the client."""
    parser = argparse.ArgumentParser(description="Remote Control Client")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host address to connect to")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to connect to")
    parser.add_argument("--cert", default=DEFAULT_CERT_FILE, help="Path to SSL certificate file")
    
    args = parser.parse_args()
    
    # Create client
    client = RemoteControlClient(
        host=args.host,
        port=args.port,
        cert_file=args.cert
    )
    
    # Connect to server if host is specified
    if args.host != DEFAULT_HOST:
        if client.connect():
            # Start command loop
            client.cmdloop()
        else:
            sys.exit(1)
    else:
        # Start command loop without connecting
        client.cmdloop()

if __name__ == "__main__":
    main() 