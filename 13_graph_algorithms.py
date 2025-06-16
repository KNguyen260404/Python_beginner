"""
Thuật toán đồ thị (Graph Algorithms)
1. BFS (Breadth-First Search) - duyệt theo chiều rộng
2. DFS (Depth-First Search) - duyệt theo chiều sâu
3. Shortest path, Connected components, Cycle detection
"""

from collections import deque, defaultdict
import heapq

class Graph:
    """Đồ thị sử dụng adjacency list"""
    
    def __init__(self, directed=False):
        self.graph = defaultdict(list)
        self.directed = directed
    
    def add_edge(self, u, v, weight=1):
        """
        Thêm cạnh giữa đỉnh u và v
        Input: u = 'A', v = 'B', weight = 5
        Output: Thêm cạnh A-B với trọng số 5
        """
        self.graph[u].append((v, weight))
        if not self.directed:
            self.graph[v].append((u, weight))
    
    def add_vertex(self, vertex):
        """Thêm đỉnh vào đồ thị"""
        if vertex not in self.graph:
            self.graph[vertex] = []
    
    def get_vertices(self):
        """Lấy tất cả đỉnh"""
        return list(self.graph.keys())
    
    def get_edges(self):
        """Lấy tất cả cạnh"""
        edges = []
        for u in self.graph:
            for v, weight in self.graph[u]:
                if self.directed or u <= v:  # Tránh trùng lặp với undirected graph
                    edges.append((u, v, weight))
        return edges
    
    def print_graph(self):
        """In đồ thị"""
        for vertex in self.graph:
            neighbors = [f"{v}({w})" for v, w in self.graph[vertex]]
            print(f"{vertex}: {' -> '.join(neighbors)}")

def bfs(graph, start):
    """
    Breadth-First Search (Tìm kiếm theo chiều rộng)
    Input: graph, start = 'A'
    Output: ['A', 'B', 'C', 'D', 'E'] (thứ tự duyệt)
    
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    visited = set()
    queue = deque([start])
    result = []
    
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        
        # Thêm các đỉnh kề chưa thăm
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return result

def dfs(graph, start):
    """
    Depth-First Search (Tìm kiếm theo chiều sâu)
    Input: graph, start = 'A'
    Output: ['A', 'B', 'D', 'E', 'C'] (thứ tự duyệt)
    
    Time Complexity: O(V + E)
    Space Complexity: O(V)
    """
    visited = set()
    result = []
    
    def dfs_helper(vertex):
        visited.add(vertex)
        result.append(vertex)
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                dfs_helper(neighbor)
    
    dfs_helper(start)
    return result

def dfs_iterative(graph, start):
    """
    DFS sử dụng stack (không đệ quy)
    """
    visited = set()
    stack = [start]
    result = []
    
    while stack:
        vertex = stack.pop()
        
        if vertex not in visited:
            visited.add(vertex)
            result.append(vertex)
            
            # Thêm neighbors vào stack (ngược thứ tự để duyệt đúng)
            neighbors = [neighbor for neighbor, _ in graph.graph[vertex]]
            for neighbor in reversed(neighbors):
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return result

def find_shortest_path_bfs(graph, start, end):
    """
    Tìm đường đi ngắn nhất (unweighted graph) sử dụng BFS
    Input: graph, start = 'A', end = 'E'
    Output: ['A', 'B', 'E'] (đường đi ngắn nhất)
    
    Time Complexity: O(V + E)
    """
    if start == end:
        return [start]
    
    visited = set()
    queue = deque([(start, [start])])
    visited.add(start)
    
    while queue:
        vertex, path = queue.popleft()
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor == end:
                return path + [neighbor]
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return None  # Không tìm thấy đường đi

def dijkstra(graph, start):
    """
    Thuật toán Dijkstra - tìm đường đi ngắn nhất có trọng số
    Input: weighted graph, start = 'A'
    Output: {vertex: (distance, path)} cho tất cả đỉnh
    
    Time Complexity: O((V + E) log V)
    Space Complexity: O(V)
    """
    distances = {vertex: float('inf') for vertex in graph.get_vertices()}
    distances[start] = 0
    previous = {}
    
    # Priority queue: (distance, vertex)
    pq = [(0, start)]
    
    while pq:
        current_distance, current_vertex = heapq.heappop(pq)
        
        # Bỏ qua nếu đã có đường đi ngắn hơn
        if current_distance > distances[current_vertex]:
            continue
        
        # Kiểm tra các đỉnh kề
        for neighbor, weight in graph.graph[current_vertex]:
            distance = current_distance + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_vertex
                heapq.heappush(pq, (distance, neighbor))
    
    # Xây dựng đường đi
    paths = {}
    for vertex in graph.get_vertices():
        if distances[vertex] != float('inf'):
            path = []
            current = vertex
            while current is not None:
                path.append(current)
                current = previous.get(current)
            paths[vertex] = (distances[vertex], path[::-1])
        else:
            paths[vertex] = (float('inf'), [])
    
    return paths

def find_connected_components(graph):
    """
    Tìm các thành phần liên thông
    Input: undirected graph
    Output: [['A', 'B', 'C'], ['D', 'E']] (các component)
    
    Time Complexity: O(V + E)
    """
    visited = set()
    components = []
    
    def dfs_component(vertex, component):
        visited.add(vertex)
        component.append(vertex)
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                dfs_component(neighbor, component)
    
    for vertex in graph.get_vertices():
        if vertex not in visited:
            component = []
            dfs_component(vertex, component)
            components.append(component)
    
    return components

def has_cycle_undirected(graph):
    """
    Kiểm tra chu trình trong đồ thị vô hướng
    Input: undirected graph
    Output: True nếu có chu trình
    
    Time Complexity: O(V + E)
    """
    visited = set()
    
    def dfs_cycle(vertex, parent):
        visited.add(vertex)
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                if dfs_cycle(neighbor, vertex):
                    return True
            elif neighbor != parent:
                return True  # Tìm thấy chu trình
        
        return False
    
    for vertex in graph.get_vertices():
        if vertex not in visited:
            if dfs_cycle(vertex, None):
                return True
    
    return False

def has_cycle_directed(graph):
    """
    Kiểm tra chu trình trong đồ thị có hướng (sử dụng DFS)
    Input: directed graph
    Output: True nếu có chu trình
    
    Time Complexity: O(V + E)
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {vertex: WHITE for vertex in graph.get_vertices()}
    
    def dfs_cycle(vertex):
        if color[vertex] == GRAY:
            return True  # Back edge - chu trình
        
        if color[vertex] == BLACK:
            return False
        
        color[vertex] = GRAY
        
        for neighbor, _ in graph.graph[vertex]:
            if dfs_cycle(neighbor):
                return True
        
        color[vertex] = BLACK
        return False
    
    for vertex in graph.get_vertices():
        if color[vertex] == WHITE:
            if dfs_cycle(vertex):
                return True
    
    return False

def topological_sort(graph):
    """
    Sắp xếp topo (chỉ áp dụng cho DAG - Directed Acyclic Graph)
    Input: directed acyclic graph
    Output: ['A', 'B', 'C', 'D'] (thứ tự topo)
    
    Time Complexity: O(V + E)
    """
    visited = set()
    stack = []
    
    def dfs_topo(vertex):
        visited.add(vertex)
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor not in visited:
                dfs_topo(neighbor)
        
        stack.append(vertex)
    
    for vertex in graph.get_vertices():
        if vertex not in visited:
            dfs_topo(vertex)
    
    return stack[::-1]

def is_bipartite(graph):
    """
    Kiểm tra đồ thị có phải là đồ thị hai phần không
    Input: undirected graph
    Output: True nếu là bipartite, False nếu không
    
    Time Complexity: O(V + E)
    """
    color = {}
    
    def bfs_bipartite(start):
        queue = deque([start])
        color[start] = 0
        
        while queue:
            vertex = queue.popleft()
            
            for neighbor, _ in graph.graph[vertex]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    queue.append(neighbor)
                elif color[neighbor] == color[vertex]:
                    return False
        
        return True
    
    for vertex in graph.get_vertices():
        if vertex not in color:
            if not bfs_bipartite(vertex):
                return False
    
    return True

def minimum_spanning_tree_kruskal(graph):
    """
    Tìm cây khung nhỏ nhất sử dụng thuật toán Kruskal
    Input: weighted undirected graph
    Output: [(u, v, weight)] - các cạnh trong MST
    
    Time Complexity: O(E log E)
    """
    class UnionFind:
        def __init__(self, vertices):
            self.parent = {v: v for v in vertices}
            self.rank = {v: 0 for v in vertices}
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return False
            
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
            
            return True
    
    edges = graph.get_edges()
    edges.sort(key=lambda x: x[2])  # Sắp xếp theo trọng số
    
    uf = UnionFind(graph.get_vertices())
    mst = []
    
    for u, v, weight in edges:
        if uf.union(u, v):
            mst.append((u, v, weight))
    
    return mst

def path_exists(graph, start, end):
    """
    Kiểm tra có đường đi từ start đến end không
    Input: graph, start = 'A', end = 'E'
    Output: True nếu có đường đi
    """
    if start == end:
        return True
    
    visited = set()
    queue = deque([start])
    visited.add(start)
    
    while queue:
        vertex = queue.popleft()
        
        for neighbor, _ in graph.graph[vertex]:
            if neighbor == end:
                return True
            
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    
    return False

# Ví dụ sử dụng
if __name__ == "__main__":
    print("=== Graph Algorithms Demo ===")
    
    # Tạo đồ thị vô hướng
    print("=== Undirected Graph ===")
    g = Graph(directed=False)
    
    # Thêm các cạnh
    edges = [
        ('A', 'B', 4),
        ('A', 'C', 2),
        ('B', 'C', 1),
        ('B', 'D', 5),
        ('C', 'D', 8),
        ('C', 'E', 10),
        ('D', 'E', 2)
    ]
    
    for u, v, w in edges:
        g.add_edge(u, v, w)
    
    print("Graph structure:")
    g.print_graph()
    
    # BFS và DFS
    print(f"\\n=== Graph Traversals ===")
    start_vertex = 'A'
    
    bfs_result = bfs(g, start_vertex)
    dfs_result = dfs(g, start_vertex)
    dfs_iter_result = dfs_iterative(g, start_vertex)
    
    print(f"BFS from {start_vertex}: {bfs_result}")
    print(f"DFS from {start_vertex} (recursive): {dfs_result}")
    print(f"DFS from {start_vertex} (iterative): {dfs_iter_result}")
    
    # Tìm đường đi ngắn nhất
    print(f"\\n=== Shortest Path ===")
    start, end = 'A', 'E'
    
    # BFS (unweighted)
    shortest_path = find_shortest_path_bfs(g, start, end)
    print(f"Shortest path from {start} to {end} (unweighted): {shortest_path}")
    
    # Dijkstra (weighted)
    dijkstra_paths = dijkstra(g, start)
    print(f"Dijkstra from {start}:")
    for vertex, (distance, path) in dijkstra_paths.items():
        if distance != float('inf'):
            print(f"  To {vertex}: distance = {distance}, path = {' -> '.join(path)}")
    
    # Connected Components
    print(f"\\n=== Connected Components ===")
    components = find_connected_components(g)
    print(f"Connected components: {components}")
    
    # Cycle Detection
    print(f"\\n=== Cycle Detection ===")
    has_cycle = has_cycle_undirected(g)
    print(f"Has cycle (undirected): {has_cycle}")
    
    # Bipartite Check
    print(f"\\n=== Bipartite Check ===")
    is_bip = is_bipartite(g)
    print(f"Is bipartite: {is_bip}")
    
    # Minimum Spanning Tree
    print(f"\\n=== Minimum Spanning Tree (Kruskal) ===")
    mst = minimum_spanning_tree_kruskal(g)
    total_weight = sum(weight for _, _, weight in mst)
    print(f"MST edges: {mst}")
    print(f"Total weight: {total_weight}")
    
    # Đồ thị có hướng
    print(f"\\n=== Directed Graph ===")
    dg = Graph(directed=True)
    
    # Tạo DAG cho topological sort
    dag_edges = [
        ('A', 'B'),
        ('A', 'C'),
        ('B', 'D'),
        ('C', 'D'),
        ('C', 'E'),
        ('D', 'E')
    ]
    
    for u, v in dag_edges:
        dg.add_edge(u, v)
    
    print("Directed graph structure:")
    dg.print_graph()
    
    # Cycle detection for directed graph
    has_cycle_dir = has_cycle_directed(dg)
    print(f"\\nHas cycle (directed): {has_cycle_dir}")
    
    # Topological Sort
    if not has_cycle_dir:
        topo_order = topological_sort(dg)
        print(f"Topological order: {topo_order}")
    
    # Đồ thị với chu trình có hướng
    print(f"\\n=== Directed Graph with Cycle ===")
    cycle_graph = Graph(directed=True)
    cycle_edges = [('A', 'B'), ('B', 'C'), ('C', 'A')]
    
    for u, v in cycle_edges:
        cycle_graph.add_edge(u, v)
    
    print("Cycle graph structure:")
    cycle_graph.print_graph()
    
    has_cycle_dir = has_cycle_directed(cycle_graph)
    print(f"Has cycle (directed): {has_cycle_dir}")
    
    # Đồ thị không liên thông
    print(f"\\n=== Disconnected Graph ===")
    disconnected = Graph(directed=False)
    
    # Component 1
    disconnected.add_edge('A', 'B')
    disconnected.add_edge('B', 'C')
    
    # Component 2
    disconnected.add_edge('D', 'E')
    disconnected.add_edge('E', 'F')
    
    # Isolated vertex
    disconnected.add_vertex('G')
    
    print("Disconnected graph structure:")
    disconnected.print_graph()
    
    components = find_connected_components(disconnected)
    print(f"Connected components: {components}")
    
    # Path existence
    print(f"\\n=== Path Existence ===")
    test_paths = [('A', 'C'), ('A', 'D'), ('D', 'F'), ('A', 'G')]
    
    for start, end in test_paths:
        exists = path_exists(disconnected, start, end)
        print(f"Path from {start} to {end}: {'Exists' if exists else 'Does not exist'}")
    
    # Performance analysis
    print(f"\\n=== Performance Analysis ===")
    
    # Tạo đồ thị lớn
    import time
    import random
    
    large_graph = Graph(directed=False)
    n_vertices = 1000
    n_edges = 5000
    
    # Thêm vertices
    for i in range(n_vertices):
        large_graph.add_vertex(i)
    
    # Thêm edges ngẫu nhiên
    for _ in range(n_edges):
        u = random.randint(0, n_vertices - 1)
        v = random.randint(0, n_vertices - 1)
        if u != v:
            large_graph.add_edge(u, v, random.randint(1, 10))
    
    print(f"Testing on large graph: {n_vertices} vertices, {n_edges} edges")
    
    # BFS performance
    start_time = time.time()
    bfs_result = bfs(large_graph, 0)
    bfs_time = time.time() - start_time
    
    # DFS performance
    start_time = time.time()
    dfs_result = dfs(large_graph, 0)
    dfs_time = time.time() - start_time
    
    # Dijkstra performance
    start_time = time.time()
    dijkstra_result = dijkstra(large_graph, 0)
    dijkstra_time = time.time() - start_time
    
    print(f"BFS time: {bfs_time:.4f} seconds (visited {len(bfs_result)} nodes)")
    print(f"DFS time: {dfs_time:.4f} seconds (visited {len(dfs_result)} nodes)")
    print(f"Dijkstra time: {dijkstra_time:.4f} seconds")
