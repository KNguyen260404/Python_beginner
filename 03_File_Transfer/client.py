#!/usr/bin/env python3
import sys
import socket
import json
import os
import threading
import time
import select
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QFileDialog, QListWidget, QProgressBar,
                           QLineEdit, QMessageBox, QInputDialog, QSplitter, QTableWidget,
                           QTableWidgetItem, QHeaderView, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize, QThread
from PyQt5.QtGui import QIcon, QFont, QDragEnterEvent, QDropEvent

class ClientSignals(QObject):
    """Signals for client events"""
    connected = pyqtSignal(dict)
    error = pyqtSignal(str)
    file_list_updated = pyqtSignal(list)
    upload_progress = pyqtSignal(float)
    upload_completed = pyqtSignal(dict)
    download_progress = pyqtSignal(float)
    download_completed = pyqtSignal(dict)
    file_deleted = pyqtSignal(str)

class FileTransferClient:
    """Client for file transfer operations"""
    def __init__(self, host='localhost', port=9000, buffer_size=4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.socket = None
        self.connected = False
        self.client_name = "Unknown"
        self.signals = ClientSignals()
    
    def connect(self, client_name):
        """Connect to server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.client_name = client_name
            
            # Send client info
            self.send_json({
                'client_name': client_name
            })
            
            # Receive server response
            response = self.receive_json()
            if response and response.get('status') == 'connected':
                self.connected = True
                self.signals.connected.emit(response)
                return True
            else:
                self.signals.error.emit("Failed to connect to server")
                return False
        
        except Exception as e:
            self.signals.error.emit(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
    
    def list_files(self):
        """Get list of files from server"""
        if not self.connected:
            self.signals.error.emit("Not connected to server")
            return
        
        try:
            self.send_json({
                'action': 'list_files'
            })
            
            response = self.receive_json()
            if response and response.get('status') == 'success':
                self.signals.file_list_updated.emit(response.get('files', []))
            else:
                self.signals.error.emit("Failed to get file list")
        
        except Exception as e:
            self.signals.error.emit(f"Error listing files: {str(e)}")
    
    def upload_file(self, file_path):
        """Upload file to server"""
        if not self.connected:
            self.signals.error.emit("Not connected to server")
            return
        
        if not os.path.exists(file_path):
            self.signals.error.emit(f"File not found: {file_path}")
            return
        
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        
        try:
            # Send upload request
            self.send_json({
                'action': 'upload',
                'filename': filename,
                'filesize': filesize
            })
            
            # Wait for server ready
            response = self.receive_json()
            if not response or response.get('status') != 'ready':
                self.signals.error.emit("Server not ready for upload")
                return
            
            # Start upload in a separate thread
            upload_thread = threading.Thread(
                target=self._upload_file_thread,
                args=(file_path, filesize)
            )
            upload_thread.daemon = True
            upload_thread.start()
        
        except Exception as e:
            self.signals.error.emit(f"Error initiating upload: {str(e)}")
    
    def _upload_file_thread(self, file_path, filesize):
        """Thread function for file upload"""
        try:
            sent = 0
            
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(self.buffer_size)
                    if not data:
                        break
                    
                    self.socket.sendall(data)
                    sent += len(data)
                    
                    # Update progress
                    progress = (sent / filesize) * 100
                    self.signals.upload_progress.emit(progress)
                    
                    # Check for progress response from server
                    try:
                        if self.socket.recv in select.select([self.socket], [], [], 0)[0]:
                            response = self.receive_json()
                            # Process progress response if needed
                    except:
                        pass
            
            # Wait for completion confirmation
            response = self.receive_json()
            if response and response.get('status') == 'completed':
                self.signals.upload_completed.emit(response)
            else:
                self.signals.error.emit("Upload failed or incomplete")
        
        except Exception as e:
            self.signals.error.emit(f"Error during upload: {str(e)}")
    
    def download_file(self, filename, save_path):
        """Download file from server"""
        if not self.connected:
            self.signals.error.emit("Not connected to server")
            return
        
        try:
            # Send download request
            self.send_json({
                'action': 'download',
                'filename': filename
            })
            
            # Wait for server response with file info
            response = self.receive_json()
            if not response or response.get('status') != 'ready':
                self.signals.error.emit(f"Error: {response.get('message', 'Server not ready for download')}")
                return
            
            filesize = response.get('filesize', 0)
            
            # Send ready confirmation
            self.send_json({
                'status': 'ready'
            })
            
            # Start download in a separate thread
            download_thread = threading.Thread(
                target=self._download_file_thread,
                args=(filename, save_path, filesize)
            )
            download_thread.daemon = True
            download_thread.start()
        
        except Exception as e:
            self.signals.error.emit(f"Error initiating download: {str(e)}")
    
    def _download_file_thread(self, filename, save_path, filesize):
        """Thread function for file download"""
        try:
            received = 0
            file_path = os.path.join(save_path, filename)
            
            with open(file_path, 'wb') as file:
                while received < filesize:
                    data = self.socket.recv(self.buffer_size)
                    if not data:
                        break
                    
                    file.write(data)
                    received += len(data)
                    
                    # Update progress
                    progress = (received / filesize) * 100
                    self.signals.download_progress.emit(progress)
            
            # Check if download completed
            if received == filesize:
                self.signals.download_completed.emit({
                    'filename': filename,
                    'path': file_path,
                    'size': filesize
                })
            else:
                self.signals.error.emit("Download incomplete")
        
        except Exception as e:
            self.signals.error.emit(f"Error during download: {str(e)}")
    
    def delete_file(self, filename):
        """Delete file from server"""
        if not self.connected:
            self.signals.error.emit("Not connected to server")
            return
        
        try:
            self.send_json({
                'action': 'delete_file',
                'filename': filename
            })
            
            response = self.receive_json()
            if response and response.get('status') == 'success':
                self.signals.file_deleted.emit(filename)
            else:
                self.signals.error.emit(f"Error: {response.get('message', 'Failed to delete file')}")
        
        except Exception as e:
            self.signals.error.emit(f"Error deleting file: {str(e)}")
    
    def send_json(self, data):
        """Send JSON data to server"""
        message = json.dumps(data).encode('utf-8')
        message_length = len(message).to_bytes(4, byteorder='big')
        self.socket.sendall(message_length + message)
    
    def receive_json(self):
        """Receive JSON data from server"""
        try:
            message_length_bytes = self.socket.recv(4)
            if not message_length_bytes:
                return None
            
            message_length = int.from_bytes(message_length_bytes, byteorder='big')
            message = b''
            
            while len(message) < message_length:
                chunk = self.socket.recv(min(message_length - len(message), self.buffer_size))
                if not chunk:
                    break
                message += chunk
            
            return json.loads(message.decode('utf-8'))
        except:
            return None

class DropFileArea(QWidget):
    """Widget that accepts file drops"""
    fileDropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout()
        self.label = QLabel("Kéo thả file vào đây để tải lên")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed #aaa; padding: 30px; border-radius: 10px;")
        layout.addWidget(self.label)
        
        self.setLayout(layout)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.fileDropped.emit(file_path)
                break

class FileTransferWindow(QMainWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.client = FileTransferClient()
        self.setup_ui()
        self.connect_signals()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("File Transfer Client")
        self.setGeometry(100, 100, 900, 600)
        
        # Main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Connection panel
        connection_group = QGroupBox("Kết nối")
        connection_layout = QHBoxLayout()
        
        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("9000")
        self.port_input.setMaximumWidth(100)
        self.name_input = QLineEdit("Client")
        self.connect_button = QPushButton("Kết nối")
        
        connection_layout.addWidget(QLabel("Máy chủ:"))
        connection_layout.addWidget(self.host_input)
        connection_layout.addWidget(QLabel("Cổng:"))
        connection_layout.addWidget(self.port_input)
        connection_layout.addWidget(QLabel("Tên:"))
        connection_layout.addWidget(self.name_input)
        connection_layout.addWidget(self.connect_button)
        
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)
        
        # Split view for file list and upload area
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Server files
        server_files_widget = QWidget()
        server_files_layout = QVBoxLayout()
        
        self.refresh_button = QPushButton("Làm mới danh sách")
        
        self.files_table = QTableWidget(0, 3)
        self.files_table.setHorizontalHeaderLabels(["Tên file", "Kích thước", "Ngày sửa đổi"])
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.files_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        file_actions_layout = QHBoxLayout()
        self.download_button = QPushButton("Tải xuống")
        self.delete_button = QPushButton("Xóa")
        file_actions_layout.addWidget(self.download_button)
        file_actions_layout.addWidget(self.delete_button)
        
        server_files_layout.addWidget(QLabel("File trên máy chủ:"))
        server_files_layout.addWidget(self.refresh_button)
        server_files_layout.addWidget(self.files_table)
        server_files_layout.addLayout(file_actions_layout)
        
        server_files_widget.setLayout(server_files_layout)
        
        # Right panel - Upload area
        upload_widget = QWidget()
        upload_layout = QVBoxLayout()
        
        self.drop_area = DropFileArea()
        self.select_file_button = QPushButton("Chọn file để tải lên")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Chưa kết nối")
        self.status_label.setAlignment(Qt.AlignCenter)
        
        upload_layout.addWidget(QLabel("Tải file lên máy chủ:"))
        upload_layout.addWidget(self.drop_area)
        upload_layout.addWidget(self.select_file_button)
        upload_layout.addWidget(self.progress_bar)
        upload_layout.addWidget(self.status_label)
        
        upload_widget.setLayout(upload_layout)
        
        # Add panels to splitter
        splitter.addWidget(server_files_widget)
        splitter.addWidget(upload_widget)
        splitter.setSizes([500, 400])
        
        main_layout.addWidget(splitter)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Disable controls until connected
        self.set_controls_enabled(False)
    
    def connect_signals(self):
        """Connect signals to slots"""
        # Client signals
        self.client.signals.connected.connect(self.on_connected)
        self.client.signals.error.connect(self.on_error)
        self.client.signals.file_list_updated.connect(self.on_file_list_updated)
        self.client.signals.upload_progress.connect(self.on_upload_progress)
        self.client.signals.upload_completed.connect(self.on_upload_completed)
        self.client.signals.download_progress.connect(self.on_download_progress)
        self.client.signals.download_completed.connect(self.on_download_completed)
        self.client.signals.file_deleted.connect(self.on_file_deleted)
        
        # UI signals
        self.connect_button.clicked.connect(self.on_connect_clicked)
        self.refresh_button.clicked.connect(self.on_refresh_clicked)
        self.download_button.clicked.connect(self.on_download_clicked)
        self.delete_button.clicked.connect(self.on_delete_clicked)
        self.select_file_button.clicked.connect(self.on_select_file_clicked)
        self.drop_area.fileDropped.connect(self.on_file_dropped)
    
    def set_controls_enabled(self, enabled):
        """Enable or disable controls based on connection state"""
        self.refresh_button.setEnabled(enabled)
        self.download_button.setEnabled(enabled)
        self.delete_button.setEnabled(enabled)
        self.select_file_button.setEnabled(enabled)
        self.drop_area.setEnabled(enabled)
        
        # Toggle connection controls
        self.host_input.setEnabled(not enabled)
        self.port_input.setEnabled(not enabled)
        self.name_input.setEnabled(not enabled)
        
        if enabled:
            self.connect_button.setText("Ngắt kết nối")
        else:
            self.connect_button.setText("Kết nối")
    
    def on_connect_clicked(self):
        """Handle connect/disconnect button click"""
        if self.client.connected:
            self.client.disconnect()
            self.set_controls_enabled(False)
            self.status_label.setText("Đã ngắt kết nối")
            self.files_table.setRowCount(0)
        else:
            host = self.host_input.text()
            try:
                port = int(self.port_input.text())
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Cổng không hợp lệ")
                return
            
            client_name = self.name_input.text()
            if not client_name:
                client_name = "Client"
            
            self.client.host = host
            self.client.port = port
            
            if self.client.connect(client_name):
                self.status_label.setText("Đang kết nối...")
            else:
                self.status_label.setText("Kết nối thất bại")
    
    def on_connected(self, response):
        """Handle successful connection"""
        self.set_controls_enabled(True)
        self.status_label.setText(f"Đã kết nối: {response.get('message', '')}")
        self.client.list_files()
    
    def on_error(self, error_message):
        """Handle client error"""
        self.status_label.setText(f"Lỗi: {error_message}")
        QMessageBox.warning(self, "Lỗi", error_message)
    
    def on_refresh_clicked(self):
        """Handle refresh button click"""
        self.client.list_files()
    
    def on_file_list_updated(self, files):
        """Update file list in UI"""
        self.files_table.setRowCount(0)
        
        for file_info in files:
            row = self.files_table.rowCount()
            self.files_table.insertRow(row)
            
            name_item = QTableWidgetItem(file_info.get('name', ''))
            
            # Format file size
            size = file_info.get('size', 0)
            size_str = self.format_size(size)
            size_item = QTableWidgetItem(size_str)
            
            modified_item = QTableWidgetItem(file_info.get('modified', ''))
            
            self.files_table.setItem(row, 0, name_item)
            self.files_table.setItem(row, 1, size_item)
            self.files_table.setItem(row, 2, modified_item)
    
    def format_size(self, size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.2f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"
    
    def on_download_clicked(self):
        """Handle download button click"""
        selected_rows = self.files_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file để tải xuống")
            return
        
        row = selected_rows[0].row()
        filename = self.files_table.item(row, 0).text()
        
        # Ask for save location
        save_dir = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu file")
        if not save_dir:
            return
        
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Đang tải xuống {filename}...")
        
        self.client.download_file(filename, save_dir)
    
    def on_delete_clicked(self):
        """Handle delete button click"""
        selected_rows = self.files_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn file để xóa")
            return
        
        row = selected_rows[0].row()
        filename = self.files_table.item(row, 0).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Xác nhận xóa",
            f"Bạn có chắc muốn xóa file {filename}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.status_label.setText(f"Đang xóa {filename}...")
            self.client.delete_file(filename)
    
    def on_select_file_clicked(self):
        """Handle select file button click"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file để tải lên")
        if file_path:
            self.on_file_dropped(file_path)
    
    def on_file_dropped(self, file_path):
        """Handle file drop event"""
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        filename = os.path.basename(file_path)
        self.status_label.setText(f"Đang tải lên {filename}...")
        
        self.client.upload_file(file_path)
    
    def on_upload_progress(self, progress):
        """Update upload progress"""
        self.progress_bar.setValue(int(progress))
    
    def on_upload_completed(self, response):
        """Handle upload completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Tải lên hoàn tất: {response.get('message', '')}")
        
        # Refresh file list
        self.client.list_files()
    
    def on_download_progress(self, progress):
        """Update download progress"""
        self.progress_bar.setValue(int(progress))
    
    def on_download_completed(self, info):
        """Handle download completion"""
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Tải xuống hoàn tất: {info.get('filename', '')}")
        
        QMessageBox.information(
            self, "Tải xuống hoàn tất",
            f"File {info.get('filename', '')} đã được tải xuống thành công.\n"
            f"Đường dẫn: {info.get('path', '')}"
        )
    
    def on_file_deleted(self, filename):
        """Handle file deletion"""
        self.status_label.setText(f"Đã xóa {filename}")
        
        # Refresh file list
        self.client.list_files()
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.client.connected:
            self.client.disconnect()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTransferWindow()
    window.show()
    sys.exit(app.exec_()) 