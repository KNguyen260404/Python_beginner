"""
Cấu trúc dữ liệu: Queue (Hàng đợi)
FIFO - First In, First Out
Ứng dụng: lập lịch tác vụ, BFS trong đồ thị, xử lý buffer
"""

from collections import deque

class Queue:
    """Cài đặt Queue sử dụng deque để hiệu quả hơn"""
    def __init__(self):
        self.items = deque()
    
    def enqueue(self, item):
        """
        Thêm phần tử vào cuối queue
        Input: item = 5
        Output: Queue = [1, 2, 3, 5] (1 ở đầu, 5 ở cuối)
        """
        self.items.append(item)
    
    def dequeue(self):
        """
        Lấy và xóa phần tử ở đầu queue
        Input: Queue = [1, 2, 3, 5]
        Output: 1, Queue = [2, 3, 5]
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items.popleft()
    
    def front(self):
        """
        Xem phần tử ở đầu queue mà không xóa
        Input: Queue = [2, 3, 5]
        Output: 2
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items[0]
    
    def rear(self):
        """
        Xem phần tử ở cuối queue mà không xóa
        Input: Queue = [2, 3, 5]
        Output: 5
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self.items[-1]
    
    def is_empty(self):
        """
        Kiểm tra queue có rỗng không
        Output: True/False
        """
        return len(self.items) == 0
    
    def size(self):
        """
        Trả về kích thước queue
        Output: số lượng phần tử
        """
        return len(self.items)
    
    def display(self):
        """
        Hiển thị queue (đầu ở bên trái, cuối ở bên phải)
        Output: [1, 2, 3, 4] -> front...rear
        """
        return list(self.items)

class CircularQueue:
    """Circular Queue (Hàng đợi vòng) với kích thước cố định"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = -1
        self.rear = -1
        self.size = 0
    
    def enqueue(self, item):
        """
        Thêm phần tử vào circular queue
        Input: item = 5 (capacity = 4)
        """
        if self.is_full():
            raise OverflowError("Queue is full")
        
        if self.front == -1:  # Queue rỗng
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.capacity
        
        self.queue[self.rear] = item
        self.size += 1
    
    def dequeue(self):
        """
        Lấy phần tử từ circular queue
        """
        if self.is_empty():
            raise IndexError("Queue is empty")
        
        item = self.queue[self.front]
        self.queue[self.front] = None
        
        if self.size == 1:  # Chỉ còn 1 phần tử
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        
        self.size -= 1
        return item
    
    def is_empty(self):
        return self.size == 0
    
    def is_full(self):
        return self.size == self.capacity
    
    def display(self):
        if self.is_empty():
            return []
        
        result = []
        i = self.front
        for _ in range(self.size):
            result.append(self.queue[i])
            i = (i + 1) % self.capacity
        return result

def simulate_print_queue():
    """
    Mô phỏng hàng đợi in ấn
    Input: Các tác vụ in với độ ưu tiên
    Output: Thứ tự xử lý các tác vụ
    """
    print("=== Print Queue Simulation ===")
    
    queue = Queue()
    
    # Thêm các tác vụ in
    tasks = [
        "Document1.pdf",
        "Photo.jpg", 
        "Report.docx",
        "Presentation.pptx",
        "Invoice.pdf"
    ]
    
    print("Adding print tasks:")
    for task in tasks:
        queue.enqueue(task)
        print(f"  Added: {task}")
    
    print(f"\nQueue status: {queue.display()}")
    print(f"Queue size: {queue.size()}")
    
    print("\nProcessing print tasks:")
    while not queue.is_empty():
        current_task = queue.dequeue()
        print(f"  Processing: {current_task}")
        print(f"  Remaining queue: {queue.display()}")
    
    return "All tasks completed!"

def breadth_first_search_demo():
    """
    Demo BFS sử dụng Queue
    Input: Đồ thị dạng adjacency list
    Output: Thứ tự duyệt BFS
    """
    # Đồ thị mẫu
    graph = {
        'A': ['B', 'C'],
        'B': ['A', 'D', 'E'],
        'C': ['A', 'F'],
        'D': ['B'],
        'E': ['B', 'F'],
        'F': ['C', 'E']
    }
    
    def bfs(graph, start):
        """
        Breadth-First Search
        Input: graph, start_node = 'A'
        Output: ['A', 'B', 'C', 'D', 'E', 'F']
        """
        visited = set()
        queue = Queue()
        result = []
        
        queue.enqueue(start)
        visited.add(start)
        
        while not queue.is_empty():
            vertex = queue.dequeue()
            result.append(vertex)
            
            # Thêm các đỉnh kề chưa được thăm
            for neighbor in graph.get(vertex, []):
                if neighbor not in visited:
                    queue.enqueue(neighbor)
                    visited.add(neighbor)
        
        return result
    
    print("=== BFS Demo ===")
    print(f"Graph: {graph}")
    
    start_node = 'A'
    bfs_result = bfs(graph, start_node)
    print(f"BFS traversal from '{start_node}': {bfs_result}")
    
    return bfs_result

def hot_potato_game(names, num):
    """
    Trò chơi "Hot Potato" sử dụng Queue
    Input: names = ["Alice", "Bob", "Charlie", "David"], num = 3
    Output: Thứ tự loại bỏ và người chiến thắng
    """
    queue = Queue()
    
    # Thêm tất cả người chơi vào queue
    for name in names:
        queue.enqueue(name)
    
    eliminated = []
    
    while queue.size() > 1:
        # Chuyển "khoai tây nóng" num lần
        for _ in range(num):
            person = queue.dequeue()
            queue.enqueue(person)
        
        # Loại bỏ người đang cầm "khoai tây nóng"
        eliminated_person = queue.dequeue()
        eliminated.append(eliminated_person)
        print(f"  {eliminated_person} is eliminated!")
        print(f"  Remaining players: {queue.display()}")
    
    winner = queue.dequeue()
    return eliminated, winner

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Queue Operations Demo ===")
    
    # Tạo queue và thêm phần tử
    queue = Queue()
    print("Enqueueing elements: 1, 2, 3, 4, 5")
    for i in range(1, 6):
        queue.enqueue(i)
    
    print(f"Queue: {queue.display()} (front -> rear)")
    print(f"Size: {queue.size()}")
    print(f"Front element: {queue.front()}")
    print(f"Rear element: {queue.rear()}")
    
    # Dequeue phần tử
    print(f"\nDequeueing elements:")
    while not queue.is_empty():
        dequeued = queue.dequeue()
        print(f"Dequeued: {dequeued}, Queue: {queue.display()}")
    
    # Circular Queue
    print(f"\n=== Circular Queue Demo ===")
    cqueue = CircularQueue(4)
    
    print("Adding elements to circular queue (capacity=4):")
    for i in range(1, 5):
        cqueue.enqueue(i)
        print(f"  Added {i}: {cqueue.display()}")
    
    print(f"Queue is full: {cqueue.is_full()}")
    
    print("\nRemoving 2 elements:")
    for _ in range(2):
        removed = cqueue.dequeue()
        print(f"  Removed {removed}: {cqueue.display()}")
    
    print("Adding 2 more elements:")
    for i in range(5, 7):
        cqueue.enqueue(i)
        print(f"  Added {i}: {cqueue.display()}")
    
    # Print Queue Simulation
    print(f"\n{simulate_print_queue()}")
    
    # BFS Demo
    print(f"\n{breadth_first_search_demo()}")
    
    # Hot Potato Game
    print(f"\n=== Hot Potato Game ===")
    players = ["Alice", "Bob", "Charlie", "David", "Eve"]
    pass_count = 3
    
    print(f"Players: {players}")
    print(f"Pass count: {pass_count}")
    print("Game starts!")
    
    eliminated, winner = hot_potato_game(players, pass_count)
    print(f"\nElimination order: {eliminated}")
    print(f"Winner: {winner}! 🎉")
