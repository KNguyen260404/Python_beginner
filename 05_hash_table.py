"""
Cấu trúc dữ liệu: Hash Map / Hash Table (Bảng băm)
Key-Value mapping với truy cập O(1) trung bình
Ứng dụng: lookup nhanh, đếm tần suất, cache
"""

class HashTable:
    """Cài đặt Hash Table đơn giản với chaining để xử lý collision"""
    
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]  # Mỗi bucket là một list
    
    def _hash(self, key):
        """
        Hash function đơn giản
        Input: key = "apple"
        Output: hash_value = 3 (ví dụ)
        """
        if isinstance(key, str):
            return sum(ord(char) for char in key) % self.size
        elif isinstance(key, int):
            return key % self.size
        else:
            return hash(key) % self.size
    
    def put(self, key, value):
        """
        Thêm cặp key-value vào hash table
        Input: key = "apple", value = 5
        Output: Lưu trữ trong bucket tương ứng
        """
        index = self._hash(key)
        bucket = self.table[index]
        
        # Kiểm tra xem key đã tồn tại chưa
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # Cập nhật giá trị
                return
        
        # Nếu key chưa tồn tại, thêm mới
        bucket.append((key, value))
    
    def get(self, key):
        """
        Lấy giá trị theo key
        Input: key = "apple"
        Output: value = 5
        """
        index = self._hash(key)
        bucket = self.table[index]
        
        for k, v in bucket:
            if k == key:
                return v
        
        raise KeyError(f"Key '{key}' not found")
    
    def delete(self, key):
        """
        Xóa cặp key-value
        Input: key = "apple"
        Output: Xóa khỏi hash table
        """
        index = self._hash(key)
        bucket = self.table[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                return v
        
        raise KeyError(f"Key '{key}' not found")
    
    def contains(self, key):
        """
        Kiểm tra key có tồn tại không
        Input: key = "apple"
        Output: True/False
        """
        try:
            self.get(key)
            return True
        except KeyError:
            return False
    
    def keys(self):
        """
        Trả về tất cả keys
        Output: ["apple", "banana", "orange"]
        """
        all_keys = []
        for bucket in self.table:
            for k, v in bucket:
                all_keys.append(k)
        return all_keys
    
    def values(self):
        """
        Trả về tất cả values
        Output: [5, 3, 8]
        """
        all_values = []
        for bucket in self.table:
            for k, v in bucket:
                all_values.append(v)
        return all_values
    
    def items(self):
        """
        Trả về tất cả cặp key-value
        Output: [("apple", 5), ("banana", 3), ("orange", 8)]
        """
        all_items = []
        for bucket in self.table:
            for item in bucket:
                all_items.append(item)
        return all_items
    
    def display(self):
        """Hiển thị cấu trúc hash table"""
        print("Hash Table Structure:")
        for i, bucket in enumerate(self.table):
            if bucket:
                print(f"  Bucket {i}: {bucket}")
            else:
                print(f"  Bucket {i}: []")

def count_word_frequency(text):
    """
    Đếm tần suất xuất hiện của các từ trong text
    Input: text = "hello world hello python world"
    Output: {"hello": 2, "world": 2, "python": 1}
    """
    word_count = HashTable()
    words = text.lower().split()
    
    for word in words:
        try:
            current_count = word_count.get(word)
            word_count.put(word, current_count + 1)
        except KeyError:
            word_count.put(word, 1)
    
    # Chuyển đổi thành dictionary thông thường để hiển thị
    result = {}
    for key, value in word_count.items():
        result[key] = value
    
    return result

def find_duplicates_hash(arr):
    """
    Tìm phần tử trùng lặp sử dụng hash table
    Input: arr = [1, 2, 3, 2, 4, 5, 1]
    Output: [1, 2]
    """
    seen = HashTable()
    duplicates = []
    
    for num in arr:
        if seen.contains(num):
            if num not in duplicates:
                duplicates.append(num)
        else:
            seen.put(num, True)
    
    return duplicates

def two_sum(nums, target):
    """
    Tìm hai số trong mảng có tổng bằng target
    Input: nums = [2, 7, 11, 15], target = 9
    Output: [0, 1] (vì nums[0] + nums[1] = 2 + 7 = 9)
    """
    hash_map = HashTable()
    
    for i, num in enumerate(nums):
        complement = target - num
        
        if hash_map.contains(complement):
            return [hash_map.get(complement), i]
        
        hash_map.put(num, i)
    
    return []  # Không tìm thấy

def group_anagrams(words):
    """
    Nhóm các từ là anagram của nhau
    Input: words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    Output: [["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]
    """
    anagram_groups = HashTable()
    
    for word in words:
        # Sắp xếp các ký tự để tạo key
        sorted_word = ''.join(sorted(word))
        
        try:
            group = anagram_groups.get(sorted_word)
            group.append(word)
        except KeyError:
            anagram_groups.put(sorted_word, [word])
    
    return anagram_groups.values()

def cache_demo():
    """
    Demo cache đơn giản sử dụng hash table
    """
    class SimpleCache:
        def __init__(self, max_size=3):
            self.cache = HashTable()
            self.max_size = max_size
            self.access_order = []  # Để theo dõi thứ tự truy cập
        
        def get(self, key):
            if self.cache.contains(key):
                # Cập nhật thứ tự truy cập (LRU)
                self.access_order.remove(key)
                self.access_order.append(key)
                return self.cache.get(key)
            else:
                return None
        
        def put(self, key, value):
            if self.cache.contains(key):
                # Cập nhật giá trị hiện có
                self.cache.put(key, value)
                self.access_order.remove(key)
                self.access_order.append(key)
            else:
                # Thêm mới
                if len(self.access_order) >= self.max_size:
                    # Xóa phần tử cũ nhất (LRU)
                    oldest_key = self.access_order.pop(0)
                    self.cache.delete(oldest_key)
                    print(f"    Evicted: {oldest_key}")
                
                self.cache.put(key, value)
                self.access_order.append(key)
        
        def display(self):
            print(f"    Cache contents: {dict(self.cache.items())}")
            print(f"    Access order: {self.access_order}")
    
    print("=== Simple Cache Demo ===")
    cache = SimpleCache(max_size=3)
    
    operations = [
        ("put", "A", 1),
        ("put", "B", 2),
        ("put", "C", 3),
        ("get", "A", None),
        ("put", "D", 4),  # Sẽ evict B
        ("get", "B", None),  # Cache miss
        ("get", "C", None),
        ("put", "E", 5),  # Sẽ evict A
    ]
    
    for op in operations:
        if op[0] == "put":
            print(f"  PUT {op[1]}={op[2]}")
            cache.put(op[1], op[2])
        else:
            print(f"  GET {op[1]}")
            result = cache.get(op[1])
            print(f"    Result: {result}")
        
        cache.display()
        print()

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Hash Table Operations Demo ===")
    
    # Tạo hash table
    ht = HashTable(size=5)
    
    # Thêm dữ liệu
    print("Adding key-value pairs:")
    items = [("apple", 5), ("banana", 3), ("orange", 8), ("grape", 2), ("kiwi", 4)]
    
    for key, value in items:
        ht.put(key, value)
        print(f"  Added: {key} -> {value}")
    
    print(f"\nHash table structure:")
    ht.display()
    
    print(f"\nAll keys: {ht.keys()}")
    print(f"All values: {ht.values()}")
    
    # Truy cập dữ liệu
    print(f"\nAccessing values:")
    test_keys = ["apple", "banana", "mango"]
    for key in test_keys:
        try:
            value = ht.get(key)
            print(f"  {key}: {value}")
        except KeyError as e:
            print(f"  {key}: {e}")
    
    # Xóa dữ liệu
    print(f"\nDeleting 'banana':")
    try:
        deleted_value = ht.delete("banana")
        print(f"  Deleted value: {deleted_value}")
        print(f"  Keys after deletion: {ht.keys()}")
    except KeyError as e:
        print(f"  Error: {e}")
    
    # Đếm tần suất từ
    print(f"\n=== Word Frequency Counter ===")
    text = "hello world hello python world hello"
    word_freq = count_word_frequency(text)
    print(f"Text: '{text}'")
    print(f"Word frequencies: {word_freq}")
    
    # Tìm phần tử trùng lặp
    print(f"\n=== Find Duplicates ===")
    test_array = [1, 2, 3, 2, 4, 5, 1, 6, 3]
    duplicates = find_duplicates_hash(test_array)
    print(f"Array: {test_array}")
    print(f"Duplicates: {duplicates}")
    
    # Two Sum problem
    print(f"\n=== Two Sum Problem ===")
    nums = [2, 7, 11, 15]
    target = 9
    result = two_sum(nums, target)
    print(f"Array: {nums}, Target: {target}")
    print(f"Indices: {result}")
    if result:
        print(f"Values: {nums[result[0]]} + {nums[result[1]]} = {target}")
    
    # Group Anagrams
    print(f"\n=== Group Anagrams ===")
    words = ["eat", "tea", "tan", "ate", "nat", "bat"]
    anagram_groups = group_anagrams(words)
    print(f"Words: {words}")
    print(f"Anagram groups: {list(anagram_groups)}")
    
    # Cache demo
    print(f"\n")
    cache_demo()
