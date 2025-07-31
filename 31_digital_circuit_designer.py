#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Digital Circuit Designer
-----------------------
A comprehensive digital circuit design and simulation application that provides:
- Drag-and-drop circuit design interface
- Logic gate library (AND, OR, XOR, NOT, NAND, NOR, etc.)
- Real-time signal simulation with visual feedback
- RTL (Register Transfer Level) design capabilities
- Truth table generation
- Timing diagram visualization
- Circuit optimization suggestions
- Export to Verilog/VHDL
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import tkinter.font as tkFont
from PIL import Image, ImageDraw, ImageTk
import json
import math
import time
import threading
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import re

class LogicState(Enum):
    """Logic states for digital signals"""
    LOW = 0
    HIGH = 1
    UNKNOWN = 2
    HIGH_Z = 3  # High impedance

class GateType(Enum):
    """Types of logic gates"""
    AND = "AND"
    OR = "OR"
    XOR = "XOR"
    NOT = "NOT"
    NAND = "NAND"
    NOR = "NOR"
    XNOR = "XNOR"
    BUFFER = "BUFFER"
    # Sequential elements
    D_FLIP_FLOP = "D_FF"
    JK_FLIP_FLOP = "JK_FF"
    T_FLIP_FLOP = "T_FF"
    SR_LATCH = "SR_LATCH"
    # Complex components
    MULTIPLEXER = "MUX"
    DEMULTIPLEXER = "DEMUX"
    DECODER = "DECODER"
    ENCODER = "ENCODER"
    ADDER = "ADDER"
    COUNTER = "COUNTER"
    # I/O
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    CLOCK = "CLOCK"
    LED = "LED"
    SWITCH = "SWITCH"

@dataclass
class Point:
    """2D Point representation"""
    x: float
    y: float
    
    def distance_to(self, other: 'Point') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass
class Pin:
    """Logic gate pin (input/output)"""
    id: str
    position: Point
    is_input: bool
    state: LogicState = LogicState.UNKNOWN
    connected_wires: List['Wire'] = field(default_factory=list)
    
class Wire:
    """Connection wire between pins"""
    
    def __init__(self, start_pin: Pin, end_pin: Pin, wire_id: str = None):
        self.id = wire_id or f"wire_{id(self)}"
        self.start_pin = start_pin
        self.end_pin = end_pin
        self.state = LogicState.UNKNOWN
        self.path_points: List[Point] = []
        self.color = "#000000"  # Default black
        self.selected = False
        self.auto_route()
        
        # Connect to pins
        start_pin.connected_wires.append(self)
        end_pin.connected_wires.append(self)
    
    def update_visual_state(self):
        """Update wire color based on logic state"""
        if self.state == LogicState.HIGH:
            self.color = "#FF0000"  # Red for HIGH
        elif self.state == LogicState.LOW:
            self.color = "#000000"  # Black for LOW
        elif self.state == LogicState.UNKNOWN:
            self.color = "#808080"  # Gray for UNKNOWN
        else:
            self.color = "#0000FF"  # Blue for HIGH_Z
    
    def auto_route(self):
        """Automatically route wire with right angles"""
        start_pos = self.start_pin.position
        end_pos = self.end_pin.position
        
        # Clear existing path points
        self.path_points = []
        
        # Calculate the routing strategy based on pin positions and directions
        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y
        
        # Only add routing points if there's significant distance
        if abs(dx) > 20 or abs(dy) > 20:
            # Determine routing style based on pin types and positions
            if self.start_pin.is_input and not self.end_pin.is_input:
                # Input to output routing (shouldn't normally happen)
                self._route_input_to_output(start_pos, end_pos)
            elif not self.start_pin.is_input and self.end_pin.is_input:
                # Output to input routing (normal case)
                self._route_output_to_input(start_pos, end_pos)
            else:
                # Default routing
                self._route_default(start_pos, end_pos)
    
    def _route_output_to_input(self, start_pos: Point, end_pos: Point):
        """Route from output pin to input pin"""
        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y
        
        # For output to input, use L-shaped or Z-shaped routing
        if abs(dy) < 10:  # Roughly horizontal
            # Simple horizontal line
            return
        
        if dx > 50:  # Enough horizontal space
            # Standard L-shaped routing: horizontal first, then vertical
            mid_x = start_pos.x + dx * 0.6  # 60% of the way
            self.path_points.append(Point(mid_x, start_pos.y))
            self.path_points.append(Point(mid_x, end_pos.y))
        else:  # Limited horizontal space
            # Go out, up/down, then in
            out_distance = 30
            self.path_points.append(Point(start_pos.x + out_distance, start_pos.y))
            self.path_points.append(Point(start_pos.x + out_distance, end_pos.y))
    
    def _route_input_to_output(self, start_pos: Point, end_pos: Point):
        """Route from input pin to output pin"""
        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y
        
        if abs(dy) < 10:  # Roughly horizontal
            return
        
        # For input to output, route around
        if dx < -50:  # Going backwards
            # Go out from input, around, then to output
            out_distance = 30
            self.path_points.append(Point(start_pos.x - out_distance, start_pos.y))
            self.path_points.append(Point(start_pos.x - out_distance, end_pos.y))
        else:
            # Standard routing
            mid_x = start_pos.x + dx * 0.4
            self.path_points.append(Point(mid_x, start_pos.y))
            self.path_points.append(Point(mid_x, end_pos.y))
    
    def _route_default(self, start_pos: Point, end_pos: Point):
        """Default routing strategy"""
        dx = end_pos.x - start_pos.x
        dy = end_pos.y - start_pos.y
        
        if abs(dy) < 10:  # Roughly horizontal
            return
        
        # Simple L-shaped routing
        mid_x = start_pos.x + dx * 0.5
        self.path_points.append(Point(mid_x, start_pos.y))
        self.path_points.append(Point(mid_x, end_pos.y))
    
    def add_point(self, point: Point):
        """Add a point to the wire path"""
        self.path_points.append(point)
    
    def contains_point(self, point: Point, tolerance: float = 5.0) -> bool:
        """Check if a point is near the wire"""
        # Check if point is near any segment of the wire
        points = [self.start_pin.position] + self.path_points + [self.end_pin.position]
        
        for i in range(len(points) - 1):
            # Check distance to line segment
            if self._point_to_segment_distance(point, points[i], points[i+1]) <= tolerance:
                return True
        return False
    
    def _point_to_segment_distance(self, p: Point, v: Point, w: Point) -> float:
        """Calculate distance from point p to line segment vw"""
        # Return minimum distance between line segment vw and point p
        l2 = (v.x - w.x)**2 + (v.y - w.y)**2  # length_squared
        if l2 == 0.0:
            return p.distance_to(v)   # v == w case
            
        # Consider the line extending the segment, parameterized as v + t (w - v)
        # We find projection of point p onto the line.
        # It falls where t = [(p-v) . (w-v)] / |w-v|^2
        t = ((p.x - v.x) * (w.x - v.x) + (p.y - v.y) * (w.y - v.y)) / l2
        
        if t < 0.0:
            return p.distance_to(v)  # Beyond the 'v' end of the segment
        elif t > 1.0:
            return p.distance_to(w)  # Beyond the 'w' end of the segment
        
        projection = Point(v.x + t * (w.x - v.x), v.y + t * (w.y - v.y))
        return p.distance_to(projection)

class LogicGate:
    """Base class for logic gates"""
    
    def __init__(self, gate_type: GateType, position: Point, gate_id: str = None):
        self.id = gate_id or f"{gate_type.value}_{id(self)}"
        self.gate_type = gate_type
        self.position = position
        self.width = 80
        self.height = 60
        self.selected = False
        self.label = gate_type.value
        
        # Initialize pins based on gate type
        self.input_pins: List[Pin] = []
        self.output_pins: List[Pin] = []
        self._create_pins()
        
        # Gate-specific properties
        self.delay = 1  # Propagation delay in simulation steps
        self.last_update_time = 0
    
    def _create_pins(self):
        """Create input and output pins based on gate type"""
        pin_spacing = 20
        
        if self.gate_type in [GateType.AND, GateType.OR, GateType.XOR, 
                             GateType.NAND, GateType.NOR, GateType.XNOR]:
            # Two input gates
            self.input_pins = [
                Pin(f"{self.id}_in1", Point(self.position.x - self.width/2, 
                                          self.position.y - pin_spacing/2), True),
                Pin(f"{self.id}_in2", Point(self.position.x - self.width/2, 
                                          self.position.y + pin_spacing/2), True)
            ]
            self.output_pins = [
                Pin(f"{self.id}_out", Point(self.position.x + self.width/2, 
                                          self.position.y), False)
            ]
        
        elif self.gate_type in [GateType.NOT, GateType.BUFFER]:
            # Single input gates
            self.input_pins = [
                Pin(f"{self.id}_in", Point(self.position.x - self.width/2, 
                                         self.position.y), True)
            ]
            self.output_pins = [
                Pin(f"{self.id}_out", Point(self.position.x + self.width/2, 
                                          self.position.y), False)
            ]
        
        elif self.gate_type == GateType.D_FLIP_FLOP:
            # D Flip-flop: D, Clock inputs; Q, Q' outputs
            self.input_pins = [
                Pin(f"{self.id}_D", Point(self.position.x - self.width/2, 
                                        self.position.y - pin_spacing), True),
                Pin(f"{self.id}_CLK", Point(self.position.x - self.width/2, 
                                          self.position.y + pin_spacing), True)
            ]
            self.output_pins = [
                Pin(f"{self.id}_Q", Point(self.position.x + self.width/2, 
                                        self.position.y - pin_spacing/2), False),
                Pin(f"{self.id}_Qn", Point(self.position.x + self.width/2, 
                                         self.position.y + pin_spacing/2), False)
            ]
        
        elif self.gate_type == GateType.INPUT:
            # Input source
            self.output_pins = [
                Pin(f"{self.id}_out", Point(self.position.x + self.width/2, 
                                          self.position.y), False)
            ]
            self.state = LogicState.LOW  # Default state
        
        elif self.gate_type == GateType.OUTPUT:
            # Output sink
            self.input_pins = [
                Pin(f"{self.id}_in", Point(self.position.x - self.width/2, 
                                         self.position.y), True)
            ]
        
        elif self.gate_type == GateType.CLOCK:
            # Clock generator
            self.output_pins = [
                Pin(f"{self.id}_out", Point(self.position.x + self.width/2, 
                                          self.position.y), False)
            ]
            self.frequency = 1.0  # Hz
            self.state = LogicState.LOW
    
    def move_to(self, new_position: Point):
        """Move gate to new position and update pin positions"""
        delta_x = new_position.x - self.position.x
        delta_y = new_position.y - self.position.y
        
        self.position = new_position
        
        # Update pin positions
        for pin in self.input_pins + self.output_pins:
            pin.position.x += delta_x
            pin.position.y += delta_y
    
    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box (x1, y1, x2, y2)"""
        x1 = self.position.x - self.width / 2
        y1 = self.position.y - self.height / 2
        x2 = self.position.x + self.width / 2
        y2 = self.position.y + self.height / 2
        return (x1, y1, x2, y2)
    
    def contains_point(self, point: Point) -> bool:
        """Check if point is inside gate bounds"""
        x1, y1, x2, y2 = self.get_bounds()
        return x1 <= point.x <= x2 and y1 <= point.y <= y2
    
    def compute_output(self, current_time: float = 0) -> Dict[str, LogicState]:
        """Compute gate output based on inputs"""
        if current_time - self.last_update_time < self.delay:
            return {}  # Not ready to update yet
        
        self.last_update_time = current_time
        
        if self.gate_type == GateType.AND:
            inputs = [pin.state for pin in self.input_pins]
            if all(state == LogicState.HIGH for state in inputs):
                return {self.output_pins[0].id: LogicState.HIGH}
            elif any(state == LogicState.LOW for state in inputs):
                return {self.output_pins[0].id: LogicState.LOW}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.OR:
            inputs = [pin.state for pin in self.input_pins]
            if any(state == LogicState.HIGH for state in inputs):
                return {self.output_pins[0].id: LogicState.HIGH}
            elif all(state == LogicState.LOW for state in inputs):
                return {self.output_pins[0].id: LogicState.LOW}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.XOR:
            inputs = [pin.state for pin in self.input_pins]
            if all(state in [LogicState.HIGH, LogicState.LOW] for state in inputs):
                high_count = sum(1 for state in inputs if state == LogicState.HIGH)
                return {self.output_pins[0].id: LogicState.HIGH if high_count % 2 == 1 else LogicState.LOW}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.NOT:
            input_state = self.input_pins[0].state
            if input_state == LogicState.HIGH:
                return {self.output_pins[0].id: LogicState.LOW}
            elif input_state == LogicState.LOW:
                return {self.output_pins[0].id: LogicState.HIGH}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.NAND:
            # NAND = NOT(AND)
            and_result = self._compute_and()
            if and_result == LogicState.HIGH:
                return {self.output_pins[0].id: LogicState.LOW}
            elif and_result == LogicState.LOW:
                return {self.output_pins[0].id: LogicState.HIGH}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.NOR:
            # NOR = NOT(OR)
            or_result = self._compute_or()
            if or_result == LogicState.HIGH:
                return {self.output_pins[0].id: LogicState.LOW}
            elif or_result == LogicState.LOW:
                return {self.output_pins[0].id: LogicState.HIGH}
            else:
                return {self.output_pins[0].id: LogicState.UNKNOWN}
        
        elif self.gate_type == GateType.D_FLIP_FLOP:
            # D Flip-flop logic (simplified - edge triggered)
            d_input = self.input_pins[0].state
            clk_input = self.input_pins[1].state
            
            # Simple edge detection (would need more sophisticated handling in real implementation)
            if hasattr(self, 'prev_clk') and self.prev_clk == LogicState.LOW and clk_input == LogicState.HIGH:
                # Rising edge
                if d_input == LogicState.HIGH:
                    self.stored_state = LogicState.HIGH
                elif d_input == LogicState.LOW:
                    self.stored_state = LogicState.LOW
            
            if not hasattr(self, 'stored_state'):
                self.stored_state = LogicState.LOW
            
            self.prev_clk = clk_input
            
            # Q output is stored state, Q' is inverted
            q_bar = LogicState.LOW if self.stored_state == LogicState.HIGH else LogicState.HIGH
            return {
                self.output_pins[0].id: self.stored_state,
                self.output_pins[1].id: q_bar
            }
        
        elif self.gate_type == GateType.INPUT:
            # Input gates maintain their set state
            return {self.output_pins[0].id: getattr(self, 'state', LogicState.LOW)}
        
        elif self.gate_type == GateType.CLOCK:
            # Clock generator
            period = 1.0 / self.frequency if self.frequency > 0 else 1.0
            phase = (current_time % period) / period
            new_state = LogicState.HIGH if phase < 0.5 else LogicState.LOW
            return {self.output_pins[0].id: new_state}
        
        return {}
    
    def _compute_and(self) -> LogicState:
        """Helper method for AND computation"""
        inputs = [pin.state for pin in self.input_pins]
        if all(state == LogicState.HIGH for state in inputs):
            return LogicState.HIGH
        elif any(state == LogicState.LOW for state in inputs):
            return LogicState.LOW
        else:
            return LogicState.UNKNOWN
    
    def _compute_or(self) -> LogicState:
        """Helper method for OR computation"""
        inputs = [pin.state for pin in self.input_pins]
        if any(state == LogicState.HIGH for state in inputs):
            return LogicState.HIGH
        elif all(state == LogicState.LOW for state in inputs):
            return LogicState.LOW
        else:
            return LogicState.UNKNOWN

class Circuit:
    """Digital circuit containing gates and wires"""
    
    def __init__(self):
        self.gates: Dict[str, LogicGate] = {}
        self.wires: Dict[str, Wire] = {}
        self.simulation_running = False
        self.simulation_time = 0.0
        self.simulation_step = 0.1  # seconds
        
        # For timing diagram
        self.signal_history: Dict[str, List[Tuple[float, LogicState]]] = {}
        self.max_history_time = 10.0  # seconds
    
    def add_gate(self, gate: LogicGate):
        """Add a gate to the circuit"""
        self.gates[gate.id] = gate
        
        # Initialize signal history for gate outputs
        for pin in gate.output_pins:
            self.signal_history[pin.id] = [(0.0, LogicState.UNKNOWN)]
    
    def remove_gate(self, gate_id: str):
        """Remove a gate and its connections"""
        if gate_id in self.gates:
            gate = self.gates[gate_id]
            
            # Remove connected wires
            wires_to_remove = []
            for pin in gate.input_pins + gate.output_pins:
                for wire in pin.connected_wires[:]:
                    wires_to_remove.append(wire.id)
            
            for wire_id in wires_to_remove:
                self.remove_wire(wire_id)
            
            # Remove from signal history
            for pin in gate.output_pins:
                if pin.id in self.signal_history:
                    del self.signal_history[pin.id]
            
            del self.gates[gate_id]
    
    def add_wire(self, start_pin_id: str, end_pin_id: str) -> Optional[Wire]:
        """Add a wire between two pins"""
        start_pin = self.find_pin(start_pin_id)
        end_pin = self.find_pin(end_pin_id)
        
        if not start_pin or not end_pin:
            return None
        
        # Check if connection is valid (output to input)
        if start_pin.is_input == end_pin.is_input:
            return None  # Can't connect input to input or output to output
        
        # Ensure start_pin is output and end_pin is input
        if start_pin.is_input:
            start_pin, end_pin = end_pin, start_pin
        
        wire = Wire(start_pin, end_pin)
        self.wires[wire.id] = wire
        return wire
    
    def remove_wire(self, wire_id: str):
        """Remove a wire from the circuit"""
        if wire_id in self.wires:
            wire = self.wires[wire_id]
            
            # Remove from connected pins
            if wire in wire.start_pin.connected_wires:
                wire.start_pin.connected_wires.remove(wire)
            if wire in wire.end_pin.connected_wires:
                wire.end_pin.connected_wires.remove(wire)
            
            del self.wires[wire_id]
    
    def find_pin(self, pin_id: str) -> Optional[Pin]:
        """Find a pin by ID"""
        for gate in self.gates.values():
            for pin in gate.input_pins + gate.output_pins:
                if pin.id == pin_id:
                    return pin
        return None
    
    def find_gate_at_position(self, position: Point) -> Optional[LogicGate]:
        """Find gate at given position"""
        for gate in self.gates.values():
            if gate.contains_point(position):
                return gate
        return None
    
    def find_pin_at_position(self, position: Point, tolerance: float = 10.0) -> Optional[Pin]:
        """Find pin near given position"""
        for gate in self.gates.values():
            for pin in gate.input_pins + gate.output_pins:
                if pin.position.distance_to(position) <= tolerance:
                    return pin
        return None
    
    def simulate_step(self):
        """Perform one simulation step"""
        if not self.simulation_running:
            return
        
        # Update all gates
        pin_updates = {}
        for gate in self.gates.values():
            updates = gate.compute_output(self.simulation_time)
            pin_updates.update(updates)
        
        # Apply updates to pins and propagate through wires
        for pin_id, new_state in pin_updates.items():
            pin = self.find_pin(pin_id)
            if pin:
                pin.state = new_state
                
                # Record signal history
                if pin_id not in self.signal_history:
                    self.signal_history[pin_id] = []
                
                # Add to history if state changed
                history = self.signal_history[pin_id]
                if not history or history[-1][1] != new_state:
                    history.append((self.simulation_time, new_state))
                
                # Limit history length
                cutoff_time = self.simulation_time - self.max_history_time
                self.signal_history[pin_id] = [(t, s) for t, s in history if t >= cutoff_time]
                
                # Propagate through connected wires
                for wire in pin.connected_wires:
                    if wire.start_pin == pin:  # This is an output pin
                        wire.state = new_state
                        wire.end_pin.state = new_state
                        wire.update_visual_state()
        
        self.simulation_time += self.simulation_step
    
    def start_simulation(self):
        """Start circuit simulation"""
        self.simulation_running = True
        self.simulation_time = 0.0
        
        # Initialize all pins to unknown state
        for gate in self.gates.values():
            for pin in gate.input_pins + gate.output_pins:
                if gate.gate_type not in [GateType.INPUT, GateType.CLOCK]:
                    pin.state = LogicState.UNKNOWN
    
    def stop_simulation(self):
        """Stop circuit simulation"""
        self.simulation_running = False
    
    def reset_simulation(self):
        """Reset simulation state"""
        self.stop_simulation()
        self.simulation_time = 0.0
        self.signal_history.clear()
        
        # Reset all pin states
        for gate in self.gates.values():
            for pin in gate.input_pins + gate.output_pins:
                pin.state = LogicState.UNKNOWN
        
        # Reset wire states
        for wire in self.wires.values():
            wire.state = LogicState.UNKNOWN
            wire.update_visual_state()
    
    def generate_truth_table(self, input_pins: List[str], output_pins: List[str]) -> List[Dict]:
        """Generate truth table for specified inputs and outputs"""
        truth_table = []
        
        # Get input gates
        input_gates = []
        for pin_id in input_pins:
            pin = self.find_pin(pin_id)
            if pin:
                gate = next((g for g in self.gates.values() 
                           if pin in g.output_pins), None)
                if gate and gate.gate_type == GateType.INPUT:
                    input_gates.append(gate)
        
        if not input_gates:
            return truth_table
        
        # Generate all input combinations
        num_inputs = len(input_gates)
        for i in range(2 ** num_inputs):
            # Set input states
            input_values = {}
            for j, gate in enumerate(input_gates):
                state = LogicState.HIGH if (i >> j) & 1 else LogicState.LOW
                gate.state = state
                gate.output_pins[0].state = state
                input_values[gate.output_pins[0].id] = state.value
            
            # Simulate to get outputs
            self.reset_simulation()
            for gate in input_gates:
                gate.output_pins[0].state = gate.state
            
            # Propagate through circuit (simplified)
            for _ in range(10):  # Max iterations to avoid infinite loops
                self.simulate_step()
            
            # Collect output values
            output_values = {}
            for pin_id in output_pins:
                pin = self.find_pin(pin_id)
                if pin:
                    output_values[pin_id] = pin.state.value
            
            truth_table.append({**input_values, **output_values})
        
        return truth_table
    
    def export_verilog(self) -> str:
        """Export circuit to Verilog HDL"""
        verilog_code = []
        
        # Module declaration
        verilog_code.append("module circuit (")
        
        # Collect inputs and outputs
        inputs = []
        outputs = []
        
        for gate in self.gates.values():
            if gate.gate_type == GateType.INPUT:
                inputs.append(f"input_{gate.id}")
            elif gate.gate_type == GateType.OUTPUT:
                outputs.append(f"output_{gate.id}")
        
        ports = inputs + outputs
        verilog_code.append("    " + ",\n    ".join(ports))
        verilog_code.append(");")
        verilog_code.append("")
        
        # Port declarations
        for inp in inputs:
            verilog_code.append(f"    input {inp};")
        for out in outputs:
            verilog_code.append(f"    output {out};")
        verilog_code.append("")
        
        # Wire declarations
        wire_names = set()
        for wire in self.wires.values():
            wire_name = f"wire_{wire.start_pin.id}_to_{wire.end_pin.id}"
            wire_names.add(wire_name)
        
        for wire_name in sorted(wire_names):
            verilog_code.append(f"    wire {wire_name};")
        verilog_code.append("")
        
        # Gate instantiations
        for gate in self.gates.values():
            if gate.gate_type in [GateType.INPUT, GateType.OUTPUT]:
                continue
            
            gate_name = gate.gate_type.value.lower()
            instance_name = f"{gate_name}_{gate.id}"
            
            if gate.gate_type in [GateType.AND, GateType.OR, GateType.XOR, 
                                 GateType.NAND, GateType.NOR, GateType.XNOR]:
                input1 = self._get_wire_name_for_pin(gate.input_pins[0])
                input2 = self._get_wire_name_for_pin(gate.input_pins[1])
                output = self._get_wire_name_for_pin(gate.output_pins[0])
                verilog_code.append(f"    {gate_name} {instance_name} ({output}, {input1}, {input2});")
            
            elif gate.gate_type in [GateType.NOT, GateType.BUFFER]:
                input_pin = self._get_wire_name_for_pin(gate.input_pins[0])
                output = self._get_wire_name_for_pin(gate.output_pins[0])
                verilog_code.append(f"    {gate_name} {instance_name} ({output}, {input_pin});")
        
        verilog_code.append("")
        verilog_code.append("endmodule")
        
        return "\n".join(verilog_code)
    
    def _get_wire_name_for_pin(self, pin: Pin) -> str:
        """Get wire name for a pin"""
        # Find connected wire or use pin name
        for wire in pin.connected_wires:
            if wire.end_pin == pin:
                return f"wire_{wire.start_pin.id}_to_{wire.end_pin.id}"
        
        # If no wire, might be direct connection to input/output
        gate = next((g for g in self.gates.values() 
                    if pin in g.input_pins + g.output_pins), None)
        
        if gate:
            if gate.gate_type == GateType.INPUT:
                return f"input_{gate.id}"
            elif gate.gate_type == GateType.OUTPUT:
                return f"output_{gate.id}"
        
        return pin.id
    
    def save_to_file(self, filename: str):
        """Save circuit to JSON file"""
        circuit_data = {
            'gates': [],
            'wires': []
        }
        
        # Save gates
        for gate in self.gates.values():
            gate_data = {
                'id': gate.id,
                'type': gate.gate_type.value,
                'position': {'x': gate.position.x, 'y': gate.position.y},
                'label': gate.label
            }
            
            # Save gate-specific properties
            if hasattr(gate, 'state'):
                gate_data['state'] = gate.state.value
            if hasattr(gate, 'frequency'):
                gate_data['frequency'] = gate.frequency
            
            circuit_data['gates'].append(gate_data)
        
        # Save wires
        for wire in self.wires.values():
            wire_data = {
                'id': wire.id,
                'start_pin': wire.start_pin.id,
                'end_pin': wire.end_pin.id
            }
            circuit_data['wires'].append(wire_data)
        
        with open(filename, 'w') as f:
            json.dump(circuit_data, f, indent=2)
    
    def load_from_file(self, filename: str):
        """Load circuit from JSON file"""
        with open(filename, 'r') as f:
            circuit_data = json.load(f)
        
        # Clear existing circuit
        self.gates.clear()
        self.wires.clear()
        self.signal_history.clear()
        
        # Load gates
        for gate_data in circuit_data.get('gates', []):
            gate_type = GateType(gate_data['type'])
            position = Point(gate_data['position']['x'], gate_data['position']['y'])
            gate = LogicGate(gate_type, position, gate_data['id'])
            gate.label = gate_data.get('label', gate_type.value)
            
            # Load gate-specific properties
            if 'state' in gate_data:
                gate.state = LogicState(gate_data['state'])
            if 'frequency' in gate_data:
                gate.frequency = gate_data['frequency']
            
            self.add_gate(gate)
        
        # Load wires
        for wire_data in circuit_data.get('wires', []):
            self.add_wire(wire_data['start_pin'], wire_data['end_pin'])

class CircuitCanvas:
    """Canvas for drawing and interacting with circuits"""
    
    def __init__(self, parent, circuit):
        self.parent = parent
        self.canvas = tk.Canvas(parent, bg="white", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.circuit = circuit
        self.zoom_level = 1.0
        self.pan_offset = Point(0, 0)
        self.last_mouse_pos = None
        self.panning = False
        self.space_pressed = False  # Thêm flag cho Space key
        
        # Grid properties
        self.grid_size = 20
        self.show_grid = True
        
        # Selection and editing
        self.selected_gate = None
        self.selected_wire = None
        self.dragging = False
        self.drag_start = None
        self.connecting = False
        self.temp_wire_start = None
        self.temp_wire_end = None
        self.wire_edit_mode = False
        self.wire_edit_point = None
        
        # Drawing optimization
        self.last_draw_time = 0
        self.draw_throttle = 1.0 / 30  # 30 FPS
        self.draw_pending = False
        
        # Bind events
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<B2-Motion>", self.on_middle_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<ButtonRelease-2>", self.on_middle_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        
        # Keyboard events cho pan
        self.canvas.bind("<KeyPress-space>", self.on_space_press)
        self.canvas.bind("<KeyRelease-space>", self.on_space_release)
        self.canvas.focus_set()  # Cho phép canvas nhận keyboard events
        
        # Colors
        self.colors = {
            'gate_fill': '#E8E8E8',
            'gate_outline': '#333333',
            'gate_selected': '#FFE6CC',
            'wire': '#0066CC',
            'wire_active': '#FF6600',
            'wire_selected': '#FF6600',
            'pin': '#666666',
            'pin_input': '#666666',
            'pin_output': '#666666',
            'pin_active': '#FF0000',
            'background': '#FFFFFF',
            'grid': '#F0F0F0',
            'selection': '#FF6600',
            'signal_high': '#FF0000',
            'signal_low': '#000000',
            'signal_unknown': '#808080'
        }
        
        self.draw_circuit()
    
    def screen_to_world(self, screen_point: Point) -> Point:
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_point.x - self.pan_offset.x) / self.zoom_level
        world_y = (screen_point.y - self.pan_offset.y) / self.zoom_level
        return Point(world_x, world_y)
    
    def world_to_screen(self, world_point: Point) -> Point:
        """Convert world coordinates to screen coordinates"""
        screen_x = world_point.x * self.zoom_level + self.pan_offset.x
        screen_y = world_point.y * self.zoom_level + self.pan_offset.y
        return Point(screen_x, screen_y)
    
    def snap_to_grid(self, point: Point) -> Point:
        """Snap point to grid"""
        if self.show_grid:
            grid_x = round(point.x / self.grid_size) * self.grid_size
            grid_y = round(point.y / self.grid_size) * self.grid_size
            return Point(grid_x, grid_y)
        return point
    
    def draw_grid(self):
        """Draw background grid"""
        if not self.show_grid:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Calculate grid bounds in world coordinates
        top_left = self.screen_to_world(Point(0, 0))
        bottom_right = self.screen_to_world(Point(canvas_width, canvas_height))
        
        # Draw vertical lines
        start_x = int(top_left.x / self.grid_size) * self.grid_size
        end_x = int(bottom_right.x / self.grid_size + 1) * self.grid_size
        
        for x in range(int(start_x), int(end_x) + 1, self.grid_size):
            screen_start = self.world_to_screen(Point(x, top_left.y))
            screen_end = self.world_to_screen(Point(x, bottom_right.y))
            self.canvas.create_line(screen_start.x, screen_start.y, 
                                  screen_end.x, screen_end.y, 
                                  fill=self.colors['grid'], width=1)
        
        # Draw horizontal lines
        start_y = int(top_left.y / self.grid_size) * self.grid_size
        end_y = int(bottom_right.y / self.grid_size + 1) * self.grid_size
        
        for y in range(int(start_y), int(end_y) + 1, self.grid_size):
            screen_start = self.world_to_screen(Point(top_left.x, y))
            screen_end = self.world_to_screen(Point(bottom_right.x, y))
            self.canvas.create_line(screen_start.x, screen_start.y, 
                                  screen_end.x, screen_end.y, 
                                  fill=self.colors['grid'], width=1)
    
    def draw_gate(self, gate: LogicGate):
        """Draw a logic gate"""
        screen_pos = self.world_to_screen(gate.position)
        screen_width = gate.width * self.zoom_level
        screen_height = gate.height * self.zoom_level
        
        x1 = screen_pos.x - screen_width / 2
        y1 = screen_pos.y - screen_height / 2
        x2 = screen_pos.x + screen_width / 2
        y2 = screen_pos.y + screen_height / 2
        
        # Gate body
        fill_color = self.colors['gate_selected'] if gate.selected else self.colors['gate_fill']
        
        if gate.gate_type in [GateType.AND, GateType.NAND]:
            # AND gate shape (rectangle with curved right side)
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                       fill=fill_color, outline=self.colors['gate_outline'], width=2)
            # Add curved right side (simplified as arc)
            self.canvas.create_arc(x2-20, y1, x2+20, y2, 
                                 start=270, extent=180, outline=self.colors['gate_outline'], width=2)
        
        elif gate.gate_type in [GateType.OR, GateType.NOR]:
            # OR gate shape (curved)
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                       fill=fill_color, outline=self.colors['gate_outline'], width=2)
        
        else:
            # Default rectangular shape
            self.canvas.create_rectangle(x1, y1, x2, y2, 
                                       fill=fill_color, outline=self.colors['gate_outline'], width=2)
        
        # Gate label
        self.canvas.create_text(screen_pos.x, screen_pos.y - 10, text=gate.label, 
                              font=("Arial", int(10 * self.zoom_level)), fill="black")
        
        # Show signal state on gate when simulating
        if hasattr(gate, 'state') and self.circuit.simulation_running:
            state_text = ""
            if gate.state == LogicState.HIGH:
                state_text = "1"
                state_color = self.colors['signal_high']
            elif gate.state == LogicState.LOW:
                state_text = "0"
                state_color = self.colors['signal_low']
            else:
                state_text = "?"
                state_color = self.colors['signal_unknown']
            
            self.canvas.create_text(screen_pos.x, screen_pos.y + 10, 
                                  text=state_text, font=("Arial", int(14 * self.zoom_level)), 
                                  fill=state_color)
        
        # Draw inversion bubble for NAND, NOR, NOT
        if gate.gate_type in [GateType.NAND, GateType.NOR, GateType.NOT]:
            bubble_radius = 5 * self.zoom_level
            bubble_x = x2 + bubble_radius
            bubble_y = screen_pos.y
            self.canvas.create_oval(bubble_x - bubble_radius, bubble_y - bubble_radius,
                                  bubble_x + bubble_radius, bubble_y + bubble_radius,
                                  fill="white", outline=self.colors['gate_outline'], width=2)
        
        # Draw pins
        for pin in gate.input_pins + gate.output_pins:
            self.draw_pin(pin)
    
    def draw_pin(self, pin: Pin):
        """Draw a pin"""
        screen_pos = self.world_to_screen(pin.position)
        radius = 4 * self.zoom_level
        
        color = self.colors['pin_input'] if pin.is_input else self.colors['pin_output']
        
        # Pin state indicator
        if pin.state == LogicState.HIGH:
            fill_color = self.colors['signal_high']
            # Draw signal value
            self.canvas.create_text(screen_pos.x + (10 if pin.is_input else -10) * self.zoom_level, 
                                  screen_pos.y - 10 * self.zoom_level,
                                  text="1", font=("Arial", int(10 * self.zoom_level)), 
                                  fill=fill_color)
        elif pin.state == LogicState.LOW:
            fill_color = self.colors['signal_low']
            # Draw signal value
            self.canvas.create_text(screen_pos.x + (10 if pin.is_input else -10) * self.zoom_level, 
                                  screen_pos.y - 10 * self.zoom_level,
                                  text="0", font=("Arial", int(10 * self.zoom_level)), 
                                  fill=fill_color)
        else:
            fill_color = self.colors['signal_unknown']
        
        self.canvas.create_oval(screen_pos.x - radius, screen_pos.y - radius,
                              screen_pos.x + radius, screen_pos.y + radius,
                              fill=fill_color, outline=color, width=2)
    
    def draw_wire(self, wire: Wire):
        """Draw a wire connection"""
        start_screen = self.world_to_screen(wire.start_pin.position)
        end_screen = self.world_to_screen(wire.end_pin.position)
        
        # Wire color based on state
        color = wire.color
        if wire.selected:
            color = self.colors['wire_selected']
        
        width = max(2, int(3 * self.zoom_level))
        
        if wire.path_points:
            # Draw wire with path points
            points = [start_screen]
            for point in wire.path_points:
                points.append(self.world_to_screen(point))
            points.append(end_screen)
            
            for i in range(len(points) - 1):
                self.canvas.create_line(points[i].x, points[i].y,
                                      points[i+1].x, points[i+1].y,
                                      fill=color, width=width)
                
                # Draw small circle at bend points
                if i > 0 and i < len(points) - 1:
                    radius = 3 * self.zoom_level
                    self.canvas.create_oval(
                        points[i].x - radius, points[i].y - radius,
                        points[i].x + radius, points[i].y + radius,
                        fill=color, outline=color
                    )
        else:
            # Direct connection
            self.canvas.create_line(start_screen.x, start_screen.y,
                                  end_screen.x, end_screen.y,
                                  fill=color, width=width)
    
    def draw_temp_wire(self):
        """Draw temporary wire during connection"""
        if self.connecting and self.connection_start_pin and self.temp_wire_end:
            start_screen = self.world_to_screen(self.connection_start_pin.position)
            end_screen = self.world_to_screen(self.temp_wire_end)
            
            self.canvas.create_line(start_screen.x, start_screen.y,
                                  end_screen.x, end_screen.y,
                                  fill="gray", width=2, dash=(5, 5))
    
    def draw_circuit(self):
        """Draw the entire circuit"""
        current_time = time.time()
        
        # Throttle drawing for performance
        if not self.draw_pending and current_time - self.last_draw_time < self.draw_throttle:
            if not self.draw_pending:
                self.draw_pending = True
                self.canvas.after(int(self.draw_throttle * 1000), self.deferred_draw)
            return
        
        self.last_draw_time = current_time
        self.draw_pending = False
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw grid
        if self.show_grid:
            self.draw_grid()
        
        # Draw wires first (so they appear behind gates)
        for wire in self.circuit.wires.values():
            self.draw_wire(wire)
        
        # Draw temporary wire
        self.draw_temp_wire()
        
        # Draw gates
        for gate in self.circuit.gates.values():
            self.draw_gate(gate)
    
    def deferred_draw(self):
        """Handle deferred drawing for performance"""
        self.draw_pending = False
        self.draw_circuit()

    def on_click(self, event):
        """Handle mouse click"""
        if self.space_pressed:
            # Start panning with space+click
            self.panning = True
            self.last_mouse_pos = Point(event.x, event.y)
            return
        
        # Convert screen coordinates to world coordinates
        world_pos = self.screen_to_world(Point(event.x, event.y))
        
        # Check if clicking on a wire first
        clicked_wire = None
        for wire in self.circuit.wires.values():
            if wire.contains_point(world_pos):
                clicked_wire = wire
                break
        
        if clicked_wire:
            self.selected_wire = clicked_wire
            self.selected_gate = None
            self.draw_circuit()
            return
        
        # Check if clicking on a gate
        clicked_gate = self.circuit.find_gate_at_position(world_pos)
        if clicked_gate:
            self.selected_gate = clicked_gate
            self.selected_wire = None
            self.dragging = True
            self.drag_start = world_pos
            self.draw_circuit()
            return
        
        # Check if clicking on a pin for connection
        clicked_pin = self.circuit.find_pin_at_position(world_pos)
        if clicked_pin:
            if not self.connecting:
                # Start connection
                self.connecting = True
                self.temp_wire_start = clicked_pin
                self.temp_wire_end = world_pos
            else:
                # Complete connection
                if self.temp_wire_start and clicked_pin != self.temp_wire_start:
                    wire = self.circuit.add_wire(self.temp_wire_start.id, clicked_pin.id)
                    if wire:
                        wire.auto_route()
                
                self.connecting = False
                self.temp_wire_start = None
                self.temp_wire_end = None
            
            self.draw_circuit()
            return
        
        # Click on empty space
        self.selected_gate = None
        self.selected_wire = None
        if self.connecting:
            self.connecting = False
            self.temp_wire_start = None
            self.temp_wire_end = None
        
        self.draw_circuit()
    
    def on_drag(self, event):
        """Handle mouse drag"""
        current_pos = Point(event.x, event.y)
        
        if self.space_pressed and self.panning:
            # Pan the canvas
            if self.last_mouse_pos:
                dx = current_pos.x - self.last_mouse_pos.x
                dy = current_pos.y - self.last_mouse_pos.y
                self.pan_offset.x += dx
                self.pan_offset.y += dy
                self.deferred_draw()
            self.last_mouse_pos = current_pos
            return
        
        world_pos = self.screen_to_world(current_pos)
        
        if self.dragging and self.selected_gate:
            # Drag selected gate
            self.selected_gate.move_to(world_pos)
            
            # Auto-route connected wires
            for wire in self.circuit.wires.values():
                if (wire.start_pin.gate == self.selected_gate or 
                    wire.end_pin.gate == self.selected_gate):
                    wire.auto_route()
            
            self.deferred_draw()
        
        elif self.wire_edit_mode and self.wire_edit_point is not None:
            # Drag wire bend point
            if self.selected_wire and 0 <= self.wire_edit_point < len(self.selected_wire.path_points):
                self.selected_wire.path_points[self.wire_edit_point] = world_pos
                self.deferred_draw()
        
        elif self.connecting and self.temp_wire_start:
            # Update temporary wire end position
            self.temp_wire_end = world_pos
            self.deferred_draw()
    
    def on_release(self, event):
        """Handle mouse release"""
        if self.space_pressed:
            self.panning = False
            return
            
        self.dragging = False
        self.wire_edit_mode = False
        self.wire_edit_point = None
    
    def on_right_click(self, event):
        """Handle right click (context menu)"""
        click_point = self.screen_to_world(Point(event.x, event.y))
        
        # Check if right-clicking on a wire
        for wire_id, wire in self.circuit.wires.items():
            if wire.contains_point(click_point):
                # Create context menu for wire
                context_menu = tk.Menu(self.parent, tearoff=0)
                context_menu.add_command(label="Add Bend Point", 
                                      command=lambda w=wire, p=click_point: self.add_wire_bend_point(w, p))
                context_menu.add_command(label="Delete Wire", 
                                      command=lambda w=wire_id: self.circuit.remove_wire(w))
                context_menu.add_command(label="Auto-Route", 
                                      command=lambda w=wire: self.auto_route_wire(w))
                
                try:
                    context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    context_menu.grab_release()
                return
        
        # Check if right-clicking on a gate
        clicked_gate = self.circuit.find_gate_at_position(click_point)
        if clicked_gate:
            # Create context menu for gate
            context_menu = tk.Menu(self.parent, tearoff=0)
            context_menu.add_command(label="Delete Gate", 
                                   command=lambda: self.delete_gate(clicked_gate.id))
            context_menu.add_command(label="Properties", 
                                   command=lambda: self.show_gate_properties(clicked_gate))
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
    
    def add_wire_bend_point(self, wire: Wire, point: Point):
        """Add a bend point to a wire at the specified position"""
        # Find the closest segment to insert the point
        points = [wire.start_pin.position] + wire.path_points + [wire.end_pin.position]
        min_dist = float('inf')
        insert_idx = 0
        
        for i in range(len(points) - 1):
            dist = wire._point_to_segment_distance(point, points[i], points[i+1])
            if dist < min_dist:
                min_dist = dist
                insert_idx = i + 1
        
        # Insert the new point
        wire.path_points.insert(insert_idx - 1, self.snap_to_grid(point))
        self.draw_circuit()
    
    def auto_route_wire(self, wire: Wire):
        """Auto-route a wire with right angles"""
        wire.auto_route()
        self.draw_circuit()
    
    def add_gate(self, gate_type: GateType):
        """Add a new gate to the circuit"""
        # Add at center of canvas
        canvas_center = Point(self.canvas.winfo_width() / 2, 
                            self.canvas.winfo_height() / 2)
        position = self.screen_to_world(canvas_center)
        
        position = self.snap_to_grid(position)
        gate = LogicGate(gate_type, position)
        self.circuit.add_gate(gate)
        self.draw_circuit()
        return gate
    
    def delete_gate(self, gate_id: str):
        """Delete a gate from the circuit"""
        self.circuit.remove_gate(gate_id)
        if self.selected_gate and self.selected_gate.id == gate_id:
            self.selected_gate = None
        self.draw_circuit()
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        if self.connecting and self.temp_wire_end:
            current_point = self.screen_to_world(Point(event.x, event.y))
            self.temp_wire_end = current_point
            self.draw_circuit()
    
    def on_zoom(self, event):
        """Handle mouse wheel zoom"""
        # Get mouse position for center-point zooming
        mouse_x = event.x
        mouse_y = event.y
        
        # Calculate zoom factor
        zoom_factor = 1.1 if event.delta > 0 else 1/1.1
        old_zoom = self.zoom_level
        
        # Apply zoom with limits
        self.zoom_level *= zoom_factor
        self.zoom_level = max(0.1, min(5.0, self.zoom_level))  # Limit zoom range
        
        # Calculate new pan offset to zoom towards mouse cursor
        if old_zoom != self.zoom_level:
            # Convert mouse position to world coordinates before zoom
            world_x = (mouse_x - self.pan_offset.x) / old_zoom
            world_y = (mouse_y - self.pan_offset.y) / old_zoom
            
            # Calculate new screen position after zoom
            new_screen_x = world_x * self.zoom_level + self.pan_offset.x
            new_screen_y = world_y * self.zoom_level + self.pan_offset.y
            
            # Adjust pan offset to keep mouse position fixed
            self.pan_offset.x += mouse_x - new_screen_x
            self.pan_offset.y += mouse_y - new_screen_y
        
        # Update display and redraw
        if hasattr(self.parent, 'update_zoom_display'):
            self.parent.update_zoom_display()
        
        self.draw_circuit()

    def on_middle_click(self, event):
        """Handle middle mouse button press (for panning)"""
        self.panning = True
        self.last_mouse_pos = Point(event.x, event.y)
    
    def on_middle_drag(self, event):
        """Handle middle mouse drag for panning"""
        if self.panning:
            dx = event.x - self.last_mouse_pos.x
            dy = event.y - self.last_mouse_pos.y
            
            self.pan_offset.x += dx
            self.pan_offset.y += dy
            
            self.last_mouse_pos = Point(event.x, event.y)
            self.draw_circuit()
    
    def on_middle_release(self, event):
        """Handle middle mouse button release"""
        self.panning = False
    
    def show_gate_properties(self, gate: LogicGate):
        """Show gate properties dialog"""
        props_window = tk.Toplevel(self.parent)
        props_window.title(f"Properties - {gate.label}")
        props_window.geometry("300x200")
        
        # Gate ID
        tk.Label(props_window, text="Gate ID:").pack(pady=5)
        id_entry = tk.Entry(props_window, width=30)
        id_entry.insert(0, gate.id)
        id_entry.pack(pady=5)
        
        # Gate Label
        tk.Label(props_window, text="Label:").pack(pady=5)
        label_entry = tk.Entry(props_window, width=30)
        label_entry.insert(0, gate.label)
        label_entry.pack(pady=5)
        
        # Gate-specific properties
        if gate.gate_type == GateType.CLOCK:
            tk.Label(props_window, text="Frequency (Hz):").pack(pady=5)
            freq_entry = tk.Entry(props_window, width=30)
            freq_entry.insert(0, str(getattr(gate, 'frequency', 1.0)))
            freq_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(props_window)
        button_frame.pack(pady=10)
        
        def apply_changes():
            gate.id = id_entry.get()
            gate.label = label_entry.get()
            
            if gate.gate_type == GateType.CLOCK:
                try:
                    gate.frequency = float(freq_entry.get())
                except ValueError:
                    pass
            
            self.draw_circuit()
            props_window.destroy()
        
        tk.Button(button_frame, text="Apply", command=apply_changes).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=props_window.destroy).pack(side=tk.LEFT, padx=5)

    def zoom_to_fit(self):
        """Zoom to fit all circuit elements"""
        if not self.circuit.gates:
            return
        
        # Find bounding box of all gates
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        for gate in self.circuit.gates.values():
            x1, y1, x2, y2 = gate.get_bounds()
            min_x = min(min_x, x1)
            min_y = min(min_y, y1)
            max_x = max(max_x, x2)
            max_y = max(max_y, y2)
        
        # Add some padding
        padding = 50
        min_x -= padding
        min_y -= padding
        max_x += padding
        max_y += padding
        
        # Calculate required zoom level
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width > 0 and canvas_height > 0:
            zoom_x = canvas_width / (max_x - min_x)
            zoom_y = canvas_height / (max_y - min_y)
            
            # Use the smaller zoom to fit everything
            self.zoom_level = min(zoom_x, zoom_y, 2.0)  # Max 200% for readability
            self.zoom_level = max(0.1, self.zoom_level)  # Min 10%
            
            # Center the view
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            
            self.pan_offset.x = canvas_width / 2 - center_x * self.zoom_level
            self.pan_offset.y = canvas_height / 2 - center_y * self.zoom_level
            
            self.draw_circuit()

    def on_space_press(self, event):
        """Handle space key press for pan mode"""
        self.space_pressed = True
        self.canvas.config(cursor="fleur")  # Change cursor to move cursor
    
    def on_space_release(self, event):
        """Handle space key release"""
        self.space_pressed = False
        self.panning = False
        self.canvas.config(cursor="")  # Reset cursor

class TimingDiagramWindow:
    """Window for displaying timing diagrams"""
    
    def __init__(self, parent, circuit: Circuit):
        self.window = tk.Toplevel(parent)
        self.window.title("Timing Diagram")
        self.window.geometry("800x600")
        
        self.circuit = circuit
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, self.window)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Control frame
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(control_frame, text="Refresh", command=self.update_diagram).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text="Clear History", command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
        self.update_diagram()
    
    def update_diagram(self):
        """Update the timing diagram"""
        self.ax.clear()
        
        if not self.circuit.signal_history:
            self.ax.text(0.5, 0.5, "No signal history available", 
                        ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()
            return
        
        # Plot each signal
        y_offset = 0
        signal_names = []
        
        for pin_id, history in self.circuit.signal_history.items():
            if not history:
                continue
            
            signal_names.append(pin_id)
            
            # Convert history to plottable format
            times = []
            values = []
            
            for time_point, state in history:
                times.append(time_point)
                if state == LogicState.HIGH:
                    values.append(1 + y_offset)
                elif state == LogicState.LOW:
                    values.append(0 + y_offset)
                else:
                    values.append(0.5 + y_offset)  # Unknown state
            
            if times and values:
                # Create step plot
                step_times = []
                step_values = []
                
                for i in range(len(times)):
                    step_times.append(times[i])
                    step_values.append(values[i])
                    
                    # Add step to next value
                    if i < len(times) - 1:
                        step_times.append(times[i+1])
                        step_values.append(values[i])
                
                self.ax.plot(step_times, step_values, linewidth=2, label=pin_id)
            
            y_offset += 2
        
        # Formatting
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Signals")
        self.ax.set_yticks(range(0, len(signal_names) * 2, 2))
        self.ax.set_yticklabels(signal_names)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        self.canvas.draw()
    
    def clear_history(self):
        """Clear signal history"""
        self.circuit.signal_history.clear()
        self.update_diagram()

class TruthTableWindow:
    """Window for displaying truth tables"""
    
    def __init__(self, parent, circuit: Circuit):
        self.window = tk.Toplevel(parent)
        self.window.title("Truth Table Generator")
        self.window.geometry("600x500")
        
        self.circuit = circuit
        
        # Input/Output selection frame
        selection_frame = tk.Frame(self.window)
        selection_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input pins
        tk.Label(selection_frame, text="Input Pins:").grid(row=0, column=0, sticky="w")
        self.input_listbox = tk.Listbox(selection_frame, selectmode=tk.MULTIPLE, height=6)
        self.input_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        # Output pins
        tk.Label(selection_frame, text="Output Pins:").grid(row=0, column=1, sticky="w")
        self.output_listbox = tk.Listbox(selection_frame, selectmode=tk.MULTIPLE, height=6)
        self.output_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(button_frame, text="Generate Table", command=self.generate_table).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh Pins", command=self.refresh_pins).pack(side=tk.LEFT, padx=5)
        
        # Truth table display
        self.table_frame = tk.Frame(self.window)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.refresh_pins()
    
    def refresh_pins(self):
        """Refresh the list of available pins"""
        self.input_listbox.delete(0, tk.END)
        self.output_listbox.delete(0, tk.END)
        
        for gate in self.circuit.gates.values():
            if gate.gate_type == GateType.INPUT:
                for pin in gate.output_pins:
                    self.input_listbox.insert(tk.END, f"{gate.label}: {pin.id}")
            
            if gate.gate_type == GateType.OUTPUT:
                for pin in gate.input_pins:
                    self.output_listbox.insert(tk.END, f"{gate.label}: {pin.id}")
            
            # Also add intermediate pins
            for pin in gate.output_pins:
                if gate.gate_type not in [GateType.INPUT, GateType.OUTPUT]:
                    self.output_listbox.insert(tk.END, f"{gate.label}: {pin.id}")
    
    def generate_table(self):
        """Generate and display truth table"""
        # Get selected pins
        input_selections = self.input_listbox.curselection()
        output_selections = self.output_listbox.curselection()
        
        if not input_selections or not output_selections:
            messagebox.showwarning("Warning", "Please select input and output pins")
            return
        
        input_pins = []
        output_pins = []
        
        for i in input_selections:
            pin_text = self.input_listbox.get(i)
            pin_id = pin_text.split(": ")[1]
            input_pins.append(pin_id)
        
        for i in output_selections:
            pin_text = self.output_listbox.get(i)
            pin_id = pin_text.split(": ")[1]
            output_pins.append(pin_id)
        
        # Generate truth table
        truth_table = self.circuit.generate_truth_table(input_pins, output_pins)
        
        # Clear previous table
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        if not truth_table:
            tk.Label(self.table_frame, text="Could not generate truth table").pack()
            return
        
        # Create table
        canvas = tk.Canvas(self.table_frame)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Headers
        headers = list(truth_table[0].keys())
        for col, header in enumerate(headers):
            tk.Label(scrollable_frame, text=header, font=("Arial", 10, "bold"), 
                    relief=tk.RAISED, borderwidth=1).grid(row=0, column=col, sticky="ew")
        
        # Data rows
        for row, data in enumerate(truth_table, start=1):
            for col, header in enumerate(headers):
                value = data.get(header, "?")
                tk.Label(scrollable_frame, text=str(value), 
                        relief=tk.RAISED, borderwidth=1).grid(row=row, column=col, sticky="ew")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

class BooleanExpressionParser:
    """Parser for Boolean expressions"""
    
    def __init__(self):
        self.variables = set()
        self.gate_counter = 0
    
    def parse_expression(self, expression: str) -> Dict:
        """Parse a boolean expression and return circuit structure"""
        # Clean up the expression
        expression = expression.strip()
        expression = re.sub(r'\s+', '', expression)  # Remove whitespace
        
        # Replace common operators
        expression = expression.replace('AND', '*')
        expression = expression.replace('OR', '+')
        expression = expression.replace('NOT', '~')
        expression = expression.replace('!', '~')
        expression = expression.replace('&', '*')
        expression = expression.replace('|', '+')
        expression = expression.replace('^', '@')  # XOR
        
        # Extract output variable if present
        output_var = "OUTPUT"
        if '=' in expression:
            parts = expression.split('=', 1)
            output_var = parts[0].strip()
            expression = parts[1].strip()
        
        # Find all variables
        self.variables = set()
        for char in expression:
            if char.isalpha() and char not in ['*', '+', '~', '@']:
                self.variables.add(char)
        
        # Parse the expression into a tree
        try:
            tree = self._parse_expression_tree(expression)
            return {
                'tree': tree,
                'variables': list(self.variables),
                'output': output_var
            }
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
    
    def _parse_expression_tree(self, expr: str) -> Dict:
        """Parse expression into a tree structure with correct operator precedence"""
        expr = expr.strip()
        
        # Handle parentheses
        if expr.startswith('(') and expr.endswith(')'):
            # Check if outer parentheses are balanced and necessary
            paren_count = 0
            for i, char in enumerate(expr):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                if paren_count == 0 and i < len(expr) - 1:
                    break
            if paren_count == 0 and i == len(expr) - 1:
                return self._parse_expression_tree(expr[1:-1])
        
        # Parse with correct precedence: OR (lowest) > XOR > AND > NOT (highest)
        return self._parse_or(expr)
    
    def _parse_or(self, expr: str) -> Dict:
        """Parse OR expressions (lowest precedence)"""
        # Find OR operators outside parentheses
        parts = []
        current_part = ""
        paren_count = 0
        
        for char in expr:
            if char == '(':
                paren_count += 1
                current_part += char
            elif char == ')':
                paren_count -= 1
                current_part += char
            elif char == '+' and paren_count == 0:
                # Found OR operator at top level
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        if len(parts) > 1:
            # Build OR tree from left to right
            result = self._parse_xor(parts[0])
            for part in parts[1:]:
                right = self._parse_xor(part)
                result = {
                    'type': 'OR',
                    'left': result,
                    'right': right
                }
            return result
        else:
            return self._parse_xor(expr)
    
    def _parse_xor(self, expr: str) -> Dict:
        """Parse XOR expressions"""
        # Find XOR operators outside parentheses
        parts = []
        current_part = ""
        paren_count = 0
        
        for char in expr:
            if char == '(':
                paren_count += 1
                current_part += char
            elif char == ')':
                paren_count -= 1
                current_part += char
            elif char == '@' and paren_count == 0:
                # Found XOR operator at top level
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        if len(parts) > 1:
            # Build XOR tree from left to right
            result = self._parse_and(parts[0])
            for part in parts[1:]:
                right = self._parse_and(part)
                result = {
                    'type': 'XOR',
                    'left': result,
                    'right': right
                }
            return result
        else:
            return self._parse_and(expr)
    
    def _parse_and(self, expr: str) -> Dict:
        """Parse AND expressions"""
        # Find AND operators outside parentheses
        parts = []
        current_part = ""
        paren_count = 0
        
        for char in expr:
            if char == '(':
                paren_count += 1
                current_part += char
            elif char == ')':
                paren_count -= 1
                current_part += char
            elif char == '*' and paren_count == 0:
                # Found AND operator at top level
                parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        if len(parts) > 1:
            # Build AND tree from left to right
            result = self._parse_not(parts[0])
            for part in parts[1:]:
                right = self._parse_not(part)
                result = {
                    'type': 'AND',
                    'left': result,
                    'right': right
                }
            return result
        else:
            return self._parse_not(expr)
    
    def _parse_not(self, expr: str) -> Dict:
        """Parse NOT expressions (highest precedence)"""
        expr = expr.strip()
        
        if expr.startswith('~'):
            # Handle NOT operator
            operand_expr = expr[1:].strip()
            
            # Handle parentheses after NOT
            if operand_expr.startswith('(') and operand_expr.endswith(')'):
                # Check if parentheses are balanced
                paren_count = 0
                for i, char in enumerate(operand_expr):
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    if paren_count == 0 and i < len(operand_expr) - 1:
                        break
                if paren_count == 0 and i == len(operand_expr) - 1:
                    # Parentheses are balanced and cover the whole expression
                    operand = self._parse_expression_tree(operand_expr[1:-1])
                    return {'type': 'NOT', 'operand': operand}
            
            # For single variable or complex expression without outer parentheses
            if len(operand_expr) == 1 and operand_expr.isalpha():
                # Single variable
                operand = {'type': 'VAR', 'name': operand_expr}
                return {'type': 'NOT', 'operand': operand}
            else:
                # Complex expression - parse recursively
                operand = self._parse_expression_tree(operand_expr)
                return {'type': 'NOT', 'operand': operand}
        
        # Handle parentheses
        if expr.startswith('(') and expr.endswith(')'):
            # Check if outer parentheses are balanced
            paren_count = 0
            for i, char in enumerate(expr):
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                if paren_count == 0 and i < len(expr) - 1:
                    break
            if paren_count == 0 and i == len(expr) - 1:
                return self._parse_expression_tree(expr[1:-1])
        
        # Must be a variable
        if expr.isalpha():
            return {'type': 'VAR', 'name': expr}
        
        raise ValueError(f"Cannot parse: {expr}")
    
    def _replace_temp_var(self, tree: Dict, temp_var: str, replacement: Dict) -> Dict:
        """Replace temporary variable in tree with replacement node"""
        if tree['type'] == 'VAR' and tree['name'] == temp_var:
            return replacement
        elif tree['type'] == 'NOT':
            return {'type': 'NOT', 'operand': self._replace_temp_var(tree['operand'], temp_var, replacement)}
        elif tree['type'] in ['AND', 'OR', 'XOR']:
            return {
                'type': tree['type'],
                'left': self._replace_temp_var(tree['left'], temp_var, replacement),
                'right': self._replace_temp_var(tree['right'], temp_var, replacement)
            }
        return tree
    
    def optimize_expression(self, tree: Dict) -> Dict:
        """Apply basic Boolean algebra optimizations"""
        # This is a simplified optimization - could be expanded
        return self._apply_optimizations(tree)
    
    def _apply_optimizations(self, tree: Dict) -> Dict:
        """Apply optimization rules recursively"""
        if tree['type'] == 'VAR':
            return tree
        
        if tree['type'] == 'NOT':
            operand = self._apply_optimizations(tree['operand'])
            
            # Double negation elimination: ~~A = A
            if operand['type'] == 'NOT':
                return operand['operand']
            
            # De Morgan's laws: ~(A+B) = ~A*~B, ~(A*B) = ~A+~B
            if operand['type'] == 'OR':
                return {
                    'type': 'AND',
                    'left': {'type': 'NOT', 'operand': operand['left']},
                    'right': {'type': 'NOT', 'operand': operand['right']}
                }
            elif operand['type'] == 'AND':
                return {
                    'type': 'OR',
                    'left': {'type': 'NOT', 'operand': operand['left']},
                    'right': {'type': 'NOT', 'operand': operand['right']}
                }
            
            return {'type': 'NOT', 'operand': operand}
        
        if tree['type'] in ['AND', 'OR', 'XOR']:
            left = self._apply_optimizations(tree['left'])
            right = self._apply_optimizations(tree['right'])
            
            # Check for identical operands (Idempotent laws)
            if self._trees_equal(left, right):
                if tree['type'] in ['AND', 'OR']:
                    return left  # A*A = A, A+A = A
                elif tree['type'] == 'XOR':
                    return {'type': 'VAR', 'name': '0'}  # A@A = 0
            
            # Check for complementary operands
            if ((left['type'] == 'NOT' and self._trees_equal(left['operand'], right)) or
                (right['type'] == 'NOT' and self._trees_equal(right['operand'], left))):
                if tree['type'] == 'AND':
                    return {'type': 'VAR', 'name': '0'}  # A*~A = 0
                elif tree['type'] == 'OR':
                    return {'type': 'VAR', 'name': '1'}  # A+~A = 1
                elif tree['type'] == 'XOR':
                    return {'type': 'VAR', 'name': '1'}  # A@~A = 1
            
            # Absorption laws: A*(A+B) = A, A+(A*B) = A
            if tree['type'] == 'AND':
                if (right['type'] == 'OR' and 
                    (self._trees_equal(left, right['left']) or self._trees_equal(left, right['right']))):
                    return left
                if (left['type'] == 'OR' and 
                    (self._trees_equal(right, left['left']) or self._trees_equal(right, left['right']))):
                    return right
            elif tree['type'] == 'OR':
                if (right['type'] == 'AND' and 
                    (self._trees_equal(left, right['left']) or self._trees_equal(left, right['right']))):
                    return left
                if (left['type'] == 'AND' and 
                    (self._trees_equal(right, left['left']) or self._trees_equal(right, left['right']))):
                    return right
            
            return {
                'type': tree['type'],
                'left': left,
                'right': right
            }
        
        return tree
    
    def _trees_equal(self, tree1: Dict, tree2: Dict) -> bool:
        """Check if two expression trees are equal"""
        if tree1['type'] != tree2['type']:
            return False
        
        if tree1['type'] == 'VAR':
            return tree1['name'] == tree2['name']
        elif tree1['type'] == 'NOT':
            return self._trees_equal(tree1['operand'], tree2['operand'])
        elif tree1['type'] in ['AND', 'OR', 'XOR']:
            return ((self._trees_equal(tree1['left'], tree2['left']) and 
                    self._trees_equal(tree1['right'], tree2['right'])) or
                   (tree1['type'] in ['AND', 'OR'] and  # Commutative operations
                    self._trees_equal(tree1['left'], tree2['right']) and 
                    self._trees_equal(tree1['right'], tree2['left'])))
        
        return False
    
    def tree_to_circuit(self, tree: Dict, canvas, start_x: float = 100, start_y: float = 100) -> Dict:
        """Convert expression tree to circuit gates"""
        self.gate_counter = 0
        input_gates = {}
        
        # Calculate circuit layout
        layout = self._calculate_layout(tree)
        
        # Create input gates for all variables
        input_y_start = start_y - (len(self.variables) - 1) * 40
        y_offset = 0
        for var in sorted(self.variables):
            input_gate = LogicGate(GateType.INPUT, Point(start_x, input_y_start + y_offset))
            input_gate.label = var
            input_gate.id = f"INPUT_{var}"
            canvas.circuit.add_gate(input_gate)
            input_gates[var] = input_gate
            y_offset += 80
        
        # Build the circuit from the tree with improved layout
        output_gate = self._build_circuit_with_layout(tree, canvas, input_gates, layout, start_x + 200)
        
        # Create output gate
        final_output = LogicGate(GateType.OUTPUT, Point(output_gate.position.x + 200, output_gate.position.y))
        final_output.label = "OUTPUT"
        canvas.circuit.add_gate(final_output)
        
        # Connect to output
        try:
            if hasattr(output_gate, 'output_pins') and output_gate.output_pins:
                if hasattr(final_output, 'input_pins') and final_output.input_pins:
                    canvas.circuit.add_wire(output_gate.output_pins[0].id, final_output.input_pins[0].id)
                else:
                    print(f"Warning: final_output has no input pins")
            else:
                print(f"Warning: output_gate has no output pins")
        except Exception as e:
            print(f"Error connecting output: {e}")
        
        return {
            'inputs': input_gates,
            'output': final_output
        }
    
    def _calculate_layout(self, tree: Dict) -> Dict:
        """Calculate optimal layout for the circuit"""
        layout = {}
        
        def calculate_depth_and_width(node, depth=0):
            if node['type'] == 'VAR':
                layout[id(node)] = {'depth': 0, 'width': 1, 'height': 1}
                return 1, 1
            
            if node['type'] == 'NOT':
                width, height = calculate_depth_and_width(node['operand'], depth + 1)
                layout[id(node)] = {'depth': depth, 'width': width, 'height': height}
                return width, height
            
            if node['type'] in ['AND', 'OR', 'XOR']:
                left_width, left_height = calculate_depth_and_width(node['left'], depth + 1)
                right_width, right_height = calculate_depth_and_width(node['right'], depth + 1)
                
                total_width = max(left_width, right_width)
                total_height = left_height + right_height
                
                layout[id(node)] = {
                    'depth': depth,
                    'width': total_width,
                    'height': total_height,
                    'left_height': left_height,
                    'right_height': right_height
                }
                return total_width, total_height
            
            return 1, 1
        
        calculate_depth_and_width(tree)
        return layout
    
    def _build_circuit_with_layout(self, tree: Dict, canvas, input_gates: Dict, layout: Dict, 
                                 base_x: float, base_y: float = 300) -> LogicGate:
        """Build circuit with improved layout"""
        node_id = id(tree)
        node_layout = layout.get(node_id, {'depth': 0, 'width': 1, 'height': 1})
        
        if tree['type'] == 'VAR':
            return input_gates[tree['name']]
        
        # Calculate position based on depth and layout
        x = base_x + node_layout['depth'] * 150
        y = base_y
        
        if tree['type'] == 'NOT':
            operand_gate = self._build_circuit_with_layout(
                tree['operand'], canvas, input_gates, layout, base_x, base_y
            )
            
            # Position NOT gate to the right of its operand
            not_x = operand_gate.position.x + 120
            not_gate = LogicGate(GateType.NOT, Point(not_x, operand_gate.position.y))
            not_gate.id = f"NOT_{self.gate_counter}"
            self.gate_counter += 1
            canvas.circuit.add_gate(not_gate)
            
            # Connect operand to NOT gate
            try:
                if hasattr(operand_gate, 'output_pins') and operand_gate.output_pins:
                    if hasattr(not_gate, 'input_pins') and not_gate.input_pins:
                        canvas.circuit.add_wire(operand_gate.output_pins[0].id, not_gate.input_pins[0].id)
                    else:
                        print(f"Warning: NOT gate has no input pins")
                else:
                    print(f"Warning: operand gate has no output pins")
            except Exception as e:
                print(f"Error connecting NOT gate: {e}")
            return not_gate
        
        if tree['type'] in ['AND', 'OR', 'XOR']:
            # Determine gate type
            if tree['type'] == 'AND':
                gate_type = GateType.AND
            elif tree['type'] == 'OR':
                gate_type = GateType.OR
            else:  # XOR
                gate_type = GateType.XOR
            
            # Calculate positions for left and right operands
            left_height = node_layout.get('left_height', 1)
            right_height = node_layout.get('right_height', 1)
            total_height = left_height + right_height
            
            # Position left operand above center
            left_y = base_y - (left_height * 30)
            left_gate = self._build_circuit_with_layout(
                tree['left'], canvas, input_gates, layout, base_x, left_y
            )
            
            # Position right operand below center
            right_y = base_y + (right_height * 30)
            right_gate = self._build_circuit_with_layout(
                tree['right'], canvas, input_gates, layout, base_x, right_y
            )
            
            # Position main gate between operands
            gate_x = max(left_gate.position.x, right_gate.position.x) + 150
            gate_y = (left_gate.position.y + right_gate.position.y) / 2
            
            gate = LogicGate(gate_type, Point(gate_x, gate_y))
            gate.id = f"{tree['type']}_{self.gate_counter}"
            self.gate_counter += 1
            canvas.circuit.add_gate(gate)
            
            # Connect operands to gate
            try:
                if hasattr(left_gate, 'output_pins') and left_gate.output_pins:
                    if hasattr(gate, 'input_pins') and len(gate.input_pins) > 0:
                        canvas.circuit.add_wire(left_gate.output_pins[0].id, gate.input_pins[0].id)
                    else:
                        print(f"Warning: gate has no input pins")
                else:
                    print(f"Warning: left_gate has no output pins")
                
                if hasattr(right_gate, 'output_pins') and right_gate.output_pins:
                    if hasattr(gate, 'input_pins') and len(gate.input_pins) > 1:
                        canvas.circuit.add_wire(right_gate.output_pins[0].id, gate.input_pins[1].id)
                    else:
                        print(f"Warning: gate has no second input pin")
                else:
                    print(f"Warning: right_gate has no output pins")
            except Exception as e:
                print(f"Error connecting {tree['type']} gate: {e}")
            
            return gate
        
        raise ValueError(f"Unknown tree type: {tree['type']}")

class ExpressionInputDialog:
    """Dialog for entering Boolean expressions"""
    
    def __init__(self, parent, canvas):
        self.parent = parent
        self.canvas = canvas
        self.result = None
        
        self.window = tk.Toplevel(parent)
        self.window.title("Boolean Expression Input")
        self.window.geometry("600x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main frame
        main_frame = tk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = tk.Label(main_frame, 
                              text="Enter Boolean Expression:", 
                              font=("Arial", 12, "bold"))
        instructions.pack(anchor="w", pady=(0, 5))
        
        help_text = tk.Label(main_frame, 
                           text="Syntax: Use +, *, ~ for OR, AND, NOT\n" +
                                "Example: OUTPUT = ~((A+B)*C)\n" +
                                "Variables: A-Z, operators: +, *, ~, (, )",
                           font=("Arial", 9),
                           fg="gray")
        help_text.pack(anchor="w", pady=(0, 10))
        
        # Expression input
        self.expr_var = tk.StringVar()
        self.expr_var.set("OUTPUT = ~((A+B)*C)")
        
        expr_frame = tk.Frame(main_frame)
        expr_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(expr_frame, text="Expression:").pack(anchor="w")
        self.expr_entry = tk.Entry(expr_frame, textvariable=self.expr_var, font=("Courier", 12))
        self.expr_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="Generation Options")
        options_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.optimize_var = tk.BooleanVar(value=False)  # Tắt optimization mặc định
        tk.Checkbutton(options_frame, text="Apply Boolean algebra optimizations", 
                      variable=self.optimize_var).pack(anchor="w", padx=5, pady=2)
        
        self.auto_arrange_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Auto-arrange circuit layout", 
                      variable=self.auto_arrange_var).pack(anchor="w", padx=5, pady=2)
        
        self.clean_routing_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_frame, text="Use clean wire routing", 
                      variable=self.clean_routing_var).pack(anchor="w", padx=5, pady=2)
        
        # Preview area
        preview_frame = tk.LabelFrame(main_frame, text="Expression Tree Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.preview_text = tk.Text(preview_frame, height=6, font=("Courier", 10))
        scrollbar = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=scrollbar.set)
        
        self.preview_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(button_frame, text="Preview", command=self.preview_expression).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(button_frame, text="Generate Circuit", command=self.generate_circuit, 
                 bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
        # Bind Enter key to preview
        self.expr_entry.bind("<KeyRelease>", lambda e: self.preview_expression())
        
        # Initial preview
        self.preview_expression()
    
    def preview_expression(self):
        """Preview the parsed expression"""
        try:
            parser = BooleanExpressionParser()
            result = parser.parse_expression(self.expr_var.get())
            
            # Optimize the expression
            optimized_tree = parser.optimize_expression(result['tree'])
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, "Parsed Expression:\n")
            self.preview_text.insert(tk.END, f"Output: {result['output']}\n")
            self.preview_text.insert(tk.END, f"Variables: {', '.join(result['variables'])}\n\n")
            
            self.preview_text.insert(tk.END, "Original Expression Tree:\n")
            self.preview_text.insert(tk.END, self._tree_to_string(result['tree']))
            self.preview_text.insert(tk.END, "\n")
            
            # Show optimized version if different
            if not self._trees_equal_simple(result['tree'], optimized_tree):
                self.preview_text.insert(tk.END, "Optimized Expression Tree:\n")
                self.preview_text.insert(tk.END, self._tree_to_string(optimized_tree))
                self.preview_text.insert(tk.END, "\nOptimizations applied: Boolean algebra rules\n")
            else:
                self.preview_text.insert(tk.END, "Expression is already optimized.\n")
            
        except Exception as e:
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(tk.END, f"Error: {str(e)}")
    
    def _trees_equal_simple(self, tree1: Dict, tree2: Dict) -> bool:
        """Simple tree equality check for preview"""
        if tree1['type'] != tree2['type']:
            return False
        
        if tree1['type'] == 'VAR':
            return tree1['name'] == tree2['name']
        elif tree1['type'] == 'NOT':
            return self._trees_equal_simple(tree1['operand'], tree2['operand'])
        elif tree1['type'] in ['AND', 'OR', 'XOR']:
            return (self._trees_equal_simple(tree1['left'], tree2['left']) and 
                   self._trees_equal_simple(tree1['right'], tree2['right']))
        
        return False
    
    def _tree_to_string(self, tree, indent=0):
        """Convert tree to readable string"""
        spaces = "  " * indent
        
        if tree['type'] == 'VAR':
            return f"{spaces}{tree['name']}\n"
        elif tree['type'] == 'NOT':
            result = f"{spaces}NOT\n"
            result += self._tree_to_string(tree['operand'], indent + 1)
            return result
        else:
            result = f"{spaces}{tree['type']}\n"
            result += self._tree_to_string(tree['left'], indent + 1)
            result += self._tree_to_string(tree['right'], indent + 1)
            return result
    
    def generate_circuit(self):
        """Generate circuit from expression"""
        try:
            parser = BooleanExpressionParser()
            result = parser.parse_expression(self.expr_var.get())
            
            # Choose whether to optimize based on checkbox
            if self.optimize_var.get():
                # Use optimized expression
                tree_to_use = parser.optimize_expression(result['tree'])
                result['optimized_tree'] = tree_to_use
            else:
                # Use original expression structure
                tree_to_use = result['tree']
                result['optimized_tree'] = tree_to_use
            
            # Clear existing circuit
            self.canvas.circuit = Circuit()
            
            # Generate circuit from chosen tree
            circuit_info = parser.tree_to_circuit(tree_to_use, self.canvas)
            
            # Auto-arrange the circuit for better appearance if requested
            if self.auto_arrange_var.get():
                self._auto_arrange_circuit()
            
            # Redraw canvas
            self.canvas.draw_circuit()
            
            self.result = result
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate circuit: {str(e)}")
    
    def _auto_arrange_circuit(self):
        """Automatically arrange circuit for better appearance"""
        # Re-route all wires for better appearance
        for wire in self.canvas.circuit.wires.values():
            wire.auto_route()
        
        # Align gates in layers
        self._align_gates_in_layers()
    
    def _align_gates_in_layers(self):
        """Align gates in horizontal layers"""
        if not self.canvas.circuit.gates:
            return
        
        # Group gates by their x-coordinate (layer)
        layers = {}
        for gate in self.canvas.circuit.gates.values():
            x_layer = round(gate.position.x / 150) * 150  # Snap to 150-pixel grid
            if x_layer not in layers:
                layers[x_layer] = []
            layers[x_layer].append(gate)
        
        # Align gates within each layer
        for x_pos, gates_in_layer in layers.items():
            if len(gates_in_layer) <= 1:
                continue
            
            # Sort gates by y-coordinate
            gates_in_layer.sort(key=lambda g: g.position.y)
            
            # Calculate optimal spacing
            total_height = (len(gates_in_layer) - 1) * 100
            start_y = 300 - total_height / 2
            
            # Reposition gates
            for i, gate in enumerate(gates_in_layer):
                new_y = start_y + i * 100
                gate.move_to(Point(x_pos, new_y))
        
        # Re-route wires after repositioning
        for wire in self.canvas.circuit.wires.values():
            wire.auto_route()
    
    def cancel(self):
        """Cancel dialog"""
        self.window.destroy()

class DigitalCircuitDesigner:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Digital Circuit Designer")
        self.root.geometry("1400x900")
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-e>', lambda e: self.show_expression_dialog())
        self.root.bind('<Control-E>', lambda e: self.show_expression_dialog())
        self.root.bind('<Control-plus>', lambda e: self.zoom_in())
        self.root.bind('<Control-equal>', lambda e: self.zoom_in())  # For keyboards without numpad
        self.root.bind('<Control-minus>', lambda e: self.zoom_out())
        self.root.bind('<Control-0>', lambda e: self.reset_zoom())
        self.root.bind('<Control-f>', lambda e: self.zoom_to_fit())
        self.root.bind('<Control-F>', lambda e: self.zoom_to_fit())
        self.root.bind('<Control-g>', lambda e: self.toggle_grid())
        self.root.bind('<Control-G>', lambda e: self.toggle_grid())
        
        # Create main menu
        self.create_menu()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main layout
        self.create_layout()
        
        # Simulation thread
        self.simulation_thread = None
        self.simulation_running = False
        
        # Start simulation timer
        self.simulation_timer()
    
    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Circuit", command=self.new_circuit)
        file_menu.add_command(label="Open Circuit", command=self.open_circuit)
        file_menu.add_command(label="Save Circuit", command=self.save_circuit)
        file_menu.add_command(label="Save As...", command=self.save_circuit_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export Verilog", command=self.export_verilog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Clear Circuit", command=self.clear_circuit)
        edit_menu.add_separator()
        edit_menu.add_command(label="📝 Boolean Expression... (Ctrl+E)", command=self.show_expression_dialog, 
                            accelerator="Ctrl+E")
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="🔍+ Zoom In", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="🔍- Zoom Out", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="1:1 Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")
        view_menu.add_command(label="⤢ Zoom to Fit", command=self.zoom_to_fit, accelerator="Ctrl+F")
        view_menu.add_separator()
        view_menu.add_command(label="Show Grid", command=self.toggle_grid, accelerator="Ctrl+G")
        view_menu.add_separator()
        view_menu.add_command(label="Pan Tool (Middle Mouse)", state="disabled")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="📝 Expression to Circuit (Ctrl+E)", command=self.show_expression_dialog,
                             accelerator="Ctrl+E")
        tools_menu.add_separator()
        tools_menu.add_command(label="Optimize Circuit", command=self.optimize_circuit)
        tools_menu.add_command(label="Minimize Expression", command=self.minimize_expression)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start Simulation", command=self.start_simulation)
        sim_menu.add_command(label="Stop Simulation", command=self.stop_simulation)
        sim_menu.add_command(label="Reset Simulation", command=self.reset_simulation)
        sim_menu.add_separator()
        sim_menu.add_command(label="Timing Diagram", command=self.show_timing_diagram)
        sim_menu.add_command(label="Truth Table", command=self.show_truth_table)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Expression Syntax", command=self.show_expression_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_toolbar(self):
        """Create application toolbar"""
        self.toolbar = tk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Gate buttons
        gate_types = [
            ("AND", GateType.AND),
            ("OR", GateType.OR),
            ("XOR", GateType.XOR),
            ("NOT", GateType.NOT),
            ("NAND", GateType.NAND),
            ("NOR", GateType.NOR),
            ("INPUT", GateType.INPUT),
            ("OUTPUT", GateType.OUTPUT),
            ("CLOCK", GateType.CLOCK),
            ("D-FF", GateType.D_FLIP_FLOP)
        ]
        
        for label, gate_type in gate_types:
            btn = tk.Button(self.toolbar, text=label, 
                          command=lambda gt=gate_type: self.add_gate(gt))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Separator
        tk.Frame(self.toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Expression button - make it more prominent
        self.expr_button = tk.Button(self.toolbar, text="📝 Expression", 
                                   bg="#4CAF50", fg="white", font=("Arial", 10, "bold"),
                                   command=self.show_expression_dialog, 
                                   relief=tk.RAISED, borderwidth=2)
        self.expr_button.pack(side=tk.LEFT, padx=5, pady=2)
        
        # Add tooltip
        self.create_tooltip(self.expr_button, "Generate circuit from Boolean expression\n(e.g., OUTPUT = ~((A+B)*C))")
        
        # Separator
        tk.Frame(self.toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Zoom controls
        zoom_frame = tk.Frame(self.toolbar)
        zoom_frame.pack(side=tk.LEFT, padx=5)
        
        tk.Button(zoom_frame, text="🔍+", font=("Arial", 12, "bold"), 
                 command=self.zoom_in, width=3, height=1,
                 bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=1)
        
        tk.Button(zoom_frame, text="🔍-", font=("Arial", 12, "bold"), 
                 command=self.zoom_out, width=3, height=1,
                 bg="#2196F3", fg="white").pack(side=tk.LEFT, padx=1)
        
        tk.Button(zoom_frame, text="1:1", font=("Arial", 10, "bold"), 
                 command=self.reset_zoom, width=3, height=1,
                 bg="#FF9800", fg="white").pack(side=tk.LEFT, padx=1)
        
        tk.Button(zoom_frame, text="⤢", font=("Arial", 12, "bold"), 
                 command=self.zoom_to_fit, width=3, height=1,
                 bg="#9C27B0", fg="white").pack(side=tk.LEFT, padx=1)
        
        # Pan controls
        pan_frame = tk.Frame(self.toolbar)
        pan_frame.pack(side=tk.LEFT, padx=5)
        
        # Pan buttons arranged in cross pattern
        pan_up = tk.Button(pan_frame, text="↑", font=("Arial", 12, "bold"),
                          command=self.pan_up, width=2, height=1,
                          bg="#4CAF50", fg="white")
        pan_up.grid(row=0, column=1, padx=1, pady=1)
        
        pan_left = tk.Button(pan_frame, text="←", font=("Arial", 12, "bold"),
                            command=self.pan_left, width=2, height=1,
                            bg="#4CAF50", fg="white")
        pan_left.grid(row=1, column=0, padx=1, pady=1)
        
        pan_center = tk.Button(pan_frame, text="⌂", font=("Arial", 10, "bold"),
                              command=self.pan_center, width=2, height=1,
                              bg="#FF5722", fg="white")
        pan_center.grid(row=1, column=1, padx=1, pady=1)
        
        pan_right = tk.Button(pan_frame, text="→", font=("Arial", 12, "bold"),
                             command=self.pan_right, width=2, height=1,
                             bg="#4CAF50", fg="white")
        pan_right.grid(row=1, column=2, padx=1, pady=1)
        
        pan_down = tk.Button(pan_frame, text="↓", font=("Arial", 12, "bold"),
                            command=self.pan_down, width=2, height=1,
                            bg="#4CAF50", fg="white")
        pan_down.grid(row=2, column=1, padx=1, pady=1)
        
        # Zoom level display
        self.zoom_label = tk.Label(self.toolbar, text="100%", font=("Arial", 9))
        self.zoom_label.pack(side=tk.LEFT, padx=5)
        
        # Add tooltips for zoom buttons
        self.create_tooltip(zoom_frame.winfo_children()[0], "Zoom In (Mouse Wheel Up)")
        self.create_tooltip(zoom_frame.winfo_children()[1], "Zoom Out (Mouse Wheel Down)")
        self.create_tooltip(zoom_frame.winfo_children()[2], "Reset Zoom to 100%")
        self.create_tooltip(zoom_frame.winfo_children()[3], "Zoom to Fit All Elements")
        
        # Add tooltips for pan buttons
        self.create_tooltip(pan_up, "Pan Up")
        self.create_tooltip(pan_left, "Pan Left")
        self.create_tooltip(pan_center, "Center View")
        self.create_tooltip(pan_right, "Pan Right")
        self.create_tooltip(pan_down, "Pan Down")
        
        # Separator
        tk.Frame(self.toolbar, width=2, bg="gray").pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Simulation controls
        self.sim_button = tk.Button(self.toolbar, text="Start Sim", 
                                  command=self.toggle_simulation)
        self.sim_button.pack(side=tk.LEFT, padx=2, pady=2)
        
        tk.Button(self.toolbar, text="Reset", 
                 command=self.reset_simulation).pack(side=tk.LEFT, padx=2, pady=2)
        
        # Status label
        self.status_label = tk.Label(self.toolbar, text="Ready - Space+Drag to pan, Mouse wheel to zoom, Middle mouse to pan")
        self.status_label.pack(side=tk.RIGHT, padx=10)
    
    def create_tooltip(self, widget, text):
        """Create tooltip for widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", 
                           relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def create_layout(self):
        """Create main application layout"""
        # Main paned window
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for component library
        left_panel = tk.Frame(main_paned, width=200, bg="lightgray")
        main_paned.add(left_panel)
        
        tk.Label(left_panel, text="Component Library", 
                font=("Arial", 12, "bold"), bg="lightgray").pack(pady=10)
        
        # Component categories
        categories = [
            ("Basic Gates", [GateType.AND, GateType.OR, GateType.XOR, GateType.NOT]),
            ("Advanced Gates", [GateType.NAND, GateType.NOR, GateType.XNOR]),
            ("Sequential", [GateType.D_FLIP_FLOP, GateType.JK_FLIP_FLOP]),
            ("I/O", [GateType.INPUT, GateType.OUTPUT, GateType.CLOCK])
        ]
        
        for category_name, gates in categories:
            frame = tk.LabelFrame(left_panel, text=category_name, bg="lightgray")
            frame.pack(fill=tk.X, padx=5, pady=5)
            
            for gate_type in gates:
                btn = tk.Button(frame, text=gate_type.value, 
                              command=lambda gt=gate_type: self.add_gate(gt))
                btn.pack(fill=tk.X, padx=2, pady=1)
        
        # Right panel for circuit canvas
        right_panel = tk.Frame(main_paned)
        main_paned.add(right_panel)
        
        # Create circuit canvas
        self.canvas = CircuitCanvas(right_panel, Circuit())
        
        # Bottom panel for properties
        bottom_panel = tk.Frame(self.root, height=100, bg="lightgray")
        bottom_panel.pack(side=tk.BOTTOM, fill=tk.X)
        
        tk.Label(bottom_panel, text="Properties", 
                font=("Arial", 10, "bold"), bg="lightgray").pack(anchor="w", padx=5)
        
        self.properties_text = tk.Text(bottom_panel, height=5)
        self.properties_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def add_gate(self, gate_type: GateType):
        """Add a gate to the circuit"""
        gate = self.canvas.add_gate(gate_type)
        self.update_status(f"Added {gate_type.value} gate")
    
    def toggle_simulation(self):
        """Toggle simulation on/off"""
        if self.simulation_running:
            self.stop_simulation()
        else:
            self.start_simulation()
    
    def start_simulation(self):
        """Start circuit simulation"""
        self.canvas.circuit.start_simulation()
        self.simulation_running = True
        self.sim_button.config(text="Stop Sim")
        self.update_status("Simulation started")
    
    def stop_simulation(self):
        """Stop circuit simulation"""
        self.canvas.circuit.stop_simulation()
        self.simulation_running = False
        self.sim_button.config(text="Start Sim")
        self.update_status("Simulation stopped")
    
    def reset_simulation(self):
        """Reset circuit simulation"""
        self.canvas.circuit.reset_simulation()
        self.canvas.draw_circuit()
        self.update_status("Simulation reset")
    
    def simulation_timer(self):
        """Simulation timer callback"""
        if self.simulation_running:
            self.canvas.circuit.simulate_step()
            self.canvas.draw_circuit()
        
        # Schedule next update
        self.root.after(100, self.simulation_timer)  # 100ms = 10 FPS
    
    def new_circuit(self):
        """Create new circuit"""
        self.canvas.circuit = Circuit()
        self.canvas.draw_circuit()
        self.update_status("New circuit created")
    
    def open_circuit(self):
        """Open circuit from file"""
        filename = filedialog.askopenfilename(
            title="Open Circuit",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.canvas.circuit.load_from_file(filename)
                self.canvas.draw_circuit()
                self.update_status(f"Opened circuit: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_circuit(self):
        """Save current circuit"""
        if not hasattr(self, 'current_filename'):
            self.save_circuit_as()
        else:
            try:
                self.canvas.circuit.save_to_file(self.current_filename)
                self.update_status(f"Saved circuit: {self.current_filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def save_circuit_as(self):
        """Save circuit with new filename"""
        filename = filedialog.asksaveasfilename(
            title="Save Circuit As",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                self.canvas.circuit.save_to_file(filename)
                self.current_filename = filename
                self.update_status(f"Saved circuit: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def export_verilog(self):
        """Export circuit to Verilog"""
        filename = filedialog.asksaveasfilename(
            title="Export Verilog",
            defaultextension=".v",
            filetypes=[("Verilog files", "*.v"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                verilog_code = self.canvas.circuit.export_verilog()
                with open(filename, 'w') as f:
                    f.write(verilog_code)
                self.update_status(f"Exported Verilog: {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export Verilog: {e}")
    
    def clear_circuit(self):
        """Clear current circuit"""
        if messagebox.askyesno("Confirm", "Clear current circuit?"):
            self.new_circuit()
    
    def toggle_grid(self):
        """Toggle grid display"""
        self.canvas.show_grid = not self.canvas.show_grid
        self.canvas.draw_circuit()
    
    def zoom_in(self):
        """Zoom in"""
        self.canvas.zoom_level *= 1.2
        self.canvas.zoom_level = min(5.0, self.canvas.zoom_level)  # Max zoom 500%
        self.update_zoom_display()
        self.canvas.draw_circuit()
    
    def zoom_out(self):
        """Zoom out"""
        self.canvas.zoom_level /= 1.2
        self.canvas.zoom_level = max(0.1, self.canvas.zoom_level)  # Min zoom 10%
        self.update_zoom_display()
        self.canvas.draw_circuit()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.canvas.zoom_level = 1.0
        self.update_zoom_display()
        self.canvas.draw_circuit()
    
    def update_zoom_display(self):
        """Update zoom level display"""
        zoom_percent = int(self.canvas.zoom_level * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")
        
        # Update status
        self.update_status(f"Zoom: {zoom_percent}%")
    
    def show_timing_diagram(self):
        """Show timing diagram window"""
        TimingDiagramWindow(self.root, self.canvas.circuit)
    
    def show_truth_table(self):
        """Show truth table window"""
        TruthTableWindow(self.root, self.canvas.circuit)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Digital Circuit Designer v1.0

A comprehensive digital circuit design and simulation tool.

Features:
- Drag-and-drop circuit design
- Real-time logic simulation
- Timing diagram visualization
- Truth table generation
- Verilog export
- RTL design capabilities

Created with Python and Tkinter
        """
        messagebox.showinfo("About", about_text)
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()
    
    def show_expression_dialog(self):
        """Show Boolean expression input dialog"""
        dialog = ExpressionInputDialog(self.root, self.canvas)
        self.root.wait_window(dialog.window)
        
        if dialog.result:
            self.update_status(f"Generated circuit from expression: {dialog.result['output']}")
    
    def optimize_circuit(self):
        """Optimize current circuit"""
        # This is a placeholder for circuit optimization
        messagebox.showinfo("Circuit Optimization", 
                          "Circuit optimization feature is under development.\n" +
                          "This would analyze the current circuit and suggest optimizations.")
    
    def minimize_expression(self):
        """Minimize Boolean expression using Quine-McCluskey or similar"""
        # This is a placeholder for expression minimization
        messagebox.showinfo("Expression Minimization", 
                          "Expression minimization feature is under development.\n" +
                          "This would use Karnaugh maps or Quine-McCluskey algorithm\n" +
                          "to find the minimal expression.")
    
    def show_expression_help(self):
        """Show help for Boolean expression syntax"""
        help_text = """
Boolean Expression Syntax Help

Operators:
  +  OR  (A + B means A OR B)
  *  AND (A * B means A AND B)  
  ~  NOT (~A means NOT A)
  @  XOR (A @ B means A XOR B)

Precedence (highest to lowest):
  1. ~ (NOT)
  2. * (AND)
  3. @ (XOR)
  4. + (OR)

Parentheses can be used to override precedence.

Examples:
  OUTPUT = A + B          (A OR B)
  OUTPUT = A * B          (A AND B)
  OUTPUT = ~A             (NOT A)
  OUTPUT = A @ B          (A XOR B)
  OUTPUT = ~(A + B)       (NOT(A OR B))
  OUTPUT = A * B + C      ((A AND B) OR C)
  OUTPUT = (A + B) * C    ((A OR B) AND C)
  OUTPUT = ~((A + B) * C) (NOT((A OR B) AND C))

Variables:
  Use single letters A-Z for input variables.
  The tool will automatically create input gates for all variables used.

Tips:
  - The expression will be automatically parsed and optimized
  - A circuit diagram will be generated showing the logic structure
  - You can simulate the circuit to verify the logic
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Boolean Expression Syntax Help")
        help_window.geometry("600x500")
        
        text_widget = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = tk.Scrollbar(help_window, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        tk.Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)

    def zoom_to_fit(self):
        """Zoom to fit all circuit elements"""
        self.canvas.zoom_to_fit()
        self.update_zoom_display()
    
    def pan_up(self):
        """Pan canvas up"""
        self.canvas.pan_offset.y += 50
        self.canvas.draw_circuit()
    
    def pan_down(self):
        """Pan canvas down"""
        self.canvas.pan_offset.y -= 50
        self.canvas.draw_circuit()
    
    def pan_left(self):
        """Pan canvas left"""
        self.canvas.pan_offset.x += 50
        self.canvas.draw_circuit()
    
    def pan_right(self):
        """Pan canvas right"""
        self.canvas.pan_offset.x -= 50
        self.canvas.draw_circuit()
    
    def pan_center(self):
        """Center the canvas view"""
        self.canvas.pan_offset = Point(0, 0)
        self.canvas.draw_circuit()
        self.update_status("View centered")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Digital Circuit Designer".center(60))
    print("Interactive Logic Circuit Design & Simulation".center(60))
    print("=" * 60)
    print()
    print("🎯 FEATURES:")
    print("   📝 Boolean Expression to Circuit:")
    print("      • Click green '📝 Expression' button or press Ctrl+E")
    print("      • Example: OUTPUT = ~((A+B)*C)")
    print()
    print("   🔍 Zoom & Navigation:")
    print("      • Mouse wheel: Zoom in/out")
    print("      • Toolbar buttons: 🔍+ 🔍- 1:1 ⤢")
    print("      • Pan buttons: ↑ ← ⌂ → ↓")
    print("      • Space+Drag: Pan around like Canva")
    print("      • Middle mouse: Pan around")
    print("      • Keyboard: Ctrl+/- (zoom), Ctrl+0 (reset), Ctrl+F (fit)")
    print()
    print("   ⚡ Simulation:")
    print("      • Real-time signal display (red=1, black=0)")
    print("      • Drag gates, click inputs to toggle")
    print()
    print("Starting application...")
    print("=" * 60)
    
    app = DigitalCircuitDesigner()
    app.run()

if __name__ == "__main__":
    main()