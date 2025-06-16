"""
Cấu trúc dữ liệu: Set (Tập hợp)
Collection với các phần tử duy nhất, không có thứ tự
Ứng dụng: loại bỏ trùng lặp, kiểm tra tồn tại, các phép toán tập hợp
"""

class CustomSet:
    """Cài đặt Set đơn giản sử dụng hash table"""
    
    def __init__(self, iterable=None):
        self.data = {}  # Sử dụng dict để lưu trữ, key là phần tử, value là True
        if iterable:
            for item in iterable:
                self.add(item)
    
    def add(self, element):
        """
        Thêm phần tử vào set
        Input: element = 5
        Output: Set = {1, 2, 3, 5}
        """
        self.data[element] = True
    
    def remove(self, element):
        """
        Xóa phần tử khỏi set
        Input: element = 3
        Output: Set = {1, 2, 5} (nếu 3 tồn tại)
        """
        if element in self.data:
            del self.data[element]
        else:
            raise KeyError(f"Element {element} not found in set")
    
    def discard(self, element):
        """
        Xóa phần tử mà không raise exception nếu không tồn tại
        Input: element = 10
        Output: Không làm gì nếu 10 không tồn tại
        """
        if element in self.data:
            del self.data[element]
    
    def contains(self, element):
        """
        Kiểm tra phần tử có trong set không
        Input: element = 5
        Output: True/False
        """
        return element in self.data
    
    def size(self):
        """
        Trả về số lượng phần tử
        Output: 4
        """
        return len(self.data)
    
    def is_empty(self):
        """
        Kiểm tra set có rỗng không
        Output: True/False
        """
        return len(self.data) == 0
    
    def clear(self):
        """
        Xóa tất cả phần tử
        """
        self.data.clear()
    
    def to_list(self):
        """
        Chuyển đổi set thành list
        Output: [1, 2, 3, 5]
        """
        return list(self.data.keys())
    
    def union(self, other_set):
        """
        Phép hợp (Union): A ∪ B
        Input: set1 = {1, 2, 3}, set2 = {3, 4, 5}
        Output: {1, 2, 3, 4, 5}
        """
        result = CustomSet()
        
        # Thêm tất cả phần tử từ set hiện tại
        for element in self.data:
            result.add(element)
        
        # Thêm tất cả phần tử từ set khác
        for element in other_set.data:
            result.add(element)
        
        return result
    
    def intersection(self, other_set):
        """
        Phép giao (Intersection): A ∩ B
        Input: set1 = {1, 2, 3}, set2 = {3, 4, 5}
        Output: {3}
        """
        result = CustomSet()
        
        # Chỉ thêm phần tử có trong cả hai set
        for element in self.data:
            if element in other_set.data:
                result.add(element)
        
        return result
    
    def difference(self, other_set):
        """
        Phép hiệu (Difference): A - B
        Input: set1 = {1, 2, 3}, set2 = {3, 4, 5}
        Output: {1, 2}
        """
        result = CustomSet()
        
        # Thêm phần tử có trong set hiện tại nhưng không có trong set khác
        for element in self.data:
            if element not in other_set.data:
                result.add(element)
        
        return result
    
    def symmetric_difference(self, other_set):
        """
        Phép hiệu đối xứng (Symmetric Difference): A △ B = (A - B) ∪ (B - A)
        Input: set1 = {1, 2, 3}, set2 = {3, 4, 5}
        Output: {1, 2, 4, 5}
        """
        return self.difference(other_set).union(other_set.difference(self))
    
    def is_subset(self, other_set):
        """
        Kiểm tra có phải là tập con không: A ⊆ B
        Input: set1 = {1, 2}, set2 = {1, 2, 3, 4}
        Output: True
        """
        for element in self.data:
            if element not in other_set.data:
                return False
        return True
    
    def is_superset(self, other_set):
        """
        Kiểm tra có phải là tập cha không: A ⊇ B
        Input: set1 = {1, 2, 3, 4}, set2 = {1, 2}
        Output: True
        """
        return other_set.is_subset(self)
    
    def __str__(self):
        """String representation"""
        return "{" + ", ".join(str(x) for x in sorted(self.data.keys()) if isinstance(x, (int, float))) + "}"

def remove_duplicates_from_list(lst):
    """
    Loại bỏ phần tử trùng lặp từ list sử dụng set
    Input: lst = [1, 2, 2, 3, 4, 4, 5]
    Output: [1, 2, 3, 4, 5]
    """
    return list(set(lst))

def count_distinct_elements(lst):
    """
    Đếm số phần tử phân biệt trong list
    Input: lst = [1, 2, 2, 3, 4, 4, 5, 5, 5]
    Output: 5
    """
    unique_set = CustomSet(lst)
    return unique_set.size()

def find_common_elements(list1, list2):
    """
    Tìm phần tử chung giữa hai list
    Input: list1 = [1, 2, 3, 4], list2 = [3, 4, 5, 6]
    Output: [3, 4]
    """
    set1 = CustomSet(list1)
    set2 = CustomSet(list2)
    common = set1.intersection(set2)
    return common.to_list()

def find_unique_elements(list1, list2):
    """
    Tìm phần tử có trong list1 nhưng không có trong list2
    Input: list1 = [1, 2, 3, 4], list2 = [3, 4, 5, 6]
    Output: [1, 2]
    """
    set1 = CustomSet(list1)
    set2 = CustomSet(list2)
    unique = set1.difference(set2)
    return unique.to_list()

def check_lists_have_common_elements(list1, list2):
    """
    Kiểm tra hai list có phần tử chung không
    Input: list1 = [1, 2, 3], list2 = [4, 5, 6]
    Output: False
    """
    set1 = CustomSet(list1)
    set2 = CustomSet(list2)
    common = set1.intersection(set2)
    return not common.is_empty()

def filter_unique_words(text):
    """
    Lọc các từ duy nhất từ văn bản
    Input: text = "hello world hello python world"
    Output: ["hello", "world", "python"]
    """
    words = text.lower().split()
    unique_words = CustomSet(words)
    return unique_words.to_list()

def validate_permissions(user_permissions, required_permissions):
    """
    Kiểm tra user có đủ quyền yêu cầu không
    Input: user_permissions = ["read", "write", "execute"]
           required_permissions = ["read", "write"]
    Output: True
    """
    user_set = CustomSet(user_permissions)
    required_set = CustomSet(required_permissions)
    
    return required_set.is_subset(user_set)

def analyze_survey_responses():
    """
    Phân tích phản hồi khảo sát sử dụng set operations
    """
    # Dữ liệu mẫu: người trả lời các câu hỏi
    question_a_yes = CustomSet(["Alice", "Bob", "Charlie", "David", "Eve"])
    question_b_yes = CustomSet(["Bob", "Charlie", "Frank", "Grace"])
    question_c_yes = CustomSet(["Alice", "Charlie", "David", "Frank", "Henry"])
    
    print("=== Survey Analysis ===")
    print(f"Question A - Yes: {question_a_yes.to_list()}")
    print(f"Question B - Yes: {question_b_yes.to_list()}")
    print(f"Question C - Yes: {question_c_yes.to_list()}")
    print()
    
    # Phần tích
    print("Analysis:")
    
    # Người trả lời Yes cho cả A và B
    a_and_b = question_a_yes.intersection(question_b_yes)
    print(f"Both A and B: {a_and_b.to_list()}")
    
    # Người chỉ trả lời Yes cho A
    only_a = question_a_yes.difference(question_b_yes.union(question_c_yes))
    print(f"Only A: {only_a.to_list()}")
    
    # Người trả lời Yes cho ít nhất một câu hỏi
    at_least_one = question_a_yes.union(question_b_yes).union(question_c_yes)
    print(f"At least one: {at_least_one.to_list()}")
    
    # Người trả lời Yes cho cả ba câu hỏi
    all_three = question_a_yes.intersection(question_b_yes).intersection(question_c_yes)
    print(f"All three: {all_three.to_list()}")
    
    return {
        "both_a_and_b": a_and_b.to_list(),
        "only_a": only_a.to_list(),
        "at_least_one": at_least_one.to_list(),
        "all_three": all_three.to_list()
    }

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Custom Set Operations Demo ===")
    
    # Tạo set
    set1 = CustomSet([1, 2, 3, 4, 5])
    set2 = CustomSet([4, 5, 6, 7, 8])
    
    print(f"Set 1: {set1}")
    print(f"Set 2: {set2}")
    print()
    
    # Các phép toán tập hợp
    print("Set Operations:")
    union_set = set1.union(set2)
    print(f"Union (A ∪ B): {union_set}")
    
    intersection_set = set1.intersection(set2)
    print(f"Intersection (A ∩ B): {intersection_set}")
    
    difference_set = set1.difference(set2)
    print(f"Difference (A - B): {difference_set}")
    
    sym_diff_set = set1.symmetric_difference(set2)
    print(f"Symmetric Difference (A △ B): {sym_diff_set}")
    print()
    
    # Kiểm tra quan hệ tập hợp
    subset = CustomSet([1, 2, 3])
    superset = CustomSet([1, 2, 3, 4, 5, 6])
    
    print("Set Relationships:")
    print(f"Subset {subset} ⊆ Set1 {set1}: {subset.is_subset(set1)}")
    print(f"Superset {superset} ⊇ Set1 {set1}: {superset.is_superset(set1)}")
    print()
    
    # Ứng dụng thực tế
    print("=== Practical Applications ===")
    
    # Loại bỏ trùng lặp
    duplicate_list = [1, 2, 2, 3, 4, 4, 5, 5, 5]
    unique_list = remove_duplicates_from_list(duplicate_list)
    print(f"Remove duplicates: {duplicate_list} -> {unique_list}")
    
    # Đếm phần tử phân biệt
    count = count_distinct_elements(duplicate_list)
    print(f"Distinct elements count: {count}")
    
    # Tìm phần tử chung
    list_a = [1, 2, 3, 4, 5]
    list_b = [4, 5, 6, 7, 8]
    common = find_common_elements(list_a, list_b)
    print(f"Common elements between {list_a} and {list_b}: {common}")
    
    # Tìm phần tử duy nhất
    unique = find_unique_elements(list_a, list_b)
    print(f"Elements in first but not second: {unique}")
    
    # Kiểm tra có phần tử chung
    has_common = check_lists_have_common_elements(list_a, list_b)
    print(f"Lists have common elements: {has_common}")
    
    # Lọc từ duy nhất
    text = "hello world hello python world programming"
    unique_words = filter_unique_words(text)
    print(f"Unique words in '{text}': {unique_words}")
    
    # Kiểm tra quyền
    user_perms = ["read", "write", "execute", "admin"]
    required_perms = ["read", "write"]
    has_permission = validate_permissions(user_perms, required_perms)
    print(f"User permissions {user_perms} satisfy requirements {required_perms}: {has_permission}")
    
    print()
    
    # Phân tích khảo sát
    survey_results = analyze_survey_responses()
