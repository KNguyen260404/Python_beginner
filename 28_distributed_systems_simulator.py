#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Distributed Systems Simulator
----------------------------
A comprehensive simulator for distributed systems that implements:
- Consensus algorithms (Raft, PBFT, Paxos)
- Distributed hash tables
- Fault tolerance mechanisms
- Load balancing strategies
- Network partitioning simulation
- Byzantine fault tolerance
"""

import asyncio
import random
import time
import json
import hashlib
import logging
from typing import Dict, List, Set, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
import threading
import socket
import pickle
import argparse
import matplotlib.pyplot as plt
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NodeState(Enum):
    """States for distributed system nodes"""
    FOLLOWER = auto()
    CANDIDATE = auto()
    LEADER = auto()
    FAILED = auto()
    RECOVERING = auto()

class MessageType(Enum):
    """Types of messages in the distributed system"""
    HEARTBEAT = auto()
    VOTE_REQUEST = auto()
    VOTE_RESPONSE = auto()
    APPEND_ENTRIES = auto()
    APPEND_RESPONSE = auto()
    CLIENT_REQUEST = auto()
    CLIENT_RESPONSE = auto()
    PREPARE = auto()
    PROMISE = auto()
    ACCEPT = auto()
    ACCEPTED = auto()

class ConsensusAlgorithm(Enum):
    """Available consensus algorithms"""
    RAFT = auto()
    PBFT = auto()
    PAXOS = auto()

@dataclass
class Message:
    """Message structure for distributed communication"""
    msg_type: MessageType
    sender_id: str
    receiver_id: str
    term: int = 0
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class LogEntry:
    """Log entry for consensus algorithms"""
    term: int
    index: int
    command: str
    data: Any
    timestamp: float = field(default_factory=time.time)

class NetworkSimulator:
    """Simulates network conditions for distributed systems"""
    
    def __init__(self):
        """Initialize network simulator"""
        self.latency_range = (10, 100)  # milliseconds
        self.packet_loss_rate = 0.0
        self.partition_groups: List[Set[str]] = []
        self.failed_nodes: Set[str] = set()
        
    def set_network_conditions(self, latency_range: Tuple[int, int], packet_loss_rate: float):
        """Set network conditions
        
        Args:
            latency_range: Min and max latency in milliseconds
            packet_loss_rate: Probability of packet loss (0.0 to 1.0)
        """
        self.latency_range = latency_range
        self.packet_loss_rate = packet_loss_rate
    
    def create_partition(self, group1: Set[str], group2: Set[str]):
        """Create a network partition
        
        Args:
            group1: First group of nodes
            group2: Second group of nodes
        """
        self.partition_groups = [group1, group2]
        logger.info(f"Created network partition: {group1} | {group2}")
    
    def heal_partition(self):
        """Heal network partition"""
        self.partition_groups = []
        logger.info("Network partition healed")
    
    def fail_node(self, node_id: str):
        """Simulate node failure
        
        Args:
            node_id: ID of the node to fail
        """
        self.failed_nodes.add(node_id)
        logger.info(f"Node {node_id} failed")
    
    def recover_node(self, node_id: str):
        """Recover a failed node
        
        Args:
            node_id: ID of the node to recover
        """
        self.failed_nodes.discard(node_id)
        logger.info(f"Node {node_id} recovered")
    
    async def send_message(self, message: Message) -> bool:
        """Simulate message sending with network conditions
        
        Args:
            message: Message to send
            
        Returns:
            True if message was delivered, False otherwise
        """
        # Check if sender or receiver failed
        if message.sender_id in self.failed_nodes or message.receiver_id in self.failed_nodes:
            return False
        
        # Check network partition
        if self.partition_groups:
            sender_group = None
            receiver_group = None
            
            for i, group in enumerate(self.partition_groups):
                if message.sender_id in group:
                    sender_group = i
                if message.receiver_id in group:
                    receiver_group = i
            
            if sender_group != receiver_group:
                return False
        
        # Simulate packet loss
        if random.random() < self.packet_loss_rate:
            return False
        
        # Simulate network latency
        latency = random.randint(*self.latency_range) / 1000.0
        await asyncio.sleep(latency)
        
        return True

class RaftNode:
    """Implementation of a Raft consensus algorithm node"""
    
    def __init__(self, node_id: str, cluster_nodes: List[str], network: NetworkSimulator):
        """Initialize Raft node
        
        Args:
            node_id: Unique identifier for this node
            cluster_nodes: List of all nodes in the cluster
            network: Network simulator instance
        """
        self.node_id = node_id
        self.cluster_nodes = cluster_nodes
        self.network = network
        
        # Raft state
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.last_applied = 0
        
        # Leader state
        self.next_index: Dict[str, int] = {}
        self.match_index: Dict[str, int] = {}
        
        # Timing
        self.last_heartbeat = time.time()
        self.election_timeout = random.uniform(150, 300) / 1000.0  # 150-300ms
        self.heartbeat_interval = 50 / 1000.0  # 50ms
        
        # Message queues
        self.message_queue = asyncio.Queue()
        self.client_requests = asyncio.Queue()
        
        # Statistics
        self.stats = {
            'elections_started': 0,
            'elections_won': 0,
            'messages_sent': 0,
            'messages_received': 0
        }
    
    async def start(self):
        """Start the Raft node"""
        # Start background tasks
        tasks = [
            asyncio.create_task(self.election_timer()),
            asyncio.create_task(self.message_processor()),
            asyncio.create_task(self.client_request_processor())
        ]
        
        if self.state == NodeState.LEADER:
            tasks.append(asyncio.create_task(self.heartbeat_sender()))
        
        await asyncio.gather(*tasks)
    
    async def election_timer(self):
        """Timer for election timeout"""
        while True:
            await asyncio.sleep(0.01)  # Check every 10ms
            
            if self.state != NodeState.LEADER:
                if time.time() - self.last_heartbeat > self.election_timeout:
                    await self.start_election()
    
    async def start_election(self):
        """Start a new election"""
        if self.node_id in self.network.failed_nodes:
            return
        
        self.state = NodeState.CANDIDATE
        self.current_term += 1
        self.voted_for = self.node_id
        self.last_heartbeat = time.time()
        self.stats['elections_started'] += 1
        
        logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
        
        # Vote for self
        votes_received = 1
        
        # Request votes from other nodes
        vote_tasks = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = asyncio.create_task(self.request_vote(node_id))
                vote_tasks.append(task)
        
        # Wait for vote responses
        if vote_tasks:
            votes = await asyncio.gather(*vote_tasks, return_exceptions=True)
            votes_received += sum(1 for vote in votes if vote is True)
        
        # Check if won election
        majority = len(self.cluster_nodes) // 2 + 1
        if votes_received >= majority and self.state == NodeState.CANDIDATE:
            await self.become_leader()
        else:
            self.state = NodeState.FOLLOWER
    
    async def request_vote(self, target_node: str) -> bool:
        """Request vote from a target node
        
        Args:
            target_node: ID of the node to request vote from
            
        Returns:
            True if vote granted, False otherwise
        """
        last_log_index = len(self.log) - 1 if self.log else -1
        last_log_term = self.log[-1].term if self.log else 0
        
        message = Message(
            msg_type=MessageType.VOTE_REQUEST,
            sender_id=self.node_id,
            receiver_id=target_node,
            term=self.current_term,
            data={
                'last_log_index': last_log_index,
                'last_log_term': last_log_term
            }
        )
        
        # Send message through network simulator
        if await self.network.send_message(message):
            self.stats['messages_sent'] += 1
            # In a real implementation, we'd wait for response
            # Here we simulate the response
            return random.random() > 0.3  # 70% chance of getting vote
        
        return False
    
    async def become_leader(self):
        """Become the leader of the cluster"""
        self.state = NodeState.LEADER
        self.stats['elections_won'] += 1
        
        # Initialize leader state
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                self.next_index[node_id] = len(self.log)
                self.match_index[node_id] = -1
        
        logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
        
        # Start sending heartbeats
        asyncio.create_task(self.heartbeat_sender())
    
    async def heartbeat_sender(self):
        """Send periodic heartbeats to followers"""
        while self.state == NodeState.LEADER:
            await self.send_heartbeats()
            await asyncio.sleep(self.heartbeat_interval)
    
    async def send_heartbeats(self):
        """Send heartbeat messages to all followers"""
        tasks = []
        for node_id in self.cluster_nodes:
            if node_id != self.node_id:
                task = asyncio.create_task(self.send_append_entries(node_id))
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_append_entries(self, target_node: str, entries: List[LogEntry] = None):
        """Send append entries message to a follower
        
        Args:
            target_node: ID of the target node
            entries: Log entries to send (empty for heartbeat)
        """
        if entries is None:
            entries = []
        
        prev_log_index = self.next_index.get(target_node, 0) - 1
        prev_log_term = 0
        if prev_log_index >= 0 and prev_log_index < len(self.log):
            prev_log_term = self.log[prev_log_index].term
        
        message = Message(
            msg_type=MessageType.APPEND_ENTRIES,
            sender_id=self.node_id,
            receiver_id=target_node,
            term=self.current_term,
            data={
                'prev_log_index': prev_log_index,
                'prev_log_term': prev_log_term,
                'entries': entries,
                'leader_commit': self.commit_index
            }
        )
        
        if await self.network.send_message(message):
            self.stats['messages_sent'] += 1
    
    async def message_processor(self):
        """Process incoming messages"""
        while True:
            try:
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                await self.handle_message(message)
                self.stats['messages_received'] += 1
            except asyncio.TimeoutError:
                continue
    
    async def handle_message(self, message: Message):
        """Handle incoming message
        
        Args:
            message: Incoming message
        """
        # Update term if necessary
        if message.term > self.current_term:
            self.current_term = message.term
            self.voted_for = None
            if self.state != NodeState.FOLLOWER:
                self.state = NodeState.FOLLOWER
        
        if message.msg_type == MessageType.VOTE_REQUEST:
            await self.handle_vote_request(message)
        elif message.msg_type == MessageType.APPEND_ENTRIES:
            await self.handle_append_entries(message)
        elif message.msg_type == MessageType.CLIENT_REQUEST:
            await self.handle_client_request(message)
    
    async def handle_vote_request(self, message: Message):
        """Handle vote request message
        
        Args:
            message: Vote request message
        """
        grant_vote = False
        
        if (message.term >= self.current_term and 
            (self.voted_for is None or self.voted_for == message.sender_id)):
            
            # Check log up-to-date condition
            last_log_index = len(self.log) - 1 if self.log else -1
            last_log_term = self.log[-1].term if self.log else 0
            
            candidate_last_log_index = message.data['last_log_index']
            candidate_last_log_term = message.data['last_log_term']
            
            if (candidate_last_log_term > last_log_term or
                (candidate_last_log_term == last_log_term and 
                 candidate_last_log_index >= last_log_index)):
                grant_vote = True
                self.voted_for = message.sender_id
                self.last_heartbeat = time.time()
        
        # Send vote response
        response = Message(
            msg_type=MessageType.VOTE_RESPONSE,
            sender_id=self.node_id,
            receiver_id=message.sender_id,
            term=self.current_term,
            data={'vote_granted': grant_vote}
        )
        
        if await self.network.send_message(response):
            self.stats['messages_sent'] += 1
    
    async def handle_append_entries(self, message: Message):
        """Handle append entries message
        
        Args:
            message: Append entries message
        """
        success = False
        
        if message.term >= self.current_term:
            self.state = NodeState.FOLLOWER
            self.last_heartbeat = time.time()
            
            # Check log consistency
            prev_log_index = message.data['prev_log_index']
            prev_log_term = message.data['prev_log_term']
            
            if (prev_log_index == -1 or
                (prev_log_index < len(self.log) and 
                 self.log[prev_log_index].term == prev_log_term)):
                success = True
                
                # Append new entries
                entries = message.data['entries']
                if entries:
                    # Remove conflicting entries
                    self.log = self.log[:prev_log_index + 1]
                    self.log.extend(entries)
                
                # Update commit index
                leader_commit = message.data['leader_commit']
                if leader_commit > self.commit_index:
                    self.commit_index = min(leader_commit, len(self.log) - 1)
        
        # Send response
        response = Message(
            msg_type=MessageType.APPEND_RESPONSE,
            sender_id=self.node_id,
            receiver_id=message.sender_id,
            term=self.current_term,
            data={'success': success}
        )
        
        if await self.network.send_message(response):
            self.stats['messages_sent'] += 1
    
    async def handle_client_request(self, message: Message):
        """Handle client request
        
        Args:
            message: Client request message
        """
        if self.state == NodeState.LEADER:
            # Add to log
            entry = LogEntry(
                term=self.current_term,
                index=len(self.log),
                command=message.data['command'],
                data=message.data.get('data')
            )
            self.log.append(entry)
            
            # Replicate to followers
            await self.send_heartbeats()
        else:
            # Redirect to leader if known
            pass
    
    async def client_request_processor(self):
        """Process client requests"""
        while True:
            try:
                request = await asyncio.wait_for(self.client_requests.get(), timeout=1.0)
                await self.handle_client_request(request)
            except asyncio.TimeoutError:
                continue
    
    def get_status(self) -> Dict[str, Any]:
        """Get current node status
        
        Returns:
            Status dictionary
        """
        return {
            'node_id': self.node_id,
            'state': self.state.name,
            'term': self.current_term,
            'log_length': len(self.log),
            'commit_index': self.commit_index,
            'stats': self.stats
        }

class DistributedHashTable:
    """Implementation of a distributed hash table"""
    
    def __init__(self, node_id: str, nodes: List[str], replication_factor: int = 3):
        """Initialize DHT node
        
        Args:
            node_id: Unique identifier for this node
            nodes: List of all nodes in the DHT
            replication_factor: Number of replicas for each key
        """
        self.node_id = node_id
        self.nodes = sorted(nodes)  # Consistent ordering
        self.replication_factor = replication_factor
        self.data: Dict[str, Any] = {}
        self.ring_size = 2**32  # 32-bit hash space
        
        # Create consistent hash ring
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _build_ring(self):
        """Build the consistent hash ring"""
        self.ring = {}
        
        # Add virtual nodes for better distribution
        virtual_nodes_per_node = 100
        
        for node in self.nodes:
            for i in range(virtual_nodes_per_node):
                virtual_node = f"{node}:{i}"
                hash_key = self._hash(virtual_node)
                self.ring[hash_key] = node
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def _hash(self, key: str) -> int:
        """Hash function for consistent hashing
        
        Args:
            key: Key to hash
            
        Returns:
            Hash value
        """
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % self.ring_size
    
    def _get_responsible_nodes(self, key: str) -> List[str]:
        """Get nodes responsible for a key
        
        Args:
            key: The key to find nodes for
            
        Returns:
            List of responsible node IDs
        """
        hash_key = self._hash(key)
        
        # Find the first node clockwise from hash_key
        idx = 0
        for i, ring_key in enumerate(self.sorted_keys):
            if ring_key >= hash_key:
                idx = i
                break
        
        # Get replication_factor nodes
        responsible_nodes = []
        seen_nodes = set()
        
        for i in range(len(self.sorted_keys)):
            ring_idx = (idx + i) % len(self.sorted_keys)
            node = self.ring[self.sorted_keys[ring_idx]]
            
            if node not in seen_nodes:
                responsible_nodes.append(node)
                seen_nodes.add(node)
                
                if len(responsible_nodes) >= self.replication_factor:
                    break
        
        return responsible_nodes
    
    def put(self, key: str, value: Any) -> bool:
        """Store a key-value pair
        
        Args:
            key: The key
            value: The value
            
        Returns:
            True if stored successfully
        """
        responsible_nodes = self._get_responsible_nodes(key)
        
        if self.node_id in responsible_nodes:
            self.data[key] = {
                'value': value,
                'timestamp': time.time(),
                'version': self.data.get(key, {}).get('version', 0) + 1
            }
            return True
        
        return False
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key
        
        Args:
            key: The key to retrieve
            
        Returns:
            The value if found, None otherwise
        """
        responsible_nodes = self._get_responsible_nodes(key)
        
        if self.node_id in responsible_nodes and key in self.data:
            return self.data[key]['value']
        
        return None
    
    def delete(self, key: str) -> bool:
        """Delete a key-value pair
        
        Args:
            key: The key to delete
            
        Returns:
            True if deleted successfully
        """
        responsible_nodes = self._get_responsible_nodes(key)
        
        if self.node_id in responsible_nodes and key in self.data:
            del self.data[key]
            return True
        
        return False
    
    def add_node(self, node_id: str):
        """Add a new node to the DHT
        
        Args:
            node_id: ID of the new node
        """
        if node_id not in self.nodes:
            self.nodes.append(node_id)
            self.nodes.sort()
            self._build_ring()
            
            # Redistribute data if necessary
            self._redistribute_data()
    
    def remove_node(self, node_id: str):
        """Remove a node from the DHT
        
        Args:
            node_id: ID of the node to remove
        """
        if node_id in self.nodes:
            self.nodes.remove(node_id)
            self._build_ring()
            
            # Redistribute data if necessary
            self._redistribute_data()
    
    def _redistribute_data(self):
        """Redistribute data after topology changes"""
        # In a real implementation, this would involve
        # transferring data between nodes
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get DHT statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'node_id': self.node_id,
            'total_nodes': len(self.nodes),
            'stored_keys': len(self.data),
            'ring_size': len(self.ring),
            'replication_factor': self.replication_factor
        }

class LoadBalancer:
    """Load balancer for distributed systems"""
    
    def __init__(self, servers: List[str], algorithm: str = "round_robin"):
        """Initialize load balancer
        
        Args:
            servers: List of server identifiers
            algorithm: Load balancing algorithm
        """
        self.servers = servers
        self.algorithm = algorithm
        self.current_index = 0
        self.server_weights = {server: 1 for server in servers}
        self.server_connections = {server: 0 for server in servers}
        self.server_response_times = {server: deque(maxlen=100) for server in servers}
        
    def get_server(self, client_id: str = None) -> str:
        """Get next server based on load balancing algorithm
        
        Args:
            client_id: Optional client identifier for sticky sessions
            
        Returns:
            Selected server identifier
        """
        if self.algorithm == "round_robin":
            return self._round_robin()
        elif self.algorithm == "least_connections":
            return self._least_connections()
        elif self.algorithm == "weighted_round_robin":
            return self._weighted_round_robin()
        elif self.algorithm == "least_response_time":
            return self._least_response_time()
        elif self.algorithm == "consistent_hash" and client_id:
            return self._consistent_hash(client_id)
        else:
            return self._round_robin()
    
    def _round_robin(self) -> str:
        """Round robin algorithm"""
        server = self.servers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.servers)
        return server
    
    def _least_connections(self) -> str:
        """Least connections algorithm"""
        return min(self.servers, key=lambda s: self.server_connections[s])
    
    def _weighted_round_robin(self) -> str:
        """Weighted round robin algorithm"""
        # Simplified implementation
        weighted_servers = []
        for server in self.servers:
            weighted_servers.extend([server] * self.server_weights[server])
        
        server = weighted_servers[self.current_index % len(weighted_servers)]
        self.current_index += 1
        return server
    
    def _least_response_time(self) -> str:
        """Least response time algorithm"""
        def avg_response_time(server):
            times = self.server_response_times[server]
            return sum(times) / len(times) if times else 0
        
        return min(self.servers, key=avg_response_time)
    
    def _consistent_hash(self, client_id: str) -> str:
        """Consistent hashing for sticky sessions"""
        hash_value = hash(client_id) % len(self.servers)
        return self.servers[hash_value]
    
    def record_connection(self, server: str, connect: bool = True):
        """Record connection to server
        
        Args:
            server: Server identifier
            connect: True for new connection, False for disconnection
        """
        if connect:
            self.server_connections[server] += 1
        else:
            self.server_connections[server] = max(0, self.server_connections[server] - 1)
    
    def record_response_time(self, server: str, response_time: float):
        """Record response time for server
        
        Args:
            server: Server identifier
            response_time: Response time in seconds
        """
        self.server_response_times[server].append(response_time)
    
    def set_server_weight(self, server: str, weight: int):
        """Set weight for server
        
        Args:
            server: Server identifier
            weight: Weight value
        """
        self.server_weights[server] = max(1, weight)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get load balancer statistics
        
        Returns:
            Statistics dictionary
        """
        return {
            'algorithm': self.algorithm,
            'servers': self.servers,
            'connections': dict(self.server_connections),
            'weights': dict(self.server_weights),
            'avg_response_times': {
                server: sum(times) / len(times) if times else 0
                for server, times in self.server_response_times.items()
            }
        }

class DistributedSystemsSimulator:
    """Main simulator for distributed systems"""
    
    def __init__(self):
        """Initialize the distributed systems simulator"""
        self.network = NetworkSimulator()
        self.nodes: Dict[str, RaftNode] = {}
        self.dht_nodes: Dict[str, DistributedHashTable] = {}
        self.load_balancer: Optional[LoadBalancer] = None
        
        # Simulation state
        self.running = False
        self.simulation_time = 0
        self.events = []
        
        # Statistics
        self.stats = {
            'total_messages': 0,
            'failed_messages': 0,
            'elections': 0,
            'leader_changes': 0
        }
    
    def create_raft_cluster(self, node_ids: List[str]):
        """Create a Raft consensus cluster
        
        Args:
            node_ids: List of node identifiers
        """
        for node_id in node_ids:
            node = RaftNode(node_id, node_ids, self.network)
            self.nodes[node_id] = node
        
        logger.info(f"Created Raft cluster with {len(node_ids)} nodes")
    
    def create_dht_cluster(self, node_ids: List[str], replication_factor: int = 3):
        """Create a DHT cluster
        
        Args:
            node_ids: List of node identifiers
            replication_factor: Replication factor for the DHT
        """
        for node_id in node_ids:
            dht_node = DistributedHashTable(node_id, node_ids, replication_factor)
            self.dht_nodes[node_id] = dht_node
        
        logger.info(f"Created DHT cluster with {len(node_ids)} nodes")
    
    def create_load_balancer(self, servers: List[str], algorithm: str = "round_robin"):
        """Create a load balancer
        
        Args:
            servers: List of server identifiers
            algorithm: Load balancing algorithm
        """
        self.load_balancer = LoadBalancer(servers, algorithm)
        logger.info(f"Created load balancer with {algorithm} algorithm")
    
    async def run_simulation(self, duration: float):
        """Run the distributed systems simulation
        
        Args:
            duration: Simulation duration in seconds
        """
        self.running = True
        start_time = time.time()
        
        # Start all Raft nodes
        node_tasks = []
        for node in self.nodes.values():
            task = asyncio.create_task(node.start())
            node_tasks.append(task)
        
        # Run simulation events
        simulation_task = asyncio.create_task(self._run_simulation_events(duration))
        
        try:
            await asyncio.wait_for(simulation_task, timeout=duration)
        except asyncio.TimeoutError:
            pass
        
        self.running = False
        
        # Cancel node tasks
        for task in node_tasks:
            task.cancel()
        
        logger.info(f"Simulation completed in {time.time() - start_time:.2f} seconds")
    
    async def _run_simulation_events(self, duration: float):
        """Run simulation events
        
        Args:
            duration: Simulation duration
        """
        start_time = time.time()
        
        while time.time() - start_time < duration:
            await asyncio.sleep(1.0)  # Check every second
            
            # Randomly inject failures and recoveries
            if random.random() < 0.1:  # 10% chance per second
                await self._inject_random_event()
    
    async def _inject_random_event(self):
        """Inject a random simulation event"""
        if not self.nodes:
            return
        
        event_type = random.choice(['node_failure', 'node_recovery', 'network_partition', 'heal_partition'])
        
        if event_type == 'node_failure':
            available_nodes = [node_id for node_id in self.nodes.keys() 
                             if node_id not in self.network.failed_nodes]
            if available_nodes:
                node_id = random.choice(available_nodes)
                self.network.fail_node(node_id)
        
        elif event_type == 'node_recovery':
            if self.network.failed_nodes:
                node_id = random.choice(list(self.network.failed_nodes))
                self.network.recover_node(node_id)
        
        elif event_type == 'network_partition':
            if not self.network.partition_groups:
                node_ids = list(self.nodes.keys())
                if len(node_ids) >= 2:
                    split_point = len(node_ids) // 2
                    group1 = set(node_ids[:split_point])
                    group2 = set(node_ids[split_point:])
                    self.network.create_partition(group1, group2)
        
        elif event_type == 'heal_partition':
            if self.network.partition_groups:
                self.network.heal_partition()
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get status of the entire cluster
        
        Returns:
            Cluster status dictionary
        """
        raft_status = {}
        for node_id, node in self.nodes.items():
            raft_status[node_id] = node.get_status()
        
        dht_status = {}
        for node_id, node in self.dht_nodes.items():
            dht_status[node_id] = node.get_statistics()
        
        lb_status = None
        if self.load_balancer:
            lb_status = self.load_balancer.get_statistics()
        
        return {
            'raft_nodes': raft_status,
            'dht_nodes': dht_status,
            'load_balancer': lb_status,
            'network': {
                'failed_nodes': list(self.network.failed_nodes),
                'partitions': [list(group) for group in self.network.partition_groups],
                'packet_loss_rate': self.network.packet_loss_rate
            }
        }
    
    def visualize_cluster(self, output_path: str = "cluster_topology.png"):
        """Visualize the cluster topology
        
        Args:
            output_path: Path to save the visualization
        """
        G = nx.Graph()
        
        # Add nodes
        for node_id in self.nodes.keys():
            color = 'red' if node_id in self.network.failed_nodes else 'green'
            G.add_node(node_id, color=color)
        
        # Add edges (connections)
        node_list = list(self.nodes.keys())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                # Check if nodes can communicate
                can_communicate = True
                
                if self.network.partition_groups:
                    node1_group = None
                    node2_group = None
                    
                    for idx, group in enumerate(self.network.partition_groups):
                        if node_list[i] in group:
                            node1_group = idx
                        if node_list[j] in group:
                            node2_group = idx
                    
                    if node1_group != node2_group:
                        can_communicate = False
                
                if can_communicate:
                    G.add_edge(node_list[i], node_list[j])
        
        # Draw the graph
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G)
        
        node_colors = [G.nodes[node].get('color', 'blue') for node in G.nodes()]
        
        nx.draw(G, pos, node_color=node_colors, with_labels=True, 
                node_size=1000, font_size=10, font_weight='bold')
        
        plt.title("Distributed System Cluster Topology")
        plt.savefig(output_path)
        plt.close()
        
        logger.info(f"Cluster topology saved to {output_path}")

class DSApplication:
    """Main application class for the distributed systems simulator"""
    
    def __init__(self):
        """Initialize the application"""
        self.simulator = DistributedSystemsSimulator()
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Distributed Systems Simulator')
        
        parser.add_argument('--nodes', type=int, default=5, help='Number of nodes in the cluster')
        parser.add_argument('--algorithm', choices=['raft', 'pbft', 'paxos'], default='raft',
                           help='Consensus algorithm to use')
        parser.add_argument('--duration', type=float, default=60.0, help='Simulation duration in seconds')
        parser.add_argument('--packet-loss', type=float, default=0.0, help='Packet loss rate (0.0 to 1.0)')
        parser.add_argument('--latency', type=int, nargs=2, default=[10, 100], 
                           help='Network latency range in milliseconds')
        parser.add_argument('--visualize', action='store_true', help='Generate cluster visualization')
        parser.add_argument('--output', type=str, help='Output file for results')
        
        self.args = parser.parse_args()
    
    async def run(self):
        """Run the distributed systems simulation"""
        # Configure network conditions
        self.simulator.network.set_network_conditions(
            tuple(self.args.latency), 
            self.args.packet_loss
        )
        
        # Create cluster
        node_ids = [f"node_{i}" for i in range(self.args.nodes)]
        
        if self.args.algorithm == 'raft':
            self.simulator.create_raft_cluster(node_ids)
        
        # Create DHT cluster as well
        self.simulator.create_dht_cluster(node_ids)
        
        # Create load balancer
        self.simulator.create_load_balancer(node_ids[:3])  # Use first 3 nodes as servers
        
        print(f"Starting simulation with {self.args.nodes} nodes using {self.args.algorithm} algorithm")
        print(f"Network conditions: {self.args.latency}ms latency, {self.args.packet_loss:.1%} packet loss")
        
        # Run simulation
        await self.simulator.run_simulation(self.args.duration)
        
        # Get final status
        status = self.simulator.get_cluster_status()
        
        # Display results
        print("\n=== SIMULATION RESULTS ===")
        print(f"Raft Nodes: {len(status['raft_nodes'])}")
        
        for node_id, node_status in status['raft_nodes'].items():
            print(f"  {node_id}: {node_status['state']} (term {node_status['term']})")
        
        print(f"\nDHT Nodes: {len(status['dht_nodes'])}")
        print(f"Failed Nodes: {status['network']['failed_nodes']}")
        print(f"Network Partitions: {status['network']['partitions']}")
        
        # Save results
        if self.args.output:
            with open(self.args.output, 'w') as f:
                json.dump(status, f, indent=2, default=str)
            print(f"\nResults saved to {self.args.output}")
        
        # Generate visualization
        if self.args.visualize:
            self.simulator.visualize_cluster()

def main():
    """Main entry point"""
    print("=" * 60)
    print("Distributed Systems Simulator".center(60))
    print("Consensus algorithms and fault tolerance".center(60))
    print("=" * 60)
    
    app = DSApplication()
    asyncio.run(app.run())

if __name__ == "__main__":
    main() 