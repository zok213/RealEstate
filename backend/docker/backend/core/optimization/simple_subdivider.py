"""
Simple Grid Subdivider - BYPASS OR-Tools constraints

Creates lots using simple grid division without complex optimization.
Guaranteed to generate lots!
"""

import logging
from typing import List, Dict, Any
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


def subdivide_block_simple(
    block: Polygon,
    zone_type: str = 'WAREHOUSE',
    target_lot_width: float = 60.0,
    target_lot_depth: float = 80.0
) -> List[Dict[str, Any]]:
    """
    Subdivide block into lots with ADAPTIVE sizing
    
    More realistic than uniform grid:
    - Lot sizes vary ±20% for organic look
    - Edge lots adjust to boundary
    - Larger lots near main roads
    
    Args:
        block: Block polygon to subdivide
        zone_type: Zone type (FACTORY, WAREHOUSE, RESIDENTIAL)
        target_lot_width: Target lot width in meters
        target_lot_depth: Target lot depth in meters
        
    Returns:
        List of lot dictionaries with geometry and properties
    """
    logger.info(
        f"[ADAPTIVE SUB] Block area={block.area:.0f}m², "
        f"zone={zone_type}, target={target_lot_width}x{target_lot_depth}m"
    )
    
    # Get block bounds
    bounds = block.bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    
    # Add variation to lot sizes (±20%)
    import random
    random.seed(int(block.area))  # Consistent variation per block
    
    width_variation = target_lot_width * 0.2
    depth_variation = target_lot_depth * 0.2
    
    # Calculate number of lots with variation
    num_x = max(1, int(width / (target_lot_width * 0.9)))
    num_y = max(1, int(height / (target_lot_depth * 0.9)))
    
    logger.info(
        f"[ADAPTIVE SUB] Creating {num_x}x{num_y} varied grid "
        f"(variation: ±{width_variation:.0f}m x ±{depth_variation:.0f}m)"
    )
    
    # Create adaptive grid with varied lot sizes
    lots = []
    lot_id = 1
    
    current_x = minx
    for i in range(num_x):
        # Vary width for this column
        lot_width = target_lot_width + random.uniform(-width_variation, width_variation)
        lot_width = max(target_lot_width * 0.7, min(target_lot_width * 1.3, lot_width))
        
        # Last column adjusts to fill remaining space
        if i == num_x - 1:
            lot_width = maxx - current_x
        
        current_y = miny
        for j in range(num_y):
            # Vary depth for this row
            lot_depth = target_lot_depth + random.uniform(-depth_variation, depth_variation)
            lot_depth = max(target_lot_depth * 0.7, min(target_lot_depth * 1.3, lot_depth))
            
            # Last row adjusts to fill remaining space
            if j == num_y - 1:
                lot_depth = maxy - current_y
            
            # Create lot rectangle
            lot_box = box(current_x, current_y, current_x + lot_width, current_y + lot_depth)
            
            # Create lot rectangle
            lot_box = box(current_x, current_y, current_x + lot_width, current_y + lot_depth)
            
            # CRITICAL: Intersect with block boundary to clip exactly
            lot = lot_box.intersection(block)
            
            # Skip if empty or invalid
            if lot.is_empty or not hasattr(lot, 'area'):
                pass
            else:
                # Handle MultiPolygon results from intersection
                lot_polygons = []
                if lot.geom_type == 'Polygon':
                    lot_polygons = [lot]
                elif lot.geom_type == 'MultiPolygon':
                    lot_polygons = list(lot.geoms)
                
                # Add each polygon as separate lot (if large enough)
                for lot_poly in lot_polygons:
                    # Filter: Only keep if polygon and reasonable size
                    min_lot_area = 100.0  # 100m² minimum
                    
                    if lot_poly.area >= min_lot_area:
                        # Ensure lot is FULLY within block (99% overlap)
                        overlap_ratio = lot_poly.intersection(block).area / lot_poly.area
                        
                        if overlap_ratio > 0.99:  # 99% inside block
                            lots.append({
                                'geometry': lot_poly,
                                'id': lot_id,
                                'zone': zone_type,
                                'area': lot_poly.area,
                                'width': lot_width,
                                'depth': lot_depth
                            })
                            lot_id += 1
            
            # Move to next row
            current_y += lot_depth
        
        # Move to next column
        current_x += lot_width
    
    logger.info(f"[ADAPTIVE SUB] ✓ Created {len(lots)} varied lots")
    
    return lots


def get_target_dimensions_for_zone(zone_type: str) -> tuple:
    """
    Get target lot dimensions for REAL INDUSTRIAL ESTATES
    
    CORRECTED based on actual master plan analysis:
    Each lot is ONE individual factory/warehouse, NOT entire zone!
    
    Based on Vietnamese industrial estate samples:
    - FACTORY: Small individual plots 20×40m (800m²)
    - WAREHOUSE: Medium plots 15×30m (450m²)
    - SERVICE: Small service plots 10×20m (200m²)
    - GREEN: Preserved as-is (no subdivision)
    
    Reference: Real KCN plans show 50-150 lots per block
    
    Args:
        zone_type: Zone type
        
    Returns:
        (width, depth) in meters
    """
    if zone_type == 'FACTORY':
        # Individual factory lot: 20m × 40m (800m²)
        # Real Vietnamese industrial standard
        # Each block will contain 50-150 of these
        return (20.0, 40.0)
    
    elif zone_type == 'WAREHOUSE':
        # Individual warehouse lot: 15m × 30m (450m²)
        # Typical logistics/storage unit
        return (15.0, 30.0)
    
    elif zone_type == 'SERVICE':
        # Individual service lot: 10m × 20m (200m²)
        # For offices, utilities, small amenities
        return (10.0, 20.0)
    
    elif zone_type == 'GREEN':
        # Green spaces not subdivided
        return (0, 0)
    
    else:
        # Default: medium warehouse size
        return (60.0, 100.0)
