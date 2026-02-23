"""
Water feature generator for industrial zone layouts.

Creates decorative lakes and ponds at strategic positions
to match the reference design pattern.
"""

import logging
from typing import List, Tuple, Optional
from shapely.geometry import Polygon, Point, box
from shapely.affinity import scale, rotate
from shapely.ops import unary_union
import random
import math

logger = logging.getLogger(__name__)


def create_water_feature(
    center: Point,
    size: float = 5000.0,  # m² target area
    shape: str = 'organic'  # 'organic', 'rectangular', 'oval'
) -> Polygon:
    """Create a single water feature (lake/pond) at given location.
    
    Args:
        center: Center point for the water feature
        size: Target area in m²
        shape: Shape type - 'organic' for natural lakes, 'rectangular' for ponds
        
    Returns:
        Polygon representing the water feature
    """
    # Calculate radius from target area (approximate)
    radius = math.sqrt(size / math.pi)
    
    if shape == 'rectangular':
        # Create rectangular pond with rounded corners
        half_w = radius * 1.5
        half_h = radius * 0.8
        rect = box(
            center.x - half_w, center.y - half_h,
            center.x + half_w, center.y + half_h
        )
        # Round corners
        return rect.buffer(radius * 0.1).buffer(-radius * 0.1)
    
    elif shape == 'oval':
        # Create elliptical lake
        circle = center.buffer(radius)
        return scale(circle, xfact=1.5, yfact=0.8, origin=center)
    
    else:  # organic
        # Create organic-shaped lake using multiple circles
        base = center.buffer(radius * 0.7)
        
        # Add bulges for organic shape
        for i in range(4):
            angle = (i / 4) * 2 * math.pi + random.uniform(-0.3, 0.3)
            offset_x = radius * 0.5 * math.cos(angle)
            offset_y = radius * 0.5 * math.sin(angle)
            bulge = Point(center.x + offset_x, center.y + offset_y).buffer(
                radius * random.uniform(0.3, 0.5)
            )
            base = base.union(bulge)
        
        # Smooth the result
        return base.buffer(radius * 0.1).buffer(-radius * 0.05)


def create_lakes(
    site: Polygon,
    blocks: List[Polygon],
    num_lakes: int = 3,
    lake_size_ratio: float = 0.015,  # 1.5% of total site area per lake
    min_distance_to_blocks: float = 20.0
) -> List[dict]:
    """Create decorative lakes at strategic positions matching reference design.
    
    Reference design shows lakes at:
    - Top-right corner (near warehouse zone)
    - Center-right (near main road intersection)
    - Bottom-right corner
    
    Args:
        site: Site boundary polygon
        blocks: Existing subdivision blocks to avoid
        num_lakes: Number of lakes to create (default 3 like reference)
        lake_size_ratio: Ratio of site area for each lake
        min_distance_to_blocks: Minimum distance from blocks
        
    Returns:
        List of lake dictionaries with geometry and metadata
    """
    lakes = []
    site_area = site.area
    lake_size = site_area * lake_size_ratio
    
    # Get site bounds for positioning
    minx, miny, maxx, maxy = site.bounds
    width = maxx - minx
    height = maxy - miny
    
    # Strategic positions based on reference design
    # Using relative positions from site bounds
    positions = [
        # Top-right area
        Point(minx + width * 0.85, miny + height * 0.85),
        # Center-right area
        Point(minx + width * 0.80, miny + height * 0.50),
        # Bottom-right corner
        Point(minx + width * 0.75, miny + height * 0.25),
    ]
    
    # Create blocks union for avoidance check
    blocks_union = unary_union(blocks) if blocks else Polygon()
    
    for i, pos in enumerate(positions[:num_lakes]):
        # Adjust position if outside site
        if not site.contains(pos):
            # Move toward site centroid
            centroid = site.centroid
            dx = centroid.x - pos.x
            dy = centroid.y - pos.y
            pos = Point(pos.x + dx * 0.3, pos.y + dy * 0.3)
        
        # Vary shape based on position
        shapes = ['organic', 'oval', 'organic']
        lake_geom = create_water_feature(
            center=pos,
            size=lake_size * random.uniform(0.8, 1.2),
            shape=shapes[i % len(shapes)]
        )
        
        # Ensure lake is within site
        lake_geom = lake_geom.intersection(site)
        
        # Check minimum distance to blocks
        if not blocks_union.is_empty:
            dist = lake_geom.distance(blocks_union)
            if dist < min_distance_to_blocks:
                # Scale down if too close
                scale_factor = 0.7
                lake_geom = scale(lake_geom, xfact=scale_factor, yfact=scale_factor, origin=pos)
        
        if lake_geom.is_valid and lake_geom.area > 100:
            lakes.append({
                'geometry': lake_geom,
                'type': 'WATER',
                'zone': 'WATER',
                'zone_color': '#1E88E5',  # Blue
                'area': lake_geom.area,
                'name': f'Lake_{i+1}'
            })
            logger.info(f"Created lake {i+1}: {lake_geom.area:.0f}m² at ({pos.x:.1f}, {pos.y:.1f})")
    
    return lakes


def find_lake_positions(
    site: Polygon,
    road_network: Polygon,
    green_zones: List[Polygon]
) -> List[Point]:
    """Find optimal positions for lakes based on available space.
    
    Prioritizes:
    1. Corners of the site
    2. Near green buffer zones
    3. Away from main roads
    
    Args:
        site: Site boundary
        road_network: Road network polygon to avoid
        green_zones: Existing green zones (good neighbors for lakes)
        
    Returns:
        List of optimal lake center points
    """
    positions = []
    
    minx, miny, maxx, maxy = site.bounds
    width = maxx - minx
    height = maxy - miny
    
    # Check corners
    corner_offsets = [
        (0.1, 0.9),   # Top-left
        (0.9, 0.9),   # Top-right
        (0.9, 0.1),   # Bottom-right
    ]
    
    for rx, ry in corner_offsets:
        pt = Point(minx + width * rx, miny + height * ry)
        
        # Check if position is valid (in site, not on road)
        if site.contains(pt):
            dist_to_road = pt.distance(road_network) if road_network else float('inf')
            if dist_to_road > 30:
                positions.append(pt)
    
    return positions
