# Quantum Computing Simulator

An extremely advanced Python application that simulates quantum computing systems, implements quantum algorithms, and provides visualization tools for quantum states.

## Features

- **Complete Quantum Circuit Model**: Implementation of quantum gates, registers, and measurements
- **Advanced Quantum Algorithms**: Shor's, Grover's, Deutsch-Jozsa, QFT, and more
- **Quantum Error Correction**: Bit-flip, phase-flip, and Shor's 9-qubit code
- **Quantum Machine Learning**: Quantum kernels, variational classifiers, and quantum neural networks
- **Interactive Visualization**: Bloch sphere, statevector, density matrix, and circuit evolution
- **High Performance**: Optimized simulation with multiple backend options

## Requirements

- Python 3.7+
- NumPy
- SciPy
- Matplotlib
- SymPy
- NetworkX
- tqdm

## Installation

1. Install the required packages:

```bash
pip install -r requirements_quantum.txt
```

## Usage

### Command Line Interface

Run the simulator with a specific algorithm:

```bash
python 26_quantum_computing_simulator.py --algorithm bell_state --num-qubits 3 --visualize
```

Available algorithms:
- `bell_state`: Create and measure Bell states
- `teleportation`: Quantum teleportation protocol
- `deutsch_jozsa`: Deutsch-Jozsa algorithm
- `grover`: Grover's search algorithm
- `shor`: Shor's factoring algorithm
- `qft`: Quantum Fourier Transform
- `phase_estimation`: Quantum Phase Estimation
- `error_correction`: Quantum error correction demonstration
- `qml`: Quantum Machine Learning demonstration

### Interactive Menu

Run the simulator without arguments to use the interactive menu:

```bash
python 26_quantum_computing_simulator.py
```

## Project Structure

The simulator is organized into multiple components:

1. **Core Quantum Circuit Model** (`26_quantum_computing_simulator.py`):
   - Quantum gates, registers, and circuit operations
   - State representation and manipulation

2. **Quantum Algorithms** (`26_quantum_computing_simulator_part2.py`):
   - Implementation of standard quantum algorithms
   - Quantum state simulation

3. **Error Correction & Visualization** (`26_quantum_computing_simulator_part3.py`):
   - Quantum error models and correction codes
   - Visualization tools for quantum states

4. **Quantum Machine Learning & Application** (`26_quantum_computing_simulator_part4.py`):
   - Quantum machine learning algorithms
   - Main application interface

## Quantum Gates

The simulator implements all standard quantum gates:

- **Single-qubit gates**: Pauli-X/Y/Z, Hadamard, Phase (S), T, Rotation (Rx, Ry, Rz)
- **Two-qubit gates**: CNOT, CZ, SWAP, Controlled-Phase
- **Multi-qubit gates**: Toffoli (CCNOT)
- **Custom gates**: User-defined unitary operations

## Quantum Algorithms

### Bell State Creation
Creates maximally entangled states between qubits.

### Quantum Teleportation
Transfers a quantum state from one qubit to another using entanglement.

### Deutsch-Jozsa Algorithm
Determines if a function is constant or balanced with a single query.

### Grover's Search Algorithm
Finds a marked item in an unstructured database with quadratic speedup.

### Quantum Fourier Transform
Transforms between the computational basis and the Fourier basis.

### Shor's Factoring Algorithm
Factors integers in polynomial time (theoretical demonstration).

## Quantum Error Correction

The simulator includes implementations of:

- **Bit Flip Code**: Protects against X errors
- **Phase Flip Code**: Protects against Z errors
- **Shor's 9-Qubit Code**: Protects against arbitrary single-qubit errors

## Quantum Machine Learning

- **Quantum Kernel Estimation**: For support vector machines
- **Variational Quantum Classifier**: Parameterized quantum circuits for classification
- **Quantum Neural Networks**: Quantum analogue of classical neural networks

## Visualization Tools

- **Statevector Visualization**: Amplitude and probability plots
- **Bloch Sphere Representation**: For single-qubit states
- **Density Matrix Plots**: For mixed quantum states
- **Circuit Evolution Animation**: Watch quantum states evolve during circuit execution

## Advanced Usage

### Custom Quantum Circuits

Create your own quantum circuits:

```python
from main.26_quantum_computing_simulator import QuantumCircuit, QuantumRegister

# Create registers and circuit
qreg = QuantumRegister(3, "q")
circuit = QuantumCircuit(qregs=[qreg])

# Add gates
circuit.h(0)
circuit.cnot(0, 1)
circuit.x(2)
```

### Backend Selection

Choose different simulation backends:

```bash
python 26_quantum_computing_simulator.py --backend sparse --num-qubits 10
```

Available backends:
- `numpy`: Dense matrix representation (default)
- `sparse`: Sparse matrix for larger systems
- `tensor_network`: Tensor network representation for certain circuits
- `symbolic`: Symbolic computation for exact results

## Performance Considerations

- Simulation complexity grows exponentially with qubit count
- For systems larger than 20 qubits, use specialized backends
- Parallelization is available for certain operations

## License

This project is open source and available under the MIT License. 