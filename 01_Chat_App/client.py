#!/usr/bin/env python3
import sys
import socket
import json
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QLineEdit, QPushButton, QLabel, QTabWidget, 
                            QListWidget, QInputDialog, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QObject

class ChatSignals(QObject):
    message_received = pyqtSignal(dict)
    connection_error = pyqtSignal(str)

class ChatClient:
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.client_socket = None
        self.signals = ChatSignals()
        self.connected = False
        self.username = ""
        
    def connect(self, username):
        try:
            self.username = username
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            
            # Send username to server
            self.client_socket.send(json.dumps({"username": username}).encode('utf-8'))
            
            # Start listening thread
            self.connected = True
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            self.signals.connection_error.emit(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        self.connected = False
        if self.client_socket:
            self.client_socket.close()
    
    def send_message(self, message_type, content, target=None, group=None):
        if not self.connected:
            return False
        
        message = {
            "type": message_type,
            "message": content,
        }
        
        if target:
            message["target"] = target
            
        if group:
            message["group"] = group
            
        try:
            self.client_socket.send(json.dumps(message).encode('utf-8'))
            return True
        except:
            self.connected = False
            self.signals.connection_error.emit("Connection lost")
            return False
    
    def receive_messages(self):
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                
                message = json.loads(data)
                self.signals.message_received.emit(message)
                
            except json.JSONDecodeError:
                print("Invalid JSON received")
            except Exception as e:
                if self.connected:  # Only show error if we're supposed to be connected
                    self.signals.connection_error.emit(f"Error receiving messages: {str(e)}")
                break
        
        self.connected = False

class ChatTab(QWidget):
    def __init__(self, client, tab_type="public", target=None):
        super().__init__()
        self.client = client
        self.tab_type = tab_type  # "public", "private", "group"
        self.target = target  # username for private chat, group name for group chat
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Message input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
        
        if self.tab_type == "public":
            success = self.client.send_message("broadcast", message)
        elif self.tab_type == "private":
            success = self.client.send_message("private_message", message, target=self.target)
        elif self.tab_type == "group":
            success = self.client.send_message("group_message", message, group=self.target)
            
        if success:
            self.message_input.clear()
    
    def add_message(self, sender, message, is_system=False):
        if is_system:
            self.chat_display.append(f"<b><font color='blue'>{sender}: {message}</font></b>")
        else:
            self.chat_display.append(f"<b>{sender}</b>: {message}")
        
        # Auto scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.client = ChatClient()
        self.client.signals.message_received.connect(self.handle_message)
        self.client.signals.connection_error.connect(self.handle_error)
        
        self.username = ""
        self.users = []
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Python Chat Client")
        self.setGeometry(100, 100, 800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Create a splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - user list and controls
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # User list
        self.user_list_label = QLabel("Online Users:")
        self.user_list = QListWidget()
        self.user_list.itemDoubleClicked.connect(self.open_private_chat)
        
        # Group controls
        group_layout = QHBoxLayout()
        self.group_input = QLineEdit()
        self.group_input.setPlaceholderText("Group name")
        self.join_group_button = QPushButton("Join Group")
        self.join_group_button.clicked.connect(self.join_group)
        group_layout.addWidget(self.group_input)
        group_layout.addWidget(self.join_group_button)
        
        left_layout.addWidget(self.user_list_label)
        left_layout.addWidget(self.user_list)
        left_layout.addLayout(group_layout)
        left_panel.setLayout(left_layout)
        
        # Right panel - chat tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Add main chat tab
        self.main_chat_tab = ChatTab(self.client)
        self.tabs.addTab(self.main_chat_tab, "Main Chat")
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.tabs)
        
        # Set initial sizes
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Show login dialog on start
        self.show_login_dialog()
    
    def show_login_dialog(self):
        username, ok = QInputDialog.getText(self, "Login", "Enter your username:")
        if ok and username:
            self.username = username
            if self.client.connect(username):
                self.setWindowTitle(f"Python Chat Client - {username}")
            else:
                QMessageBox.critical(self, "Connection Error", "Could not connect to server")
                self.close()
        else:
            self.close()
    
    def handle_message(self, message):
        message_type = message.get("type", "")
        sender = message.get("sender", "Unknown")
        content = message.get("message", "")
        
        if message_type == "system":
            # System messages go to all tabs
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                tab.add_message(sender, content, is_system=True)
                
        elif message_type == "user_list":
            # Update user list
            self.users = message.get("users", [])
            self.update_user_list()
            
        elif message_type == "broadcast":
            # Public messages go to main chat
            self.main_chat_tab.add_message(sender, content)
            
        elif message_type == "private_message":
            # Private messages go to the specific private chat tab
            target = message.get("target", "")
            other_user = sender if sender != self.username else target
            
            # Find or create private chat tab
            tab = self.find_or_create_tab("private", other_user)
            tab.add_message(sender, content)
            
        elif message_type == "group_message":
            # Group messages go to the specific group chat tab
            group = message.get("group", "")
            tab = self.find_or_create_tab("group", group)
            tab.add_message(sender, content)
            
        elif message_type == "error":
            QMessageBox.warning(self, "Error", content)
    
    def handle_error(self, error_message):
        QMessageBox.critical(self, "Connection Error", error_message)
        self.close()
    
    def update_user_list(self):
        self.user_list.clear()
        for user in self.users:
            if user != self.username:  # Don't show ourselves
                self.user_list.addItem(user)
    
    def open_private_chat(self, item):
        username = item.text()
        self.find_or_create_tab("private", username)
    
    def join_group(self):
        group_name = self.group_input.text().strip()
        if group_name:
            self.client.send_message("join_group", f"Joining group {group_name}", group=group_name)
            self.find_or_create_tab("group", group_name)
            self.group_input.clear()
    
    def find_or_create_tab(self, tab_type, target):
        # Check if tab already exists
        tab_title = f"Private: {target}" if tab_type == "private" else f"Group: {target}"
        
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == tab_title:
                self.tabs.setCurrentIndex(i)
                return self.tabs.widget(i)
        
        # Create new tab
        new_tab = ChatTab(self.client, tab_type, target)
        index = self.tabs.addTab(new_tab, tab_title)
        self.tabs.setCurrentIndex(index)
        return new_tab
    
    def close_tab(self, index):
        if index != 0:  # Don't close main chat tab
            self.tabs.removeTab(index)
    
    def closeEvent(self, event):
        self.client.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_()) 