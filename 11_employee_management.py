"""
HỆ THỐNG QUẢN LÝ NHÂN VIÊN

Bài tập OOP cơ bản về quản lý nhân viên trong một công ty.
Minh họa các khái niệm:
- Class và Object
- Inheritance
- Polymorphism
- Method overriding
- Properties
- Static methods
- Class methods

Chức năng:
- Quản lý thông tin nhân viên
- Tính lương theo từng loại nhân viên
- Quản lý phòng ban và nhóm
- Tìm kiếm và báo cáo
"""

import datetime
from enum import Enum
from typing import List, Dict, Optional, Union


class Department(Enum):
    """Enum đại diện cho các phòng ban trong công ty"""
    MARKETING = "Marketing"
    ENGINEERING = "Kỹ thuật"
    FINANCE = "Tài chính"
    HUMAN_RESOURCES = "Nhân sự"
    SALES = "Kinh doanh"
    OPERATIONS = "Vận hành"


class Position(Enum):
    """Enum đại diện cho các vị trí công việc"""
    INTERN = "Thực tập sinh"
    JUNIOR = "Nhân viên"
    SENIOR = "Nhân viên cao cấp"
    MANAGER = "Quản lý"
    DIRECTOR = "Giám đốc"


class Employee:
    """Lớp cơ sở cho tất cả nhân viên"""
    
    # Class variable để theo dõi tổng số nhân viên
    _employee_count = 0
    
    def __init__(self, employee_id: str, name: str, birth_date: datetime.date, 
                 department: Department, position: Position, base_salary: float):
        """Khởi tạo nhân viên với thông tin cơ bản"""
        self._employee_id = employee_id
        self._name = name
        self._birth_date = birth_date
        self._department = department
        self._position = position
        self._base_salary = base_salary
        self._hire_date = datetime.date.today()
        
        # Tăng số lượng nhân viên
        Employee._employee_count += 1
    
    @property
    def employee_id(self) -> str:
        """Getter cho ID nhân viên"""
        return self._employee_id
    
    @property
    def name(self) -> str:
        """Getter cho tên nhân viên"""
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        """Setter cho tên nhân viên"""
        if not value or not isinstance(value, str):
            raise ValueError("Tên nhân viên không được để trống")
        self._name = value
    
    @property
    def age(self) -> int:
        """Tính tuổi dựa trên ngày sinh"""
        today = datetime.date.today()
        return today.year - self._birth_date.year - ((today.month, today.day) < 
                                                   (self._birth_date.month, self._birth_date.day))
    
    @property
    def department(self) -> Department:
        """Getter cho phòng ban"""
        return self._department
    
    @department.setter
    def department(self, value: Department) -> None:
        """Setter cho phòng ban"""
        if not isinstance(value, Department):
            raise TypeError("Phòng ban phải là một Department")
        self._department = value
    
    @property
    def position(self) -> Position:
        """Getter cho vị trí"""
        return self._position
    
    @position.setter
    def position(self, value: Position) -> None:
        """Setter cho vị trí"""
        if not isinstance(value, Position):
            raise TypeError("Vị trí phải là một Position")
        self._position = value
    
    @property
    def base_salary(self) -> float:
        """Getter cho lương cơ bản"""
        return self._base_salary
    
    @base_salary.setter
    def base_salary(self, value: float) -> None:
        """Setter cho lương cơ bản"""
        if value < 0:
            raise ValueError("Lương cơ bản không được âm")
        self._base_salary = value
    
    @property
    def years_of_service(self) -> int:
        """Tính số năm làm việc"""
        today = datetime.date.today()
        return today.year - self._hire_date.year - ((today.month, today.day) < 
                                                  (self._hire_date.month, self._hire_date.day))
    
    def calculate_salary(self) -> float:
        """Tính lương cho nhân viên
        Phương thức này sẽ được ghi đè bởi các lớp con
        """
        # Lương cơ bản + phụ cấp theo vị trí + phụ cấp thâm niên
        position_bonus = {
            Position.INTERN: 0,
            Position.JUNIOR: self._base_salary * 0.05,
            Position.SENIOR: self._base_salary * 0.1,
            Position.MANAGER: self._base_salary * 0.2,
            Position.DIRECTOR: self._base_salary * 0.3
        }
        
        # Phụ cấp thâm niên: 1% mỗi năm làm việc
        seniority_bonus = self._base_salary * 0.01 * self.years_of_service
        
        return self._base_salary + position_bonus[self._position] + seniority_bonus
    
    def __str__(self) -> str:
        """Biểu diễn chuỗi của nhân viên"""
        return f"{self._name} (ID: {self._employee_id}) - {self._position.value} tại {self._department.value}"
    
    @classmethod
    def get_employee_count(cls) -> int:
        """Class method trả về tổng số nhân viên"""
        return cls._employee_count
    
    @staticmethod
    def is_retirement_age(age: int) -> bool:
        """Static method kiểm tra xem một nhân viên có đủ tuổi nghỉ hưu không"""
        return age >= 60


class FullTimeEmployee(Employee):
    """Lớp đại diện cho nhân viên toàn thời gian"""
    
    def __init__(self, employee_id: str, name: str, birth_date: datetime.date,
                 department: Department, position: Position, base_salary: float,
                 health_insurance: bool = True, performance_rating: float = 1.0):
        """Khởi tạo nhân viên toàn thời gian"""
        super().__init__(employee_id, name, birth_date, department, position, base_salary)
        self._health_insurance = health_insurance
        self._performance_rating = performance_rating  # Từ 0.0 đến 2.0
    
    @property
    def performance_rating(self) -> float:
        """Getter cho đánh giá hiệu suất"""
        return self._performance_rating
    
    @performance_rating.setter
    def performance_rating(self, value: float) -> None:
        """Setter cho đánh giá hiệu suất"""
        if not 0.0 <= value <= 2.0:
            raise ValueError("Đánh giá hiệu suất phải từ 0.0 đến 2.0")
        self._performance_rating = value
    
    def calculate_salary(self) -> float:
        """Ghi đè phương thức tính lương cho nhân viên toàn thời gian"""
        base_salary = super().calculate_salary()
        
        # Thưởng theo hiệu suất
        performance_bonus = self._base_salary * (self._performance_rating - 1.0) if self._performance_rating > 1.0 else 0
        
        # Phụ cấp bảo hiểm sức khỏe
        insurance_bonus = self._base_salary * 0.05 if self._health_insurance else 0
        
        return base_salary + performance_bonus + insurance_bonus


class PartTimeEmployee(Employee):
    """Lớp đại diện cho nhân viên bán thời gian"""
    
    def __init__(self, employee_id: str, name: str, birth_date: datetime.date,
                 department: Department, position: Position, hourly_rate: float,
                 hours_worked: float = 0):
        """Khởi tạo nhân viên bán thời gian"""
        # Lương cơ bản được tính dựa trên giờ làm việc
        super().__init__(employee_id, name, birth_date, department, position, 0)
        self._hourly_rate = hourly_rate
        self._hours_worked = hours_worked
    
    @property
    def hourly_rate(self) -> float:
        """Getter cho mức lương theo giờ"""
        return self._hourly_rate
    
    @hourly_rate.setter
    def hourly_rate(self, value: float) -> None:
        """Setter cho mức lương theo giờ"""
        if value < 0:
            raise ValueError("Mức lương theo giờ không được âm")
        self._hourly_rate = value
    
    @property
    def hours_worked(self) -> float:
        """Getter cho số giờ làm việc"""
        return self._hours_worked
    
    @hours_worked.setter
    def hours_worked(self, value: float) -> None:
        """Setter cho số giờ làm việc"""
        if value < 0:
            raise ValueError("Số giờ làm việc không được âm")
        self._hours_worked = value
    
    def add_hours(self, hours: float) -> None:
        """Thêm giờ làm việc"""
        if hours < 0:
            raise ValueError("Số giờ làm việc không được âm")
        self._hours_worked += hours
    
    def reset_hours(self) -> None:
        """Reset số giờ làm việc về 0 (thường dùng sau khi tính lương)"""
        self._hours_worked = 0
    
    def calculate_salary(self) -> float:
        """Ghi đè phương thức tính lương cho nhân viên bán thời gian"""
        # Lương = số giờ làm việc * mức lương theo giờ
        base_salary = self._hourly_rate * self._hours_worked
        
        # Phụ cấp làm thêm giờ (>40 giờ/tuần)
        overtime_pay = 0
        if self._hours_worked > 40:
            overtime_hours = self._hours_worked - 40
            overtime_pay = overtime_hours * self._hourly_rate * 0.5  # Phụ cấp 50% cho giờ làm thêm
        
        return base_salary + overtime_pay


class ContractEmployee(Employee):
    """Lớp đại diện cho nhân viên hợp đồng"""
    
    def __init__(self, employee_id: str, name: str, birth_date: datetime.date,
                 department: Department, position: Position, contract_value: float,
                 contract_duration_months: int):
        """Khởi tạo nhân viên hợp đồng"""
        # Lương cơ bản được tính dựa trên giá trị hợp đồng
        super().__init__(employee_id, name, birth_date, department, position, 0)
        self._contract_value = contract_value
        self._contract_duration_months = contract_duration_months
        self._contract_start_date = datetime.date.today()
    
    @property
    def contract_value(self) -> float:
        """Getter cho giá trị hợp đồng"""
        return self._contract_value
    
    @property
    def monthly_value(self) -> float:
        """Tính giá trị hàng tháng của hợp đồng"""
        return self._contract_value / self._contract_duration_months
    
    @property
    def remaining_months(self) -> int:
        """Tính số tháng còn lại của hợp đồng"""
        today = datetime.date.today()
        months_passed = (today.year - self._contract_start_date.year) * 12 + \
                        (today.month - self._contract_start_date.month)
        remaining = self._contract_duration_months - months_passed
        return max(0, remaining)
    
    def calculate_salary(self) -> float:
        """Ghi đè phương thức tính lương cho nhân viên hợp đồng"""
        # Lương hàng tháng = giá trị hợp đồng / số tháng
        monthly_salary = self.monthly_value
        
        # Không có phụ cấp thêm cho nhân viên hợp đồng
        return monthly_salary
    
    def extend_contract(self, additional_months: int, new_contract_value: Optional[float] = None) -> None:
        """Gia hạn hợp đồng"""
        if additional_months <= 0:
            raise ValueError("Số tháng gia hạn phải lớn hơn 0")
        
        # Tính toán giá trị hợp đồng mới
        if new_contract_value is not None:
            # Giá trị còn lại của hợp đồng cũ
            remaining_value = self.monthly_value * self.remaining_months
            # Giá trị mới = giá trị còn lại + giá trị hợp đồng mới
            self._contract_value = remaining_value + new_contract_value
        else:
            # Giữ nguyên mức lương hàng tháng, chỉ gia hạn thời gian
            self._contract_value = self.monthly_value * (self.remaining_months + additional_months)
        
        # Cập nhật thời hạn hợp đồng
        self._contract_duration_months = self.remaining_months + additional_months


class EmployeeManager:
    """Lớp quản lý nhân viên"""
    
    def __init__(self):
        """Khởi tạo quản lý nhân viên"""
        self._employees: Dict[str, Employee] = {}  # Dictionary lưu trữ nhân viên theo ID
    
    def add_employee(self, employee: Employee) -> None:
        """Thêm nhân viên mới"""
        if employee.employee_id in self._employees:
            raise ValueError(f"Nhân viên với ID {employee.employee_id} đã tồn tại")
        self._employees[employee.employee_id] = employee
    
    def remove_employee(self, employee_id: str) -> None:
        """Xóa nhân viên"""
        if employee_id not in self._employees:
            raise ValueError(f"Không tìm thấy nhân viên với ID {employee_id}")
        del self._employees[employee_id]
    
    def get_employee(self, employee_id: str) -> Employee:
        """Lấy thông tin nhân viên theo ID"""
        if employee_id not in self._employees:
            raise ValueError(f"Không tìm thấy nhân viên với ID {employee_id}")
        return self._employees[employee_id]
    
    def get_all_employees(self) -> List[Employee]:
        """Lấy danh sách tất cả nhân viên"""
        return list(self._employees.values())
    
    def get_employees_by_department(self, department: Department) -> List[Employee]:
        """Lấy danh sách nhân viên theo phòng ban"""
        return [e for e in self._employees.values() if e.department == department]
    
    def get_employees_by_position(self, position: Position) -> List[Employee]:
        """Lấy danh sách nhân viên theo vị trí"""
        return [e for e in self._employees.values() if e.position == position]
    
    def calculate_total_salary(self) -> float:
        """Tính tổng lương của tất cả nhân viên"""
        return sum(e.calculate_salary() for e in self._employees.values())
    
    def calculate_department_salary(self, department: Department) -> float:
        """Tính tổng lương của nhân viên trong một phòng ban"""
        dept_employees = self.get_employees_by_department(department)
        return sum(e.calculate_salary() for e in dept_employees)
    
    def get_employee_count(self) -> int:
        """Lấy số lượng nhân viên"""
        return len(self._employees)
    
    def search_employees(self, keyword: str) -> List[Employee]:
        """Tìm kiếm nhân viên theo từ khóa trong tên"""
        keyword = keyword.lower()
        return [e for e in self._employees.values() if keyword in e.name.lower()]


def main():
    """Hàm chính để demo chương trình"""
    # Tạo quản lý nhân viên
    manager = EmployeeManager()
    
    # Tạo một số nhân viên mẫu
    # Nhân viên toàn thời gian
    ft_emp1 = FullTimeEmployee(
        "FT001", "Nguyễn Văn A", 
        datetime.date(1990, 5, 15),
        Department.ENGINEERING, Position.SENIOR,
        15000000, True, 1.2
    )
    
    ft_emp2 = FullTimeEmployee(
        "FT002", "Trần Thị B",
        datetime.date(1985, 8, 22),
        Department.MARKETING, Position.MANAGER,
        20000000, True, 1.5
    )
    
    # Nhân viên bán thời gian
    pt_emp1 = PartTimeEmployee(
        "PT001", "Lê Văn C",
        datetime.date(1995, 3, 10),
        Department.SALES, Position.JUNIOR,
        100000  # 100,000 VND/giờ
    )
    pt_emp1.add_hours(80)  # 80 giờ làm việc trong tháng
    
    # Nhân viên hợp đồng
    ct_emp1 = ContractEmployee(
        "CT001", "Phạm Thị D",
        datetime.date(1992, 11, 5),
        Department.FINANCE, Position.SENIOR,
        180000000,  # 180 triệu VND
        12  # 12 tháng
    )
    
    # Thêm nhân viên vào quản lý
    manager.add_employee(ft_emp1)
    manager.add_employee(ft_emp2)
    manager.add_employee(pt_emp1)
    manager.add_employee(ct_emp1)
    
    # In thông tin nhân viên
    print("=== DANH SÁCH NHÂN VIÊN ===")
    for emp in manager.get_all_employees():
        print(f"{emp} - Lương: {emp.calculate_salary():,.0f} VND")
    
    print("\n=== THỐNG KÊ THEO PHÒNG BAN ===")
    for dept in Department:
        dept_employees = manager.get_employees_by_department(dept)
        if dept_employees:
            dept_salary = manager.calculate_department_salary(dept)
            print(f"{dept.value}: {len(dept_employees)} nhân viên - Tổng lương: {dept_salary:,.0f} VND")
    
    print(f"\nTổng số nhân viên: {manager.get_employee_count()}")
    print(f"Tổng lương: {manager.calculate_total_salary():,.0f} VND")


if __name__ == "__main__":
    main() 