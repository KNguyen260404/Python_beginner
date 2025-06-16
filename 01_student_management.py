"""
Bài 1: Hệ thống quản lý học sinh
Chủ đề: Lớp cơ bản, thuộc tính và phương thức

Mục tiêu: Học cách tạo lớp, khởi tạo đối tượng, và sử dụng các phương thức cơ bản
"""

class Student:
    def __init__(self, student_id, name, age, grade):
        """Khởi tạo thông tin học sinh"""
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.subjects = {}  # Dictionary lưu điểm các môn học
    
    def add_subject_score(self, subject, score):
        """Thêm điểm cho một môn học"""
        if 0 <= score <= 10:
            self.subjects[subject] = score
            print(f"Đã thêm điểm {score} cho môn {subject}")
        else:
            print("Điểm phải từ 0 đến 10!")
    
    def calculate_average(self):
        """Tính điểm trung bình"""
        if not self.subjects:
            return 0
        total = sum(self.subjects.values())
        return round(total / len(self.subjects), 2)
    
    def get_classification(self):
        """Xếp loại học lực"""
        avg = self.calculate_average()
        if avg >= 9:
            return "Xuất sắc"
        elif avg >= 8:
            return "Giỏi"
        elif avg >= 6.5:
            return "Khá"
        elif avg >= 5:
            return "Trung bình"
        else:
            return "Yếu"
    
    def display_info(self):
        """Hiển thị thông tin học sinh"""
        print(f"\n--- Thông tin học sinh ---")
        print(f"Mã số: {self.student_id}")
        print(f"Tên: {self.name}")
        print(f"Tuổi: {self.age}")
        print(f"Lớp: {self.grade}")
        print(f"Các môn học và điểm:")
        for subject, score in self.subjects.items():
            print(f"  - {subject}: {score}")
        print(f"Điểm trung bình: {self.calculate_average()}")
        print(f"Xếp loại: {self.get_classification()}")

class Classroom:
    def __init__(self, class_name, teacher):
        """Khởi tạo lớp học"""
        self.class_name = class_name
        self.teacher = teacher
        self.students = []
    
    def add_student(self, student):
        """Thêm học sinh vào lớp"""
        self.students.append(student)
        print(f"Đã thêm học sinh {student.name} vào lớp {self.class_name}")
    
    def remove_student(self, student_id):
        """Xóa học sinh khỏi lớp"""
        for student in self.students:
            if student.student_id == student_id:
                self.students.remove(student)
                print(f"Đã xóa học sinh {student.name} khỏi lớp")
                return
        print("Không tìm thấy học sinh!")
    
    def find_student(self, student_id):
        """Tìm học sinh theo mã số"""
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    
    def display_class_info(self):
        """Hiển thị thông tin lớp học"""
        print(f"\n=== Lớp {self.class_name} ===")
        print(f"Giáo viên chủ nhiệm: {self.teacher}")
        print(f"Số học sinh: {len(self.students)}")
        print("Danh sách học sinh:")
        for student in self.students:
            print(f"  - {student.name} (MS: {student.student_id}) - ĐTB: {student.calculate_average()}")
    
    def get_top_students(self, n=3):
        """Lấy top n học sinh giỏi nhất"""
        sorted_students = sorted(self.students, key=lambda s: s.calculate_average(), reverse=True)
        return sorted_students[:n]

# Demo chương trình
def main():
    print("🎓 CHƯƠNG TRÌNH QUẢN LÝ HỌC SINH 🎓")
    
    # Tạo lớp học
    class_10a1 = Classroom("10A1", "Cô Nguyễn Thị Lan")
    
    # Tạo học sinh
    student1 = Student("HS001", "Nguyễn Văn An", 16, "10A1")
    student1.add_subject_score("Toán", 8.5)
    student1.add_subject_score("Văn", 7.5)
    student1.add_subject_score("Anh", 9.0)
    
    student2 = Student("HS002", "Trần Thị Bình", 15, "10A1")
    student2.add_subject_score("Toán", 9.5)
    student2.add_subject_score("Văn", 8.5)
    student2.add_subject_score("Anh", 9.5)
    
    student3 = Student("HS003", "Lê Văn Cường", 16, "10A1")
    student3.add_subject_score("Toán", 6.5)
    student3.add_subject_score("Văn", 7.0)
    student3.add_subject_score("Anh", 6.0)
    
    # Thêm học sinh vào lớp
    class_10a1.add_student(student1)
    class_10a1.add_student(student2)
    class_10a1.add_student(student3)
    
    # Hiển thị thông tin lớp
    class_10a1.display_class_info()
    
    # Hiển thị thông tin chi tiết từng học sinh
    for student in class_10a1.students:
        student.display_info()
    
    # Hiển thị top học sinh giỏi
    print(f"\n🏆 TOP 3 HỌC SINH GIỎI NHẤT:")
    top_students = class_10a1.get_top_students(3)
    for i, student in enumerate(top_students, 1):
        print(f"{i}. {student.name} - ĐTB: {student.calculate_average()}")

if __name__ == "__main__":
    main()
