# Math Equation Solver - Giải Phương Trình

Ứng dụng Math Equation Solver là một công cụ toán học đa năng được phát triển bằng Python, giúp người dùng giải quyết nhiều loại bài toán khác nhau, từ phương trình đơn giản đến phức tạp, tính toán tích phân, chuyển đổi hệ cơ số, tính toán ma trận và vẽ đồ thị hàm số.

## Tính năng chính

### 1. Giải phương trình
- Giải phương trình từ bậc 1 đến bậc 6
- Hiển thị các bước giải chi tiết
- Vẽ đồ thị hàm số
- Hỗ trợ nhiều loại phương trình khác nhau

### 2. Tích phân và Nguyên hàm
- Tính nguyên hàm (tích phân bất định)
- Tính tích phân xác định với các cận tích phân
- Vẽ đồ thị hàm số và diện tích dưới đường cong
- Hiển thị các bước tính tích phân

### 3. Chuyển đổi hệ cơ số
- Chuyển đổi giữa các hệ cơ số: nhị phân, bát phân, thập phân, thập lục phân
- Hiển thị các bước chuyển đổi chi tiết
- Kiểm tra tính hợp lệ của số đầu vào
- Các ví dụ minh họa

### 4. Tính toán ma trận
- **Phép toán ma trận đơn:**
  - Tính định thức ma trận
  - Tìm ma trận nghịch đảo
  - Tính ma trận chuyển vị
  - Tính hạng của ma trận
  - Hiển thị các bước tính toán chi tiết

- **Phép toán hai ma trận:**
  - Cộng hai ma trận
  - Trừ hai ma trận
  - Nhân hai ma trận
  - Kiểm tra điều kiện thực hiện phép toán
  - Hiển thị các bước tính toán chi tiết

- **Giải hệ phương trình tuyến tính:**
  - Giải hệ phương trình bằng phương pháp ma trận
  - Phân tích hệ có nghiệm duy nhất, vô nghiệm hoặc vô số nghiệm
  - Hiển thị các bước giải bằng phương pháp khử Gauss
  - Kiểm tra nghiệm bằng cách thế lại vào hệ phương trình

### 5. Vẽ đồ thị hàm số
- Vẽ đồ thị nhiều hàm số cùng lúc
- Mỗi hàm số được hiển thị với màu sắc khác nhau
- Có thể xóa từng hàm số hoặc tất cả các hàm số
- Tùy chỉnh phạm vi đồ thị (giá trị x và y)
- Các ví dụ hàm số phổ biến có sẵn để sử dụng
- Hiển thị chú thích màu sắc cho từng đường đồ thị

## Yêu cầu hệ thống
- Python 3.6 trở lên
- Thư viện: tkinter, numpy, sympy, matplotlib

## Cài đặt
1. Đảm bảo đã cài đặt Python
2. Cài đặt các thư viện cần thiết:
   ```
   pip install numpy sympy matplotlib
   ```
3. Chạy ứng dụng:
   ```
   python 21_math_equation_solver.py
   ```
   Hoặc sử dụng file script:
   - Windows: Chạy `run_equation_solver.bat`
   - Linux/Mac: Chạy `run_equation_solver.sh`

## Hướng dẫn sử dụng

### Giải phương trình
1. Nhập phương trình vào ô nhập liệu
2. Chọn loại phương trình
3. Nhấn nút "Giải phương trình"
4. Kết quả và các bước giải sẽ hiển thị ở phần kết quả

### Tính tích phân
1. Nhập hàm cần tính tích phân
2. Chọn loại tích phân (bất định hoặc xác định)
3. Nếu là tích phân xác định, nhập cận dưới và cận trên
4. Nhấn nút "Tính tích phân"
5. Kết quả và đồ thị sẽ hiển thị ở phần kết quả

### Chuyển đổi hệ cơ số
1. Nhập số cần chuyển đổi
2. Chọn hệ cơ số của số đã nhập
3. Chọn hệ cơ số đích cần chuyển đổi sang
4. Nhấn nút "Chuyển đổi"
5. Kết quả và các bước chuyển đổi sẽ hiển thị ở phần kết quả

### Tính toán ma trận
1. Chọn tab tương ứng với loại phép toán ma trận cần thực hiện
2. Nhập ma trận (hoặc các ma trận) theo định dạng yêu cầu
3. Chọn phép toán cần thực hiện
4. Kết quả và các bước tính toán sẽ hiển thị ở phần kết quả

### Vẽ đồ thị hàm số
1. Nhập hàm số vào ô nhập liệu (ví dụ: x^2 + 2*x + 1)
2. Nhấn nút "Thêm" để thêm hàm số vào danh sách
3. Có thể thêm nhiều hàm số khác nhau, mỗi hàm sẽ có một màu riêng
4. Nhấn nút "×" bên cạnh hàm số để xóa hàm đó khỏi đồ thị
5. Tùy chỉnh phạm vi đồ thị bằng cách nhập giá trị X min, X max, Y min, Y max
6. Nhấn nút "Vẽ đồ thị" để cập nhật đồ thị theo phạm vi mới
7. Nhấn nút "Xóa tất cả" để xóa toàn bộ hàm số và đặt lại đồ thị

## Lưu ý
- Đối với phương trình, sử dụng cú pháp tiêu chuẩn (ví dụ: x^2 + 2*x + 1 = 0)
- Đối với tích phân, sử dụng biến x (ví dụ: x^2 + sin(x))
- Đối với ma trận, nhập mỗi hàng trên một dòng, các phần tử cách nhau bởi dấu cách
- Đối với đồ thị hàm số, có thể sử dụng các hàm toán học như sin(x), cos(x), exp(x), log(x)

## Tác giả
Ứng dụng được phát triển bởi [Tên tác giả]

## Giấy phép
[Loại giấy phép] 