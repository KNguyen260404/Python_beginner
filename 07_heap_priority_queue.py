"""
Cấu trúc dữ liệu: Heap (Priority Queue)
Tree-based structure thỏa mãn heap property
Max Heap: parent >= children, Min Heap: parent <= children
Ứng dụng: priority queue, heap sort, tìm K phần tử lớn nhất/nhỏ nhất
"""

import heapq

class MinHeap:
    """Min Heap implementation - phần tử nhỏ nhất ở root"""
    
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        """
        Thêm phần tử vào heap
        Input: item = 5
        Output: Heap duy trì min heap property
        """
        heapq.heappush(self.heap, item)
    
    def pop(self):
        """
        Lấy và xóa phần tử nhỏ nhất (root)
        Input: Heap = [1, 3, 2, 7, 5]
        Output: 1, Heap = [2, 3, 5, 7]
        """
        if self.is_empty():
            raise IndexError("Heap is empty")
        return heapq.heappop(self.heap)
    
    def peek(self):
        """
        Xem phần tử nhỏ nhất mà không xóa
        Input: Heap = [1, 3, 2, 7, 5]
        Output: 1
        """
        if self.is_empty():
            raise IndexError("Heap is empty")
        return self.heap[0]
    
    def is_empty(self):
        """Kiểm tra heap có rỗng không"""
        return len(self.heap) == 0
    
    def size(self):
        """Trả về kích thước heap"""
        return len(self.heap)
    
    def build_heap(self, arr):
        """
        Xây dựng heap từ array
        Input: arr = [4, 1, 3, 2, 16, 9, 10, 14, 8, 7]
        Output: Min heap
        """
        self.heap = arr.copy()
        heapq.heapify(self.heap)
    
    def get_heap(self):
        """Trả về heap array"""
        return self.heap.copy()

class MaxHeap:
    """Max Heap implementation - phần tử lớn nhất ở root"""
    
    def __init__(self):
        self.heap = []
    
    def push(self, item):
        """
        Thêm phần tử vào max heap
        Trick: sử dụng số âm để biến min heap thành max heap
        """
        heapq.heappush(self.heap, -item)
    
    def pop(self):
        """Lấy và xóa phần tử lớn nhất"""
        if self.is_empty():
            raise IndexError("Heap is empty")
        return -heapq.heappop(self.heap)
    
    def peek(self):
        """Xem phần tử lớn nhất mà không xóa"""
        if self.is_empty():
            raise IndexError("Heap is empty")
        return -self.heap[0]
    
    def is_empty(self):
        return len(self.heap) == 0
    
    def size(self):
        return len(self.heap)
    
    def get_heap(self):
        """Trả về heap array (với giá trị thực)"""
        return [-x for x in self.heap]

class PriorityQueue:
    """Priority Queue với custom priority"""
    
    def __init__(self):
        self.heap = []
        self.counter = 0  # Để xử lý các item có cùng priority
    
    def push(self, item, priority):
        """
        Thêm item với priority
        Input: item = "Task A", priority = 1 (số nhỏ = priority cao)
        """
        heapq.heappush(self.heap, (priority, self.counter, item))
        self.counter += 1
    
    def pop(self):
        """
        Lấy item có priority cao nhất
        Output: ("Task A", 1)
        """
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        
        priority, _, item = heapq.heappop(self.heap)
        return item, priority
    
    def peek(self):
        """Xem item có priority cao nhất"""
        if self.is_empty():
            raise IndexError("Priority queue is empty")
        
        priority, _, item = self.heap[0]
        return item, priority
    
    def is_empty(self):
        return len(self.heap) == 0
    
    def size(self):
        return len(self.heap)

def find_k_largest(arr, k):
    """
    Tìm K phần tử lớn nhất trong array
    Input: arr = [3, 2, 1, 5, 6, 4], k = 2
    Output: [5, 6]
    """
    if k > len(arr):
        return arr
    
    # Sử dụng min heap với kích thước k
    heap = []
    
    for num in arr:
        if len(heap) < k:
            heapq.heappush(heap, num)
        elif num > heap[0]:
            heapq.heappushpop(heap, num)
    
    return sorted(heap, reverse=True)

def find_k_smallest(arr, k):
    """
    Tìm K phần tử nhỏ nhất trong array
    Input: arr = [3, 2, 1, 5, 6, 4], k = 2
    Output: [1, 2]
    """
    if k > len(arr):
        return sorted(arr)
    
    # Sử dụng max heap với kích thước k
    heap = []
    
    for num in arr:
        if len(heap) < k:
            heapq.heappush(heap, -num)  # Negative for max heap
        elif num < -heap[0]:
            heapq.heappushpop(heap, -num)
    
    return sorted([-x for x in heap])

def heap_sort(arr):
    """
    Sắp xếp array sử dụng heap sort
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    """
    # Tạo max heap
    max_heap = MaxHeap()
    
    # Thêm tất cả phần tử vào heap
    for num in arr:
        max_heap.push(num)
    
    # Lấy phần tử theo thứ tự giảm dần
    result = []
    while not max_heap.is_empty():
        result.append(max_heap.pop())
    
    # Đảo ngược để có thứ tự tăng dần
    return result[::-1]

def merge_k_sorted_lists(lists):
    """
    Gộp K sorted lists thành 1 sorted list
    Input: lists = [[1,4,5],[1,3,4],[2,6]]
    Output: [1,1,2,3,4,4,5,6]
    """
    heap = []
    
    # Thêm phần tử đầu tiên của mỗi list vào heap
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))  # (value, list_index, element_index)
    
    result = []
    
    while heap:
        value, list_idx, elem_idx = heapq.heappop(heap)
        result.append(value)
        
        # Thêm phần tử tiếp theo từ cùng list
        if elem_idx + 1 < len(lists[list_idx]):
            next_value = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_value, list_idx, elem_idx + 1))
    
    return result

def task_scheduler_demo():
    """
    Demo scheduler sử dụng priority queue
    """
    print("=== Task Scheduler Demo ===")
    
    pq = PriorityQueue()
    
    # Thêm tasks với priority (số nhỏ = priority cao)
    tasks = [
        ("Send email", 2),
        ("Fix critical bug", 1),
        ("Update documentation", 3),
        ("Code review", 2),
        ("Deploy to production", 1),
        ("Write unit tests", 3)
    ]
    
    print("Adding tasks to scheduler:")
    for task, priority in tasks:
        pq.push(task, priority)
        print(f"  Added: '{task}' (priority {priority})")
    
    print(f"\nProcessing tasks in priority order:")
    while not pq.is_empty():
        task, priority = pq.pop()
        print(f"  Processing: '{task}' (priority {priority})")

def find_median_stream():
    """
    Tìm median trong stream of numbers sử dụng 2 heaps
    """
    print("=== Running Median Demo ===")
    
    # Max heap cho nửa nhỏ hơn
    max_heap = MaxHeap()
    # Min heap cho nửa lớn hơn
    min_heap = MinHeap()
    
    def add_number(num):
        # Thêm vào max heap (nửa nhỏ hơn)
        if max_heap.is_empty() or num <= max_heap.peek():
            max_heap.push(num)
        else:
            min_heap.push(num)
        
        # Cân bằng hai heap
        if max_heap.size() > min_heap.size() + 1:
            min_heap.push(max_heap.pop())
        elif min_heap.size() > max_heap.size() + 1:
            max_heap.push(min_heap.pop())
    
    def get_median():
        if max_heap.size() == min_heap.size():
            return (max_heap.peek() + min_heap.peek()) / 2
        elif max_heap.size() > min_heap.size():
            return max_heap.peek()
        else:
            return min_heap.peek()
    
    numbers = [5, 15, 1, 3, 8, 7, 9, 2, 10]
    print(f"Stream: {numbers}")
    print("Adding numbers and finding median:")
    
    for num in numbers:
        add_number(num)
        median = get_median()
        print(f"  Added {num}, Median: {median}")

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Min Heap Demo ===")
    
    # Min Heap
    min_heap = MinHeap()
    
    # Thêm phần tử
    numbers = [4, 1, 3, 2, 16, 9, 10, 14, 8, 7]
    print(f"Adding numbers: {numbers}")
    
    for num in numbers:
        min_heap.push(num)
    
    print(f"Min heap: {min_heap.get_heap()}")
    print(f"Min element (peek): {min_heap.peek()}")
    
    # Lấy phần tử theo thứ tự
    print("Extracting elements in sorted order:")
    extracted = []
    while not min_heap.is_empty():
        extracted.append(min_heap.pop())
    print(f"Extracted: {extracted}")
    
    print(f"\n=== Max Heap Demo ===")
    
    # Max Heap
    max_heap = MaxHeap()
    
    for num in numbers:
        max_heap.push(num)
    
    print(f"Max heap: {max_heap.get_heap()}")
    print(f"Max element (peek): {max_heap.peek()}")
    
    # Lấy phần tử theo thứ tự giảm dần
    print("Extracting elements in descending order:")
    extracted = []
    while not max_heap.is_empty():
        extracted.append(max_heap.pop())
    print(f"Extracted: {extracted}")
    
    print(f"\n=== K Largest/Smallest Demo ===")
    
    test_array = [3, 2, 1, 5, 6, 4, 8, 7]
    k = 3
    
    largest = find_k_largest(test_array, k)
    smallest = find_k_smallest(test_array, k)
    
    print(f"Array: {test_array}")
    print(f"{k} largest elements: {largest}")
    print(f"{k} smallest elements: {smallest}")
    
    print(f"\n=== Heap Sort Demo ===")
    
    unsorted = [64, 34, 25, 12, 22, 11, 90]
    sorted_array = heap_sort(unsorted)
    
    print(f"Unsorted: {unsorted}")
    print(f"Sorted: {sorted_array}")
    
    print(f"\n=== Merge K Sorted Lists Demo ===")
    
    sorted_lists = [
        [1, 4, 5],
        [1, 3, 4],
        [2, 6]
    ]
    
    merged = merge_k_sorted_lists(sorted_lists)
    print(f"Input lists: {sorted_lists}")
    print(f"Merged: {merged}")
    
    print(f"\n")
    task_scheduler_demo()
    
    print(f"\n")
    find_median_stream()
