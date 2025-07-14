#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Computing Simulator - Part 4
-----------------------------------
Implementation of quantum machine learning and the main application
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Union, Optional, Any, Callable
import time
import argparse
import json
import os
import sys
from tqdm import tqdm

# Constants
SQRT2 = np.sqrt(2)
SQRT2_INV = 1 / SQRT2
PI = np.pi
I_UNIT = 1j  # Imaginary unit

class QuantumML:
    """Implementation of quantum machine learning algorithms"""
    
    @staticmethod
    def quantum_kernel_estimation(simulator, data_points: List[np.ndarray], kernel_function: Callable):
        """Estimate a quantum kernel matrix for a set of data points
        
        Args:
            simulator: Quantum simulator
            data_points: List of data vectors
            kernel_function: Function to encode data into quantum circuit
            
        Returns:
            Kernel matrix
        """
        n_samples = len(data_points)
        kernel_matrix = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(i, n_samples):
                # Prepare circuit for kernel estimation
                simulator.reset()
                
                # Encode first data point
                kernel_function(simulator, data_points[i])
                
                # Apply inverse encoding of second data point
                kernel_function(simulator, data_points[j], inverse=True)
                
                # Measure probability of returning to |0...0⟩ state
                prob_zero = np.abs(simulator.state_vector[0]) ** 2
                
                # Store in kernel matrix (symmetric)
                kernel_matrix[i, j] = prob_zero
                kernel_matrix[j, i] = prob_zero
        
        return kernel_matrix
    
    @staticmethod
    def variational_quantum_classifier(simulator, data_point: np.ndarray, params: List[float], 
                                      encoding_function: Callable, variational_function: Callable):
        """Apply a variational quantum classifier to a data point
        
        Args:
            simulator: Quantum simulator
            data_point: Input data vector
            params: Variational circuit parameters
            encoding_function: Function to encode data into quantum circuit
            variational_function: Function to apply variational circuit
            
        Returns:
            Classification probability
        """
        # Reset simulator
        simulator.reset()
        
        # Encode data
        encoding_function(simulator, data_point)
        
        # Apply variational circuit
        variational_function(simulator, params)
        
        # Measure output qubit (assume it's the first qubit)
        simulator.measure(0)
        
        # Return probability of measuring |1⟩
        probabilities = np.abs(simulator.state_vector) ** 2
        prob_one = sum(probabilities[i] for i in range(len(probabilities)) if (i & 1) != 0)
        
        return prob_one
    
    @staticmethod
    def quantum_neural_network(simulator, data_point: np.ndarray, weights: List[List[float]],
                              n_qubits: int, n_layers: int):
        """Apply a quantum neural network to a data point
        
        Args:
            simulator: Quantum simulator
            data_point: Input data vector
            weights: Network weights for each layer
            n_qubits: Number of qubits
            n_layers: Number of network layers
            
        Returns:
            Output state after network application
        """
        # Reset simulator
        simulator.reset()
        
        # Normalize data if needed
        if np.linalg.norm(data_point) > 1.0:
            data_point = data_point / np.linalg.norm(data_point)
        
        # Encode data as rotation angles
        for i, x in enumerate(data_point):
            if i < n_qubits:
                # Apply RY rotation based on data
                ry_matrix = np.array([
                    [np.cos(x * PI / 2), -np.sin(x * PI / 2)],
                    [np.sin(x * PI / 2), np.cos(x * PI / 2)]
                ], dtype=complex)
                simulator.apply_gate(ry_matrix, [i])
        
        # Apply network layers
        for layer in range(n_layers):
            # Apply single-qubit rotations
            for qubit in range(n_qubits):
                # RY rotation
                ry_matrix = np.array([
                    [np.cos(weights[layer][qubit*3] / 2), -np.sin(weights[layer][qubit*3] / 2)],
                    [np.sin(weights[layer][qubit*3] / 2), np.cos(weights[layer][qubit*3] / 2)]
                ], dtype=complex)
                simulator.apply_gate(ry_matrix, [qubit])
                
                # RZ rotation
                rz_matrix = np.array([
                    [np.exp(-I_UNIT * weights[layer][qubit*3+1] / 2), 0],
                    [0, np.exp(I_UNIT * weights[layer][qubit*3+1] / 2)]
                ], dtype=complex)
                simulator.apply_gate(rz_matrix, [qubit])
                
                # RY rotation
                ry_matrix = np.array([
                    [np.cos(weights[layer][qubit*3+2] / 2), -np.sin(weights[layer][qubit*3+2] / 2)],
                    [np.sin(weights[layer][qubit*3+2] / 2), np.cos(weights[layer][qubit*3+2] / 2)]
                ], dtype=complex)
                simulator.apply_gate(ry_matrix, [qubit])
            
            # Apply entangling gates
            for q in range(n_qubits - 1):
                cnot_matrix = np.array([
                    [1, 0, 0, 0],
                    [0, 1, 0, 0],
                    [0, 0, 0, 1],
                    [0, 0, 1, 0]
                ], dtype=complex)
                simulator.apply_gate(cnot_matrix, [q+1], [q])
        
        return simulator.state_vector
    
    @staticmethod
    def quantum_support_vector_machine(simulator, training_data: List[Tuple[np.ndarray, int]], 
                                      test_point: np.ndarray, encoding_function: Callable):
        """Implement a quantum support vector machine
        
        Args:
            simulator: Quantum simulator
            training_data: List of (data_point, label) tuples
            test_point: Data point to classify
            encoding_function: Function to encode data into quantum circuit
            
        Returns:
            Predicted class
        """
        # Calculate kernel matrix for training data
        n_samples = len(training_data)
        kernel_matrix = np.zeros((n_samples, n_samples))
        
        for i in range(n_samples):
            for j in range(i, n_samples):
                # Prepare circuit for kernel estimation
                simulator.reset()
                
                # Encode first data point
                encoding_function(simulator, training_data[i][0])
                
                # Apply inverse encoding of second data point
                encoding_function(simulator, training_data[j][0], inverse=True)
                
                # Measure probability of returning to |0...0⟩ state
                prob_zero = np.abs(simulator.state_vector[0]) ** 2
                
                # Store in kernel matrix (symmetric)
                kernel_matrix[i, j] = prob_zero
                kernel_matrix[j, i] = prob_zero
        
        # Extract labels
        y = np.array([label for _, label in training_data])
        
        # Solve dual problem (simplified)
        # In a real implementation, we would solve the quadratic programming problem
        # Here we'll use a simplified approach
        alpha = np.ones(n_samples) / n_samples  # Simple uniform weights
        
        # Calculate kernel values between test point and all training points
        test_kernel = np.zeros(n_samples)
        for i in range(n_samples):
            simulator.reset()
            encoding_function(simulator, training_data[i][0])
            encoding_function(simulator, test_point, inverse=True)
            test_kernel[i] = np.abs(simulator.state_vector[0]) ** 2
        
        # Make prediction
        prediction = np.sign(np.sum(alpha * y * test_kernel))
        
        return prediction

class QuantumApplication:
    """Main application class for the quantum computing simulator"""
    
    def __init__(self):
        """Initialize the quantum application"""
        self.simulator = None
        self.circuit = None
        self.parse_arguments()
    
    def parse_arguments(self):
        """Parse command line arguments"""
        parser = argparse.ArgumentParser(description='Quantum Computing Simulator')
        
        # Main operation modes
        parser.add_argument('--algorithm', type=str, choices=[
            'bell_state', 'teleportation', 'deutsch_jozsa', 'grover', 'shor',
            'qft', 'phase_estimation', 'error_correction', 'qml'
        ], help='Quantum algorithm to run')
        
        parser.add_argument('--circuit', type=str, help='Path to a saved quantum circuit')
        parser.add_argument('--num-qubits', type=int, default=3, help='Number of qubits to simulate')
        parser.add_argument('--backend', type=str, default='numpy', help='Simulation backend')
        parser.add_argument('--visualize', action='store_true', help='Visualize results')
        parser.add_argument('--save', type=str, help='Save results to file')
        
        # Algorithm-specific parameters
        parser.add_argument('--n', type=int, help='Input for Shor\'s algorithm')
        parser.add_argument('--oracle', type=str, choices=['constant', 'balanced'], 
                           help='Oracle type for Deutsch-Jozsa algorithm')
        parser.add_argument('--marked-state', type=int, help='Marked state for Grover\'s algorithm')
        
        self.args = parser.parse_args()
    
    def initialize(self):
        """Initialize the quantum simulator"""
        from main.26_quantum_computing_simulator_part2 import QuantumSimulator
        self.simulator = QuantumSimulator(self.args.num_qubits, self.args.backend)
    
    def run_bell_state(self):
        """Create and measure a Bell state"""
        from main.26_quantum_computing_simulator_part2 import QuantumAlgorithms
        
        print("Creating Bell state between qubits 0 and 1...")
        QuantumAlgorithms.create_bell_state(self.simulator, 0, 1)
        
        # Get state before measurement
        state_vector = self.simulator.get_statevector()
        print("State vector:", state_vector)
        
        # Measure qubits
        result0 = self.simulator.measure(0)
        result1 = self.simulator.measure(1)
        print(f"Measurement results: qubit 0 = {result0}, qubit 1 = {result1}")
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            QuantumVisualization.plot_statevector(state_vector, self.args.num_qubits, "Bell State")
    
    def run_teleportation(self):
        """Run quantum teleportation protocol"""
        from main.26_quantum_computing_simulator_part2 import QuantumAlgorithms
        
        print("Initializing qubit 0 with a random state...")
        # Create a random state for qubit 0
        theta = np.random.random() * PI
        phi = np.random.random() * 2 * PI
        
        # Apply rotations to create the state
        # |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩
        ry_matrix = np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
        self.simulator.apply_gate(ry_matrix, [0])
        
        rz_matrix = np.array([
            [1, 0],
            [0, np.exp(I_UNIT * phi)]
        ], dtype=complex)
        self.simulator.apply_gate(rz_matrix, [0])
        
        # Get initial state
        initial_state = self.simulator.get_statevector()
        print("Initial state of qubit 0:", initial_state[:2])  # Show only first 2 amplitudes
        
        # Run teleportation protocol
        print("Teleporting state from qubit 0 to qubit 2...")
        QuantumAlgorithms.quantum_teleportation(self.simulator, 0, 1, 2)
        
        # Get final state
        final_state = self.simulator.get_statevector()
        print("Final state of qubit 2:", final_state)
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            
            # Extract single-qubit states
            q0_state = np.array([initial_state[0], initial_state[1]])
            q2_state = np.array([final_state[0], final_state[4]])  # Extracting |0⟩ and |1⟩ components for qubit 2
            
            # Normalize
            q0_state /= np.linalg.norm(q0_state)
            q2_state /= np.linalg.norm(q2_state)
            
            # Plot Bloch sphere representations
            QuantumVisualization.plot_bloch_sphere(q0_state, "Initial State (Qubit 0)")
            QuantumVisualization.plot_bloch_sphere(q2_state, "Teleported State (Qubit 2)")
    
    def run_deutsch_jozsa(self):
        """Run Deutsch-Jozsa algorithm"""
        from main.26_quantum_computing_simulator_part2 import QuantumAlgorithms
        
        # Define oracle functions
        def constant_oracle(n_qubits):
            """Oracle that always returns 0"""
            dim = 2 ** (n_qubits + 1)
            matrix = np.eye(dim, dtype=complex)
            return matrix
        
        def balanced_oracle(n_qubits):
            """Oracle that returns 0 for half the inputs and 1 for the other half"""
            dim = 2 ** (n_qubits + 1)
            matrix = np.eye(dim, dtype=complex)
            
            # Flip the phase of the ancilla qubit for half the inputs
            for i in range(dim // 2, dim):
                # Flip the last bit (XOR with 1)
                j = i ^ 1
                matrix[i, i] = 0
                matrix[i, j] = 1
                matrix[j, i] = 1
                matrix[j, j] = 0
            
            return matrix
        
        # Choose oracle based on argument
        if self.args.oracle == 'constant':
            oracle = constant_oracle
            print("Using constant oracle")
        else:
            oracle = balanced_oracle
            print("Using balanced oracle")
        
        # Run the algorithm
        print(f"Running Deutsch-Jozsa algorithm with {self.args.num_qubits} qubits...")
        result = QuantumAlgorithms.deutsch_jozsa(self.simulator, oracle, self.args.num_qubits)
        
        print(f"Result: The function is {'constant' if result else 'balanced'}")
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            state_vector = self.simulator.get_statevector()
            QuantumVisualization.plot_statevector(state_vector, self.args.num_qubits + 1, "Deutsch-Jozsa Result")
    
    def run_grover(self):
        """Run Grover's search algorithm"""
        from main.26_quantum_computing_simulator_part2 import QuantumAlgorithms
        
        # Define oracle for the marked state
        marked_state = self.args.marked_state
        if marked_state is None:
            marked_state = np.random.randint(0, 2 ** self.args.num_qubits)
        
        print(f"Running Grover's algorithm to find marked state: {marked_state}")
        
        def oracle_function(n_qubits):
            """Oracle that marks a specific state"""
            dim = 2 ** n_qubits
            matrix = np.eye(dim, dtype=complex)
            matrix[marked_state, marked_state] = -1  # Flip phase of marked state
            return matrix
        
        # Calculate optimal number of iterations
        optimal_iterations = int(np.pi/4 * np.sqrt(2**self.args.num_qubits))
        print(f"Using {optimal_iterations} Grover iterations")
        
        # Run the algorithm
        result = QuantumAlgorithms.grover_search(self.simulator, oracle_function, 
                                                self.args.num_qubits, optimal_iterations)
        
        # Convert result to integer
        found_state = 0
        for i, bit in enumerate(result):
            found_state |= (bit << i)
        
        print(f"Found state: {found_state} (expected: {marked_state})")
        print(f"Success: {found_state == marked_state}")
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            state_vector = self.simulator.get_statevector()
            QuantumVisualization.plot_statevector(state_vector, self.args.num_qubits, "Grover's Algorithm Result")
    
    def run_qft(self):
        """Run Quantum Fourier Transform"""
        from main.26_quantum_computing_simulator_part2 import QuantumAlgorithms
        
        # Initialize with a computational basis state
        state = np.random.randint(0, 2 ** self.args.num_qubits)
        
        # Set the initial state
        self.simulator.reset()
        state_vector = np.zeros(2 ** self.args.num_qubits, dtype=complex)
        state_vector[state] = 1.0
        self.simulator.state_vector = state_vector
        
        print(f"Applying QFT to state |{state}⟩...")
        
        # Apply QFT
        qubits = list(range(self.args.num_qubits))
        QuantumAlgorithms.quantum_fourier_transform(self.simulator, qubits)
        
        # Get transformed state
        transformed_state = self.simulator.get_statevector()
        print("Transformed state (first 8 amplitudes):", transformed_state[:8])
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            QuantumVisualization.plot_statevector(transformed_state, self.args.num_qubits, "QFT Result")
    
    def run_error_correction(self):
        """Demonstrate quantum error correction"""
        from main.26_quantum_computing_simulator_part3 import QuantumErrorCorrection, QuantumErrorType
        
        print("Demonstrating quantum error correction with bit flip code...")
        
        # Initialize qubit 0 in superposition state
        self.simulator.reset()
        h_gate = np.array([[SQRT2_INV, SQRT2_INV], [SQRT2_INV, -SQRT2_INV]], dtype=complex)
        self.simulator.apply_gate(h_gate, [0])
        
        # Get initial state
        initial_state = self.simulator.get_statevector()
        print("Initial state:", initial_state[:2])  # Show only first 2 amplitudes
        
        # Encode using bit flip code
        print("Encoding qubit 0 using qubits 1 and 2 as ancillas...")
        QuantumErrorCorrection.encode_bit_flip_code(self.simulator, 0, [1, 2])
        
        # Apply bit flip error to qubit 0
        print("Applying bit flip error to qubit 0...")
        QuantumErrorCorrection.apply_quantum_error(self.simulator, 0, QuantumErrorType.BIT_FLIP, 1.0)
        
        # Get state after error
        error_state = self.simulator.get_statevector()
        print("State after error:", error_state[:8])  # Show first 8 amplitudes
        
        # Correct the error
        print("Correcting the error...")
        QuantumErrorCorrection.decode_bit_flip_code(self.simulator, 0, [1, 2])
        
        # Get corrected state
        corrected_state = self.simulator.get_statevector()
        print("Corrected state:", corrected_state[:2])  # Show only first 2 amplitudes
        
        # Visualize if requested
        if self.args.visualize:
            from main.26_quantum_computing_simulator_part3 import QuantumVisualization
            
            # Plot the states
            plt.figure(figsize=(15, 5))
            
            plt.subplot(1, 3, 1)
            plt.bar(range(2), np.abs(initial_state[:2])**2)
            plt.title("Initial State")
            plt.xticks([0, 1], ['|0⟩', '|1⟩'])
            
            plt.subplot(1, 3, 2)
            plt.bar(range(8), np.abs(error_state[:8])**2)
            plt.title("State After Error")
            plt.xticks(range(8), [f'|{i:03b}⟩' for i in range(8)])
            
            plt.subplot(1, 3, 3)
            plt.bar(range(2), np.abs(corrected_state[:2])**2)
            plt.title("Corrected State")
            plt.xticks([0, 1], ['|0⟩', '|1⟩'])
            
            plt.tight_layout()
            plt.show()
    
    def run_qml(self):
        """Demonstrate quantum machine learning"""
        from main.26_quantum_computing_simulator_part4 import QuantumML
        
        print("Demonstrating quantum machine learning...")
        
        # Generate synthetic dataset
        np.random.seed(42)
        n_samples = 10
        n_features = self.args.num_qubits
        
        # Create two classes of data
        class_0 = np.random.normal(0.2, 0.1, (n_samples // 2, n_features))
        class_1 = np.random.normal(0.8, 0.1, (n_samples // 2, n_features))
        
        # Combine and normalize data
        X = np.vstack([class_0, class_1])
        for i in range(len(X)):
            X[i] = X[i] / np.linalg.norm(X[i])
        
        y = np.array([0] * (n_samples // 2) + [1] * (n_samples // 2))
        
        # Create training data
        training_data = [(X[i], y[i]) for i in range(n_samples)]
        
        # Define encoding function
        def encoding_function(simulator, data_point, inverse=False):
            """Encode data point into quantum circuit"""
            sign = -1 if inverse else 1
            for i, x in enumerate(data_point):
                if i < simulator.num_qubits:
                    # Apply RY rotation based on data
                    angle = sign * x * PI
                    ry_matrix = np.array([
                        [np.cos(angle / 2), -np.sin(angle / 2)],
                        [np.sin(angle / 2), np.cos(angle / 2)]
                    ], dtype=complex)
                    simulator.apply_gate(ry_matrix, [i])
        
        # Generate test point
        test_point = np.random.normal(0.8, 0.2, n_features)
        test_point = test_point / np.linalg.norm(test_point)
        
        # Run quantum SVM
        print("Running quantum support vector machine...")
        prediction = QuantumML.quantum_support_vector_machine(
            self.simulator, training_data, test_point, encoding_function
        )
        
        print(f"Predicted class for test point: {1 if prediction > 0 else 0}")
        
        # Visualize if requested and if 2D data
        if self.args.visualize and n_features == 2:
            plt.figure(figsize=(8, 6))
            
            # Plot training data
            plt.scatter(class_0[:, 0], class_0[:, 1], label='Class 0')
            plt.scatter(class_1[:, 0], class_1[:, 1], label='Class 1')
            
            # Plot test point
            plt.scatter(test_point[0], test_point[1], color='red', marker='x', s=100, label='Test Point')
            
            plt.title('Quantum SVM Classification')
            plt.xlabel('Feature 1')
            plt.ylabel('Feature 2')
            plt.legend()
            plt.show()
    
    def run(self):
        """Run the selected algorithm"""
        # Initialize simulator
        self.initialize()
        
        # Run the selected algorithm
        if self.args.algorithm == 'bell_state':
            self.run_bell_state()
        elif self.args.algorithm == 'teleportation':
            self.run_teleportation()
        elif self.args.algorithm == 'deutsch_jozsa':
            self.run_deutsch_jozsa()
        elif self.args.algorithm == 'grover':
            self.run_grover()
        elif self.args.algorithm == 'qft':
            self.run_qft()
        elif self.args.algorithm == 'error_correction':
            self.run_error_correction()
        elif self.args.algorithm == 'qml':
            self.run_qml()
        else:
            print("No algorithm selected. Use --algorithm to select one.")
            self.show_menu()
    
    def show_menu(self):
        """Show an interactive menu"""
        while True:
            print("\n===== Quantum Computing Simulator =====")
            print("1. Create and measure Bell state")
            print("2. Run quantum teleportation")
            print("3. Run Deutsch-Jozsa algorithm")
            print("4. Run Grover's search algorithm")
            print("5. Run Quantum Fourier Transform")
            print("6. Demonstrate quantum error correction")
            print("7. Demonstrate quantum machine learning")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == '1':
                self.args.algorithm = 'bell_state'
                self.args.visualize = True
                self.run_bell_state()
            elif choice == '2':
                self.args.algorithm = 'teleportation'
                self.args.visualize = True
                self.run_teleportation()
            elif choice == '3':
                self.args.algorithm = 'deutsch_jozsa'
                self.args.oracle = input("Choose oracle type (constant/balanced): ")
                self.args.visualize = True
                self.run_deutsch_jozsa()
            elif choice == '4':
                self.args.algorithm = 'grover'
                marked_input = input("Enter marked state (leave blank for random): ")
                self.args.marked_state = int(marked_input) if marked_input else None
                self.args.visualize = True
                self.run_grover()
            elif choice == '5':
                self.args.algorithm = 'qft'
                self.args.visualize = True
                self.run_qft()
            elif choice == '6':
                self.args.algorithm = 'error_correction'
                self.args.visualize = True
                self.run_error_correction()
            elif choice == '7':
                self.args.algorithm = 'qml'
                self.args.visualize = True
                self.run_qml()
            elif choice == '8':
                print("Exiting the simulator...")
                break
            else:
                print("Invalid choice. Please try again.")

def main():
    """Main entry point"""
    print("=" * 60)
    print("Quantum Computing Simulator".center(60))
    print("A sophisticated quantum computing simulation system".center(60))
    print("=" * 60)
    
    app = QuantumApplication()
    app.run()

if __name__ == "__main__":
    main() 