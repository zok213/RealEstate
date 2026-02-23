"""
Simple Test - Optimized Algorithms with Real DXF

Test đơn giản hơn với pilot file, không dùng fishbone pattern
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend' / 'docker'
sys.path.insert(0, str(backend_path))

import logging
import json
from shapely.geometry import Polygon, box, mapping

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 70)
print("SIMPLE TEST: Optimized Algorithms with Pilot DXF")
print("=" * 70)

# Import modules
try:
    import ezdxf
    from core.optimization.advanced_plot_optimizer import PlotShapeMetrics
    from core.optimization.simple_subdivider import subdivide_block_simple
    from core.optimization.advanced_plot_optimizer import PlotOptimizer
    logger.info("✓ Modules imported")
except ImportError as e:
    logger.error(f"Import failed: {e}")
    sys.exit(1)


def extract_boundary_from_dxf(dxf_file):
    """Extract boundary from DXF"""
    logger.info(f"Reading: {dxf_file}")
    
    doc = ezdxf.readfile(dxf_file)
    msp = doc.modelspace()
    
    polylines = []
    for entity in msp:
        if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) > 2:
                polylines.append(points)
    
    logger.info(f"Found {len(polylines)} polylines")
    
    # Find largest by area
    def calc_area(pts):
        try:
            return Polygon(pts).area
        except:
            return 0
    
    largest = max(polylines, key=calc_area)
    boundary = Polygon(largest)
    
    if not boundary.is_valid:
        boundary = boundary.buffer(0)
    
    logger.info(f"Boundary: {boundary.area/10000:.1f} ha")
    return boundary


def main():
    # Read DXF
    dxf_file = Path(__file__).parent / 'Pilot_Existing Topo _ Boundary.dxf'
    
    if not dxf_file.exists():
        logger.error(f"File not found: {dxf_file}")
        return False
    
    boundary = extract_boundary_from_dxf(str(dxf_file))
    
    print(f"\n📐 Site: {boundary.area/10000:.1f} hectares")
    
    # Create ONE test block (simplified)
    bounds = boundary.bounds
    minx, miny, maxx, maxy = bounds
    
    # Create a single block in the center
    width = maxx - minx
    height = maxy - miny
    
    block_geom = box(
        minx + width * 0.25,
        miny + height * 0.25,
        minx + width * 0.75,
        miny + height * 0.75
    )
    
    # Clip to boundary
    block_geom = block_geom.intersection(boundary)
    
    print(f"🏗️  Test block: {block_geom.area:.0f} m²")
    
    # Test 1: Simple subdivision
    print("\n" + "=" * 70)
    print("TEST 1: Simple Grid Subdivision")
    print("=" * 70)
    
    lots = subdivide_block_simple(
        block=block_geom,
        zone_type='FACTORY',
        target_lot_width=20.0,
        target_lot_depth=40.0
    )
    
    print(f"✓ Generated {len(lots)} lots")
    
    if lots:
        avg_area = sum(l['geometry'].area for l in lots) / len(lots)
        print(f"  Average lot size: {avg_area:.0f} m²")
    
    # Test 2: Plot optimization
    print("\n" + "=" * 70)
    print("TEST 2: Advanced Plot Optimization")
    print("=" * 70)
    
    optimizer = PlotOptimizer(
        min_plot_area=500.0,
        min_quality_score=60.0,
        target_aspect_ratio=2.0
    )
    
    optimized_lots = optimizer.optimize_plots(lots, block_geom)
    
    print(f"✓ Optimized: {len(lots)} → {len(optimized_lots)} lots")
    
    # Calculate metrics
    if optimized_lots:
        scores = [
            PlotShapeMetrics.calculate_quality_score(l['geometry'])
            for l in optimized_lots
        ]
        avg_quality = sum(scores) / len(scores)
        
        rectangularities = [
            PlotShapeMetrics.calculate_rectangularity(l['geometry'])
            for l in optimized_lots
        ]
        avg_rect = sum(rectangularities) / len(rectangularities)
        
        print(f"\n📊 Quality Metrics:")
        print(f"  Average Quality Score: {avg_quality:.1f}/100")
        print(f"  Average Rectangularity: {avg_rect*100:.1f}%")
        print(f"  High Quality Lots (>80): {sum(1 for s in scores if s > 80)}/{len(scores)}")
    
    # Export results
    print("\n💾 Exporting results...")
    
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    features = []
    
    # Add boundary
    features.append({
        'type': 'Feature',
        'geometry': mapping(boundary),
        'properties': {'type': 'boundary'}
    })
    
    # Add block
    features.append({
        'type': 'Feature',
        'geometry': mapping(block_geom),
        'properties': {'type': 'block'}
    })
    
    # Add lots
    for lot in optimized_lots:
        quality = PlotShapeMetrics.calculate_quality_score(lot['geometry'])
        features.append({
            'type': 'Feature',
            'geometry': mapping(lot['geometry']),
            'properties': {
                'type': 'lot',
                'area': lot['geometry'].area,
                'quality': round(quality, 1)
            }
        })
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    output_file = output_dir / 'simple_test_result.geojson'
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✓ Saved to: {output_file}")
    
    print("\n" + "=" * 70)
    print("✓ TEST COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
