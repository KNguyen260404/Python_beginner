#!/usr/bin/env python3
import socket
import threading
import os
import json
import time
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server_log.txt"),
        logging.StreamHandler()
    ]
)

class FileTransferServer:
    def __init__(self, host='0.0.0.0', port=9000, buffer_size=4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.server_socket = None
        self.clients = {}  # {client_address: client_name}
        self.transfers = []  # [(timestamp, client_name, filename, size, status)]
        self.upload_folder = "uploads"
        
        # Tạo thư mục uploads nếu chưa tồn tại
        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder)
    
    def start(self):
        """Khởi động server và lắng nghe kết nối"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            logging.info(f"Server started on {self.host}:{self.port}")
            print(f"Server is listening on {self.host}:{self.port}")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.daemon = True
                client_thread.start()
        
        except KeyboardInterrupt:
            logging.info("Server shutting down...")
            print("Server shutting down...")
        except Exception as e:
            logging.error(f"Server error: {str(e)}")
        finally:
            if self.server_socket:
                self.server_socket.close()
    
    def handle_client(self, client_socket, client_address):
        """Xử lý kết nối từ client"""
        try:
            # Nhận thông tin client
            client_info = self.receive_json(client_socket)
            client_name = client_info.get('client_name', f"Client-{client_address[0]}")
            self.clients[client_address] = client_name
            
            logging.info(f"Client connected: {client_name} ({client_address[0]}:{client_address[1]})")
            
            # Gửi xác nhận kết nối
            self.send_json(client_socket, {
                'status': 'connected',
                'message': f"Connected to server as {client_name}"
            })
            
            # Xử lý các yêu cầu từ client
            while True:
                request = self.receive_json(client_socket)
                if not request:
                    break
                
                action = request.get('action')
                
                if action == 'upload':
                    self.handle_upload(client_socket, client_name, request)
                elif action == 'download':
                    self.handle_download(client_socket, client_name, request)
                elif action == 'list_files':
                    self.handle_list_files(client_socket)
                elif action == 'delete_file':
                    self.handle_delete_file(client_socket, client_name, request)
                else:
                    self.send_json(client_socket, {
                        'status': 'error',
                        'message': 'Unknown action'
                    })
        
        except ConnectionResetError:
            logging.info(f"Client disconnected: {client_address}")
        except Exception as e:
            logging.error(f"Error handling client {client_address}: {str(e)}")
        finally:
            if client_address in self.clients:
                del self.clients[client_address]
            client_socket.close()
    
    def handle_upload(self, client_socket, client_name, request):
        """Xử lý tải file lên từ client"""
        filename = request.get('filename')
        filesize = request.get('filesize')
        
        if not filename or filesize is None:
            self.send_json(client_socket, {
                'status': 'error',
                'message': 'Missing filename or filesize'
            })
            return
        
        # Đảm bảo tên file an toàn
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(self.upload_folder, safe_filename)
        
        # Gửi xác nhận sẵn sàng nhận file
        self.send_json(client_socket, {
            'status': 'ready',
            'message': f"Ready to receive {safe_filename}"
        })
        
        # Nhận và lưu file
        try:
            received = 0
            start_time = time.time()
            
            with open(file_path, 'wb') as file:
                while received < filesize:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        break
                    file.write(data)
                    received += len(data)
                    
                    # Gửi tiến trình
                    if received % (self.buffer_size * 10) == 0 or received == filesize:
                        progress = (received / filesize) * 100
                        self.send_json(client_socket, {
                            'status': 'progress',
                            'progress': progress
                        })
            
            duration = time.time() - start_time
            transfer_speed = filesize / (1024 * 1024 * duration) if duration > 0 else 0  # MB/s
            
            # Thêm vào lịch sử truyền file
            self.transfers.append((
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_name,
                safe_filename,
                filesize,
                'completed'
            ))
            
            # Gửi xác nhận hoàn thành
            self.send_json(client_socket, {
                'status': 'completed',
                'message': f"File {safe_filename} uploaded successfully",
                'duration': duration,
                'speed': transfer_speed
            })
            
            logging.info(f"File uploaded: {safe_filename} ({filesize} bytes) from {client_name}")
        
        except Exception as e:
            logging.error(f"Error during file upload: {str(e)}")
            self.send_json(client_socket, {
                'status': 'error',
                'message': f"Error during file upload: {str(e)}"
            })
            
            # Thêm vào lịch sử truyền file
            self.transfers.append((
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_name,
                safe_filename,
                filesize,
                'failed'
            ))
    
    def handle_download(self, client_socket, client_name, request):
        """Xử lý tải file từ server"""
        filename = request.get('filename')
        
        if not filename:
            self.send_json(client_socket, {
                'status': 'error',
                'message': 'Missing filename'
            })
            return
        
        # Đảm bảo tên file an toàn
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(self.upload_folder, safe_filename)
        
        if not os.path.exists(file_path):
            self.send_json(client_socket, {
                'status': 'error',
                'message': f"File {safe_filename} not found"
            })
            return
        
        filesize = os.path.getsize(file_path)
        
        # Gửi thông tin file
        self.send_json(client_socket, {
            'status': 'ready',
            'filename': safe_filename,
            'filesize': filesize
        })
        
        # Nhận xác nhận từ client
        response = self.receive_json(client_socket)
        if response.get('status') != 'ready':
            return
        
        # Gửi file
        try:
            sent = 0
            start_time = time.time()
            
            with open(file_path, 'rb') as file:
                while True:
                    data = file.read(self.buffer_size)
                    if not data:
                        break
                    client_socket.sendall(data)
                    sent += len(data)
                    
                    # Cập nhật tiến trình
                    if sent % (self.buffer_size * 10) == 0 or sent == filesize:
                        progress = (sent / filesize) * 100
                        # Không gửi tiến trình ở đây vì có thể gây xung đột với dữ liệu file
            
            duration = time.time() - start_time
            transfer_speed = filesize / (1024 * 1024 * duration) if duration > 0 else 0  # MB/s
            
            # Thêm vào lịch sử truyền file
            self.transfers.append((
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_name,
                safe_filename,
                filesize,
                'downloaded'
            ))
            
            logging.info(f"File downloaded: {safe_filename} ({filesize} bytes) by {client_name}")
        
        except Exception as e:
            logging.error(f"Error during file download: {str(e)}")
            
            # Thêm vào lịch sử truyền file
            self.transfers.append((
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                client_name,
                safe_filename,
                filesize,
                'download_failed'
            ))
    
    def handle_list_files(self, client_socket):
        """Xử lý yêu cầu liệt kê danh sách file"""
        try:
            files = []
            for filename in os.listdir(self.upload_folder):
                file_path = os.path.join(self.upload_folder, filename)
                if os.path.isfile(file_path):
                    files.append({
                        'name': filename,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                    })
            
            self.send_json(client_socket, {
                'status': 'success',
                'files': files
            })
        
        except Exception as e:
            logging.error(f"Error listing files: {str(e)}")
            self.send_json(client_socket, {
                'status': 'error',
                'message': f"Error listing files: {str(e)}"
            })
    
    def handle_delete_file(self, client_socket, client_name, request):
        """Xử lý yêu cầu xóa file"""
        filename = request.get('filename')
        
        if not filename:
            self.send_json(client_socket, {
                'status': 'error',
                'message': 'Missing filename'
            })
            return
        
        # Đảm bảo tên file an toàn
        safe_filename = os.path.basename(filename)
        file_path = os.path.join(self.upload_folder, safe_filename)
        
        if not os.path.exists(file_path):
            self.send_json(client_socket, {
                'status': 'error',
                'message': f"File {safe_filename} not found"
            })
            return
        
        try:
            os.remove(file_path)
            
            self.send_json(client_socket, {
                'status': 'success',
                'message': f"File {safe_filename} deleted successfully"
            })
            
            logging.info(f"File deleted: {safe_filename} by {client_name}")
        
        except Exception as e:
            logging.error(f"Error deleting file: {str(e)}")
            self.send_json(client_socket, {
                'status': 'error',
                'message': f"Error deleting file: {str(e)}"
            })
    
    def send_json(self, socket, data):
        """Gửi dữ liệu JSON qua socket"""
        try:
            message = json.dumps(data).encode('utf-8')
            message_length = len(message).to_bytes(4, byteorder='big')
            socket.sendall(message_length + message)
        except Exception as e:
            logging.error(f"Error sending JSON: {str(e)}")
            raise
    
    def receive_json(self, socket):
        """Nhận dữ liệu JSON từ socket"""
        try:
            message_length_bytes = socket.recv(4)
            if not message_length_bytes:
                return None
            
            message_length = int.from_bytes(message_length_bytes, byteorder='big')
            message = b''
            
            while len(message) < message_length:
                chunk = socket.recv(min(message_length - len(message), self.buffer_size))
                if not chunk:
                    break
                message += chunk
            
            return json.loads(message.decode('utf-8'))
        except Exception as e:
            logging.error(f"Error receiving JSON: {str(e)}")
            raise

if __name__ == "__main__":
    server = FileTransferServer()
    server.start() 