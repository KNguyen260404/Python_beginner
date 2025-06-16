"""
Bài 4: Máy tính hình học
Chủ đề: Lớp trừu tượng (Abstract Class) và ghi đè phương thức

Mục tiêu: Học cách sử dụng ABC (Abstract Base Class) và abstract methods
"""

from abc import ABC, abstractmethod
import math

class Shape(ABC):
    """Lớp trừu tượng - Hình học"""
    
    def __init__(self, name, color="Không màu"):
        self.name = name
        self.color = color
        self.created_count = 0
    
    @abstractmethod
    def calculate_area(self):
        """Phương thức trừu tượng - phải được implement ở lớp con"""
        pass
    
    @abstractmethod
    def calculate_perimeter(self):
        """Phương thức trừu tượng - phải được implement ở lớp con"""
        pass
    
    def get_info(self):
        """Hiển thị thông tin cơ bản của hình"""
        print(f"\n📐 Thông tin hình {self.name}:")
        print(f"   Màu sắc: {self.color}")
        print(f"   Diện tích: {self.calculate_area():.2f}")
        print(f"   Chu vi: {self.calculate_perimeter():.2f}")
    
    def change_color(self, new_color):
        """Đổi màu hình"""
        old_color = self.color
        self.color = new_color
        print(f"🎨 Đã đổi màu {self.name} từ {old_color} sang {new_color}")

class Rectangle(Shape):
    """Hình chữ nhật"""
    
    def __init__(self, width, height, color="Trắng"):
        super().__init__("Hình chữ nhật", color)
        self.width = width
        self.height = height
    
    def calculate_area(self):
        """Tính diện tích hình chữ nhật"""
        return self.width * self.height
    
    def calculate_perimeter(self):
        """Tính chu vi hình chữ nhật"""
        return 2 * (self.width + self.height)
    
    def is_square(self):
        """Kiểm tra có phải hình vuông không"""
        return self.width == self.height
    
    def get_diagonal(self):
        """Tính đường chéo"""
        return math.sqrt(self.width**2 + self.height**2)
    
    def get_info(self):
        """Override phương thức từ lớp cha"""
        super().get_info()
        print(f"   Chiều rộng: {self.width}")
        print(f"   Chiều cao: {self.height}")
        print(f"   Đường chéo: {self.get_diagonal():.2f}")
        if self.is_square():
            print("   ⭐ Đây là hình vuông!")

class Circle(Shape):
    """Hình tròn"""
    
    def __init__(self, radius, color="Đỏ"):
        super().__init__("Hình tròn", color)
        self.radius = radius
    
    def calculate_area(self):
        """Tính diện tích hình tròn"""
        return math.pi * self.radius**2
    
    def calculate_perimeter(self):
        """Tính chu vi hình tròn (chu vi = 2πr)"""
        return 2 * math.pi * self.radius
    
    def get_diameter(self):
        """Tính đường kính"""
        return 2 * self.radius
    
    def get_info(self):
        """Override phương thức từ lớp cha"""
        super().get_info()
        print(f"   Bán kính: {self.radius}")
        print(f"   Đường kính: {self.get_diameter()}")

class Triangle(Shape):
    """Tam giác"""
    
    def __init__(self, side_a, side_b, side_c, color="Xanh"):
        super().__init__("Tam giác", color)
        self.side_a = side_a
        self.side_b = side_b
        self.side_c = side_c
        
        # Kiểm tra tính hợp lệ của tam giác
        if not self.is_valid_triangle():
            raise ValueError("Ba cạnh không tạo thành tam giác hợp lệ!")
    
    def is_valid_triangle(self):
        """Kiểm tra tam giác hợp lệ"""
        return (self.side_a + self.side_b > self.side_c and
                self.side_a + self.side_c > self.side_b and
                self.side_b + self.side_c > self.side_a)
    
    def calculate_area(self):
        """Tính diện tích tam giác bằng công thức Heron"""
        s = self.calculate_perimeter() / 2  # Nửa chu vi
        return math.sqrt(s * (s - self.side_a) * (s - self.side_b) * (s - self.side_c))
    
    def calculate_perimeter(self):
        """Tính chu vi tam giác"""
        return self.side_a + self.side_b + self.side_c
    
    def get_triangle_type(self):
        """Xác định loại tam giác"""
        sides = sorted([self.side_a, self.side_b, self.side_c])
        
        # Kiểm tra tam giác vuông
        if abs(sides[0]**2 + sides[1]**2 - sides[2]**2) < 1e-10:
            return "Tam giác vuông"
        
        # Kiểm tra tam giác cân
        if (self.side_a == self.side_b or 
            self.side_b == self.side_c or 
            self.side_a == self.side_c):
            # Kiểm tra tam giác đều
            if self.side_a == self.side_b == self.side_c:
                return "Tam giác đều"
            return "Tam giác cân"
        
        return "Tam giác thường"
    
    def get_info(self):
        """Override phương thức từ lớp cha"""
        super().get_info()
        print(f"   Cạnh a: {self.side_a}")
        print(f"   Cạnh b: {self.side_b}")
        print(f"   Cạnh c: {self.side_c}")
        print(f"   Loại: {self.get_triangle_type()}")

class Trapezoid(Shape):
    """Hình thang"""
    
    def __init__(self, base1, base2, height, side1, side2, color="Vàng"):
        super().__init__("Hình thang", color)
        self.base1 = base1  # Đáy lớn
        self.base2 = base2  # Đáy nhỏ
        self.height = height
        self.side1 = side1  # Cạnh bên 1
        self.side2 = side2  # Cạnh bên 2
    
    def calculate_area(self):
        """Tính diện tích hình thang"""
        return (self.base1 + self.base2) * self.height / 2
    
    def calculate_perimeter(self):
        """Tính chu vi hình thang"""
        return self.base1 + self.base2 + self.side1 + self.side2
    
    def is_isosceles(self):
        """Kiểm tra hình thang cân"""
        return abs(self.side1 - self.side2) < 1e-10
    
    def get_info(self):
        """Override phương thức từ lớp cha"""
        super().get_info()
        print(f"   Đáy lớn: {self.base1}")
        print(f"   Đáy nhỏ: {self.base2}")
        print(f"   Chiều cao: {self.height}")
        print(f"   Cạnh bên 1: {self.side1}")
        print(f"   Cạnh bên 2: {self.side2}")
        if self.is_isosceles():
            print("   ⭐ Đây là hình thang cân!")

class ShapeCalculator:
    """Máy tính hình học - quản lý và tính toán các hình"""
    
    def __init__(self):
        self.shapes = []
        self.calculations_count = 0
    
    def add_shape(self, shape):
        """Thêm hình vào danh sách"""
        self.shapes.append(shape)
        print(f"✅ Đã thêm {shape.name} màu {shape.color}")
    
    def remove_shape(self, index):
        """Xóa hình theo chỉ số"""
        if 0 <= index < len(self.shapes):
            removed_shape = self.shapes.pop(index)
            print(f"🗑️ Đã xóa {removed_shape.name}")
        else:
            print("❌ Chỉ số không hợp lệ!")
    
    def display_all_shapes(self):
        """Hiển thị tất cả hình"""
        if not self.shapes:
            print("📭 Chưa có hình nào được thêm!")
            return
        
        print(f"\n📋 DANH SÁCH CÁC HÌNH ({len(self.shapes)} hình):")
        print("=" * 60)
        
        for i, shape in enumerate(self.shapes):
            print(f"{i+1}. {shape.name} - Màu: {shape.color}")
            print(f"   Diện tích: {shape.calculate_area():.2f}")
            print(f"   Chu vi: {shape.calculate_perimeter():.2f}")
    
    def get_detailed_info(self, index):
        """Hiển thị thông tin chi tiết của một hình"""
        if 0 <= index < len(self.shapes):
            self.shapes[index].get_info()
            self.calculations_count += 1
        else:
            print("❌ Chỉ số không hợp lệ!")
    
    def calculate_total_area(self):
        """Tính tổng diện tích tất cả hình"""
        total = sum(shape.calculate_area() for shape in self.shapes)
        print(f"📊 Tổng diện tích tất cả hình: {total:.2f}")
        return total
    
    def calculate_total_perimeter(self):
        """Tính tổng chu vi tất cả hình"""
        total = sum(shape.calculate_perimeter() for shape in self.shapes)
        print(f"📊 Tổng chu vi tất cả hình: {total:.2f}")
        return total
    
    def find_largest_area(self):
        """Tìm hình có diện tích lớn nhất"""
        if not self.shapes:
            print("📭 Chưa có hình nào!")
            return None
        
        largest = max(self.shapes, key=lambda shape: shape.calculate_area())
        print(f"🏆 Hình có diện tích lớn nhất: {largest.name} - {largest.calculate_area():.2f}")
        return largest
    
    def find_smallest_area(self):
        """Tìm hình có diện tích nhỏ nhất"""
        if not self.shapes:
            print("📭 Chưa có hình nào!")
            return None
        
        smallest = min(self.shapes, key=lambda shape: shape.calculate_area())
        print(f"🎯 Hình có diện tích nhỏ nhất: {smallest.name} - {smallest.calculate_area():.2f}")
        return smallest
    
    def filter_by_color(self, color):
        """Lọc hình theo màu"""
        filtered_shapes = [shape for shape in self.shapes if shape.color.lower() == color.lower()]
        
        if filtered_shapes:
            print(f"\n🎨 Các hình màu {color}:")
            for shape in filtered_shapes:
                print(f"   - {shape.name}: Diện tích = {shape.calculate_area():.2f}")
        else:
            print(f"❌ Không có hình nào màu {color}!")
        
        return filtered_shapes
    
    def get_statistics(self):
        """Thống kê tổng quan"""
        if not self.shapes:
            print("📭 Chưa có hình nào để thống kê!")
            return
        
        print(f"\n📈 THỐNG KÊ TỔNG QUAN:")
        print("=" * 40)
        print(f"Tổng số hình: {len(self.shapes)}")
        print(f"Số lần tính toán: {self.calculations_count}")
        
        # Thống kê theo loại hình
        shape_types = {}
        for shape in self.shapes:
            shape_type = shape.name
            shape_types[shape_type] = shape_types.get(shape_type, 0) + 1
        
        print("\nThống kê theo loại:")
        for shape_type, count in shape_types.items():
            print(f"   - {shape_type}: {count}")
        
        # Thống kê theo màu
        colors = {}
        for shape in self.shapes:
            color = shape.color
            colors[color] = colors.get(color, 0) + 1
        
        print("\nThống kê theo màu:")
        for color, count in colors.items():
            print(f"   - {color}: {count}")

# Demo chương trình
def main():
    print("🔢 MÁY TÍNH HÌNH HỌC 🔢")
    
    # Tạo máy tính
    calculator = ShapeCalculator()
    
    print("\n🎨 Tạo các hình học:")
    print("=" * 30)
    
    # Tạo các hình
    try:
        # Hình chữ nhật
        rect1 = Rectangle(5, 3, "Đỏ")
        rect2 = Rectangle(4, 4, "Xanh")  # Hình vuông
        
        # Hình tròn
        circle1 = Circle(3, "Vàng")
        circle2 = Circle(2.5, "Tím")
        
        # Tam giác
        triangle1 = Triangle(3, 4, 5, "Xanh lá")  # Tam giác vuông
        triangle2 = Triangle(5, 5, 5, "Cam")     # Tam giác đều
        
        # Hình thang
        trapezoid1 = Trapezoid(8, 4, 3, 4, 4, "Hồng")  # Hình thang cân
        
        # Thêm vào máy tính
        shapes = [rect1, rect2, circle1, circle2, triangle1, triangle2, trapezoid1]
        for shape in shapes:
            calculator.add_shape(shape)
        
        # Hiển thị danh sách
        calculator.display_all_shapes()
        
        # Hiển thị thông tin chi tiết
        print(f"\n🔍 THÔNG TIN CHI TIẾT:")
        print("=" * 40)
        for i in range(len(calculator.shapes)):
            calculator.get_detailed_info(i)
        
        # Tính toán tổng quan
        print(f"\n📊 TÍNH TOÁN TỔNG QUAN:")
        print("=" * 40)
        calculator.calculate_total_area()
        calculator.calculate_total_perimeter()
        calculator.find_largest_area()
        calculator.find_smallest_area()
        
        # Lọc theo màu
        print(f"\n🎨 LỌC THEO MÀU:")
        print("=" * 30)
        calculator.filter_by_color("Xanh")
        calculator.filter_by_color("Đỏ")
        
        # Đổi màu một số hình
        print(f"\n🎨 ĐỔI MÀU:")
        print("=" * 20)
        rect1.change_color("Xanh navy")
        circle1.change_color("Vàng chanh")
        
        # Thống kê cuối
        calculator.get_statistics()
        
    except ValueError as e:
        print(f"❌ Lỗi: {e}")
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")

if __name__ == "__main__":
    main()
