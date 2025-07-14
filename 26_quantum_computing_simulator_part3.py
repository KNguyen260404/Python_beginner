#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Computing Simulator - Part 3
-----------------------------------
Implementation of quantum error correction and visualization tools
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Dict, Tuple, Union, Optional, Any
import time
from enum import Enum

# Constants
SQRT2 = np.sqrt(2)
SQRT2_INV = 1 / SQRT2
PI = np.pi
I_UNIT = 1j  # Imaginary unit

class QuantumErrorType(Enum):
    """Types of quantum errors"""
    BIT_FLIP = 1    # X error
    PHASE_FLIP = 2  # Z error
    BIT_PHASE_FLIP = 3  # Y error
    DEPOLARIZING = 4  # Random X, Y, Z errors
    AMPLITUDE_DAMPING = 5  # Energy dissipation
    PHASE_DAMPING = 6  # Decoherence without energy loss

class QuantumErrorCorrection:
    """Implementation of quantum error correction codes"""
    
    @staticmethod
    def encode_bit_flip_code(simulator, logical_qubit: int, ancilla_qubits: List[int]):
        """Encode a qubit using the 3-qubit bit flip code
        
        Args:
            simulator: Quantum simulator
            logical_qubit: Index of the logical qubit to encode
            ancilla_qubits: Indices of two ancilla qubits
        """
        if len(ancilla_qubits) != 2:
            raise ValueError("Bit flip code requires exactly 2 ancilla qubits")
        
        # Apply CNOT from logical qubit to both ancilla qubits
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[1]], [logical_qubit])
    
    @staticmethod
    def decode_bit_flip_code(simulator, logical_qubit: int, ancilla_qubits: List[int]):
        """Decode and correct a qubit encoded with the 3-qubit bit flip code
        
        Args:
            simulator: Quantum simulator
            logical_qubit: Index of the logical qubit
            ancilla_qubits: Indices of two ancilla qubits
        """
        if len(ancilla_qubits) != 2:
            raise ValueError("Bit flip code requires exactly 2 ancilla qubits")
        
        # Create additional ancilla qubits for syndrome measurement
        syndrome_qubits = [3, 4]  # Assuming these are available
        
        # Measure syndrome
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        # First syndrome qubit checks qubits 0 and 1
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[0]], [ancilla_qubits[0]])
        
        # Second syndrome qubit checks qubits 0 and 2
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[1]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[1]], [ancilla_qubits[1]])
        
        # Measure syndrome qubits
        syndrome_0 = simulator.measure(syndrome_qubits[0])
        syndrome_1 = simulator.measure(syndrome_qubits[1])
        
        # Apply correction based on syndrome
        x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
        
        if syndrome_0 == 1 and syndrome_1 == 1:
            # Error on qubit 0
            simulator.apply_gate(x_gate, [logical_qubit])
        elif syndrome_0 == 1 and syndrome_1 == 0:
            # Error on qubit 1
            simulator.apply_gate(x_gate, [ancilla_qubits[0]])
        elif syndrome_0 == 0 and syndrome_1 == 1:
            # Error on qubit 2
            simulator.apply_gate(x_gate, [ancilla_qubits[1]])
        
        # Decode by applying CNOTs again
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[1]], [logical_qubit])
    
    @staticmethod
    def encode_phase_flip_code(simulator, logical_qubit: int, ancilla_qubits: List[int]):
        """Encode a qubit using the 3-qubit phase flip code
        
        Args:
            simulator: Quantum simulator
            logical_qubit: Index of the logical qubit to encode
            ancilla_qubits: Indices of two ancilla qubits
        """
        if len(ancilla_qubits) != 2:
            raise ValueError("Phase flip code requires exactly 2 ancilla qubits")
        
        # Apply Hadamard to all qubits
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        simulator.apply_gate(h_gate, [logical_qubit])
        simulator.apply_gate(h_gate, [ancilla_qubits[0]])
        simulator.apply_gate(h_gate, [ancilla_qubits[1]])
        
        # Apply CNOT from logical qubit to both ancilla qubits
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[1]], [logical_qubit])
        
        # Apply Hadamard to all qubits again
        simulator.apply_gate(h_gate, [logical_qubit])
        simulator.apply_gate(h_gate, [ancilla_qubits[0]])
        simulator.apply_gate(h_gate, [ancilla_qubits[1]])
    
    @staticmethod
    def decode_phase_flip_code(simulator, logical_qubit: int, ancilla_qubits: List[int]):
        """Decode and correct a qubit encoded with the 3-qubit phase flip code
        
        Args:
            simulator: Quantum simulator
            logical_qubit: Index of the logical qubit
            ancilla_qubits: Indices of two ancilla qubits
        """
        if len(ancilla_qubits) != 2:
            raise ValueError("Phase flip code requires exactly 2 ancilla qubits")
        
        # Apply Hadamard to all qubits
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        simulator.apply_gate(h_gate, [logical_qubit])
        simulator.apply_gate(h_gate, [ancilla_qubits[0]])
        simulator.apply_gate(h_gate, [ancilla_qubits[1]])
        
        # Create additional ancilla qubits for syndrome measurement
        syndrome_qubits = [3, 4]  # Assuming these are available
        
        # Measure syndrome
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        # First syndrome qubit checks qubits 0 and 1
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[0]], [ancilla_qubits[0]])
        
        # Second syndrome qubit checks qubits 0 and 2
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[1]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [syndrome_qubits[1]], [ancilla_qubits[1]])
        
        # Measure syndrome qubits
        syndrome_0 = simulator.measure(syndrome_qubits[0])
        syndrome_1 = simulator.measure(syndrome_qubits[1])
        
        # Apply correction based on syndrome
        z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
        
        if syndrome_0 == 1 and syndrome_1 == 1:
            # Error on qubit 0
            simulator.apply_gate(z_gate, [logical_qubit])
        elif syndrome_0 == 1 and syndrome_1 == 0:
            # Error on qubit 1
            simulator.apply_gate(z_gate, [ancilla_qubits[0]])
        elif syndrome_0 == 0 and syndrome_1 == 1:
            # Error on qubit 2
            simulator.apply_gate(z_gate, [ancilla_qubits[1]])
        
        # Apply Hadamard to all qubits again
        simulator.apply_gate(h_gate, [logical_qubit])
        simulator.apply_gate(h_gate, [ancilla_qubits[0]])
        simulator.apply_gate(h_gate, [ancilla_qubits[1]])
        
        # Decode by applying CNOTs
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[0]], [logical_qubit])
        simulator.apply_gate(cnot_matrix, [ancilla_qubits[1]], [logical_qubit])
    
    @staticmethod
    def encode_shor_code(simulator, logical_qubit: int, ancilla_qubits: List[int]):
        """Encode a qubit using Shor's 9-qubit code
        
        Args:
            simulator: Quantum simulator
            logical_qubit: Index of the logical qubit to encode
            ancilla_qubits: Indices of eight ancilla qubits
        """
        if len(ancilla_qubits) != 8:
            raise ValueError("Shor code requires exactly 8 ancilla qubits")
        
        # Group qubits into blocks of 3
        blocks = [
            [logical_qubit, ancilla_qubits[0], ancilla_qubits[1]],
            [ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]],
            [ancilla_qubits[5], ancilla_qubits[6], ancilla_qubits[7]]
        ]
        
        # First, create |+⟩ state for each block's first qubit
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        simulator.apply_gate(h_gate, [blocks[0][0]])  # logical qubit
        simulator.apply_gate(h_gate, [blocks[1][0]])
        simulator.apply_gate(h_gate, [blocks[2][0]])
        
        # Apply CNOT within each block for phase error protection
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        
        for block in blocks:
            simulator.apply_gate(cnot_matrix, [block[1]], [block[0]])
            simulator.apply_gate(cnot_matrix, [block[2]], [block[0]])
        
        # Apply Hadamard to all qubits for bit flip protection
        for block in blocks:
            for qubit in block:
                simulator.apply_gate(h_gate, [qubit])
        
        # Apply CNOT between blocks for bit flip protection
        simulator.apply_gate(cnot_matrix, [blocks[1][0]], [blocks[0][0]])
        simulator.apply_gate(cnot_matrix, [blocks[1][1]], [blocks[0][1]])
        simulator.apply_gate(cnot_matrix, [blocks[1][2]], [blocks[0][2]])
        
        simulator.apply_gate(cnot_matrix, [blocks[2][0]], [blocks[0][0]])
        simulator.apply_gate(cnot_matrix, [blocks[2][1]], [blocks[0][1]])
        simulator.apply_gate(cnot_matrix, [blocks[2][2]], [blocks[0][2]])
    
    @staticmethod
    def apply_quantum_error(simulator, qubit: int, error_type: QuantumErrorType, error_prob: float = 0.1):
        """Apply a quantum error to a qubit
        
        Args:
            simulator: Quantum simulator
            qubit: Index of the qubit
            error_type: Type of error to apply
            error_prob: Probability of error occurring
        """
        # Only apply error with probability error_prob
        if np.random.random() > error_prob:
            return
        
        if error_type == QuantumErrorType.BIT_FLIP:
            # Apply X gate (bit flip)
            x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
            simulator.apply_gate(x_gate, [qubit])
        
        elif error_type == QuantumErrorType.PHASE_FLIP:
            # Apply Z gate (phase flip)
            z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
            simulator.apply_gate(z_gate, [qubit])
        
        elif error_type == QuantumErrorType.BIT_PHASE_FLIP:
            # Apply Y gate (bit and phase flip)
            y_gate = np.array([[0, -I_UNIT], [I_UNIT, 0]], dtype=complex)
            simulator.apply_gate(y_gate, [qubit])
        
        elif error_type == QuantumErrorType.DEPOLARIZING:
            # Apply random X, Y, or Z gate
            error_choice = np.random.choice(['X', 'Y', 'Z'])
            if error_choice == 'X':
                x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
                simulator.apply_gate(x_gate, [qubit])
            elif error_choice == 'Y':
                y_gate = np.array([[0, -I_UNIT], [I_UNIT, 0]], dtype=complex)
                simulator.apply_gate(y_gate, [qubit])
            else:  # Z
                z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
                simulator.apply_gate(z_gate, [qubit])
        
        elif error_type == QuantumErrorType.AMPLITUDE_DAMPING:
            # Apply amplitude damping channel
            # This is a simplified implementation
            # In a real quantum system, this would be a non-unitary operation
            # Here we'll approximate it with a probabilistic bit flip
            if np.random.random() < error_prob:
                # Get the state vector
                state = simulator.get_statevector()
                
                # Calculate probability of |1⟩ state for this qubit
                mask = 1 << qubit
                prob_one = sum(np.abs(state[i])**2 for i in range(len(state)) if (i & mask) != 0)
                
                # Apply probabilistic bit flip from |1⟩ to |0⟩
                if np.random.random() < prob_one:
                    # Project to |1⟩ and then apply bit flip
                    x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
                    simulator.apply_gate(x_gate, [qubit])
        
        elif error_type == QuantumErrorType.PHASE_DAMPING:
            # Apply phase damping channel
            # This is a simplified implementation
            # In a real quantum system, this would be a non-unitary operation
            # Here we'll approximate it with a probabilistic phase flip
            if np.random.random() < error_prob:
                z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
                simulator.apply_gate(z_gate, [qubit])

class QuantumVisualization:
    """Tools for visualizing quantum states and circuits"""
    
    @staticmethod
    def plot_statevector(statevector: np.ndarray, num_qubits: int, title: str = "Quantum State Vector"):
        """Plot the amplitudes of a quantum state vector
        
        Args:
            statevector: Quantum state vector
            num_qubits: Number of qubits
            title: Plot title
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Calculate probabilities
        probabilities = np.abs(statevector) ** 2
        
        # Create labels for basis states
        labels = [format(i, f'0{num_qubits}b') for i in range(len(statevector))]
        
        # Plot probabilities
        ax1.bar(labels, probabilities)
        ax1.set_xlabel('Basis State')
        ax1.set_ylabel('Probability')
        ax1.set_title('State Probabilities')
        ax1.tick_params(axis='x', rotation=70)
        
        # Plot real and imaginary parts
        x = np.arange(len(statevector))
        width = 0.35
        ax2.bar(x - width/2, np.real(statevector), width, label='Real')
        ax2.bar(x + width/2, np.imag(statevector), width, label='Imaginary')
        ax2.set_xlabel('Basis State')
        ax2.set_ylabel('Amplitude')
        ax2.set_title('State Amplitudes')
        ax2.set_xticks(x)
        ax2.set_xticklabels(labels, rotation=70)
        ax2.legend()
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_bloch_sphere(qubit_state: np.ndarray, title: str = "Bloch Sphere Representation"):
        """Plot a single-qubit state on the Bloch sphere
        
        Args:
            qubit_state: Single-qubit state vector [alpha, beta]
            title: Plot title
        """
        # Check if this is a valid single-qubit state
        if len(qubit_state) != 2:
            raise ValueError("Expected a single-qubit state vector of length 2")
        
        # Normalize the state
        norm = np.sqrt(np.abs(qubit_state[0])**2 + np.abs(qubit_state[1])**2)
        qubit_state = qubit_state / norm
        
        # Extract Bloch sphere coordinates
        # |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
        alpha = qubit_state[0]
        beta = qubit_state[1]
        
        # Handle special case where alpha is close to zero
        if np.abs(alpha) < 1e-10:
            theta = np.pi
        else:
            theta = 2 * np.arccos(np.abs(alpha))
        
        # Calculate phi
        if np.abs(beta) < 1e-10:
            phi = 0
        else:
            phi = np.angle(beta / alpha) if np.abs(alpha) > 1e-10 else np.angle(beta)
        
        # Convert to Cartesian coordinates
        x = np.sin(theta) * np.cos(phi)
        y = np.sin(theta) * np.sin(phi)
        z = np.cos(theta)
        
        # Create figure
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw Bloch sphere
        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        sphere_x = np.cos(u) * np.sin(v)
        sphere_y = np.sin(u) * np.sin(v)
        sphere_z = np.cos(v)
        ax.plot_wireframe(sphere_x, sphere_y, sphere_z, color='gray', alpha=0.2)
        
        # Draw axes
        ax.quiver(0, 0, 0, 1, 0, 0, color='r', arrow_length_ratio=0.1, label='X')
        ax.quiver(0, 0, 0, 0, 1, 0, color='g', arrow_length_ratio=0.1, label='Y')
        ax.quiver(0, 0, 0, 0, 0, 1, color='b', arrow_length_ratio=0.1, label='Z')
        
        # Draw state vector
        ax.quiver(0, 0, 0, x, y, z, color='purple', arrow_length_ratio=0.1, label='State')
        
        # Set labels and limits
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim([-1.2, 1.2])
        ax.set_ylim([-1.2, 1.2])
        ax.set_zlim([-1.2, 1.2])
        ax.set_title(title)
        ax.legend()
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_density_matrix(density_matrix: np.ndarray, num_qubits: int, title: str = "Density Matrix"):
        """Plot the density matrix of a quantum state
        
        Args:
            density_matrix: Density matrix
            num_qubits: Number of qubits
            title: Plot title
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
        
        # Create a custom colormap
        cmap = LinearSegmentedColormap.from_list(
            'complex', 
            [(0, 'blue'), (0.5, 'white'), (1, 'red')]
        )
        
        # Plot real part
        im1 = ax1.imshow(np.real(density_matrix), cmap=cmap)
        ax1.set_title('Real Part')
        plt.colorbar(im1, ax=ax1)
        
        # Plot imaginary part
        im2 = ax2.imshow(np.imag(density_matrix), cmap=cmap)
        ax2.set_title('Imaginary Part')
        plt.colorbar(im2, ax=ax2)
        
        # Create labels for basis states
        labels = [format(i, f'0{num_qubits}b') for i in range(2**num_qubits)]
        
        # Set ticks and labels
        for ax in [ax1, ax2]:
            ax.set_xticks(np.arange(len(labels)))
            ax.set_yticks(np.arange(len(labels)))
            ax.set_xticklabels(labels)
            ax.set_yticklabels(labels)
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def animate_quantum_evolution(simulator, circuit, num_steps: int = 10, interval: int = 200):
        """Animate the evolution of a quantum state as gates are applied
        
        Args:
            simulator: Quantum simulator
            circuit: Quantum circuit
            num_steps: Number of animation steps
            interval: Time interval between frames (ms)
        """
        # Reset simulator
        simulator.reset()
        
        # Divide gates into steps
        gates_per_step = max(1, len(circuit.gates) // num_steps)
        gate_groups = [circuit.gates[i:i+gates_per_step] for i in range(0, len(circuit.gates), gates_per_step)]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Create labels for basis states
        labels = [format(i, f'0{simulator.num_qubits}b') for i in range(simulator.dim)]
        
        # Initialize bar plot
        probabilities = np.abs(simulator.state_vector) ** 2
        bars = ax.bar(labels, probabilities)
        
        # Set labels and title
        ax.set_xlabel('Basis State')
        ax.set_ylabel('Probability')
        ax.set_title('Quantum State Evolution')
        ax.tick_params(axis='x', rotation=70)
        
        # Animation function
        def animate(i):
            if i < len(gate_groups):
                # Apply gates for this step
                for gate in gate_groups[i]:
                    simulator.apply_gate(gate.matrix, gate.target_qubits, gate.control_qubits)
                
                # Update probabilities
                probabilities = np.abs(simulator.state_vector) ** 2
                for bar, prob in zip(bars, probabilities):
                    bar.set_height(prob)
                
                ax.set_title(f'Quantum State Evolution - Step {i+1}/{len(gate_groups)}')
            
            return bars
        
        # Create animation
        anim = animation.FuncAnimation(
            fig, animate, frames=len(gate_groups) + 1, interval=interval, blit=True
        )
        
        plt.tight_layout()
        plt.show()
        
        return anim 