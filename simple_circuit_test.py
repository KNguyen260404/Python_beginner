#!/usr/bin/env python3
"""
Simple Circuit Generation Test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import necessary classes
import importlib.util
spec = importlib.util.spec_from_file_location("circuit_designer", "31_digital_circuit_designer.py")
circuit_designer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(circuit_designer)

def test_circuit_generation():
    """Test circuit generation step by step"""
    
    # Create parser
    parser = circuit_designer.BooleanExpressionParser()
    
    # Parse expression
    expression = "OUTPUT = ~((A+B)*C)"
    print(f"Expression: {expression}")
    print("=" * 50)
    
    result = parser.parse_expression(expression)
    
    # Print the tree structure
    def print_tree_detailed(tree, indent=0):
        prefix = "  " * indent
        if tree['type'] == 'VAR':
            print(f"{prefix}VAR: {tree['name']}")
        elif tree['type'] == 'NOT':
            print(f"{prefix}NOT:")
            print_tree_detailed(tree['operand'], indent + 1)
        elif tree['type'] in ['AND', 'OR', 'XOR']:
            print(f"{prefix}{tree['type']}:")
            print(f"{prefix}  Left:")
            print_tree_detailed(tree['left'], indent + 2)
            print(f"{prefix}  Right:")
            print_tree_detailed(tree['right'], indent + 2)
    
    print("Original Tree Structure:")
    print_tree_detailed(result['tree'])
    
    print("\n" + "=" * 50)
    print("EXPECTED CIRCUIT STRUCTURE:")
    print("=" * 50)
    print("For expression: ~((A+B)*C)")
    print()
    print("Step 1: A + B (OR gate)")
    print("  INPUT_A ──┐")
    print("            ├── OR_1 ──┐")
    print("  INPUT_B ──┘           │")
    print()
    print("Step 2: (A+B) * C (AND gate)")
    print("  OR_1 ──────────┐")
    print("                 ├── AND_1 ──┐")
    print("  INPUT_C ───────┘            │")
    print()
    print("Step 3: ~((A+B)*C) (NOT gate)")
    print("  AND_1 ── NOT_1 ── OUTPUT")
    print()
    print("Final circuit should be:")
    print("INPUT_A ──┐")
    print("          ├─ OR_1 ──┐")
    print("INPUT_B ──┘         ├─ AND_1 ── NOT_1 ── OUTPUT")
    print("INPUT_C ────────────┘")

if __name__ == "__main__":
    test_circuit_generation() 