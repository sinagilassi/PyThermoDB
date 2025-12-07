"""
Test suite for the make_parm_identifiers method in TableEquation class.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyThermoDB as ptdb


def setup_test_environment():
    """
    Setup test environment with paths and reference data.
    
    Returns
    -------
    tuple
        A tuple containing (thermo_db, test_component)
    """
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
    
    # Initialize and return
    thermo_db = ptdb.init(ref)
    test_component = 'Methane'
    
    return thermo_db, test_component


def test_make_parm_identifiers_basic():
    """Test basic functionality with a real equation."""
    print("\n=== Test 1: Basic functionality with real equation ===")
    
    # Setup
    thermo_db, comp1 = setup_test_environment()
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    # Test the new method
    parm_identifiers = comp1_eq.make_parm_identifiers()
    
    print(f"Parameters: {comp1_eq.parms}")
    print(f"Parameter identifiers: {parm_identifiers}")
    
    # Assertions
    assert isinstance(parm_identifiers, list), "Should return a list"
    assert len(parm_identifiers) == 4, "Should have 4 parameters (a, b, c, d)"
    
    # Check format of identifiers
    for identifier in parm_identifiers:
        assert ' | ' in identifier, f"Identifier '{identifier}' should contain ' | '"
        parts = identifier.split(' | ')
        assert len(parts) == 3, f"Identifier '{identifier}' should have 3 parts"
    
    print("✓ Test 1 passed!")


def test_make_parm_identifiers_with_explicit_parms():
    """Test with explicitly provided parameters."""
    print("\n=== Test 2: Explicit parameters ===")
    
    # Setup
    thermo_db, comp1 = setup_test_environment()
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    # Create custom parameters
    custom_parms = {
        'C1': {'name': 'C1', 'symbol': 'C1', 'unit': '1'},
        'C2': {'name': 'C2', 'symbol': 'C2', 'unit': 'K'},
        'C3': {'name': 'C3', 'symbol': 'C3', 'unit': '1E3'},
    }
    
    # Test with custom parameters
    parm_identifiers = comp1_eq.make_parm_identifiers(custom_parms)
    
    print(f"Custom parameters: {custom_parms}")
    print(f"Parameter identifiers: {parm_identifiers}")
    
    # Assertions
    assert len(parm_identifiers) == 3, "Should have 3 custom parameters"
    assert 'C1 | C1 | 1' in parm_identifiers
    assert 'C2 | C2 | K' in parm_identifiers
    assert 'C3 | C3 | 1E3' in parm_identifiers
    
    print("✓ Test 2 passed!")


def test_make_parm_identifiers_empty_parms():
    """Test with empty parameters."""
    print("\n=== Test 3: Empty parameters ===")
    
    # Setup
    thermo_db, comp1 = setup_test_environment()
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    # Test with empty dict
    empty_parms = {}
    parm_identifiers = comp1_eq.make_parm_identifiers(empty_parms)
    
    print(f"Empty parameters: {empty_parms}")
    print(f"Parameter identifiers: {parm_identifiers}")
    
    # Assertions
    assert isinstance(parm_identifiers, list), "Should return a list"
    assert len(parm_identifiers) == 0, "Should return empty list for empty params"
    
    print("✓ Test 3 passed!")


def test_make_parm_identifiers_missing_attributes():
    """Test error handling for missing attributes."""
    print("\n=== Test 4: Missing attributes ===")
    
    # Setup
    thermo_db, comp1 = setup_test_environment()
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    # Create parameters with missing attributes
    incomplete_parms = {
        'C1': {'name': 'C1', 'symbol': 'C1'},  # missing 'unit'
        'C2': {'symbol': 'C2', 'unit': 'K'},   # missing 'name'
        'C3': {'name': 'C3', 'symbol': 'C3', 'unit': '1'},  # complete
    }
    
    # Test - should skip incomplete params and only return complete one
    parm_identifiers = comp1_eq.make_parm_identifiers(incomplete_parms)
    
    print(f"Incomplete parameters: {incomplete_parms}")
    print(f"Parameter identifiers: {parm_identifiers}")
    
    # Assertions
    assert isinstance(parm_identifiers, list), "Should return a list"
    assert len(parm_identifiers) == 1, "Should only return complete parameter"
    assert 'C3 | C3 | 1' in parm_identifiers
    
    print("✓ Test 4 passed!")


def test_make_parm_identifiers_none_parms():
    """Test with None parameters (should use self.parms)."""
    print("\n=== Test 5: None parameters (use self.parms) ===")
    
    # Setup
    thermo_db, comp1 = setup_test_environment()
    comp1_eq = thermo_db.build_equation(comp1, 'CO2 Hydrogenation', 1)
    
    # Test with None (should use self.parms)
    parm_identifiers = comp1_eq.make_parm_identifiers(None)
    
    print(f"Parameters from self.parms: {comp1_eq.parms}")
    print(f"Parameter identifiers: {parm_identifiers}")
    
    # Assertions
    assert isinstance(parm_identifiers, list), "Should return a list"
    assert len(parm_identifiers) > 0, "Should use self.parms when None is provided"
    
    print("✓ Test 5 passed!")


def run_all_tests():
    """Run all test functions."""
    print("=" * 70)
    print("Running make_parm_identifiers test suite")
    print("=" * 70)
    
    try:
        test_make_parm_identifiers_basic()
        test_make_parm_identifiers_with_explicit_parms()
        test_make_parm_identifiers_empty_parms()
        test_make_parm_identifiers_missing_attributes()
        test_make_parm_identifiers_none_parms()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        return True
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
