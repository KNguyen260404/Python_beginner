# 🐍 10 Dự Án Python Từ Cơ Bản Đến Nâng Cao

Chào mừng bạn đến với bộ sưu tập **10 dự án Python** từ cơ bản đến nâng cao dành cho người học lập trình! 🎉

## 📋 Danh Sách Dự Án

### 🚀 Dự Án Cơ Bản (1-7)
| STT | Dự Án | File | Mô Tả |
|-----|-------|------|-------|
| 1️⃣ | **Calculator** | `01_calculator.py` | Máy tính cơ bản với 4 phép tính |
| 2️⃣ | **Guess Number** | `02_guess_number.py` | Game đoán số thú vị |
| 3️⃣ | **Password Generator** | `03_password_generator.py` | Tạo mật khẩu mạnh |
| 4️⃣ | **Temperature Converter** | `04_temperature_converter.py` | Chuyển đổi nhiệt độ |
| 5️⃣ | **Todo List** | `05_todo_list.py` | Quản lý công việc |
| 6️⃣ | **Rock Paper Scissors** | `06_rock_paper_scissors.py` | Game oẳn tù tì |
| 7️⃣ | **BMI Calculator** | `07_bmi_calculator.py` | Tính chỉ số BMI |

### 🏆 Dự Án Nâng Cao (8-10)
| STT | Dự Án | File | Mô Tả | Công Nghệ |
|-----|-------|------|-------|-----------|
| 8️⃣ | **Library Management System** | `08_library_management.py` | Hệ thống quản lý thư viện | SQLite, OOP |
| 9️⃣ | **Snake Game Advanced** | `09_snake_game.py` | Game rắn săn mồi với GUI | Tkinter, JSON |
| 🔟 | **Personal Finance Manager** | `10_personal_finance.py` | Quản lý tài chính cá nhân | SQLite, Tkinter, Matplotlib |

---

## 🚀 Hướng Dẫn Chạy

### Yêu Cầu Hệ Thống
- 🐍 **Python 3.6+** 
- 💻 **Terminal/Command Prompt**

### Cài Đặt Thư Viện (cho dự án nâng cao)
```bash
# Cho dự án Personal Finance Manager
pip install matplotlib pandas

# Tất cả thư viện cần thiết
pip install tkinter sqlite3 matplotlib pandas
```

### Cách Chạy
```bash
# Di chuyển đến thư mục dự án
cd /home/nguyen2604/Python_beginner

# Chạy dự án cơ bản
python3 01_calculator.py

# Chạy dự án nâng cao
python3 08_library_management.py
python3 09_snake_game.py
python3 10_personal_finance.py
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

## 🏆 DỰ ÁN NÂNG CAO

### 8️⃣ Library Management System - Hệ Thống Quản Lý Thư Viện
**File:** `08_library_management.py`

🎯 **Chức năng:**
- 📚 Quản lý sách (thêm, sửa, xóa, tìm kiếm)
- 👥 Quản lý thành viên thư viện
- 📖 Cho mượn và trả sách
- ⏰ Theo dõi sách quá hạn
- 📊 Báo cáo thống kê
- 🗄️ Lưu trữ dữ liệu SQLite

💡 **Kiến thức nâng cao:**
- SQLite Database
- Object-Oriented Programming (OOP)
- Complex SQL queries
- Data relationships
- Error handling
- Type hints

🖥️ **Demo:**
```
🏛️ HỆ THỐNG QUẢN LÝ THƯ VIỆN
1. 📚 Thêm sách mới
2. 👤 Thêm thành viên mới
3. 🔍 Tìm kiếm sách
4. 📖 Mượn sách
5. 📚 Trả sách

📚 Tìm thấy 5 cuốn sách:
ID   Tên sách                      Tác giả            Thể loại       Năm   Có sẵn/Tổng
1    Lập trình Python cơ bản       Nguyễn Văn A       IT             2023  2/3
```

**📋 Database Schema:**
- 📖 Books: ID, Title, Author, ISBN, Category, Copies
- 👥 Members: ID, Name, Email, Phone, Join Date
- 📝 Transactions: ID, Member, Book, Type, Date, Due Date

---

### 9️⃣ Snake Game Advanced - Game Rắn Săn Mồi Nâng Cao
**File:** `09_snake_game.py`

🎯 **Chức năng:**
- 🎮 Game Snake với giao diện GUI
- 🏆 4 chế độ chơi (Easy, Normal, Hard, Extreme)
- 🌟 Đồ ăn đặc biệt (điểm cao hơn)
- 📊 Bảng xếp hạng điểm cao
- ⏸️ Tạm dừng/Tiếp tục
- 🎨 Hiệu ứng mắt rắn và sparkle
- 💾 Lưu điểm số cao

💡 **Kiến thức nâng cao:**
- Tkinter GUI Programming
- Game development patterns
- Canvas drawing
- Event handling
- JSON data persistence
- Enum và Type hints
- Threading concepts

🖥️ **Demo:**
```
🐍 SNAKE GAME ADVANCED
🎮 Select Game Mode:
🐌 Easy (Slow)
🐍 Normal  
⚡ Hard (Fast)
🚀 Extreme

📊 Tỷ số: Bạn 2450 - Level 8
🏆 TOP 5 SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT:
1. Player1 - Score: 2450 Level: 8 (2023-12-10 15:30:25)
```

**🎮 Game Features:**
- 🕹️ Smooth controls (Arrow keys)
- 🍎 Normal food (+10 points)
- ⭐ Special food (+20 points, 10% chance)
- 📈 Progressive difficulty
- 🎯 Level system
- 👀 Snake eyes animation

---

### 🔟 Personal Finance Manager - Quản Lý Tài Chính Cá Nhân
**File:** `10_personal_finance.py`

🎯 **Chức năng chính:**
- 📊 Dashboard tổng quan tài chính
- 💳 Quản lý thu chi chi tiết
- 💰 Thiết lập và theo dõi ngân sách
- 🎯 Đặt mục tiêu tài chính
- 📈 Báo cáo với biểu đồ trực quan
- 💾 Xuất dữ liệu CSV
- 🗄️ Lưu trữ SQLite

💡 **Kiến thức nâng cao:**
- Advanced Tkinter (Notebook, Treeview, Canvas)
- Matplotlib integration
- Pandas for data analysis
- Complex database relationships
- Financial calculations
- Data visualization
- Export functionality

🖥️ **Demo Dashboard:**
```
💰 Personal Finance Manager

📊 DASHBOARD
┌─────────────────┬─────────────────┬─────────────────┐
│  💰 Thu nhập    │  💸 Chi tiêu    │  💰 Số dư       │
│   5,000,000 VNĐ │   3,200,000 VNĐ │   1,800,000 VNĐ │
└─────────────────┴─────────────────┴─────────────────┘

📋 Recent Transactions:
Date       Type        Category        Amount          Description
2023-12-10 💰 Income   💰 Lương        5,000,000 VNĐ   Lương tháng 12
2023-12-09 💸 Expense  🍔 Ăn uống      150,000 VNĐ     Ăn trưa
```

**📊 Biểu Đồ Bao Gồm:**
- 📈 Thu nhập vs Chi tiêu
- 🥧 Phân bổ chi tiêu theo danh mục
- 📉 Xu hướng số dư tích lũy
- 📊 So sánh ngân sách vs thực tế

**💰 Categories:**
- Thu nhập: Lương, Thưởng, Đầu tư, Freelance
- Chi tiêu: Ăn uống, Nhà ở, Di chuyển, Y tế, Giải trí

---

## 🎓 Kiến Thức Tổng Hợp

### 🏗️ **Cơ Bản (Dự án 1-7)**
- Variables và Data types
- Input/Output operations
- Conditional statements (if/else)
- Loops (while/for)
- Functions

### 🔧 **Trung Cấp (Dự án 1-7)**
- Exception handling
- File operations
- JSON data handling
- Object-oriented programming
- Modules và imports

### 🚀 **Nâng Cao (Dự án 8-10)**
- **Database Design & Management**
  - SQLite advanced queries
  - Database relationships
  - Data integrity
  - Transaction management

- **GUI Development**
  - Tkinter advanced widgets
  - Event-driven programming
  - Canvas graphics
  - Layout management

- **Data Visualization**
  - Matplotlib charts
  - Data analysis with Pandas
  - Interactive reports
  - Export functionality

- **Software Architecture**
  - Design patterns
  - Code organization
  - Error handling strategies
  - Performance optimization

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
├── 🏛️ 08_library_management.py
├── 🐍 09_snake_game.py
├── 💰 10_personal_finance.py
├── 📊 todos.json (tự động tạo)
├── 🗄️ library.db (tự động tạo)
├── 🎯 snake_scores.json (tự động tạo)
└── 💾 personal_finance.db (tự động tạo)
```

---

## 🛠️ Hướng Dẫn Phát Triển

### 🎯 **Lộ Trình Học Tập:**

**👶 Người Mới Bắt Đầu:**
1. `01_calculator.py` - Học cú pháp cơ bản
2. `02_guess_number.py` - Hiểu logic game
3. `04_temperature_converter.py` - Làm quen với hàm

**🚀 Trung Cấp:**
4. `03_password_generator.py` - String manipulation
5. `06_rock_paper_scissors.py` - Game logic phức tạp
6. `07_bmi_calculator.py` - Tính toán và phân loại
7. `05_todo_list.py` - File I/O và JSON

**🏆 Nâng Cao:**
8. `08_library_management.py` - Database và OOP
9. `09_snake_game.py` - GUI và Game development
10. `10_personal_finance.py` - Full-stack application

### 🚀 **Ý Tưởng Mở Rộng:**
**Cho Dự Án Cơ Bản:**
- 🎨 Thêm GUI với tkinter
- 🌐 Tạo web interface với Flask
- 📱 Phát triển mobile app
- 🗄️ Kết nối database
- 🔗 Tích hợp API

**Cho Dự Án Nâng Cao:**
- 🌐 **Web Interface:** Flask/Django web app
- 📱 **Mobile App:** Kivy hoặc BeeWare
- ☁️ **Cloud Integration:** AWS/Google Cloud
- 🔗 **API Development:** REST API với FastAPI
- 🤖 **AI Integration:** Machine Learning features
- 🔒 **Security:** User authentication, encryption
- 📊 **Advanced Analytics:** Predictive modeling

---

## 💻 Yêu Cầu Kỹ Thuật

### 🔧 **Cho Dự Án Cơ Bản (1-7):**
- Python 3.6+
- Thư viện built-in (random, json, datetime, etc.)

### 🏗️ **Cho Dự Án Nâng Cao (8-10):**
```bash
# Yêu cầu bắt buộc
Python 3.8+
tkinter (thường có sẵn)
sqlite3 (built-in)

# Yêu cầu tùy chọn (cho biểu đồ)
pip install matplotlib pandas
```

### 🐧 **Cài Đặt Trên Linux/WSL:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-pip

# Cài đặt thư viện Python
pip3 install matplotlib pandas
```

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

- 📧 **Email:** nguyenvhk.22ceb@vku.udn.vn
- 💬 **Issues:** Tạo issue trên GitHub
- 📚 **Wiki:** Xem thêm tài liệu chi tiết

---

## 🙏 Lời Cảm Ơn

Cảm ơn bạn đã quan tâm đến dự án! Chúc bạn học Python vui vẻ! 🎉🐍

---

### 🏁 Kết Luận

**🎯 Bộ sưu tập 10 dự án này sẽ đưa bạn từ:**
- ✅ **Beginner** → Hiểu cú pháp Python cơ bản
- ✅ **Intermediate** → Làm chủ logic lập trình
- ✅ **Advanced** → Xây dựng ứng dụng thực tế
- ✅ **Expert** → Sẵn sàng cho dự án production

**🚀 Progression Path:**
```
Dự án 1-3: Syntax & Logic → Dự án 4-7: Problem Solving → Dự án 8-10: Real Applications
```

**💼 Career Ready Skills:**
- Database Management
- GUI Development  
- Data Visualization
- Software Architecture
- Project Organization

**Happy Coding!** 🚀💻✨
