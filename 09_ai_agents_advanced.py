"""
Bài 9: AI Agent System với Neural Network và Behavioral Trees
Chủ đề: Protocol Classes, Advanced Generics, Neural Networks, Behavioral AI

Mục tiêu: Tạo hệ thống AI agents với machine learning và behavioral trees
"""

import math
import random
import time
import json
import threading
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import (
    Dict, List, Tuple, Optional, Any, Callable, Protocol, TypeVar, Generic,
    Union, Set, runtime_checkable
)
from dataclasses import dataclass, field
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, Future

# TYPE DEFINITIONS
T = TypeVar('T')
NodeType = TypeVar('NodeType', bound='BehaviorNode')

# PROTOCOLS
@runtime_checkable
class Learnable(Protocol):
    """Protocol cho các objects có thể học"""
    
    def learn(self, experience: 'Experience') -> None:
        """Học từ experience"""
        ...
    
    def predict(self, input_data: List[float]) -> List[float]:
        """Dự đoán output từ input"""
        ...

@runtime_checkable
class Evaluable(Protocol):
    """Protocol cho các objects có thể đánh giá performance"""
    
    def evaluate(self, test_data: List[Tuple[List[float], List[float]]]) -> float:
        """Đánh giá performance"""
        ...

@runtime_checkable
class Serializable(Protocol):
    """Protocol cho serialization"""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Serializable':
        """Create from dictionary"""
        ...

# ENUMS
class NodeStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    RUNNING = auto()
    INVALID = auto()

class AgentState(Enum):
    IDLE = auto()
    THINKING = auto()
    ACTING = auto()
    LEARNING = auto()
    DEAD = auto()

class ActivationFunction(Enum):
    SIGMOID = "sigmoid"
    TANH = "tanh"
    RELU = "relu"
    LEAKY_RELU = "leaky_relu"
    SOFTMAX = "softmax"

# DATA STRUCTURES
@dataclass
class Vector3:
    """3D Vector với các phép toán"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    def __add__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3') -> 'Vector3':
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)
    
    def normalized(self) -> 'Vector3':
        mag = self.magnitude()
        return self / mag if mag > 0 else Vector3()
    
    def __truediv__(self, scalar: float) -> 'Vector3':
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

@dataclass
class Experience:
    """Experience cho reinforcement learning"""
    state: List[float]
    action: int
    reward: float
    next_state: List[float]
    done: bool
    timestamp: float = field(default_factory=time.time)

@dataclass
class Perception:
    """Thông tin cảm nhận của agent"""
    position: Vector3
    nearby_objects: List[Dict[str, Any]]
    health: float
    energy: float
    resources: Dict[str, int]
    sensors: Dict[str, float]

# NEURAL NETWORK IMPLEMENTATION (Simplified without numpy)
class ActivationFunctions:
    """Utility class cho activation functions"""
    
    @staticmethod
    def sigmoid(x):
        """Sigmoid activation"""
        if isinstance(x, list):
            return [1 / (1 + math.exp(-max(-500, min(500, val)))) for val in x]
        return 1 / (1 + math.exp(-max(-500, min(500, x))))
    
    @staticmethod
    def tanh(x):
        """Tanh activation"""
        if isinstance(x, list):
            return [math.tanh(val) for val in x]
        return math.tanh(x)
    
    @staticmethod
    def relu(x):
        """ReLU activation"""
        if isinstance(x, list):
            return [max(0, val) for val in x]
        return max(0, x)
    
    @staticmethod
    def leaky_relu(x, alpha=0.01):
        """Leaky ReLU activation"""
        if isinstance(x, list):
            return [val if val > 0 else alpha * val for val in x]
        return x if x > 0 else alpha * x
    
    @staticmethod
    def softmax(x):
        """Softmax activation"""
        if not isinstance(x, list):
            return [1.0]
        
        max_x = max(x)
        exp_x = [math.exp(val - max_x) for val in x]
        sum_exp = sum(exp_x)
        return [val / sum_exp for val in exp_x]
    
    @classmethod
    def get_function(cls, func_type: ActivationFunction):
        """Get activation function by type"""
        mapping = {
            ActivationFunction.SIGMOID: cls.sigmoid,
            ActivationFunction.TANH: cls.tanh,
            ActivationFunction.RELU: cls.relu,
            ActivationFunction.LEAKY_RELU: cls.leaky_relu,
            ActivationFunction.SOFTMAX: cls.softmax
        }
        return mapping.get(func_type, cls.relu)

class Layer:
    """Neural network layer (simplified)"""
    
    def __init__(self, input_size: int, output_size: int, 
                 activation: ActivationFunction = ActivationFunction.RELU):
        # Initialize weights randomly
        self.weights = [[random.uniform(-0.1, 0.1) for _ in range(output_size)] 
                       for _ in range(input_size)]
        self.biases = [0.0] * output_size
        self.activation_func = ActivationFunctions.get_function(activation)
        self.activation_type = activation
        
        # For backpropagation
        self.last_input = None
        self.last_output = None
    
    def forward(self, input_data: List[float]) -> List[float]:
        """Forward pass"""
        self.last_input = input_data[:]
        
        # Matrix multiplication: input * weights + bias
        output = []
        for j in range(len(self.weights[0])):  # For each output neuron
            weighted_sum = self.biases[j]
            for i in range(len(input_data)):
                weighted_sum += input_data[i] * self.weights[i][j]
            output.append(weighted_sum)
        
        # Apply activation function
        self.last_output = self.activation_func(output)
        return self.last_output
    
    def backward(self, gradient: List[float], learning_rate: float = 0.01) -> List[float]:
        """Backward pass (simplified)"""
        if not self.last_input or not self.last_output:
            return [0.0] * len(self.weights)
        
        # Update weights and biases (simplified)
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                self.weights[i][j] -= learning_rate * gradient[j] * self.last_input[i]
        
        for j in range(len(self.biases)):
            self.biases[j] -= learning_rate * gradient[j]
        
        # Return input gradient (simplified)
        input_gradient = [0.0] * len(self.weights)
        for i in range(len(input_gradient)):
            for j in range(len(gradient)):
                input_gradient[i] += gradient[j] * self.weights[i][j]
        
        return input_gradient

class NeuralNetwork:
    """Simple neural network implementation"""
    
    def __init__(self, layer_sizes: List[int], 
                 activations: List[ActivationFunction] = None):
        self.layers = []
        
        if activations is None:
            activations = [ActivationFunction.RELU] * (len(layer_sizes) - 2) + [ActivationFunction.SIGMOID]
        
        for i in range(len(layer_sizes) - 1):
            layer = Layer(layer_sizes[i], layer_sizes[i + 1], activations[i])
            self.layers.append(layer)
        
        self.training_history = []
    
    def forward(self, input_data: List[float]) -> List[float]:
        """Forward pass through network"""
        current_input = input_data[:]
        
        for layer in self.layers:
            current_input = layer.forward(current_input)
        
        return current_input
    
    def train_step(self, input_data: List[float], target: List[float], 
                  learning_rate: float = 0.01) -> float:
        """Single training step"""
        # Forward pass
        prediction = self.forward(input_data)
        
        # Calculate loss (MSE)
        loss = sum((p - t) ** 2 for p, t in zip(prediction, target)) / len(target)
        
        # Backward pass (simplified)
        gradient = [(p - t) * 2 / len(target) for p, t in zip(prediction, target)]
        
        for layer in reversed(self.layers):
            gradient = layer.backward(gradient, learning_rate)
        
        return loss
    
    def train(self, training_data: List[Tuple[List[float], List[float]]], 
              epochs: int = 100, learning_rate: float = 0.01):
        """Train the network"""
        print(f"🧠 Training neural network for {epochs} epochs...")
        
        for epoch in range(epochs):
            total_loss = 0
            
            for input_data, target in training_data:
                loss = self.train_step(input_data, target, learning_rate)
                total_loss += loss
            
            avg_loss = total_loss / len(training_data)
            self.training_history.append(avg_loss)
            
            if epoch % 20 == 0:
                print(f"   Epoch {epoch}: Loss = {avg_loss:.4f}")
    
    def predict(self, input_data: List[float]) -> List[float]:
        """Make prediction"""
        return self.forward(input_data)
    
    def evaluate(self, test_data: List[Tuple[List[float], List[float]]]) -> float:
        """Evaluate network performance"""
        total_loss = 0
        
        for input_data, target in test_data:
            prediction = self.predict(input_data)
            loss = sum((p - t) ** 2 for p, t in zip(prediction, target)) / len(target)
            total_loss += loss
        
        return total_loss / len(test_data)

# BEHAVIORAL TREE SYSTEM
class BehaviorNode(ABC):
    """Base class cho behavior tree nodes"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.status = NodeStatus.INVALID
        self.children: List['BehaviorNode'] = []
        self.parent: Optional['BehaviorNode'] = None
        self.execution_count = 0
        self.success_count = 0
    
    @abstractmethod
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        """Execute node logic"""
        self.execution_count += 1
        pass
    
    def add_child(self, child: 'BehaviorNode'):
        """Add child node"""
        child.parent = self
        self.children.append(child)
        return self
    
    def get_success_rate(self) -> float:
        """Get success rate"""
        return self.success_count / self.execution_count if self.execution_count > 0 else 0.0

class Sequence(BehaviorNode):
    """Sequence node - succeeds if all children succeed"""
    
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        super().tick(agent)
        
        for child in self.children:
            result = child.tick(agent)
            
            if result == NodeStatus.FAILURE:
                self.status = NodeStatus.FAILURE
                return self.status
            elif result == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status
        
        self.status = NodeStatus.SUCCESS
        self.success_count += 1
        return self.status

class Selector(BehaviorNode):
    """Selector node - succeeds if any child succeeds"""
    
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        super().tick(agent)
        
        for child in self.children:
            result = child.tick(agent)
            
            if result == NodeStatus.SUCCESS:
                self.status = NodeStatus.SUCCESS
                self.success_count += 1
                return self.status
            elif result == NodeStatus.RUNNING:
                self.status = NodeStatus.RUNNING
                return self.status
        
        self.status = NodeStatus.FAILURE
        return self.status

class Condition(BehaviorNode):
    """Condition node"""
    
    def __init__(self, name: str, condition_func: Callable[['AIAgent'], bool]):
        super().__init__(name)
        self.condition_func = condition_func
    
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        super().tick(agent)
        
        if self.condition_func(agent):
            self.status = NodeStatus.SUCCESS
            self.success_count += 1
        else:
            self.status = NodeStatus.FAILURE
        
        return self.status

class Action(BehaviorNode):
    """Action node"""
    
    def __init__(self, name: str, action_func: Callable[['AIAgent'], NodeStatus]):
        super().__init__(name)
        self.action_func = action_func
    
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        super().tick(agent)
        
        self.status = self.action_func(agent)
        if self.status == NodeStatus.SUCCESS:
            self.success_count += 1
        
        return self.status

class BehaviorTree:
    """Behavior tree container"""
    
    def __init__(self, root: BehaviorNode):
        self.root = root
        self.execution_count = 0
        self.last_status = NodeStatus.INVALID
    
    def tick(self, agent: 'AIAgent') -> NodeStatus:
        """Execute behavior tree"""
        self.execution_count += 1
        self.last_status = self.root.tick(agent)
        return self.last_status
    
    def get_node_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all nodes"""
        stats = {}
        
        def collect_stats(node: BehaviorNode):
            stats[node.name or f"{type(node).__name__}_{id(node)}"] = {
                'type': type(node).__name__,
                'execution_count': node.execution_count,
                'success_count': node.success_count,
                'success_rate': node.get_success_rate()
            }
            
            for child in node.children:
                collect_stats(child)
        
        collect_stats(self.root)
        return stats

# AI AGENT SYSTEM
class Memory(Generic[T]):
    """Generic memory system for agents"""
    
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.data: deque[T] = deque(maxlen=capacity)
        self.importance_weights: deque[float] = deque(maxlen=capacity)
    
    def store(self, item: T, importance: float = 1.0):
        """Store item with importance weight"""
        self.data.append(item)
        self.importance_weights.append(importance)
    
    def recall(self, count: int = 10, min_importance: float = 0.0) -> List[T]:
        """Recall items based on importance"""
        items_with_weights = list(zip(self.data, self.importance_weights))
        
        # Filter by minimum importance
        filtered = [(item, weight) for item, weight in items_with_weights 
                   if weight >= min_importance]
        
        # Sort by importance and return top items
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in filtered[:count]]
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'size': len(self.data),
            'capacity': self.capacity,
            'avg_importance': sum(self.importance_weights) / len(self.importance_weights) if self.importance_weights else 0
        }

class AIAgent:
    """Advanced AI Agent với neural network và behavior trees"""
    
    def __init__(self, agent_id: str, brain_architecture: List[int] = None):
        self.agent_id = agent_id
        self.state = AgentState.IDLE
        
        # Neural network brain
        if brain_architecture is None:
            brain_architecture = [10, 16, 8, 4]  # Default architecture
        
        self.brain = NeuralNetwork(brain_architecture)
        
        # Memory systems
        self.short_term_memory = Memory[Perception](capacity=100)
        self.long_term_memory = Memory[Experience](capacity=1000)
        self.episodic_memory = Memory[Dict[str, Any]](capacity=500)
        
        # Current state
        self.perception = Perception(
            position=Vector3(),
            nearby_objects=[],
            health=100.0,
            energy=100.0,
            resources={},
            sensors={}
        )
        
        # Behavior tree
        self.behavior_tree = self._create_default_behavior_tree()
        
        # Learning parameters
        self.learning_rate = 0.01
        self.exploration_rate = 0.1
        self.reward_history = []
        
        # Performance tracking
        self.actions_taken = 0
        self.successful_actions = 0
        self.total_reward = 0.0
        
        # Threading
        self.thinking_thread: Optional[Future] = None
        self.is_thinking = False
    
    def _create_default_behavior_tree(self) -> BehaviorTree:
        """Create default behavior tree"""
        
        # Conditions
        low_health = Condition("LowHealth", lambda agent: agent.perception.health < 30)
        low_energy = Condition("LowEnergy", lambda agent: agent.perception.energy < 20)
        enemy_nearby = Condition("EnemyNearby", lambda agent: any(
            obj.get('type') == 'enemy' for obj in agent.perception.nearby_objects
        ))
        
        # Actions
        def rest_action(agent: 'AIAgent') -> NodeStatus:
            agent.perception.energy = min(100, agent.perception.energy + 10)
            print(f"🛌 {agent.agent_id} is resting (Energy: {agent.perception.energy})")
            return NodeStatus.SUCCESS
        
        def heal_action(agent: 'AIAgent') -> NodeStatus:
            if agent.perception.resources.get('healing_potion', 0) > 0:
                agent.perception.health = min(100, agent.perception.health + 20)
                agent.perception.resources['healing_potion'] -= 1
                print(f"🩹 {agent.agent_id} used healing potion (Health: {agent.perception.health})")
                return NodeStatus.SUCCESS
            return NodeStatus.FAILURE
        
        def flee_action(agent: 'AIAgent') -> NodeStatus:
            print(f"🏃 {agent.agent_id} is fleeing from danger!")
            # Simulate movement
            agent.perception.position += Vector3(random.uniform(-5, 5), random.uniform(-5, 5), 0)
            return NodeStatus.SUCCESS
        
        def explore_action(agent: 'AIAgent') -> NodeStatus:
            print(f"🗺️ {agent.agent_id} is exploring")
            # Use neural network to decide exploration direction
            input_data = [
                agent.perception.position.x, agent.perception.position.y,
                agent.perception.health, agent.perception.energy,
                len(agent.perception.nearby_objects)
            ] + [0] * 5  # Pad to match brain input size
            
            decision = agent.brain.predict(input_data[:10])  # Take first 10
            
            # Interpret decision as movement
            if decision[0] > 0.5:
                agent.perception.position += Vector3(random.uniform(-3, 3), random.uniform(-3, 3), 0)
            
            return NodeStatus.SUCCESS
        
        # Create tree structure
        survival = Sequence("Survival")
        
        # Health management
        health_check = Selector("HealthCheck")
        heal_sequence = Sequence("HealSequence")
        heal_sequence.add_child(low_health).add_child(Action("Heal", heal_action))
        health_check.add_child(heal_sequence)
        
        # Energy management
        energy_check = Selector("EnergyCheck")
        rest_sequence = Sequence("RestSequence")
        rest_sequence.add_child(low_energy).add_child(Action("Rest", rest_action))
        energy_check.add_child(rest_sequence)
        
        # Danger response
        danger_check = Selector("DangerCheck")
        flee_sequence = Sequence("FleeSequence")
        flee_sequence.add_child(enemy_nearby).add_child(Action("Flee", flee_action))
        danger_check.add_child(flee_sequence)
        
        # Main behavior
        main_behavior = Selector("MainBehavior")
        main_behavior.add_child(danger_check)
        main_behavior.add_child(health_check)
        main_behavior.add_child(energy_check)
        main_behavior.add_child(Action("Explore", explore_action))
        
        return BehaviorTree(main_behavior)
    
    def perceive(self, environment_data: Dict[str, Any]):
        """Update perception from environment"""
        # Update perception based on environment data
        if 'nearby_objects' in environment_data:
            self.perception.nearby_objects = environment_data['nearby_objects']
        
        if 'position' in environment_data:
            pos_data = environment_data['position']
            self.perception.position = Vector3(pos_data[0], pos_data[1], pos_data.get(2, 0))
        
        # Store in short-term memory
        self.short_term_memory.store(self.perception, importance=1.0)
    
    def think(self) -> Dict[str, Any]:
        """High-level thinking process"""
        self.state = AgentState.THINKING
        self.is_thinking = True
        
        try:
            # Analyze current situation
            situation_vector = self._encode_situation()
            
            # Use neural network to evaluate situation
            evaluation = self.brain.predict(situation_vector)
            
            # Make decision based on evaluation
            decision = {
                'action_confidence': evaluation[0] if len(evaluation) > 0 else 0.5,
                'exploration_desire': evaluation[1] if len(evaluation) > 1 else 0.3,
                'risk_assessment': evaluation[2] if len(evaluation) > 2 else 0.2,
                'resource_priority': evaluation[3] if len(evaluation) > 3 else 0.4
            }
            
            # Store decision in episodic memory
            episode = {
                'timestamp': time.time(),
                'situation': situation_vector,
                'decision': decision,
                'perception': self.perception
            }
            self.episodic_memory.store(episode, importance=decision['action_confidence'])
            
            return decision
            
        finally:
            self.is_thinking = False
    
    def _encode_situation(self) -> List[float]:
        """Encode current situation as vector"""
        # Create feature vector from perception
        features = [
            self.perception.position.x / 100.0,  # Normalize position
            self.perception.position.y / 100.0,
            self.perception.health / 100.0,
            self.perception.energy / 100.0,
            len(self.perception.nearby_objects) / 10.0,  # Normalize object count
            1.0 if any(obj.get('type') == 'enemy' for obj in self.perception.nearby_objects) else 0.0,
            1.0 if any(obj.get('type') == 'food' for obj in self.perception.nearby_objects) else 0.0,
            sum(self.perception.resources.values()) / 10.0,  # Normalize resources
            len(self.short_term_memory.data) / 100.0,
            self.total_reward / 1000.0  # Normalize reward
        ]
        
        return features
    
    def act(self) -> NodeStatus:
        """Execute behavior tree"""
        self.state = AgentState.ACTING
        self.actions_taken += 1
        
        # Execute behavior tree
        result = self.behavior_tree.tick(self)
        
        if result == NodeStatus.SUCCESS:
            self.successful_actions += 1
        
        return result
    
    def learn(self, experience: Experience):
        """Learn from experience"""
        self.state = AgentState.LEARNING
        
        # Store experience
        self.long_term_memory.store(experience, importance=abs(experience.reward))
        
        # Update reward tracking
        self.reward_history.append(experience.reward)
        self.total_reward += experience.reward
        
        # Train neural network if we have enough experiences
        if len(self.long_term_memory.data) >= 10:
            self._train_from_experiences()
        
        print(f"🎓 {self.agent_id} learned from experience (Reward: {experience.reward:.2f})")
    
    def _train_from_experiences(self):
        """Train neural network from stored experiences"""
        recent_experiences = self.long_term_memory.recall(50, min_importance=0.1)
        
        if len(recent_experiences) < 5:
            return
        
        # Prepare training data
        training_data = []
        for exp in recent_experiences:
            # Input: current state
            input_data = exp.state[:10]  # Take first 10 features
            
            # Target: expected future value
            target = [exp.reward / 10.0]  # Normalize reward
            if not exp.done and len(exp.next_state) >= 4:
                # Add discounted future value estimate
                target.extend([exp.next_state[i] / 100.0 for i in range(min(3, len(exp.next_state)))])
            else:
                target.extend([0.0, 0.0, 0.0])
            
            training_data.append((input_data, target))
        
        # Train network
        self.brain.train(training_data, epochs=10, learning_rate=self.learning_rate)
    
    def update(self, delta_time: float):
        """Update agent state"""
        # Passive energy consumption
        self.perception.energy = max(0, self.perception.energy - delta_time * 2)
        
        # Start thinking if idle and not already thinking
        if self.state == AgentState.IDLE and not self.is_thinking:
            self.state = AgentState.THINKING
        
        # Execute behavior
        if self.state != AgentState.LEARNING and not self.is_thinking:
            self.act()
            self.state = AgentState.IDLE
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            'agent_id': self.agent_id,
            'state': self.state.name,
            'health': self.perception.health,
            'energy': self.perception.energy,
            'position': [self.perception.position.x, self.perception.position.y, self.perception.position.z],
            'actions_taken': self.actions_taken,
            'successful_actions': self.successful_actions,
            'success_rate': self.successful_actions / self.actions_taken if self.actions_taken > 0 else 0,
            'total_reward': self.total_reward,
            'average_reward': sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0,
            'memory_stats': {
                'short_term': self.short_term_memory.get_stats(),
                'long_term': self.long_term_memory.get_stats(),
                'episodic': self.episodic_memory.get_stats()
            },
            'behavior_tree_stats': self.behavior_tree.get_node_stats()
        }

class AIEnvironment:
    """Environment cho AI agents"""
    
    def __init__(self, width: float = 1000, height: float = 1000):
        self.width = width
        self.height = height
        self.agents: Dict[str, AIAgent] = {}
        self.objects: List[Dict[str, Any]] = []
        self.time_step = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    def add_agent(self, agent: AIAgent):
        """Add agent to environment"""
        self.agents[agent.agent_id] = agent
        print(f"🤖 Added agent {agent.agent_id} to environment")
    
    def add_object(self, obj_type: str, position: Vector3, properties: Dict[str, Any] = None):
        """Add object to environment"""
        obj = {
            'id': f"{obj_type}_{len(self.objects)}",
            'type': obj_type,
            'position': position,
            'properties': properties or {}
        }
        self.objects.append(obj)
    
    def get_nearby_objects(self, position: Vector3, radius: float = 50.0) -> List[Dict[str, Any]]:
        """Get objects near a position"""
        nearby = []
        for obj in self.objects:
            distance = position.distance_to(obj['position'])
            if distance <= radius:
                nearby.append({
                    **obj,
                    'distance': distance
                })
        return nearby
    
    def update_agent_perceptions(self):
        """Update all agents' perceptions"""
        for agent in self.agents.values():
            nearby_objects = self.get_nearby_objects(agent.perception.position)
            
            environment_data = {
                'nearby_objects': nearby_objects,
                'position': [agent.perception.position.x, agent.perception.position.y, agent.perception.position.z],
                'time_step': self.time_step
            }
            
            agent.perceive(environment_data)
    
    def simulate_step(self, delta_time: float = 1.0):
        """Simulate one time step"""
        self.time_step += 1
        
        # Update perceptions
        self.update_agent_perceptions()
        
        # Update all agents
        for agent in self.agents.values():
            agent.update(delta_time)
        
        # Generate random rewards based on agent actions
        self._generate_rewards()
    
    def _generate_rewards(self):
        """Generate rewards for agents based on their actions"""
        for agent in self.agents.values():
            # Simple reward system
            reward = 0.0
            
            # Reward for maintaining health
            if agent.perception.health > 70:
                reward += 0.1
            
            # Reward for maintaining energy
            if agent.perception.energy > 50:
                reward += 0.05
            
            # Penalty for low health/energy
            if agent.perception.health < 30:
                reward -= 0.2
            if agent.perception.energy < 20:
                reward -= 0.1
            
            # Random exploration reward
            reward += random.uniform(-0.05, 0.1)
            
            # Create experience
            if len(agent.short_term_memory.data) >= 2:
                current_state = agent._encode_situation()
                previous_perception = list(agent.short_term_memory.data)[-2]
                previous_state = [
                    previous_perception.position.x / 100.0,
                    previous_perception.position.y / 100.0,
                    previous_perception.health / 100.0,
                    previous_perception.energy / 100.0,
                ] + [0.0] * 6  # Pad to match current state size
                
                experience = Experience(
                    state=previous_state,
                    action=random.randint(0, 3),  # Simulated action
                    reward=reward,
                    next_state=current_state,
                    done=agent.perception.health <= 0
                )
                
                agent.learn(experience)
    
    def get_environment_stats(self) -> Dict[str, Any]:
        """Get environment statistics"""
        return {
            'time_step': self.time_step,
            'num_agents': len(self.agents),
            'num_objects': len(self.objects),
            'environment_size': [self.width, self.height],
            'agents': {agent_id: agent.get_stats() for agent_id, agent in self.agents.items()}
        }

def main():
    print("🧠 AI AGENT SYSTEM VỚI NEURAL NETWORKS VÀ BEHAVIORAL TREES 🧠")
    
    # Create environment
    environment = AIEnvironment(1000, 1000)
    
    # Add some objects to the environment
    for i in range(10):
        environment.add_object("food", Vector3(
            random.uniform(-500, 500),
            random.uniform(-500, 500),
            0
        ), {'nutrition': random.uniform(10, 30)})
    
    for i in range(5):
        environment.add_object("enemy", Vector3(
            random.uniform(-500, 500),
            random.uniform(-500, 500),
            0
        ), {'aggression': random.uniform(0.3, 0.8)})
    
    # Create AI agents
    agents = []
    for i in range(3):
        agent = AIAgent(f"Agent_{i+1}", brain_architecture=[10, 16, 12, 4])
        
        # Set random starting position
        agent.perception.position = Vector3(
            random.uniform(-200, 200),
            random.uniform(-200, 200),
            0
        )
        
        # Give some starting resources
        agent.perception.resources = {
            'healing_potion': random.randint(1, 3),
            'food': random.randint(0, 2)
        }
        
        environment.add_agent(agent)
        agents.append(agent)
    
    print(f"\n🎮 RUNNING SIMULATION:")
    print("=" * 40)
    
    # Run simulation
    simulation_steps = 50
    for step in range(simulation_steps):
        print(f"\n--- Time Step {step + 1} ---")
        
        environment.simulate_step(delta_time=1.0)
        
        # Print some stats every 10 steps
        if (step + 1) % 10 == 0:
            print(f"\n📊 SIMULATION STATS (Step {step + 1}):")
            for agent in agents:
                stats = agent.get_stats()
                print(f"🤖 {stats['agent_id']}:")
                print(f"   Health: {stats['health']:.1f}, Energy: {stats['energy']:.1f}")
                print(f"   Success Rate: {stats['success_rate']:.2%}")
                print(f"   Average Reward: {stats['average_reward']:.3f}")
    
    print(f"\n📈 FINAL RESULTS:")
    print("=" * 30)
    
    # Final statistics
    env_stats = environment.get_environment_stats()
    
    print(f"🌍 Environment: {env_stats['time_step']} steps completed")
    print(f"🤖 Agents: {env_stats['num_agents']}")
    print(f"🎯 Objects: {env_stats['num_objects']}")
    
    print(f"\n🏆 AGENT PERFORMANCE:")
    for agent_id, stats in env_stats['agents'].items():
        print(f"\n{agent_id}:")
        print(f"   Final Health: {stats['health']:.1f}")
        print(f"   Final Energy: {stats['energy']:.1f}")
        print(f"   Actions Taken: {stats['actions_taken']}")
        print(f"   Success Rate: {stats['success_rate']:.2%}")
        print(f"   Total Reward: {stats['total_reward']:.2f}")
        print(f"   Average Reward: {stats['average_reward']:.3f}")
        
        # Memory stats
        print(f"   Memory Usage:")
        for mem_type, mem_stats in stats['memory_stats'].items():
            print(f"     {mem_type}: {mem_stats['size']}/{mem_stats['capacity']}")
    
    print(f"\n🌳 BEHAVIOR TREE ANALYSIS:")
    print("=" * 35)
    
    # Analyze behavior trees
    for agent in agents:
        print(f"\n{agent.agent_id} Behavior Tree:")
        tree_stats = agent.behavior_tree.get_node_stats()
        
        for node_name, node_stats in tree_stats.items():
            if node_stats['execution_count'] > 0:
                print(f"   {node_name}: {node_stats['success_rate']:.2%} success "
                      f"({node_stats['success_count']}/{node_stats['execution_count']})")
    
    print(f"\n🧹 Shutting down environment...")
    environment.executor.shutdown(wait=True)
    print("✅ Simulation completed!")

if __name__ == "__main__":
    main()
