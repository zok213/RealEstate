"""
Enhanced amenities and landscape features generator

Creates parks, green buffers, water features, and pedestrian walkways
for industrial estate master planning.
"""

import logging
from typing import List, Dict, Tuple
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


def create_green_buffer_zones(
    site_boundary: Polygon,
    blocks: List[Polygon],
    buffer_width: float = 5.0
) -> List[Polygon]:
    """
    Create green buffer zones along site perimeter
    
    Args:
        site_boundary: Site polygon
        blocks: List of building blocks
        buffer_width: Width of buffer zone (m)
        
    Returns:
        List of green buffer polygons
    """
    # Create buffer zone along perimeter
    inner_boundary = site_boundary.buffer(-buffer_width)
    
    if inner_boundary.is_empty:
        return []
    
    # Buffer zone is the difference
    buffer_zone = site_boundary.difference(inner_boundary)
    
    # Subtract existing blocks
    if blocks:
        blocks_union = unary_union(blocks)
        buffer_zone = buffer_zone.difference(blocks_union)
    
    # Split into segments if multipolygon
    if buffer_zone.geom_type == 'MultiPolygon':
        return list(buffer_zone.geoms)
    elif buffer_zone.geom_type == 'Polygon':
        return [buffer_zone]
    
    return []


def create_pedestrian_walkways(
    parks: List[Polygon],
    residential_blocks: List[Polygon],
    width: float = 3.0
) -> List[LineString]:
    """
    Create pedestrian walkways connecting parks and residential areas
    
    Args:
        parks: List of park polygons
        residential_blocks: List of residential blocks
        width: Walkway width (m)
        
    Returns:
        List of walkway LineStrings
    """
    walkways = []
    
    if not parks or not residential_blocks:
        return walkways
    
    # Connect each park to nearest residential blocks
    for park in parks:
        park_center = park.centroid
        
        # Find 3 nearest residential blocks
        distances = []
        for block in residential_blocks:
            dist = park_center.distance(block.centroid)
            distances.append((dist, block))
        
        distances.sort()
        nearest_blocks = [b for _, b in distances[:min(3, len(distances))]]
        
        # Create walkways
        for block in nearest_blocks:
            walkway = LineString([
                (park_center.x, park_center.y),
                (block.centroid.x, block.centroid.y)
            ])
            walkways.append(walkway)
    
    return walkways


def create_corner_parks(
    site_boundary: Polygon,
    existing_blocks: List[Polygon],
    min_park_area: float = 2000.0
) -> List[Polygon]:
    """
    Create small parks at site corners
    
    Args:
        site_boundary: Site polygon
        existing_blocks: List of existing blocks to avoid
        min_park_area: Minimum park area (m²)
        
    Returns:
        List of corner park polygons
    """
    parks = []
    bounds = site_boundary.bounds
    
    # Define corner zones (each 10% of site dimensions)
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    corner_size = min(width, height) * 0.1
    
    corners = [
        # (x_center, y_center, label)
        (bounds[0] + corner_size/2, bounds[1] + corner_size/2, 'SW'),
        (bounds[2] - corner_size/2, bounds[1] + corner_size/2, 'SE'),
        (bounds[2] - corner_size/2, bounds[3] - corner_size/2, 'NE'),
        (bounds[0] + corner_size/2, bounds[3] - corner_size/2, 'NW'),
    ]
    
    blocks_union = unary_union(existing_blocks) if existing_blocks else Polygon()
    
    for x, y, label in corners:
        # Create circular park (smaller to preserve space)
        park = Point(x, y).buffer(corner_size * 0.3)
        
        # Clip to site
        park = park.intersection(site_boundary)
        
        # Remove overlaps with blocks
        park = park.difference(blocks_union)
        
        if not park.is_empty and park.area >= min_park_area:
            parks.append(park)
            logger.info(f"Created corner park at {label}: {park.area:.0f}m²")
    
    return parks


def create_linear_parks(
    main_roads: List[LineString],
    site_boundary: Polygon,
    park_width: float = 25.0,
    min_length: float = 100.0
) -> List[Polygon]:
    """
    Create linear parks along main roads
    
    Args:
        main_roads: List of main road LineStrings
        site_boundary: Site polygon
        park_width: Width of linear park (m)
        min_length: Minimum road length to create park (m)
        
    Returns:
        List of linear park polygons
    """
    parks = []
    
    for road in main_roads:
        if road.length < min_length:
            continue
        
        # Create buffer on one side
        park = road.buffer(park_width, single_sided=True)
        
        # Clip to site
        park = park.intersection(site_boundary)
        
        if not park.is_empty and park.area > 500:
            parks.append(park)
    
    return parks


def enhance_water_features(
    existing_water: List[Polygon],
    site_boundary: Polygon,
    add_islands: bool = True
) -> List[Dict]:
    """
    Enhance water features with islands and natural edges
    
    Args:
        existing_water: Existing water feature polygons
        site_boundary: Site polygon
        add_islands: Whether to add small islands
        
    Returns:
        List of enhanced water feature dictionaries
    """
    enhanced = []
    
    for idx, water in enumerate(existing_water):
        water_dict = {
            'geometry': water,
            'type': 'water',
            'name': f'Lake {idx + 1}',
            'area_sqm': water.area
        }
        
        # Add island if water is large enough
        if add_islands and water.area > 5000:
            center = water.centroid
            island_radius = (water.area / 3.14159) ** 0.5 * 0.15
            island = center.buffer(island_radius)
            
            # Ensure island is within water
            if island.within(water):
                water_dict['island'] = island
        
        enhanced.append(water_dict)
    
    return enhanced


def create_complete_landscape_package(
    site_boundary: Polygon,
    blocks: List[Polygon],
    zoned_blocks: Dict[str, List[Polygon]],
    main_roads: List[LineString]
) -> Dict:
    """
    Create complete landscape package with all amenities
    
    Args:
        site_boundary: Site polygon
        blocks: All blocks
        zoned_blocks: Blocks organized by zone type
        main_roads: Main road LineStrings
        
    Returns:
        Dictionary with all landscape features
    """
    landscape = {
        'green_buffers': [],
        'corner_parks': [],
        'linear_parks': [],
        'walkways': [],
        'water_enhanced': []
    }
    
    # 1. Green buffer zones
    landscape['green_buffers'] = create_green_buffer_zones(
        site_boundary,
        blocks,
        buffer_width=12.0
    )
    logger.info(f"Created {len(landscape['green_buffers'])} green buffer zones")
    
    # 2. Corner parks
    landscape['corner_parks'] = create_corner_parks(
        site_boundary,
        blocks,
        min_park_area=1500.0
    )
    logger.info(f"Created {len(landscape['corner_parks'])} corner parks")
    
    # 3. Linear parks along main roads
    if main_roads:
        landscape['linear_parks'] = create_linear_parks(
            main_roads,
            site_boundary,
            park_width=20.0,
            min_length=80.0
        )
        logger.info(f"Created {len(landscape['linear_parks'])} linear parks")
    
    # 4. Pedestrian walkways
    residential_blocks = zoned_blocks.get('RESIDENTIAL', [])
    all_parks = (
        landscape['corner_parks'] + 
        landscape['linear_parks'] +
        zoned_blocks.get('GREEN', [])
    )
    
    if residential_blocks and all_parks:
        landscape['walkways'] = create_pedestrian_walkways(
            all_parks,
            residential_blocks,
            width=2.5
        )
        logger.info(f"Created {len(landscape['walkways'])} pedestrian walkways")
    
    return landscape
