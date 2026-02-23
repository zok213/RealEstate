"""
Test Optimized Subdivision Algorithms with Real DXF Data

Script này test các thuật toán tối ưu hóa mới với dữ liệu thực tế từ file DXF/DWG
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend' / 'docker'
sys.path.insert(0, str(backend_path))

import logging
import json
from shapely.geometry import Polygon, mapping
from shapely.ops import unary_union

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("=" * 70)
print("TEST OPTIMIZED ALGORITHMS WITH REAL DXF DATA")
print("=" * 70)

# Import DXF parsing
try:
    import ezdxf
    logger.info("✓ ezdxf imported")
except ImportError:
    logger.error("✗ ezdxf not found. Install: pip install ezdxf")
    sys.exit(1)

# Import optimization algorithms
try:
    from core.optimization.advanced_plot_optimizer import (
        PlotOptimizer,
        PlotShapeMetrics,
        apply_plot_optimization
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
    logger.info("✓ All optimization algorithms imported")
except ImportError as e:
    logger.error(f"✗ Failed to import algorithms: {e}")
    sys.exit(1)


def extract_boundary_from_dxf(dxf_file):
    """Extract boundary polygon from DXF file"""
    logger.info(f"Reading DXF file: {dxf_file}")
    
    try:
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()
        
        # Get all polylines
        polylines = []
        for entity in msp:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = list(entity.get_points())
                if len(points) > 2:
                    # Convert to 2D if needed
                    points_2d = [(p[0], p[1]) for p in points]
                    polylines.append(points_2d)
        
        logger.info(f"Found {len(polylines)} polylines")
        
        if not polylines:
            logger.error("No polylines found in DXF")
            return None
        
        # Find largest polyline by area
        def calc_area(points):
            if len(points) < 3:
                return 0
            try:
                poly = Polygon(points)
                return poly.area
            except:
                return 0
        
        largest = max(polylines, key=calc_area)
        boundary = Polygon(largest)
        
        if not boundary.is_valid:
            logger.warning("Invalid boundary, attempting to fix...")
            boundary = boundary.buffer(0)
        
        logger.info(f"✓ Extracted boundary: {boundary.area:.0f} m² ({boundary.area/10000:.2f} ha)")
        
        return boundary
        
    except Exception as e:
        logger.error(f"Error reading DXF: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_grid_blocks(boundary, num_blocks_x=2, num_blocks_y=2, road_width=12.0):
    """Create simple grid blocks for testing"""
    logger.info(f"Creating {num_blocks_x}x{num_blocks_y} grid blocks")
    
    bounds = boundary.bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    
    block_width = (width - (num_blocks_x + 1) * road_width) / num_blocks_x
    block_height = (height - (num_blocks_y + 1) * road_width) / num_blocks_y
    
    blocks = []
    block_id = 1
    
    for i in range(num_blocks_x):
        for j in range(num_blocks_y):
            x_start = minx + road_width + i * (block_width + road_width)
            y_start = miny + road_width + j * (block_height + road_width)
            
            x_end = x_start + block_width
            y_end = y_start + block_height
            
            block_poly = Polygon([
                (x_start, y_start),
                (x_end, y_start),
                (x_end, y_end),
                (x_start, y_end)
            ])
            
            # Clip to boundary
            clipped = block_poly.intersection(boundary)
            
            if not clipped.is_empty and clipped.area > 500:
                if clipped.geom_type == 'Polygon':
                    blocks.append({
                        'id': block_id,
                        'geometry': clipped,
                        'zone': 'FACTORY' if (i + j) % 2 == 0 else 'WAREHOUSE'
                    })
                    block_id += 1
    
    logger.info(f"✓ Created {len(blocks)} blocks")
    return blocks


def test_with_pilot_dxf():
    """Test with Pilot DXF file"""
    print("\n" + "=" * 70)
    print("TEST 1: Pilot Project DXF (Real Industrial Estate)")
    print("=" * 70)
    
    dxf_file = Path(__file__).parent / 'Pilot_Existing Topo _ Boundary.dxf'
    
    if not dxf_file.exists():
        logger.error(f"File not found: {dxf_file}")
        return False
    
    # Extract boundary
    boundary = extract_boundary_from_dxf(str(dxf_file))
    
    if boundary is None:
        return False
    
    print(f"\n📐 Site Information:")
    print(f"  Area: {boundary.area/10000:.2f} hectares ({boundary.area:.0f} m²)")
    print(f"  Bounds: {boundary.bounds}")
    
    # Create blocks
    blocks = create_grid_blocks(boundary, num_blocks_x=3, num_blocks_y=2)
    
    print(f"\n🏗️  Created {len(blocks)} blocks for subdivision")
    
    # Run optimization
    print(f"\n🚀 Running Optimized Subdivision Pipeline...")
    print("-" * 70)
    
    config = {
        'use_advanced_optimization': True,
        'num_road_branches': 3,
        'min_plot_quality': 60.0
    }
    
    try:
        optimized_blocks, roads, metrics = optimize_subdivision_pipeline(
            blocks=blocks,
            land_boundary=boundary,
            config=config
        )
        
        print("\n" + "=" * 70)
        print("📊 OPTIMIZATION RESULTS")
        print("=" * 70)
        
        print(f"\n🏘️  Lots Generated:")
        print(f"  Total Lots: {metrics['total_lots']}")
        print(f"  Total Lot Area: {metrics['total_lot_area']:.0f} m² ({metrics['total_lot_area']/10000:.2f} ha)")
        print(f"  Average Lot Size: {metrics['avg_lot_area']:.0f} m²")
        
        print(f"\n✨ Quality Metrics:")
        print(f"  Average Quality Score: {metrics['avg_quality_score']:.1f}/100")
        print(f"  High Quality Lots: {metrics['high_quality_lots']} ({metrics['high_quality_rate']*100:.1f}%)")
        print(f"  Average Rectangularity: {metrics['avg_rectangularity']*100:.1f}%")
        print(f"  Average Aspect Ratio: {metrics['avg_aspect_ratio']:.2f}:1")
        
        print(f"\n🛣️  Road Network:")
        print(f"  Road Segments: {metrics['road_segments']}")
        print(f"  Total Road Length: {metrics['total_road_length']:.0f}m ({metrics['total_road_length']/1000:.2f}km)")
        
        print(f"\n🚗 Access:")
        print(f"  Lots with Road Access: {metrics['lots_with_access']} ({metrics['access_rate']*100:.1f}%)")
        
        # Export results
        export_results(optimized_blocks, roads, boundary, 'pilot_optimized_result')
        
        return True
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_belair_dxf():
    """Test with Bel Air DXF file"""
    print("\n" + "=" * 70)
    print("TEST 2: Bel Air Lot Plan DXF")
    print("=" * 70)
    
    dxf_file = Path(__file__).parent.parent / 'examples' / 'Lot Plan Bel air Technical Description.dxf'
    
    if not dxf_file.exists():
        logger.warning(f"File not found: {dxf_file}")
        return False
    
    boundary = extract_boundary_from_dxf(str(dxf_file))
    
    if boundary is None:
        return False
    
    print(f"\n📐 Site Information:")
    print(f"  Area: {boundary.area/10000:.2f} hectares ({boundary.area:.0f} m²)")
    
    # Create blocks
    blocks = create_grid_blocks(boundary, num_blocks_x=2, num_blocks_y=2)
    
    # Run optimization
    config = {
        'use_advanced_optimization': True,
        'num_road_branches': 2,
        'min_plot_quality': 65.0
    }
    
    try:
        optimized_blocks, roads, metrics = optimize_subdivision_pipeline(
            blocks=blocks,
            land_boundary=boundary,
            config=config
        )
        
        print(f"\n📊 Results: {metrics['total_lots']} lots, Quality: {metrics['avg_quality_score']:.1f}/100")
        
        export_results(optimized_blocks, roads, boundary, 'belair_optimized_result')
        
        return True
        
    except Exception as e:
        logger.error(f"Optimization failed: {e}")
        return False


def export_results(blocks, roads, boundary, filename):
    """Export results to GeoJSON"""
    output_dir = Path(__file__).parent / 'output'
    output_dir.mkdir(exist_ok=True)
    
    # Prepare GeoJSON
    features = []
    
    # Add boundary
    features.append({
        'type': 'Feature',
        'geometry': mapping(boundary),
        'properties': {
            'type': 'boundary',
            'area': boundary.area
        }
    })
    
    # Add roads
    for road in roads:
        features.append({
            'type': 'Feature',
            'geometry': mapping(road['geometry']),
            'properties': {
                'type': 'road',
                'road_type': road.get('type', 'unknown'),
                'width': road.get('width', 0),
                'length': road.get('length', 0)
            }
        })
    
    # Add lots
    for block in blocks:
        for lot in block.get('lots', []):
            quality = PlotShapeMetrics.calculate_quality_score(lot['geometry'])
            
            features.append({
                'type': 'Feature',
                'geometry': mapping(lot['geometry']),
                'properties': {
                    'type': 'lot',
                    'zone': lot.get('zone', 'unknown'),
                    'area': lot['geometry'].area,
                    'quality_score': round(quality, 1),
                    'has_access': lot.get('has_access', False),
                    'road_frontage': lot.get('road_frontage', 0)
                }
            })
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    output_file = output_dir / f'{filename}.geojson'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Exported to: {output_file}")
    print(f"\n💾 Results saved to: {output_file}")


def main():
    """Run all tests"""
    
    results = []
    
    # Test 1: Pilot DXF
    success = test_with_pilot_dxf()
    results.append(('Pilot Project', success))
    
    # Test 2: Bel Air DXF
    success = test_with_belair_dxf()
    results.append(('Bel Air', success))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {name}: {status}")
    
    total_success = sum(1 for _, s in results if s)
    print(f"\n  Total: {total_success}/{len(results)} tests passed")
    
    return total_success == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
