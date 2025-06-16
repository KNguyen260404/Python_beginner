"""
Bài 5: Hệ thống thư viện
Chủ đề: Mối quan hệ phức tạp và Composition

Mục tiêu: Học cách thiết kế hệ thống với nhiều lớp có mối quan hệ phức tạp
"""

from datetime import datetime, timedelta
from enum import Enum

class BookStatus(Enum):
    """Trạng thái sách"""
    AVAILABLE = "Có sẵn"
    BORROWED = "Đã mượn"
    RESERVED = "Đã đặt trước"
    MAINTENANCE = "Bảo trì"
    LOST = "Mất"

class MemberType(Enum):
    """Loại thành viên"""
    STUDENT = "Học sinh"
    TEACHER = "Giáo viên"
    STAFF = "Nhân viên"
    GUEST = "Khách"

class Book:
    """Lớp sách"""
    
    def __init__(self, isbn, title, author, publisher, year, category, copies=1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publisher = publisher
        self.year = year
        self.category = category
        self.total_copies = copies
        self.available_copies = copies
        self.status = BookStatus.AVAILABLE
        self.reservation_queue = []  # Hàng đợi đặt trước
        self.borrow_history = []     # Lịch sử mượn
    
    def __str__(self):
        return f"'{self.title}' - {self.author} ({self.year})"
    
    def is_available(self):
        """Kiểm tra sách có sẵn không"""
        return self.available_copies > 0 and self.status == BookStatus.AVAILABLE
    
    def reserve(self, member):
        """Đặt trước sách"""
        if member not in self.reservation_queue:
            self.reservation_queue.append(member)
            if not self.is_available():
                self.status = BookStatus.RESERVED
            return True
        return False
    
    def cancel_reservation(self, member):
        """Hủy đặt trước"""
        if member in self.reservation_queue:
            self.reservation_queue.remove(member)
            if not self.reservation_queue and self.available_copies > 0:
                self.status = BookStatus.AVAILABLE
            return True
        return False
    
    def borrow(self, member):
        """Mượn sách"""
        if self.is_available():
            self.available_copies -= 1
            if self.available_copies == 0:
                self.status = BookStatus.BORROWED
            
            # Xóa khỏi hàng đợi nếu có
            if member in self.reservation_queue:
                self.reservation_queue.remove(member)
            
            return True
        return False
    
    def return_book(self):
        """Trả sách"""
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            if self.reservation_queue:
                self.status = BookStatus.RESERVED
            else:
                self.status = BookStatus.AVAILABLE
            return True
        return False
    
    def get_info(self):
        """Thông tin chi tiết sách"""
        return {
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'publisher': self.publisher,
            'year': self.year,
            'category': self.category,
            'total_copies': self.total_copies,
            'available_copies': self.available_copies,
            'status': self.status.value,
            'reservations': len(self.reservation_queue)
        }

class Member:
    """Lớp thành viên thư viện"""
    
    def __init__(self, member_id, name, email, phone, member_type, address=""):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.member_type = member_type
        self.address = address
        self.join_date = datetime.now()
        self.borrowed_books = []     # Sách đang mượn
        self.borrow_history = []     # Lịch sử mượn
        self.reservations = []       # Sách đã đặt trước
        self.fines = 0              # Tiền phạt
        self.is_active = True
    
    def __str__(self):
        return f"{self.name} ({self.member_type.value}) - ID: {self.member_id}"
    
    def get_max_borrow_limit(self):
        """Giới hạn mượn sách theo loại thành viên"""
        limits = {
            MemberType.STUDENT: 3,
            MemberType.TEACHER: 10,
            MemberType.STAFF: 5,
            MemberType.GUEST: 1
        }
        return limits.get(self.member_type, 1)
    
    def get_max_borrow_days(self):
        """Số ngày mượn tối đa"""
        days = {
            MemberType.STUDENT: 14,
            MemberType.TEACHER: 30,
            MemberType.STAFF: 21,
            MemberType.GUEST: 7
        }
        return days.get(self.member_type, 7)
    
    def can_borrow(self):
        """Kiểm tra có thể mượn sách không"""
        return (self.is_active and 
                len(self.borrowed_books) < self.get_max_borrow_limit() and
                self.fines < 100000)  # Không quá 100k tiền phạt
    
    def add_fine(self, amount, reason):
        """Thêm tiền phạt"""
        self.fines += amount
        print(f"💰 Đã thêm {amount:,.0f} VNĐ tiền phạt cho {self.name}: {reason}")
    
    def pay_fine(self, amount):
        """Thanh toán tiền phạt"""
        if amount <= self.fines:
            self.fines -= amount
            print(f"💳 {self.name} đã thanh toán {amount:,.0f} VNĐ tiền phạt")
            return True
        return False
    
    def get_info(self):
        """Thông tin thành viên"""
        return {
            'member_id': self.member_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'member_type': self.member_type.value,
            'join_date': self.join_date.strftime("%Y-%m-%d"),
            'borrowed_books': len(self.borrowed_books),
            'reservations': len(self.reservations),
            'fines': self.fines,
            'is_active': self.is_active
        }

class BorrowRecord:
    """Bản ghi mượn sách"""
    
    def __init__(self, book, member, librarian):
        self.book = book
        self.member = member
        self.librarian = librarian
        self.borrow_date = datetime.now()
        self.due_date = self.borrow_date + timedelta(days=member.get_max_borrow_days())
        self.return_date = None
        self.fine_amount = 0
        self.is_returned = False
    
    def calculate_fine(self):
        """Tính tiền phạt trả trễ"""
        if self.is_returned or datetime.now() <= self.due_date:
            return 0
        
        overdue_days = (datetime.now() - self.due_date).days
        fine_per_day = 2000  # 2000 VNĐ/ngày
        return overdue_days * fine_per_day
    
    def return_book(self, librarian):
        """Trả sách"""
        if not self.is_returned:
            self.return_date = datetime.now()
            self.is_returned = True
            self.fine_amount = self.calculate_fine()
            
            # Xóa khỏi danh sách mượn của thành viên
            if self in self.member.borrowed_books:
                self.member.borrowed_books.remove(self)
            
            # Thêm vào lịch sử
            self.member.borrow_history.append(self)
            
            # Trả sách
            self.book.return_book()
            
            # Thêm tiền phạt nếu có
            if self.fine_amount > 0:
                self.member.add_fine(self.fine_amount, f"Trả trễ sách '{self.book.title}'")
            
            return True
        return False
    
    def get_info(self):
        """Thông tin bản ghi mượn"""
        return {
            'book_title': self.book.title,
            'member_name': self.member.name,
            'borrow_date': self.borrow_date.strftime("%Y-%m-%d %H:%M"),
            'due_date': self.due_date.strftime("%Y-%m-%d"),
            'return_date': self.return_date.strftime("%Y-%m-%d %H:%M") if self.return_date else None,
            'fine_amount': self.fine_amount,
            'is_returned': self.is_returned,
            'days_overdue': max(0, (datetime.now() - self.due_date).days) if not self.is_returned else 0
        }

class Librarian:
    """Lớp thủ thư"""
    
    def __init__(self, employee_id, name, email, phone):
        self.employee_id = employee_id
        self.name = name
        self.email = email
        self.phone = phone
        self.work_start_date = datetime.now()
        self.books_processed = 0
        self.members_served = set()
    
    def __str__(self):
        return f"Thủ thư {self.name} (ID: {self.employee_id})"

class Library:
    """Lớp thư viện chính"""
    
    def __init__(self, name, address, phone):
        self.name = name
        self.address = address
        self.phone = phone
        self.books = {}          # ISBN -> Book
        self.members = {}        # member_id -> Member
        self.librarians = {}     # employee_id -> Librarian
        self.borrow_records = [] # Tất cả bản ghi mượn
        self.categories = set()  # Danh mục sách
    
    # Quản lý sách
    def add_book(self, book):
        """Thêm sách vào thư viện"""
        if book.isbn in self.books:
            # Nếu sách đã có, tăng số lượng
            existing_book = self.books[book.isbn]
            existing_book.total_copies += book.total_copies
            existing_book.available_copies += book.available_copies
            print(f"📚 Đã thêm {book.total_copies} bản sao của '{book.title}'")
        else:
            self.books[book.isbn] = book
            self.categories.add(book.category)
            print(f"📚 Đã thêm sách mới: {book}")
    
    def remove_book(self, isbn):
        """Xóa sách khỏi thư viện"""
        if isbn in self.books:
            book = self.books[isbn]
            if book.available_copies == book.total_copies:
                del self.books[isbn]
                print(f"🗑️ Đã xóa sách: {book}")
                return True
            else:
                print(f"❌ Không thể xóa sách '{book.title}' vì đang có người mượn!")
                return False
        else:
            print("❌ Không tìm thấy sách!")
            return False
    
    def search_books(self, keyword="", category="", author=""):
        """Tìm kiếm sách"""
        results = []
        keyword = keyword.lower()
        
        for book in self.books.values():
            match = True
            
            if keyword and keyword not in book.title.lower():
                match = False
            
            if category and category.lower() != book.category.lower():
                match = False
            
            if author and author.lower() not in book.author.lower():
                match = False
            
            if match:
                results.append(book)
        
        return results
    
    # Quản lý thành viên
    def add_member(self, member):
        """Thêm thành viên"""
        if member.member_id not in self.members:
            self.members[member.member_id] = member
            print(f"👤 Đã thêm thành viên: {member}")
            return True
        else:
            print(f"❌ Thành viên với ID {member.member_id} đã tồn tại!")
            return False
    
    def get_member(self, member_id):
        """Lấy thông tin thành viên"""
        return self.members.get(member_id)
    
    # Quản lý thủ thư  
    def add_librarian(self, librarian):
        """Thêm thủ thư"""
        if librarian.employee_id not in self.librarians:
            self.librarians[librarian.employee_id] = librarian
            print(f"👨‍💼 Đã thêm thủ thư: {librarian}")
            return True
        else:
            print(f"❌ Thủ thư với ID {librarian.employee_id} đã tồn tại!")
            return False
    
    # Mượn và trả sách
    def borrow_book(self, isbn, member_id, librarian_id):
        """Mượn sách"""
        book = self.books.get(isbn)
        member = self.members.get(member_id)
        librarian = self.librarians.get(librarian_id)
        
        if not book:
            print("❌ Không tìm thấy sách!")
            return False
        
        if not member:
            print("❌ Không tìm thấy thành viên!")
            return False
        
        if not librarian:
            print("❌ Không tìm thấy thủ thư!")
            return False
        
        if not member.can_borrow():
            print(f"❌ {member.name} không thể mượn sách (đã đạt giới hạn hoặc có tiền phạt)!")
            return False
        
        if not book.is_available():
            print(f"❌ Sách '{book.title}' không có sẵn!")
            # Đề xuất đặt trước
            if book.reserve(member):
                member.reservations.append(book)
                print(f"📋 Đã đặt trước sách cho {member.name}")
            return False
        
        # Thực hiện mượn sách
        if book.borrow(member):
            record = BorrowRecord(book, member, librarian)
            self.borrow_records.append(record)
            member.borrowed_books.append(record)
            
            librarian.books_processed += 1
            librarian.members_served.add(member_id)
            
            print(f"✅ {member.name} đã mượn '{book.title}' - Hạn trả: {record.due_date.strftime('%Y-%m-%d')}")
            return True
        
        return False
    
    def return_book(self, isbn, member_id, librarian_id):
        """Trả sách"""
        member = self.members.get(member_id)
        librarian = self.librarians.get(librarian_id)
        
        if not member or not librarian:
            print("❌ Không tìm thấy thành viên hoặc thủ thư!")
            return False
        
        # Tìm bản ghi mượn
        for record in member.borrowed_books:
            if record.book.isbn == isbn and not record.is_returned:
                if record.return_book(librarian):
                    librarian.books_processed += 1
                    print(f"✅ {member.name} đã trả '{record.book.title}'")
                    
                    # Thông báo cho người đặt trước tiếp theo
                    if record.book.reservation_queue:
                        next_member = record.book.reservation_queue[0]
                        print(f"📢 Thông báo {next_member.name}: Sách '{record.book.title}' đã có sẵn!")
                    
                    return True
        
        print(f"❌ Không tìm thấy bản ghi mượn sách với ISBN {isbn}!")
        return False
    
    # Báo cáo và thống kê
    def get_overdue_books(self):
        """Lấy danh sách sách quá hạn"""
        overdue_records = []
        for record in self.borrow_records:
            if not record.is_returned and datetime.now() > record.due_date:
                overdue_records.append(record)
        return overdue_records
    
    def get_popular_books(self, limit=10):
        """Sách được mượn nhiều nhất"""
        book_borrow_count = {}
        
        for record in self.borrow_records:
            isbn = record.book.isbn
            book_borrow_count[isbn] = book_borrow_count.get(isbn, 0) + 1
        
        # Sắp xếp theo số lần mượn
        sorted_books = sorted(book_borrow_count.items(), key=lambda x: x[1], reverse=True)
        
        popular_books = []
        for isbn, count in sorted_books[:limit]:
            book = self.books[isbn]
            popular_books.append((book, count))
        
        return popular_books
    
    def generate_member_report(self, member_id):
        """Báo cáo chi tiết thành viên"""
        member = self.members.get(member_id)
        if not member:
            print("❌ Không tìm thấy thành viên!")
            return
        
        print(f"\n📋 BÁO CÁO THÀNH VIÊN: {member.name}")
        print("=" * 50)
        
        info = member.get_info()
        for key, value in info.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Sách đang mượn
        if member.borrowed_books:
            print(f"\n📚 SÁCH ĐANG MƯỢN ({len(member.borrowed_books)}):")
            for record in member.borrowed_books:
                days_left = (record.due_date - datetime.now()).days
                status_emoji = "⚠️" if days_left < 0 else "✅"
                print(f"   {status_emoji} {record.book.title} - Hạn trả: {record.due_date.strftime('%Y-%m-%d')}")
        
        # Sách đã đặt trước
        if member.reservations:
            print(f"\n📋 SÁCH ĐÃ ĐẶT TRƯỚC ({len(member.reservations)}):")
            for book in member.reservations:
                print(f"   📖 {book.title}")
    
    def generate_library_report(self):
        """Báo cáo tổng quan thư viện"""
        print(f"\n📊 BÁO CÁO TỔNG QUAN THƯ VIỆN: {self.name}")
        print("=" * 60)
        
        total_books = sum(book.total_copies for book in self.books.values())
        available_books = sum(book.available_copies for book in self.books.values())
        borrowed_books = total_books - available_books
        
        print(f"📚 Tổng số sách: {len(self.books)} đầu sách ({total_books} bản)")
        print(f"📖 Sách có sẵn: {available_books} bản")
        print(f"📋 Sách đang mượn: {borrowed_books} bản")
        print(f"👥 Tổng số thành viên: {len(self.members)}")
        print(f"👨‍💼 Tổng số thủ thư: {len(self.librarians)}")
        print(f"📑 Tổng số giao dịch mượn: {len(self.borrow_records)}")
        
        # Thống kê theo danh mục
        category_stats = {}
        for book in self.books.values():
            category_stats[book.category] = category_stats.get(book.category, 0) + book.total_copies
        
        print(f"\n📂 THỐNG KÊ THEO DANH MỤC:")
        for category, count in sorted(category_stats.items()):
            print(f"   {category}: {count} bản")
        
        # Sách quá hạn
        overdue = self.get_overdue_books()
        if overdue:
            print(f"\n⚠️ SÁCH QUÁ HẠN ({len(overdue)}):")
            for record in overdue[:5]:  # Chỉ hiển thị 5 bản ghi đầu
                days_overdue = (datetime.now() - record.due_date).days
                print(f"   📚 {record.book.title} - {record.member.name} ({days_overdue} ngày)")
        
        # Sách phổ biến
        popular = self.get_popular_books(5)
        if popular:
            print(f"\n🏆 TOP 5 SÁCH PHỔ BIẾN NHẤT:")
            for i, (book, count) in enumerate(popular, 1):
                print(f"   {i}. {book.title} - Mượn {count} lần")

# Demo chương trình
def main():
    print("📚 HỆ THỐNG QUẢN LÝ THƯ VIỆN 📚")
    
    # Tạo thư viện
    library = Library("Thư viện Trung tâm", "123 Đường ABC, TP.HCM", "028-1234-5678")
    
    # Thêm thủ thư
    librarian1 = Librarian("LIB001", "Nguyễn Thị Lan", "lan@library.com", "0901234567")
    librarian2 = Librarian("LIB002", "Trần Văn Nam", "nam@library.com", "0902234567")
    library.add_librarian(librarian1)
    library.add_librarian(librarian2)
    
    # Thêm sách
    books_data = [
        ("978-0134685991", "Effective Java", "Joshua Bloch", "Addison-Wesley", 2017, "Lập trình", 3),
        ("978-0596009205", "Head First Design Patterns", "Eric Freeman", "O'Reilly", 2004, "Lập trình", 2),
        ("978-0135957059", "The Pragmatic Programmer", "David Thomas", "Addison-Wesley", 2019, "Lập trình", 4),
        ("978-0134757599", "Refactoring", "Martin Fowler", "Addison-Wesley", 2018, "Lập trình", 2),
        ("978-8934974429", "Đắc Nhân Tâm", "Dale Carnegie", "NXB Tổng hợp TP.HCM", 2016, "Tâm lý", 5),
        ("978-8935235342", "Nhà Giả Kim", "Paulo Coelho", "NXB Hội Nhà văn", 2020, "Tiểu thuyết", 3),
        ("978-8935086357", "Sapiens", "Yuval Noah Harari", "NXB Thế giới", 2018, "Lịch sử", 4),
    ]
    
    for isbn, title, author, publisher, year, category, copies in books_data:
        book = Book(isbn, title, author, publisher, year, category, copies)
        library.add_book(book)
    
    # Thêm thành viên
    members_data = [
        ("MEM001", "Nguyễn Văn An", "an@email.com", "0911111111", MemberType.STUDENT),
        ("MEM002", "Trần Thị Bình", "binh@email.com", "0922222222", MemberType.TEACHER),
        ("MEM003", "Lê Văn Cường", "cuong@email.com", "0933333333", MemberType.STUDENT),
        ("MEM004", "Phạm Thị Dung", "dung@email.com", "0944444444", MemberType.STAFF),
        ("MEM005", "Hoàng Văn Em", "em@email.com", "0955555555", MemberType.GUEST),
    ]
    
    for member_id, name, email, phone, member_type in members_data:
        member = Member(member_id, name, email, phone, member_type)
        library.add_member(member)
    
    print(f"\n🔍 TÌM KIẾM SÁCH:")
    print("=" * 30)
    
    # Tìm kiếm sách
    programming_books = library.search_books(category="Lập trình")
    print(f"Sách lập trình ({len(programming_books)}):")
    for book in programming_books:
        print(f"   📚 {book}")
    
    print(f"\n📋 THỰC HIỆN MƯỢN SÁCH:")
    print("=" * 40)
    
    # Mượn sách
    borrow_requests = [
        ("978-0134685991", "MEM001", "LIB001"),  # An mượn Effective Java
        ("978-8934974429", "MEM002", "LIB001"),  # Bình mượn Đắc Nhân Tâm
        ("978-0596009205", "MEM001", "LIB002"),  # An mượn thêm Design Patterns
        ("978-8935235342", "MEM003", "LIB001"),  # Cường mượn Nhà Giả Kim
        ("978-0134685991", "MEM004", "LIB002"),  # Dung mượn Effective Java
        ("978-0134685991", "MEM005", "LIB001"),  # Em mượn Effective Java (sẽ đặt trước)
    ]
    
    for isbn, member_id, librarian_id in borrow_requests:
        library.borrow_book(isbn, member_id, librarian_id)
    
    print(f"\n📊 THÔNG TIN THÀNH VIÊN:")
    print("=" * 40)
    
    # Hiển thị thông tin thành viên
    for member_id in ["MEM001", "MEM002", "MEM005"]:
        library.generate_member_report(member_id)
    
    print(f"\n📥 TRẢ SÁCH:")
    print("=" * 20)
    
    # Trả sách
    library.return_book("978-8934974429", "MEM002", "LIB001")  # Bình trả Đắc Nhân Tâm
    
    # Mô phỏng trả trễ
    member_an = library.get_member("MEM001")
    if member_an and member_an.borrowed_books:
        # Giả lập trả trễ
        record = member_an.borrowed_books[0]
        record.due_date = datetime.now() - timedelta(days=5)  # Quá hạn 5 ngày
        library.return_book(record.book.isbn, "MEM001", "LIB002")
    
    print(f"\n💳 THANH TOÁN TIỀN PHẠT:")
    print("=" * 35)
    
    # Thanh toán tiền phạt
    if member_an.fines > 0:
        member_an.pay_fine(member_an.fines)
    
    # Báo cáo tổng quan
    library.generate_library_report()
    
    # Hiển thị sách quá hạn
    overdue_books = library.get_overdue_books()
    if overdue_books:
        print(f"\n⚠️ CHI TIẾT SÁCH QUÁ HẠN:")
        print("=" * 40)
        for record in overdue_books:
            info = record.get_info()
            print(f"📚 {info['book_title']}")
            print(f"   Người mượn: {info['member_name']}")
            print(f"   Ngày mượn: {info['borrow_date']}")
            print(f"   Hạn trả: {info['due_date']}")
            print(f"   Quá hạn: {info['days_overdue']} ngày")
            print(f"   Tiền phạt: {record.calculate_fine():,.0f} VNĐ")

if __name__ == "__main__":
    main()
