# 📚 Data Structures and Algorithms - Python Implementation

Thư mục này chứa các ví dụ thực tế về **Cấu trúc dữ liệu** và **Thuật toán** được viết bằng Python. Mỗi file minh họa một chủ đề cụ thể với đầu vào và đầu ra rõ ràng.

## 📂 Danh sách Files

### 🧩 Cấu trúc dữ liệu (Data Structures)

| File | Chủ đề | Mô tả | Time Complexity |
|------|--------|--------|-----------------|
| `01_array_operations.py` | **Array (Mảng)** | Tính tổng, tìm min/max, đảo ngược, loại bỏ trùng lặp | O(n) |
| `02_linked_list.py` | **Linked List** | Thêm, xóa, đảo ngược, gộp danh sách liên kết | O(n) |
| `03_stack.py` | **Stack (LIFO)** | Kiểm tra dấu ngoặc, đánh giá postfix, chuyển đổi số | O(1) push/pop |
| `04_queue.py` | **Queue (FIFO)** | Hàng đợi in, BFS, trò chơi Hot Potato | O(1) enqueue/dequeue |
| `05_hash_table.py` | **Hash Table** | Key-value mapping, đếm tần suất, cache LRU | O(1) trung bình |
| `06_set_operations.py` | **Set (Tập hợp)** | Loại bỏ trùng lặp, phép toán tập hợp, phân tích khảo sát | O(1) contains |
| `07_heap_priority_queue.py` | **Heap/Priority Queue** | Min/Max heap, tìm K largest, task scheduler | O(log n) push/pop |
| `12_binary_tree.py` | **Binary Tree/BST** | Duyệt cây, BST operations, cân bằng cây | O(h) với h = height |

### ⚙️ Thuật toán (Algorithms)

| File | Chủ đề | Mô tả | Time Complexity |
|------|--------|--------|-----------------|
| `08_search_algorithms.py` | **Tìm kiếm** | Linear, Binary, Jump, Interpolation search | O(log n) - O(n) |
| `09_sorting_algorithms.py` | **Sắp xếp** | Bubble, Merge, Quick, Heap, Radix sort | O(n log n) - O(n²) |
| `10_recursion.py` | **Đệ quy** | Factorial, Fibonacci, Tower of Hanoi, permutations | Varies |
| `11_backtracking.py` | **Quay lui** | N-Queens, Sudoku, Subset Sum, Maze solving | O(2ⁿ) - O(n!) |
| `13_graph_algorithms.py` | **Đồ thị** | BFS, DFS, Dijkstra, MST, cycle detection | O(V + E) |

## 🚀 Cách sử dụng

### Chạy từng file riêng biệt:

```bash
# Ví dụ chạy Array operations
cd /mnt/c/path/to/Python_beginner/Algorithms_and_Data_Structure
python 01_array_operations.py

# Chạy Stack operations
python 03_stack.py

# Chạy Graph algorithms
python 13_graph_algorithms.py
```

### Chạy tất cả tests:

```bash
# Chạy tất cả các file cùng lúc
python -c "
import os
for file in sorted(os.listdir('.')):
    if file.endswith('.py') and file[0].isdigit():
        print(f'\\n=== Running {file} ===')
        exec(open(file).read())
"
```

## 🎯 Ví dụ cụ thể

### Array Operations (01_array_operations.py)
```python
# Input
test_array = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

# Operations
sum_result = sum_array(test_array)          # Output: 39
max_val, min_val = find_max_min(test_array) # Output: (9, 1)
reversed_arr = reverse_array(test_array)    # Output: [3, 5, 6, 2, 9, 5, 1, 4, 1, 3]
duplicates = find_duplicates(test_array)    # Output: [1, 3, 5]
```

### Binary Search (08_search_algorithms.py)
```python
# Input
sorted_arr = [1, 3, 5, 7, 9, 11, 13, 15]
target = 7

# Binary Search
index = binary_search(sorted_arr, target)   # Output: 3
print(f"Found {target} at index {index}")
```

### N-Queens Problem (11_backtracking.py)
```python
# Input
n = 4  # 4x4 chessboard

# Solve N-Queens
solutions = solve_n_queens(n)               # Output: 2 solutions
print(f"Found {len(solutions)} solutions for {n}-Queens")
```

### Dijkstra's Algorithm (13_graph_algorithms.py)
```python
# Create weighted graph
g = Graph()
g.add_edge('A', 'B', 4)
g.add_edge('A', 'C', 2)
g.add_edge('B', 'D', 5)

# Find shortest paths
paths = dijkstra(g, 'A')
# Output: Shortest distances and paths from A to all vertices
```

## 📊 Độ phức tạp thời gian

| Cấu trúc dữ liệu | Truy cập | Tìm kiếm | Chèn | Xóa |
|------------------|----------|----------|------|-----|
| Array | O(1) | O(n) | O(n) | O(n) |
| Linked List | O(n) | O(n) | O(1) | O(1) |
| Stack | O(n) | O(n) | O(1) | O(1) |
| Queue | O(n) | O(n) | O(1) | O(1) |
| Hash Table | N/A | O(1)* | O(1)* | O(1)* |
| Binary Search Tree | O(log n) | O(log n) | O(log n) | O(log n) |
| Heap | N/A | O(n) | O(log n) | O(log n) |

*Trung bình case, worst case có thể là O(n)

## 🔍 Thuật toán tìm kiếm

| Thuật toán | Time Complexity | Space Complexity | Yêu cầu |
|------------|-----------------|------------------|---------|
| Linear Search | O(n) | O(1) | Không |
| Binary Search | O(log n) | O(1) | Sorted array |
| Jump Search | O(√n) | O(1) | Sorted array |
| Interpolation Search | O(log log n)* | O(1) | Sorted, uniform distribution |

## 🔄 Thuật toán sắp xếp

| Thuật toán | Time Complexity | Space Complexity | Stable | Ghi chú |
|------------|-----------------|------------------|--------|---------|
| Bubble Sort | O(n²) | O(1) | ✅ | Đơn giản, chậm |
| Selection Sort | O(n²) | O(1) | ❌ | Không stable |
| Insertion Sort | O(n²) | O(1) | ✅ | Tốt cho dữ liệu nhỏ |
| Merge Sort | O(n log n) | O(n) | ✅ | Consistent performance |
| Quick Sort | O(n log n)* | O(log n) | ❌ | Average case tốt |
| Heap Sort | O(n log n) | O(1) | ❌ | In-place |
| Counting Sort | O(n + k) | O(k) | ✅ | Integer sorting |
| Radix Sort | O(d(n + k)) | O(n + k) | ✅ | Non-comparative |

*Average case, worst case có thể khác

## 📈 Khi nào sử dụng thuật toán nào?

### Tìm kiếm:
- **Linear Search**: Dữ liệu chưa sắp xếp, mảng nhỏ
- **Binary Search**: Dữ liệu đã sắp xếp, cần tốc độ
- **Hash Table**: Cần truy cập O(1), có đủ memory

### Sắp xếp:
- **Insertion Sort**: Dữ liệu nhỏ (< 50 elements), gần như đã sắp xếp
- **Merge Sort**: Cần stable sort, worst-case performance quan trọng
- **Quick Sort**: General purpose, average performance tốt
- **Heap Sort**: Memory hạn chế, cần O(n log n) guaranteed
- **Counting Sort**: Integers trong range nhỏ
- **Radix Sort**: Integers, strings với độ dài cố định

### Cấu trúc dữ liệu:
- **Array**: Truy cập random, cache-friendly
- **Linked List**: Chèn/xóa thường xuyên, kích thước dynamic
- **Stack**: LIFO operations (undo, parsing)
- **Queue**: FIFO operations (scheduling, BFS)
- **Hash Table**: Fast lookup, caching
- **BST**: Sorted data, range queries
- **Heap**: Priority queue, top-K problems

## 🛠️ Yêu cầu hệ thống

- **Python**: 3.6+
- **Libraries**: Chỉ sử dụng standard library (collections, heapq, time, random, etc.)
- **Memory**: Tối thiểu 512MB RAM để chạy các test lớn
- **OS**: Windows, macOS, Linux

## 📝 Ghi chú

1. **Code Quality**: Tất cả code đều có docstring và comments chi tiết
2. **Testing**: Mỗi file có section test với multiple test cases
3. **Performance**: Các thuật toán được benchmark và so sánh
4. **Educational**: Code được viết để dễ hiểu, không tối ưu hóa quá mức
5. **Real-world Examples**: Mỗi cấu trúc dữ liệu có ví dụ ứng dụng thực tế

## 🔗 Tài liệu tham khảo

- **Sách**: "Introduction to Algorithms" (CLRS)
- **Online**: [VisuAlgo](https://visualgo.net) - Visualization tool
- **Practice**: [LeetCode](https://leetcode.com), [HackerRank](https://hackerrank.com)
- **Big O**: [BigO CheatSheet](https://www.bigocheatsheet.com)

---

*Được tạo như một tài liệu học tập có cấu trúc cho người mới bắt đầu quan tâm đến Data Structures và Algorithms.*
