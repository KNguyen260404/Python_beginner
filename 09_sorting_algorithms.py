"""
Thuật toán sắp xếp (Sorting Algorithms)
1. Simple sorts: Bubble, Selection, Insertion - O(n²)
2. Efficient sorts: Merge, Quick, Heap - O(n log n)
3. Special sorts: Counting, Radix, Bucket - O(n)
"""

import random
import time

def bubble_sort(arr):
    """
    Bubble Sort - so sánh cặp phần tử liền kề và đổi chỗ
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    n = len(arr)
    arr = arr.copy()  # Không thay đổi mảng gốc
    
    for i in range(n):
        swapped = False
        
        # Duyệt từ 0 đến n-i-1
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        
        # Nếu không có hoán đổi nào, mảng đã sắp xếp
        if not swapped:
            break
    
    return arr

def selection_sort(arr):
    """
    Selection Sort - tìm phần tử nhỏ nhất và đưa về đầu
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n²)
    Space Complexity: O(1)
    """
    arr = arr.copy()
    n = len(arr)
    
    for i in range(n):
        # Tìm phần tử nhỏ nhất trong phần chưa sắp xếp
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        
        # Hoán đổi phần tử nhỏ nhất với phần tử đầu tiên
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    
    return arr

def insertion_sort(arr):
    """
    Insertion Sort - chèn phần tử vào vị trí đúng
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n²) tệ nhất, O(n) tốt nhất
    Space Complexity: O(1)
    """
    arr = arr.copy()
    
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        
        # Di chuyển các phần tử lớn hơn key về phía sau
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        
        arr[j + 1] = key
    
    return arr

def merge_sort(arr):
    """
    Merge Sort - chia để trị
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n log n)
    Space Complexity: O(n)
    """
    def merge(left, right):
        """Gộp hai mảng đã sắp xếp"""
        result = []
        i = j = 0
        
        # Gộp các phần tử theo thứ tự
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        
        # Thêm các phần tử còn lại
        result.extend(left[i:])
        result.extend(right[j:])
        
        return result
    
    if len(arr) <= 1:
        return arr
    
    # Chia mảng thành hai nửa
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Gộp hai nửa đã sắp xếp
    return merge(left, right)

def quick_sort(arr):
    """
    Quick Sort - chọn pivot và phân hoạch
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n log n) trung bình, O(n²) tệ nhất
    Space Complexity: O(log n)
    """
    def partition(arr, low, high):
        """Phân hoạch mảng quanh pivot"""
        pivot = arr[high]  # Chọn phần tử cuối làm pivot
        i = low - 1
        
        for j in range(low, high):
            if arr[j] <= pivot:
                i += 1
                arr[i], arr[j] = arr[j], arr[i]
        
        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        return i + 1
    
    def quick_sort_helper(arr, low, high):
        if low < high:
            pi = partition(arr, low, high)
            
            # Sắp xếp đệ quy hai phần
            quick_sort_helper(arr, low, pi - 1)
            quick_sort_helper(arr, pi + 1, high)
    
    arr = arr.copy()
    quick_sort_helper(arr, 0, len(arr) - 1)
    return arr

def heap_sort(arr):
    """
    Heap Sort - sử dụng heap để sắp xếp
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n log n)
    Space Complexity: O(1)
    """
    def heapify(arr, n, i):
        """Tạo max heap"""
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        # Nếu con trái lớn hơn root
        if left < n and arr[left] > arr[largest]:
            largest = left
        
        # Nếu con phải lớn hơn largest hiện tại
        if right < n and arr[right] > arr[largest]:
            largest = right
        
        # Nếu largest không phải root
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest)
    
    arr = arr.copy()
    n = len(arr)
    
    # Xây dựng max heap
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    
    # Trích xuất phần tử từ heap
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # Hoán đổi
        heapify(arr, i, 0)
    
    return arr

def counting_sort(arr):
    """
    Counting Sort - đếm tần suất xuất hiện
    Input: arr = [4, 2, 2, 8, 3, 3, 1]
    Output: [1, 2, 2, 3, 3, 4, 8]
    
    Time Complexity: O(n + k) với k là range của dữ liệu
    Space Complexity: O(k)
    """
    if not arr:
        return arr
    
    # Tìm giá trị max và min
    max_val = max(arr)
    min_val = min(arr)
    range_val = max_val - min_val + 1
    
    # Tạo mảng đếm
    count = [0] * range_val
    
    # Đếm tần suất
    for num in arr:
        count[num - min_val] += 1
    
    # Tạo mảng kết quả
    result = []
    for i in range(range_val):
        result.extend([i + min_val] * count[i])
    
    return result

def radix_sort(arr):
    """
    Radix Sort - sắp xếp theo từng chữ số
    Input: arr = [170, 45, 75, 90, 2, 802, 24, 66]
    Output: [2, 24, 45, 66, 75, 90, 170, 802]
    
    Time Complexity: O(d * (n + k)) với d là số chữ số
    Space Complexity: O(n + k)
    """
    def counting_sort_for_radix(arr, exp):
        """Counting sort cho radix sort"""
        n = len(arr)
        output = [0] * n
        count = [0] * 10
        
        # Đếm tần suất của các chữ số
        for i in range(n):
            index = arr[i] // exp
            count[index % 10] += 1
        
        # Tính vị trí thực tế
        for i in range(1, 10):
            count[i] += count[i - 1]
        
        # Xây dựng mảng output
        i = n - 1
        while i >= 0:
            index = arr[i] // exp
            output[count[index % 10] - 1] = arr[i]
            count[index % 10] -= 1
            i -= 1
        
        # Sao chép output về arr
        for i in range(n):
            arr[i] = output[i]
    
    if not arr:
        return arr
    
    arr = arr.copy()
    
    # Tìm số lớn nhất để biết số chữ số
    max_num = max(arr)
    
    # Áp dụng counting sort cho từng chữ số
    exp = 1
    while max_num // exp > 0:
        counting_sort_for_radix(arr, exp)
        exp *= 10
    
    return arr

def bucket_sort(arr):
    """
    Bucket Sort - phân phối vào các bucket rồi sắp xếp
    Input: arr = [0.897, 0.565, 0.656, 0.1234, 0.665, 0.3434]
    Output: [0.1234, 0.3434, 0.565, 0.656, 0.665, 0.897]
    
    Time Complexity: O(n + k) trung bình
    Space Complexity: O(n)
    """
    if not arr:
        return arr
    
    # Tạo buckets
    n = len(arr)
    buckets = [[] for _ in range(n)]
    
    # Phân phối vào buckets
    for num in arr:
        bucket_index = int(n * num)
        if bucket_index == n:
            bucket_index = n - 1
        buckets[bucket_index].append(num)
    
    # Sắp xếp từng bucket
    for bucket in buckets:
        bucket.sort()
    
    # Kết hợp các bucket
    result = []
    for bucket in buckets:
        result.extend(bucket)
    
    return result

def shell_sort(arr):
    """
    Shell Sort - cải tiến của insertion sort
    Input: arr = [64, 34, 25, 12, 22, 11, 90]
    Output: [11, 12, 22, 25, 34, 64, 90]
    
    Time Complexity: O(n log n) đến O(n²)
    Space Complexity: O(1)
    """
    arr = arr.copy()
    n = len(arr)
    
    # Bắt đầu với gap lớn và giảm dần
    gap = n // 2
    
    while gap > 0:
        # Thực hiện insertion sort với gap
        for i in range(gap, n):
            temp = arr[i]
            j = i
            
            # Dịch chuyển các phần tử
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            
            arr[j] = temp
        
        gap //= 2
    
    return arr

def is_sorted(arr):
    """Kiểm tra mảng đã sắp xếp chưa"""
    return all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))

def benchmark_sorting_algorithms():
    """So sánh hiệu suất các thuật toán sắp xếp"""
    
    algorithms = [
        ("Bubble Sort", bubble_sort),
        ("Selection Sort", selection_sort),
        ("Insertion Sort", insertion_sort),
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
        ("Heap Sort", heap_sort),
        ("Shell Sort", shell_sort),
    ]
    
    # Tạo dữ liệu test
    sizes = [100, 1000]
    
    for size in sizes:
        print(f"\n=== Benchmark with {size} elements ===")
        
        # Tạo mảng ngẫu nhiên
        test_array = [random.randint(1, 1000) for _ in range(size)]
        
        for name, algorithm in algorithms:
            # Bỏ qua các thuật toán O(n²) với dữ liệu lớn
            if size > 1000 and name in ["Bubble Sort", "Selection Sort"]:
                continue
            
            start_time = time.time()
            sorted_array = algorithm(test_array)
            end_time = time.time()
            
            # Kiểm tra tính đúng đắn
            if is_sorted(sorted_array):
                print(f"{name:15}: {end_time - start_time:.6f} seconds ✓")
            else:
                print(f"{name:15}: FAILED ✗")

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Sorting Algorithms Demo ===")
    
    # Dữ liệu test
    test_data = [64, 34, 25, 12, 22, 11, 90]
    print(f"Original array: {test_data}")
    print()
    
    # Test các thuật toán
    algorithms = [
        ("Bubble Sort", bubble_sort),
        ("Selection Sort", selection_sort),
        ("Insertion Sort", insertion_sort),
        ("Merge Sort", merge_sort),
        ("Quick Sort", quick_sort),
        ("Heap Sort", heap_sort),
        ("Shell Sort", shell_sort),
    ]
    
    for name, algorithm in algorithms:
        sorted_array = algorithm(test_data)
        print(f"{name:15}: {sorted_array}")
    
    # Test special sorting algorithms
    print(f"\n=== Special Sorting Algorithms ===")
    
    # Counting Sort
    counting_data = [4, 2, 2, 8, 3, 3, 1]
    print(f"Counting Sort input: {counting_data}")
    print(f"Counting Sort output: {counting_sort(counting_data)}")
    
    # Radix Sort
    radix_data = [170, 45, 75, 90, 2, 802, 24, 66]
    print(f"Radix Sort input: {radix_data}")
    print(f"Radix Sort output: {radix_sort(radix_data)}")
    
    # Bucket Sort
    bucket_data = [0.897, 0.565, 0.656, 0.1234, 0.665, 0.3434]
    print(f"Bucket Sort input: {bucket_data}")
    print(f"Bucket Sort output: {bucket_sort(bucket_data)}")
    
    # Stability test
    print(f"\n=== Stability Test ===")
    # Test với các tuple (value, original_index)
    stability_data = [(4, 'a'), (2, 'b'), (4, 'c'), (1, 'd'), (2, 'e')]
    print(f"Original: {stability_data}")
    
    # Merge sort (stable)
    stable_result = merge_sort(stability_data)
    print(f"Merge Sort (stable): {stable_result}")
    
    # Quick sort (not stable)
    quick_result = quick_sort(stability_data)
    print(f"Quick Sort (unstable): {quick_result}")
    
    # Performance benchmark
    benchmark_sorting_algorithms()
    
    # Best case scenarios
    print(f"\n=== Best Case Scenarios ===")
    
    # Already sorted
    sorted_data = list(range(1, 11))
    print(f"Already sorted: {sorted_data}")
    
    start_time = time.time()
    bubble_result = bubble_sort(sorted_data)
    bubble_time = time.time() - start_time
    
    start_time = time.time()
    insertion_result = insertion_sort(sorted_data)
    insertion_time = time.time() - start_time
    
    print(f"Bubble Sort time: {bubble_time:.6f} seconds")
    print(f"Insertion Sort time: {insertion_time:.6f} seconds")
    
    # Reverse sorted
    reverse_data = list(range(10, 0, -1))
    print(f"\nReverse sorted: {reverse_data}")
    
    start_time = time.time()
    quick_result = quick_sort(reverse_data)
    quick_time = time.time() - start_time
    
    start_time = time.time()
    merge_result = merge_sort(reverse_data)
    merge_time = time.time() - start_time
    
    print(f"Quick Sort time: {quick_time:.6f} seconds")
    print(f"Merge Sort time: {merge_time:.6f} seconds")
