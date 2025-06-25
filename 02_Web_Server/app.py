#!/usr/bin/env python3
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
import os
import json
import psutil
import time
import threading
import logging
from datetime import datetime

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)

# Cấu hình
CONFIG_FILE = 'config.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'html', 'css', 'js'}

# Tạo thư mục uploads nếu chưa tồn tại
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Biến lưu trữ số liệu thống kê
server_stats = {
    'start_time': time.time(),
    'requests': 0,
    'errors': 0,
    'bandwidth_usage': 0,  # bytes
    'active_connections': 0,
    'request_history': []  # [(timestamp, path, method, status_code)]
}

# Đọc cấu hình từ file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        # Cấu hình mặc định
        default_config = {
            'port': 5000,
            'debug': False,
            'max_upload_size': 16 * 1024 * 1024,  # 16MB
            'allowed_extensions': list(ALLOWED_EXTENSIONS),
            'server_name': 'Python Simple Web Server'
        }
        # Lưu cấu hình mặc định
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=4)
        return default_config

config = load_config()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config['max_upload_size']
app.config['SERVER_NAME'] = None  # Không sử dụng SERVER_NAME để tránh lỗi

# Kiểm tra file hợp lệ
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Middleware để theo dõi request
@app.before_request
def before_request():
    server_stats['requests'] += 1
    server_stats['active_connections'] += 1

@app.after_request
def after_request(response):
    server_stats['active_connections'] -= 1
    server_stats['bandwidth_usage'] += len(response.get_data())
    
    # Lưu lịch sử request (giới hạn 100 request gần nhất)
    server_stats['request_history'].append((
        time.time(),
        request.path,
        request.method,
        response.status_code
    ))
    if len(server_stats['request_history']) > 100:
        server_stats['request_history'].pop(0)
    
    return response

@app.errorhandler(Exception)
def handle_error(e):
    server_stats['errors'] += 1
    logging.error(f"Error: {str(e)}")
    return str(e), 500

# Routes
@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files, server_name=config['server_name'])

@app.route('/admin')
def admin():
    # Tính toán thời gian hoạt động
    uptime = time.time() - server_stats['start_time']
    uptime_str = f"{int(uptime // 86400)}d {int((uptime % 86400) // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s"
    
    # Lấy thông tin hệ thống
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Thống kê request
    request_count = server_stats['requests']
    error_count = server_stats['errors']
    bandwidth_usage = server_stats['bandwidth_usage']
    
    # Định dạng bandwidth
    if bandwidth_usage < 1024:
        bandwidth_str = f"{bandwidth_usage} B"
    elif bandwidth_usage < 1024 * 1024:
        bandwidth_str = f"{bandwidth_usage / 1024:.2f} KB"
    else:
        bandwidth_str = f"{bandwidth_usage / (1024 * 1024):.2f} MB"
    
    # Lịch sử request
    history = []
    for timestamp, path, method, status_code in server_stats['request_history']:
        history.append({
            'time': datetime.fromtimestamp(timestamp).strftime('%H:%M:%S'),
            'path': path,
            'method': method,
            'status': status_code
        })
    
    return render_template(
        'admin.html',
        uptime=uptime_str,
        cpu_percent=cpu_percent,
        memory_percent=memory.percent,
        disk_percent=disk.percent,
        request_count=request_count,
        error_count=error_count,
        bandwidth=bandwidth_str,
        active_connections=server_stats['active_connections'],
        request_history=history,
        config=config
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = os.path.basename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        logging.info(f"File uploaded: {filename}")
        return redirect(url_for('index'))
    
    return "File type not allowed", 400

@app.route('/files/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        logging.info(f"File deleted: {filename}")
        return redirect(url_for('index'))
    return "File not found", 404

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'uptime': time.time() - server_stats['start_time'],
        'requests': server_stats['requests'],
        'errors': server_stats['errors'],
        'bandwidth_usage': server_stats['bandwidth_usage'],
        'active_connections': server_stats['active_connections'],
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    })

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    global config
    
    if request.method == 'POST':
        new_config = request.get_json()
        if new_config:
            # Cập nhật cấu hình
            for key in new_config:
                if key in config:
                    config[key] = new_config[key]
            
            # Lưu cấu hình mới
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            
            # Cập nhật cấu hình app
            app.config['MAX_CONTENT_LENGTH'] = config['max_upload_size']
            
            return jsonify({'status': 'success'})
        return jsonify({'status': 'error', 'message': 'Invalid config data'})
    
    return jsonify(config)

if __name__ == '__main__':
    port = config.get('port', 5000)
    debug = config.get('debug', False)
    
    logging.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 