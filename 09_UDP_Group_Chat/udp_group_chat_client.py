#!/usr/bin/env python3
import socket
import json
import threading
import time
import sys
import os
import signal
import argparse
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
                            QTabWidget, QListWidget, QMessageBox, QSplitter, QMenu,
                            QAction, QDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QTextCursor, QIcon


class ChatClientBackend(threading.Thread):
    """Backend thread to handle network communication"""
    
    def __init__(self, server_host, server_port, username, message_callback):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.message_callback = message_callback
        self.running = False
        self.socket = None
        self.registered = False
        
    def run(self):
        """Main thread function"""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1)  # 1 second timeout for non-blocking receive
            
            # Register with the server
            self.register()
            
            # Start heartbeat thread
            heartbeat_thread = threading.Thread(target=self.send_heartbeat)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
            
            # Main receive loop
            self.running = True
            while self.running:
                try:
                    # Receive data from server
                    data, server_address = self.socket.recvfrom(4096)
                    
                    # Process the message
                    self.process_message(data)
                    
                except socket.timeout:
                    # Socket timeout, just continue the loop
                    pass
                except Exception as e:
                    self.message_callback({
                        'type': 'error',
                        'message': f"Error receiving data: {str(e)}"
                    })
            
        except Exception as e:
            self.message_callback({
                'type': 'error',
                'message': f"Connection error: {str(e)}"
            })
        finally:
            if self.socket:
                self.socket.close()
    
    def register(self):
        """Register with the server"""
        register_msg = {
            'type': 'register',
            'username': self.username
        }
        self.send_message(register_msg)
    
    def send_message(self, message):
        """Send a message to the server"""
        if self.socket:
            try:
                data = json.dumps(message).encode('utf-8')
                self.socket.sendto(data, (self.server_host, self.server_port))
            except Exception as e:
                self.message_callback({
                    'type': 'error',
                    'message': f"Error sending message: {str(e)}"
                })
    
    def process_message(self, data):
        """Process a message from the server"""
        try:
            message = json.loads(data.decode('utf-8'))
            
            # Handle registration acknowledgment
            if message['type'] == 'register_ack':
                self.registered = True
                
            # Forward the message to the UI
            self.message_callback(message)
            
        except json.JSONDecodeError:
            self.message_callback({
                'type': 'error',
                'message': "Received invalid data from server"
            })
        except Exception as e:
            self.message_callback({
                'type': 'error',
                'message': f"Error processing message: {str(e)}"
            })
    
    def send_chat_message(self, content, target_type='broadcast', target=None):
        """Send a chat message"""
        message = {
            'type': 'message',
            'content': content,
            'target_type': target_type
        }
        
        if target:
            message['target'] = target
            
        self.send_message(message)
    
    def join_group(self, group_name):
        """Join a group"""
        message = {
            'type': 'join_group',
            'group': group_name
        }
        self.send_message(message)
    
    def leave_group(self, group_name):
        """Leave a group"""
        message = {
            'type': 'leave_group',
            'group': group_name
        }
        self.send_message(message)
    
    def request_group_list(self):
        """Request a list of available groups"""
        message = {
            'type': 'list_groups'
        }
        self.send_message(message)
    
    def request_user_list(self, group_name=None):
        """Request a list of users"""
        message = {
            'type': 'list_users'
        }
        if group_name:
            message['group'] = group_name
            
        self.send_message(message)
    
    def send_heartbeat(self):
        """Send periodic heartbeat to keep connection alive"""
        while self.running:
            if self.registered:
                heartbeat = {
                    'type': 'heartbeat'
                }
                self.send_message(heartbeat)
            time.sleep(30)  # Send heartbeat every 30 seconds
    
    def stop(self):
        """Stop the client thread"""
        self.running = False


class GroupChatDialog(QDialog):
    """Dialog for joining or creating a group"""
    
    def __init__(self, parent=None, groups=None):
        super().__init__(parent)
        self.setWindowTitle("Join or Create Group")
        self.setMinimumWidth(300)
        self.groups = groups or {}
        self.selected_group = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Group list
        self.group_list = QListWidget()
        for group_name, member_count in self.groups.items():
            self.group_list.addItem(f"{group_name} ({member_count} members)")
        
        # New group input
        new_group_layout = QHBoxLayout()
        new_group_label = QLabel("New Group:")
        self.new_group_input = QLineEdit()
        new_group_layout.addWidget(new_group_label)
        new_group_layout.addWidget(self.new_group_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        join_btn = QPushButton("Join Selected")
        create_btn = QPushButton("Create New")
        cancel_btn = QPushButton("Cancel")
        
        join_btn.clicked.connect(self.join_selected)
        create_btn.clicked.connect(self.create_new)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(join_btn)
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        
        # Add to main layout
        layout.addWidget(QLabel("Select a group to join:"))
        layout.addWidget(self.group_list)
        layout.addLayout(new_group_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def join_selected(self):
        """Join the selected group"""
        selected_items = self.group_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a group to join")
            return
            
        # Extract group name from item text (remove member count)
        item_text = selected_items[0].text()
        group_name = item_text.split(" (")[0]
        
        self.selected_group = group_name
        self.accept()
    
    def create_new(self):
        """Create a new group"""
        group_name = self.new_group_input.text().strip()
        if not group_name:
            QMessageBox.warning(self, "Empty Name", "Please enter a group name")
            return
            
        self.selected_group = group_name
        self.accept()


class ChatTab(QWidget):
    """Tab for a chat (main, group, or private)"""
    
    send_message_signal = pyqtSignal(str, str, str)
    
    def __init__(self, name, tab_type="main", parent=None):
        super().__init__(parent)
        self.name = name
        self.tab_type = tab_type  # "main", "group", or "private"
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        
        # Message input area
        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)
        
        # Add to main layout
        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        
        self.setLayout(layout)
    
    def add_message(self, sender, content, is_system=False):
        """Add a message to the chat display"""
        # Format the message
        if is_system:
            html = f'<p style="color: gray; margin: 2px;"><i>{content}</i></p>'
        else:
            html = f'<p style="margin: 2px;"><b>{sender}:</b> {content}</p>'
        
        # Add to display
        self.chat_display.moveCursor(QTextCursor.End)
        self.chat_display.insertHtml(html)
        self.chat_display.moveCursor(QTextCursor.End)
    
    def send_message(self):
        """Send a message"""
        content = self.message_input.text().strip()
        if not content:
            return
            
        if self.tab_type == "main":
            target_type = "broadcast"
            target = None
        elif self.tab_type == "group":
            target_type = "group"
            target = self.name
        elif self.tab_type == "private":
            target_type = "private"
            target = self.name
            
        self.send_message_signal.emit(content, target_type, target)
        self.message_input.clear()


class UDPGroupChatClient(QMainWindow):
    """Main client window"""
    
    def __init__(self, server_host, server_port, username):
        super().__init__()
        self.server_host = server_host
        self.server_port = server_port
        self.username = username
        self.client = None
        self.groups = {}
        self.users = []
        self.current_tab = None
        
        self.init_ui()
        self.start_client()
        
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle(f"UDP Group Chat - {self.username}")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Left side (tabs and chat)
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        
        # Chat tabs
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        
        # Create main tab
        main_tab = ChatTab("Main", "main")
        main_tab.send_message_signal.connect(self.send_chat_message)
        self.tabs.addTab(main_tab, "Main")
        
        left_layout.addWidget(self.tabs)
        left_widget.setLayout(left_layout)
        
        # Right side (users and groups)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        # Groups section
        groups_label = QLabel("Groups")
        self.groups_list = QListWidget()
        self.groups_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.groups_list.customContextMenuRequested.connect(self.show_group_menu)
        self.groups_list.itemDoubleClicked.connect(self.open_group_chat)
        
        join_group_btn = QPushButton("Join/Create Group")
        join_group_btn.clicked.connect(self.join_group_dialog)
        
        # Users section
        users_label = QLabel("Users Online")
        self.users_list = QListWidget()
        self.users_list.itemDoubleClicked.connect(self.open_private_chat)
        
        refresh_btn = QPushButton("Refresh Lists")
        refresh_btn.clicked.connect(self.refresh_lists)
        
        # Add to right layout
        right_layout.addWidget(groups_label)
        right_layout.addWidget(self.groups_list)
        right_layout.addWidget(join_group_btn)
        right_layout.addWidget(users_label)
        right_layout.addWidget(self.users_list)
        right_layout.addWidget(refresh_btn)
        right_widget.setLayout(right_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([600, 200])
        
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Status bar
        self.statusBar().showMessage("Connecting to server...")
        
        # Set up timer for refreshing lists
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_lists)
        self.refresh_timer.start(60000)  # Refresh every minute
    
    def start_client(self):
        """Start the client backend"""
        self.client = ChatClientBackend(
            self.server_host, 
            self.server_port, 
            self.username, 
            self.handle_server_message
        )
        self.client.daemon = True
        self.client.start()
    
    def handle_server_message(self, message):
        """Handle messages from the server"""
        message_type = message.get('type', '')
        
        if message_type == 'register_ack':
            if message.get('status') == 'success':
                self.statusBar().showMessage("Connected to server")
                self.refresh_lists()
            else:
                self.statusBar().showMessage(f"Registration failed: {message.get('message', '')}")
                
        elif message_type == 'message':
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            group = message.get('group', None)
            
            if group:
                # Group message
                self.handle_group_message(sender, content, group)
            else:
                # Broadcast message
                self.handle_broadcast_message(sender, content)
                
        elif message_type == 'private_message':
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            
            self.handle_private_message(sender, content)
                
        elif message_type == 'system_message':
            content = message.get('content', '')
            group = message.get('group', None)
            
            if group:
                # Group system message
                self.handle_group_system_message(content, group)
            else:
                # Broadcast system message
                self.handle_broadcast_system_message(content)
                
        elif message_type == 'group_list':
            self.groups = message.get('groups', {})
            self.update_groups_list()
                
        elif message_type == 'user_list':
            self.users = message.get('users', [])
            self.update_users_list()
                
        elif message_type == 'join_group_ack':
            if message.get('status') == 'success':
                group = message.get('group', '')
                self.statusBar().showMessage(f"Joined group: {group}")
                
                # Create a tab for the group if it doesn't exist
                self.open_group_chat(group)
                
        elif message_type == 'leave_group_ack':
            if message.get('status') == 'success':
                group = message.get('group', '')
                self.statusBar().showMessage(f"Left group: {group}")
                
        elif message_type == 'error':
            error_msg = message.get('message', 'Unknown error')
            self.statusBar().showMessage(f"Error: {error_msg}")
            QMessageBox.warning(self, "Error", error_msg)
    
    def send_chat_message(self, content, target_type='broadcast', target=None):
        """Send a chat message"""
        if self.client:
            self.client.send_chat_message(content, target_type, target)
    
    def handle_broadcast_message(self, sender, content):
        """Handle a broadcast message"""
        # Find the main tab
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.tab_type == "main":
                tab.add_message(sender, content)
                break
    
    def handle_group_message(self, sender, content, group):
        """Handle a group message"""
        # Find the group tab or create it
        group_tab = self.find_tab("group", group)
        if not group_tab:
            group_tab = self.open_group_chat(group)
            
        group_tab.add_message(sender, content)
    
    def handle_private_message(self, sender, content):
        """Handle a private message"""
        # Find the private chat tab or create it
        private_tab = self.find_tab("private", sender)
        if not private_tab:
            private_tab = self.open_private_chat(sender)
            
        private_tab.add_message(sender, content)
    
    def handle_broadcast_system_message(self, content):
        """Handle a broadcast system message"""
        # Add to main tab
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.tab_type == "main":
                tab.add_message("System", content, is_system=True)
                break
    
    def handle_group_system_message(self, content, group):
        """Handle a group system message"""
        # Find the group tab
        group_tab = self.find_tab("group", group)
        if group_tab:
            group_tab.add_message("System", content, is_system=True)
    
    def find_tab(self, tab_type, name):
        """Find a tab by type and name"""
        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            if tab.tab_type == tab_type and tab.name == name:
                return tab
        return None
    
    def open_group_chat(self, group_name):
        """Open a group chat tab"""
        # If group_name is a QListWidgetItem, get its text
        if hasattr(group_name, 'text'):
            group_name = group_name.text()
        
        # Check if tab already exists
        group_tab = self.find_tab("group", group_name)
        if not group_tab:
            # Create new tab
            group_tab = ChatTab(group_name, "group")
            group_tab.send_message_signal.connect(self.send_chat_message)
            self.tabs.addTab(group_tab, f"Group: {group_name}")
            
            # Join the group if not already a member
            if self.client:
                self.client.join_group(group_name)
                
        # Switch to the tab
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == group_tab:
                self.tabs.setCurrentIndex(i)
                break
                
        return group_tab
    
    def open_private_chat(self, username):
        """Open a private chat tab"""
        # If username is a QListWidgetItem, get its text
        if hasattr(username, 'text'):
            username = username.text()
            
        # Don't open chat with yourself
        if username == self.username:
            return None
        
        # Check if tab already exists
        private_tab = self.find_tab("private", username)
        if not private_tab:
            # Create new tab
            private_tab = ChatTab(username, "private")
            private_tab.send_message_signal.connect(self.send_chat_message)
            self.tabs.addTab(private_tab, f"PM: {username}")
            
        # Switch to the tab
        for i in range(self.tabs.count()):
            if self.tabs.widget(i) == private_tab:
                self.tabs.setCurrentIndex(i)
                break
                
        return private_tab
    
    def close_tab(self, index):
        """Close a tab"""
        # Don't close the main tab
        if index == 0:
            return
            
        tab = self.tabs.widget(index)
        if tab.tab_type == "group":
            # Leave the group
            if self.client:
                self.client.leave_group(tab.name)
                
        self.tabs.removeTab(index)
    
    def join_group_dialog(self):
        """Show dialog for joining a group"""
        dialog = GroupChatDialog(self, self.groups)
        if dialog.exec_():
            group_name = dialog.selected_group
            if group_name:
                self.open_group_chat(group_name)
    
    def show_group_menu(self, position):
        """Show context menu for groups list"""
        menu = QMenu()
        join_action = menu.addAction("Join Group")
        refresh_action = menu.addAction("Refresh List")
        
        # Get the selected item
        selected_items = self.groups_list.selectedItems()
        if not selected_items:
            join_action.setEnabled(False)
            
        # Show the menu and get the selected action
        action = menu.exec_(self.groups_list.mapToGlobal(position))
        
        if action == join_action and selected_items:
            self.open_group_chat(selected_items[0].text())
        elif action == refresh_action:
            self.refresh_lists()
    
    def refresh_lists(self):
        """Refresh the groups and users lists"""
        if self.client:
            self.client.request_group_list()
            self.client.request_user_list()
    
    def update_groups_list(self):
        """Update the groups list"""
        self.groups_list.clear()
        for group_name, member_count in self.groups.items():
            self.groups_list.addItem(f"{group_name} ({member_count})")
    
    def update_users_list(self):
        """Update the users list"""
        self.users_list.clear()
        for username in self.users:
            self.users_list.addItem(username)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop the client
        if self.client:
            self.client.stop()
            
        event.accept()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="UDP Group Chat Client")
    parser.add_argument("-s", "--server", default="127.0.0.1", help="Server hostname or IP")
    parser.add_argument("-p", "--port", type=int, default=5000, help="Server port")
    parser.add_argument("-u", "--username", help="Username")
    return parser.parse_args()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Get username if not provided
    username = args.username
    if not username:
        username = input("Enter your username: ")
        
    # Start the application
    app = QApplication(sys.argv)
    window = UDPGroupChatClient(args.server, args.port, username)
    window.show()
    sys.exit(app.exec_()) 