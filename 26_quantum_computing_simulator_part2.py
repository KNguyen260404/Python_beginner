#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Computing Simulator - Part 2
-----------------------------------
Implementation of the quantum state simulator and algorithms
"""

import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Union, Optional, Callable, Any
import time
import random
from enum import Enum, auto
from dataclasses import dataclass, field

# Constants
SQRT2 = np.sqrt(2)
SQRT2_INV = 1 / SQRT2
PI = np.pi
I_UNIT = 1j  # Imaginary unit

class QuantumSimulator:
    """Core quantum state simulator"""
    
    def __init__(self, num_qubits: int, backend: str = "numpy"):
        """Initialize the quantum simulator
        
        Args:
            num_qubits: Number of qubits to simulate
            backend: Simulation backend to use
        """
        self.num_qubits = num_qubits
        self.backend = backend
        
        # Initialize state vector to |0...0⟩
        self.dim = 2 ** num_qubits
        self.state_vector = np.zeros(self.dim, dtype=complex)
        self.state_vector[0] = 1.0
        
        # For tracking measurements
        self.measured_qubits = set()
        self.measurement_results = {}
    
    def reset(self):
        """Reset the quantum state to |0...0⟩"""
        self.state_vector = np.zeros(self.dim, dtype=complex)
        self.state_vector[0] = 1.0
        self.measured_qubits = set()
        self.measurement_results = {}
    
    def get_statevector(self) -> np.ndarray:
        """Get the current state vector
        
        Returns:
            Current quantum state vector
        """
        return self.state_vector.copy()
    
    def get_density_matrix(self) -> np.ndarray:
        """Get the density matrix representation of the current state
        
        Returns:
            Density matrix
        """
        state = self.state_vector.reshape(-1, 1)
        return np.dot(state, state.conj().T)
    
    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities for all basis states
        
        Returns:
            Array of probabilities
        """
        return np.abs(self.state_vector) ** 2
    
    def apply_gate(self, gate_matrix: np.ndarray, target_qubits: List[int], control_qubits: List[int] = None):
        """Apply a quantum gate to the state vector
        
        Args:
            gate_matrix: Matrix representation of the gate
            target_qubits: List of target qubit indices
            control_qubits: List of control qubit indices (optional)
        """
        if control_qubits is None:
            control_qubits = []
        
        # Check if any target qubits have been measured
        if any(q in self.measured_qubits for q in target_qubits):
            raise ValueError("Cannot apply gate to already measured qubits")
        
        # For single-qubit gates without controls, use optimized implementation
        if len(target_qubits) == 1 and not control_qubits:
            self._apply_single_qubit_gate(gate_matrix, target_qubits[0])
        else:
            # For multi-qubit gates or controlled gates, construct the full matrix
            full_matrix = self._construct_full_gate_matrix(gate_matrix, target_qubits, control_qubits)
            self.state_vector = np.dot(full_matrix, self.state_vector)
    
    def _apply_single_qubit_gate(self, gate_matrix: np.ndarray, target_qubit: int):
        """Apply a single-qubit gate efficiently
        
        Args:
            gate_matrix: 2x2 gate matrix
            target_qubit: Target qubit index
        """
        # Reshape state vector to isolate the target qubit
        n = self.num_qubits
        target = n - 1 - target_qubit  # Reverse bit order convention
        
        # Reshape state vector to separate the target qubit
        new_shape = [2] * n
        self.state_vector = self.state_vector.reshape(new_shape)
        
        # Apply gate using np.tensordot for efficiency
        indices = list(range(n))
        gate_index = indices.pop(target)
        self.state_vector = np.tensordot(gate_matrix, self.state_vector, axes=([1], [gate_index]))
        
        # Transpose to restore original qubit order
        transpose_indices = indices[:target] + [n-1] + indices[target:]
        self.state_vector = self.state_vector.transpose(transpose_indices)
        
        # Reshape back to vector
        self.state_vector = self.state_vector.reshape(-1)
    
    def _construct_full_gate_matrix(self, gate_matrix: np.ndarray, target_qubits: List[int], control_qubits: List[int]) -> np.ndarray:
        """Construct the full gate matrix for the entire system
        
        Args:
            gate_matrix: Matrix for target qubits
            target_qubits: List of target qubit indices
            control_qubits: List of control qubit indices
            
        Returns:
            Full system gate matrix
        """
        n = self.num_qubits
        
        # Sort qubits to simplify tensor product construction
        all_qubits = sorted(target_qubits + control_qubits)
        
        # For controlled gates
        if control_qubits:
            # Construct projection operators for control qubits
            P0 = np.array([[1, 0], [0, 0]])
            P1 = np.array([[0, 0], [0, 1]])
            
            # Identity matrix for when control condition is not met
            I = np.eye(2 ** len(target_qubits), dtype=complex)
            
            # Initialize the full matrix
            full_matrix = np.zeros((self.dim, self.dim), dtype=complex)
            
            # Loop through all possible control qubit states
            for i in range(2 ** len(control_qubits)):
                # Convert i to binary representation
                control_state = [(i >> j) & 1 for j in range(len(control_qubits))]
                
                # Determine if this control state activates the gate
                activate = all(control_state)
                
                # Construct the matrix for this control configuration
                matrices = []
                for q in range(n):
                    if q in control_qubits:
                        # Use P1 for control qubits that should be 1
                        idx = control_qubits.index(q)
                        matrices.append(P1 if control_state[idx] else P0)
                    elif q in target_qubits:
                        # For target qubits, use identity or the gate matrix
                        if activate:
                            # Need to map the target qubit to the correct position in gate_matrix
                            # This gets complex for multi-qubit gates
                            if len(target_qubits) == 1:
                                matrices.append(gate_matrix)
                            else:
                                # For multi-qubit gates, we need to handle them specially
                                # This is a simplification; actual implementation would be more complex
                                pass
                        else:
                            matrices.append(np.eye(2, dtype=complex))
                    else:
                        # Identity for uninvolved qubits
                        matrices.append(np.eye(2, dtype=complex))
                
                # Compute tensor product of all matrices
                config_matrix = matrices[0]
                for mat in matrices[1:]:
                    config_matrix = np.kron(config_matrix, mat)
                
                # Add to the full matrix
                full_matrix += config_matrix
            
            return full_matrix
        
        else:
            # No control qubits, just apply the gate to target qubits
            # Construct the full matrix using tensor products
            matrices = []
            for q in range(n):
                if q in target_qubits:
                    # Map the target qubit to the correct position in gate_matrix
                    # This is a simplification; actual implementation would handle multi-qubit gates
                    matrices.append(gate_matrix if len(target_qubits) == 1 else np.eye(2, dtype=complex))
                else:
                    matrices.append(np.eye(2, dtype=complex))
            
            # Compute tensor product of all matrices
            full_matrix = matrices[0]
            for mat in matrices[1:]:
                full_matrix = np.kron(full_matrix, mat)
            
            return full_matrix
    
    def measure(self, qubit: int) -> int:
        """Measure a single qubit in the computational basis
        
        Args:
            qubit: Index of the qubit to measure
            
        Returns:
            Measurement result (0 or 1)
        """
        if qubit in self.measured_qubits:
            # Return previously measured value
            return self.measurement_results[qubit]
        
        # Calculate probabilities for the qubit being 0 or 1
        probabilities = self.get_probabilities()
        
        # Calculate probability of measuring 1
        mask = 1 << qubit
        prob_one = sum(probabilities[i] for i in range(self.dim) if (i & mask) != 0)
        
        # Generate random outcome based on probability
        outcome = 1 if random.random() < prob_one else 0
        
        # Update state vector based on measurement outcome
        new_state = np.zeros(self.dim, dtype=complex)
        norm = 0.0
        
        for i in range(self.dim):
            # Check if this basis state is consistent with the measurement
            if ((i & mask) >> qubit) == outcome:
                new_state[i] = self.state_vector[i]
                norm += abs(self.state_vector[i]) ** 2
        
        # Normalize the new state
        self.state_vector = new_state / np.sqrt(norm)
        
        # Record the measurement
        self.measured_qubits.add(qubit)
        self.measurement_results[qubit] = outcome
        
        return outcome
    
    def measure_all(self) -> List[int]:
        """Measure all qubits in the computational basis
        
        Returns:
            List of measurement outcomes
        """
        results = []
        for q in range(self.num_qubits):
            results.append(self.measure(q))
        return results
    
    def run_circuit(self, circuit) -> Dict[str, Any]:
        """Run a quantum circuit
        
        Args:
            circuit: QuantumCircuit to execute
            
        Returns:
            Dictionary with execution results
        """
        # Reset the simulator state
        self.reset()
        
        # Apply all gates in the circuit
        for gate in circuit.gates:
            gate_matrix = gate.matrix
            self.apply_gate(gate_matrix, gate.target_qubits, gate.control_qubits)
        
        # Perform all measurements
        results = {}
        for meas in circuit.measurements:
            qubit = meas["qubit"]
            cbit = meas["cbit"]
            basis = meas["basis"]
            
            # Apply basis change if needed
            if basis == "X_BASIS":
                # Apply Hadamard before measurement
                h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
                self.apply_gate(h_gate, [qubit])
            elif basis == "Y_BASIS":
                # Apply rotation before measurement
                s_dag = np.array([[1, 0], [0, -I_UNIT]], dtype=complex)
                h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
                self.apply_gate(s_dag, [qubit])
                self.apply_gate(h_gate, [qubit])
            
            # Perform the measurement
            outcome = self.measure(qubit)
            results[cbit] = outcome
        
        return {
            "results": results,
            "statevector": self.get_statevector(),
            "probabilities": self.get_probabilities()
        }

class QuantumAlgorithms:
    """Implementation of quantum algorithms"""
    
    @staticmethod
    def create_bell_state(simulator: QuantumSimulator, q1: int, q2: int):
        """Create a Bell state (maximally entangled state) between two qubits
        
        Args:
            simulator: Quantum simulator
            q1: First qubit index
            q2: Second qubit index
        """
        # Apply Hadamard to first qubit
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        simulator.apply_gate(h_gate, [q1])
        
        # Apply CNOT with first qubit as control and second as target
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        simulator.apply_gate(cnot_matrix, [q2], [q1])
    
    @staticmethod
    def quantum_teleportation(simulator: QuantumSimulator, state_qubit: int, sender_qubit: int, receiver_qubit: int):
        """Implement quantum teleportation protocol
        
        Args:
            simulator: Quantum simulator
            state_qubit: Qubit with state to teleport
            sender_qubit: Sender's entangled qubit
            receiver_qubit: Receiver's entangled qubit
        """
        # Create Bell state between sender and receiver qubits
        QuantumAlgorithms.create_bell_state(simulator, sender_qubit, receiver_qubit)
        
        # Apply CNOT between state qubit and sender qubit
        cnot_matrix = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
        simulator.apply_gate(cnot_matrix, [sender_qubit], [state_qubit])
        
        # Apply Hadamard to state qubit
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        simulator.apply_gate(h_gate, [state_qubit])
        
        # Measure state and sender qubits
        m1 = simulator.measure(state_qubit)
        m2 = simulator.measure(sender_qubit)
        
        # Apply corrections to receiver qubit based on measurements
        if m2 == 1:
            # Apply X gate
            x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
            simulator.apply_gate(x_gate, [receiver_qubit])
        
        if m1 == 1:
            # Apply Z gate
            z_gate = np.array([[1, 0], [0, -1]], dtype=complex)
            simulator.apply_gate(z_gate, [receiver_qubit])
    
    @staticmethod
    def deutsch_jozsa(simulator: QuantumSimulator, oracle_function, n_qubits: int):
        """Implement Deutsch-Jozsa algorithm
        
        Args:
            simulator: Quantum simulator
            oracle_function: Function implementing the oracle
            n_qubits: Number of qubits (excluding ancilla)
            
        Returns:
            True if function is constant, False if balanced
        """
        # Reset simulator
        simulator.reset()
        
        # Apply Hadamard to all qubits
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        for i in range(n_qubits + 1):  # +1 for ancilla
            simulator.apply_gate(h_gate, [i])
        
        # Apply X to ancilla qubit (last qubit)
        x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
        simulator.apply_gate(x_gate, [n_qubits])
        
        # Apply oracle
        oracle_matrix = oracle_function(n_qubits)
        simulator.apply_gate(oracle_matrix, list(range(n_qubits + 1)))
        
        # Apply Hadamard to all qubits except ancilla
        for i in range(n_qubits):
            simulator.apply_gate(h_gate, [i])
        
        # Measure all qubits except ancilla
        all_zeros = True
        for i in range(n_qubits):
            if simulator.measure(i) == 1:
                all_zeros = False
                break
        
        # If all measurements are 0, function is constant
        return all_zeros
    
    @staticmethod
    def grover_search(simulator: QuantumSimulator, oracle_function, n_qubits: int, iterations: int = None):
        """Implement Grover's search algorithm
        
        Args:
            simulator: Quantum simulator
            oracle_function: Function implementing the oracle
            n_qubits: Number of qubits
            iterations: Number of Grover iterations (if None, use optimal)
            
        Returns:
            Measured state after algorithm execution
        """
        # Reset simulator
        simulator.reset()
        
        # Calculate optimal number of iterations if not specified
        if iterations is None:
            iterations = int(np.pi/4 * np.sqrt(2**n_qubits))
        
        # Apply Hadamard to all qubits
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        for i in range(n_qubits):
            simulator.apply_gate(h_gate, [i])
        
        # Grover iterations
        for _ in range(iterations):
            # Apply oracle
            oracle_matrix = oracle_function(n_qubits)
            simulator.apply_gate(oracle_matrix, list(range(n_qubits)))
            
            # Apply diffusion operator
            # 1. Apply Hadamard to all qubits
            for i in range(n_qubits):
                simulator.apply_gate(h_gate, [i])
            
            # 2. Apply conditional phase shift (except |0...0⟩)
            # This is a simplification; actual implementation would be more complex
            phase_matrix = np.eye(2**n_qubits, dtype=complex)
            phase_matrix[0, 0] = -1  # Flip phase of |0...0⟩
            simulator.apply_gate(phase_matrix, list(range(n_qubits)))
            
            # 3. Apply Hadamard to all qubits again
            for i in range(n_qubits):
                simulator.apply_gate(h_gate, [i])
        
        # Measure all qubits
        return simulator.measure_all()
    
    @staticmethod
    def quantum_fourier_transform(simulator: QuantumSimulator, qubits: List[int]):
        """Apply Quantum Fourier Transform
        
        Args:
            simulator: Quantum simulator
            qubits: List of qubits to apply QFT to
        """
        n = len(qubits)
        
        # Apply QFT
        for i in range(n):
            # Apply Hadamard to current qubit
            h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
            simulator.apply_gate(h_gate, [qubits[i]])
            
            # Apply controlled phase rotations
            for j in range(i + 1, n):
                k = j - i
                phase = 2 * np.pi / (2 ** k)
                cp_matrix = np.array([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, np.exp(I_UNIT * phase)]
                ], dtype=complex)
                simulator.apply_gate(cp_matrix, [qubits[j]], [qubits[i]])
        
        # Swap qubits to match standard QFT output order
        for i in range(n // 2):
            swap_matrix = np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ], dtype=complex)
            simulator.apply_gate(swap_matrix, [qubits[i], qubits[n-i-1]])
    
    @staticmethod
    def inverse_quantum_fourier_transform(simulator: QuantumSimulator, qubits: List[int]):
        """Apply inverse Quantum Fourier Transform
        
        Args:
            simulator: Quantum simulator
            qubits: List of qubits to apply inverse QFT to
        """
        n = len(qubits)
        
        # Swap qubits to match standard QFT input order
        for i in range(n // 2):
            swap_matrix = np.array([
                [1, 0, 0, 0],
                [0, 0, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 1]
            ], dtype=complex)
            simulator.apply_gate(swap_matrix, [qubits[i], qubits[n-i-1]])
        
        # Apply inverse QFT
        for i in range(n - 1, -1, -1):
            # Apply controlled phase rotations (conjugate)
            for j in range(n - 1, i, -1):
                k = j - i
                phase = -2 * np.pi / (2 ** k)  # Negative phase for inverse
                cp_matrix = np.array([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 1, 0],
                    [0, 0, 0, np.exp(I_UNIT * phase)]
                ], dtype=complex)
                simulator.apply_gate(cp_matrix, [qubits[j]], [qubits[i]])
            
            # Apply Hadamard to current qubit
            h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
            simulator.apply_gate(h_gate, [qubits[i]])
    
    @staticmethod
    def phase_estimation(simulator: QuantumSimulator, unitary_gate: np.ndarray, target_qubit: int, precision_qubits: List[int]) -> float:
        """Implement Quantum Phase Estimation
        
        Args:
            simulator: Quantum simulator
            unitary_gate: Unitary operator whose eigenvalue phase we want to estimate
            target_qubit: Qubit prepared in the eigenstate
            precision_qubits: List of qubits used for precision
            
        Returns:
            Estimated phase
        """
        n = len(precision_qubits)
        
        # Apply Hadamard to all precision qubits
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        for i in range(n):
            simulator.apply_gate(h_gate, [precision_qubits[i]])
        
        # Apply controlled-U^(2^j) operations
        for j in range(n):
            # Calculate U^(2^j)
            power = 2 ** j
            u_power = np.linalg.matrix_power(unitary_gate, power)
            
            # Apply controlled version of U^(2^j)
            simulator.apply_gate(u_power, [target_qubit], [precision_qubits[j]])
        
        # Apply inverse QFT to precision qubits
        QuantumAlgorithms.inverse_quantum_fourier_transform(simulator, precision_qubits)
        
        # Measure precision qubits
        measurements = []
        for i in range(n):
            measurements.append(simulator.measure(precision_qubits[i]))
        
        # Convert binary measurements to phase estimate
        phase_int = 0
        for i, bit in enumerate(measurements):
            phase_int |= (bit << i)
        
        # Convert to phase in [0, 1)
        phase = phase_int / (2 ** n)
        
        return phase
    
    @staticmethod
    def shor_algorithm(simulator: QuantumSimulator, N: int, a: int = None) -> Optional[Tuple[int, int]]:
        """Implement Shor's factoring algorithm
        
        Args:
            simulator: Quantum simulator
            N: Number to factor
            a: Random number for the algorithm (if None, choose randomly)
            
        Returns:
            Tuple of factors if successful, None otherwise
        """
        # Check if N is even
        if N % 2 == 0:
            return (2, N // 2)
        
        # Check if N is a prime power
        for i in range(2, int(np.sqrt(N)) + 1):
            if N % i == 0:
                return (i, N // i)
        
        # Choose random a if not provided
        if a is None:
            a = random.randint(2, N - 1)
        
        # Calculate GCD(a, N)
        gcd = np.gcd(a, N)
        if gcd > 1:
            return (gcd, N // gcd)
        
        # Determine number of qubits needed
        n_count = 2 * int(np.ceil(np.log2(N)))
        n_target = int(np.ceil(np.log2(N)))
        
        # This is a simplified implementation of Shor's algorithm
        # In a real implementation, we would:
        # 1. Create a quantum circuit for period finding
        # 2. Use QFT to find the period r
        # 3. Use classical post-processing to find factors
        
        # For demonstration, we'll use a classical simulation of the period finding
        def find_period(a: int, N: int) -> int:
            """Find the period of a^x mod N"""
            x = 1
            for r in range(1, N):
                x = (x * a) % N
                if x == 1:
                    return r
            return 0
        
        r = find_period(a, N)
        
        # Check if r is even and a^(r/2) != -1 mod N
        if r % 2 == 0 and pow(a, r // 2, N) != N - 1:
            # Calculate potential factors
            factor1 = np.gcd(pow(a, r // 2) - 1, N)
            factor2 = np.gcd(pow(a, r // 2) + 1, N)
            
            # Check if we found non-trivial factors
            if factor1 > 1 and factor1 < N:
                return (factor1, N // factor1)
            elif factor2 > 1 and factor2 < N:
                return (factor2, N // factor2)
        
        # If we reach here, the algorithm failed
        return None 