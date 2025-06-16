"""
Cấu trúc dữ liệu: Array (Mảng)
Các thao tác cơ bản: tính tổng, tìm min/max, đảo ngược, tìm phần tử trùng lặp
"""

def sum_array(arr):
    """
    Tính tổng các phần tử trong mảng
    Input: arr = [1, 2, 3, 4, 5]
    Output: 15
    """
    return sum(arr)

def find_max_min(arr):
    """
    Tìm giá trị lớn nhất và nhỏ nhất trong mảng
    Input: arr = [3, 1, 4, 1, 5, 9, 2, 6]
    Output: (max=9, min=1)
    """
    if not arr:
        return None, None
    return max(arr), min(arr)

def reverse_array(arr):
    """
    Đảo ngược mảng
    Input: arr = [1, 2, 3, 4, 5]
    Output: [5, 4, 3, 2, 1]
    """
    return arr[::-1]

def find_duplicates(arr):
    """
    Tìm các phần tử trùng lặp trong mảng
    Input: arr = [1, 2, 3, 2, 4, 3, 5]
    Output: [2, 3]
    """
    seen = set()
    duplicates = set()
    
    for num in arr:
        if num in seen:
            duplicates.add(num)
        else:
            seen.add(num)
    
    return list(duplicates)

def remove_duplicates(arr):
    """
    Loại bỏ các phần tử trùng lặp
    Input: arr = [1, 2, 2, 3, 4, 4, 5]
    Output: [1, 2, 3, 4, 5]
    """
    return list(dict.fromkeys(arr))  # Giữ thứ tự

# Ví dụ sử dụng
if __name__ == "__main__":
    # Test data
    test_array = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
    
    print("=== Array Operations Demo ===")
    print(f"Original array: {test_array}")
    print()
    
    # Tính tổng
    total = sum_array(test_array)
    print(f"Sum of array: {total}")
    
    # Tìm max/min
    max_val, min_val = find_max_min(test_array)
    print(f"Max value: {max_val}, Min value: {min_val}")
    
    # Đảo ngược
    reversed_arr = reverse_array(test_array)
    print(f"Reversed array: {reversed_arr}")
    
    # Tìm trùng lặp
    duplicates = find_duplicates(test_array)
    print(f"Duplicate elements: {duplicates}")
    
    # Loại bỏ trùng lặp
    unique_arr = remove_duplicates(test_array)
    print(f"Array without duplicates: {unique_arr}")
