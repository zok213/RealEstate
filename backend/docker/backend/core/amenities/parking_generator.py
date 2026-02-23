"""
Parking Area Generator for QCVN 01:2021/BXD compliance.

VERSION 2: Creates ONE dedicated parking lot per block (instead of parking strip per lot).
This approach: 1 small lot in each block becomes the parking area.
"""
from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.ops import unary_union
from shapely.affinity import translate, scale
import logging

logger = logging.getLogger(__name__)


def generate_block_parking_lot(
    block_lots: List[Dict[str, Any]],
    block_id: int,
    settings: Any
) -> Optional[Dict[str, Any]]:
    """
    Generate ONE parking lot for a block by selecting the smallest lot.
    
    Strategy: Take the smallest lot in the block and designate it as parking.
    This ensures each block has dedicated parking without complex geometry.
    
    Args:
        block_lots: List of all lots in this block
        block_id: Block identifier
        settings: Algorithm settings
        
    Returns:
        Parking lot dictionary or None
    """
    if not block_lots:
        return None
    
    # Find smallest lot in block (ideal for parking)
    smallest_lot = min(block_lots, key=lambda lot: lot.get('area', 0))
    
    # Require minimum size for parking (500m²)
    if smallest_lot.get('area', 0) < 500:
        return None
    
    # Convert this lot to parking
    parking_lot = {
        'coords': smallest_lot.get('coords'),
        'geometry': smallest_lot.get('geometry'),
        'area': smallest_lot.get('area'),
        'zone': 'PARKING',
        'type': 'parking',
        'block_id': block_id,
        'lot_id': f"PARKING-B{block_id}"
    }
    
    logger.info(f"[PARKING] Block {block_id}: Created parking lot {parking_lot['area']:.0f}m² from smallest lot")
    
    return parking_lot


def generate_parking_areas(
    lots: List[Dict[str, Any]],
    settings: Any
) -> List[Dict[str, Any]]:
    """
    Generate parking areas by selecting 1 lot per block.
    
    Strategy:
    1. Group lots by block_id (if available) or spatial proximity
    2. Select smallest lot in each block
    3. Designate as parking lot
    
    Args:
        lots: List of lot dictionaries with 'geometry', 'zone', 'area'
        settings: Algorithm settings
        
    Returns:
        List of parking lot dictionaries (1 per block)
    """
    if not lots:
        return []
    
    parking_lots = []
    
    # Method 1: If lots have block_id, group by block
    if any('block_id' in lot for lot in lots):
        blocks = {}
        for lot in lots:
            block_id = lot.get('block_id', 0)
            if block_id not in blocks:
                blocks[block_id] = []
            blocks[block_id].append(lot)
        
        # Generate 1 parking lot per block
        for block_id, block_lots in blocks.items():
            parking_lot = generate_block_parking_lot(block_lots, block_id, settings)
            if parking_lot:
                parking_lots.append(parking_lot)
    
    # Method 2: Spatial grouping (cluster nearby lots)
    else:
        # Simple approach: Take every Nth smallest lot as parking
        # Assuming 10-20 lots per "virtual block"
        sorted_lots = sorted(lots, key=lambda lot: lot.get('area', 0))
        block_size = 15  # Approximate lots per block
        
        for i in range(0, len(sorted_lots), block_size):
            block_lots = sorted_lots[i:i+block_size]
            if block_lots:
                parking_lot = generate_block_parking_lot(block_lots, i // block_size, settings)
                if parking_lot:
                    parking_lots.append(parking_lot)
    
    logger.info(f"[PARKING] Generated {len(parking_lots)} parking lots (1 per block strategy)")
    
    return parking_lots


# ===== LEGACY FUNCTIONS (kept for compatibility) =====

def generate_lot_parking(
    lot: Polygon,
    lot_area: float,
    zone_type: str,
    settings: Any
) -> Optional[Polygon]:
    """
    LEGACY: Generate parking strip for a single lot.
    NOTE: Now using generate_block_parking_lot() instead.
    """
    # Simple fallback: 15% of lot area
    bounds = lot.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    
    parking_depth = min(8.0, height * 0.15)
    parking_width = min(width, lot_area * 0.15 / parking_depth)
    
    parking_polygon = Polygon([
        (bounds[0], bounds[1]),
        (bounds[0] + parking_width, bounds[1]),
        (bounds[0] + parking_width, bounds[1] + parking_depth),
        (bounds[0], bounds[1] + parking_depth)
    ])
    
    if parking_polygon.area < 50:
        return None
    
    return parking_polygon
