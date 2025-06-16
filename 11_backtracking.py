"""
Thuật toán Backtracking (Quay lui)
Thử tất cả các khả năng và quay lại khi gặp đường cụt
Ứng dụng: N-Queens, Sudoku, tìm đường đi, subset sum
"""

def solve_n_queens(n):
    """
    Bài toán N-Queens: Đặt N quân hậu trên bàn cờ NxN
    sao cho không có quân nào tấn công được quân khác
    
    Input: n = 4
    Output: Các cách đặt hậu hợp lệ
    
    Time Complexity: O(N!)
    Space Complexity: O(N)
    """
    def is_safe(board, row, col):
        """Kiểm tra vị trí (row, col) có an toàn không"""
        # Kiểm tra cột
        for i in range(row):
            if board[i][col] == 1:
                return False
        
        # Kiểm tra đường chéo trái
        for i, j in zip(range(row-1, -1, -1), range(col-1, -1, -1)):
            if board[i][j] == 1:
                return False
        
        # Kiểm tra đường chéo phải
        for i, j in zip(range(row-1, -1, -1), range(col+1, n)):
            if board[i][j] == 1:
                return False
        
        return True
    
    def solve_queens(board, row):
        """Đệ quy giải N-Queens"""
        # Base case: đã đặt được tất cả hậu
        if row >= n:
            return True
        
        # Thử đặt hậu ở mỗi cột của hàng hiện tại
        for col in range(n):
            if is_safe(board, row, col):
                # Đặt hậu
                board[row][col] = 1
                
                # Đệ quy giải hàng tiếp theo
                if solve_queens(board, row + 1):
                    return True
                
                # Backtrack: bỏ hậu nếu không có giải pháp
                board[row][col] = 0
        
        return False
    
    def find_all_solutions(board, row, solutions):
        """Tìm tất cả các giải pháp"""
        if row >= n:
            # Tìm được một giải pháp, lưu lại
            solutions.append([row[:] for row in board])
            return
        
        for col in range(n):
            if is_safe(board, row, col):
                board[row][col] = 1
                find_all_solutions(board, row + 1, solutions)
                board[row][col] = 0  # Backtrack
    
    # Tìm tất cả giải pháp
    board = [[0 for _ in range(n)] for _ in range(n)]
    solutions = []
    find_all_solutions(board, 0, solutions)
    
    return solutions

def solve_sudoku(board):
    """
    Giải Sudoku 9x9
    Input: board - ma trận 9x9 với 0 là ô trống
    Output: True nếu có giải pháp, False nếu không
    
    Time Complexity: O(9^(n*n)) trong trường hợp xấu nhất
    """
    def is_valid(board, row, col, num):
        """Kiểm tra số num có thể đặt tại (row, col) không"""
        # Kiểm tra hàng
        for j in range(9):
            if board[row][j] == num:
                return False
        
        # Kiểm tra cột
        for i in range(9):
            if board[i][col] == num:
                return False
        
        # Kiểm tra ô 3x3
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        
        return True
    
    def solve():
        """Giải Sudoku bằng backtracking"""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    # Thử các số từ 1 đến 9
                    for num in range(1, 10):
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            
                            if solve():
                                return True
                            
                            # Backtrack
                            board[i][j] = 0
                    
                    return False
        return True
    
    return solve()

def subset_sum(arr, target_sum):
    """
    Tìm tập con có tổng bằng target_sum
    Input: arr = [3, 34, 4, 12, 5, 2], target_sum = 9
    Output: [4, 5] hoặc [3, 4, 2]
    
    Time Complexity: O(2^n)
    """
    def backtrack(index, current_sum, current_subset):
        # Base case: tìm thấy giải pháp
        if current_sum == target_sum:
            return current_subset[:]
        
        # Base case: vượt quá tổng hoặc hết phần tử
        if current_sum > target_sum or index >= len(arr):
            return None
        
        # Thử bao gồm phần tử hiện tại
        current_subset.append(arr[index])
        result = backtrack(index + 1, current_sum + arr[index], current_subset)
        if result is not None:
            return result
        
        # Backtrack: không bao gồm phần tử hiện tại
        current_subset.pop()
        return backtrack(index + 1, current_sum, current_subset)
    
    return backtrack(0, 0, [])

def generate_parentheses(n):
    """
    Sinh tất cả các chuỗi dấu ngoặc hợp lệ với n cặp ngoặc
    Input: n = 3
    Output: ["((()))", "(()())", "(())()", "()(())", "()()()"]
    
    Time Complexity: O(4^n / √n) - Catalan number
    """
    def backtrack(current, open_count, close_count):
        # Base case: đã sử dụng hết n cặp ngoặc
        if len(current) == 2 * n:
            results.append(current)
            return
        
        # Thêm ngoặc mở nếu còn có thể
        if open_count < n:
            backtrack(current + "(", open_count + 1, close_count)
        
        # Thêm ngoặc đóng nếu có thể
        if close_count < open_count:
            backtrack(current + ")", open_count, close_count + 1)
    
    results = []
    backtrack("", 0, 0)
    return results

def solve_maze(maze):
    """
    Tìm đường đi trong mê cung
    Input: maze - ma trận với 0 là đường đi, 1 là tường
    Output: ma trận path với 1 là đường đi tìm được
    
    Time Complexity: O(4^(n*m))
    """
    rows, cols = len(maze), len(maze[0])
    path = [[0 for _ in range(cols)] for _ in range(rows)]
    
    def is_safe(x, y):
        """Kiểm tra ô (x, y) có thể đi được không"""
        return (0 <= x < rows and 0 <= y < cols and 
                maze[x][y] == 0 and path[x][y] == 0)
    
    def solve(x, y):
        """Tìm đường từ (x, y) đến (rows-1, cols-1)"""
        # Base case: đến đích
        if x == rows - 1 and y == cols - 1:
            path[x][y] = 1
            return True
        
        # Kiểm tra ô hiện tại có hợp lệ không
        if is_safe(x, y):
            path[x][y] = 1
            
            # Di chuyển theo 4 hướng
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
            
            for dx, dy in directions:
                if solve(x + dx, y + dy):
                    return True
            
            # Backtrack
            path[x][y] = 0
            return False
        
        return False
    
    if solve(0, 0):
        return path
    else:
        return None

def word_search(board, word):
    """
    Tìm từ trong bảng ký tự 2D
    Input: board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
           word = "ABCCED"
    Output: True
    
    Time Complexity: O(N * M * 4^L) với L là độ dài từ
    """
    def backtrack(x, y, index):
        # Base case: tìm được từ hoàn chỉnh
        if index == len(word):
            return True
        
        # Kiểm tra biên và ký tự
        if (x < 0 or x >= len(board) or y < 0 or y >= len(board[0]) or
            board[x][y] != word[index]):
            return False
        
        # Lưu ký tự hiện tại và đánh dấu đã sử dụng
        temp = board[x][y]
        board[x][y] = '#'
        
        # Thử 4 hướng
        found = (backtrack(x + 1, y, index + 1) or
                backtrack(x - 1, y, index + 1) or
                backtrack(x, y + 1, index + 1) or
                backtrack(x, y - 1, index + 1))
        
        # Backtrack: khôi phục ký tự
        board[x][y] = temp
        
        return found
    
    # Thử từ mỗi ô
    for i in range(len(board)):
        for j in range(len(board[0])):
            if backtrack(i, j, 0):
                return True
    
    return False

def permute_unique(nums):
    """
    Sinh hoán vị của mảng có thể có phần tử trùng lặp
    Input: nums = [1, 1, 2]
    Output: [[1,1,2], [1,2,1], [2,1,1]]
    
    Time Complexity: O(N! * N)
    """
    def backtrack(current_perm):
        if len(current_perm) == len(nums):
            results.append(current_perm[:])
            return
        
        for i in range(len(nums)):
            # Bỏ qua phần tử đã sử dụng
            if used[i]:
                continue
            
            # Bỏ qua trùng lặp: nếu nums[i] == nums[i-1] và nums[i-1] chưa dùng
            if i > 0 and nums[i] == nums[i-1] and not used[i-1]:
                continue
            
            used[i] = True
            current_perm.append(nums[i])
            backtrack(current_perm)
            
            # Backtrack
            current_perm.pop()
            used[i] = False
    
    nums.sort()  # Sắp xếp để xử lý trùng lặp
    results = []
    used = [False] * len(nums)
    backtrack([])
    return results

def combination_sum(candidates, target):
    """
    Tìm tất cả tổ hợp có tổng bằng target
    Input: candidates = [2,3,6,7], target = 7
    Output: [[2,2,3], [7]]
    
    Time Complexity: O(N^(T/M)) với T=target, M=min(candidates)
    """
    def backtrack(remaining, current_combination, start):
        # Base case: tìm được tổ hợp
        if remaining == 0:
            results.append(current_combination[:])
            return
        
        # Thử từng ứng viên
        for i in range(start, len(candidates)):
            if candidates[i] <= remaining:
                current_combination.append(candidates[i])
                # Có thể sử dụng lại cùng số (i, không phải i+1)
                backtrack(remaining - candidates[i], current_combination, i)
                # Backtrack
                current_combination.pop()
    
    results = []
    candidates.sort()
    backtrack(target, [], 0)
    return results

def print_board(board):
    """In bàn cờ/ma trận đẹp"""
    for row in board:
        print(" ".join(str(cell) for cell in row))
    print()

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Backtracking Algorithms Demo ===")
    
    # N-Queens
    print("=== N-Queens Problem ===")
    n = 4
    solutions = solve_n_queens(n)
    print(f"Solutions for {n}-Queens problem: {len(solutions)} solutions")
    
    for i, solution in enumerate(solutions[:2]):  # Chỉ hiển thị 2 giải pháp đầu
        print(f"Solution {i+1}:")
        print_board(solution)
    
    # Sudoku
    print("=== Sudoku Solver ===")
    sudoku_board = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    print("Original Sudoku:")
    print_board(sudoku_board)
    
    if solve_sudoku(sudoku_board):
        print("Solved Sudoku:")
        print_board(sudoku_board)
    else:
        print("No solution exists!")
    
    # Subset Sum
    print("=== Subset Sum Problem ===")
    arr = [3, 34, 4, 12, 5, 2]
    target = 9
    result = subset_sum(arr, target)
    print(f"Array: {arr}")
    print(f"Target sum: {target}")
    print(f"Subset with sum {target}: {result}")
    
    # Generate Parentheses
    print("\n=== Generate Parentheses ===")
    n = 3
    parentheses = generate_parentheses(n)
    print(f"All valid parentheses with {n} pairs:")
    for p in parentheses:
        print(f"  {p}")
    
    # Maze Solver
    print("\n=== Maze Solver ===")
    maze = [
        [0, 1, 0, 0, 0],
        [0, 1, 0, 1, 0],
        [0, 0, 0, 1, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 0, 1, 0]
    ]
    
    print("Maze (0=path, 1=wall):")
    print_board(maze)
    
    path = solve_maze(maze)
    if path:
        print("Solution path (1=path taken):")
        print_board(path)
    else:
        print("No path found!")
    
    # Word Search
    print("=== Word Search ===")
    board = [
        ["A", "B", "C", "E"],
        ["S", "F", "C", "S"],
        ["A", "D", "E", "E"]
    ]
    
    words = ["ABCCED", "SEE", "ABCB"]
    
    print("Board:")
    for row in board:
        print(" ".join(row))
    print()
    
    for word in words:
        # Tạo bản sao board để tránh thay đổi
        board_copy = [row[:] for row in board]
        found = word_search(board_copy, word)
        print(f"Word '{word}': {'Found' if found else 'Not found'}")
    
    # Permutations with duplicates
    print("\n=== Unique Permutations ===")
    nums = [1, 1, 2]
    perms = permute_unique(nums)
    print(f"Unique permutations of {nums}:")
    for perm in perms:
        print(f"  {perm}")
    
    # Combination Sum
    print("\n=== Combination Sum ===")
    candidates = [2, 3, 6, 7]
    target = 7
    combinations = combination_sum(candidates, target)
    print(f"Candidates: {candidates}, Target: {target}")
    print(f"Combinations that sum to {target}:")
    for combo in combinations:
        print(f"  {combo} (sum: {sum(combo)})")
    
    # Performance comparison
    print("\n=== Performance Analysis ===")
    
    # N-Queens scaling
    print("N-Queens solutions count:")
    for n in range(1, 9):
        import time
        start_time = time.time()
        solutions = solve_n_queens(n)
        end_time = time.time()
        print(f"  N={n}: {len(solutions)} solutions, Time: {end_time - start_time:.4f}s")
        
        # Dừng nếu quá chậm
        if end_time - start_time > 1.0:
            print("  (Stopping due to long execution time)")
            break
