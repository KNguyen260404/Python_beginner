# Trình phân tích gói tin mạng (Packet Analyzer)

Ứng dụng phân tích gói tin mạng với giao diện đồ họa sử dụng Python và PyQt5, cho phép người dùng bắt và phân tích các gói tin mạng theo thời gian thực.

## Tính năng

- **Bắt gói tin mạng** theo thời gian thực từ các giao diện mạng
- **Lọc gói tin** theo các tiêu chí như giao thức, địa chỉ IP, cổng
- **Hiển thị thông tin chi tiết** của từng gói tin
- **Phân tích cấu trúc gói tin** theo từng lớp giao thức
- **Hiển thị dữ liệu dạng hex** của gói tin
- **Lưu gói tin** vào file định dạng PCAP để phân tích sau
- **Phân tích các giao thức phổ biến** như TCP, UDP, ICMP, ARP, HTTP, DNS

## Yêu cầu

- Python 3.6+
- PyQt5
- Scapy
- Quyền quản trị để bắt gói tin mạng (trên hầu hết các hệ điều hành)

## Cài đặt

```bash
# Cài đặt các thư viện cần thiết
pip install PyQt5 scapy

# Trên Linux, có thể cần cài đặt thêm
sudo apt-get install tcpdump
```

## Sử dụng

1. Chạy ứng dụng với quyền quản trị:

```bash
# Trên Windows
python packet_analyzer.py

# Trên Linux/Mac
sudo python3 packet_analyzer.py
```

2. Chọn giao diện mạng muốn bắt gói tin
3. Tùy chọn cấu hình bộ lọc (sử dụng cú pháp BPF như "tcp port 80")
4. Nhấn "Bắt đầu bắt gói tin"
5. Xem thông tin gói tin trong bảng và chi tiết khi chọn một gói tin
6. Lưu các gói tin đã bắt vào file PCAP nếu cần

## Lưu ý

- Bắt gói tin mạng yêu cầu quyền quản trị trên hầu hết các hệ điều hành
- Bộ lọc sử dụng cú pháp Berkeley Packet Filter (BPF)
- Một số giao diện mạng có thể không hỗ trợ chế độ bắt gói tin

## Ví dụ bộ lọc hữu ích

- `tcp port 80`: Bắt gói tin HTTP
- `tcp port 443`: Bắt gói tin HTTPS
- `host 8.8.8.8`: Bắt gói tin đến/từ Google DNS
- `icmp`: Chỉ bắt gói tin ICMP (ping)
- `arp`: Chỉ bắt gói tin ARP
- `udp port 53`: Bắt gói tin DNS
