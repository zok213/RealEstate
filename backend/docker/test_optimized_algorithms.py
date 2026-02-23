"""
Test Script cho Optimized Subdivision Algorithms

Demo các thuật toán tối ưu hóa mới:
1. Advanced Plot Optimizer
2. Layout-Aware Subdivider
3. Enhanced Subdivision Solver
4. Access Optimizer
"""

import sys
import logging
from shapely.geometry import Polygon, box
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import optimizers
try:
    from core.optimization.advanced_plot_optimizer import (
        PlotOptimizer,
        PlotShapeMetrics
    )
    from core.optimization.layout_aware_subdivider import (
        LayoutAwareSubdivider,
        LayoutAnalyzer
    )
    from core.optimization.enhanced_subdivision_solver import (
        EnhancedSubdivisionSolver
    )
    from core.optimization.access_optimizer import (
        RoadNetworkDesigner,
        FrontageOptimizer
    )
    from core.optimization.optimized_pipeline_integrator import (
        OptimizedPipelineIntegrator,
        optimize_subdivision_pipeline
    )
    logger.info("✓ All optimizer modules imported successfully")
except ImportError as e:
    logger.error(f"✗ Failed to import: {e}")
    sys.exit(1)


def test_plot_shape_metrics():
    """Test 1: Plot shape quality metrics"""
    print("\n" + "="*60)
    print("TEST 1: Plot Shape Quality Metrics")
    print("="*60)
    
    # Create test plots
    # Perfect rectangle
    rect = box(0, 0, 20, 40)
    
    # Irregular polygon
    irregular = Polygon([
        (0, 0), (25, 5), (30, 20), (20, 35), (5, 30)
    ])
    
    # Narrow plot
    narrow = box(0, 0, 5, 50)
    
    plots = [
        ('Perfect Rectangle 20x40m', rect),
        ('Irregular Pentagon', irregular),
        ('Narrow 5x50m', narrow)
    ]
    
    for name, plot in plots:
        rect_score = PlotShapeMetrics.calculate_rectangularity(plot)
        aspect = PlotShapeMetrics.calculate_aspect_ratio(plot)
        compactness = PlotShapeMetrics.calculate_compactness(plot)
        quality = PlotShapeMetrics.calculate_quality_score(plot)
        
        print(f"\n{name}:")
        print(f"  Area: {plot.area:.0f} m²")
        print(f"  Rectangularity: {rect_score*100:.1f}%")
        print(f"  Aspect Ratio: {aspect:.2f}:1")
        print(f"  Compactness: {compactness*100:.1f}%")
        print(f"  Overall Quality: {quality:.1f}/100")


def test_layout_analysis():
    """Test 2: Block geometry analysis and pattern selection"""
    print("\n" + "="*60)
    print("TEST 2: Layout Pattern Selection")
    print("="*60)
    
    # Create test blocks
    blocks = [
        ('Square 100x100m', box(0, 0, 100, 100)),
        ('Elongated 200x50m', box(0, 0, 200, 50)),
        ('Very Long 400x40m', box(0, 0, 400, 40)),
        ('Irregular L-shape', Polygon([
            (0, 0), (100, 0), (100, 50), (50, 50), (50, 100), (0, 100)
        ]))
    ]
    
    for name, block in blocks:
        analysis = LayoutAnalyzer.analyze_block_geometry(block)
        
        print(f"\n{name}:")
        print(f"  Area: {block.area:.0f} m²")
        print(f"  Shape Type: {analysis['shape_type']}")
        if 'aspect_ratio' in analysis:
            print(f"  Aspect Ratio: {analysis['aspect_ratio']:.2f}")
        if 'rectangularity' in analysis:
            print(f"  Rectangularity: {analysis['rectangularity']*100:.1f}%")
        print(f"  Recommended Pattern: {analysis['recommended_pattern']}")


def test_enhanced_subdivision_solver():
    """Test 3: Enhanced CP solver with frontage ratio"""
    print("\n" + "="*60)
    print("TEST 3: Enhanced Subdivision Solver")
    print("="*60)
    
    # Test subdivision with frontage ratio
    total_length = 200.0  # 200m block edge
    min_width = 15.0
    max_width = 30.0
    target_width = 20.0
    target_frontage_ratio = 0.5  # Frontage is 50% of depth
    
    print(f"\nSubdividing {total_length}m with frontage ratio {target_frontage_ratio}")
    print(f"Target: {target_width}m frontage × {target_width/target_frontage_ratio}m depth")
    
    lots = EnhancedSubdivisionSolver.solve_subdivision_with_frontage(
        total_length=total_length,
        min_width=min_width,
        max_width=max_width,
        target_width=target_width,
        target_frontage_ratio=target_frontage_ratio,
        corner_premium=1.2,
        time_limit=5.0
    )
    
    print(f"\n✓ Generated {len(lots)} lots:")
    for i, lot in enumerate(lots):
        corner_mark = " [CORNER]" if lot['is_corner'] else ""
        print(
            f"  Lot {i+1}: {lot['width']:.1f}m × {lot['depth']:.1f}m = {lot['area']:.0f}m²"
            f"{corner_mark}"
        )
    
    # Statistics
    regular_lots = [l for l in lots if not l['is_corner']]
    corner_lots = [l for l in lots if l['is_corner']]
    
    if regular_lots:
        avg_regular_area = np.mean([l['area'] for l in regular_lots])
        print(f"\nRegular lots average: {avg_regular_area:.0f} m²")
    
    if corner_lots:
        avg_corner_area = np.mean([l['area'] for l in corner_lots])
        print(f"Corner lots average: {avg_corner_area:.0f} m² (premium)")


def test_fishbone_subdivider():
    """Test 4: Fishbone pattern subdivider"""
    print("\n" + "="*60)
    print("TEST 4: Fishbone Pattern Subdivision")
    print("="*60)
    
    # Create elongated block (ideal for fishbone)
    block = box(0, 0, 300, 80)
    
    print(f"Block: 300m × 80m = {block.area:.0f} m²")
    
    from core.optimization.layout_aware_subdivider import FishboneSubdivider
    
    lots = FishboneSubdivider.subdivide(
        block=block,
        zone_type='FACTORY',
        target_lot_width=20.0,
        target_lot_depth=30.0,
        spine_road_width=12.0
    )
    
    print(f"\n✓ Generated {len(lots)} lots in fishbone pattern")
    
    # Count by side
    north = sum(1 for l in lots if l.get('side') == 'north')
    south = sum(1 for l in lots if l.get('side') == 'south')
    
    print(f"  North side: {north} lots")
    print(f"  South side: {south} lots")
    
    total_area = sum(l['area'] for l in lots)
    coverage = total_area / block.area * 100
    print(f"  Total lot area: {total_area:.0f} m² ({coverage:.1f}% of block)")


def test_road_network_design():
    """Test 5: Road network design"""
    print("\n" + "="*60)
    print("TEST 5: Road Network Design")
    print("="*60)
    
    # Create site boundary
    site = box(0, 0, 500, 400)
    
    print(f"Site: 500m × 400m = {site.area/10000:.1f} hectares")
    
    designer = RoadNetworkDesigner(
        main_road_width=12.0,
        internal_road_width=8.0
    )
    
    # Test grid pattern
    roads = designer.design_skeleton_network(
        land_boundary=site,
        num_branches=3,
        pattern='grid'
    )
    
    print(f"\n✓ Created {len(roads)} road segments")
    
    main_roads = [r for r in roads if r['type'] == 'main']
    connectors = [r for r in roads if r['type'] == 'connector']
    
    print(f"  Main roads: {len(main_roads)}")
    print(f"  Connectors: {len(connectors)}")
    
    total_length = sum(r['length'] for r in roads)
    print(f"  Total length: {total_length:.0f}m ({total_length/1000:.2f}km)")


def test_integrated_pipeline():
    """Test 6: Full integrated pipeline"""
    print("\n" + "="*60)
    print("TEST 6: Integrated Optimization Pipeline")
    print("="*60)
    
    # Create test site
    site = box(0, 0, 400, 300)
    
    # Create test blocks (simulate grid result)
    blocks = [
        {'geometry': box(10, 10, 190, 140), 'zone': 'FACTORY'},
        {'geometry': box(210, 10, 390, 140), 'zone': 'FACTORY'},
        {'geometry': box(10, 160, 190, 290), 'zone': 'WAREHOUSE'},
        {'geometry': box(210, 160, 390, 290), 'zone': 'WAREHOUSE'}
    ]
    
    print(f"Site: 400m × 300m = {site.area/10000:.1f} hectares")
    print(f"Input: {len(blocks)} blocks")
    
    # Run optimization
    config = {
        'use_advanced_optimization': True,
        'num_road_branches': 2,
        'min_plot_quality': 60.0
    }
    
    optimized_blocks, roads, metrics = optimize_subdivision_pipeline(
        blocks=blocks,
        land_boundary=site,
        config=config
    )
    
    print(f"\n✓ Optimization complete!")
    print(f"\nResults:")
    print(f"  Total Lots: {metrics['total_lots']}")
    print(f"  Average Lot Area: {metrics['avg_lot_area']:.0f} m²")
    print(f"  Average Quality Score: {metrics['avg_quality_score']:.1f}/100")
    print(f"  High Quality Lots: {metrics['high_quality_lots']} ({metrics['high_quality_rate']*100:.1f}%)")
    print(f"  Average Rectangularity: {metrics['avg_rectangularity']*100:.1f}%")
    print(f"  Lots with Road Access: {metrics['lots_with_access']} ({metrics['access_rate']*100:.1f}%)")
    print(f"  Total Road Length: {metrics['total_road_length']:.0f}m")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("OPTIMIZED SUBDIVISION ALGORITHMS - TEST SUITE")
    print("="*60)
    
    try:
        test_plot_shape_metrics()
        test_layout_analysis()
        test_enhanced_subdivision_solver()
        test_fishbone_subdivider()
        test_road_network_design()
        test_integrated_pipeline()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print("\n" + "="*60)
        print(f"✗ TEST FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
