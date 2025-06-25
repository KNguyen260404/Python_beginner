# Ứng Dụng Chat Đơn Giản

Ứng dụng chat đơn giản sử dụng socket và PyQt5 để tạo giao diện đồ họa.

## Tính năng

- Chat công khai với tất cả người dùng trực tuyến
- Chat riêng tư giữa hai người dùng
- Tạo và tham gia các nhóm chat
- Hiển thị danh sách người dùng trực tuyến
- Giao diện đồ họa thân thiện với người dùng
- Hỗ trợ nhiều tab chat

## Yêu cầu

- Python 3.6+
- PyQt5
- socket (thư viện chuẩn của Python)
- threading (thư viện chuẩn của Python)
- json (thư viện chuẩn của Python)

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

Server sẽ chạy mặc định trên localhost:9999.

### Khởi động client

```bash
python client.py
```

Sau khi khởi động client:
1. Nhập tên người dùng của bạn
2. Bắt đầu chat trong tab "Main Chat"
3. Double-click vào tên người dùng trong danh sách để bắt đầu chat riêng tư
4. Nhập tên nhóm và nhấn "Join Group" để tạo hoặc tham gia nhóm chat

## Cấu trúc mã nguồn

- `server.py`: Mã nguồn máy chủ chat
- `client.py`: Mã nguồn ứng dụng client với giao diện PyQt5

## Giao thức tin nhắn

Ứng dụng sử dụng JSON để định dạng tin nhắn giữa client và server:

```json
{
  "type": "broadcast|private_message|group_message|system|user_list",
  "message": "Nội dung tin nhắn",
  "sender": "Người gửi",
  "target": "Người nhận (cho tin nhắn riêng tư)",
  "group": "Tên nhóm (cho tin nhắn nhóm)",
  "timestamp": 1234567890
}
```

## Hướng phát triển

- Thêm tính năng mã hóa tin nhắn
- Hỗ trợ gửi file
- Lưu lịch sử chat
- Thêm emoji và định dạng tin nhắn
- Hỗ trợ thông báo âm thanh 