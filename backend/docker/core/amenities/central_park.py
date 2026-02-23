"""
Central park and roundabout generator for industrial zone layouts.

Creates:
- Central park with landscaping at main road intersections
- Roundabout geometry for traffic flow
- Tree-lined buffers along main roads
"""

import logging
from typing import List, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString, MultiPolygon
from shapely.affinity import scale, rotate
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


def create_roundabout(
    center: Point,
    outer_radius: float = 25.0,  # Outer road radius
    inner_radius: float = 12.0,  # Central island radius
    road_width: float = 8.0
) -> Tuple[Polygon, Polygon]:
    """Create roundabout geometry at an intersection.
    
    Args:
        center: Center point of roundabout
        outer_radius: Outer edge radius of the roundabout road
        inner_radius: Radius of the central landscaped island
        road_width: Width of the circular road
        
    Returns:
        Tuple of (road_ring, central_island) polygons
    """
    # Central landscaped island (GREEN)
    central_island = center.buffer(inner_radius)
    
    # Road ring (the circular road around the island)
    outer_circle = center.buffer(outer_radius)
    inner_circle = center.buffer(outer_radius - road_width)
    road_ring = outer_circle.difference(inner_circle)
    
    logger.info(f"Created roundabout at ({center.x:.1f}, {center.y:.1f}) radius={outer_radius}m")
    
    return road_ring, central_island


def create_central_park(
    site: Polygon,
    road_intersections: List[Point],
    park_ratio: float = 0.03,  # 3% of total site area
    include_roundabout: bool = True
) -> dict:
    """Create central park with optional roundabout at main intersection.
    
    Based on reference design showing "Công Viên Trung Tâm" with:
    - Large green area
    - Central roundabout
    - Tree-lined paths
    
    Args:
        site: Site boundary polygon
        road_intersections: List of road intersection points
        park_ratio: Ratio of site area for the park
        include_roundabout: Whether to add roundabout at center
        
    Returns:
        Dictionary with park geometry and components
    """
    park_area = site.area * park_ratio
    park_radius = math.sqrt(park_area / math.pi) * 1.2  # Slightly larger for non-circular
    
    # Find best intersection for central park (prefer center of site)
    site_centroid = site.centroid
    
    if road_intersections:
        # Find intersection closest to center
        best_intersection = min(
            road_intersections,
            key=lambda p: p.distance(site_centroid)
        )
    else:
        # Use site centroid
        best_intersection = site_centroid
    
    # Create park polygon (rectangular with rounded corners)
    half_size = park_radius * 0.7
    park_bounds = Polygon([
        (best_intersection.x - half_size, best_intersection.y - half_size * 0.8),
        (best_intersection.x + half_size, best_intersection.y - half_size * 0.8),
        (best_intersection.x + half_size, best_intersection.y + half_size * 0.8),
        (best_intersection.x - half_size, best_intersection.y + half_size * 0.8),
    ])
    
    # Round corners
    park_polygon = park_bounds.buffer(half_size * 0.1).buffer(-half_size * 0.05)
    
    # Ensure park is within site
    park_polygon = park_polygon.intersection(site)
    
    result = {
        'park_polygon': park_polygon,
        'type': 'PARK',
        'zone': 'GREEN',
        'zone_color': '#43A047',
        'area': park_polygon.area,
        'center': best_intersection,
        'name': 'Công Viên Trung Tâm',
        'components': []
    }
    
    if include_roundabout:
        road_ring, central_island = create_roundabout(
            center=best_intersection,
            outer_radius=min(25.0, park_radius * 0.3),
            inner_radius=min(12.0, park_radius * 0.15)
        )
        
        result['roundabout'] = {
            'road_ring': road_ring,
            'central_island': central_island,
            'zone_color': '#43A047'  # Green for island
        }
        result['components'].append({
            'geometry': central_island,
            'type': 'ROUNDABOUT_ISLAND',
            'zone': 'GREEN',
            'zone_color': '#2E7D32'  # Darker green
        })
    
    logger.info(f"Created central park: {park_polygon.area:.0f}m² at ({best_intersection.x:.1f}, {best_intersection.y:.1f})")
    
    return result


def create_tree_buffer(
    road_line: LineString,
    buffer_width: float = 8.0,
    side: str = 'both'  # 'left', 'right', 'both'
) -> Polygon:
    """Create tree-lined buffer zone along a road.
    
    Args:
        road_line: Road centerline
        buffer_width: Width of tree buffer zone
        side: Which side(s) of road to buffer
        
    Returns:
        Polygon representing tree buffer zone
    """
    if side == 'both':
        return road_line.buffer(buffer_width)
    elif side == 'left':
        return road_line.buffer(buffer_width, single_sided=True)
    else:
        # Right side - buffer negative then flip
        left = road_line.buffer(buffer_width, single_sided=True)
        return left  # Simplified - would need proper offset


def find_road_intersections(
    road_lines: List[LineString]
) -> List[Point]:
    """Find intersection points of road lines.
    
    Args:
        road_lines: List of road centerlines
        
    Returns:
        List of intersection points
    """
    intersections = []
    
    for i, road1 in enumerate(road_lines):
        for road2 in road_lines[i+1:]:
            if road1.intersects(road2):
                intersection = road1.intersection(road2)
                if intersection.geom_type == 'Point':
                    intersections.append(intersection)
                elif intersection.geom_type == 'MultiPoint':
                    intersections.extend(list(intersection.geoms))
    
    return intersections


def create_parking_lot(
    location: Point,
    width: float = 40.0,
    depth: float = 25.0,
    orientation: float = 0.0  # degrees
) -> dict:
    """Create a parking lot polygon.
    
    Args:
        location: Center point of parking lot
        width: Width of parking lot
        depth: Depth of parking lot
        orientation: Rotation angle in degrees
        
    Returns:
        Dictionary with parking lot geometry and metadata
    """
    # Create rectangular parking lot
    half_w = width / 2
    half_d = depth / 2
    
    parking = Polygon([
        (location.x - half_w, location.y - half_d),
        (location.x + half_w, location.y - half_d),
        (location.x + half_w, location.y + half_d),
        (location.x - half_w, location.y + half_d),
    ])
    
    # Rotate if needed
    if orientation != 0:
        parking = rotate(parking, orientation, origin=location)
    
    return {
        'geometry': parking,
        'type': 'PARKING',
        'zone': 'SERVICE',
        'zone_color': '#78909C',
        'area': parking.area,
        'name': 'Parking Lot'
    }
