"""
Bài 8: Game Engine với Component System và Event-Driven Architecture  
Chủ đề: Component Pattern, Event System, State Machines, Memory Management

Mục tiêu: Tạo một game engine đơn giản với kiến trúc component-based và event-driven
"""

import math
import time
import threading
import weakref
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Set, Optional, Any, Callable, TypeVar, Generic
from dataclasses import dataclass, field
from collections import defaultdict, deque
import uuid
import gc

# TYPE DEFINITIONS
T = TypeVar('T')
ComponentType = TypeVar('ComponentType', bound='Component')

# ENUMS
class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    LOADING = auto()

class EntityState(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    DESTROYED = auto()

class EventType(Enum):
    # Input events
    KEY_PRESSED = auto()
    KEY_RELEASED = auto()
    MOUSE_CLICKED = auto()
    MOUSE_MOVED = auto()
    
    # Game events
    ENTITY_CREATED = auto()
    ENTITY_DESTROYED = auto()
    COMPONENT_ADDED = auto()
    COMPONENT_REMOVED = auto()
    
    # Collision events
    COLLISION_STARTED = auto()
    COLLISION_ENDED = auto()
    
    # Game logic events
    PLAYER_DIED = auto()
    ENEMY_SPAWNED = auto()
    ITEM_COLLECTED = auto()
    LEVEL_COMPLETED = auto()

# DATA STRUCTURES
@dataclass
class Vector2:
    """2D Vector với các phép toán cơ bản"""
    x: float = 0.0
    y: float = 0.0
    
    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalized(self) -> 'Vector2':
        mag = self.magnitude()
        if mag == 0:
            return Vector2(0, 0)
        return self / mag
    
    def distance_to(self, other: 'Vector2') -> float:
        return (other - self).magnitude()
    
    def dot(self, other: 'Vector2') -> float:
        return self.x * other.x + self.y * other.y

@dataclass
class Event:
    """Base event class"""
    event_type: EventType
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    entity_id: Optional[str] = None

@dataclass
class Transform:
    """Transform data cho entity positioning"""
    position: Vector2 = field(default_factory=Vector2)
    rotation: float = 0.0
    scale: Vector2 = field(default_factory=lambda: Vector2(1.0, 1.0))

# MEMORY MANAGEMENT
class ObjectPool(Generic[T]):
    """Object pool để tái sử dụng objects"""
    
    def __init__(self, factory: Callable[[], T], initial_size: int = 10):
        self._factory = factory
        self._available: deque[T] = deque()
        self._in_use: Set[T] = set()
        
        # Pre-allocate objects
        for _ in range(initial_size):
            obj = self._factory()
            self._available.append(obj)
    
    def acquire(self) -> T:
        """Lấy object từ pool"""
        if self._available:
            obj = self._available.popleft()
        else:
            obj = self._factory()
        
        self._in_use.add(obj)
        return obj
    
    def release(self, obj: T):
        """Trả object về pool"""
        if obj in self._in_use:
            self._in_use.remove(obj)
            
            # Reset object nếu có phương thức reset
            if hasattr(obj, 'reset'):
                obj.reset()
            
            self._available.append(obj)
    
    def get_stats(self) -> Dict[str, int]:
        return {
            'available': len(self._available),
            'in_use': len(self._in_use),
            'total': len(self._available) + len(self._in_use)
        }

# EVENT SYSTEM
class EventManager:
    """Singleton event manager với weak references"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._listeners: Dict[EventType, List[weakref.ref]] = defaultdict(list)
            self._event_queue: deque[Event] = deque()
            self._processing = False
            self._stats = {
                'events_processed': 0,
                'listeners_count': 0
            }
            self._initialized = True
    
    def subscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Đăng ký lắng nghe event"""
        weak_callback = weakref.ref(callback)
        self._listeners[event_type].append(weak_callback)
        self._stats['listeners_count'] += 1
        print(f"📡 Subscribed to {event_type.name}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable[[Event], None]):
        """Hủy đăng ký lắng nghe event"""
        callback_ref = weakref.ref(callback)
        listeners = self._listeners[event_type]
        
        # Remove matching weak references
        to_remove = []
        for weak_ref in listeners:
            if weak_ref() is callback or weak_ref() is None:
                to_remove.append(weak_ref)
        
        for weak_ref in to_remove:
            listeners.remove(weak_ref)
            self._stats['listeners_count'] -= 1
    
    def emit(self, event: Event):
        """Phát event"""
        self._event_queue.append(event)
    
    def process_events(self):
        """Xử lý tất cả events trong queue"""
        if self._processing:
            return
        
        self._processing = True
        
        try:
            while self._event_queue:
                event = self._event_queue.popleft()
                self._dispatch_event(event)
                self._stats['events_processed'] += 1
        finally:
            self._processing = False
    
    def _dispatch_event(self, event: Event):
        """Gửi event đến các listeners"""
        listeners = self._listeners[event.event_type]
        
        # Clean up dead references và dispatch
        alive_listeners = []
        for weak_ref in listeners:
            callback = weak_ref()
            if callback is not None:
                alive_listeners.append(weak_ref)
                try:
                    callback(event)
                except Exception as e:
                    print(f"❌ Error in event handler: {e}")
            else:
                self._stats['listeners_count'] -= 1
        
        # Update listeners list
        self._listeners[event.event_type] = alive_listeners
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            'queued_events': len(self._event_queue),
            'event_types': len(self._listeners)
        }

# COMPONENT SYSTEM
class Component(ABC):
    """Base component class"""
    
    def __init__(self):
        self.entity_id: Optional[str] = None
        self.enabled = True
        self.created_at = time.time()
    
    @abstractmethod
    def update(self, delta_time: float):
        """Update component logic"""
        pass
    
    def reset(self):
        """Reset component for object pooling"""
        self.entity_id = None
        self.enabled = True

class TransformComponent(Component):
    """Component quản lý position, rotation, scale"""
    
    def __init__(self):
        super().__init__()
        self.transform = Transform()
        self.velocity = Vector2()
        self.angular_velocity = 0.0
    
    def update(self, delta_time: float):
        if not self.enabled:
            return
        
        # Update position based on velocity
        self.transform.position += self.velocity * delta_time
        
        # Update rotation
        self.transform.rotation += self.angular_velocity * delta_time
    
    def move_to(self, position: Vector2):
        """Di chuyển đến vị trí mới"""
        self.transform.position = position
    
    def translate(self, offset: Vector2):
        """Di chuyển theo offset"""
        self.transform.position += offset
    
    def rotate(self, angle: float):
        """Xoay thêm góc"""
        self.transform.rotation += angle
    
    def reset(self):
        super().reset()
        self.transform = Transform()
        self.velocity = Vector2()
        self.angular_velocity = 0.0

class RenderComponent(Component):
    """Component render graphics"""
    
    def __init__(self, sprite_name: str = "", color: str = "white"):
        super().__init__()
        self.sprite_name = sprite_name
        self.color = color
        self.visible = True
        self.layer = 0
        self.opacity = 1.0
    
    def update(self, delta_time: float):
        # Render components thường không cần update logic
        pass
    
    def set_sprite(self, sprite_name: str):
        self.sprite_name = sprite_name
    
    def set_color(self, color: str):
        self.color = color
    
    def reset(self):
        super().reset()
        self.sprite_name = ""
        self.color = "white"
        self.visible = True
        self.layer = 0
        self.opacity = 1.0

class PhysicsComponent(Component):
    """Component xử lý physics"""
    
    def __init__(self, mass: float = 1.0):
        super().__init__()
        self.mass = mass
        self.force = Vector2()
        self.drag = 0.98  # Air resistance
        self.bounce = 0.8  # Bounce factor
        self.is_static = False
    
    def update(self, delta_time: float):
        if not self.enabled or self.is_static:
            return
        
        # Get transform component
        entity = EntityManager().get_entity(self.entity_id)
        if not entity:
            return
        
        transform_comp = entity.get_component(TransformComponent)
        if not transform_comp:
            return
        
        # Apply force to velocity (F = ma, so a = F/m)
        if self.mass > 0:
            acceleration = self.force / self.mass
            transform_comp.velocity += acceleration * delta_time
        
        # Apply drag
        transform_comp.velocity *= self.drag
        
        # Reset force after applying
        self.force = Vector2()
    
    def apply_force(self, force: Vector2):
        """Áp dụng lực"""
        self.force += force
    
    def apply_impulse(self, impulse: Vector2):
        """Áp dụng xung lực (thay đổi velocity trực tiếp)"""
        entity = EntityManager().get_entity(self.entity_id)
        if entity:
            transform_comp = entity.get_component(TransformComponent)
            if transform_comp and self.mass > 0:
                transform_comp.velocity += impulse / self.mass
    
    def reset(self):
        super().reset()
        self.mass = 1.0
        self.force = Vector2()
        self.drag = 0.98
        self.bounce = 0.8
        self.is_static = False

class HealthComponent(Component):
    """Component quản lý health"""
    
    def __init__(self, max_health: float = 100.0):
        super().__init__()
        self.max_health = max_health
        self.current_health = max_health
        self.is_invulnerable = False
        self.invulnerability_time = 0.0
    
    def update(self, delta_time: float):
        if self.invulnerability_time > 0:
            self.invulnerability_time -= delta_time
            if self.invulnerability_time <= 0:
                self.is_invulnerable = False
    
    def take_damage(self, damage: float) -> bool:
        """Nhận damage, return True nếu chết"""
        if self.is_invulnerable or not self.enabled:
            return False
        
        self.current_health -= damage
        
        # Emit event
        event_manager = EventManager()
        event_manager.emit(Event(
            EventType.ENTITY_DESTROYED if self.current_health <= 0 else EventType.COLLISION_STARTED,
            {'entity_id': self.entity_id, 'damage': damage, 'health': self.current_health}
        ))
        
        return self.current_health <= 0
    
    def heal(self, amount: float):
        """Hồi máu"""
        self.current_health = min(self.max_health, self.current_health + amount)
    
    def set_invulnerable(self, duration: float):
        """Đặt trạng thái bất tử tạm thời"""
        self.is_invulnerable = True
        self.invulnerability_time = duration
    
    def reset(self):
        super().reset()
        self.current_health = self.max_health
        self.is_invulnerable = False
        self.invulnerability_time = 0.0

# ENTITY SYSTEM
class Entity:
    """Entity chứa các components"""
    
    def __init__(self, name: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name or f"Entity_{self.id[:8]}"
        self.state = EntityState.ACTIVE
        self.components: Dict[type, Component] = {}
        self.tags: Set[str] = set()
        self.created_at = time.time()
    
    def add_component(self, component: Component) -> 'Entity':
        """Thêm component"""
        component.entity_id = self.id
        self.components[type(component)] = component
        
        # Emit event
        EventManager().emit(Event(
            EventType.COMPONENT_ADDED,
            {'entity_id': self.id, 'component_type': type(component).__name__}
        ))
        
        return self
    
    def remove_component(self, component_type: type) -> bool:
        """Xóa component"""
        if component_type in self.components:
            del self.components[component_type]
            
            # Emit event
            EventManager().emit(Event(
                EventType.COMPONENT_REMOVED,
                {'entity_id': self.id, 'component_type': component_type.__name__}
            ))
            
            return True
        return False
    
    def get_component(self, component_type: type) -> Optional[Component]:
        """Lấy component"""
        return self.components.get(component_type)
    
    def has_component(self, component_type: type) -> bool:
        """Kiểm tra có component không"""
        return component_type in self.components
    
    def add_tag(self, tag: str):
        """Thêm tag"""
        self.tags.add(tag)
    
    def remove_tag(self, tag: str):
        """Xóa tag"""
        self.tags.discard(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Kiểm tra có tag không"""
        return tag in self.tags
    
    def update(self, delta_time: float):
        """Update tất cả components"""
        if self.state != EntityState.ACTIVE:
            return
        
        for component in self.components.values():
            component.update(delta_time)
    
    def destroy(self):
        """Destroy entity"""
        self.state = EntityState.DESTROYED
        
        # Emit event
        EventManager().emit(Event(
            EventType.ENTITY_DESTROYED,
            {'entity_id': self.id, 'name': self.name}
        ))

class EntityManager:
    """Singleton quản lý entities"""
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.entities: Dict[str, Entity] = {}
            self.entities_by_tag: Dict[str, Set[str]] = defaultdict(set)
            self.component_pools: Dict[type, ObjectPool] = {}
            self._stats = {
                'entities_created': 0,
                'entities_destroyed': 0
            }
            self._initialized = True
    
    def create_entity(self, name: str = "") -> Entity:
        """Tạo entity mới"""
        entity = Entity(name)
        self.entities[entity.id] = entity
        self._stats['entities_created'] += 1
        
        # Emit event
        EventManager().emit(Event(
            EventType.ENTITY_CREATED,
            {'entity_id': entity.id, 'name': entity.name}
        ))
        
        print(f"🎭 Created entity: {entity.name} ({entity.id[:8]})")
        return entity
    
    def destroy_entity(self, entity_id: str):
        """Destroy entity"""
        if entity_id in self.entities:
            entity = self.entities[entity_id]
            
            # Remove from tag indexes
            for tag in entity.tags:
                self.entities_by_tag[tag].discard(entity_id)
            
            # Return components to pools
            for component in entity.components.values():
                component_type = type(component)
                if component_type in self.component_pools:
                    self.component_pools[component_type].release(component)
            
            entity.destroy()
            del self.entities[entity_id]
            self._stats['entities_destroyed'] += 1
            
            print(f"💀 Destroyed entity: {entity.name} ({entity_id[:8]})")
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Lấy entity theo ID"""
        return self.entities.get(entity_id)
    
    def get_entities_with_tag(self, tag: str) -> List[Entity]:
        """Lấy entities có tag"""
        entity_ids = self.entities_by_tag.get(tag, set())
        return [self.entities[eid] for eid in entity_ids if eid in self.entities]
    
    def get_entities_with_component(self, component_type: type) -> List[Entity]:
        """Lấy entities có component type"""
        return [entity for entity in self.entities.values() 
                if entity.has_component(component_type)]
    
    def update_all(self, delta_time: float):
        """Update tất cả entities"""
        # Create list để tránh modification during iteration
        active_entities = [entity for entity in self.entities.values() 
                          if entity.state == EntityState.ACTIVE]
        
        for entity in active_entities:
            entity.update(delta_time)
    
    def cleanup_destroyed(self):
        """Dọn dẹp entities đã destroyed"""
        to_remove = [eid for eid, entity in self.entities.items() 
                    if entity.state == EntityState.DESTROYED]
        
        for entity_id in to_remove:
            self.destroy_entity(entity_id)
    
    def get_component_pool(self, component_type: type) -> ObjectPool:
        """Lấy hoặc tạo component pool"""
        if component_type not in self.component_pools:
            self.component_pools[component_type] = ObjectPool(component_type, 10)
        return self.component_pools[component_type]
    
    def get_stats(self) -> Dict[str, Any]:
        active_count = sum(1 for e in self.entities.values() if e.state == EntityState.ACTIVE)
        
        pool_stats = {}
        for comp_type, pool in self.component_pools.items():
            pool_stats[comp_type.__name__] = pool.get_stats()
        
        return {
            **self._stats,
            'active_entities': active_count,
            'total_entities': len(self.entities),
            'component_pools': pool_stats
        }

# GAME ENGINE
class GameEngine:
    """Main game engine"""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        self.running = False
        self.paused = False
        
        self.entity_manager = EntityManager()
        self.event_manager = EventManager()
        
        self.last_frame_time = time.time()
        self.delta_time = 0.0
        self.frame_count = 0
        self.fps = 0.0
        
        # Performance tracking
        self.performance_stats = {
            'update_time': 0.0,
            'render_time': 0.0,
            'total_frame_time': 0.0,
            'memory_usage': 0
        }
    
    def start(self):
        """Khởi động engine"""
        print("🚀 Starting Game Engine...")
        self.running = True
        self.last_frame_time = time.time()
        
        # Emit start event
        self.event_manager.emit(Event(EventType.ENTITY_CREATED, {'message': 'Engine started'}))
    
    def stop(self):
        """Dừng engine"""
        print("🛑 Stopping Game Engine...")
        self.running = False
    
    def pause(self):
        """Tạm dừng game"""
        self.paused = True
        print("⏸️ Game Paused")
    
    def resume(self):
        """Tiếp tục game"""
        self.paused = False
        self.last_frame_time = time.time()  # Reset timing
        print("▶️ Game Resumed")
    
    def update(self):
        """Update một frame"""
        current_time = time.time()
        self.delta_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # Calculate FPS
        self.frame_count += 1
        if self.frame_count % 60 == 0:  # Update FPS every 60 frames
            self.fps = 1.0 / self.delta_time if self.delta_time > 0 else 0
        
        if not self.paused:
            # Measure update performance
            update_start = time.time()
            
            # Process events
            self.event_manager.process_events()
            
            # Update entities
            self.entity_manager.update_all(self.delta_time)
            
            # Cleanup destroyed entities
            self.entity_manager.cleanup_destroyed()
            
            update_end = time.time()
            self.performance_stats['update_time'] = update_end - update_start
    
    def run_frame(self):
        """Chạy một frame hoàn chỉnh"""
        frame_start = time.time()
        
        self.update()
        
        # Simulate render time
        render_start = time.time()
        time.sleep(0.001)  # Giả lập render
        render_end = time.time()
        
        self.performance_stats['render_time'] = render_end - render_start
        
        frame_end = time.time()
        self.performance_stats['total_frame_time'] = frame_end - frame_start
        
        # Frame rate limiting
        elapsed = frame_end - frame_start
        if elapsed < self.target_frame_time:
            time.sleep(self.target_frame_time - elapsed)
    
    def get_stats(self) -> Dict[str, Any]:
        """Lấy thống kê engine"""
        return {
            'fps': round(self.fps, 2),
            'frame_count': self.frame_count,
            'delta_time': round(self.delta_time, 4),
            'running': self.running,
            'paused': self.paused,
            'performance': self.performance_stats,
            'entity_manager': self.entity_manager.get_stats(),
            'event_manager': self.event_manager.get_stats()
        }

def main():
    print("🎮 GAME ENGINE VỚI COMPONENT SYSTEM 🎮")
    
    # Tạo game engine
    engine = GameEngine(target_fps=60)
    
    # Event listeners để demo
    def on_entity_created(event: Event):
        print(f"👶 Entity created: {event.data}")
    
    def on_entity_destroyed(event: Event):
        print(f"💥 Entity destroyed: {event.data}")
    
    def on_component_added(event: Event):
        print(f"🔧 Component added: {event.data}")
    
    # Subscribe to events
    engine.event_manager.subscribe(EventType.ENTITY_CREATED, on_entity_created)
    engine.event_manager.subscribe(EventType.ENTITY_DESTROYED, on_entity_destroyed)
    engine.event_manager.subscribe(EventType.COMPONENT_ADDED, on_component_added)
    
    # Tạo entities với components
    print(f"\n🎭 CREATING GAME ENTITIES:")
    print("=" * 40)
    
    # Tạo player
    player = engine.entity_manager.create_entity("Player")
    player.add_component(TransformComponent())
    player.add_component(RenderComponent("player_sprite", "blue"))
    player.add_component(PhysicsComponent(mass=1.0))
    player.add_component(HealthComponent(max_health=100))
    player.add_tag("player")
    
    # Set player position
    transform = player.get_component(TransformComponent)
    transform.move_to(Vector2(100, 100))
    
    # Tạo enemies
    enemies = []
    for i in range(3):
        enemy = engine.entity_manager.create_entity(f"Enemy_{i+1}")
        enemy.add_component(TransformComponent())
        enemy.add_component(RenderComponent("enemy_sprite", "red"))
        enemy.add_component(PhysicsComponent(mass=0.8))
        enemy.add_component(HealthComponent(max_health=50))
        enemy.add_tag("enemy")
        
        # Set enemy positions
        enemy_transform = enemy.get_component(TransformComponent)
        enemy_transform.move_to(Vector2(200 + i * 50, 150 + i * 30))
        enemy_transform.velocity = Vector2(-20 + i * 10, 10 - i * 5)
        
        enemies.append(enemy)
    
    # Tạo collectible items
    items = []
    for i in range(5):
        item = engine.entity_manager.create_entity(f"Item_{i+1}")
        item.add_component(TransformComponent())
        item.add_component(RenderComponent("item_sprite", "yellow"))
        item.add_tag("collectible")
        
        # Set item positions
        item_transform = item.get_component(TransformComponent)
        item_transform.move_to(Vector2(50 + i * 100, 50 + i * 20))
        
        items.append(item)
    
    print(f"\n🎮 STARTING GAME SIMULATION:")
    print("=" * 40)
    
    # Start engine
    engine.start()
    
    # Simulate game loop
    simulation_time = 0.0
    max_simulation_time = 5.0  # 5 seconds simulation
    
    while engine.running and simulation_time < max_simulation_time:
        engine.run_frame()
        simulation_time += engine.delta_time
        
        # Simulate some game events
        if int(simulation_time * 2) % 3 == 0 and enemies:  # Every 1.5 seconds
            # Damage random enemy
            enemy = enemies[int(simulation_time) % len(enemies)]
            health_comp = enemy.get_component(HealthComponent)
            if health_comp and health_comp.current_health > 0:
                died = health_comp.take_damage(25)
                if died:
                    engine.entity_manager.destroy_entity(enemy.id)
                    enemies.remove(enemy)
                    print(f"💀 {enemy.name} died!")
        
        if int(simulation_time * 4) % 5 == 0 and items:  # Collect items
            item = items.pop(0)
            engine.entity_manager.destroy_entity(item.id)
            print(f"✨ Collected {item.name}!")
        
        # Apply some physics
        player_physics = player.get_component(PhysicsComponent)
        if player_physics:
            # Apply random forces to player
            force = Vector2(
                math.sin(simulation_time * 2) * 50,
                math.cos(simulation_time * 3) * 30
            )
            player_physics.apply_force(force)
    
    print(f"\n📊 FINAL STATISTICS:")
    print("=" * 30)
    
    # Print final stats
    stats = engine.get_stats()
    
    print(f"🎮 Engine Stats:")
    print(f"   FPS: {stats['fps']}")
    print(f"   Frames: {stats['frame_count']}")
    print(f"   Delta Time: {stats['delta_time']}s")
    
    print(f"\n🎭 Entity Manager:")
    em_stats = stats['entity_manager']
    print(f"   Created: {em_stats['entities_created']}")    
    print(f"   Destroyed: {em_stats['entities_destroyed']}")
    print(f"   Active: {em_stats['active_entities']}")
    print(f"\n📡 Event Manager:")
    ev_stats = stats['event_manager']
    print(f"   Events Processed: {ev_stats['events_processed']}")
    print(f"   Listeners: {ev_stats['listeners_count']}")
    
    print(f"\n🏊 Component Pools:")
    for comp_name, pool_stats in em_stats['component_pools'].items():
        print(f"   {comp_name}: {pool_stats['in_use']}/{pool_stats['total']} in use")
    
    print(f"\n⚡ Performance:")
    perf = stats['performance']
    print(f"   Update Time: {perf['update_time']:.4f}s")
    print(f"   Render Time: {perf['render_time']:.4f}s")
    print(f"   Total Frame Time: {perf['total_frame_time']:.4f}s")
    
    # Cleanup
    engine.stop()
    
    # Force garbage collection
    gc.collect()
    print(f"\n🧹 Cleanup completed!")

if __name__ == "__main__":
    main()
