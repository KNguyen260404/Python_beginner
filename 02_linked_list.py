"""
Cấu trúc dữ liệu: Linked List (Danh sách liên kết)
Các thao tác: thêm, xóa, đảo ngược, gộp hai danh sách
"""

class Node:
    """Nút trong danh sách liên kết"""
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    """Danh sách liên kết đơn"""
    def __init__(self):
        self.head = None
    
    def append(self, data):
        """
        Thêm phần tử vào cuối danh sách
        Input: data = 5
        Output: Thêm node với giá trị 5 vào cuối
        """
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def prepend(self, data):
        """
        Thêm phần tử vào đầu danh sách
        Input: data = 1
        Output: Thêm node với giá trị 1 vào đầu
        """
        new_node = Node(data)
        new_node.next = self.head
        self.head = new_node
    
    def delete(self, data):
        """
        Xóa node có giá trị data
        Input: data = 3
        Output: Xóa node đầu tiên có giá trị 3
        """
        if not self.head:
            return
        
        if self.head.data == data:
            self.head = self.head.next
            return
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return
            current = current.next
    
    def reverse(self):
        """
        Đảo ngược danh sách liên kết
        Input: 1 -> 2 -> 3 -> None
        Output: 3 -> 2 -> 1 -> None
        """
        prev = None
        current = self.head
        
        while current:
            next_temp = current.next
            current.next = prev
            prev = current
            current = next_temp
        
        self.head = prev
    
    def display(self):
        """
        Hiển thị danh sách
        Output: [1, 2, 3, 4]
        """
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements
    
    def find(self, data):
        """
        Tìm kiếm phần tử trong danh sách
        Input: data = 3
        Output: True nếu tìm thấy, False nếu không
        """
        current = self.head
        while current:
            if current.data == data:
                return True
            current = current.next
        return False
    
    def length(self):
        """
        Tính độ dài danh sách
        Output: số lượng node trong danh sách
        """
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count

def merge_sorted_lists(list1, list2):
    """
    Gộp hai danh sách đã sắp xếp
    Input: list1 = [1, 3, 5], list2 = [2, 4, 6]
    Output: [1, 2, 3, 4, 5, 6]
    """
    merged = LinkedList()
    
    # Chuyển đổi danh sách thành linked list
    ll1 = LinkedList()
    ll2 = LinkedList()
    
    for item in list1:
        ll1.append(item)
    for item in list2:
        ll2.append(item)
    
    # Gộp hai linked list
    current1 = ll1.head
    current2 = ll2.head
    
    while current1 and current2:
        if current1.data <= current2.data:
            merged.append(current1.data)
            current1 = current1.next
        else:
            merged.append(current2.data)
            current2 = current2.next
    
    # Thêm các phần tử còn lại
    while current1:
        merged.append(current1.data)
        current1 = current1.next
    
    while current2:
        merged.append(current2.data)
        current2 = current2.next
    
    return merged.display()

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Linked List Operations Demo ===")
    
    # Tạo danh sách liên kết
    ll = LinkedList()
    
    # Thêm phần tử
    print("Adding elements: 1, 2, 3, 4, 5")
    for i in range(1, 6):
        ll.append(i)
    
    print(f"List after adding: {ll.display()}")
    print(f"Length: {ll.length()}")
    
    # Thêm vào đầu
    print("\nPrepending 0:")
    ll.prepend(0)
    print(f"List: {ll.display()}")
    
    # Tìm kiếm
    search_value = 3
    found = ll.find(search_value)
    print(f"\nSearching for {search_value}: {'Found' if found else 'Not found'}")
    
    # Xóa phần tử
    print(f"\nDeleting element 3:")
    ll.delete(3)
    print(f"List after deletion: {ll.display()}")
    
    # Đảo ngược
    print(f"\nReversing the list:")
    ll.reverse()
    print(f"Reversed list: {ll.display()}")
    
    # Gộp hai danh sách đã sắp xếp
    print(f"\nMerging two sorted lists:")
    list1 = [1, 3, 5, 7]
    list2 = [2, 4, 6, 8]
    merged = merge_sorted_lists(list1, list2)
    print(f"List 1: {list1}")
    print(f"List 2: {list2}")
    print(f"Merged: {merged}")
