#!/usr/bin/env python3
import os
import sys
import socket
import select
import threading
import time
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, ParseResult
import ssl

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QLineEdit, QSpinBox, QTextEdit, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
                            QCheckBox, QGroupBox, QFileDialog, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt5.QtGui import QIcon, QTextCursor, QColor, QFont


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ProxyServer')


class ProxyRequestHandler(BaseHTTPRequestHandler):
    """
    HTTP request handler for the proxy server
    """
    protocol_version = 'HTTP/1.1'
    timeout = 10
    
    # Class variable to store reference to the GUI
    gui = None
    
    # Class variables for configuration
    blocked_domains = []
    cache_enabled = True
    cache_directory = './cache'
    
    def log_message(self, format, *args):
        """Override to send logs to GUI instead of stderr"""
        if self.gui:
            self.gui.log_message(f"{self.address_string()} - {format % args}")
        else:
            logger.info(format, *args)
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL
        url = self.path
        parsed_url = urlparse(url)
        
        # Check if domain is blocked
        if self._is_domain_blocked(parsed_url.netloc):
            self.send_error(403, "Forbidden - Domain blocked by proxy")
            return
            
        # Try to get from cache if enabled
        if self.cache_enabled and self._serve_from_cache(url):
            return
            
        try:
            # Connect to the remote server
            if parsed_url.scheme == 'https':
                conn = self._create_https_connection(parsed_url)
            else:
                conn = self._create_http_connection(parsed_url)
                
            # Send the request
            request_path = parsed_url.path
            if parsed_url.query:
                request_path += f"?{parsed_url.query}"
            if not request_path:
                request_path = "/"
                
            conn.request(self.command, request_path, headers=self._filter_headers(self.headers))
            
            # Get the response
            response = conn.getresponse()
            
            # Send the response status and headers
            self.send_response(response.status, response.reason)
            for header, value in response.getheaders():
                if header.lower() != 'transfer-encoding':
                    self.send_header(header, value)
            self.end_headers()
            
            # Send the response body
            response_body = response.read()
            self.wfile.write(response_body)
            
            # Cache the response if enabled
            if self.cache_enabled:
                self._cache_response(url, response_body, response.getheaders())
                
            # Log the request
            if self.gui:
                self.gui.add_request(self.client_address[0], self.command, url, response.status)
                
            conn.close()
            
        except Exception as e:
            self.send_error(500, f"Proxy Error: {str(e)}")
            logger.error(f"Error handling GET request: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        url = self.path
        parsed_url = urlparse(url)
        
        # Check if domain is blocked
        if self._is_domain_blocked(parsed_url.netloc):
            self.send_error(403, "Forbidden - Domain blocked by proxy")
            return
            
        try:
            # Get request body
            content_length = int(self.headers.get('Content-Length', 0))
            request_body = self.rfile.read(content_length)
            
            # Connect to the remote server
            if parsed_url.scheme == 'https':
                conn = self._create_https_connection(parsed_url)
            else:
                conn = self._create_http_connection(parsed_url)
                
            # Send the request
            request_path = parsed_url.path
            if parsed_url.query:
                request_path += f"?{parsed_url.query}"
            if not request_path:
                request_path = "/"
                
            conn.request(self.command, request_path, body=request_body, headers=self._filter_headers(self.headers))
            
            # Get the response
            response = conn.getresponse()
            
            # Send the response status and headers
            self.send_response(response.status, response.reason)
            for header, value in response.getheaders():
                if header.lower() != 'transfer-encoding':
                    self.send_header(header, value)
            self.end_headers()
            
            # Send the response body
            response_body = response.read()
            self.wfile.write(response_body)
            
            # Log the request
            if self.gui:
                self.gui.add_request(self.client_address[0], self.command, url, response.status)
                
            conn.close()
            
        except Exception as e:
            self.send_error(500, f"Proxy Error: {str(e)}")
            logger.error(f"Error handling POST request: {str(e)}")
    
    def do_CONNECT(self):
        """Handle CONNECT requests (for HTTPS tunneling)"""
        try:
            # Parse the target address
            host_port = self.path.split(':')
            host = host_port[0]
            port = int(host_port[1]) if len(host_port) > 1 else 443
            
            # Check if domain is blocked
            if self._is_domain_blocked(host):
                self.send_error(403, "Forbidden - Domain blocked by proxy")
                return
                
            # Connect to the target server
            target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_socket.connect((host, port))
            
            # Send a 200 Connection established response
            self.send_response(200, 'Connection Established')
            self.end_headers()
            
            # Log the connection
            if self.gui:
                self.gui.add_request(self.client_address[0], self.command, f"{host}:{port}", 200)
            
            # Start tunneling
            self._tunnel(target_socket)
            
        except Exception as e:
            self.send_error(500, f"Proxy Error: {str(e)}")
            logger.error(f"Error handling CONNECT request: {str(e)}")
    
    def _tunnel(self, target_socket):
        """Create a tunnel between client and target server"""
        client_socket = self.connection
        
        # Set both sockets to non-blocking mode
        client_socket.setblocking(0)
        target_socket.setblocking(0)
        
        client_buffer = b''
        target_buffer = b''
        
        is_active = True
        
        while is_active:
            # Wait until client or target is available for read/write
            inputs = [client_socket, target_socket]
            readable, writable, exceptional = select.select(inputs, inputs, inputs, 1)
            
            # Handle socket errors
            if exceptional:
                break
                
            # Read from client
            if client_socket in readable:
                try:
                    data = client_socket.recv(8192)
                    if not data:
                        is_active = False
                        break
                    target_buffer += data
                except:
                    is_active = False
                    break
            
            # Read from target
            if target_socket in readable:
                try:
                    data = target_socket.recv(8192)
                    if not data:
                        is_active = False
                        break
                    client_buffer += data
                except:
                    is_active = False
                    break
            
            # Write to target
            if target_socket in writable and target_buffer:
                try:
                    sent = target_socket.send(target_buffer)
                    target_buffer = target_buffer[sent:]
                except:
                    is_active = False
                    break
            
            # Write to client
            if client_socket in writable and client_buffer:
                try:
                    sent = client_socket.send(client_buffer)
                    client_buffer = client_buffer[sent:]
                except:
                    is_active = False
                    break
        
        # Close connections
        target_socket.close()
    
    def _create_http_connection(self, parsed_url):
        """Create a connection to an HTTP server"""
        host = parsed_url.netloc
        port = parsed_url.port or 80
        
        if ':' in host and not host.startswith('['):
            host = host.split(':')[0]
            
        conn = socket.create_connection((host, port), timeout=self.timeout)
        return conn
    
    def _create_https_connection(self, parsed_url):
        """Create a connection to an HTTPS server"""
        host = parsed_url.netloc
        port = parsed_url.port or 443
        
        if ':' in host and not host.startswith('['):
            host = host.split(':')[0]
            
        conn = socket.create_connection((host, port), timeout=self.timeout)
        context = ssl.create_default_context()
        conn = context.wrap_socket(conn, server_hostname=host)
        return conn
    
    def _filter_headers(self, headers):
        """Filter headers to forward to the remote server"""
        filtered_headers = {}
        for header in headers:
            if header.lower() not in ('connection', 'keep-alive', 'proxy-connection', 'proxy-authenticate', 'proxy-authorization'):
                filtered_headers[header] = headers[header]
        return filtered_headers
    
    def _is_domain_blocked(self, domain):
        """Check if a domain is in the blocked list"""
        if not domain:
            return False
            
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
            
        for blocked in self.blocked_domains:
            if domain == blocked or domain.endswith('.' + blocked):
                return True
        return False
    
    def _serve_from_cache(self, url):
        """Try to serve a response from cache"""
        cache_path = os.path.join(self.cache_directory, self._get_cache_filename(url))
        
        if not os.path.exists(cache_path):
            return False
            
        try:
            with open(cache_path, 'rb') as f:
                # Read headers
                header_lines = []
                while True:
                    line = f.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        break
                    header_lines.append(line)
                
                # Parse status line
                status_line = header_lines[0].split(' ', 2)
                status_code = int(status_line[1])
                reason = status_line[2] if len(status_line) > 2 else ''
                
                # Send status and headers
                self.send_response(status_code, reason)
                for header in header_lines[1:]:
                    name, value = header.split(': ', 1)
                    self.send_header(name, value)
                self.end_headers()
                
                # Send body
                self.wfile.write(f.read())
                
                # Log cache hit
                if self.gui:
                    self.gui.log_message(f"Cache hit: {url}")
                    self.gui.add_request(self.client_address[0], self.command, url, status_code, cached=True)
                
                return True
                
        except Exception as e:
            logger.error(f"Error serving from cache: {str(e)}")
            return False
    
    def _cache_response(self, url, body, headers):
        """Cache a response for future use"""
        try:
            if not os.path.exists(self.cache_directory):
                os.makedirs(self.cache_directory)
                
            cache_path = os.path.join(self.cache_directory, self._get_cache_filename(url))
            
            with open(cache_path, 'wb') as f:
                # Write status line
                f.write(f"HTTP/1.1 {self.last_code} {self.last_message}\r\n".encode())
                
                # Write headers
                for header, value in headers:
                    if header.lower() not in ('connection', 'transfer-encoding'):
                        f.write(f"{header}: {value}\r\n".encode())
                
                # End of headers
                f.write(b"\r\n")
                
                # Write body
                f.write(body)
                
        except Exception as e:
            logger.error(f"Error caching response: {str(e)}")
    
    def _get_cache_filename(self, url):
        """Generate a filename for caching based on URL"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()


class ProxyServerThread(QThread):
    """Thread to run the proxy server"""
    log_signal = pyqtSignal(str)
    
    def __init__(self, host='127.0.0.1', port=8080, gui=None):
        super().__init__()
        self.host = host
        self.port = port
        self.gui = gui
        self.running = False
        self.server = None
    
    def run(self):
        try:
            # Create HTTP server
            self.server = ThreadingHTTPServer((self.host, self.port), ProxyRequestHandler)
            
            # Set GUI reference for the handler
            ProxyRequestHandler.gui = self.gui
            
            self.running = True
            self.log_signal.emit(f"Proxy server started on {self.host}:{self.port}")
            
            # Start serving
            while self.running:
                self.server.handle_request()
                
        except Exception as e:
            self.log_signal.emit(f"Error in proxy server: {str(e)}")
    
    def stop(self):
        self.running = False
        if self.server:
            self.server.server_close()
        self.log_signal.emit("Proxy server stopped")


class ProxyServerGUI(QMainWindow):
    """Main GUI for the proxy server application"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proxy Server")
        self.setMinimumSize(800, 600)
        
        # Server state
        self.server_thread = None
        self.is_running = False
        
        # Configuration
        self.blocked_domains = []
        self.cache_enabled = True
        self.cache_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
        
        # Initialize UI
        self.init_ui()
        
        # Update blocked domains in handler
        ProxyRequestHandler.blocked_domains = self.blocked_domains
        ProxyRequestHandler.cache_enabled = self.cache_enabled
        ProxyRequestHandler.cache_directory = self.cache_directory
    
    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tabs
        tabs = QTabWidget()
        
        # Main tab
        main_tab = QWidget()
        main_tab_layout = QVBoxLayout()
        
        # Server configuration group
        server_group = QGroupBox("Server Configuration")
        server_layout = QVBoxLayout()
        
        # Host and port
        host_layout = QHBoxLayout()
        host_label = QLabel("Host:")
        self.host_input = QLineEdit("127.0.0.1")
        port_label = QLabel("Port:")
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(8080)
        host_layout.addWidget(host_label)
        host_layout.addWidget(self.host_input)
        host_layout.addWidget(port_label)
        host_layout.addWidget(self.port_input)
        
        # Start/Stop button
        self.start_stop_btn = QPushButton("Start Server")
        self.start_stop_btn.clicked.connect(self.toggle_server)
        
        # Add to server group
        server_layout.addLayout(host_layout)
        server_layout.addWidget(self.start_stop_btn)
        server_group.setLayout(server_layout)
        
        # Request log
        log_group = QGroupBox("Request Log")
        log_layout = QVBoxLayout()
        
        self.request_table = QTableWidget(0, 5)
        self.request_table.setHorizontalHeaderLabels(["Time", "Client", "Method", "URL", "Status"])
        self.request_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        log_layout.addWidget(self.request_table)
        
        # Clear log button
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        log_layout.addWidget(clear_log_btn)
        
        log_group.setLayout(log_layout)
        
        # Add to main tab
        main_tab_layout.addWidget(server_group)
        main_tab_layout.addWidget(log_group)
        main_tab.setLayout(main_tab_layout)
        
        # Settings tab
        settings_tab = QWidget()
        settings_layout = QVBoxLayout()
        
        # Blocking group
        blocking_group = QGroupBox("Domain Blocking")
        blocking_layout = QVBoxLayout()
        
        # Domain input
        domain_layout = QHBoxLayout()
        domain_label = QLabel("Domain:")
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("example.com")
        add_domain_btn = QPushButton("Block Domain")
        add_domain_btn.clicked.connect(self.add_blocked_domain)
        domain_layout.addWidget(domain_label)
        domain_layout.addWidget(self.domain_input)
        domain_layout.addWidget(add_domain_btn)
        
        # Blocked domains list
        self.blocked_domains_list = QTableWidget(0, 2)
        self.blocked_domains_list.setHorizontalHeaderLabels(["Domain", "Actions"])
        self.blocked_domains_list.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        
        # Add to blocking group
        blocking_layout.addLayout(domain_layout)
        blocking_layout.addWidget(self.blocked_domains_list)
        blocking_group.setLayout(blocking_layout)
        
        # Caching group
        caching_group = QGroupBox("Caching")
        caching_layout = QVBoxLayout()
        
        # Enable caching
        self.cache_checkbox = QCheckBox("Enable Caching")
        self.cache_checkbox.setChecked(True)
        self.cache_checkbox.stateChanged.connect(self.toggle_cache)
        
        # Cache directory
        cache_dir_layout = QHBoxLayout()
        cache_dir_label = QLabel("Cache Directory:")
        self.cache_dir_input = QLineEdit(self.cache_directory)
        self.cache_dir_input.setReadOnly(True)
        cache_dir_btn = QPushButton("Browse")
        cache_dir_btn.clicked.connect(self.browse_cache_dir)
        cache_dir_layout.addWidget(cache_dir_label)
        cache_dir_layout.addWidget(self.cache_dir_input)
        cache_dir_layout.addWidget(cache_dir_btn)
        
        # Clear cache button
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        
        # Add to caching group
        caching_layout.addWidget(self.cache_checkbox)
        caching_layout.addLayout(cache_dir_layout)
        caching_layout.addWidget(clear_cache_btn)
        caching_group.setLayout(caching_layout)
        
        # Add to settings tab
        settings_layout.addWidget(blocking_group)
        settings_layout.addWidget(caching_group)
        settings_layout.addStretch()
        settings_tab.setLayout(settings_layout)
        
        # Logs tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        logs_layout.addWidget(self.log_text)
        
        # Clear logs button
        clear_logs_btn = QPushButton("Clear Logs")
        clear_logs_btn.clicked.connect(self.clear_logs)
        logs_layout.addWidget(clear_logs_btn)
        
        logs_tab.setLayout(logs_layout)
        
        # Add tabs
        tabs.addTab(main_tab, "Main")
        tabs.addTab(settings_tab, "Settings")
        tabs.addTab(logs_tab, "Logs")
        
        # Add tabs to main layout
        main_layout.addWidget(tabs)
        
        # Set the main widget
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def toggle_server(self):
        """Start or stop the proxy server"""
        if not self.is_running:
            # Get host and port
            host = self.host_input.text()
            port = self.port_input.value()
            
            # Start server
            self.server_thread = ProxyServerThread(host, port, self)
            self.server_thread.log_signal.connect(self.log_message)
            self.server_thread.start()
            
            # Update UI
            self.is_running = True
            self.start_stop_btn.setText("Stop Server")
            self.host_input.setEnabled(False)
            self.port_input.setEnabled(False)
            
        else:
            # Stop server
            if self.server_thread:
                self.server_thread.stop()
                self.server_thread.wait()
                self.server_thread = None
            
            # Update UI
            self.is_running = False
            self.start_stop_btn.setText("Start Server")
            self.host_input.setEnabled(True)
            self.port_input.setEnabled(True)
    
    def add_blocked_domain(self):
        """Add a domain to the block list"""
        domain = self.domain_input.text().strip().lower()
        
        if not domain:
            return
            
        if domain in self.blocked_domains:
            QMessageBox.warning(self, "Warning", f"Domain '{domain}' is already blocked.")
            return
            
        # Add to list
        self.blocked_domains.append(domain)
        
        # Update handler
        ProxyRequestHandler.blocked_domains = self.blocked_domains
        
        # Update UI
        self.update_blocked_domains_list()
        self.domain_input.clear()
        
        self.log_message(f"Added blocked domain: {domain}")
    
    def remove_blocked_domain(self, domain):
        """Remove a domain from the block list"""
        if domain in self.blocked_domains:
            self.blocked_domains.remove(domain)
            
            # Update handler
            ProxyRequestHandler.blocked_domains = self.blocked_domains
            
            # Update UI
            self.update_blocked_domains_list()
            
            self.log_message(f"Removed blocked domain: {domain}")
    
    def update_blocked_domains_list(self):
        """Update the blocked domains table"""
        self.blocked_domains_list.setRowCount(0)
        
        for domain in self.blocked_domains:
            row = self.blocked_domains_list.rowCount()
            self.blocked_domains_list.insertRow(row)
            
            # Domain
            self.blocked_domains_list.setItem(row, 0, QTableWidgetItem(domain))
            
            # Remove button
            remove_btn = QPushButton("Remove")
            remove_btn.clicked.connect(lambda _, d=domain: self.remove_blocked_domain(d))
            self.blocked_domains_list.setCellWidget(row, 1, remove_btn)
    
    def toggle_cache(self, state):
        """Enable or disable caching"""
        self.cache_enabled = (state == Qt.Checked)
        ProxyRequestHandler.cache_enabled = self.cache_enabled
        self.log_message(f"Caching {'enabled' if self.cache_enabled else 'disabled'}")
    
    def browse_cache_dir(self):
        """Select a cache directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Cache Directory")
        if directory:
            self.cache_directory = directory
            self.cache_dir_input.setText(directory)
            ProxyRequestHandler.cache_directory = directory
            self.log_message(f"Cache directory set to: {directory}")
    
    def clear_cache(self):
        """Clear the cache directory"""
        try:
            if os.path.exists(self.cache_directory):
                for file in os.listdir(self.cache_directory):
                    file_path = os.path.join(self.cache_directory, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                self.log_message("Cache cleared")
            else:
                self.log_message("Cache directory does not exist")
        except Exception as e:
            self.log_message(f"Error clearing cache: {str(e)}")
    
    def add_request(self, client, method, url, status, cached=False):
        """Add a request to the log table"""
        row = self.request_table.rowCount()
        self.request_table.insertRow(row)
        
        # Time
        current_time = time.strftime("%H:%M:%S")
        self.request_table.setItem(row, 0, QTableWidgetItem(current_time))
        
        # Client
        self.request_table.setItem(row, 1, QTableWidgetItem(client))
        
        # Method
        self.request_table.setItem(row, 2, QTableWidgetItem(method))
        
        # URL
        url_item = QTableWidgetItem(url)
        if cached:
            url_item.setForeground(QColor(0, 128, 0))  # Green for cached
        self.request_table.setItem(row, 3, url_item)
        
        # Status
        status_item = QTableWidgetItem(str(status))
        if status >= 400:
            status_item.setForeground(QColor(255, 0, 0))  # Red for errors
        elif status >= 300:
            status_item.setForeground(QColor(255, 165, 0))  # Orange for redirects
        self.request_table.setItem(row, 4, status_item)
        
        # Scroll to bottom
        self.request_table.scrollToBottom()
    
    def log_message(self, message):
        """Add a message to the log"""
        current_time = time.strftime("%H:%M:%S")
        log_message = f"[{current_time}] {message}"
        
        self.log_text.append(log_message)
        
        # Scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def clear_log(self):
        """Clear the request log"""
        self.request_table.setRowCount(0)
    
    def clear_logs(self):
        """Clear the text logs"""
        self.log_text.clear()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running:
            self.toggle_server()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProxyServerGUI()
    window.show()
    sys.exit(app.exec_()) 