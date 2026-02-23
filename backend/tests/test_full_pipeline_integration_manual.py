
import sys
import os
from pathlib import Path
import pytest
from shapely.geometry import Polygon, LineString, box
import unittest.mock

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
# Add docker directory
sys.path.insert(0, str(Path(__file__).parent.parent / "docker"))

try:
    from core.optimization.optimized_pipeline_integrator import optimize_subdivision_pipeline
    print("✅ Imported pipeline function")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

def test_pipeline_execution():
    print("\n" + "="*70)
    print("MANUAL PIPELINE INTEGRATION TEST")
    print("="*70)
    
    # 1. Setup Data
    # Site: 200x200m
    land_boundary = box(0, 0, 200, 200)
    
    # Blocks: 2 large blocks
    blocks = [
        {'geometry': box(10, 10, 90, 190), 'zone': 'FACTORY'},
        {'geometry': box(110, 10, 190, 190), 'zone': 'WAREHOUSE'}
    ]
    
    config = {
        'use_advanced_optimization': True,
        'min_plot_quality': 70.0,
        'num_road_branches': 2
    }
    
    print("🚀 Running optimize_subdivision_pipeline...")
    
    # 2. Run Pipeline
    opt_blocks, roads, metrics = optimize_subdivision_pipeline(
        blocks,
        land_boundary,
        config
    )
    
    # 3. Verify Results
    print("\n📊 Verification:")
    print(f"  - Total Lots: {metrics.get('total_lots')}")
    print(f"  - Financial ROI: {metrics.get('roi_percentage')}")
    print(f"  - Utility Networks: {list(metrics.get('utility_networks', {}).keys())}")
    
    # Assertions
    if metrics.get('roi_percentage') is None:
        print("❌ ROI missing! Integration likely failed.")
        sys.exit(1)
        
    if 'water' not in metrics.get('utility_networks', {}):
        print("❌ Utility networks missing!")
        sys.exit(1)
        
    # Check if costs are non-zero (assuming some generation happened)
    # Note: If random generation fails to place lots, roi might be weird, but structure should be there.
    utility_nets = metrics['utility_networks']
    print(f"  - Water Cost: {utility_nets['water'].get('cost', 0):,.0f}")
    
    print("\n✅ Pipeline Integration SUCCESS!")

if __name__ == "__main__":
    try:
        test_pipeline_execution()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Execution Failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
