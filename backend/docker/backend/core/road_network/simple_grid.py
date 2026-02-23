"""
Simplified Grid Road Generator for Industrial Estates

Creates minimal road network like reference design:
- 1 main horizontal spine
- 2-3 perpendicular branches
- NO loops, NO curves, NO roundabouts
- Minimal buffer widths

Goal: MAXIMIZE lot generation space
"""

import logging
from typing import List, Tuple
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


def create_simple_grid_roads(
    site_boundary: Polygon,
    num_branches: int = 2,
    main_width: float = 6.0,
    branch_width: float = 4.0
) -> Tuple[Polygon, List[Polygon]]:
    """
    Create ADAPTIVE road network that follows boundary shape
    
    Like real-world design:
    - Main spine follows longest dimension
    - Branches adapt to boundary angles
    - Roads clip to boundary (organic shape)
    - Variable spacing based on area
    
    Args:
        site_boundary: Site polygon
        num_branches: Number of perpendicular branches (default 2)
        main_width: Main road width in meters (default 6m)
        branch_width: Branch road width in meters (default 4m)
        
    Returns:
        (road_network_polygon, list_of_blocks)
    """
    bounds = site_boundary.bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    
    logger.info(
        f"[ADAPTIVE GRID] Site: {width:.0f}m x {height:.0f}m, "
        f"area: {site_boundary.area:.0f}m²"
    )
    
    # Use CENTROID and oriented bounding box
    centroid = site_boundary.centroid
    cx, cy = centroid.x, centroid.y
    
    logger.info(f"[ADAPTIVE GRID] Centroid: ({cx:.1f}, {cy:.1f})")
    
    road_lines = []
    
    # Determine orientation (horizontal vs vertical)
    is_horizontal = width > height
    
    # 1. Main spine along longest dimension, through centroid
    if is_horizontal:
        # Horizontal spine through centroid
        spine = LineString([
            (minx, cy),
            (maxx, cy)
        ])
    else:
        # Vertical spine through centroid
        spine = LineString([
            (cx, miny),
            (cx, maxy)
        ])
    
    # Clip spine to actual boundary
    spine_clipped = spine.intersection(site_boundary)
    if not spine_clipped.is_empty:
        if spine_clipped.geom_type == 'LineString':
            road_lines.append(spine_clipped)
        elif spine_clipped.geom_type == 'MultiLineString':
            road_lines.extend(list(spine_clipped.geoms))
    
    # 2. Adaptive branch spacing based on area
    # Larger sites = more branches
    area = site_boundary.area
    if area > 300000:  # > 30 hectares
        num_branches = 3
    elif area > 150000:  # > 15 hectares
        num_branches = 2
    else:
        num_branches = 1
    
    logger.info(f"[ADAPTIVE GRID] Using {num_branches} branches for {area:.0f}m² site")
    
    # 3. Perpendicular branches - ADAPTIVE spacing
    if num_branches > 0:
        if is_horizontal:
            # Vertical branches for horizontal spine
            # Use adaptive spacing - denser near center
            positions = []
            for i in range(1, num_branches + 1):
                # Non-uniform spacing - more branches in center
                ratio = i / (num_branches + 1)
                # Apply smoothing to cluster toward center
                smoothed_ratio = 0.5 + (ratio - 0.5) * 0.8
                x_pos = minx + width * smoothed_ratio
                positions.append(x_pos)
            
            for x_pos in positions:
                # Create branch from bottom to top
                branch = LineString([
                    (x_pos, miny),
                    (x_pos, maxy)
                ])
                
                # Clip to boundary
                branch_clipped = branch.intersection(site_boundary)
                if not branch_clipped.is_empty:
                    if branch_clipped.geom_type == 'LineString':
                        road_lines.append(branch_clipped)
                    elif branch_clipped.geom_type == 'MultiLineString':
                        road_lines.extend(list(branch_clipped.geoms))
        else:
            # Horizontal branches for vertical spine
            positions = []
            for i in range(1, num_branches + 1):
                ratio = i / (num_branches + 1)
                smoothed_ratio = 0.5 + (ratio - 0.5) * 0.8
                y_pos = miny + height * smoothed_ratio
                positions.append(y_pos)
            
            for y_pos in positions:
                branch = LineString([
                    (minx, y_pos),
                    (maxx, y_pos)
                ])
                
                branch_clipped = branch.intersection(site_boundary)
                if not branch_clipped.is_empty:
                    if branch_clipped.geom_type == 'LineString':
                        road_lines.append(branch_clipped)
                    elif branch_clipped.geom_type == 'MultiLineString':
                        road_lines.extend(list(branch_clipped.geoms))
    
    logger.info(f"[SIMPLE GRID] Created {len(road_lines)} road segments")
    
    # 3. Create minimal buffers
    road_polys = []
    
    for idx, line in enumerate(road_lines):
        # First road = spine (wider)
        width = main_width if idx == 0 else branch_width
        buffer = line.buffer(width / 2, cap_style=2)
        road_polys.append(buffer)
    
    # 4. Merge roads
    network_poly = unary_union(road_polys)
    
    # 5. Extract blocks (site minus roads)
    remaining = site_boundary.difference(network_poly)
    
    # Normalize to list of polygons
    if remaining.is_empty:
        logger.error("[SIMPLE GRID] Road network consumed entire site!")
        return network_poly, []
    
    blocks = []
    if remaining.geom_type == 'Polygon':
        blocks = [remaining]
    elif remaining.geom_type == 'MultiPolygon':
        blocks = list(remaining.geoms)
    else:
        logger.warning(f"[SIMPLE GRID] Unexpected geometry type: {remaining.geom_type}")
        return network_poly, []
    
    # Filter small blocks (< 500m²) and ensure within boundary
    min_block_area = 500.0
    valid_blocks = []
    
    for block in blocks:
        # Check size
        if block.area < min_block_area:
            continue
        
        # CRITICAL: Ensure block is FULLY within site boundary
        # Clip to boundary to fix overflow
        clipped_block = block.intersection(site_boundary)
        
        if not clipped_block.is_empty and clipped_block.area >= min_block_area:
            if clipped_block.geom_type == 'Polygon':
                valid_blocks.append(clipped_block)
            elif clipped_block.geom_type == 'MultiPolygon':
                # Add each polygon separately
                for poly in clipped_block.geoms:
                    if poly.area >= min_block_area:
                        valid_blocks.append(poly)
    
    logger.info(
        f"[SIMPLE GRID] Generated {len(valid_blocks)} blocks "
        f"(total area: {sum(b.area for b in valid_blocks):.0f}m²)"
    )
    
    return network_poly, valid_blocks


def classify_block_by_position(
    block: Polygon,
    site_boundary: Polygon,
    main_roads: List[LineString] = None
) -> str:
    """
    MULTI-CRITERIA classification for real industrial planning
    
    Factors (weighted):
    1. Distance to main road (40%) - Closer = more valuable
    2. Block area size (30%) - Larger = industrial use
    3. Position in site (20%) - Front = commercial, back = service
    4. Block shape (10%) - Regular = easier to develop
    
    Returns: FACTORY, WAREHOUSE, SERVICE, or GREEN
    """
    block_area = block.area
    block_centroid = block.centroid
    
    # Get site info
    site_bounds = site_boundary.bounds
    site_centroid = site_boundary.centroid
    site_area = site_boundary.area
    
    # === CRITERION 1: Distance to main road (40%) ===
    distance_to_road = 999999  # Default large value
    
    if main_roads and len(main_roads) > 0:
        # Find closest main road
        min_dist = 999999
        for road in main_roads:
            dist = block_centroid.distance(road)
            if dist < min_dist:
                min_dist = dist
        distance_to_road = min_dist
    
    # Normalize: closer = higher score
    max_road_dist = (site_area ** 0.5) * 0.5  # Half of site diagonal
    road_score = max(0, 1 - (distance_to_road / max_road_dist))
    
    # === CRITERION 2: Block area (30%) ===
    # Large blocks = factories, small = service
    area_score = 0
    if block_area >= 5000:
        area_score = 1.0  # Very large
    elif block_area >= 2000:
        area_score = 0.6  # Medium
    elif block_area >= 800:
        area_score = 0.3  # Small-medium
    else:
        area_score = 0.1  # Very small
    
    # === CRITERION 3: Position (20%) ===
    # Distance to entrance (assume entrance at left-bottom)
    entrance_point = Point(site_bounds[0], site_bounds[1])
    entrance_dist = block_centroid.distance(entrance_point)
    
    max_entrance_dist = ((site_bounds[2] - site_bounds[0])**2 + 
                        (site_bounds[3] - site_bounds[1])**2) ** 0.5
    
    # Closer to entrance = higher value
    position_score = max(0, 1 - (entrance_dist / max_entrance_dist))
    
    # === CRITERION 4: Shape regularity (10%) ===
    # Regular shapes easier to subdivide
    shape_score = 0.5  # Default medium
    try:
        perimeter = block.length
        area = block.area
        # Compactness: 4π*area/perimeter²
        # Circle = 1.0, square ≈ 0.785, irregular < 0.5
        compactness = (4 * 3.14159 * area) / (perimeter * perimeter)
        shape_score = min(1.0, compactness * 1.3)
    except:
        pass
    
    # === WEIGHTED SCORING ===
    final_score = (
        road_score * 0.40 +      # 40% weight on road access
        area_score * 0.30 +      # 30% weight on size
        position_score * 0.20 +  # 20% weight on location
        shape_score * 0.10       # 10% weight on shape
    )
    
    # === CLASSIFICATION RULES ===
    if final_score >= 0.70:
        # HIGH VALUE: Large, road access, front position = FACTORY
        return 'FACTORY'
    
    elif final_score >= 0.45:
        # MEDIUM VALUE: Medium size, some access = WAREHOUSE
        return 'WAREHOUSE'
    
    elif final_score >= 0.25:
        # LOW-MEDIUM VALUE: Smaller, less access = SERVICE
        return 'SERVICE'
    
    else:
        # LOW VALUE: Small, far from roads = SERVICE/utilities
        return 'SERVICE'
