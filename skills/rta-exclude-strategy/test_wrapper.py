"""Test RTA skill wrapper"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from rta_exclude import run_rta_exclude_strategy
from rta_exclude.skill_wrapper import validate_config

def test_validate_config():
    print("="*80)
    print("Test: validate_config")
    print("="*80)
    
    result = validate_config(data_path="nonexistent.csv", ctrl_group_value="ctrl")
    print(f"Valid: {result['valid']}")
    print(f"Errors: {result['errors']}")
    assert not result['valid'], "Should be invalid for nonexistent file"
    print("PASS")

def test_wrapper_basic():
    print("\n" + "="*80)
    print("Test: run_rta_exclude_strategy error handling")
    print("="*80)
    
    result = run_rta_exclude_strategy(
        data_path="test_data.csv",
        ctrl_group_value="ctrl",
        verbose=False
    )
    
    print(f"Success: {result['success']}")
    print(f"Error: {result['error'][:100] if result['error'] else None}")
    assert not result['success'], "Should fail for nonexistent file"
    assert result['error'] is not None, "Should have error message"
    print("PASS")

if __name__ == "__main__":
    try:
        test_validate_config()
        test_wrapper_basic()
        print("\n" + "="*80)
        print("All tests passed!")
        print("="*80)
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
