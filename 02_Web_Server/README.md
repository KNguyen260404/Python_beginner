# Web Server Đơn Giản với Python

Một web server đơn giản được xây dựng bằng Flask với giao diện quản trị.

## Tính năng

- Giao diện đồ họa dễ sử dụng
- Tải lên và quản lý file
- Bảng điều khiển quản trị với thống kê thời gian thực
- Giám sát tài nguyên hệ thống (CPU, RAM, Disk)
- Lịch sử request
- Cấu hình server qua giao diện web
- API cho thống kê và cấu hình

## Yêu cầu

- Python 3.6+
- Flask
- psutil (để giám sát tài nguyên hệ thống)

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install flask psutil
```

2. Chạy server:

```bash
python app.py
```

Server sẽ chạy mặc định trên http://localhost:5000

## Cấu trúc thư mục

```
02_Web_Server/
├── app.py                  # Mã nguồn chính
├── config.json             # File cấu hình
├── server.log              # File log
├── static/                 # Tài nguyên tĩnh
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/              # Templates HTML
│   ├── admin.html
│   ├── base.html
│   └── index.html
└── uploads/                # Thư mục chứa file tải lên
```

## API

### GET /api/stats

Trả về thống kê hiện tại của server:

```json
{
  "uptime": 3600,
  "requests": 150,
  "errors": 5,
  "bandwidth_usage": 1048576,
  "active_connections": 3,
  "cpu_percent": 25.5,
  "memory_percent": 40.2,
  "disk_percent": 60.0
}
```

### GET /api/config

Trả về cấu hình hiện tại của server:

```json
{
  "port": 5000,
  "debug": false,
  "max_upload_size": 16777216,
  "allowed_extensions": ["txt", "pdf", "png", "jpg", "jpeg", "gif", "html", "css", "js"],
  "server_name": "Python Simple Web Server"
}
```

### POST /api/config

Cập nhật cấu hình server. Gửi JSON với các trường cần cập nhật:

```json
{
  "port": 8080,
  "debug": true,
  "server_name": "My Custom Server"
}
```

## Tùy chỉnh

Bạn có thể tùy chỉnh server bằng cách chỉnh sửa file `config.json` hoặc thông qua giao diện quản trị. 