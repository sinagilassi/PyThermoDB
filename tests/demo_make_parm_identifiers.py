"""
Demonstration of make_parm_identifiers method usage.
This shows how the method can be used in practice.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyThermoDB as ptdb


def demo_basic_usage():
    """Demonstrate basic usage of make_parm_identifiers."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION: make_parm_identifiers Method")
    print("=" * 70)
    
    # Setup
    parent_dir = os.path.join(
        os.path.dirname(__file__), 
        '../examples/basic-1'
    )
    yml_path = os.path.join(parent_dir, 'ref1.yml')
    csv_path_1 = os.path.join(
        parent_dir, 
        'Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
    )
    csv_path_2 = os.path.join(
        parent_dir, 
        'Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
    )
    
    ref = {
        'reference': [yml_path],
        'tables': [csv_path_1, csv_path_2]
    }
    
    # Initialize and build equation
    thermo_db = ptdb.init(ref)
    comp1 = 'Methane'
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    print("\n1. Original Parameters Dictionary:")
    print("-" * 70)
    for key, value in comp1_eq.parms.items():
        print(f"  {key}: {value}")
    
    print("\n2. Using make_parm_identifiers():")
    print("-" * 70)
    parm_identifiers = comp1_eq.make_parm_identifiers()
    for i, identifier in enumerate(parm_identifiers, 1):
        print(f"  {i}. {identifier}")
    
    print("\n3. Practical Use Case - Building Equation References:")
    print("-" * 70)
    print("  These identifiers can be used in equation bodies like:")
    print("  Example format: parms['<identifier>']")
    print()
    for identifier in parm_identifiers:
        param_symbol = identifier.split(' | ')[1]
        print(f"  parms['{identifier}'] for parameter '{param_symbol}'")
    
    print("\n4. Comparison with Equation Body:")
    print("-" * 70)
    print("  Current equation body:")
    print(f"  {comp1_eq.body}")
    print()
    print("  With full identifiers, it could be written as:")
    example_body = "res = parms['a | a | 1'] + parms['b | b | 1E2']*args['T'] + parms['c | c | 1E5']*(args['T']**2) + parms['d | d | 1E9']*(args['T']**3)"
    print(f"  {example_body}")
    
    print("\n5. Benefits:")
    print("-" * 70)
    print("  ✓ Clear documentation of parameter units in equation body")
    print("  ✓ Self-documenting code for complex equations")
    print("  ✓ Easier debugging and validation")
    print("  ✓ Consistent parameter naming across equations")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


def demo_custom_parameters():
    """Demonstrate with custom parameters."""
    print("\n" + "=" * 70)
    print("DEMONSTRATION: Custom Parameters")
    print("=" * 70)
    
    # Setup
    parent_dir = os.path.join(
        os.path.dirname(__file__), 
        '../examples/basic-1'
    )
    yml_path = os.path.join(parent_dir, 'ref1.yml')
    csv_path_1 = os.path.join(
        parent_dir, 
        'Table A.II The Molar Heat Capacities of Gases in the Ideal Gas (Zero-Pressure) State.csv'
    )
    csv_path_2 = os.path.join(
        parent_dir, 
        'Table A.IV Enthalpies and Gibbs Energies of Formation.csv'
    )
    
    ref = {
        'reference': [yml_path],
        'tables': [csv_path_1, csv_path_2]
    }
    
    thermo_db = ptdb.init(ref)
    comp1_eq = thermo_db.build_equation('Methane', 'CO2 Hydrogenation', 1)
    
    # Create vapor pressure equation parameters
    vapor_pressure_parms = {
        'C1': {'name': 'C1', 'symbol': 'C1', 'unit': '1'},
        'C2': {'name': 'C2', 'symbol': 'C2', 'unit': '1'},
        'C3': {'name': 'C3', 'symbol': 'C3', 'unit': '1'},
        'C4': {'name': 'C4', 'symbol': 'C4', 'unit': '1'},
        'C5': {'name': 'C5', 'symbol': 'C5', 'unit': '1'},
    }
    
    print("\nVapor Pressure Equation Parameters:")
    print("-" * 70)
    parm_identifiers = comp1_eq.make_parm_identifiers(vapor_pressure_parms)
    for identifier in parm_identifiers:
        print(f"  {identifier}")
    
    print("\nExample Antoine Equation Body Using These Identifiers:")
    print("-" * 70)
    equation = """
    res = math.exp(
        parms['C1 | C1 | 1'] + 
        parms['C2 | C2 | 1']/args['T'] + 
        parms['C3 | C3 | 1']*math.log(args['T']) + 
        parms['C4 | C4 | 1']*(args['T']**parms['C5 | C5 | 1'])
    )
    """
    print(equation)
    
    print("=" * 70)


if __name__ == "__main__":
    demo_basic_usage()
    demo_custom_parameters()
