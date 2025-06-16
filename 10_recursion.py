"""
Thuật toán đệ quy (Recursion)
Hàm gọi chính nó với tham số khác nhau
Cần có: base case (điều kiện dừng) và recursive case (gọi đệ quy)
"""

import sys
import time

# Tăng giới hạn đệ quy nếu cần
sys.setrecursionlimit(10000)

def factorial(n):
    """
    Tính giai thừa n!
    Input: n = 5
    Output: 5! = 5 * 4 * 3 * 2 * 1 = 120
    
    Time Complexity: O(n)
    Space Complexity: O(n) - do stack đệ quy
    """
    # Base case
    if n <= 1:
        return 1
    
    # Recursive case
    return n * factorial(n - 1)

def factorial_iterative(n):
    """Tính giai thừa không đệ quy"""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def fibonacci(n):
    """
    Tính số Fibonacci thứ n
    Input: n = 6
    Output: F(6) = 8 (sequence: 0, 1, 1, 2, 3, 5, 8)
    
    Time Complexity: O(2^n) - rất chậm!
    Space Complexity: O(n)
    """
    # Base cases
    if n <= 1:
        return n
    
    # Recursive case
    return fibonacci(n - 1) + fibonacci(n - 2)

def fibonacci_memoized(n, memo={}):
    """
    Fibonacci với memoization để tránh tính toán lặp lại
    Time Complexity: O(n)
    Space Complexity: O(n)
    """
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci_memoized(n - 1, memo) + fibonacci_memoized(n - 2, memo)
    return memo[n]

def fibonacci_iterative(n):
    """Fibonacci không đệ quy - hiệu quả nhất"""
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b

def power(base, exponent):
    """
    Tính base^exponent
    Input: base = 2, exponent = 10
    Output: 2^10 = 1024
    
    Time Complexity: O(log n)
    Space Complexity: O(log n)
    """
    # Base cases
    if exponent == 0:
        return 1
    if exponent == 1:
        return base
    
    # Recursive case - tối ưu bằng cách chia đôi
    if exponent % 2 == 0:
        half_power = power(base, exponent // 2)
        return half_power * half_power
    else:
        return base * power(base, exponent - 1)

def gcd(a, b):
    """
    Tìm ước chung lớn nhất (Greatest Common Divisor)
    Sử dụng thuật toán Euclid
    Input: a = 48, b = 18
    Output: gcd(48, 18) = 6
    
    Time Complexity: O(log min(a,b))
    Space Complexity: O(log min(a,b))
    """
    # Base case
    if b == 0:
        return a
    
    # Recursive case
    return gcd(b, a % b)

def sum_array(arr, index=0):
    """
    Tính tổng các phần tử trong mảng
    Input: arr = [1, 2, 3, 4, 5]
    Output: 15
    """
    # Base case
    if index >= len(arr):
        return 0
    
    # Recursive case
    return arr[index] + sum_array(arr, index + 1)

def reverse_string(s):
    """
    Đảo ngược chuỗi
    Input: s = "hello"
    Output: "olleh"
    """
    # Base case
    if len(s) <= 1:
        return s
    
    # Recursive case
    return s[-1] + reverse_string(s[:-1])

def is_palindrome(s):
    """
    Kiểm tra chuỗi có phải palindrome không
    Input: s = "racecar"
    Output: True
    """
    # Base case
    if len(s) <= 1:
        return True
    
    # Recursive case
    if s[0] != s[-1]:
        return False
    
    return is_palindrome(s[1:-1])

def binary_search_recursive(arr, target, left=0, right=None):
    """
    Tìm kiếm nhị phân đệ quy
    Input: arr = [1, 3, 5, 7, 9, 11], target = 7
    Output: 3 (index của 7)
    """
    if right is None:
        right = len(arr) - 1
    
    # Base case
    if left > right:
        return -1
    
    mid = (left + right) // 2
    
    # Base case - tìm thấy
    if arr[mid] == target:
        return mid
    
    # Recursive cases
    if arr[mid] > target:
        return binary_search_recursive(arr, target, left, mid - 1)
    else:
        return binary_search_recursive(arr, target, mid + 1, right)

def hanoi_tower(n, source, destination, auxiliary):
    """
    Bài toán Tháp Hà Nội
    Input: n = 3 disks, source = 'A', destination = 'C', auxiliary = 'B'
    Output: Chuỗi các bước di chuyển
    
    Time Complexity: O(2^n)
    Space Complexity: O(n)
    """
    moves = []
    
    def hanoi_helper(n, source, destination, auxiliary):
        # Base case
        if n == 1:
            moves.append(f"Move disk 1 from {source} to {destination}")
            return
        
        # Recursive cases
        # 1. Di chuyển n-1 đĩa từ source sang auxiliary
        hanoi_helper(n - 1, source, auxiliary, destination)
        
        # 2. Di chuyển đĩa lớn nhất từ source sang destination
        moves.append(f"Move disk {n} from {source} to {destination}")
        
        # 3. Di chuyển n-1 đĩa từ auxiliary sang destination
        hanoi_helper(n - 1, auxiliary, destination, source)
    
    hanoi_helper(n, source, destination, auxiliary)
    return moves

def generate_permutations(arr):
    """
    Sinh tất cả các hoán vị của mảng
    Input: arr = [1, 2, 3]
    Output: [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]
    """
    # Base case
    if len(arr) <= 1:
        return [arr]
    
    permutations = []
    
    for i in range(len(arr)):
        # Lấy phần tử hiện tại
        current = arr[i]
        # Lấy phần còn lại
        remaining = arr[:i] + arr[i+1:]
        
        # Sinh hoán vị của phần còn lại
        for perm in generate_permutations(remaining):
            permutations.append([current] + perm)
    
    return permutations

def generate_subsets(arr):
    """
    Sinh tất cả các tập con
    Input: arr = [1, 2, 3]
    Output: [[], [1], [2], [1,2], [3], [1,3], [2,3], [1,2,3]]
    """
    # Base case
    if not arr:
        return [[]]
    
    # Lấy phần tử đầu tiên
    first = arr[0]
    rest = arr[1:]
    
    # Sinh tập con của phần còn lại
    subsets_without_first = generate_subsets(rest)
    
    # Thêm phần tử đầu tiên vào mỗi tập con
    subsets_with_first = [[first] + subset for subset in subsets_without_first]
    
    return subsets_without_first + subsets_with_first

def count_ways_to_climb(n):
    """
    Đếm số cách leo cầu thang n bậc (mỗi lần leo 1 hoặc 2 bậc)
    Input: n = 4
    Output: 5 cách (1+1+1+1, 1+1+2, 1+2+1, 2+1+1, 2+2)
    """
    # Base cases
    if n <= 1:
        return 1
    if n == 2:
        return 2
    
    # Recursive case
    return count_ways_to_climb(n - 1) + count_ways_to_climb(n - 2)

def count_ways_memoized(n, memo={}):
    """Phiên bản có memoization"""
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return 1
    if n == 2:
        return 2
    
    memo[n] = count_ways_memoized(n - 1, memo) + count_ways_memoized(n - 2, memo)
    return memo[n]

def tree_height(root):
    """
    Tính chiều cao của cây nhị phân
    Input: Binary tree
    Output: Chiều cao (số level - 1)
    """
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right
    
    def height_helper(node):
        # Base case
        if node is None:
            return -1
        
        # Recursive case
        left_height = height_helper(node.left)
        right_height = height_helper(node.right)
        
        return max(left_height, right_height) + 1
    
    return height_helper(root)

def quick_sort_recursive(arr):
    """
    Quick Sort đệ quy
    Input: arr = [3, 6, 8, 10, 1, 2, 1]
    Output: [1, 1, 2, 3, 6, 8, 10]
    """
    # Base case
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort_recursive(left) + middle + quick_sort_recursive(right)

def is_valid_parentheses_recursive(s, index=0, count=0):
    """
    Kiểm tra dấu ngoặc hợp lệ bằng đệ quy
    Input: s = "((()))"
    Output: True
    """
    # Base cases
    if index == len(s):
        return count == 0
    
    if count < 0:
        return False
    
    # Recursive cases
    if s[index] == '(':
        return is_valid_parentheses_recursive(s, index + 1, count + 1)
    elif s[index] == ')':
        return is_valid_parentheses_recursive(s, index + 1, count - 1)
    else:
        return is_valid_parentheses_recursive(s, index + 1, count)

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Recursion Examples ===")
    
    # Factorial
    print("=== Factorial ===")
    n = 5
    print(f"Factorial of {n}:")
    print(f"  Recursive: {factorial(n)}")
    print(f"  Iterative: {factorial_iterative(n)}")
    
    # Fibonacci
    print(f"\n=== Fibonacci ===")
    n = 10
    print(f"Fibonacci sequence up to F({n}):")
    
    # So sánh hiệu suất
    start_time = time.time()
    result_memo = fibonacci_memoized(n)
    memo_time = time.time() - start_time
    
    start_time = time.time()
    result_iter = fibonacci_iterative(n)
    iter_time = time.time() - start_time
    
    print(f"  Memoized: F({n}) = {result_memo} (Time: {memo_time:.6f}s)")
    print(f"  Iterative: F({n}) = {result_iter} (Time: {iter_time:.6f}s)")
    
    # Power
    print(f"\n=== Power ===")
    base, exp = 2, 10
    result = power(base, exp)
    print(f"{base}^{exp} = {result}")
    
    # GCD
    print(f"\n=== Greatest Common Divisor ===")
    a, b = 48, 18
    result = gcd(a, b)
    print(f"gcd({a}, {b}) = {result}")
    
    # Array sum
    print(f"\n=== Array Sum ===")
    arr = [1, 2, 3, 4, 5]
    result = sum_array(arr)
    print(f"Sum of {arr} = {result}")
    
    # String operations
    print(f"\n=== String Operations ===")
    s = "hello"
    reversed_s = reverse_string(s)
    print(f"Reverse of '{s}' = '{reversed_s}'")
    
    palindrome = "racecar"
    is_pal = is_palindrome(palindrome)
    print(f"'{palindrome}' is palindrome: {is_pal}")
    
    # Binary search
    print(f"\n=== Binary Search ===")
    sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
    target = 7
    index = binary_search_recursive(sorted_arr, target)
    print(f"Binary search for {target} in {sorted_arr}: index {index}")
    
    # Tower of Hanoi
    print(f"\n=== Tower of Hanoi ===")
    n_disks = 3
    moves = hanoi_tower(n_disks, 'A', 'C', 'B')
    print(f"Tower of Hanoi with {n_disks} disks:")
    for move in moves:
        print(f"  {move}")
    print(f"Total moves: {len(moves)} (should be {2**n_disks - 1})")
    
    # Permutations
    print(f"\n=== Permutations ===")
    arr = [1, 2, 3]
    perms = generate_permutations(arr)
    print(f"Permutations of {arr}:")
    for perm in perms:
        print(f"  {perm}")
    
    # Subsets
    print(f"\n=== Subsets ===")
    arr = [1, 2, 3]
    subsets = generate_subsets(arr)
    print(f"Subsets of {arr}:")
    for subset in subsets:
        print(f"  {subset}")
    
    # Climbing stairs
    print(f"\n=== Climbing Stairs ===")
    n_stairs = 5
    ways_recursive = count_ways_to_climb(n_stairs)
    ways_memoized = count_ways_memoized(n_stairs)
    print(f"Ways to climb {n_stairs} stairs:")
    print(f"  Recursive: {ways_recursive}")
    print(f"  Memoized: {ways_memoized}")
    
    # Quick sort
    print(f"\n=== Quick Sort ===")
    unsorted = [3, 6, 8, 10, 1, 2, 1]
    sorted_arr = quick_sort_recursive(unsorted)
    print(f"Original: {unsorted}")
    print(f"Sorted: {sorted_arr}")
    
    # Valid parentheses
    print(f"\n=== Valid Parentheses ===")
    test_strings = ["((()))", "((())", "()()()"]
    for s in test_strings:
        valid = is_valid_parentheses_recursive(s)
        print(f"'{s}' is valid: {valid}")
    
    # Performance comparison
    print(f"\n=== Performance Comparison ===")
    print("Fibonacci F(30) comparison:")
    
    # Memoized
    start_time = time.time()
    result = fibonacci_memoized(30, {})
    memo_time = time.time() - start_time
    
    # Iterative
    start_time = time.time()
    result = fibonacci_iterative(30)
    iter_time = time.time() - start_time
    
    print(f"  Memoized: {memo_time:.6f} seconds")
    print(f"  Iterative: {iter_time:.6f} seconds")
    print(f"  Speedup: {memo_time/iter_time:.1f}x")
