"""
Test incremental parameter updates in orchestrator
"""
import sys
sys.path.insert(0, '.')

from ai.llm_orchestrator import IndustrialParkLLMOrchestrator

def test_incremental_updates():
    """Test incremental parameter adjustment capabilities"""
    
    print("\n=== Testing Incremental Parameter Updates ===\n")
    
    # Initialize orchestrator
    print("1. Initializing orchestrator...")
    orchestrator = IndustrialParkLLMOrchestrator()
    print("✓ Orchestrator initialized\n")
    
    # Simulate initial design parameters (from first conversation)
    initial_params = {
        "projectName": "Pilot Industrial Estate",
        "totalArea_ha": 191.42,
        "industryFocus": [
            {"type": "light_manufacturing", "percentage": 40, "count": 15},
            {"type": "warehouse", "percentage": 25, "count": 8},
            {"type": "logistics", "percentage": 15, "count": 3}
        ],
        "workerCapacity": 5000,
        "constraints": {
            "greenAreaMin_percent": 10,
            "salableAreaMin_percent": 75,
            "utilitiesAreaMin_percent": 15
        }
    }
    
    orchestrator.current_design_params = initial_params
    print("2. Initial parameters set:")
    print(f"   - Total area: {initial_params['totalArea_ha']} ha")
    print(f"   - Green area min: {initial_params['constraints']['greenAreaMin_percent']}%")
    print(f"   - Worker capacity: {initial_params['workerCapacity']}")
    print()
    
    # Test 1: Update single parameter
    print("3. Testing update_parameter (tăng green area lên 12%)...")
    try:
        result = orchestrator.update_parameter(
            param_path="constraints.greenAreaMin_percent",
            value=12,
            user_request="Tăng green area lên 12%"
        )
        print(f"✓ Update result: {result['status']}")
        print(f"   Message: {result['message']}")
        print(f"   New value: {result['new_value']}%")
        print(f"   Design iteration #{len(orchestrator.design_iterations)}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 2: IEAT compliance validation
    print("4. Testing IEAT compliance validation...")
    try:
        compliance = orchestrator._validate_ieat_compliance()
        print("✓ Compliance check:")
        print(f"   Overall compliant: {compliance['compliant']}")
        for rule, result in compliance['rules'].items():
            status = "✓" if result['compliant'] else "✗"
            print(f"   {status} {rule}: {result['status']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 3: Suggest adjustments
    print("5. Testing suggest_adjustment (thêm 3 nhà máy)...")
    try:
        suggestions = orchestrator.suggest_adjustment(
            "Thêm 3 nhà máy light manufacturing nữa"
        )
        print("✓ Suggestions generated:")
        print(f"   Action: {suggestions['action']}")
        print(f"   Target: {suggestions['target']}")
        if 'changes' in suggestions:
            print(f"   Changes: {suggestions['changes']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 4: Apply suggestions
    print("6. Testing apply_suggestions...")
    try:
        suggested_changes = {
            "industryFocus[0].count": 18  # Increase from 15 to 18
        }
        apply_result = orchestrator.apply_suggestions(suggested_changes)
        print("✓ Suggestions applied:")
        print(f"   Status: {apply_result['status']}")
        print(f"   Applied: {apply_result['applied_count']} changes")
        if 'failed' in apply_result:
            print(f"   Failed: {apply_result['failed']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test 5: View iteration history
    print("7. Design iteration history:")
    for i, iteration in enumerate(orchestrator.design_iterations, 1):
        print(f"   Iteration #{i}:")
        print(f"     - Request: {iteration['user_request']}")
        print(f"     - Param: {iteration['param_path']}")
        print(f"     - Value: {iteration['old_value']} → {iteration['new_value']}")
        print(f"     - Time: {iteration['timestamp']}")
    print()
    
    print("=== All Tests Complete ===\n")

if __name__ == "__main__":
    test_incremental_updates()
