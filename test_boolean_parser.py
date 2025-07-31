#!/usr/bin/env python3
"""
Test Boolean Expression Parser
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the parser from the main file
import importlib.util
spec = importlib.util.spec_from_file_location("circuit_designer", "31_digital_circuit_designer.py")
circuit_designer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(circuit_designer)

def test_expression_parsing():
    """Test parsing of Boolean expressions"""
    parser = circuit_designer.BooleanExpressionParser()
    
    # Test cases
    test_cases = [
        "OUTPUT = ~((A+B)*C)",      # NOT((A OR B) AND C)
        "OUTPUT = ~(A+B)*C",        # (~(A OR B)) AND C  
        "OUTPUT = ~A+B*C",          # (~A) OR (B AND C)
        "OUTPUT = (A+B)*C",         # (A OR B) AND C
        "OUTPUT = A+B*C",           # A OR (B AND C)
    ]
    
    for expr in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {expr}")
        print(f"{'='*50}")
        
        try:
            result = parser.parse_expression(expr)
            print(f"Variables: {result['variables']}")
            print(f"Output: {result['output']}")
            
            # Print the tree structure
            def print_tree(tree, indent=0):
                prefix = "  " * indent
                if tree['type'] == 'VAR':
                    print(f"{prefix}VAR: {tree['name']}")
                elif tree['type'] == 'NOT':
                    print(f"{prefix}NOT:")
                    print_tree(tree['operand'], indent + 1)
                elif tree['type'] in ['AND', 'OR', 'XOR']:
                    print(f"{prefix}{tree['type']}:")
                    print(f"{prefix}  Left:")
                    print_tree(tree['left'], indent + 2)
                    print(f"{prefix}  Right:")
                    print_tree(tree['right'], indent + 2)
            
            print("\nParsed Tree:")
            print_tree(result['tree'])
            
            # Test optimization
            optimized = parser.optimize_expression(result['tree'])
            print("\nOptimized Tree:")
            print_tree(optimized)
            
        except Exception as e:
            print(f"ERROR: {e}")

def test_precedence():
    """Test operator precedence"""
    parser = circuit_designer.BooleanExpressionParser()
    
    print(f"\n{'='*60}")
    print("TESTING OPERATOR PRECEDENCE")
    print(f"{'='*60}")
    
    # Test operator precedence: NOT > AND > OR
    expressions = [
        "A+B*C",        # Should be: A OR (B AND C)
        "~A+B",         # Should be: (~A) OR B
        "~A*B+C",       # Should be: ((~A) AND B) OR C
        "A*~B+C",       # Should be: (A AND (~B)) OR C
        "~(A+B)*C",     # Should be: (~(A OR B)) AND C
        "~((A+B)*C)",   # Should be: ~((A OR B) AND C)
    ]
    
    for expr in expressions:
        print(f"\nExpression: {expr}")
        try:
            result = parser.parse_expression(expr)
            
            def tree_to_string(tree):
                if tree['type'] == 'VAR':
                    return tree['name']
                elif tree['type'] == 'NOT':
                    operand_str = tree_to_string(tree['operand'])
                    if tree['operand']['type'] in ['AND', 'OR', 'XOR']:
                        return f"~({operand_str})"
                    else:
                        return f"~{operand_str}"
                elif tree['type'] in ['AND', 'OR', 'XOR']:
                    left_str = tree_to_string(tree['left'])
                    right_str = tree_to_string(tree['right'])
                    op_symbol = {'AND': '*', 'OR': '+', 'XOR': '@'}[tree['type']]
                    
                    # Add parentheses if needed for clarity
                    if tree['type'] == 'OR' and tree['left']['type'] == 'AND':
                        left_str = f"({left_str})"
                    if tree['type'] == 'OR' and tree['right']['type'] == 'AND':
                        right_str = f"({right_str})"
                    
                    return f"{left_str}{op_symbol}{right_str}"
                return str(tree)
            
            parsed_str = tree_to_string(result['tree'])
            print(f"Parsed as: {parsed_str}")
            
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_expression_parsing()
    test_precedence() 