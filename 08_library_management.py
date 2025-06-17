import sqlite3
import datetime
from typing import List, Optional, Dict
import json

class Book:
    def __init__(self, book_id: int, title: str, author: str, isbn: str, 
                 category: str, published_year: int, total_copies: int):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.published_year = published_year
        self.total_copies = total_copies
        self.available_copies = total_copies

class Member:
    def __init__(self, member_id: int, name: str, email: str, phone: str, address: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.join_date = datetime.date.today()
        self.borrowed_books = []

class Transaction:
    def __init__(self, transaction_id: int, member_id: int, book_id: int, 
                 transaction_type: str, date: datetime.date):
        self.transaction_id = transaction_id
        self.member_id = member_id
        self.book_id = book_id
        self.transaction_type = transaction_type  # 'borrow' or 'return'
        self.date = date
        self.due_date = date + datetime.timedelta(days=14) if transaction_type == 'borrow' else None

class LibraryDatabase:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tạo bảng books
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                book_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                isbn TEXT UNIQUE,
                category TEXT,
                published_year INTEGER,
                total_copies INTEGER DEFAULT 1,
                available_copies INTEGER DEFAULT 1
            )
        ''')
        
        # Tạo bảng members
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT,
                address TEXT,
                join_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        # Tạo bảng transactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                member_id INTEGER,
                book_id INTEGER,
                transaction_type TEXT CHECK(transaction_type IN ('borrow', 'return')),
                transaction_date DATE DEFAULT CURRENT_DATE,
                due_date DATE,
                FOREIGN KEY (member_id) REFERENCES members (member_id),
                FOREIGN KEY (book_id) REFERENCES books (book_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        conn.commit()
        conn.close()
        return result

class LibraryManagement:
    def __init__(self):
        self.db = LibraryDatabase()
        print("🏛️ Hệ thống quản lý thư viện đã khởi tạo!")
    
    def add_book(self, title: str, author: str, isbn: str, category: str, 
                 published_year: int, copies: int = 1):
        try:
            query = '''
                INSERT INTO books (title, author, isbn, category, published_year, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            self.db.execute_query(query, (title, author, isbn, category, published_year, copies, copies))
            print(f"✅ Đã thêm sách: {title}")
        except sqlite3.IntegrityError:
            print(f"❌ Sách với ISBN {isbn} đã tồn tại!")
    
    def add_member(self, name: str, email: str, phone: str, address: str):
        try:
            query = '''
                INSERT INTO members (name, email, phone, address)
                VALUES (?, ?, ?, ?)
            '''
            self.db.execute_query(query, (name, email, phone, address))
            print(f"✅ Đã thêm thành viên: {name}")
        except sqlite3.IntegrityError:
            print(f"❌ Email {email} đã được sử dụng!")
    
    def search_books(self, keyword: str = "", category: str = ""):
        query = '''
            SELECT book_id, title, author, isbn, category, published_year, total_copies, available_copies
            FROM books
            WHERE (title LIKE ? OR author LIKE ? OR isbn LIKE ?)
        '''
        params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        books = self.db.execute_query(query, tuple(params))
        
        if books:
            print(f"\n📚 Tìm thấy {len(books)} cuốn sách:")
            print("-" * 100)
            print(f"{'ID':<5}{'Tên sách':<30}{'Tác giả':<20}{'Thể loại':<15}{'Năm':<6}{'Có sẵn/Tổng':<12}")
            print("-" * 100)
            for book in books:
                print(f"{book[0]:<5}{book[1][:29]:<30}{book[2][:19]:<20}{book[4]:<15}{book[5]:<6}{book[7]}/{book[6]:<12}")
        else:
            print("❌ Không tìm thấy sách nào!")
    
    def borrow_book(self, member_id: int, book_id: int):
        # Kiểm tra thành viên
        member_query = "SELECT name FROM members WHERE member_id = ?"
        member = self.db.execute_query(member_query, (member_id,))
        if not member:
            print("❌ Thành viên không tồn tại!")
            return
        
        # Kiểm tra sách có sẵn
        book_query = "SELECT title, available_copies FROM books WHERE book_id = ?"
        book = self.db.execute_query(book_query, (book_id,))
        if not book:
            print("❌ Sách không tồn tại!")
            return
        
        if book[0][1] <= 0:
            print("❌ Sách đã hết!")
            return
        
        # Kiểm tra thành viên đã mượn sách này chưa
        borrowed_query = '''
            SELECT COUNT(*) FROM transactions 
            WHERE member_id = ? AND book_id = ? AND transaction_type = 'borrow'
            AND transaction_id NOT IN (
                SELECT t1.transaction_id FROM transactions t1
                JOIN transactions t2 ON t1.member_id = t2.member_id AND t1.book_id = t2.book_id
                WHERE t1.transaction_type = 'borrow' AND t2.transaction_type = 'return'
                AND t2.transaction_date > t1.transaction_date
            )
        '''
        already_borrowed = self.db.execute_query(borrowed_query, (member_id, book_id))
        if already_borrowed[0][0] > 0:
            print("❌ Thành viên đã mượn sách này rồi!")
            return
        
        # Thực hiện mượn sách
        due_date = datetime.date.today() + datetime.timedelta(days=14)
        transaction_query = '''
            INSERT INTO transactions (member_id, book_id, transaction_type, due_date)
            VALUES (?, ?, 'borrow', ?)
        '''
        self.db.execute_query(transaction_query, (member_id, book_id, due_date))
        
        # Cập nhật số sách có sẵn
        update_query = "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?"
        self.db.execute_query(update_query, (book_id,))
        
        print(f"✅ {member[0][0]} đã mượn '{book[0][0]}' thành công!")
        print(f"📅 Hạn trả: {due_date.strftime('%d/%m/%Y')}")
    
    def return_book(self, member_id: int, book_id: int):
        # Kiểm tra sách đã được mượn chưa
        borrowed_query = '''
            SELECT t.transaction_id, b.title, m.name FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            JOIN members m ON t.member_id = m.member_id
            WHERE t.member_id = ? AND t.book_id = ? AND t.transaction_type = 'borrow'
            AND t.transaction_id NOT IN (
                SELECT t1.transaction_id FROM transactions t1
                JOIN transactions t2 ON t1.member_id = t2.member_id AND t1.book_id = t2.book_id
                WHERE t1.transaction_type = 'borrow' AND t2.transaction_type = 'return'
                AND t2.transaction_date > t1.transaction_date
            )
        '''
        borrowed = self.db.execute_query(borrowed_query, (member_id, book_id))
        if not borrowed:
            print("❌ Không tìm thấy giao dịch mượn sách!")
            return
        
        # Thực hiện trả sách
        return_query = '''
            INSERT INTO transactions (member_id, book_id, transaction_type)
            VALUES (?, ?, 'return')
        '''
        self.db.execute_query(return_query, (member_id, book_id))
        
        # Cập nhật số sách có sẵn
        update_query = "UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?"
        self.db.execute_query(update_query, (book_id,))
        
        print(f"✅ {borrowed[0][2]} đã trả '{borrowed[0][1]}' thành công!")
    
    def view_overdue_books(self):
        query = '''
            SELECT m.name, b.title, t.due_date, 
                   julianday('now') - julianday(t.due_date) as days_overdue
            FROM transactions t
            JOIN members m ON t.member_id = m.member_id
            JOIN books b ON t.book_id = b.book_id
            WHERE t.transaction_type = 'borrow' AND t.due_date < date('now')
            AND t.transaction_id NOT IN (
                SELECT t1.transaction_id FROM transactions t1
                JOIN transactions t2 ON t1.member_id = t2.member_id AND t1.book_id = t2.book_id
                WHERE t1.transaction_type = 'borrow' AND t2.transaction_type = 'return'
                AND t2.transaction_date > t1.transaction_date
            )
        '''
        overdue = self.db.execute_query(query)
        
        if overdue:
            print(f"\n⚠️ Có {len(overdue)} sách quá hạn:")
            print("-" * 80)
            print(f"{'Thành viên':<25}{'Tên sách':<30}{'Hạn trả':<12}{'Quá hạn':<10}")
            print("-" * 80)
            for record in overdue:
                print(f"{record[0]:<25}{record[1][:29]:<30}{record[2]:<12}{int(record[3])} ngày")
        else:
            print("✅ Không có sách nào quá hạn!")
    
    def generate_report(self):
        # Tổng số sách
        total_books = self.db.execute_query("SELECT COUNT(*) FROM books")[0][0]
        
        # Tổng số thành viên
        total_members = self.db.execute_query("SELECT COUNT(*) FROM members")[0][0]
        
        # Sách đang được mượn
        books_borrowed = self.db.execute_query('''
            SELECT COUNT(*) FROM transactions t1
            WHERE t1.transaction_type = 'borrow'
            AND t1.transaction_id NOT IN (
                SELECT t2.transaction_id FROM transactions t2
                JOIN transactions t3 ON t2.member_id = t3.member_id AND t2.book_id = t3.book_id
                WHERE t2.transaction_type = 'borrow' AND t3.transaction_type = 'return'
                AND t3.transaction_date > t2.transaction_date
            )
        ''')[0][0]
        
        # Top 5 sách được mượn nhiều nhất
        popular_books = self.db.execute_query('''
            SELECT b.title, b.author, COUNT(*) as borrow_count
            FROM transactions t
            JOIN books b ON t.book_id = b.book_id
            WHERE t.transaction_type = 'borrow'
            GROUP BY t.book_id
            ORDER BY borrow_count DESC
            LIMIT 5
        ''')
        
        print(f"\n📊 BÁO CÁO THỐNG KÊ THƯ VIỆN")
        print("=" * 50)
        print(f"📚 Tổng số sách: {total_books}")
        print(f"👥 Tổng số thành viên: {total_members}")
        print(f"📖 Sách đang được mượn: {books_borrowed}")
        
        print(f"\n🏆 TOP 5 SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT:")
        if popular_books:
            for i, book in enumerate(popular_books, 1):
                print(f"{i}. {book[0]} - {book[1]} ({book[2]} lần)")
        else:
            print("Chưa có dữ liệu")
    
    def run(self):
        while True:
            print(f"\n🏛️ HỆ THỐNG QUẢN LÝ THƯ VIỆN")
            print("1. 📚 Thêm sách mới")
            print("2. 👤 Thêm thành viên mới")
            print("3. 🔍 Tìm kiếm sách")
            print("4. 📖 Mượn sách")
            print("5. 📚 Trả sách")
            print("6. ⚠️ Xem sách quá hạn")
            print("7. 📊 Báo cáo thống kê")
            print("8. 🚪 Thoát")
            
            choice = input("\nChọn chức năng (1-8): ")
            
            if choice == '1':
                title = input("Tên sách: ")
                author = input("Tác giả: ")
                isbn = input("ISBN: ")
                category = input("Thể loại: ")
                try:
                    year = int(input("Năm xuất bản: "))
                    copies = int(input("Số lượng (mặc định 1): ") or 1)
                    self.add_book(title, author, isbn, category, year, copies)
                except ValueError:
                    print("❌ Dữ liệu không hợp lệ!")
            
            elif choice == '2':
                name = input("Tên thành viên: ")
                email = input("Email: ")
                phone = input("Số điện thoại: ")
                address = input("Địa chỉ: ")
                self.add_member(name, email, phone, address)
            
            elif choice == '3':
                keyword = input("Từ khóa tìm kiếm (tên/tác giả/ISBN): ")
                category = input("Thể loại (tùy chọn): ")
                self.search_books(keyword, category)
            
            elif choice == '4':
                try:
                    member_id = int(input("ID thành viên: "))
                    book_id = int(input("ID sách: "))
                    self.borrow_book(member_id, book_id)
                except ValueError:
                    print("❌ ID phải là số!")
            
            elif choice == '5':
                try:
                    member_id = int(input("ID thành viên: "))
                    book_id = int(input("ID sách: "))
                    self.return_book(member_id, book_id)
                except ValueError:
                    print("❌ ID phải là số!")
            
            elif choice == '6':
                self.view_overdue_books()
            
            elif choice == '7':
                self.generate_report()
            
            elif choice == '8':
                print("👋 Tạm biệt!")
                break
            
            else:
                print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    library = LibraryManagement()
    library.run()
