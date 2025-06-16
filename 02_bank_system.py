"""
Bài 2: Hệ thống ngân hàng
Chủ đề: Đóng gói (Encapsulation) và bảo vệ dữ liệu

Mục tiêu: Học cách sử dụng thuộc tính private, property, và getter/setter
"""

class BankAccount:
    def __init__(self, account_number, owner_name, initial_balance=0):
        """Khởi tạo tài khoản ngân hàng"""
        self.account_number = account_number
        self.owner_name = owner_name
        self.__balance = initial_balance  # Private attribute
        self.__transaction_history = []  # Private attribute
        self.__is_active = True
        
        # Ghi lại giao dịch đầu tiên
        if initial_balance > 0:
            self.__transaction_history.append({
                'type': 'Mở tài khoản',
                'amount': initial_balance,
                'balance': self.__balance,
                'timestamp': self.__get_current_time()
            })
    
    @property
    def balance(self):
        """Getter cho số dư (chỉ đọc)"""
        return self.__balance
    
    @property
    def is_active(self):
        """Kiểm tra tài khoản có hoạt động không"""
        return self.__is_active
    
    def __get_current_time(self):
        """Private method để lấy thời gian hiện tại"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def deposit(self, amount):
        """Gửi tiền vào tài khoản"""
        if not self.__is_active:
            print("❌ Tài khoản đã bị khóa!")
            return False
        
        if amount <= 0:
            print("❌ Số tiền gửi phải lớn hơn 0!")
            return False
        
        self.__balance += amount
        self.__transaction_history.append({
            'type': 'Gửi tiền',
            'amount': amount,
            'balance': self.__balance,
            'timestamp': self.__get_current_time()
        })
        print(f"✅ Đã gửi {amount:,.0f} VNĐ. Số dư hiện tại: {self.__balance:,.0f} VNĐ")
        return True
    
    def withdraw(self, amount):
        """Rút tiền từ tài khoản"""
        if not self.__is_active:
            print("❌ Tài khoản đã bị khóa!")
            return False
        
        if amount <= 0:
            print("❌ Số tiền rút phải lớn hơn 0!")
            return False
        
        if amount > self.__balance:
            print(f"❌ Không đủ số dư! Số dư hiện tại: {self.__balance:,.0f} VNĐ")
            return False
        
        self.__balance -= amount
        self.__transaction_history.append({
            'type': 'Rút tiền',
            'amount': -amount,
            'balance': self.__balance,
            'timestamp': self.__get_current_time()
        })
        print(f"✅ Đã rút {amount:,.0f} VNĐ. Số dư hiện tại: {self.__balance:,.0f} VNĐ")
        return True
    
    def transfer(self, target_account, amount):
        """Chuyển tiền đến tài khoản khác"""
        if not self.__is_active:
            print("❌ Tài khoản đã bị khóa!")
            return False
        
        if amount <= 0:
            print("❌ Số tiền chuyển phải lớn hơn 0!")
            return False
        
        if amount > self.__balance:
            print(f"❌ Không đủ số dư! Số dư hiện tại: {self.__balance:,.0f} VNĐ")
            return False
        
        if not target_account.is_active:
            print("❌ Tài khoản đích đã bị khóa!")
            return False
        
        # Thực hiện chuyển tiền
        self.__balance -= amount
        target_account.__balance += amount
        
        # Ghi lại giao dịch cho tài khoản gửi
        self.__transaction_history.append({
            'type': f'Chuyển tiền đến {target_account.account_number}',
            'amount': -amount,
            'balance': self.__balance,
            'timestamp': self.__get_current_time()
        })
        
        # Ghi lại giao dịch cho tài khoản nhận
        target_account.__transaction_history.append({
            'type': f'Nhận tiền từ {self.account_number}',
            'amount': amount,
            'balance': target_account.__balance,
            'timestamp': self.__get_current_time()
        })
        
        print(f"✅ Đã chuyển {amount:,.0f} VNĐ đến {target_account.owner_name}")
        print(f"   Số dư hiện tại: {self.__balance:,.0f} VNĐ")
        return True
    
    def get_transaction_history(self, limit=10):
        """Lấy lịch sử giao dịch"""
        if not self.__transaction_history:
            print("Chưa có giao dịch nào!")
            return
        
        print(f"\n📋 LỊCH SỬ GIAO DỊCH - {self.owner_name}")
        print("=" * 70)
        recent_transactions = self.__transaction_history[-limit:]
        
        for transaction in reversed(recent_transactions):
            amount_str = f"{transaction['amount']:+,.0f} VNĐ"
            print(f"{transaction['timestamp']} | {transaction['type']:<25} | {amount_str:>15} | Số dư: {transaction['balance']:,.0f} VNĐ")
    
    def lock_account(self):
        """Khóa tài khoản"""
        self.__is_active = False
        print(f"🔒 Tài khoản {self.account_number} đã bị khóa!")
    
    def unlock_account(self):
        """Mở khóa tài khoản"""
        self.__is_active = True
        print(f"🔓 Tài khoản {self.account_number} đã được mở khóa!")
    
    def get_account_info(self):
        """Hiển thị thông tin tài khoản"""
        status = "🟢 Hoạt động" if self.__is_active else "🔴 Bị khóa"
        print(f"\n💳 THÔNG TIN TÀI KHOẢN")
        print("=" * 40)
        print(f"Số tài khoản: {self.account_number}")
        print(f"Chủ tài khoản: {self.owner_name}")
        print(f"Số dư: {self.__balance:,.0f} VNĐ")
        print(f"Trạng thái: {status}")
        print(f"Số giao dịch: {len(self.__transaction_history)}")

class SavingsAccount(BankAccount):
    """Tài khoản tiết kiệm - kế thừa từ BankAccount"""
    
    def __init__(self, account_number, owner_name, initial_balance=0, interest_rate=0.05):
        super().__init__(account_number, owner_name, initial_balance)
        self.interest_rate = interest_rate  # Lãi suất hàng năm
        self.account_type = "Tiết kiệm"
    
    def calculate_interest(self, months):
        """Tính lãi suất theo tháng"""
        monthly_rate = self.interest_rate / 12
        interest = self.balance * monthly_rate * months
        return interest
    
    def add_interest(self, months):
        """Thêm lãi vào tài khoản"""
        interest = self.calculate_interest(months)
        self.deposit(interest)
        print(f"💰 Đã cộng lãi {months} tháng: {interest:,.0f} VNĐ")

# Demo chương trình
def main():
    print("🏦 HỆ THỐNG NGÂN HÀNG 🏦")
    
    # Tạo tài khoản
    account1 = BankAccount("TK001", "Nguyễn Văn An", 1000000)
    account2 = BankAccount("TK002", "Trần Thị Bình", 500000)
    savings_account = SavingsAccount("TK003", "Lê Văn Cường", 2000000, 0.06)
    
    # Hiển thị thông tin tài khoản
    account1.get_account_info()
    account2.get_account_info()
    savings_account.get_account_info()
    
    print("\n" + "="*50)
    print("THỰC HIỆN CÁC GIAO DỊCH")
    print("="*50)
    
    # Gửi tiền
    account1.deposit(500000)
    
    # Rút tiền
    account1.withdraw(200000)
    
    # Chuyển tiền
    account1.transfer(account2, 300000)
    
    # Thử rút quá số dư
    account2.withdraw(2000000)
    
    # Tính lãi cho tài khoản tiết kiệm
    print(f"\nLãi 6 tháng: {savings_account.calculate_interest(6):,.0f} VNĐ")
    savings_account.add_interest(6)
    
    # Hiển thị lịch sử giao dịch
    account1.get_transaction_history()
    account2.get_transaction_history()
    savings_account.get_transaction_history()
    
    # Khóa tài khoản và thử giao dịch
    print(f"\n🔒 KHÓA TÀI KHOẢN")
    account1.lock_account()
    account1.withdraw(100000)  # Sẽ bị từ chối
    
    # Mở khóa tài khoản
    account1.unlock_account()
    account1.withdraw(100000)  # Sẽ thành công

if __name__ == "__main__":
    main()
