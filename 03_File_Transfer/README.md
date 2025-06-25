# Ứng Dụng Truyền File Client-Server

Ứng dụng truyền file giữa client và server với giao diện đồ họa PyQt5.

## Tính năng

- Giao diện đồ họa thân thiện với người dùng
- Kéo thả file để tải lên
- Hiển thị tiến trình tải lên/tải xuống
- Quản lý file trên server (xem, tải xuống, xóa)
- Hỗ trợ nhiều client kết nối đồng thời
- Theo dõi lịch sử truyền file

## Yêu cầu

- Python 3.6+
- PyQt5
- Các thư viện chuẩn của Python: socket, threading, json, os

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install PyQt5
```

## Cách sử dụng

### Khởi động server

```bash
python server.py
```

Server sẽ chạy mặc định trên cổng 9000 và lắng nghe kết nối từ tất cả các địa chỉ IP.

### Khởi động client

```bash
python client.py
```

Sau khi khởi động client:

1. Nhập thông tin kết nối (máy chủ, cổng, tên) và nhấn "Kết nối"
2. Sau khi kết nối thành công, danh sách file trên server sẽ được hiển thị
3. Để tải file lên server:
   - Kéo thả file vào vùng kéo thả, hoặc
   - Nhấn nút "Chọn file để tải lên" và chọn file từ hộp thoại
4. Để tải file từ server:
   - Chọn file từ danh sách và nhấn nút "Tải xuống"
   - Chọn thư mục để lưu file
5. Để xóa file trên server:
   - Chọn file từ danh sách và nhấn nút "Xóa"
   - Xác nhận xóa

## Cấu trúc mã nguồn

- `server.py`: Mã nguồn máy chủ truyền file
- `client.py`: Mã nguồn ứng dụng client với giao diện PyQt5

## Giao thức truyền file

Ứng dụng sử dụng socket TCP và định dạng JSON để trao đổi thông tin giữa client và server. Mỗi tin nhắn JSON được gửi đi kèm với độ dài của tin nhắn (4 byte) để đảm bảo toàn vẹn dữ liệu.

### Các loại tin nhắn

1. **Kết nối client**:
   - Client gửi: `{"client_name": "Name"}`
   - Server trả về: `{"status": "connected", "message": "..."}`

2. **Liệt kê file**:
   - Client gửi: `{"action": "list_files"}`
   - Server trả về: `{"status": "success", "files": [{"name": "...", "size": 1234, "modified": "..."}]}`

3. **Tải file lên**:
   - Client gửi: `{"action": "upload", "filename": "...", "filesize": 1234}`
   - Server trả về: `{"status": "ready", "message": "..."}`
   - Client gửi dữ liệu file
   - Server cập nhật tiến trình: `{"status": "progress", "progress": 45.5}`
   - Server trả về khi hoàn thành: `{"status": "completed", "message": "...", "duration": 1.23, "speed": 1.45}`

4. **Tải file xuống**:
   - Client gửi: `{"action": "download", "filename": "..."}`
   - Server trả về: `{"status": "ready", "filename": "...", "filesize": 1234}`
   - Client gửi: `{"status": "ready"}`
   - Server gửi dữ liệu file

5. **Xóa file**:
   - Client gửi: `{"action": "delete_file", "filename": "..."}`
   - Server trả về: `{"status": "success", "message": "..."}` 