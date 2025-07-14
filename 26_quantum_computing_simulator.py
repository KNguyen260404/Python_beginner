#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Quantum Computing Simulator
--------------------------
A sophisticated quantum computing simulator that implements:
- Quantum gates and circuits
- Quantum algorithms (Shor's, Grover's, etc.)
- Quantum error correction
- Quantum machine learning primitives
- Interactive visualization of quantum states

This is the main entry point that combines all simulator components.
"""

import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Union, Optional, Any

# Import simulator components
from quantum_simulator_core import (
    QuantumSimulator, QuantumAlgorithms, QuantumGateType, MeasurementType,
    QuantumSimulatorBackend, QuantumGate, QuantumRegister, ClassicalRegister,
    QuantumCircuit
)
from quantum_simulator_extended import (
    QuantumErrorCorrection, QuantumErrorType, QuantumVisualization,
    QuantumML, QuantumApplication
)

# Constants
SQRT2 = np.sqrt(2)
SQRT2_INV = 1 / SQRT2
PI = np.pi
I_UNIT = 1j  # Imaginary unit

def main():
    """Main entry point"""
    print("=" * 60)
    print("Quantum Computing Simulator".center(60))
    print("A sophisticated quantum computing simulation system".center(60))
    print("=" * 60)
    
    # Create and run the application
    app = QuantumApplication()
    app.run()

if __name__ == "__main__":
    main() 