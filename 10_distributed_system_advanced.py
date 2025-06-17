"""
BÀI TẬP OOP NÂNG CAO 10: HỆ THỐNG PHÂN TÁN VÀ BLOCKCHAIN
Chủ đề: Distributed System, Blockchain, Consensus Algorithm, Cryptography

Kiến thức sử dụng:
- Advanced Metaclass và Type System
- Async/Await và Concurrent Programming
- Custom Protocols và Type Hinting
- Cryptographic Hashing
- Merkle Trees
- Consensus Algorithms (Proof of Work)
- Network Simulation
- Advanced Error Handling
- Memory Pool Management
- Chain Validation

Tác giả: Python Learning Series
"""

import hashlib
import json
import time
import asyncio
import threading
from typing import Dict, List, Optional, Protocol, TypeVar, Generic, Callable, Any
from dataclasses import dataclass, field
from enum import Enum, auto
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import random
import weakref

# ===================== TYPE DEFINITIONS =====================

T = TypeVar('T')
BlockType = TypeVar('BlockType', bound='Block')
NodeType = TypeVar('NodeType', bound='NetworkNode')

class NodeStatus(Enum):
    """Trạng thái của node trong mạng"""
    OFFLINE = auto()
    CONNECTING = auto()
    ONLINE = auto()
    MINING = auto()
    SYNCING = auto()

class TransactionStatus(Enum):
    """Trạng thái của giao dịch"""
    PENDING = auto()
    CONFIRMED = auto()
    REJECTED = auto()

# ===================== PROTOCOLS =====================

class Hashable(Protocol):
    """Protocol cho các đối tượng có thể hash"""
    def hash(self) -> str:
        ...

class Validatable(Protocol):
    """Protocol cho các đối tượng có thể validate"""
    def is_valid(self) -> bool:
        ...

class Mineable(Protocol):
    """Protocol cho các đối tượng có thể mine"""
    def mine(self, difficulty: int) -> bool:
        ...

# ===================== METACLASS FOR SINGLETON NETWORK =====================

class NetworkSingletonMeta(type):
    """Metaclass đảm bảo chỉ có một instance của Network"""
    _instances: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]

# ===================== CRYPTOGRAPHIC UTILITIES =====================

class CryptoUtils:
    """Tiện ích mã hóa cho blockchain"""
    
    @staticmethod
    def sha256(data: str) -> str:
        """Tạo SHA256 hash"""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def merkle_root(transactions: List[str]) -> str:
        """Tính Merkle root của danh sách transaction"""
        if not transactions:
            return CryptoUtils.sha256("")
        
        # Đảm bảo số lượng là lũy thừa của 2
        tx_hashes = [CryptoUtils.sha256(tx) for tx in transactions]
        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])  # Duplicate last hash
            
            next_level = []
            for i in range(0, len(tx_hashes), 2):
                combined = tx_hashes[i] + tx_hashes[i + 1]
                next_level.append(CryptoUtils.sha256(combined))
            tx_hashes = next_level
        
        return tx_hashes[0]
    
    @staticmethod
    def is_valid_proof(block_data: str, nonce: int, difficulty: int) -> bool:
        """Kiểm tra proof of work có hợp lệ không"""
        hash_result = CryptoUtils.sha256(f"{block_data}{nonce}")
        return hash_result.startswith('0' * difficulty)

# ===================== TRANSACTION SYSTEM =====================

@dataclass
class Transaction:
    """Đại diện cho một giao dịch"""
    from_address: str
    to_address: str
    amount: float
    timestamp: float = field(default_factory=time.time)
    transaction_id: str = field(init=False)
    status: TransactionStatus = TransactionStatus.PENDING
    
    def __post_init__(self):
        self.transaction_id = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """Tính hash của giao dịch"""
        data = f"{self.from_address}{self.to_address}{self.amount}{self.timestamp}"
        return CryptoUtils.sha256(data)
    
    def is_valid(self) -> bool:
        """Kiểm tra giao dịch có hợp lệ không"""
        return (
            self.from_address != self.to_address and
            self.amount > 0 and
            self.timestamp <= time.time()
        )
    
    def to_dict(self) -> Dict:
        """Chuyển đổi thành dictionary"""
        return {
            'id': self.transaction_id,
            'from': self.from_address,
            'to': self.to_address,
            'amount': self.amount,
            'timestamp': self.timestamp,
            'status': self.status.name
        }

class TransactionPool:
    """Pool quản lý các giao dịch chưa được xử lý"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.pending_transactions: deque = deque(maxlen=max_size)
        self.transaction_lookup: Dict[str, Transaction] = {}
        self._lock = threading.RLock()
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Thêm giao dịch vào pool"""
        with self._lock:
            if not transaction.is_valid():
                return False
            
            if transaction.transaction_id in self.transaction_lookup:
                return False  # Duplicate transaction
            
            self.pending_transactions.append(transaction)
            self.transaction_lookup[transaction.transaction_id] = transaction
            return True
    
    def get_transactions(self, count: int) -> List[Transaction]:
        """Lấy số lượng giao dịch nhất định từ pool"""
        with self._lock:
            transactions = []
            for _ in range(min(count, len(self.pending_transactions))):
                if self.pending_transactions:
                    tx = self.pending_transactions.popleft()
                    del self.transaction_lookup[tx.transaction_id]
                    transactions.append(tx)
            return transactions
    
    def remove_transaction(self, transaction_id: str) -> bool:
        """Xóa giao dịch khỏi pool"""
        with self._lock:
            if transaction_id in self.transaction_lookup:
                tx = self.transaction_lookup[transaction_id]
                try:
                    self.pending_transactions.remove(tx)
                    del self.transaction_lookup[transaction_id]
                    return True
                except ValueError:
                    pass
            return False
    
    def size(self) -> int:
        """Trả về kích thước pool"""
        return len(self.pending_transactions)

# ===================== BLOCK SYSTEM =====================

@dataclass
class Block:
    """Đại diện cho một block trong blockchain"""
    index: int
    transactions: List[Transaction]
    timestamp: float
    previous_hash: str
    nonce: int = 0
    hash: str = field(init=False)
    merkle_root: str = field(init=False)
    
    def __post_init__(self):
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.calculate_hash()
    
    def calculate_merkle_root(self) -> str:
        """Tính Merkle root của các giao dịch"""
        tx_strings = [json.dumps(tx.to_dict(), sort_keys=True) for tx in self.transactions]
        return CryptoUtils.merkle_root(tx_strings)
    
    def calculate_hash(self) -> str:
        """Tính hash của block"""
        data = f"{self.index}{self.previous_hash}{self.timestamp}{self.merkle_root}{self.nonce}"
        return CryptoUtils.sha256(data)
    
    def mine_block(self, difficulty: int) -> bool:
        """Mine block với độ khó nhất định"""
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
            
            # Giới hạn để tránh infinite loop
            if self.nonce > 1000000:
                return False
        
        # Cập nhật trạng thái giao dịch
        for tx in self.transactions:
            tx.status = TransactionStatus.CONFIRMED
        
        return True
    
    def is_valid(self, previous_block: Optional['Block'] = None) -> bool:
        """Kiểm tra block có hợp lệ không"""
        # Kiểm tra hash
        if self.hash != self.calculate_hash():
            return False
        
        # Kiểm tra merkle root
        if self.merkle_root != self.calculate_merkle_root():
            return False
        
        # Kiểm tra liên kết với block trước
        if previous_block and self.previous_hash != previous_block.hash:
            return False
        
        # Kiểm tra các giao dịch
        for tx in self.transactions:
            if not tx.is_valid():
                return False
        
        return True
    
    def to_dict(self) -> Dict:
        """Chuyển đổi thành dictionary"""
        return {
            'index': self.index,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'timestamp': self.timestamp,
            'merkle_root': self.merkle_root,
            'nonce': self.nonce,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }

# ===================== BLOCKCHAIN SYSTEM =====================

class Blockchain:
    """Hệ thống blockchain chính"""
    
    def __init__(self, difficulty: int = 4):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.transaction_pool = TransactionPool()
        self.create_genesis_block()
        self._lock = threading.RLock()
    
    def create_genesis_block(self):
        """Tạo block đầu tiên (Genesis block)"""
        genesis_tx = Transaction("genesis", "system", 0, time.time())
        genesis_block = Block(0, [genesis_tx], time.time(), "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        """Lấy block mới nhất"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Thêm giao dịch vào pool"""
        return self.transaction_pool.add_transaction(transaction)
    
    def mine_pending_transactions(self, mining_reward_address: str) -> Optional[Block]:
        """Mine các giao dịch đang chờ"""
        with self._lock:
            # Lấy giao dịch từ pool
            transactions = self.transaction_pool.get_transactions(10)  # Tối đa 10 tx/block
            
            if not transactions:
                return None
            
            # Thêm giao dịch thưởng cho miner
            reward_tx = Transaction("system", mining_reward_address, 10.0, time.time())
            transactions.append(reward_tx)
            
            # Tạo block mới
            latest_block = self.get_latest_block()
            new_block = Block(
                index=latest_block.index + 1,
                transactions=transactions,
                timestamp=time.time(),
                previous_hash=latest_block.hash
            )
            
            # Mine block
            if new_block.mine_block(self.difficulty):
                self.chain.append(new_block)
                return new_block
            
            return None
    
    def is_chain_valid(self) -> bool:
        """Kiểm tra tính hợp lệ của blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            if not current_block.is_valid(previous_block):
                return False
        
        return True
    
    def get_balance(self, address: str) -> float:
        """Tính số dư của một địa chỉ"""
        balance = 0
        for block in self.chain:
            for tx in block.transactions:
                if tx.status == TransactionStatus.CONFIRMED:
                    if tx.from_address == address:
                        balance -= tx.amount
                    if tx.to_address == address:
                        balance += tx.amount
        return balance
    
    def get_chain_info(self) -> Dict:
        """Lấy thông tin về blockchain"""
        return {
            'length': len(self.chain),
            'difficulty': self.difficulty,
            'pending_transactions': self.transaction_pool.size(),
            'is_valid': self.is_chain_valid(),
            'latest_block_hash': self.get_latest_block().hash
        }

# ===================== NETWORK NODE SYSTEM =====================

class NetworkNode:
    """Đại diện cho một node trong mạng blockchain"""
    
    def __init__(self, node_id: str, blockchain: Optional[Blockchain] = None):
        self.node_id = node_id
        self.blockchain = blockchain or Blockchain()
        self.status = NodeStatus.OFFLINE
        self.peers: Dict[str, 'NetworkNode'] = {}
        self.message_queue: deque = deque(maxlen=100)
        self._lock = threading.RLock()
        self.mining_active = False
        self.mining_thread: Optional[threading.Thread] = None
    
    def connect_to_network(self):
        """Kết nối node vào mạng"""
        self.status = NodeStatus.CONNECTING
        # Simulate network connection
        time.sleep(0.1)
        self.status = NodeStatus.ONLINE
        print(f"Node {self.node_id} đã kết nối vào mạng")
    
    def add_peer(self, peer: 'NetworkNode'):
        """Thêm peer node"""
        with self._lock:
            self.peers[peer.node_id] = peer
            peer.peers[self.node_id] = self
            print(f"Node {self.node_id} đã kết nối với {peer.node_id}")
    
    def broadcast_transaction(self, transaction: Transaction):
        """Broadcast giao dịch đến các peer"""
        self.blockchain.add_transaction(transaction)
        message = {
            'type': 'new_transaction',
            'data': transaction.to_dict(),
            'from_node': self.node_id
        }
        self._broadcast_message(message)
    
    def broadcast_block(self, block: Block):
        """Broadcast block mới đến các peer"""
        message = {
            'type': 'new_block',
            'data': block.to_dict(),
            'from_node': self.node_id
        }
        self._broadcast_message(message)
    
    def _broadcast_message(self, message: Dict):
        """Gửi message đến tất cả peer"""
        for peer in self.peers.values():
            peer._receive_message(message)
    
    def _receive_message(self, message: Dict):
        """Nhận message từ peer"""
        with self._lock:
            self.message_queue.append(message)
            self._process_message(message)
    
    def _process_message(self, message: Dict):
        """Xử lý message nhận được"""
        msg_type = message.get('type')
        data = message.get('data')
        from_node = message.get('from_node')
        
        if msg_type == 'new_transaction':
            # Tạo lại transaction object từ data
            tx = Transaction(
                from_address=data['from'],
                to_address=data['to'],
                amount=data['amount'],
                timestamp=data['timestamp']
            )
            self.blockchain.add_transaction(tx)
            print(f"Node {self.node_id} nhận giao dịch từ {from_node}")
        
        elif msg_type == 'new_block':
            # Xử lý block mới (simplified)
            print(f"Node {self.node_id} nhận block mới từ {from_node}")
    
    def start_mining(self):
        """Bắt đầu mining"""
        if self.mining_active:
            return
        
        self.mining_active = True
        self.status = NodeStatus.MINING
        self.mining_thread = threading.Thread(target=self._mining_loop)
        self.mining_thread.daemon = True
        self.mining_thread.start()
        print(f"Node {self.node_id} bắt đầu mining")
    
    def stop_mining(self):
        """Dừng mining"""
        self.mining_active = False
        self.status = NodeStatus.ONLINE
        print(f"Node {self.node_id} dừng mining")
    
    def _mining_loop(self):
        """Vòng lặp mining"""
        while self.mining_active:
            try:
                new_block = self.blockchain.mine_pending_transactions(self.node_id)
                if new_block:
                    print(f"Node {self.node_id} đã mine thành công block #{new_block.index}")
                    self.broadcast_block(new_block)
                time.sleep(1)  # Nghỉ giữa các lần mining
            except Exception as e:
                print(f"Lỗi mining trên node {self.node_id}: {e}")
    
    def get_node_info(self) -> Dict:
        """Lấy thông tin node"""
        return {
            'node_id': self.node_id,
            'status': self.status.name,
            'peers_count': len(self.peers),
            'balance': self.blockchain.get_balance(self.node_id),
            'blockchain_info': self.blockchain.get_chain_info()
        }

# ===================== NETWORK MANAGER =====================

class BlockchainNetwork(metaclass=NetworkSingletonMeta):
    """Quản lý toàn bộ mạng blockchain"""
    
    def __init__(self):
        self.nodes: Dict[str, NetworkNode] = {}
        self.network_stats = {
            'total_transactions': 0,
            'total_blocks': 0,
            'active_nodes': 0
        }
        self._lock = threading.RLock()
    
    def add_node(self, node_id: str) -> NetworkNode:
        """Thêm node mới vào mạng"""
        with self._lock:
            if node_id in self.nodes:
                return self.nodes[node_id]
            
            node = NetworkNode(node_id)
            node.connect_to_network()
            self.nodes[node_id] = node
            
            # Kết nối với các node khác (simplified topology)
            for existing_node in list(self.nodes.values())[:-1]:  # Exclude the new node
                if len(existing_node.peers) < 3:  # Limit connections
                    node.add_peer(existing_node)
            
            self.network_stats['active_nodes'] = len(self.nodes)
            return node
    
    def remove_node(self, node_id: str):
        """Xóa node khỏi mạng"""
        with self._lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.stop_mining()
                
                # Disconnect from peers
                for peer in list(node.peers.values()):
                    del peer.peers[node_id]
                
                del self.nodes[node_id]
                self.network_stats['active_nodes'] = len(self.nodes)
    
    def simulate_transaction(self, from_node: str, to_address: str, amount: float):
        """Mô phỏng giao dịch trong mạng"""
        if from_node in self.nodes:
            node = self.nodes[from_node]
            tx = Transaction(from_node, to_address, amount)
            node.broadcast_transaction(tx)
            self.network_stats['total_transactions'] += 1
            print(f"Giao dịch: {from_node} -> {to_address}: {amount}")
    
    def get_network_stats(self) -> Dict:
        """Lấy thống kê mạng"""
        with self._lock:
            # Calculate total blocks across all nodes
            max_blocks = 0
            for node in self.nodes.values():
                blocks = len(node.blockchain.chain)
                if blocks > max_blocks:
                    max_blocks = blocks
            
            self.network_stats['total_blocks'] = max_blocks
            
            return self.network_stats.copy()
    
    def get_all_nodes_info(self) -> Dict[str, Dict]:
        """Lấy thông tin tất cả nodes"""
        return {node_id: node.get_node_info() for node_id, node in self.nodes.items()}

# ===================== DEMO VÀ SỬ DỤNG =====================

def demo_basic_blockchain():
    """Demo cơ bản về blockchain"""
    print("=== DEMO BLOCKCHAIN CƠ BẢN ===")
    
    # Tạo blockchain
    blockchain = Blockchain(difficulty=2)
    
    # Tạo giao dịch
    tx1 = Transaction("Alice", "Bob", 50.0)
    tx2 = Transaction("Bob", "Charlie", 25.0)
    
    blockchain.add_transaction(tx1)
    blockchain.add_transaction(tx2)
    
    print(f"Pending transactions: {blockchain.transaction_pool.size()}")
    
    # Mine block
    new_block = blockchain.mine_pending_transactions("Miner1")
    if new_block:
        print(f"Block #{new_block.index} đã được mine với {len(new_block.transactions)} giao dịch")
    
    # Kiểm tra số dư
    print(f"Số dư Alice: {blockchain.get_balance('Alice')}")
    print(f"Số dư Bob: {blockchain.get_balance('Bob')}")
    print(f"Số dư Charlie: {blockchain.get_balance('Charlie')}")
    print(f"Số dư Miner1: {blockchain.get_balance('Miner1')}")
    
    print(f"Blockchain hợp lệ: {blockchain.is_chain_valid()}")

def demo_network_simulation():
    """Demo mô phỏng mạng blockchain"""
    print("\n=== DEMO MẠNG BLOCKCHAIN ===")
    
    # Tạo mạng
    network = BlockchainNetwork()
    
    # Thêm nodes
    node1 = network.add_node("Node1")
    node2 = network.add_node("Node2")
    node3 = network.add_node("Node3")
    
    # Bắt đầu mining trên một số nodes
    node1.start_mining()
    node2.start_mining()
    
    # Mô phỏng giao dịch
    network.simulate_transaction("Node1", "Node2", 30.0)
    network.simulate_transaction("Node2", "Node3", 15.0)
    network.simulate_transaction("Node3", "Node1", 45.0)
    
    # Chờ một chút để mining
    time.sleep(3)
    
    # Dừng mining
    node1.stop_mining()
    node2.stop_mining()
    
    # Hiển thị thống kê
    print("\nThống kê mạng:")
    stats = network.get_network_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\nThông tin các nodes:")
    nodes_info = network.get_all_nodes_info()
    for node_id, info in nodes_info.items():
        print(f"{node_id}: {info['status']}, Peers: {info['peers_count']}, Balance: {info['balance']}")

def demo_advanced_features():
    """Demo các tính năng nâng cao"""
    print("\n=== DEMO TÍNH NĂNG NÂNG CAO ===")
    
    # Test Merkle Tree
    transactions = ["tx1", "tx2", "tx3", "tx4"]
    merkle_root = CryptoUtils.merkle_root(transactions)
    print(f"Merkle Root: {merkle_root[:16]}...")
    
    # Test Proof of Work
    test_data = "test block data"
    nonce = 0
    difficulty = 3
    
    start_time = time.time()
    while not CryptoUtils.is_valid_proof(test_data, nonce, difficulty):
        nonce += 1
        if nonce > 100000:  # Giới hạn để demo
            break
    
    end_time = time.time()
    print(f"Proof of Work: nonce={nonce}, thời gian={end_time-start_time:.2f}s")
    
    # Test Transaction Pool
    pool = TransactionPool(max_size=5)
    for i in range(7):  # Thêm nhiều hơn max_size
        tx = Transaction(f"user{i}", f"user{i+1}", float(i+1))
        added = pool.add_transaction(tx)
        print(f"Transaction {i+1}: {'Added' if added else 'Rejected'}")
    
    print(f"Pool size: {pool.size()}")

if __name__ == "__main__":
    print("CHƯƠNG TRÌNH DEMO HỆ THỐNG BLOCKCHAIN PHÂN TÁN")
    print("=" * 50)
    
    try:
        # Demo blockchain cơ bản
        demo_basic_blockchain()
        
        # Demo mạng phân tán
        demo_network_simulation()
        
        # Demo tính năng nâng cao
        demo_advanced_features()
        
        print("\n" + "=" * 50)
        print("DEMO HOÀN THÀNH!")
        print("\nCác kỹ thuật OOP nâng cao đã sử dụng:")
        print("✓ Metaclass (NetworkSingletonMeta)")
        print("✓ Protocol và Type Hinting")
        print("✓ Generic Types và TypeVar")
        print("✓ Dataclass với field customization")
        print("✓ Threading và Async patterns")
        print("✓ Context managers (locks)")
        print("✓ Weak references")
        print("✓ Advanced error handling")
        print("✓ Memory management (deque với maxlen)")
        print("✓ Cryptographic algorithms")
        print("✓ Consensus mechanisms")
        print("✓ Network simulation")
        
    except KeyboardInterrupt:
        print("\nChương trình bị dừng bởi người dùng")
    except Exception as e:
        print(f"\nLỗi: {e}")
        import traceback
        traceback.print_exc()
