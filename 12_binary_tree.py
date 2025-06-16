"""
Cấu trúc dữ liệu: Binary Tree (Cây nhị phân)
Mỗi node có tối đa 2 con: left và right
Các phép duyệt: Preorder, Inorder, Postorder, Level-order
Ứng dụng: expression trees, binary search trees, heap
"""

from collections import deque

class TreeNode:
    """Node trong cây nhị phân"""
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right
    
    def __str__(self):
        return str(self.val)

class BinaryTree:
    """Cây nhị phân với các phép toán cơ bản"""
    
    def __init__(self, root=None):
        self.root = root
    
    def preorder_traversal(self, node=None):
        """
        Duyệt theo thứ tự trước (Root -> Left -> Right)
        Input: Tree với root = 1, left = 2, right = 3
        Output: [1, 2, 3]
        
        Time Complexity: O(n)
        Space Complexity: O(h) với h là chiều cao cây
        """
        if node is None:
            node = self.root
        
        result = []
        
        def preorder_helper(node):
            if node:
                result.append(node.val)          # Root
                preorder_helper(node.left)       # Left
                preorder_helper(node.right)      # Right
        
        preorder_helper(node)
        return result
    
    def inorder_traversal(self, node=None):
        """
        Duyệt theo thứ tự giữa (Left -> Root -> Right)
        Input: BST với root = 2, left = 1, right = 3
        Output: [1, 2, 3] (sorted order for BST)
        
        Time Complexity: O(n)
        Space Complexity: O(h)
        """
        if node is None:
            node = self.root
        
        result = []
        
        def inorder_helper(node):
            if node:
                inorder_helper(node.left)        # Left
                result.append(node.val)          # Root
                inorder_helper(node.right)       # Right
        
        inorder_helper(node)
        return result
    
    def postorder_traversal(self, node=None):
        """
        Duyệt theo thứ tự sau (Left -> Right -> Root)
        Input: Tree với root = 1, left = 2, right = 3
        Output: [2, 3, 1]
        
        Time Complexity: O(n)
        Space Complexity: O(h)
        """
        if node is None:
            node = self.root
        
        result = []
        
        def postorder_helper(node):
            if node:
                postorder_helper(node.left)      # Left
                postorder_helper(node.right)     # Right
                result.append(node.val)          # Root
        
        postorder_helper(node)
        return result
    
    def level_order_traversal(self):
        """
        Duyệt theo mức (BFS - Breadth First Search)
        Input: Tree với các level khác nhau
        Output: [[root], [level1_nodes], [level2_nodes], ...]
        
        Time Complexity: O(n)
        Space Complexity: O(w) với w là width lớn nhất của cây
        """
        if not self.root:
            return []
        
        result = []
        queue = deque([self.root])
        
        while queue:
            level_size = len(queue)
            current_level = []
            
            for _ in range(level_size):
                node = queue.popleft()
                current_level.append(node.val)
                
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            
            result.append(current_level)
        
        return result
    
    def height(self, node=None):
        """
        Tính chiều cao của cây
        Input: Cây nhị phân
        Output: Chiều cao (số level - 1)
        
        Time Complexity: O(n)
        Space Complexity: O(h)
        """
        if node is None:
            node = self.root
        
        if node is None:
            return -1
        
        left_height = self.height(node.left)
        right_height = self.height(node.right)
        
        return max(left_height, right_height) + 1
    
    def count_nodes(self, node=None):
        """
        Đếm tổng số node trong cây
        Input: Cây nhị phân
        Output: Số lượng node
        """
        if node is None:
            node = self.root
        
        if node is None:
            return 0
        
        return 1 + self.count_nodes(node.left) + self.count_nodes(node.right)
    
    def count_leaf_nodes(self, node=None):
        """
        Đếm số node lá (node không có con)
        Input: Cây nhị phân
        Output: Số node lá
        """
        if node is None:
            node = self.root
        
        if node is None:
            return 0
        
        if node.left is None and node.right is None:
            return 1
        
        return self.count_leaf_nodes(node.left) + self.count_leaf_nodes(node.right)
    
    def find_max(self, node=None):
        """
        Tìm giá trị lớn nhất trong cây
        Input: Cây nhị phân
        Output: Giá trị lớn nhất
        """
        if node is None:
            node = self.root
        
        if node is None:
            return None
        
        max_val = node.val
        
        left_max = self.find_max(node.left)
        right_max = self.find_max(node.right)
        
        if left_max is not None:
            max_val = max(max_val, left_max)
        if right_max is not None:
            max_val = max(max_val, right_max)
        
        return max_val
    
    def find_min(self, node=None):
        """
        Tìm giá trị nhỏ nhất trong cây
        Input: Cây nhị phân
        Output: Giá trị nhỏ nhất
        """
        if node is None:
            node = self.root
        
        if node is None:
            return None
        
        min_val = node.val
        
        left_min = self.find_min(node.left)
        right_min = self.find_min(node.right)
        
        if left_min is not None:
            min_val = min(min_val, left_min)
        if right_min is not None:
            min_val = min(min_val, right_min)
        
        return min_val
    
    def search(self, target, node=None):
        """
        Tìm kiếm một giá trị trong cây
        Input: target = 5
        Output: True nếu tìm thấy, False nếu không
        """
        if node is None:
            node = self.root
        
        if node is None:
            return False
        
        if node.val == target:
            return True
        
        return self.search(target, node.left) or self.search(target, node.right)
    
    def is_balanced(self, node=None):
        """
        Kiểm tra cây có cân bằng không
        Cây cân bằng: chênh lệch chiều cao giữa cây con trái và phải <= 1
        """
        if node is None:
            node = self.root
        
        def check_balance(node):
            if node is None:
                return True, -1
            
            left_balanced, left_height = check_balance(node.left)
            right_balanced, right_height = check_balance(node.right)
            
            balanced = (left_balanced and right_balanced and 
                       abs(left_height - right_height) <= 1)
            height = max(left_height, right_height) + 1
            
            return balanced, height
        
        balanced, _ = check_balance(node)
        return balanced
    
    def diameter(self, node=None):
        """
        Tính đường kính của cây (đường đi dài nhất giữa 2 node bất kỳ)
        Input: Cây nhị phân
        Output: Độ dài đường kính
        """
        if node is None:
            node = self.root
        
        self.max_diameter = 0
        
        def diameter_helper(node):
            if node is None:
                return 0
            
            left_height = diameter_helper(node.left)
            right_height = diameter_helper(node.right)
            
            # Đường kính tại node hiện tại
            current_diameter = left_height + right_height
            self.max_diameter = max(self.max_diameter, current_diameter)
            
            return max(left_height, right_height) + 1
        
        diameter_helper(node)
        return self.max_diameter
    
    def print_tree(self, node=None, level=0, prefix="Root: "):
        """
        In cây theo dạng cây đẹp
        """
        if node is None:
            node = self.root
        
        if node is not None:
            print(" " * (level * 4) + prefix + str(node.val))
            if node.left is not None or node.right is not None:
                if node.left:
                    self.print_tree(node.left, level + 1, "L--- ")
                else:
                    print(" " * ((level + 1) * 4) + "L--- None")
                if node.right:
                    self.print_tree(node.right, level + 1, "R--- ")
                else:
                    print(" " * ((level + 1) * 4) + "R--- None")

class BinarySearchTree(BinaryTree):
    """
    Binary Search Tree (BST) - Cây tìm kiếm nhị phân
    Tính chất: Left subtree < Root < Right subtree
    """
    
    def insert(self, val):
        """
        Chèn giá trị vào BST
        Input: val = 5
        Output: Chèn vào vị trí đúng để duy trì tính chất BST
        
        Time Complexity: O(h) với h là chiều cao cây
        """
        def insert_helper(node, val):
            if node is None:
                return TreeNode(val)
            
            if val < node.val:
                node.left = insert_helper(node.left, val)
            elif val > node.val:
                node.right = insert_helper(node.right, val)
            
            return node
        
        self.root = insert_helper(self.root, val)
    
    def search_bst(self, val):
        """
        Tìm kiếm trong BST (hiệu quả hơn search thông thường)
        Input: val = 5
        Output: True nếu tìm thấy
        
        Time Complexity: O(h)
        """
        def search_helper(node, val):
            if node is None:
                return False
            
            if node.val == val:
                return True
            elif val < node.val:
                return search_helper(node.left, val)
            else:
                return search_helper(node.right, val)
        
        return search_helper(self.root, val)
    
    def find_min_bst(self):
        """
        Tìm giá trị nhỏ nhất trong BST (node trái nhất)
        Time Complexity: O(h)
        """
        if self.root is None:
            return None
        
        current = self.root
        while current.left:
            current = current.left
        
        return current.val
    
    def find_max_bst(self):
        """
        Tìm giá trị lớn nhất trong BST (node phải nhất)
        Time Complexity: O(h)
        """
        if self.root is None:
            return None
        
        current = self.root
        while current.right:
            current = current.right
        
        return current.val
    
    def delete(self, val):
        """
        Xóa node có giá trị val khỏi BST
        Input: val = 5
        Output: BST sau khi xóa node
        
        Time Complexity: O(h)
        """
        def delete_helper(node, val):
            if node is None:
                return node
            
            if val < node.val:
                node.left = delete_helper(node.left, val)
            elif val > node.val:
                node.right = delete_helper(node.right, val)
            else:
                # Node cần xóa
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left
                
                # Node có 2 con: tìm successor (min trong right subtree)
                successor = node.right
                while successor.left:
                    successor = successor.left
                
                node.val = successor.val
                node.right = delete_helper(node.right, successor.val)
            
            return node
        
        self.root = delete_helper(self.root, val)
    
    def validate_bst(self, node=None, min_val=float('-inf'), max_val=float('inf')):
        """
        Kiểm tra cây có phải BST hợp lệ không
        Input: Cây nhị phân
        Output: True nếu là BST hợp lệ
        """
        if node is None:
            node = self.root
        
        if node is None:
            return True
        
        if node.val <= min_val or node.val >= max_val:
            return False
        
        return (self.validate_bst(node.left, min_val, node.val) and
                self.validate_bst(node.right, node.val, max_val))

def build_tree_from_arrays(preorder, inorder):
    """
    Xây dựng cây từ preorder và inorder traversal
    Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
    Output: TreeNode representing the tree
    """
    if not preorder or not inorder:
        return None
    
    root = TreeNode(preorder[0])
    mid = inorder.index(preorder[0])
    
    root.left = build_tree_from_arrays(preorder[1:mid+1], inorder[:mid])
    root.right = build_tree_from_arrays(preorder[mid+1:], inorder[mid+1:])
    
    return root

def lowest_common_ancestor(root, p, q):
    """
    Tìm tổ tiên chung gần nhất của 2 node
    Input: root, p = node1, q = node2
    Output: LCA node
    """
    if root is None or root == p or root == q:
        return root
    
    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)
    
    if left and right:
        return root
    
    return left if left else right

def serialize_tree(root):
    """
    Serialize cây thành string
    Input: Tree
    Output: "1,2,null,null,3,4,null,null,5,null,null"
    """
    def serialize_helper(node):
        if node is None:
            return "null"
        
        return str(node.val) + "," + serialize_helper(node.left) + "," + serialize_helper(node.right)
    
    return serialize_helper(root)

def deserialize_tree(data):
    """
    Deserialize string thành cây
    Input: "1,2,null,null,3,4,null,null,5,null,null"
    Output: TreeNode
    """
    def deserialize_helper():
        val = next(values)
        if val == "null":
            return None
        
        node = TreeNode(int(val))
        node.left = deserialize_helper()
        node.right = deserialize_helper()
        return node
    
    values = iter(data.split(","))
    return deserialize_helper()

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Binary Tree Operations Demo ===")
    
    # Tạo cây nhị phân mẫu
    #       1
    #      / \\
    #     2   3
    #    / \\
    #   4   5
    
    root = TreeNode(1)
    root.left = TreeNode(2)
    root.right = TreeNode(3)
    root.left.left = TreeNode(4)
    root.left.right = TreeNode(5)
    
    tree = BinaryTree(root)
    
    print("Tree structure:")
    tree.print_tree()
    
    # Các phép duyệt
    print("\\n=== Tree Traversals ===")
    print(f"Preorder:  {tree.preorder_traversal()}")
    print(f"Inorder:   {tree.inorder_traversal()}")
    print(f"Postorder: {tree.postorder_traversal()}")
    print(f"Level-order: {tree.level_order_traversal()}")
    
    # Thông tin về cây
    print(f"\\n=== Tree Information ===")
    print(f"Height: {tree.height()}")
    print(f"Total nodes: {tree.count_nodes()}")
    print(f"Leaf nodes: {tree.count_leaf_nodes()}")
    print(f"Max value: {tree.find_max()}")
    print(f"Min value: {tree.find_min()}")
    print(f"Is balanced: {tree.is_balanced()}")
    print(f"Diameter: {tree.diameter()}")
    
    # Tìm kiếm
    print(f"\\n=== Search Operations ===")
    search_values = [1, 3, 6]
    for val in search_values:
        found = tree.search(val)
        print(f"Search for {val}: {'Found' if found else 'Not found'}")
    
    # Binary Search Tree
    print(f"\\n=== Binary Search Tree Demo ===")
    
    bst = BinarySearchTree()
    values = [50, 30, 70, 20, 40, 60, 80]
    
    print(f"Inserting values: {values}")
    for val in values:
        bst.insert(val)
    
    print("\\nBST structure:")
    bst.print_tree()
    
    print(f"\\nBST Traversals:")
    print(f"Inorder (sorted): {bst.inorder_traversal()}")
    print(f"Preorder: {bst.preorder_traversal()}")
    
    # BST operations
    print(f"\\n=== BST Operations ===")
    print(f"Min value: {bst.find_min_bst()}")
    print(f"Max value: {bst.find_max_bst()}")
    print(f"Is valid BST: {bst.validate_bst()}")
    
    # BST search
    search_values = [40, 25, 75]
    for val in search_values:
        found = bst.search_bst(val)
        print(f"Search for {val}: {'Found' if found else 'Not found'}")
    
    # BST deletion
    print(f"\\nDeleting node with value 30:")
    bst.delete(30)
    print(f"Inorder after deletion: {bst.inorder_traversal()}")
    
    print("\\nBST after deletion:")
    bst.print_tree()
    
    # Build tree from traversals
    print(f"\\n=== Build Tree from Traversals ===")
    preorder = [3, 9, 20, 15, 7]
    inorder = [9, 3, 15, 20, 7]
    
    print(f"Preorder: {preorder}")
    print(f"Inorder: {inorder}")
    
    built_tree = build_tree_from_arrays(preorder, inorder)
    tree_from_arrays = BinaryTree(built_tree)
    
    print("\\nReconstructed tree:")
    tree_from_arrays.print_tree()
    
    print(f"Verification - Preorder: {tree_from_arrays.preorder_traversal()}")
    print(f"Verification - Inorder: {tree_from_arrays.inorder_traversal()}")
    
    # Serialization
    print(f"\\n=== Tree Serialization ===")
    serialized = serialize_tree(tree.root)
    print(f"Serialized: {serialized}")
    
    deserialized_root = deserialize_tree(serialized)
    deserialized_tree = BinaryTree(deserialized_root)
    
    print("\\nDeserialized tree:")
    deserialized_tree.print_tree()
    
    # Performance comparison
    print(f"\\n=== Performance Comparison ===")
    
    # So sánh tìm kiếm trong BST vs Binary Tree
    import time
    import random
    
    # Tạo BST lớn
    large_bst = BinarySearchTree()
    values = list(range(1, 1001))
    random.shuffle(values)
    
    for val in values:
        large_bst.insert(val)
    
    # Test tìm kiếm
    search_target = 500
    
    # BST search
    start_time = time.time()
    found_bst = large_bst.search_bst(search_target)
    bst_time = time.time() - start_time
    
    # Regular tree search
    start_time = time.time()
    found_tree = large_bst.search(search_target)
    tree_time = time.time() - start_time
    
    print(f"Search for {search_target} in tree with 1000 nodes:")
    print(f"  BST search: {bst_time:.6f} seconds")
    print(f"  Tree search: {tree_time:.6f} seconds")
    print(f"  BST is {tree_time/bst_time:.1f}x faster")
