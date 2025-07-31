#!/usr/bin/env python3
"""
Debug Expression Generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the parser from the main file
import importlib.util
spec = importlib.util.spec_from_file_location("circuit_designer", "31_digital_circuit_designer.py")
circuit_designer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(circuit_designer)

def debug_expression():
    """Debug specific expression"""
    parser = circuit_designer.BooleanExpressionParser()
    
    expression = "OUTPUT = ~((A+B)*C)"
    print(f"Testing expression: {expression}")
    print("=" * 50)
    
    # Parse expression
    result = parser.parse_expression(expression)
    print(f"Variables: {result['variables']}")
    print(f"Output: {result['output']}")
    
    # Print original tree
    def print_tree(tree, indent=0, label=""):
        prefix = "  " * indent
        if label:
            print(f"{prefix}{label}:")
            prefix += "  "
        
        if tree['type'] == 'VAR':
            print(f"{prefix}VAR: {tree['name']}")
        elif tree['type'] == 'NOT':
            print(f"{prefix}NOT:")
            print_tree(tree['operand'], indent + 1)
        elif tree['type'] in ['AND', 'OR', 'XOR']:
            print(f"{prefix}{tree['type']}:")
            print_tree(tree['left'], indent + 1, "Left")
            print_tree(tree['right'], indent + 1, "Right")
    
    print("\nOriginal Tree:")
    print_tree(result['tree'])
    
    # Test optimization
    print("\nApplying optimization...")
    optimized = parser.optimize_expression(result['tree'])
    print("\nOptimized Tree:")
    print_tree(optimized)
    
    # Show what the circuit should look like step by step
    print("\n" + "=" * 50)
    print("EXPECTED CIRCUIT FLOW:")
    print("=" * 50)
    print("1. A OR B → OR_gate_1")
    print("2. OR_gate_1 AND C → AND_gate_1") 
    print("3. NOT(AND_gate_1) → NOT_gate_1 → OUTPUT")
    print()
    print("So the correct order should be:")
    print("INPUT_A ──┐")
    print("          ├─ OR_gate ──┐")  
    print("INPUT_B ──┘            ├─ AND_gate ── NOT_gate ── OUTPUT")
    print("INPUT_C ───────────────┘")

if __name__ == "__main__":
    debug_expression() 