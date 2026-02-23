
import sys
import os
from pathlib import Path
import pytest
from shapely.geometry import Point, LineString, box

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from optimization.utility_router import UtilityNetworkDesigner
from optimization.financial_optimizer import FinancialModel

def test_utility_financial_integration():
    """
    Verify that FinancialModel accepts real utility network costs 
    instead of estimating them from road length.
    """
    print("\n" + "="*70)
    print("INTEGRATION TEST: Utility Router -> Financial Model")
    print("="*70)
    
    # 1. Setup Scenario: High utility complexity, low road complexity
    # We want a case where real pipes are MUCH longer than roads (e.g. zig-zag)
    # or shorter/different.
    
    # Simple road: 100m long
    roads = [{
        'id': 1,
        'geometry': LineString([(0, 0), (100, 0)]),
        'type': 'internal',
        'length': 100
    }]
    
    # Lots far away from road (requiring long connections)
    lots = [
        {'id': 1, 'geometry': box(50, 50, 60, 60)}, # 50m from road
        {'id': 2, 'geometry': box(80, 50, 90, 60)}  # 50m from road
    ]
    
    design = {
        'total_area': 10000,
        'roads': roads,
        'lots': lots
    }
    
    # 2. Run Utility Router
    designer = UtilityNetworkDesigner()
    water_net = designer.design_water_network(lots, roads, Point(0,0))
    
    print(f"Real Water Pipe Length: {water_net['total_length']:.2f}m")
    print(f"Real Water Cost: {water_net['cost']:,.0f} VND")
    
    # 3. Calculate Financials WITHOUT real utility data (Baseline)
    fin_model = FinancialModel()
    base_cost = fin_model.calculate_construction_cost(design)
    
    # Check what it estimated
    # It estimates pipe length = road length (100m)
    # Real length should be > 100m because of connections to lots at y=50
    print(f"Estimated Water Cost (Baseline): {base_cost['water_pipes']:,.0f} VND")
    
    # 4. Calculate Financials WITH real utility data
    # (This API doesn't exist yet, we expect this call to fail or need update)
    try:
        real_cost = fin_model.calculate_construction_cost(
            design, 
            utility_network_costs={
                'water_pipes': water_net['cost'],
                # Mock others to 0 or specific values
                'sewer_pipes': 0,
                'electric_cables': 0
            }
        )
        
        print(f"Integrated Water Cost: {real_cost['water_pipes']:,.0f} VND")
        
        # Assertion: The financial model should use the provided cost
        assert real_cost['water_pipes'] == water_net['cost']
        assert real_cost['water_pipes'] != base_cost['water_pipes']
        
        print("✅ Integration SUCCESS: Financial model used real utility costs.")
        
    except TypeError as e:
        print(f"❌ Integration FAILED: API does not support utility_network_costs")
        print(e)
        raise
    except AssertionError as e:
        print(f"❌ Integration FAILED: Cost mismatch")
        raise

if __name__ == "__main__":
    try:
        test_utility_financial_integration()
        sys.exit(0)
    except Exception as e:
        sys.exit(1)
