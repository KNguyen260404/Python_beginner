# Ứng Dụng Quét Cổng Mạng (Port Scanner)

Ứng dụng quét cổng mạng với giao diện đồ họa PyQt5, hỗ trợ quét TCP, UDP và SYN.

## Tính năng

- Giao diện đồ họa thân thiện với người dùng
- Hỗ trợ quét TCP, UDP và SYN
- Quét đa luồng để tăng tốc độ
- Hiển thị tiến trình quét theo thời gian thực
- Tự động nhận diện dịch vụ phổ biến
- Tạo và lưu báo cáo quét
- Tùy chọn quét nhanh cho các cổng phổ biến

## Yêu cầu

- Python 3.6+
- PyQt5
- socket (thư viện chuẩn của Python)
- threading (thư viện chuẩn của Python)

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install PyQt5
```

## Cách sử dụng

```bash
python port_scanner.py
```

### Hướng dẫn sử dụng

1. Nhập địa chỉ IP hoặc tên miền mục tiêu
2. Chọn dải cổng cần quét
3. Chọn kiểu quét (TCP, UDP, SYN)
4. Điều chỉnh timeout và số luồng nếu cần
5. Tùy chọn chỉ quét các cổng phổ biến
6. Nhấn "Bắt đầu quét"
7. Xem kết quả quét trong bảng
8. Chuyển sang tab "Báo cáo" để tạo và lưu báo cáo

## Các kiểu quét

- **TCP**: Quét kết nối TCP đầy đủ, đáng tin cậy nhưng chậm hơn
- **UDP**: Quét cổng UDP, ít chính xác hơn do bản chất của UDP
- **SYN**: Mô phỏng quét SYN (trong thực tế cần quyền root)

## Danh sách cổng phổ biến

Ứng dụng có sẵn danh sách các cổng phổ biến và dịch vụ tương ứng:

- 20, 21: FTP
- 22: SSH
- 23: Telnet
- 25, 465, 587: SMTP
- 53: DNS
- 80, 443: HTTP/HTTPS
- 110, 995: POP3
- 143, 993: IMAP
- 3306: MySQL
- 3389: RDP
- 5432: PostgreSQL
- 8080: HTTP Proxy
- Và nhiều cổng khác...

## Lưu ý

- Quét cổng mạng trên các hệ thống mà bạn không có quyền có thể là bất hợp pháp. Chỉ sử dụng công cụ này trên các hệ thống mà bạn được phép quét.
- Quét UDP và SYN có thể yêu cầu quyền quản trị viên trên một số hệ điều hành.
- Kết quả quét có thể bị ảnh hưởng bởi tường lửa và các biện pháp bảo mật mạng khác. 