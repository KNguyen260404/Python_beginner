# 🐍 7 Dự Án Python Nhỏ Cho Người Mới Bắt Đầu

Chào mừng bạn đến với bộ sưu tập **7 dự án Python nhỏ** dành cho người mới học! 🎉

## 📋 Danh Sách Dự Án

| STT | Dự Án | File | Mô Tả |
|-----|-------|------|-------|
| 1️⃣ | **Calculator** | `01_calculator.py` | Máy tính cơ bản với 4 phép tính |
| 2️⃣ | **Guess Number** | `02_guess_number.py` | Game đoán số thú vị |
| 3️⃣ | **Password Generator** | `03_password_generator.py` | Tạo mật khẩu mạnh |
| 4️⃣ | **Temperature Converter** | `04_temperature_converter.py` | Chuyển đổi nhiệt độ |
| 5️⃣ | **Todo List** | `05_todo_list.py` | Quản lý công việc |
| 6️⃣ | **Rock Paper Scissors** | `06_rock_paper_scissors.py` | Game oẳn tù tì |
| 7️⃣ | **BMI Calculator** | `07_bmi_calculator.py` | Tính chỉ số BMI |

---

## 🚀 Hướng Dẫn Chạy

### Yêu Cầu Hệ Thống
- 🐍 **Python 3.6+** 
- 💻 **Terminal/Command Prompt**

### Cách Chạy
```bash
# Di chuyển đến thư mục dự án
cd /home/nguyen2604/Python_beginner

# Chạy dự án bất kỳ
python3 01_calculator.py
```

---

## 📚 Chi Tiết Từng Dự Án

### 1️⃣ Calculator - Máy Tính Cơ Bản
**File:** `01_calculator.py`

🎯 **Chức năng:**
- ➕ Phép cộng
- ➖ Phép trừ  
- ✖️ Phép nhân
- ➗ Phép chia (có kiểm tra chia cho 0)

💡 **Kiến thức học được:**
- Functions (hàm)
- Input/Output
- Exception handling
- While loops

🖥️ **Demo:**
```
=== MÁY TÍNH ĐƠN GIẢN ===
1. Cộng (+)
2. Trừ (-)
3. Nhân (×)
4. Chia (÷)

Chọn phép tính (1-4) hoặc 'q' để thoát: 1
Nhập số thứ nhất: 10
Nhập số thứ hai: 5
Kết quả: 10.0 + 5.0 = 15.0
```

---

### 2️⃣ Guess Number - Game Đoán Số
**File:** `02_guess_number.py`

🎯 **Chức năng:**
- 🎲 Tạo số ngẫu nhiên từ 1-100
- 🎮 Tối đa 7 lần đoán
- 📈📉 Gợi ý lớn hơn/nhỏ hơn
- 🔄 Chơi lại

💡 **Kiến thức học được:**
- Random module
- Game logic
- Recursive function
- User interaction

🖥️ **Demo:**
```
=== GAME ĐOÁN SỐ ===
Tôi đã nghĩ ra một số từ 1 đến 100!

Lần đoán 1/7: 50
📈 Số bạn đoán nhỏ hơn! Thử số lớn hơn.

Lần đoán 2/7: 75
📉 Số bạn đoán lớn hơn! Thử số nhỏ hơn.
```

---

### 3️⃣ Password Generator - Tạo Mật Khẩu
**File:** `03_password_generator.py`

🎯 **Chức năng:**
- 🔐 Tạo mật khẩu ngẫu nhiên
- ⚙️ Tùy chỉnh độ dài và ký tự
- 💪 Kiểm tra độ mạnh mật khẩu
- 💡 Gợi ý cải thiện

💡 **Kiến thức học được:**
- String manipulation
- Random generation
- Password security
- User preferences

🖥️ **Demo:**
```
=== TRÌNH TẠO MẬT KHẨU ===

1. Tạo mật khẩu mới
2. Kiểm tra độ mạnh mật khẩu
3. Thoát

🔐 Mật khẩu được tạo: K8#mP2@vL9$x
💪 Độ mạnh: Rất mạnh
```

---

### 4️⃣ Temperature Converter - Chuyển Đổi Nhiệt Độ
**File:** `04_temperature_converter.py`

🎯 **Chức năng:**
- 🌡️ Celsius ↔ Fahrenheit
- 🌡️ Celsius ↔ Kelvin  
- 🌡️ Fahrenheit ↔ Kelvin
- ✅ Kiểm tra giá trị hợp lệ

💡 **Kiến thức học được:**
- Mathematical formulas
- Unit conversion
- Input validation
- Multiple conversions

🖥️ **Demo:**
```
=== CHUYỂN ĐỔI NHIỆT ĐỘ ===
1. Celsius sang Fahrenheit

Nhập nhiệt độ Celsius: 25
25.0°C = 77.00°F
```

---

### 5️⃣ Todo List - Quản Lý Công Việc
**File:** `05_todo_list.py`

🎯 **Chức năng:**
- ➕ Thêm công việc mới
- 👀 Xem danh sách
- ✅ Đánh dấu hoàn thành
- 🗑️ Xóa công việc
- 🎯 Phân loại ưu tiên (cao/trung/thấp)
- 💾 Lưu trữ dữ liệu (JSON)

💡 **Kiến thức học được:**
- File I/O operations
- JSON handling
- Object-oriented programming
- Data persistence
- Date/time handling

🖥️ **Demo:**
```
=== DANH SÁCH CÔNG VIỆC ===
1. ❌ 🔴 Hoàn thành báo cáo (high)
2. ✅ 🟡 Đi mua sắm (medium)
3. ❌ 🟢 Đọc sách (low)
```

---

### 6️⃣ Rock Paper Scissors - Game Oẳn Tù Tì
**File:** `06_rock_paper_scissors.py`

🎯 **Chức năng:**
- 🪨 Rock (Đá)
- 📄 Paper (Giấy)  
- ✂️ Scissors (Kéo)
- 🤖 AI đối thủ
- 📊 Thống kê tỷ số
- 📈 Tỷ lệ thắng

💡 **Kiến thức học được:**
- Game logic
- Random choices
- Score tracking
- Statistics calculation
- Dictionary usage

🖥️ **Demo:**
```
📊 Tỷ số: Bạn 2 - 1 Máy

🎯 Bạn chọn: Rock 🪨
🤖 Máy chọn: Scissors ✂️
🎉 Bạn thắng!

🏆 Chúc mừng! Bạn thắng tổng thể!
📈 Tỷ lệ thắng của bạn: 66.7%
```

---

### 7️⃣ BMI Calculator - Tính Chỉ Số BMI
**File:** `07_bmi_calculator.py`

🎯 **Chức năng:**
- ⚖️ Tính chỉ số BMI
- 📊 Phân loại theo WHO
- 💡 Lời khuyên sức khỏe
- 🎯 Tính cân nặng lý tưởng
- 📋 Bảng tham khảo đầy đủ

💡 **Kiến thức học được:**
- Mathematical calculations
- Health data analysis
- Conditional logic
- Data categorization
- User-friendly output

🖥️ **Demo:**
```
=== KẾT QUẢ ===
📏 Chiều cao: 1.7m
⚖️ Cân nặng: 65.0kg
📊 BMI: 22.5
🟢 Phân loại: Bình thường

🎯 Cân nặng lý tưởng cho bạn: 53.5 - 72.0 kg
```

---

## 🎓 Kiến Thức Tổng Hợp

Qua 7 dự án này, bạn sẽ học được:

### 🏗️ **Cơ Bản**
- Variables và Data types
- Input/Output operations
- Conditional statements (if/else)
- Loops (while/for)
- Functions

### 🔧 **Trung Cấp**
- Exception handling
- File operations
- JSON data handling
- Object-oriented programming
- Modules và imports

### 🚀 **Nâng Cao**
- Data persistence
- User interface design
- Algorithm implementation
- Code organization
- Best practices

---

## 📁 Cấu Trúc Thư Mục

```
Python_beginner/
├── 📄 README.md
├── 🧮 01_calculator.py
├── 🎲 02_guess_number.py
├── 🔐 03_password_generator.py
├── 🌡️ 04_temperature_converter.py
├── 📝 05_todo_list.py
├── 🎮 06_rock_paper_scissors.py
├── ⚖️ 07_bmi_calculator.py
└── 📊 todos.json (tự động tạo)
```

---

## 🛠️ Hướng Dẫn Phát Triển

### 🎯 **Dành Cho Người Mới:**
1. Bắt đầu với `01_calculator.py` (đơn giản nhất)
2. Tiếp tục với `02_guess_number.py` 
3. Thử thách với `05_todo_list.py` (phức tạp nhất)

### 🚀 **Ý Tưởng Mở Rộng:**
- 🎨 Thêm GUI với tkinter
- 🌐 Tạo web interface với Flask
- 📱 Phát triển mobile app
- 🗄️ Kết nối database
- 🔗 Tích hợp API

---

## 🤝 Đóng Góp

Bạn có ý tưởng cải thiện? Hãy:
1. 🍴 Fork repository
2. 🔧 Tạo feature branch
3. 💡 Thêm tính năng mới
4. 📝 Viết documentation
5. 🚀 Tạo pull request

---

## 📞 Liên Hệ & Hỗ Trợ

- 📧 **Email:** nguyen2604@example.com
- 💬 **Issues:** Tạo issue trên GitHub
- 📚 **Wiki:** Xem thêm tài liệu chi tiết

---

## 📜 Giấy Phép

Dự án này được phát hành dưới giấy phép **MIT License** 📄

---

## 🙏 Lời Cảm Ơn

Cảm ơn bạn đã quan tâm đến dự án! Chúc bạn học Python vui vẻ! 🎉🐍

---

### 🏁 Kết Luận

Những dự án này là bước đệm hoàn hảo để bạn:
- ✅ Làm quen với Python
- ✅ Hiểu logic lập trình  
- ✅ Xây dựng portfolio
- ✅ Chuẩn bị cho dự án lớn hơn

**Happy Coding!** 🚀💻✨
