"""
Hierarchical Road Network Generator - Match Reference Design

Creates professional industrial estate layout:
- Level 1: Perimeter road (20-24m)
- Level 2: Main divider roads (12-16m) creating 4-6 blocks
- Level 3: Internal block roads (6-8m) creating rows
- Strategic landscape placement (corners, centers)

Matches real Vietnamese industrial estate master plans
"""

import logging
from typing import List, Tuple, Dict, Any
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union, split
from shapely.affinity import scale
import math
import numpy as np

logger = logging.getLogger(__name__)


def create_hierarchical_roads(
    site_boundary: Polygon,
    perimeter_width: float = 20.0,
    main_width: float = 14.0,
    secondary_width: float = 7.0
) -> Tuple[Polygon, List[Dict[str, Any]], List[Polygon]]:
    """
    Create HIERARCHICAL road network matching reference design
    
    Architecture:
    1. Perimeter road (buffer from boundary)
    2. Main roads dividing site into 4-6 large blocks
    3. Secondary roads creating rows within blocks
    4. Strategic landscape features
    
    Args:
        site_boundary: Site polygon
        perimeter_width: Perimeter road width (default 20m)
        main_width: Main divider road width (default 14m)
        secondary_width: Internal road width (default 7m)
        
    Returns:
        (road_network_polygon, blocks_with_metadata, landscape_features)
    """
    bounds = site_boundary.bounds
    minx, miny, maxx, maxy = bounds
    
    width = maxx - minx
    height = maxy - miny
    area = site_boundary.area
    
    logger.info(
        f"[HIERARCHICAL] Site: {width:.0f}m x {height:.0f}m = {area:.0f}m²"
    )
    
    road_polygons = []
    landscape_features = []
    
    # ========================================
    # LEVEL 1: PERIMETER ROAD (20-24m buffer)
    # ========================================
    perimeter_buffer = perimeter_width / 2.0
    
    # Shrink boundary to create perimeter road
    inner_boundary = site_boundary.buffer(-perimeter_buffer)
    
    # Perimeter road is the difference (already within boundary)
    if not inner_boundary.is_empty and inner_boundary.is_valid:
        perimeter_road = site_boundary.difference(inner_boundary)
        if not perimeter_road.is_empty:
            # Clip to ensure strictly within boundary
            perimeter_clipped = perimeter_road.intersection(site_boundary)
            road_polygons.append(perimeter_clipped)
            logger.info(f"[PERIMETER] Created {perimeter_width}m perimeter road")
    else:
        # Site too small for perimeter road
        inner_boundary = site_boundary
        logger.warning(f"[PERIMETER] Site too small for {perimeter_width}m perimeter")
    
    # Work with inner boundary from now on
    working_area = inner_boundary
    
    # ========================================
    # LEVEL 2: MAIN DIVIDER ROADS (12-16m)
    # ========================================
    # Create 4-6 blocks based on site size
    # Strategy: 1 horizontal + 1-2 vertical dividers
    
    main_road_lines = []
    
    # Get working area bounds
    if isinstance(working_area, Polygon):
        w_bounds = working_area.bounds
        w_minx, w_miny, w_maxx, w_maxy = w_bounds
        w_width = w_maxx - w_minx
        w_height = w_maxy - w_miny
        w_cx = (w_minx + w_maxx) / 2
        w_cy = (w_miny + w_maxy) / 2
        
        # Horizontal main road (center)
        horizontal_main = LineString([
            (w_minx, w_cy),
            (w_maxx, w_cy)
        ])
        main_road_lines.append(horizontal_main)
        
        # Vertical main roads (1-2 based on width)
        if w_width > 300:  # Large site: 2 vertical dividers
            # Two vertical roads at 1/3 and 2/3
            v1_x = w_minx + w_width / 3
            v2_x = w_minx + 2 * w_width / 3
            
            vertical_1 = LineString([(v1_x, w_miny), (v1_x, w_maxy)])
            vertical_2 = LineString([(v2_x, w_miny), (v2_x, w_maxy)])
            
            main_road_lines.extend([vertical_1, vertical_2])
            logger.info("[MAIN ROADS] Created 1H + 2V = 6 blocks")
        else:  # Medium site: 1 vertical divider
            vertical = LineString([(w_cx, w_miny), (w_cx, w_maxy)])
            main_road_lines.append(vertical)
            logger.info("[MAIN ROADS] Created 1H + 1V = 4 blocks")
        
        # Buffer main roads to create polygons, clip to boundary
        for line in main_road_lines:
            # Clip to working area first
            clipped = line.intersection(working_area)
            if not clipped.is_empty:
                if clipped.geom_type == 'LineString':
                    road_poly = clipped.buffer(main_width / 2.0)
                    # CRITICAL: Clip to site boundary immediately
                    road_clipped = road_poly.intersection(site_boundary)
                    if not road_clipped.is_empty:
                        road_polygons.append(road_clipped)
                elif clipped.geom_type == 'MultiLineString':
                    for seg in clipped.geoms:
                        road_poly = seg.buffer(main_width / 2.0)
                        # CRITICAL: Clip to site boundary immediately
                        road_clipped = road_poly.intersection(site_boundary)
                        if not road_clipped.is_empty:
                            road_polygons.append(road_clipped)
        
        # ========================================
        # EXTRACT BLOCKS (remaining areas)
        # ========================================
        # Subtract all roads from working area
        all_roads = unary_union(road_polygons)
        blocks_area = working_area.difference(all_roads)
        
        # Extract individual blocks
        raw_blocks = []
        if blocks_area.geom_type == 'Polygon':
            raw_blocks = [blocks_area]
        elif blocks_area.geom_type == 'MultiPolygon':
            raw_blocks = list(blocks_area.geoms)
        
        # Filter out tiny slivers
        blocks = [b for b in raw_blocks if b.area > 1000]  # Min 1000m²
        
        logger.info(f"[BLOCKS] Created {len(blocks)} primary blocks from main roads")
        
        # ========================================
        # LEVEL 3: SECONDARY ROADS (8m) - SUBDIVIDE LARGE BLOCKS
        # ========================================
        # Large blocks (>100,000m²) need secondary roads to create manageable sub-blocks
        # Target: 20,000-50,000m² sub-blocks for efficient lot subdivision
        
        final_blocks = []
        secondary_road_width = 8.0
        
        for block_idx, block in enumerate(blocks):
            block_area = block.area
            
            # Small/medium blocks: keep as-is
            if block_area < 100000:
                final_blocks.append(block)
                continue
            
            # Large blocks: add secondary roads
            b_bounds = block.bounds
            b_minx, b_miny, b_maxx, b_maxy = b_bounds
            b_width = b_maxx - b_minx
            b_height = b_maxy - b_miny
            
            # Determine how many secondary roads needed
            # Target: ~3-5 sub-blocks per dimension
            num_h_roads = max(0, int(b_height / 250) - 1)  # Every ~250m
            num_v_roads = max(0, int(b_width / 250) - 1)
            
            if num_h_roads == 0 and num_v_roads == 0:
                # No secondary roads needed
                final_blocks.append(block)
                continue
            
            logger.info(
                f"[SECONDARY] Block {block_idx+1} ({block_area:.0f}m²): "
                f"adding {num_h_roads}H + {num_v_roads}V secondary roads"
            )
            
            # Create secondary road lines
            secondary_lines = []
            
            # Horizontal secondary roads
            if num_h_roads > 0:
                spacing = b_height / (num_h_roads + 1)
                for i in range(num_h_roads):
                    y = b_miny + spacing * (i + 1)
                    h_line = LineString([(b_minx, y), (b_maxx, y)])
                    secondary_lines.append(h_line)
            
            # Vertical secondary roads
            if num_v_roads > 0:
                spacing = b_width / (num_v_roads + 1)
                for i in range(num_v_roads):
                    x = b_minx + spacing * (i + 1)
                    v_line = LineString([(x, b_miny), (x, b_maxy)])
                    secondary_lines.append(v_line)
            
            # Buffer secondary roads and clip to site boundary
            secondary_polys = []
            for line in secondary_lines:
                clipped = line.intersection(block)
                if not clipped.is_empty:
                    if clipped.geom_type == 'LineString':
                        road_poly = clipped.buffer(secondary_road_width / 2.0)
                        # Clip to site boundary immediately
                        road_final = road_poly.intersection(site_boundary)
                        if not road_final.is_empty:
                            secondary_polys.append(road_final)
                    elif clipped.geom_type == 'MultiLineString':
                        for seg in clipped.geoms:
                            road_poly = seg.buffer(secondary_road_width / 2.0)
                            # Clip to site boundary immediately
                            road_final = road_poly.intersection(site_boundary)
                            if not road_final.is_empty:
                                secondary_polys.append(road_final)
            
            # Add secondary roads to main road network
            if secondary_polys:
                road_polygons.extend(secondary_polys)
                
                # Subtract secondary roads from block
                secondary_union = unary_union(secondary_polys)
                sub_blocks_area = block.difference(secondary_union)
                
                # Extract sub-blocks
                if sub_blocks_area.geom_type == 'Polygon':
                    final_blocks.append(sub_blocks_area)
                elif sub_blocks_area.geom_type == 'MultiPolygon':
                    final_blocks.extend([b for b in sub_blocks_area.geoms if b.area > 5000])
            else:
                final_blocks.append(block)
        
        logger.info(f"[SECONDARY] Refined to {len(final_blocks)} sub-blocks (avg: {np.mean([b.area for b in final_blocks]):.0f}m²)")
        
        # Use final_blocks instead of blocks for landscape and metadata
        blocks = final_blocks
        
        # ========================================
        # LEVEL 4: STRATEGIC LANDSCAPE FEATURES
        # ========================================
        # Place parks/water at corners and centers of blocks
        
        for i, block in enumerate(blocks):
            block_area = block.area
            b_bounds = block.bounds
            b_minx, b_miny, b_maxx, b_maxy = b_bounds
            b_cx = (b_minx + b_maxx) / 2
            b_cy = (b_miny + b_maxy) / 2
            
            # Large blocks (>50,000m²) get central park
            if block_area > 50000:
                park_radius = min(40, math.sqrt(block_area) * 0.1)
                park = Point(b_cx, b_cy).buffer(park_radius)
                
                # Clip to block
                park_clipped = park.intersection(block)
                if not park_clipped.is_empty and park_clipped.area > 500:
                    landscape_features.append({
                        'geometry': park_clipped,
                        'type': 'PARK',
                        'area': park_clipped.area,
                        'position': 'center'
                    })
                    logger.info(f"[LANDSCAPE] Block {i}: Central park {park_clipped.area:.0f}m²")
            
            # Corner parks for edge blocks
            # Check if block touches site boundary
            if block.intersects(site_boundary.boundary):
                # Small corner park (15-25m radius)
                corners = [
                    (b_minx + 20, b_miny + 20),  # Bottom-left
                    (b_maxx - 20, b_miny + 20),  # Bottom-right
                    (b_minx + 20, b_maxy - 20),  # Top-left
                    (b_maxx - 20, b_maxy - 20),  # Top-right
                ]
                
                for corner_x, corner_y in corners:
                    corner_point = Point(corner_x, corner_y)
                    if block.contains(corner_point):
                        corner_park = corner_point.buffer(18)
                        corner_clipped = corner_park.intersection(block)
                        
                        if not corner_clipped.is_empty and corner_clipped.area > 300:
                            landscape_features.append({
                                'geometry': corner_clipped,
                                'type': 'PARK',
                                'area': corner_clipped.area,
                                'position': 'corner'
                            })
                            break  # One corner park per block
        
        logger.info(f"[LANDSCAPE] Created {len(landscape_features)} strategic features")
        
        # ========================================
        # PREPARE BLOCKS WITH METADATA
        # ========================================
        blocks_with_metadata = []
        
        for i, block in enumerate(blocks):
            # Subtract landscape features from this block
            block_working = block
            for feature in landscape_features:
                if block.intersects(feature['geometry']):
                    block_working = block_working.difference(feature['geometry'])
            
            # Skip if block too small after landscape subtraction
            if isinstance(block_working, Polygon):
                if block_working.area < 1000:
                    continue
            elif isinstance(block_working, MultiPolygon):
                # Keep largest piece
                pieces = sorted(block_working.geoms, key=lambda p: p.area, reverse=True)
                block_working = pieces[0] if pieces else None
                if block_working is None or block_working.area < 1000:
                    continue
            else:
                continue
            
            # Calculate position for classification
            b_bounds = block.bounds
            b_cx = (b_bounds[0] + b_bounds[2]) / 2
            b_cy = (b_bounds[1] + b_bounds[3]) / 2
            
            # Distance to site entrance (assume bottom edge)
            entrance_dist = b_cy - miny
            
            blocks_with_metadata.append({
                'geometry': block_working,
                'id': i + 1,
                'area': block_working.area,
                'centroid': (b_cx, b_cy),
                'entrance_distance': entrance_dist
            })
        
        logger.info(f"[FINAL] {len(blocks_with_metadata)} blocks ready for subdivision")
        
        # ========================================
        # CLIP TO SITE BOUNDARY (CRITICAL!)
        # ========================================
        # Ensure everything stays within original boundary
        road_network = unary_union(road_polygons)
        
        # Clip road network to site boundary
        if not road_network.is_empty:
            road_network = road_network.intersection(site_boundary)
            logger.info(f"[CLIP] Road network clipped to site boundary")
        
        # Clip all blocks to site boundary
        clipped_blocks = []
        for block_meta in blocks_with_metadata:
            block_geom = block_meta['geometry']
            clipped_geom = block_geom.intersection(site_boundary)
            
            # Skip if clipping removed too much (< 95% overlap)
            if clipped_geom.is_empty or clipped_geom.area < block_geom.area * 0.95:
                logger.warning(f"[CLIP] Block {block_meta['id']} outside boundary, skipped")
                continue
            
            # Update geometry
            block_meta['geometry'] = clipped_geom
            block_meta['area'] = clipped_geom.area
            clipped_blocks.append(block_meta)
        
        logger.info(f"[CLIP] {len(clipped_blocks)}/{len(blocks_with_metadata)} blocks kept after boundary clipping")
        
        # Clip landscape features to boundary
        clipped_landscape = []
        for feature in landscape_features:
            feature_geom = feature['geometry']
            clipped_feat = feature_geom.intersection(site_boundary)
            
            if not clipped_feat.is_empty and clipped_feat.area > 200:
                feature['geometry'] = clipped_feat
                feature['area'] = clipped_feat.area
                clipped_landscape.append(feature)
        
        logger.info(f"[CLIP] {len(clipped_landscape)}/{len(landscape_features)} landscape features kept after clipping")
        
        # ========================================
        # RETURN RESULTS (ALL CLIPPED)
        # ========================================
        return road_network, clipped_blocks, clipped_landscape
    
    else:
        # Fallback for invalid geometry
        logger.error("[HIERARCHICAL] Invalid working area geometry")
        return site_boundary, [], []


def classify_block_hierarchical(
    block_meta: Dict[str, Any],
    site_bounds: tuple,
    total_blocks: int
) -> str:
    """
    Classify block based on hierarchical position
    
    More sophisticated than simple position:
    - Blocks near entrance → WAREHOUSE/LOGISTICS
    - Large central blocks → FACTORY
    - Small edge blocks → SERVICE
    
    Args:
        block_meta: Block metadata dict
        site_bounds: Site boundary tuple (minx, miny, maxx, maxy)
        total_blocks: Total number of blocks
        
    Returns:
        Zone type: FACTORY, WAREHOUSE, or SERVICE
    """
    area = block_meta['area']
    entrance_dist = block_meta['entrance_distance']
    
    minx, miny, maxx, maxy = site_bounds
    max_entrance_dist = maxy - miny
    
    # Normalize entrance distance (0 = near entrance, 1 = far from entrance)
    norm_entrance_dist = entrance_dist / max_entrance_dist if max_entrance_dist > 0 else 0.5
    
    # Classification logic:
    # 1. Large blocks (>20,000m²) → FACTORY
    # 2. Near entrance (<30% from bottom) → WAREHOUSE
    # 3. Small blocks (<5,000m²) → SERVICE
    # 4. Default → WAREHOUSE
    
    if area > 20000:
        return 'FACTORY'
    elif norm_entrance_dist < 0.3:
        return 'WAREHOUSE'
    elif area < 5000:
        return 'SERVICE'
    else:
        # Medium blocks in middle/back → FACTORY
        if norm_entrance_dist > 0.5:
            return 'FACTORY'
        else:
            return 'WAREHOUSE'
