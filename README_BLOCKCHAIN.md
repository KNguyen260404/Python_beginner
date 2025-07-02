# Blockchain Simulator

## Giới thiệu

Blockchain Simulator là một ứng dụng mô phỏng blockchain và tiền điện tử hoàn chỉnh được xây dựng bằng Python. Ứng dụng này giúp người dùng hiểu rõ hơn về cách thức hoạt động của công nghệ blockchain và các khái niệm cơ bản của tiền điện tử như đào coin, giao dịch, ký số và xác thực.

## Tính năng

- **Blockchain hoàn chỉnh**: Triển khai đầy đủ cấu trúc blockchain với các khối, giao dịch và cơ chế đồng thuận
- **Ví tiền điện tử**: Tạo và quản lý nhiều ví với cặp khóa công khai/riêng tư
- **Đào coin**: Mô phỏng quá trình đào coin với cơ chế Proof of Work
- **Giao dịch**: Tạo, ký và xác thực các giao dịch
- **Giao diện đồ họa**: Giao diện người dùng trực quan để tương tác với blockchain
- **Trực quan hóa dữ liệu**: Biểu đồ và đồ thị để theo dõi hoạt động của blockchain

## Cài đặt

1. Đảm bảo bạn đã cài đặt Python 3.8 trở lên
2. Cài đặt các thư viện phụ thuộc:

```bash
pip install -r requirements_blockchain.txt
```

## Cách sử dụng

Chạy ứng dụng bằng lệnh:

```bash
python 23_blockchain_simulator.py
```

### Hướng dẫn nhanh

1. **Tạo ví mới**: Chọn "Wallet" > "Create New Wallet" từ menu
2. **Đào coin**: Chọn tab "Mining" và nhấn "Start Mining"
3. **Gửi tiền**: Chọn tab "Wallet", nhập địa chỉ người nhận và số tiền, sau đó nhấn "Send"
4. **Xem blockchain**: Chọn tab "Blockchain" để xem toàn bộ chuỗi khối

## Kiến thức kỹ thuật

Dự án này minh họa các khái niệm quan trọng của blockchain:

- **Cấu trúc dữ liệu blockchain**: Chuỗi các khối được liên kết bằng hàm băm
- **Proof of Work**: Cơ chế đồng thuận dựa trên sức mạnh tính toán
- **Mã hóa khóa công khai**: Sử dụng ECDSA để tạo chữ ký số và xác thực
- **Merkle Tree**: Cấu trúc dữ liệu hiệu quả để xác minh giao dịch
- **UTXO**: Mô hình Unspent Transaction Output để theo dõi số dư
- **Mempool**: Khu vực lưu trữ các giao dịch chưa được xác nhận

## Cấu trúc mã nguồn

- **Transaction**: Đại diện cho một giao dịch tiền điện tử
- **Block**: Đại diện cho một khối trong blockchain
- **Blockchain**: Quản lý chuỗi khối và các giao dịch
- **Wallet**: Quản lý khóa và tạo giao dịch
- **BlockchainGUI**: Giao diện người dùng đồ họa

## Mở rộng

Một số ý tưởng để mở rộng dự án:

- Thêm cơ chế đồng thuận Proof of Stake
- Triển khai hợp đồng thông minh đơn giản
- Thêm tính năng mạng ngang hàng thực sự
- Tối ưu hóa hiệu suất cho blockchain lớn hơn
- Thêm tính năng phân tích và trực quan hóa dữ liệu nâng cao

## Tài nguyên học tập

- [Bitcoin Whitepaper](https://bitcoin.org/bitcoin.pdf)
- [Mastering Bitcoin](https://github.com/bitcoinbook/bitcoinbook)
- [Blockchain Basics](https://www.coursera.org/learn/blockchain-basics)

## Yêu cầu hệ thống

- Python 3.8+
- Tkinter (thường có sẵn trong Python)
- Matplotlib
- NumPy
- ECDSA

## Giấy phép

Dự án này được phân phối theo giấy phép MIT. 