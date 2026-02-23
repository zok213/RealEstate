"""
Test Full-Site Analysis System

Tests the complete full-site processing pipeline:
1. Extract boundary and topography from full Pilot file (191.42 ha)
2. Identify buildable zones
3. Generate 3 development scenarios
4. Export DXF for best scenario
"""

import sys
import os
from pathlib import Path

# Add backend to path
project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

import logging
import time

# Fix Windows console encoding
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


def test_full_site_analysis():
    """Test complete full-site analysis pipeline"""
    
    print("=" * 70)
    print("FULL-SITE PILOT ANALYSIS TEST")
    print("=" * 70)
    
    # File path
    pilot_file = Path(__file__).parent / "Pilot_Existing Topo _ Boundary.dxf"
    
    if not pilot_file.exists():
        print(f"[ERROR] Pilot file not found: {pilot_file}")
        return False
    
    print(f"\nUsing file: {pilot_file}")
    
    start_time = time.time()
    
    try:
        # Import modules
        from demo.pilot_zone_processor import PilotZoneProcessor
        from demo.full_site_analyzer import FullSiteAnalyzer
        from demo.scenario_generator import ScenarioGenerator
        from demo.demo_dxf_generator import DemoDXFGenerator
        
        # ====================================================================
        # STEP 1: Extract Site Boundary
        # ====================================================================
        print("\n" + "=" * 70)
        print("STEP 1: Extracting Site Boundary")
        print("=" * 70)
        
        step1_start = time.time()
        
        processor = PilotZoneProcessor()
        site_boundary = processor.extract_pilot_boundary(str(pilot_file))
        
        site_area_ha = site_boundary.area / 10000
        
        step1_time = time.time() - step1_start
        
        print(f"\n[OK] Site boundary extracted in {step1_time:.1f}s")
        print(f"  Total area: {site_area_ha:.2f} ha")
        print(f"  Bounds: {site_boundary.bounds}")
        
        # ====================================================================
        # STEP 2: Analyze Full Site
        # ====================================================================
        print("\n" + "=" * 70)
        print("STEP 2: Analyzing Full Site Terrain")
        print("=" * 70)
        
        step2_start = time.time()
        
        analyzer = FullSiteAnalyzer(grid_resolution=20.0)
        site_analysis = analyzer.analyze_entire_site(
            str(pilot_file),
            site_boundary
        )
        
        step2_time = time.time() - step2_start
        
        print(f"\n[OK] Site analysis completed in {step2_time:.1f}s")
        print(f"  Buildable zones found: {len(site_analysis['buildable_zones'])}")
        print(f"  Total buildable area: {site_analysis['statistics']['total_buildable_area_ha']:.1f} ha")
        print(f"  Buildable percentage: {site_analysis['statistics']['buildable_percentage']:.1f}%")
        print(f"  Optimal zones: {len(site_analysis['optimal_zones'])}")
        
        # Show top 3 buildable zones
        print(f"\n  Top 3 Buildable Zones:")
        for i, zone in enumerate(site_analysis['buildable_zones'][:3], 1):
            print(f"    {i}. Zone {zone['id']}: {zone['area_ha']:.1f} ha, "
                  f"slope {zone['metrics']['avg_slope']:.1f}%, "
                  f"score {zone['scores']['total']:.1f}/100")
        
        # ====================================================================
        # STEP 3: Generate Scenarios
        # ====================================================================
        print("\n" + "=" * 70)
        print("STEP 3: Generating Development Scenarios")
        print("=" * 70)
        
        step3_start = time.time()
        
        scenario_gen = ScenarioGenerator()
        scenarios = scenario_gen.generate_scenarios(
            site_analysis,
            target_plot_count=200
        )
        
        step3_time = time.time() - step3_start
        
        print(f"\n[OK] Generated {len(scenarios)} scenarios in {step3_time:.1f}s")
        
        # Display scenario comparison
        print(f"\n  Scenario Comparison:")
        print(f"  {'Scenario':<20} {'Plots':<10} {'Area (ha)':<12} {'Cost (USD)':<15} {'Strategy':<20}")
        print(f"  {'-'*80}")
        
        for scenario in scenarios:
            print(f"  {scenario['name']:<20} "
                  f"{scenario['metrics']['plot_count']:<10} "
                  f"{scenario['metrics']['development_area_ha']:<12.1f} "
                  f"${scenario['grading_cost']['estimated_cost_usd']:>13,.0f} "
                  f"{scenario['strategy']:<20}")
        
        # Show detailed metrics for each scenario
        for scenario in scenarios:
            print(f"\n  --- Scenario {scenario['scenario_id']}: {scenario['name']} ---")
            print(f"      Description: {scenario['description']}")
            print(f"      Zones selected: {len(scenario['selected_zones'])}")
            print(f"      Development area: {scenario['metrics']['development_area_ha']:.1f} ha")
            print(f"      Plot count: {scenario['metrics']['plot_count']}")
            print(f"      Fire stations: {scenario['metrics']['fire_station_count']}")
            print(f"      Green areas: {scenario['metrics']['green_area_count']}")
            print(f"      Land use:")
            print(f"        - Plots: {scenario['metrics']['land_use']['plot_ratio']*100:.1f}%")
            print(f"        - Roads: {scenario['metrics']['land_use']['road_ratio']*100:.1f}%")
            print(f"        - Green: {scenario['metrics']['land_use']['green_ratio']*100:.1f}%")
            print(f"      Industry distribution:")
            for itype, count in scenario['metrics']['industry_distribution'].items():
                print(f"        - {itype}: {count} plots")
            print(f"      Generation time: {scenario['generation_time_s']:.1f}s")
        
        # ====================================================================
        # STEP 4: Export Best Scenario to DXF
        # ====================================================================
        print("\n" + "=" * 70)
        print("STEP 4: Exporting Best Scenario to DXF")
        print("=" * 70)
        
        step4_start = time.time()
        
        # Select balanced scenario (C)
        best_scenario = scenarios[2]  # Scenario C
        
        print(f"\n  Selected: Scenario {best_scenario['scenario_id']} - {best_scenario['name']}")
        
        # Combine zone geometries
        from shapely.ops import unary_union
        zone_polygons = [z['geometry'] for z in best_scenario['selected_zones']]
        combined_boundary = unary_union(zone_polygons)
        
        # Create output directory
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Prepare export layout
        export_layout = {
            'name': f"Pilot Full Site - {best_scenario['name']}",
            'variant_id': f"fullsite_scenario_{best_scenario['scenario_id'].lower()}",
            'site_boundary': combined_boundary,
            'buildings': best_scenario['layout']['plots'],
            'roads': best_scenario['layout']['roads'],
            'green_areas': best_scenario['layout']['green_areas'],
            'fire_stations': best_scenario['layout']['fire_stations']
        }
        
        # Generate DXF
        dxf_gen = DemoDXFGenerator(output_dir=str(output_dir))
        dxf_path = dxf_gen.generate(
            export_layout,
            filename=f"pilot_fullsite_scenario_{best_scenario['scenario_id']}.dxf"
        )
        
        step4_time = time.time() - step4_start
        
        print(f"\n[OK] DXF exported in {step4_time:.1f}s")
        print(f"  File: {dxf_path}")
        
        # Check file size
        file_size = Path(dxf_path).stat().st_size / 1024  # KB
        print(f"  Size: {file_size:.0f} KB")
        
        # ====================================================================
        # SUMMARY
        # ====================================================================
        total_time = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"\n[OK] Complete full-site analysis executed successfully!")
        print(f"\nTiming breakdown:")
        print(f"  Site boundary extraction: {step1_time:.1f}s")
        print(f"  Full site analysis: {step2_time:.1f}s")
        print(f"  Scenario generation: {step3_time:.1f}s")
        print(f"  DXF export: {step4_time:.1f}s")
        print(f"  -------------------------")
        print(f"  Total: {total_time:.1f}s")
        
        # Check if under 120s target
        if total_time < 120:
            print(f"\n[TARGET MET] {total_time:.1f}s < 120s")
        else:
            print(f"\n[WARNING] Over target: {total_time:.1f}s > 120s")
        
        print(f"\nResults:")
        print(f"  - Site area: {site_area_ha:.1f} ha")
        print(f"  - Buildable zones: {len(site_analysis['buildable_zones'])}")
        print(f"  - Scenarios generated: {len(scenarios)}")
        print(f"  - Best scenario: {best_scenario['name']}")
        print(f"  - Plots: {best_scenario['metrics']['plot_count']}")
        print(f"  - Estimated cost: ${best_scenario['grading_cost']['estimated_cost_usd']:,.0f}")
        print(f"\nOutput file: {dxf_path}")
        print("\nOpen in AutoCAD to view full-site layout!")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_full_site_analysis()
    sys.exit(0 if success else 1)
