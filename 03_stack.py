"""
Cấu trúc dữ liệu: Stack (Ngăn xếp)
LIFO - Last In, First Out
Ứng dụng: kiểm tra dấu ngoặc, undo feature, đánh giá biểu thức
"""

class Stack:
    """Cài đặt Stack sử dụng list"""
    def __init__(self):
        self.items = []
    
    def push(self, item):
        """
        Thêm phần tử vào đỉnh stack
        Input: item = 5
        Output: Stack = [1, 2, 3, 5] (5 ở đỉnh)
        """
        self.items.append(item)
    
    def pop(self):
        """
        Lấy và xóa phần tử ở đỉnh stack
        Input: Stack = [1, 2, 3, 5]
        Output: 5, Stack = [1, 2, 3]
        """
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items.pop()
    
    def peek(self):
        """
        Xem phần tử ở đỉnh stack mà không xóa
        Input: Stack = [1, 2, 3]
        Output: 3
        """
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self.items[-1]
    
    def is_empty(self):
        """
        Kiểm tra stack có rỗng không
        Output: True/False
        """
        return len(self.items) == 0
    
    def size(self):
        """
        Trả về kích thước stack
        Output: số lượng phần tử
        """
        return len(self.items)
    
    def display(self):
        """
        Hiển thị stack (đỉnh ở bên phải)
        Output: [1, 2, 3, 4] <- top
        """
        return self.items.copy()

def is_valid_parentheses(s):
    """
    Kiểm tra dấu ngoặc có hợp lệ không
    Input: s = "({[]})"
    Output: True
    
    Input: s = "({[})"  
    Output: False
    """
    stack = Stack()
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            # Nếu là dấu đóng
            if stack.is_empty():
                return False
            
            top_element = stack.pop()
            if mapping[char] != top_element:
                return False
        else:
            # Nếu là dấu mở
            stack.push(char)
    
    return stack.is_empty()

def evaluate_postfix(expression):
    """
    Đánh giá biểu thức hậu tố (Postfix)
    Input: expression = "2 3 1 * + 9 -"
    Nghĩa là: 2 + (3 * 1) - 9 = 2 + 3 - 9 = -4
    Output: -4
    """
    stack = Stack()
    tokens = expression.split()
    
    for token in tokens:
        if token in ['+', '-', '*', '/']:
            # Lấy hai toán hạng
            if stack.size() < 2:
                raise ValueError("Invalid postfix expression")
            
            b = stack.pop()
            a = stack.pop()
            
            if token == '+':
                result = a + b
            elif token == '-':
                result = a - b
            elif token == '*':
                result = a * b
            elif token == '/':
                if b == 0:
                    raise ValueError("Division by zero")
                result = a / b
            
            stack.push(result)
        else:
            # Số
            try:
                stack.push(float(token))
            except ValueError:
                raise ValueError(f"Invalid token: {token}")
    
    if stack.size() != 1:
        raise ValueError("Invalid postfix expression")
    
    return stack.pop()

def decimal_to_binary(n):
    """
    Chuyển đổi số thập phân sang nhị phân sử dụng stack
    Input: n = 23
    Output: "10111"
    """
    if n == 0:
        return "0"
    
    stack = Stack()
    
    while n > 0:
        remainder = n % 2
        stack.push(remainder)
        n = n // 2
    
    binary = ""
    while not stack.is_empty():
        binary += str(stack.pop())
    
    return binary

def reverse_string(s):
    """
    Đảo ngược chuỗi sử dụng stack
    Input: s = "hello"
    Output: "olleh"
    """
    stack = Stack()
    
    # Push tất cả ký tự vào stack
    for char in s:
        stack.push(char)
    
    # Pop để tạo chuỗi đảo ngược
    reversed_str = ""
    while not stack.is_empty():
        reversed_str += stack.pop()
    
    return reversed_str

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Stack Operations Demo ===")
    
    # Tạo stack và thêm phần tử
    stack = Stack()
    print("Pushing elements: 1, 2, 3, 4, 5")
    for i in range(1, 6):
        stack.push(i)
    
    print(f"Stack: {stack.display()} <- top")
    print(f"Size: {stack.size()}")
    print(f"Top element (peek): {stack.peek()}")
    
    # Pop phần tử
    print(f"\nPopping elements:")
    while not stack.is_empty():
        popped = stack.pop()
        print(f"Popped: {popped}, Stack: {stack.display()}")
    
    # Kiểm tra dấu ngoặc
    print(f"\n=== Parentheses Validation ===")
    test_cases = ["()", "()[]{}", "({[]})", "([)]", "((", "))", ""]
    for case in test_cases:
        result = is_valid_parentheses(case)
        print(f"'{case}' -> {result}")
    
    # Đánh giá biểu thức postfix
    print(f"\n=== Postfix Evaluation ===")
    expressions = [
        "2 3 1 * + 9 -",  # 2 + (3 * 1) - 9 = -4
        "4 13 5 / +",      # 4 + (13 / 5) = 6.6
        "10 6 9 3 + -11 * / * 17 + 5 +"  # Phức tạp hơn
    ]
    
    for expr in expressions:
        try:
            result = evaluate_postfix(expr)
            print(f"'{expr}' = {result}")
        except Exception as e:
            print(f"'{expr}' -> Error: {e}")
    
    # Chuyển đổi thập phân sang nhị phân
    print(f"\n=== Decimal to Binary Conversion ===")
    numbers = [0, 1, 23, 42, 255]
    for num in numbers:
        binary = decimal_to_binary(num)
        print(f"{num} -> {binary}")
    
    # Đảo ngược chuỗi
    print(f"\n=== String Reversal ===")
    strings = ["hello", "world", "stack", "Python"]
    for s in strings:
        reversed_s = reverse_string(s)
        print(f"'{s}' -> '{reversed_s}'")
