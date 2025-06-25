# Hệ Thống Giám Sát Mạng Đơn Giản

Ứng dụng giám sát mạng với giao diện đồ họa PyQt5 và biểu đồ trực quan.

## Tính năng

- Hiển thị biểu đồ băng thông mạng theo thời gian thực
- Theo dõi tốc độ tải lên và tải xuống
- Liệt kê tất cả các kết nối mạng đang hoạt động
- Hiển thị thông tin chi tiết về các giao diện mạng
- Thống kê tổng lưu lượng dữ liệu đã truyền
- Giao diện đồ họa thân thiện với người dùng

## Yêu cầu

- Python 3.6+
- PyQt5
- matplotlib
- psutil

## Cài đặt

1. Cài đặt các thư viện cần thiết:

```bash
pip install PyQt5 matplotlib psutil
```

## Cách sử dụng

```bash
python network_monitor.py
```

Ứng dụng sẽ mở ra với giao diện đồ họa bao gồm ba tab:

1. **Tổng quan**: Hiển thị biểu đồ băng thông mạng và thống kê tổng quan
2. **Kết nối**: Liệt kê tất cả các kết nối mạng đang hoạt động
3. **Giao diện mạng**: Hiển thị thông tin chi tiết về các giao diện mạng

## Cấu trúc mã nguồn

### Các lớp chính

- `NetworkStats`: Thu thập và quản lý thống kê mạng
- `NetworkMonitorCanvas`: Hiển thị biểu đồ dữ liệu mạng
- `NetworkMonitorApp`: Ứng dụng chính với giao diện PyQt5

### Dữ liệu được thu thập

1. **Thông tin giao diện mạng**:
   - Số bytes đã gửi/nhận
   - Số gói tin đã gửi/nhận

2. **Thông tin kết nối**:
   - Địa chỉ cục bộ và từ xa
   - Trạng thái kết nối
   - PID và tên tiến trình

3. **Lịch sử băng thông**:
   - Tốc độ tải lên/xuống theo thời gian
   - Số lượng kết nối theo thời gian

## Giấy phép

Phần mềm này được phân phối dưới giấy phép MIT.

## Lưu ý

Một số tính năng như giám sát các kết nối mạng có thể yêu cầu quyền quản trị viên trên một số hệ điều hành. Nếu bạn gặp lỗi "Access Denied", hãy thử chạy ứng dụng với quyền quản trị viên. 