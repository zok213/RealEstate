"""
Test script for Pilot DWG demo system

Tests the complete pipeline:
1. Extract topography from Pilot DWG
2. Divide into zones
3. Generate layout for Zone 1
4. Export color-coded DXF
"""

import sys
import os
from pathlib import Path

# Add backend to path - go up one level from sample-data to project root, then into backend
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

import logging
import time

# Fix Windows console encoding
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_pilot_demo():
    """Test complete Pilot demo pipeline"""
    
    print("=" * 70)
    print("PILOT DWG DEMO SYSTEM TEST")
    print("=" * 70)
    
    # File path
    pilot_file = Path(__file__).parent / "Pilot_Existing Topo _ Boundary.dxf"
    
    if not pilot_file.exists():
        print(f"❌ Pilot file not found: {pilot_file}")
        return False
    
    print(f"\nUsing file: {pilot_file}")
    
    start_time = time.time()
    
    try:
        # Import modules
        from demo.pilot_zone_processor import process_pilot_zone
        from demo.fast_layout_generator import FastLayoutGenerator
        from demo.demo_dxf_generator import DemoDXFGenerator
        
        # Step 1: Process Zone 1
        print("\n" + "=" * 70)
        print("STEP 1: Processing Zone 1 with Topography")
        print("=" * 70)
        
        step1_start = time.time()
        
        zone_data = process_pilot_zone(
            file_path=str(pilot_file),
            zone_id=1,
            extract_terrain=True
        )
        
        step1_time = time.time() - step1_start
        
        print(f"\n[OK] Zone 1 processed in {step1_time:.1f}s")
        print(f"  Area: {zone_data['zone']['area_ha']:.2f} ha")
        print(f"  Parameters: {zone_data['parameters']['plot_count']} plots")
        
        if 'terrain_data' in zone_data['zone']:
            terrain = zone_data['zone']['terrain_data']
            print(f"  Terrain: {terrain['avg_elevation']:.1f}m avg elevation")
            print(f"  Slope: {terrain['avg_slope']:.1f}% avg")
            print(f"  Buildable: {terrain['buildable_percentage']:.1f}%")
        
        # Step 2: Generate Layout
        print("\n" + "=" * 70)
        print("STEP 2: Generating Terrain-Aware Layout")
        print("=" * 70)
        
        step2_start = time.time()
        
        generator = FastLayoutGenerator(terrain_strategy='balanced_cut_fill')
        
        layout = generator.generate_layout(
            zone=zone_data['zone'],
            parameters=zone_data['parameters'],
            terrain_data=zone_data['zone'].get('terrain_data')
        )
        
        step2_time = time.time() - step2_start
        
        print(f"\n[OK] Layout generated in {step2_time:.1f}s")
        print(f"  Plots: {len(layout['plots'])}")
        print(f"  Roads: {len(layout['roads'])} segments")
        print(f"  Fire stations: {len(layout['fire_stations'])}")
        print(f"  Green areas: {len(layout['green_areas'])}")
        
        # Print industry distribution
        industry_counts = {}
        for plot in layout['plots']:
            itype = plot['industry_type']
            industry_counts[itype] = industry_counts.get(itype, 0) + 1
        
        print(f"\n  Industry distribution:")
        for itype, count in industry_counts.items():
            print(f"    - {itype}: {count} plots")
        
        # Print grading cost
        if layout['grading_cost']['estimated_cost_vnd'] > 0:
            cost = layout['grading_cost']
            print(f"\n  Grading cost estimate:")
            print(f"    - Cut: {cost['total_cut_m3']:,.0f} m³")
            print(f"    - Fill: {cost['total_fill_m3']:,.0f} m³")
            print(f"    - Total: {cost['estimated_cost_vnd']:,.0f} VND")
            print(f"    - Total: ${cost['estimated_cost_usd']:,.0f} USD")
        
        # Step 3: Export DXF
        print("\n" + "=" * 70)
        print("STEP 3: Exporting Color-Coded DXF")
        print("=" * 70)
        
        step3_start = time.time()
        
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        dxf_gen = DemoDXFGenerator(output_dir=str(output_dir))
        
        # Prepare layout for export
        export_layout = {
            'name': "Pilot Zone 1 Demo",
            'variant_id': "zone1_demo",
            'site_boundary': zone_data['zone']['geometry'],
            'buildings': layout['plots'],
            'roads': layout['roads'],
            'green_areas': layout['green_areas'],
            'fire_stations': layout['fire_stations'],
            'terrain_data': zone_data['zone'].get('terrain_data')
        }
        
        dxf_path = dxf_gen.generate(
            export_layout,
            filename="pilot_zone1_demo.dxf"
        )
        
        step3_time = time.time() - step3_start
        
        print(f"\n[OK] DXF exported in {step3_time:.1f}s")
        print(f"  File: {dxf_path}")
        
        # Check file size
        file_size = Path(dxf_path).stat().st_size / 1024  # KB
        print(f"  Size: {file_size:.0f} KB")
        
        # Total time
        total_time = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\n[OK] Complete pipeline executed successfully!")
        print(f"\nTiming breakdown:")
        print(f"  Zone processing: {step1_time:.1f}s")
        print(f"  Layout generation: {step2_time:.1f}s")
        print(f"  DXF export: {step3_time:.1f}s")
        print(f"  ─────────────────────────")
        print(f"  Total: {total_time:.1f}s")
        
        # Check if under 120s target
        if total_time < 120:
            print(f"\n[TARGET MET] {total_time:.1f}s < 120s")
        else:
            print(f"\n[WARNING] Over target: {total_time:.1f}s > 120s")
        
        print(f"\nOutput file: {dxf_path}")
        print("\nOpen in AutoCAD to view color-coded layout!")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pilot_demo()
    sys.exit(0 if success else 1)
