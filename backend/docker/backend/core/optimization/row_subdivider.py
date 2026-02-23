"""
Row-Based Lot Subdivider - Match Reference Design

Creates neat rows of lots like professional master plans:
- Lots aligned in straight rows
- Internal access roads between rows
- Lots face roads on one side
- Clean, organized appearance

Matches real Vietnamese industrial estate layouts
"""

import logging
from typing import List, Dict, Any
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


def subdivide_block_rows(
    block: Polygon,
    zone_type: str = 'FACTORY',
    target_lot_width: float = 20.0,
    target_lot_depth: float = 40.0,
    internal_road_width: float = 6.0
) -> List[Dict[str, Any]]:
    """
    Subdivide block into ROWS of lots with internal roads
    
    Creates professional layout:
    - Rows of lots separated by internal roads
    - Lots uniform within each row
    - All lots face a road
    - Clean rectangular arrangement
    
    Args:
        block: Block polygon to subdivide
        zone_type: Zone type (FACTORY, WAREHOUSE, SERVICE)
        target_lot_width: Target lot width in meters
        target_lot_depth: Target lot depth in meters
        internal_road_width: Width of internal access roads
        
    Returns:
        List of lot dictionaries with geometry and properties
    """
    logger.info(
        f"[ROW SUB] Block area={block.area:.0f}m², zone={zone_type}, "
        f"lot={target_lot_width}x{target_lot_depth}m"
    )
    
    # Get block bounds
    bounds = block.bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    
    # Determine row orientation (rows along longer dimension)
    if width > height:
        # Horizontal rows (lots stacked vertically)
        row_direction = 'horizontal'
        row_count = max(1, int(height / (2 * target_lot_depth + internal_road_width)))
        lots_per_row = max(1, int(width / target_lot_width))
    else:
        # Vertical rows (lots stacked horizontally)
        row_direction = 'vertical'
        row_count = max(1, int(width / (2 * target_lot_depth + internal_road_width)))
        lots_per_row = max(1, int(height / target_lot_width))
    
    logger.info(
        f"[ROW SUB] Direction={row_direction}, "
        f"{row_count} rows × {lots_per_row} lots/row"
    )
    
    lots = []
    lot_id = 1
    
    if row_direction == 'horizontal':
        # ========================================
        # HORIZONTAL ROWS (north-south stacking)
        # ========================================
        # Each row has 2 columns of lots back-to-back with road between next row
        
        row_height = height / row_count
        
        for row_idx in range(row_count):
            row_y_start = miny + row_idx * row_height
            row_y_end = miny + (row_idx + 1) * row_height
            
            # Split row into: lots (north) + road + lots (south)
            # If only 1 row, use full height for lots
            if row_count == 1:
                lot_depth_actual = row_height / 2
                road_y = row_y_start + lot_depth_actual
                
                # North lots
                lots.extend(_create_row_lots(
                    minx, row_y_start, maxx, road_y,
                    target_lot_width, block, lot_id, zone_type, 'N'
                ))
                lot_id += lots_per_row
                
                # South lots
                lots.extend(_create_row_lots(
                    minx, road_y, maxx, row_y_end,
                    target_lot_width, block, lot_id, zone_type, 'S'
                ))
                lot_id += lots_per_row
            else:
                # Multiple rows: alternate lot-road-lot pattern
                if row_idx == 0:
                    # First row: lots + road
                    lot_depth_actual = row_height - internal_road_width / 2
                    lots.extend(_create_row_lots(
                        minx, row_y_start, maxx, row_y_start + lot_depth_actual,
                        target_lot_width, block, lot_id, zone_type, 'N'
                    ))
                    lot_id += lots_per_row
                elif row_idx == row_count - 1:
                    # Last row: road + lots
                    lot_y_start = row_y_start + internal_road_width / 2
                    lots.extend(_create_row_lots(
                        minx, lot_y_start, maxx, row_y_end,
                        target_lot_width, block, lot_id, zone_type, 'S'
                    ))
                    lot_id += lots_per_row
                else:
                    # Middle rows: road + lots + road
                    road_top = internal_road_width / 2
                    road_bottom = internal_road_width / 2
                    lot_depth_actual = row_height - road_top - road_bottom
                    
                    lot_y_start = row_y_start + road_top
                    lot_y_end = row_y_end - road_bottom
                    
                    # Single row of lots
                    lots.extend(_create_row_lots(
                        minx, lot_y_start, maxx, lot_y_end,
                        target_lot_width, block, lot_id, zone_type, 'M'
                    ))
                    lot_id += lots_per_row
    
    else:
        # ========================================
        # VERTICAL ROWS (east-west stacking)
        # ========================================
        row_width = width / row_count
        
        for row_idx in range(row_count):
            row_x_start = minx + row_idx * row_width
            row_x_end = minx + (row_idx + 1) * row_width
            
            if row_count == 1:
                lot_depth_actual = row_width / 2
                road_x = row_x_start + lot_depth_actual
                
                # West lots
                lots.extend(_create_column_lots(
                    row_x_start, miny, road_x, maxy,
                    target_lot_width, block, lot_id, zone_type, 'W'
                ))
                lot_id += lots_per_row
                
                # East lots
                lots.extend(_create_column_lots(
                    road_x, miny, row_x_end, maxy,
                    target_lot_width, block, lot_id, zone_type, 'E'
                ))
                lot_id += lots_per_row
            else:
                if row_idx == 0:
                    lot_depth_actual = row_width - internal_road_width / 2
                    lots.extend(_create_column_lots(
                        row_x_start, miny, row_x_start + lot_depth_actual, maxy,
                        target_lot_width, block, lot_id, zone_type, 'W'
                    ))
                    lot_id += lots_per_row
                elif row_idx == row_count - 1:
                    lot_x_start = row_x_start + internal_road_width / 2
                    lots.extend(_create_column_lots(
                        lot_x_start, miny, row_x_end, maxy,
                        target_lot_width, block, lot_id, zone_type, 'E'
                    ))
                    lot_id += lots_per_row
                else:
                    road_left = internal_road_width / 2
                    road_right = internal_road_width / 2
                    lot_depth_actual = row_width - road_left - road_right
                    
                    lot_x_start = row_x_start + road_left
                    lot_x_end = row_x_end - road_right
                    
                    lots.extend(_create_column_lots(
                        lot_x_start, miny, lot_x_end, maxy,
                        target_lot_width, block, lot_id, zone_type, 'M'
                    ))
                    lot_id += lots_per_row
    
    logger.info(f"[ROW SUB] Created {len(lots)} lots in {row_count} rows")
    
    return lots


def _create_row_lots(
    x_start: float,
    y_start: float,
    x_end: float,
    y_end: float,
    lot_width: float,
    block: Polygon,
    start_id: int,
    zone_type: str,
    position: str
) -> List[Dict[str, Any]]:
    """
    Create a horizontal row of lots
    
    Args:
        x_start, y_start, x_end, y_end: Row bounding box
        lot_width: Target width of each lot
        block: Block polygon for clipping
        start_id: Starting lot ID
        zone_type: Zone type
        position: Row position (N/S/M)
        
    Returns:
        List of lot dicts
    """
    lots = []
    
    row_width = x_end - x_start
    row_height = y_end - y_start
    
    num_lots = max(1, int(row_width / lot_width))
    actual_lot_width = row_width / num_lots
    
    for i in range(num_lots):
        lot_x_start = x_start + i * actual_lot_width
        lot_x_end = lot_x_start + actual_lot_width
        
        # Create lot box
        lot_box = box(lot_x_start, y_start, lot_x_end, y_end)
        
        # Clip to block boundary
        lot_clipped = lot_box.intersection(block)
        
        # Keep if valid and large enough
        if (not lot_clipped.is_empty and 
            lot_clipped.geom_type == 'Polygon' and
            lot_clipped.area > 100):  # Min 100m²
            
            # Calculate lot dimensions
            bounds = lot_clipped.bounds
            lot_width_actual = bounds[2] - bounds[0]
            lot_depth_actual = bounds[3] - bounds[1]
            
            lots.append({
                'id': start_id + i,
                'geometry': lot_clipped,
                'zone': zone_type,
                'area': lot_clipped.area,
                'width': lot_width_actual,
                'depth': lot_depth_actual,
                'position': position,
                'row_type': 'horizontal'
            })
    
    return lots


def _create_column_lots(
    x_start: float,
    y_start: float,
    x_end: float,
    y_end: float,
    lot_width: float,
    block: Polygon,
    start_id: int,
    zone_type: str,
    position: str
) -> List[Dict[str, Any]]:
    """
    Create a vertical column of lots
    
    Args:
        x_start, y_start, x_end, y_end: Column bounding box
        lot_width: Target width of each lot (along y-axis)
        block: Block polygon for clipping
        start_id: Starting lot ID
        zone_type: Zone type
        position: Column position (W/E/M)
        
    Returns:
        List of lot dicts
    """
    lots = []
    
    col_width = x_end - x_start
    col_height = y_end - y_start
    
    num_lots = max(1, int(col_height / lot_width))
    actual_lot_height = col_height / num_lots
    
    for i in range(num_lots):
        lot_y_start = y_start + i * actual_lot_height
        lot_y_end = lot_y_start + actual_lot_height
        
        # Create lot box
        lot_box = box(x_start, lot_y_start, x_end, lot_y_end)
        
        # Clip to block boundary
        lot_clipped = lot_box.intersection(block)
        
        # Keep if valid and large enough
        if (not lot_clipped.is_empty and 
            lot_clipped.geom_type == 'Polygon' and
            lot_clipped.area > 100):  # Min 100m²
            
            # Calculate lot dimensions
            bounds = lot_clipped.bounds
            lot_width_actual = bounds[2] - bounds[0]
            lot_depth_actual = bounds[3] - bounds[1]
            
            lots.append({
                'id': start_id + i,
                'geometry': lot_clipped,
                'zone': zone_type,
                'area': lot_clipped.area,
                'width': lot_width_actual,
                'depth': lot_depth_actual,
                'position': position,
                'row_type': 'vertical'
            })
    
    return lots


def get_target_dimensions_for_zone(zone_type: str) -> tuple:
    """
    Get target lot dimensions for BALANCED INDUSTRIAL ESTATES
    
    Based on real Vietnamese standards + hierarchical road system:
    - Blocks are 20k-50k m² after secondary road subdivision
    - Need realistic lot sizes that match actual industrial usage
    
    UPDATED SIZING:
    - FACTORY: Medium industrial plots 40×60m (2,400m²) - typical SME factory
    - WAREHOUSE: Small logistics plots 30×50m (1,500m²) - warehouse units
    - SERVICE: Support facilities 20×30m (600m²) - offices, utilities
    
    This creates:
    - 25k m² block → 10-15 factory lots (manageable)
    - Row-based layout remains clean and organized
    
    Args:
        zone_type: Zone type
        
    Returns:
        (width, depth) in meters
    """
    if zone_type == 'FACTORY':
        # Medium factory lot: 40m × 60m (2,400m²)
        # Typical Vietnamese SME factory size
        # 25k block → ~10 lots
        return (40.0, 60.0)
    
    elif zone_type == 'WAREHOUSE':
        # Small warehouse lot: 30m × 50m (1,500m²)
        # Typical logistics/storage unit
        # 25k block → ~16 lots
        return (30.0, 50.0)
    
    elif zone_type == 'SERVICE':
        # Support service lot: 20m × 30m (600m²)
        # For offices, utilities, amenities
        # 25k block → ~40 lots
        return (20.0, 30.0)
    
    elif zone_type == 'GREEN':
        # Green spaces not subdivided
        return (50.0, 50.0)
    
    else:
        # Default to warehouse size
        return (30.0, 50.0)
