"""
Bài 6: Hệ thống E-commerce với Design Patterns
Chủ đề: Singleton, Factory, Observer, Strategy Patterns

Mục tiêu: Học các mẫu thiết kế phổ biến và cách áp dụng vào hệ thống thực tế
"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Protocol
import threading
import json
import hashlib

class OrderStatus(Enum):
    PENDING = "Đang chờ"
    CONFIRMED = "Đã xác nhận"
    PROCESSING = "Đang xử lý"
    SHIPPED = "Đang giao"
    DELIVERED = "Đã giao"
    CANCELLED = "Đã hủy"
    RETURNED = "Đã trả"

class PaymentMethod(Enum):
    CREDIT_CARD = "Thẻ tín dụng"
    DEBIT_CARD = "Thẻ ghi nợ"
    BANK_TRANSFER = "Chuyển khoản"
    E_WALLET = "Ví điện tử"
    CASH_ON_DELIVERY = "Thanh toán khi nhận hàng"

# SINGLETON PATTERN - Database Connection
class DatabaseConnection:
    """Singleton pattern cho kết nối database"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.connection_string = "mongodb://localhost:27017/ecommerce"
            self.connected = False
            self.query_count = 0
            self._initialized = True
            print("🔗 Database connection initialized")
    
    def connect(self):
        if not self.connected:
            self.connected = True
            print(f"📡 Connected to database: {self.connection_string}")
    
    def execute_query(self, query: str) -> Dict:
        self.query_count += 1
        print(f"🔍 Executing query #{self.query_count}: {query[:50]}...")
        # Simulate database operation
        return {"status": "success", "query_id": self.query_count}
    
    def get_stats(self):
        return {
            "connected": self.connected,
            "total_queries": self.query_count,
            "connection_string": self.connection_string
        }

# STRATEGY PATTERN - Payment Processing
class PaymentStrategy(ABC):
    """Abstract strategy for payment processing"""
    
    @abstractmethod
    def process_payment(self, amount: float, details: Dict) -> Dict:
        pass
    
    @abstractmethod
    def validate_payment_details(self, details: Dict) -> bool:
        pass

class CreditCardPayment(PaymentStrategy):
    def process_payment(self, amount: float, details: Dict) -> Dict:
        if not self.validate_payment_details(details):
            return {"success": False, "error": "Invalid credit card details"}
        
        # Simulate payment processing
        transaction_id = hashlib.md5(f"{details['card_number']}{amount}{datetime.now()}".encode()).hexdigest()[:8]
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "Credit Card",
            "last_4_digits": details['card_number'][-4:],
            "processed_at": datetime.now().isoformat()
        }
    
    def validate_payment_details(self, details: Dict) -> bool:
        required_fields = ['card_number', 'expiry_date', 'cvv', 'holder_name']
        return all(field in details for field in required_fields)

class BankTransferPayment(PaymentStrategy):
    def process_payment(self, amount: float, details: Dict) -> Dict:
        if not self.validate_payment_details(details):
            return {"success": False, "error": "Invalid bank transfer details"}
        
        transaction_id = f"BT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "Bank Transfer",
            "bank_account": details['account_number'][-4:],
            "processed_at": datetime.now().isoformat()
        }
    
    def validate_payment_details(self, details: Dict) -> bool:
        required_fields = ['account_number', 'bank_name', 'account_holder']
        return all(field in details for field in required_fields)

class EWalletPayment(PaymentStrategy):
    def process_payment(self, amount: float, details: Dict) -> Dict:
        if not self.validate_payment_details(details):
            return {"success": False, "error": "Invalid e-wallet details"}
        
        transaction_id = f"EW{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "amount": amount,
            "method": "E-Wallet",
            "wallet_id": details['wallet_id'],
            "processed_at": datetime.now().isoformat()
        }
    
    def validate_payment_details(self, details: Dict) -> bool:
        required_fields = ['wallet_id', 'pin']
        return all(field in details for field in required_fields)

# FACTORY PATTERN - Payment Factory
class PaymentFactory:
    """Factory pattern for creating payment strategies"""
    
    @staticmethod
    def create_payment_strategy(payment_method: PaymentMethod) -> PaymentStrategy:
        strategies = {
            PaymentMethod.CREDIT_CARD: CreditCardPayment,
            PaymentMethod.DEBIT_CARD: CreditCardPayment,  # Same as credit card
            PaymentMethod.BANK_TRANSFER: BankTransferPayment,
            PaymentMethod.E_WALLET: EWalletPayment,
        }
        
        strategy_class = strategies.get(payment_method)
        if strategy_class:
            return strategy_class()
        else:
            raise ValueError(f"Unsupported payment method: {payment_method}")

# OBSERVER PATTERN - Order Status Notifications
class Observer(ABC):
    """Abstract observer for order status changes"""
    
    @abstractmethod
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        pass

class EmailNotifier(Observer):
    def __init__(self, email_service):
        self.email_service = email_service
    
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        print(f"📧 Email sent: Order {order_id} status changed from {old_status.value} to {new_status.value}")
        self.email_service.send_email(
            subject=f"Order {order_id} Update",
            message=f"Your order status has been updated to: {new_status.value}"
        )

class SMSNotifier(Observer):
    def __init__(self, sms_service):
        self.sms_service = sms_service
    
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        print(f"📱 SMS sent: Order {order_id} is now {new_status.value}")
        self.sms_service.send_sms(f"Order {order_id}: {new_status.value}")

class PushNotifier(Observer):
    def __init__(self, push_service):
        self.push_service = push_service
    
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        print(f"🔔 Push notification: Order {order_id} - {new_status.value}")
        self.push_service.send_push_notification(
            title="Order Update",
            message=f"Order {order_id} is now {new_status.value}"
        )

class InventoryUpdater(Observer):
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service
    
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        if new_status == OrderStatus.CONFIRMED:
            print(f"📦 Inventory updated for order {order_id}")
            self.inventory_service.reserve_items(order_id)
        elif new_status == OrderStatus.CANCELLED:
            print(f"🔄 Inventory restored for cancelled order {order_id}")
            self.inventory_service.restore_items(order_id)

# Core Business Objects
class Product:
    def __init__(self, product_id: str, name: str, price: float, category: str, 
                 stock_quantity: int, description: str = ""):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock_quantity = stock_quantity
        self.description = description
        self.reviews = []
        self.rating = 0.0
        self.created_at = datetime.now()
    
    def add_review(self, rating: int, comment: str, customer_name: str):
        review = {
            "rating": rating,
            "comment": comment,
            "customer_name": customer_name,
            "date": datetime.now().isoformat()
        }
        self.reviews.append(review)
        self.update_rating()
    
    def update_rating(self):
        if self.reviews:
            total_rating = sum(review["rating"] for review in self.reviews)
            self.rating = round(total_rating / len(self.reviews), 1)
    
    def is_available(self, quantity: int = 1) -> bool:
        return self.stock_quantity >= quantity
    
    def reduce_stock(self, quantity: int):
        if self.is_available(quantity):
            self.stock_quantity -= quantity
            return True
        return False
    
    def restore_stock(self, quantity: int):
        self.stock_quantity += quantity
    
    def get_info(self) -> Dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "category": self.category,
            "stock_quantity": self.stock_quantity,
            "rating": self.rating,
            "review_count": len(self.reviews)
        }

class Customer:
    def __init__(self, customer_id: str, name: str, email: str, phone: str, address: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone
        self.address = address
        self.orders = []
        self.loyalty_points = 0
        self.preferred_payment_method = None
        self.created_at = datetime.now()
    
    def add_loyalty_points(self, points: int):
        self.loyalty_points += points
        print(f"🎁 {self.name} earned {points} loyalty points! Total: {self.loyalty_points}")
    
    def redeem_loyalty_points(self, points: int) -> bool:
        if self.loyalty_points >= points:
            self.loyalty_points -= points
            return True
        return False
    
    def get_order_history(self) -> List[Dict]:
        return [order.get_summary() for order in self.orders]

class OrderItem:
    def __init__(self, product: Product, quantity: int, price_per_unit: float):
        self.product = product
        self.quantity = quantity
        self.price_per_unit = price_per_unit
        self.total_price = quantity * price_per_unit
    
    def get_info(self) -> Dict:
        return {
            "product_name": self.product.name,
            "product_id": self.product.product_id,
            "quantity": self.quantity,
            "price_per_unit": self.price_per_unit,
            "total_price": self.total_price
        }

class Order:
    def __init__(self, order_id: str, customer: Customer):
        self.order_id = order_id
        self.customer = customer
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING
        self.total_amount = 0.0
        self.discount_amount = 0.0
        self.tax_amount = 0.0
        self.shipping_fee = 0.0
        self.final_amount = 0.0
        self.payment_details = None
        self.shipping_address = customer.address
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.observers: List[Observer] = []
    
    def add_observer(self, observer: Observer):
        self.observers.append(observer)
    
    def remove_observer(self, observer: Observer):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, old_status: OrderStatus, new_status: OrderStatus):
        for observer in self.observers:
            observer.update(self.order_id, old_status, new_status)
    
    def add_item(self, product: Product, quantity: int):
        if not product.is_available(quantity):
            raise ValueError(f"Not enough stock for {product.name}")
        
        order_item = OrderItem(product, quantity, product.price)
        self.items.append(order_item)
        self.calculate_total()
        print(f"✅ Added {quantity}x {product.name} to order {self.order_id}")
    
    def remove_item(self, product_id: str):
        self.items = [item for item in self.items if item.product.product_id != product_id]
        self.calculate_total()
    
    def calculate_total(self):
        self.total_amount = sum(item.total_price for item in self.items)
        self.tax_amount = self.total_amount * 0.1  # 10% tax
        self.shipping_fee = 50000 if self.total_amount < 500000 else 0  # Free shipping over 500k
        self.final_amount = self.total_amount + self.tax_amount + self.shipping_fee - self.discount_amount
    
    def apply_discount(self, discount_amount: float, reason: str = ""):
        self.discount_amount = discount_amount
        self.calculate_total()
        print(f"💰 Applied discount of {discount_amount:,.0f} VNĐ to order {self.order_id}")
        if reason:
            print(f"   Reason: {reason}")
    
    def update_status(self, new_status: OrderStatus):
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now()
        
        print(f"📋 Order {self.order_id} status updated: {old_status.value} → {new_status.value}")
        self.notify_observers(old_status, new_status)
    
    def get_summary(self) -> Dict:
        return {
            "order_id": self.order_id,
            "customer_name": self.customer.name,
            "status": self.status.value,
            "total_items": len(self.items),
            "total_amount": self.total_amount,
            "final_amount": self.final_amount,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def get_detailed_info(self):
        print(f"\n📋 CHI TIẾT ĐỚN HÀNG {self.order_id}")
        print("=" * 60)
        print(f"Khách hàng: {self.customer.name}")
        print(f"Email: {self.customer.email}")
        print(f"Địa chỉ giao hàng: {self.shipping_address}")
        print(f"Trạng thái: {self.status.value}")
        print(f"Ngày tạo: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nSẢN PHẨM:")
        for item in self.items:
            print(f"  - {item.product.name} x{item.quantity} = {item.total_price:,.0f} VNĐ")
        
        print(f"\nTÓM TẮT THANH TOÁN:")
        print(f"  Tổng tiền hàng: {self.total_amount:,.0f} VNĐ")
        print(f"  Thuế (10%): {self.tax_amount:,.0f} VNĐ")
        print(f"  Phí vận chuyển: {self.shipping_fee:,.0f} VNĐ")
        print(f"  Giảm giá: -{self.discount_amount:,.0f} VNĐ")
        print(f"  TỔNG CỘNG: {self.final_amount:,.0f} VNĐ")

# Service Classes
class EmailService:
    def send_email(self, subject: str, message: str):
        # Simulate email sending
        pass

class SMSService:
    def send_sms(self, message: str):
        # Simulate SMS sending
        pass

class PushService:
    def send_push_notification(self, title: str, message: str):
        # Simulate push notification
        pass

class InventoryService:
    def __init__(self):
        self.reserved_items = {}
    
    def reserve_items(self, order_id: str):
        self.reserved_items[order_id] = datetime.now()
    
    def restore_items(self, order_id: str):
        if order_id in self.reserved_items:
            del self.reserved_items[order_id]

# Main E-commerce System
class ECommerceSystem:
    def __init__(self):
        self.db = DatabaseConnection()
        self.products = {}
        self.customers = {}
        self.orders = {}
        self.order_counter = 1
        
        # Services
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushService()
        self.inventory_service = InventoryService()
        
        # Observers
        self.email_notifier = EmailNotifier(self.email_service)
        self.sms_notifier = SMSNotifier(self.sms_service)
        self.push_notifier = PushNotifier(self.push_service)
        self.inventory_updater = InventoryUpdater(self.inventory_service)
    
    def add_product(self, product: Product):
        self.products[product.product_id] = product
        print(f"📦 Added product: {product.name}")
    
    def add_customer(self, customer: Customer):
        self.customers[customer.customer_id] = customer
        print(f"👤 Added customer: {customer.name}")
    
    def create_order(self, customer_id: str) -> Order:
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError("Customer not found")
        
        order_id = f"ORD{self.order_counter:06d}"
        self.order_counter += 1
        
        order = Order(order_id, customer)
        
        # Add observers to order
        order.add_observer(self.email_notifier)
        order.add_observer(self.sms_notifier)
        order.add_observer(self.push_notifier)
        order.add_observer(self.inventory_updater)
        
        self.orders[order_id] = order
        customer.orders.append(order)
        
        print(f"🛒 Created order {order_id} for {customer.name}")
        return order
    
    def process_payment(self, order_id: str, payment_method: PaymentMethod, payment_details: Dict) -> bool:
        order = self.orders.get(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Use Factory pattern to create payment strategy
        payment_strategy = PaymentFactory.create_payment_strategy(payment_method)
        
        # Process payment using Strategy pattern
        result = payment_strategy.process_payment(order.final_amount, payment_details)
        
        if result["success"]:
            order.payment_details = result
            order.update_status(OrderStatus.CONFIRMED)
            
            # Award loyalty points
            points = int(order.final_amount // 10000)  # 1 point per 10k VNĐ
            order.customer.add_loyalty_points(points)
            
            # Reserve inventory
            for item in order.items:
                item.product.reduce_stock(item.quantity)
            
            print(f"💳 Payment processed successfully for order {order_id}")
            return True
        else:
            print(f"❌ Payment failed for order {order_id}: {result.get('error', 'Unknown error')}")
            return False
    
    def get_order_analytics(self) -> Dict:
        total_orders = len(self.orders)
        total_revenue = sum(order.final_amount for order in self.orders.values() 
                          if order.status not in [OrderStatus.CANCELLED, OrderStatus.RETURNED])
        
        status_count = {}
        for order in self.orders.values():
            status = order.status.value
            status_count[status] = status_count.get(status, 0) + 1
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "status_breakdown": status_count,
            "database_stats": self.db.get_stats()
        }

def main():
    print("🛒 HỆ THỐNG E-COMMERCE VỚI DESIGN PATTERNS 🛒")
    
    # Initialize system
    ecommerce = ECommerceSystem()
    ecommerce.db.connect()
    
    # Add products
    products = [
        Product("P001", "iPhone 15 Pro", 25000000, "Electronics", 50, "Latest iPhone"),
        Product("P002", "Samsung Galaxy S24", 20000000, "Electronics", 30, "Samsung flagship"),
        Product("P003", "MacBook Air M3", 35000000, "Electronics", 20, "Apple laptop"),
        Product("P004", "AirPods Pro", 6000000, "Electronics", 100, "Wireless earbuds"),
        Product("P005", "Nike Air Max", 3000000, "Fashion", 80, "Running shoes"),
    ]
    
    for product in products:
        ecommerce.add_product(product)
    
    # Add customers
    customers = [
        Customer("C001", "Nguyễn Văn An", "an@email.com", "0901234567", "123 Lê Lợi, Q1, TP.HCM"),
        Customer("C002", "Trần Thị Bình", "binh@email.com", "0902234567", "456 Nguyễn Huệ, Q1, TP.HCM"),
        Customer("C003", "Lê Văn Cường", "cuong@email.com", "0903234567", "789 Đồng Khởi, Q1, TP.HCM"),
    ]
    
    for customer in customers:
        ecommerce.add_customer(customer)
    
    print(f"\n🛍️ TẠO ĐƠN HÀNG VÀ XỬ LÝ:")
    print("=" * 50)
    
    # Create orders
    try:
        # Order 1: Customer An buys iPhone and AirPods
        order1 = ecommerce.create_order("C001")
        order1.add_item(ecommerce.products["P001"], 1)  # iPhone
        order1.add_item(ecommerce.products["P004"], 2)  # AirPods x2
        
        # Apply loyalty discount
        if order1.customer.loyalty_points >= 50:
            order1.apply_discount(500000, "Loyalty discount")
        
        order1.get_detailed_info()
        
        # Process payment with credit card
        payment_details = {
            "card_number": "1234567890123456",
            "expiry_date": "12/26",
            "cvv": "123",
            "holder_name": "NGUYEN VAN AN"
        }
        
        success = ecommerce.process_payment(order1.order_id, PaymentMethod.CREDIT_CARD, payment_details)
        
        if success:
            # Simulate order processing
            order1.update_status(OrderStatus.PROCESSING)
            order1.update_status(OrderStatus.SHIPPED)
            order1.update_status(OrderStatus.DELIVERED)
        
        # Order 2: Customer Bình buys MacBook
        order2 = ecommerce.create_order("C002")
        order2.add_item(ecommerce.products["P003"], 1)  # MacBook
        
        # Process payment with bank transfer
        bank_details = {
            "account_number": "0123456789",
            "bank_name": "Vietcombank",
            "account_holder": "TRAN THI BINH"
        }
        
        success = ecommerce.process_payment(order2.order_id, PaymentMethod.BANK_TRANSFER, bank_details)
        
        # Order 3: Customer Cường buys shoes with e-wallet
        order3 = ecommerce.create_order("C003")
        order3.add_item(ecommerce.products["P005"], 2)  # Nike shoes x2
        
        ewallet_details = {
            "wallet_id": "momo_0903234567",
            "pin": "123456"
        }
        
        success = ecommerce.process_payment(order3.order_id, PaymentMethod.E_WALLET, ewallet_details)
        
        # Simulate cancellation
        order3.update_status(OrderStatus.CANCELLED)
        
        print(f"\n📊 PHÂN TÍCH HỆ THỐNG:")
        print("=" * 40)
        
        analytics = ecommerce.get_order_analytics()
        print(f"Tổng số đơn hàng: {analytics['total_orders']}")
        print(f"Tổng doanh thu: {analytics['total_revenue']:,.0f} VNĐ")
        print(f"Thống kê trạng thái:")
        for status, count in analytics['status_breakdown'].items():
            print(f"  - {status}: {count}")
        
        print(f"\nDatabase Stats:")
        db_stats = analytics['database_stats']
        print(f"  - Connected: {db_stats['connected']}")
        print(f"  - Total queries: {db_stats['total_queries']}")
        
        # Add product reviews
        print(f"\n⭐ ĐÁNH GIÁ SẢN PHẨM:")
        print("=" * 30)
        
        ecommerce.products["P001"].add_review(5, "Sản phẩm tuyệt vời!", "Nguyễn Văn An")
        ecommerce.products["P001"].add_review(4, "Giá hơi cao nhưng chất lượng tốt", "Trần Văn B")
        ecommerce.products["P003"].add_review(5, "MacBook rất mượt mà!", "Trần Thị Bình")
        
        # Display product info with reviews
        for product in [ecommerce.products["P001"], ecommerce.products["P003"]]:
            info = product.get_info()
            print(f"📱 {info['name']}: {info['rating']}⭐ ({info['review_count']} đánh giá)")
        
        # Show singleton pattern working
        print(f"\n🔄 KIỂM TRA SINGLETON PATTERN:")
        print("=" * 40)
        
        db1 = DatabaseConnection()
        db2 = DatabaseConnection()
        print(f"db1 is db2: {db1 is db2}")  # Should be True
        print(f"Same instance: {id(db1) == id(db2)}")
        
        db1.execute_query("SELECT * FROM orders")
        db2.execute_query("SELECT * FROM products")
        print(f"Total queries from both instances: {db1.query_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
