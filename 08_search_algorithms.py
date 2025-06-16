"""
Thuật toán tìm kiếm (Search Algorithms)
1. Linear Search - O(n): duyệt tuần tự
2. Binary Search - O(log n): tìm kiếm nhị phân trên dữ liệu đã sắp xếp
3. Jump Search - O(√n): nhảy theo bước rồi tìm kiếm tuyến tính
"""

import math

def linear_search(arr, target):
    """
    Tìm kiếm tuyến tính - duyệt từng phần tử
    Input: arr = [64, 34, 25, 12, 22, 11, 90], target = 22
    Output: 4 (index của 22)
    
    Time Complexity: O(n)
    Space Complexity: O(1)
    """
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def binary_search(arr, target):
    """
    Tìm kiếm nhị phân - chỉ hoạt động với mảng đã sắp xếp
    Input: arr = [11, 12, 22, 25, 34, 64, 90], target = 22
    Output: 2 (index của 22)
    
    Time Complexity: O(log n)
    Space Complexity: O(1)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def binary_search_recursive(arr, target, left=0, right=None):
    """
    Tìm kiếm nhị phân đệ quy
    Input: arr = [11, 12, 22, 25, 34, 64, 90], target = 22
    Output: 2
    
    Time Complexity: O(log n)
    Space Complexity: O(log n) - do stack đệ quy
    """
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)

def find_insert_position(arr, target):
    """
    Tìm vị trí để chèn target vào mảng đã sắp xếp
    Input: arr = [1, 3, 5, 6], target = 4
    Output: 2 (chèn 4 vào vị trí index 2)
    
    Sử dụng binary search
    """
    left, right = 0, len(arr)
    
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid
    
    return left

def find_first_occurrence(arr, target):
    """
    Tìm vị trí đầu tiên của target (có thể có nhiều phần tử trùng lặp)
    Input: arr = [1, 2, 2, 2, 3, 4, 5], target = 2
    Output: 1 (index đầu tiên của 2)
    """
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            right = mid - 1  # Tiếp tục tìm ở bên trái
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

def find_last_occurrence(arr, target):
    """
    Tìm vị trí cuối cùng của target
    Input: arr = [1, 2, 2, 2, 3, 4, 5], target = 2
    Output: 3 (index cuối cùng của 2)
    """
    left, right = 0, len(arr) - 1
    result = -1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            result = mid
            left = mid + 1  # Tiếp tục tìm ở bên phải
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return result

def count_occurrences(arr, target):
    """
    Đếm số lần xuất hiện của target
    Input: arr = [1, 2, 2, 2, 3, 4, 5], target = 2
    Output: 3
    """
    first = find_first_occurrence(arr, target)
    if first == -1:
        return 0
    
    last = find_last_occurrence(arr, target)
    return last - first + 1

def jump_search(arr, target):
    """
    Jump Search - nhảy theo bước √n rồi tìm kiếm tuyến tính
    Input: arr = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
           target = 55
    Output: 10
    
    Time Complexity: O(√n)
    Space Complexity: O(1)
    """
    n = len(arr)
    step = int(math.sqrt(n))
    prev = 0
    
    # Tìm block chứa target
    while arr[min(step, n) - 1] < target:
        prev = step
        step += int(math.sqrt(n))
        if prev >= n:
            return -1
    
    # Tìm kiếm tuyến tính trong block
    while arr[prev] < target:
        prev += 1
        if prev == min(step, n):
            return -1
    
    # Nếu tìm thấy
    if arr[prev] == target:
        return prev
    
    return -1

def interpolation_search(arr, target):
    """
    Interpolation Search - cải tiến của binary search
    Hoạt động tốt với dữ liệu phân bố đều
    Input: arr = [10, 12, 13, 16, 18, 19, 20, 21, 22, 23, 24, 33, 35, 42, 47]
           target = 18
    Output: 4
    
    Time Complexity: O(log log n) trung bình, O(n) tệ nhất
    """
    low = 0
    high = len(arr) - 1
    
    while low <= high and target >= arr[low] and target <= arr[high]:
        # Nếu chỉ có 1 phần tử
        if low == high:
            if arr[low] == target:
                return low
            return -1
        
        # Tính vị trí dự đoán
        pos = low + int(((float(target - arr[low]) / (arr[high] - arr[low])) * (high - low)))
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    
    return -1

def exponential_search(arr, target):
    """
    Exponential Search - tìm range rồi dùng binary search
    Input: arr = [2, 3, 4, 10, 40, 50, 80, 100, 120, 150]
           target = 10
    Output: 3
    
    Time Complexity: O(log n)
    """
    # Nếu target ở vị trí đầu tiên
    if arr[0] == target:
        return 0
    
    # Tìm range cho binary search
    n = len(arr)
    i = 1
    while i < n and arr[i] <= target:
        i *= 2
    
    # Thực hiện binary search trong range [i//2, min(i, n-1)]
    return binary_search_range(arr, target, i // 2, min(i, n - 1))

def binary_search_range(arr, target, left, right):
    """Binary search trong một range cụ thể"""
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

def search_in_rotated_array(arr, target):
    """
    Tìm kiếm trong mảng đã sắp xếp nhưng bị xoay
    Input: arr = [4, 5, 6, 7, 0, 1, 2], target = 0
    Output: 4
    
    Time Complexity: O(log n)
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if arr[mid] == target:
            return mid
        
        # Kiểm tra nửa nào được sắp xếp
        if arr[left] <= arr[mid]:
            # Nửa trái được sắp xếp
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:
            # Nửa phải được sắp xếp
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1
    
    return -1

def find_peak_element(arr):
    """
    Tìm peak element (phần tử lớn hơn các phần tử kề bên)
    Input: arr = [1, 2, 3, 1]
    Output: 2 (index của peak element 3)
    
    Time Complexity: O(log n)
    """
    left, right = 0, len(arr) - 1
    
    while left < right:
        mid = (left + right) // 2
        
        if arr[mid] > arr[mid + 1]:
            right = mid
        else:
            left = mid + 1
    
    return left

def search_2d_matrix(matrix, target):
    """
    Tìm kiếm trong ma trận 2D đã sắp xếp
    Input: matrix = [[1,4,7,11],[2,5,8,12],[3,6,9,16],[10,13,14,17]]
           target = 5
    Output: True
    
    Time Complexity: O(m + n)
    """
    if not matrix or not matrix[0]:
        return False
    
    row = 0
    col = len(matrix[0]) - 1
    
    while row < len(matrix) and col >= 0:
        if matrix[row][col] == target:
            return True
        elif matrix[row][col] > target:
            col -= 1
        else:
            row += 1
    
    return False

# Ví dụ sử dụng và benchmark
if __name__ == "__main__":
    print("=== Search Algorithms Demo ===")
    
    # Dữ liệu test
    unsorted_arr = [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
    sorted_arr = sorted(unsorted_arr)
    target = 22
    
    print(f"Unsorted array: {unsorted_arr}")
    print(f"Sorted array: {sorted_arr}")
    print(f"Target: {target}")
    print()
    
    # Linear Search
    print("=== Linear Search ===")
    result = linear_search(unsorted_arr, target)
    print(f"Linear search result: index {result}")
    
    # Binary Search
    print("\n=== Binary Search ===")
    result = binary_search(sorted_arr, target)
    print(f"Binary search result: index {result}")
    
    result_recursive = binary_search_recursive(sorted_arr, target)
    print(f"Binary search (recursive) result: index {result_recursive}")
    
    # Find Insert Position
    print("\n=== Find Insert Position ===")
    test_arr = [1, 3, 5, 6]
    insert_targets = [4, 2, 7, 0]
    
    for t in insert_targets:
        pos = find_insert_position(test_arr, t)
        print(f"Insert {t} at position: {pos}")
    
    # Find First/Last Occurrence
    print("\n=== Find First/Last Occurrence ===")
    duplicate_arr = [1, 2, 2, 2, 3, 4, 5]
    dup_target = 2
    
    first = find_first_occurrence(duplicate_arr, dup_target)
    last = find_last_occurrence(duplicate_arr, dup_target)
    count = count_occurrences(duplicate_arr, dup_target)
    
    print(f"Array: {duplicate_arr}")
    print(f"Target {dup_target}: first={first}, last={last}, count={count}")
    
    # Jump Search
    print("\n=== Jump Search ===")
    fibonacci = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]
    jump_target = 55
    
    result = jump_search(fibonacci, jump_target)
    print(f"Jump search for {jump_target} in fibonacci: index {result}")
    
    # Interpolation Search
    print("\n=== Interpolation Search ===")
    uniform_arr = [10, 12, 13, 16, 18, 19, 20, 21, 22, 23, 24, 33, 35, 42, 47]
    interp_target = 18
    
    result = interpolation_search(uniform_arr, interp_target)
    print(f"Interpolation search for {interp_target}: index {result}")
    
    # Exponential Search
    print("\n=== Exponential Search ===")
    exp_arr = [2, 3, 4, 10, 40, 50, 80, 100, 120, 150]
    exp_target = 10
    
    result = exponential_search(exp_arr, exp_target)
    print(f"Exponential search for {exp_target}: index {result}")
    
    # Search in Rotated Array
    print("\n=== Search in Rotated Array ===")
    rotated_arr = [4, 5, 6, 7, 0, 1, 2]
    rot_target = 0
    
    result = search_in_rotated_array(rotated_arr, rot_target)
    print(f"Search {rot_target} in rotated array {rotated_arr}: index {result}")
    
    # Find Peak Element
    print("\n=== Find Peak Element ===")
    peak_arr = [1, 2, 3, 1]
    peak_index = find_peak_element(peak_arr)
    print(f"Peak element in {peak_arr}: index {peak_index} (value: {peak_arr[peak_index]})")
    
    # Search 2D Matrix
    print("\n=== Search 2D Matrix ===")
    matrix = [
        [1,  4,  7,  11],
        [2,  5,  8,  12],
        [3,  6,  9,  16],
        [10, 13, 14, 17]
    ]
    
    matrix_targets = [5, 15]
    
    for t in matrix_targets:
        found = search_2d_matrix(matrix, t)
        print(f"Search {t} in 2D matrix: {'Found' if found else 'Not found'}")
    
    # Performance comparison
    print("\n=== Performance Comparison ===")
    import time
    
    large_sorted_arr = list(range(0, 1000000, 2))  # 500,000 even numbers
    search_target = 999998
    
    # Linear search
    start_time = time.time()
    result = linear_search(large_sorted_arr, search_target)
    linear_time = time.time() - start_time
    
    # Binary search
    start_time = time.time()
    result = binary_search(large_sorted_arr, search_target)
    binary_time = time.time() - start_time
    
    print(f"Array size: {len(large_sorted_arr)}")
    print(f"Linear search time: {linear_time:.6f} seconds")
    print(f"Binary search time: {binary_time:.6f} seconds")
    print(f"Binary search is {linear_time/binary_time:.1f}x faster")
