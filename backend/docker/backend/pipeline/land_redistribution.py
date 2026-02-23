"""
Main land redistribution pipeline orchestration.

Coordinates all stages of the optimization pipeline:
1. Road network generation (Voronoi or Grid-based)
2. Block subdivision (OR-Tools)
3. Infrastructure planning (MST, Transformers, Drainage)
"""

import logging
import random
from typing import List, Dict, Any, Tuple, Optional

import math
import numpy as np
from shapely.geometry import Polygon, Point, LineString, mapping
from shapely.ops import unary_union

from core.config.settings import (
    AlgorithmSettings, 
    DEFAULT_SETTINGS,
    ROAD_MAIN_WIDTH,
    ROAD_INTERNAL_WIDTH,  # This is usually the road width between blocks
    SIDEWALK_WIDTH,
    TURNING_RADIUS,
    SERVICE_AREA_RATIO,
    MIN_BLOCK_AREA,
    ENABLE_LEFTOVER_MANAGEMENT,
    MIN_RECTANGULARITY,
    MAX_ASPECT_RATIO,
    MIN_LOT_AREA,
)
from core.geometry.polygon_utils import (
    get_elevation,
    normalize_geometry_list,
    filter_by_min_area,
    sort_by_elevation,
)
from core.geometry.shape_quality import (
    analyze_shape_quality,
    classify_lot_type,
    get_dominant_edge_vector,
)
from core.geometry.voronoi import (
    generate_voronoi_seeds,
    create_voronoi_diagram,
    extract_voronoi_edges,
    classify_road_type,
    create_road_buffer,
)
from core.optimization.grid_optimizer import GridOptimizer
from core.optimization.subdivision_solver import SubdivisionSolver
from core.infrastructure.network_planner import generate_loop_network
from core.infrastructure.transformer_planner import generate_transformers
from core.infrastructure.drainage_planner import calculate_drainage
from core.road_network import generate_skeleton_roads

# Import amenities generators
try:
    from core.amenities.water_generator import create_lakes, create_water_feature
    from core.amenities.central_park import create_central_park, find_road_intersections
    from core.landscape import add_green_buffers_to_layout
    from core.amenities.parking_generator import generate_parking_areas
    HAS_AMENITIES = True
except ImportError:
    HAS_AMENITIES = False

# Import advanced zoning and road generation
try:
    from core.zoning.advanced_classifier import AdvancedZoneClassifier
    from core.roads.hierarchical_network import HierarchicalRoadNetwork
    HAS_ADVANCED_FEATURES = True
except ImportError:
    HAS_ADVANCED_FEATURES = False
    logger.warning("Advanced zoning/road features not available")

logger = logging.getLogger(__name__)

# Zone colors for frontend visualization (RGB hex)
ZONE_COLORS = {
    'FACTORY': '#E53935',      # Red - Industrial factories
    'WAREHOUSE': '#FB8C00',    # Orange - Storage/logistics
    'RESIDENTIAL': '#FDD835',  # Yellow - Worker housing
    'SERVICE': '#78909C',      # Blue-gray - Utilities, amenities
    'GREEN': '#43A047',        # Green - Parks, buffer zones
    'WATER': '#1E88E5',        # Blue - Lakes, ponds
}


def is_geographic_coords(polygon: Polygon) -> bool:
    """Check if polygon uses geographic coordinates (lat/lng) vs metric."""
    bounds = polygon.bounds
    # Geographic coordinates typically: lng in [-180, 180], lat in [-90, 90]
    # Metric coordinates typically much larger (hundreds to thousands)
    minx, miny, maxx, maxy = bounds
    return (abs(minx) <= 180 and abs(maxx) <= 180 and 
            abs(miny) <= 90 and abs(maxy) <= 90)


def project_to_metric(polygon: Polygon) -> Polygon:
    """
    Project geographic coordinates to metric using simple approximation.
    At latitude ~11° (Vietnam), 1° ≈ 111km
    """
    from shapely.affinity import scale
    
    # Get centroid latitude for scaling factor
    centroid = polygon.centroid
    lat = centroid.y
    
    # Meters per degree
    # Latitude: always ~111,320 meters per degree
    # Longitude: varies by latitude, ~111,320 * cos(lat)
    meters_per_deg_lat = 111320
    meters_per_deg_lng = 111320 * math.cos(math.radians(lat))
    
    # Scale polygon
    # Note: scale origin should be polygon centroid
    scaled = scale(polygon, 
                   xfact=meters_per_deg_lng, 
                   yfact=meters_per_deg_lat,
                   origin=(centroid.x, centroid.y))
    
    logger.info(f"[PROJECTION] Geographic -> Metric: {polygon.area:.6f} deg² -> {scaled.area:.2f} m²")
    return scaled


def project_to_geographic(polygon: Polygon, reference_lat: float = 10.896340, reference_lng: float = 106.755053) -> Polygon:
    """
    Project metric coordinates back to geographic (reverse of project_to_metric).
    Uses reference point to determine scale factors.
    """
    from shapely.affinity import scale
    
    # Meters per degree at reference latitude
    meters_per_deg_lat = 111320
    meters_per_deg_lng = 111320 * math.cos(math.radians(reference_lat))
    
    # Get centroid for scaling origin
    centroid = polygon.centroid
    
    # Inverse scale factors
    scaled = scale(polygon,
                   xfact=1.0 / meters_per_deg_lng,
                   yfact=1.0 / meters_per_deg_lat,
                   origin=(centroid.x, centroid.y))
    
    logger.debug(f"[PROJECTION] Metric -> Geographic: {polygon.area:.2f} m² -> {scaled.area:.9f} deg²")
    return scaled


class LandRedistributionPipeline:
    """
    Main pipeline orchestrating all optimization stages.
    
    Supports two modes:
    1. Voronoi-based road network (default, more organic layout)
    2. Grid-based optimization using NSGA-II (fallback)
    """
    
    def __init__(
        self, 
        land_polygons: List[Polygon], 
        config: Dict[str, Any],
        settings: Optional[AlgorithmSettings] = None
    ):
        """
        Initialize pipeline.
        
        Args:
            land_polygons: Input land plots
            config: API configuration dictionary
            settings: Algorithm settings (optional)
        """
        merged = unary_union(land_polygons)
        
        # Auto-detect and project geographic coordinates to metric
        self.is_geographic = is_geographic_coords(merged)
        if self.is_geographic:
            logger.info("[PIPELINE] Detected geographic coordinates, projecting to metric...")
            # Store reference point and scale factors for reverse projection
            centroid = merged.centroid
            self.reference_lat = centroid.y
            self.reference_lng = centroid.x
            # Calculate and store scale factors
            self.meters_per_deg_lat = 111320
            self.meters_per_deg_lng = 111320 * math.cos(math.radians(self.reference_lat))
            logger.info(f"[PIPELINE] Scale factors: lng={self.meters_per_deg_lng:.2f} m/deg, lat={self.meters_per_deg_lat:.2f} m/deg")
            self.land_poly = project_to_metric(merged)
        else:
            logger.info("[PIPELINE] Using metric coordinates as-is")
            self.land_poly = merged
            self.reference_lat = None
            self.reference_lng = None
            self.meters_per_deg_lat = None
            self.meters_per_deg_lng = None
            
        self.config = config
        self.settings = settings or AlgorithmSettings.from_dict(config)
        self.lake_poly = Polygon()  # No lake by default
        
        logger.info(f"Pipeline initialized with land area: {self.land_poly.area:.2f} m²")
    
    def to_geographic(self, geom):
        """Convert geometry back to geographic coordinates if input was geographic."""
        if not self.is_geographic or self.meters_per_deg_lat is None:
            return geom
        
        from shapely.affinity import scale, translate
        
        # Scale back to geographic degrees
        geog = scale(geom,
                     xfact=1.0 / self.meters_per_deg_lng,
                     yfact=1.0 / self.meters_per_deg_lat,
                     origin=(0, 0))
        
        # Translate back to reference position
        geog = translate(geog, xoff=self.reference_lng, yoff=self.reference_lat)
        
        return geog
    
    def generate_road_network(
        self, 
        num_branches: int = 8,
        use_hierarchical: bool = True
    ) -> Tuple[Polygon, List[Polygon], List[Polygon]]:
        """
        Generate road network using HIERARCHICAL SYSTEM (match reference design).
        
        New architecture:
        - Perimeter road (20m buffer)
        - Main divider roads (14m) creating 4-6 blocks
        - Strategic landscape features (parks, water)
        - Row-based lot subdivision
        
        Args:
            num_branches: Number of perpendicular branches (ignored, auto-calculated)
            use_hierarchical: Use new hierarchical network generator (default True)
            
        Returns:
            (road_network, service_blocks, commercial_blocks)
        """
        site = self.land_poly
        
        logger.info("=" * 60)
        logger.info("[ROAD] USING HIERARCHICAL ROAD SYSTEM (PROFESSIONAL DESIGN)")
        logger.info("=" * 60)
        
        try:
            from core.road_network.hierarchical_grid import (
                create_hierarchical_roads,
                classify_block_hierarchical
            )
            logger.info("[ROAD] ✓ Imported hierarchical_grid module")
        except ImportError as e:
            logger.error(f"[ROAD] ✗ Failed to import hierarchical_grid: {e}")
            # Fallback to simple grid
            from core.road_network.simple_grid import (
                create_simple_grid_roads,
                classify_block_by_position
            )
            logger.warning("[ROAD] Falling back to simple grid")
            network_poly, blocks = create_simple_grid_roads(site, num_branches=2)
            return network_poly, [], blocks
        
        logger.info(f"[ROAD] Site area: {site.area:.0f}m²")
        
        # Generate hierarchical road network
        try:
            network_poly, blocks_meta, landscape_features = create_hierarchical_roads(
                site_boundary=site,
                perimeter_width=20.0,
                main_width=14.0,
                secondary_width=7.0
            )
            logger.info(
                f"[ROAD] ✓ Generated {len(blocks_meta)} blocks, "
                f"{len(landscape_features)} landscape features"
            )
        except Exception as e:
            logger.error(f"[ROAD] ✗ Failed to generate hierarchical roads: {e}")
            import traceback
            traceback.print_exc()
            return Polygon(), [], [site]
        
        if not blocks_meta:
            logger.error("[ROAD] ✗ No blocks generated!")
            return Polygon(), [], [site]
        
        # Classify blocks and prepare for subdivision
        commercial_blocks = []
        service_blocks = []
        
        site_bounds = site.bounds
        total_blocks = len(blocks_meta)
        
        for block_meta in blocks_meta:
            try:
                # Classify block
                zone_type = classify_block_hierarchical(
                    block_meta, 
                    site_bounds,
                    total_blocks
                )
                
                # Store zone type in block metadata
                block_meta['zone'] = zone_type
                
                # All blocks go to commercial (will be subdivided)
                commercial_blocks.append(block_meta['geometry'])
                
                logger.info(
                    f"[ROAD] Block {block_meta['id']}: zone={zone_type}, "
                    f"area={block_meta['area']:.0f}m²"
                )
            except Exception as e:
                logger.error(f"[ROAD] Failed to classify block {block_meta['id']}: {e}")
        
        # Store landscape features for later export
        self.landscape_features = landscape_features
        
        # Store block metadata for subdivision
        self.blocks_metadata = blocks_meta
        
        logger.info(
            f"[ROAD] ✓ Generated {len(commercial_blocks)} blocks "
            f"for row-based subdivision"
        )
        logger.info("=" * 60)
        
        return network_poly, service_blocks, commercial_blocks
        
        # OLD COMPLEX LOGIC DISABLED
        if False and use_hierarchical and HAS_ADVANCED_FEATURES:
            try:
                network_gen = HierarchicalRoadNetwork(
                    site_boundary=site,
                    main_width=self.settings.road.main_width,
                    branch_width=self.settings.road.internal_width,
                    tertiary_width=8.0
                )
                
                result = network_gen.generate_complete_network(
                    num_branches=num_branches,
                    add_roundabouts=True
                )
                
                # Extract roads
                road_lines = result['main_roads'] + result['branch_roads']
                
                # Store roundabouts for later use
                self.roundabouts = result['roundabouts']
                
                logger.info(
                    f"[HIERARCHICAL] Generated {len(road_lines)} roads, "
                    f"{len(self.roundabouts)} roundabouts"
                )
                
            except Exception as e:
                logger.warning(f"Hierarchical network failed: {e}, falling back")
                use_hierarchical = False
        
        # Fallback to skeleton-based roads
        if not use_hierarchical or not HAS_ADVANCED_FEATURES:
            road_lines = generate_skeleton_roads(
                site_boundary=site,
                num_branches=num_branches,
                min_road_length=50.0
            )
            self.roundabouts = []
        
        if not road_lines:
            logger.warning("Road generation failed, returning empty")
            return Polygon(), [], [site]
        
        logger.info(f"[ROAD] Generated {len(road_lines)} road segments")
        
        # Create road buffers - MINIMIZED to match reference design
        road_polys = []
        # Main roads: 8m (like reference)
        # Branches: 6m (like reference)
        main_width = 8.0
        branch_width = 6.0
        
        for idx, line in enumerate(road_lines):
            # First road is main spine - wider
            width = main_width if idx == 0 else branch_width
            road_buffer = line.buffer(width / 2, cap_style=2)
            road_polys.append(road_buffer)
        
        if not road_polys:
            return Polygon(), [], [site]
        
        # Merge road network
        network_poly = unary_union(road_polys)
        
        # DISABLED turning radius smoothing to preserve space for lots
        # smooth_network = network_poly.buffer(
        #     TURNING_RADIUS, join_style=1
        # ).buffer(-TURNING_RADIUS, join_style=1)
        smooth_network = network_poly  # Use raw network
        
        # Extract blocks (land minus roads)
        blocks_rough = site.difference(smooth_network)
        candidates = normalize_geometry_list(blocks_rough)
        
        # Filter by minimum area
        valid_blocks = filter_by_min_area(candidates, MIN_BLOCK_AREA)
        
        if not valid_blocks:
            return smooth_network, [], []
        
        # Sort by elevation (lowest first for WWTP)
        sorted_blocks = sort_by_elevation(valid_blocks)
        
        # Allocate service areas (10% of total)
        total_area = sum(b.area for b in valid_blocks)
        service_target = total_area * SERVICE_AREA_RATIO
        
        service_blocks = []
        commercial_blocks = []
        accumulated = 0.0
        
        for block in sorted_blocks:
            if accumulated < service_target:
                service_blocks.append(block)
                accumulated += block.area
            else:
                commercial_blocks.append(block)
        
        # Ensure at least one commercial block
        if not commercial_blocks and service_blocks:
            commercial_blocks.append(service_blocks.pop())
        
        logger.info(f"Road network: {len(service_blocks)} service, {len(commercial_blocks)} commercial blocks")
        
        # Store road lines for zone classification
        self.road_lines = road_lines
        
        return smooth_network, service_blocks, commercial_blocks
    
    def run_stage1(self) -> Dict[str, Any]:
        """Run grid optimization stage (NSGA-II) with orthogonal alignment."""
        
        # Calculate dominant edge angle for orthogonal alignment
        # This addresses User feedback about "uneven blocks" in Stage 1
        dom_vec = get_dominant_edge_vector(self.land_poly)
        # atan2 returns radians between -pi and pi
        fixed_angle = math.degrees(math.atan2(dom_vec[1], dom_vec[0]))
        
        logger.info(f"Enforcing orthogonal alignment: {fixed_angle:.2f} degrees (Vector: {dom_vec})")
        
        optimizer = GridOptimizer(
            self.land_poly, 
            self.lake_poly, 
            fixed_angle=fixed_angle,
            settings=self.settings.optimization
        )
        
        best_solution, history = optimizer.optimize(
            population_size=self.config.get('population_size', 30),
            generations=self.config.get('generations', 15)
        )
        
        spacing, angle = best_solution
        blocks = optimizer.generate_grid_candidates(spacing, angle)
        
        # Filter to usable blocks and apply road buffer
        usable_blocks = []
        road_width = self.config.get('road_width', ROAD_INTERNAL_WIDTH)
        buffer_amount = -road_width / 2.0
        
        for blk in blocks:
            # Intersect with land
            intersection = blk.intersection(self.land_poly).difference(self.lake_poly)
            
            if not intersection.is_empty and intersection.area > MIN_BLOCK_AREA:
                # Apply negative buffer to create road gaps
                # simplify(0.1) helps clean up artifacts after buffering
                buffered_blk = intersection.buffer(buffer_amount, join_style=2).simplify(0.1)
                
                if not buffered_blk.is_empty:
                    if buffered_blk.geom_type == 'Polygon':
                         if buffered_blk.area > MIN_BLOCK_AREA:
                            usable_blocks.append(buffered_blk)
                    elif buffered_blk.geom_type == 'MultiPolygon':
                        for part in buffered_blk.geoms:
                            if part.area > MIN_BLOCK_AREA:
                                usable_blocks.append(part)
        
        return {
            'spacing': spacing,
            'angle': angle,
            'blocks': usable_blocks,
            'history': history,
            'metrics': {
                'total_blocks': len(usable_blocks),
                'optimal_spacing': spacing,
                'optimal_angle': angle
            }
        }
    
    def run_stage2(
        self, 
        blocks: List[Polygon], 
        spacing: float,
        zones: Dict[Polygon, str] = None,
        main_roads: List[LineString] = None
    ) -> Dict[str, Any]:
        """Run subdivision stage (OR-Tools) with leftover management and zone-specific configs."""
        logger.info(f"[RUN_STAGE2] Called with {len(blocks)} blocks")
        all_lots = []
        parks = []
        green_spaces = []  # NEW: collect poor-quality lots (Beauti_mode Section 3)
        
        # Auto-classify zones if not provided
        if zones is None:
            from core.road_network.simple_grid import classify_block_by_position
            
            zones = {}
            for block in blocks:
                # Use position-based classification
                zones[block] = classify_block_by_position(
                    block, 
                    self.land_poly,
                    main_roads
                )
        
        for block_idx, block in enumerate(blocks):
            # Get zone type for this block
            zone_type = zones.get(block, 'WAREHOUSE')  # Default to warehouse
            
            # Special handling for GREEN zones - don't subdivide, use as-is
            if zone_type == 'GREEN':
                green_spaces.append(block)
                logger.info(f"GREEN zone preserved (area={block.area:.0f}m²)")
                continue
            
            # Select appropriate config based on zone
            if zone_type == 'FACTORY':
                min_width = self.settings.subdivision.factory_config.min_lot_width
                max_width = self.settings.subdivision.factory_config.max_lot_width
                target_width = self.settings.subdivision.factory_config.target_lot_width
            elif zone_type == 'WAREHOUSE':
                min_width = self.settings.subdivision.warehouse_config.min_lot_width
                max_width = self.settings.subdivision.warehouse_config.max_lot_width
                target_width = self.settings.subdivision.warehouse_config.target_lot_width
            elif zone_type == 'RESIDENTIAL':
                min_width = self.settings.subdivision.residential_config.min_lot_width
                max_width = self.settings.subdivision.residential_config.max_lot_width
                target_width = self.settings.subdivision.residential_config.target_lot_width
            elif zone_type == 'SERVICE':
                min_width = self.config.get('min_lot_width', 30.0)
                max_width = self.config.get('max_lot_width', 60.0)
                target_width = self.config.get('target_lot_width', 45.0)
            else:  # Default fallback
                min_width = self.config.get('min_lot_width', 40.0)
                max_width = self.config.get('max_lot_width', 80.0)
                target_width = self.config.get('target_lot_width', 60.0)
            
            logger.info(f"Subdividing block (area={block.area:.0f}m², zone={zone_type}, width={min_width}-{max_width}m)")
            
            # USE ROW-BASED SUBDIVISION (professional layout)
            try:
                from core.optimization.row_subdivider import (
                    subdivide_block_rows,
                    get_target_dimensions_for_zone
                )
                
                # Get zone-specific dimensions
                target_width, target_depth = get_target_dimensions_for_zone(zone_type)
                
                logger.info(
                    f"[SUBDIVISION] Using ROW subdivider for {zone_type} "
                    f"({target_width}x{target_depth}m lots)"
                )
                
                # Create lots in neat rows with internal roads
                lots_list = subdivide_block_rows(
                    block,
                    zone_type=zone_type,
                    target_lot_width=target_width,
                    target_lot_depth=target_depth,
                    internal_road_width=6.0
                )
                
                logger.info(f"[SUBDIVISION] ✓ Generated {len(lots_list)} lots")
                
                # Convert to expected format
                result = {
                    'type': 'lots',
                    'lots': lots_list
                }
                
            except Exception as e:
                logger.error(f"[SUBDIVISION] Failed: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # OLD OR-Tools approach DISABLED
            if False:
                result = SubdivisionSolver.subdivide_block(
                    block,
                    spacing,
                    min_width,
                    max_width,
                    target_width,
                    self.config.get('ortools_time_limit', 5)
                )
            
            if result['type'] == 'park':
                parks.append(result['geometry'])
            else:
                # All lots in this block inherit the block's zone
                # This creates clear zone clusters like reference design
                block_total = len(result['lots'])
                kept_count = 0
                green_count = 0
                
                for lot_info in result['lots']:
                    lot_geom = lot_info['geometry']
                    
                    # Inherit zone from parent block
                    # This creates coherent zones like reference
                    lot_zone = zone_type
                    
                    if ENABLE_LEFTOVER_MANAGEMENT:
                        lot_type = classify_lot_type(
                            lot_geom,
                            min_rectangularity=MIN_RECTANGULARITY,
                            max_aspect_ratio=MAX_ASPECT_RATIO,
                            min_area=MIN_LOT_AREA
                        )
                        
                        if lot_type == 'commercial':
                            lot_info['zone'] = lot_zone
                            lot_info['zone_color'] = ZONE_COLORS.get(
                                lot_zone, '#9E9E9E'
                            )
                            lot_info['block_id'] = block_idx  # ADD BLOCK ID FOR PARKING
                            all_lots.append(lot_info)
                            kept_count += 1
                        elif lot_type == 'green_space':
                            green_spaces.append(lot_geom)
                            green_count += 1
                    else:
                        lot_info['zone'] = lot_zone
                        lot_info['zone_color'] = ZONE_COLORS.get(
                            lot_zone, '#9E9E9E'
                        )
                        lot_info['block_id'] = block_idx  # ADD BLOCK ID FOR PARKING
                        all_lots.append(lot_info)
                        kept_count += 1
                
                if block_total > 0:
                    logger.info(
                        f"Block {zone_type}: Generated {block_total} lots "
                        f"-> Kept {kept_count}, {green_count} green"
                    )

        # Calculate average width safely (some lots may not have width field)
        lots_with_width = [lot['width'] for lot in all_lots if 'width' in lot]
        avg_width = np.mean(lots_with_width) if lots_with_width else 0
        
        return {
            'lots': all_lots,
            'parks': parks,
            'green_spaces': green_spaces,  # NEW field
            'metrics': {
                'total_lots': len(all_lots),
                'total_parks': len(parks),
                'total_green_spaces': len(green_spaces),
                'avg_lot_width': avg_width
            }
        }
    
    def classify_block_zone(
        self,
        block: Polygon,
        main_roads: List[LineString],
        all_blocks: List[Polygon] = None
    ) -> str:
        """Classify a block into functional zones using advanced classifier.
        
        Uses AdvancedZoneClassifier if available, otherwise falls back to
        simple classification based on area, position, and distance to roads.
        
        Args:
            block: Block polygon to classify
            main_roads: List of main road linestrings
            all_blocks: All blocks for context-aware classification
            
        Returns:
            Zone type: 'FACTORY', 'WAREHOUSE', 'RESIDENTIAL', 'SERVICE', 'GREEN', or 'WATER'
        """
        # Use advanced classifier if available
        if HAS_ADVANCED_FEATURES:
            if not hasattr(self, '_zone_classifier') or self._zone_classifier is None:
                self._zone_classifier = AdvancedZoneClassifier(self.land_poly)
            
            return self._zone_classifier.classify_block(block, main_roads, all_blocks)
        
        # Fallback to simple classification
        from shapely.ops import unary_union
        
        area = block.area
        centroid = block.centroid
        
        # Calculate distance to main roads
        if main_roads:
            main_roads_union = unary_union(main_roads)
            distance_to_main = block.distance(main_roads_union)
        else:
            distance_to_main = 0
        
        # Calculate position relative to site
        site_centroid = self.land_poly.centroid
        distance_to_center = centroid.distance(site_centroid)
        
        # Normalize by site size (0 = center, 1 = edge)
        site_bounds = self.land_poly.bounds
        site_diagonal = ((site_bounds[2] - site_bounds[0])**2 + 
                         (site_bounds[3] - site_bounds[1])**2) ** 0.5
        relative_position = min(1.0, distance_to_center / (site_diagonal / 2))
        
        # Distance to site boundary (for buffer detection)
        distance_to_boundary = block.distance(self.land_poly.exterior)
        
        # Corner detection
        corners = [
            Point(site_bounds[0], site_bounds[1]),  # SW
            Point(site_bounds[2], site_bounds[1]),  # SE
            Point(site_bounds[2], site_bounds[3]),  # NE
            Point(site_bounds[0], site_bounds[3]),  # NW
        ]
        near_corner = any(centroid.distance(c) < site_diagonal * 0.15 for c in corners)
        
        # QCVN-balanced classification (theo QCVN 01:2021/BXD)
        # Target: FACTORY (40%), WAREHOUSE (30%), SERVICE (25%), GREEN (5%)
        # KHÔNG có RESIDENTIAL trong KCN (phải nằm ngoài buffer zone)
        
        # 1. GREEN zones - perimeter buffer và góc khu đất
        if distance_to_boundary < 20 and area < 6000:
            return 'GREEN'
        
        if area < 2500 and (distance_to_boundary < 30 or near_corner):
            return 'GREEN'
        
        # 2. SERVICE zones - administrative, utilities, dịch vụ hỗ trợ
        # Tăng allocation để đủ 25%
        if area < 10000 and relative_position < 0.35:
            return 'SERVICE'
        
        if 3000 <= area < 12000 and distance_to_main < 60:
            return 'SERVICE'
        
        # 3. FACTORY zones - sản xuất nặng, ưu tiên core area
        if area >= 18000 and distance_to_main < 50 and relative_position < 0.45:
            return 'FACTORY'
        
        if area >= 22000 and distance_to_main < 65:
            return 'FACTORY'
        
        # 4. WAREHOUSE zones - logistics, kho bãi
        if 9000 <= area < 18000 and distance_to_main < 75:
            return 'WAREHOUSE'
        
        if 12000 <= area < 22000 and distance_to_main < 55:
            return 'WAREHOUSE'
        
        # 5. Mixed classification theo vị trí
        if area >= 10000:
            if distance_to_main < 40 and relative_position < 0.4:
                return 'FACTORY'  # Core industrial
            elif distance_to_main < 70:
                return 'WAREHOUSE'  # Mid-zone logistics
            else:
                return 'SERVICE'  # Peripheral support
        
        if area >= 5000:
            if distance_to_main < 45:
                return 'SERVICE'
            else:
                return 'WAREHOUSE'
        
        # Default: SERVICE cho small blocks
        return 'SERVICE'
    
    def classify_blocks(
        self, 
        blocks: List[Polygon]
    ) -> Dict[str, List[Polygon]]:
        """Classify blocks into service and commercial categories."""
        if not blocks:
            return {'service': [], 'commercial': [], 'xlnt': []}
        
        sorted_blocks = sort_by_elevation(blocks)
        
        total_area = sum(b.area for b in blocks)
        service_target = total_area * SERVICE_AREA_RATIO
        accumulated = 0.0
        
        xlnt_block = []
        service_blocks = []
        commercial_blocks = []
        
        # Lowest block is XLNT (Wastewater Treatment)
        if sorted_blocks:
            xlnt = sorted_blocks.pop(0)
            xlnt_block.append(xlnt)
            accumulated += xlnt.area
        
        # Fill remaining service quota
        # Distribute service blocks (Interleave)
        # Instead of taking the first N blocks, we distribute them evenly
        # to avoid "clumping" of service areas.
        
        remaining_blocks = sorted_blocks  # These are already sorted by elevation (low -> high)
        num_remaining = len(remaining_blocks)
        
        if num_remaining > 0:
            # Calculate how many service blocks we need
            # We use checks against area, but let's approximate by count for mixing
            avg_area = sum(b.area for b in remaining_blocks) / num_remaining
            service_count = int(service_target / avg_area)
            service_count = max(1, min(service_count, int(num_remaining * 0.3))) # Cap at 30%
            
            if service_count >= num_remaining:
                 service_blocks.extend(remaining_blocks)
                 logger.warning(f"Classification: All {num_remaining} blocks assigned to Service (Count={service_count})")
            else:
                # Step size for distribution
                step = num_remaining / service_count
                indices = [int(i * step) for i in range(service_count)]
                
                logger.info(f"Classification: Total={num_remaining}, ServiceTarget={service_count}, Step={step:.2f}")
                
                for i, block in enumerate(remaining_blocks):
                    if i in indices:
                        service_blocks.append(block)
                    else:
                        commercial_blocks.append(block)
        else:
             # Should not happen if blocks exist
             pass
        
        logger.info(f"Classification Result: XLNT={len(xlnt_block)}, Service={len(service_blocks)}, Commercial={len(commercial_blocks)}")
        
        return {
            'xlnt': xlnt_block,
            'service': service_blocks,
            'commercial': commercial_blocks
        }
    
    @staticmethod
    def _safe_coords(geom):
        """Helper to safely extract coordinates for JSON serialization."""
        if geom.geom_type == 'Polygon':
            return list(geom.exterior.coords)
        elif geom.geom_type == 'MultiPolygon':
            # Return exterior of the largest part
            largest = max(geom.geoms, key=lambda p: p.area)
            return list(largest.exterior.coords)
        return []

    def run_full_pipeline(
        self, 
        layout_method: str = 'auto',  # 'auto', 'skeleton', 'voronoi', 'grid'
        num_seeds: int = 15,
        num_branches: int = 8
    ) -> Dict[str, Any]:
        """
        Run complete optimization pipeline.
        
        Args:
            layout_method: Strategy for road network ('skeleton', 'voronoi', or 'grid')
            num_seeds: Number of seeds for Voronoi generation
            num_branches: Number of branches for Skeleton generation
        """
        logger.info(f"Starting full pipeline with method: {layout_method}")
        
        road_network = Polygon()
        service_blocks_voronoi = []
        commercial_blocks_voronoi = []
        xlnt_blocks = []
        spacing_for_subdivision = 25.0
        
        # Stage 0: Skeleton/Voronoi Road Network (if selected)
        if layout_method in ['auto', 'skeleton', 'voronoi']:
            if layout_method in ['auto', 'skeleton']:
                road_network, service_blocks_voronoi, commercial_blocks_voronoi = \
                    self.generate_road_network(num_branches=num_branches)
            else:
                road_network, service_blocks_voronoi, commercial_blocks_voronoi = \
                    self.generate_road_network(num_seeds=num_seeds)
        
        # Determine if we should use Grid (fallback or forced)
        use_grid = False
        if layout_method == 'grid':
            use_grid = True
        elif layout_method == 'auto' and not commercial_blocks_voronoi:
            logger.info("Voronoi failed or produced no blocks, switching to grid-based")
            use_grid = True

        if use_grid:
            logger.info("Using Grid-based generation (Stage 1)")
            stage1_result = self.run_stage1()
            classification = self.classify_blocks(stage1_result['blocks'])
            commercial_blocks_voronoi = classification['commercial']
            service_blocks_voronoi = classification['service']
            xlnt_blocks = classification['xlnt']
            all_blocks = stage1_result['blocks']
            road_network = self.land_poly.difference(unary_union(all_blocks))
            spacing_for_subdivision = stage1_result['spacing']
        else:
            # Separate XLNT from service blocks for Voronoi path
            if service_blocks_voronoi:
                xlnt_blocks = [service_blocks_voronoi[0]]
                service_blocks_voronoi = service_blocks_voronoi[1:]
            
            # Estimate spacing for subdivision
            if commercial_blocks_voronoi:
                # Use a heuristic for Voronoi block spacing
                avg_area = sum(b.area for b in commercial_blocks_voronoi) / len(commercial_blocks_voronoi)
                spacing_for_subdivision = max(20.0, (avg_area ** 0.5) * 0.7)
            else:
                spacing_for_subdivision = 25.0
        
        # Stage 2: Subdivision with zone classification
        # Pass main roads for zone classification
        main_roads = getattr(self, 'road_lines', [])
        logger.info(f"[PIPELINE] About to call run_stage2 with {len(commercial_blocks_voronoi)} blocks")
        
        # IMPORTANT: Only subdivide if we have blocks
        if not commercial_blocks_voronoi:
            logger.warning("[PIPELINE] No commercial blocks available for subdivision!")
            stage2_result = {
                'lots': [],
                'parks': [],
                'green_spaces': [],
                'metrics': {
                    'total_lots': 0,
                    'total_parks': 0,
                    'total_green_spaces': 0,
                    'avg_lot_width': 0
                }
            }
        else:
            # Classify zones BEFORE subdivision to preserve FACTORY/WAREHOUSE distinction
            block_zones = {}
            zone_counts = {'FACTORY': 0, 'WAREHOUSE': 0, 'SERVICE': 0, 'RESIDENTIAL': 0, 'GREEN': 0}
            
            for block in commercial_blocks_voronoi:
                zone = self.classify_block_zone(block, main_roads, commercial_blocks_voronoi)
                block_zones[block] = zone
                zone_counts[zone] = zone_counts.get(zone, 0) + 1
                logger.info(f"[ZONE] Block {commercial_blocks_voronoi.index(block)}: {zone} ({block.area:.0f}m²)")
            
            # Log zone distribution
            total_blocks = len(commercial_blocks_voronoi)
            logger.info(f"[ZONE DISTRIBUTION] "
                       f"FACTORY: {zone_counts.get('FACTORY', 0)}/{total_blocks} ({zone_counts.get('FACTORY', 0)/total_blocks*100:.1f}%), "
                       f"WAREHOUSE: {zone_counts.get('WAREHOUSE', 0)}/{total_blocks} ({zone_counts.get('WAREHOUSE', 0)/total_blocks*100:.1f}%), "
                       f"SERVICE: {zone_counts.get('SERVICE', 0)}/{total_blocks} ({zone_counts.get('SERVICE', 0)/total_blocks*100:.1f}%), "
                       f"GREEN: {zone_counts.get('GREEN', 0)}/{total_blocks}")
            
            # Balance zones (QCVN compliance - KHÔNG có RESIDENTIAL trong KCN)
            # Target: FACTORY ~40%, WAREHOUSE ~30%, SERVICE ~25%, GREEN ~5%
            factory_target = int(total_blocks * 0.40)
            warehouse_target = int(total_blocks * 0.30)
            service_target = int(total_blocks * 0.25)
            
            # Rebalance FACTORY if too many
            if zone_counts.get('FACTORY', 0) > factory_target * 1.3:
                logger.info(f"[ZONE REBALANCE] Too many FACTORY ({zone_counts['FACTORY']}), converting to WAREHOUSE")
                factory_blocks = [b for b, z in block_zones.items() if z == 'FACTORY']
                sorted_factories = sorted(factory_blocks, key=lambda b: b.centroid.distance(self.land_poly.centroid), reverse=True)
                excess = zone_counts['FACTORY'] - factory_target
                for i in range(min(excess, len(sorted_factories))):
                    block_zones[sorted_factories[i]] = 'WAREHOUSE'
            
            # Ensure minimum SERVICE zones (administrative, utilities)
            if zone_counts.get('SERVICE', 0) < service_target * 0.6:
                logger.info(f"[ZONE REBALANCE] Too few SERVICE ({zone_counts.get('SERVICE', 0)}), converting some WAREHOUSE")
                warehouse_blocks = [b for b, z in block_zones.items() if z == 'WAREHOUSE']
                sorted_warehouses = sorted(warehouse_blocks, key=lambda b: b.area)
                needed = service_target - zone_counts.get('SERVICE', 0)
                for i in range(min(needed, len(sorted_warehouses))):
                    block_zones[sorted_warehouses[i]] = 'SERVICE'
            
            stage2_result = self.run_stage2(
                commercial_blocks_voronoi,
                spacing_for_subdivision,
                zones=block_zones,  # Pass zones to preserve classification
                main_roads=main_roads
            )
        
        # Stage 2.5: Amenities (Lakes, Central Park, Roundabout)
        amenities = {'lakes': [], 'parks': [], 'roundabouts': [], 'landscape': {}}
        
        # Import landscape features from hierarchical road generator
        if hasattr(self, 'landscape_features') and self.landscape_features:
            logger.info(f"[LANDSCAPE] Using {len(self.landscape_features)} features from hierarchical generator")
            
            for feature in self.landscape_features:
                amenities['parks'].append({
                    'park_polygon': feature['geometry'],
                    'type': feature['type'],
                    'area': feature['area'],
                    'position': feature.get('position', 'unknown')
                })
                
                # Add to green_spaces for export
                stage2_result['green_spaces'].append(feature['geometry'])
            
            logger.info(f"[LANDSCAPE] Imported {len(self.landscape_features)} strategic parks/water features")
        
        if HAS_AMENITIES:
            logger.info("Generating amenities (lakes, parks, landscape)...")
            
            # === GREEN BUFFERS (QCVN 01:2021/BXD) ===
            # Add green separation buffers BEFORE other amenities
            try:
                logger.info("[GREEN BUFFERS] Adding QCVN-compliant separation buffers...")
                
                # Get all blocks for buffer generation
                all_blocks = commercial_blocks_voronoi + service_blocks_voronoi
                blocks_with_zones = []
                for block in all_blocks:
                    zone = self.classify_block_zone(block, main_roads, all_blocks)
                    blocks_with_zones.append({
                        'geometry': block,
                        'zone': zone
                    })
                
                # Add green buffers (30m perimeter + 20m between zones)
                green_buffer_result = add_green_buffers_to_layout(
                    final_layout={'lots': stage2_result['lots'], 'blocks': blocks_with_zones},
                    site_boundary=self.land_poly,
                    perimeter_buffer_width=self.settings.validation.perimeter_buffer_width,  # 30m
                    zone_buffer_width=self.settings.validation.green_buffer_width  # 20m
                )
                
                # Add all green buffers to amenities
                if 'green_buffers' in green_buffer_result:
                    for buffer in green_buffer_result['green_buffers']:
                        amenities['parks'].append({
                            'park_polygon': buffer['geometry'],
                            'type': buffer['type'],  # 'perimeter_buffer' or 'zone_separation'
                            'area': buffer['area']
                        })
                        stage2_result['green_spaces'].append(buffer['geometry'])
                    
                    logger.info(
                        f"[GREEN BUFFERS] Added {len(green_buffer_result['green_buffers'])} buffers "
                        f"(total area: {sum(b['area'] for b in green_buffer_result['green_buffers']):.0f}m²)"
                    )
                
            except Exception as e:
                logger.warning(f"[GREEN BUFFERS] Failed to add green buffers: {e}")
            
            # Create lakes at strategic positions (WATER features)
            try:
                all_blocks = commercial_blocks_voronoi + service_blocks_voronoi
                lakes = create_lakes(
                    site=self.land_poly,
                    blocks=all_blocks,
                    num_lakes=min(4, len(all_blocks) // 15),  # Scale with site size
                    lake_size_ratio=0.02  # Slightly larger for visibility
                )
                amenities['lakes'] = lakes
                
                # Add lakes to stage2 green_spaces for output
                for lake in lakes:
                    stage2_result['green_spaces'].append(lake['geometry'])
                
                logger.info(f"[WATER] Created {len(lakes)} water features")
            except Exception as e:
                logger.warning(f"[WATER] Failed to create lakes: {e}")
                amenities['lakes'] = []
            
            # Create central park with roundabout at main intersection
            if main_roads:
                intersections = find_road_intersections(main_roads)
                if intersections:
                    park_data = create_central_park(
                        site=self.land_poly,
                        road_intersections=intersections,
                        park_ratio=0.03,
                        include_roundabout=True
                    )
                    amenities['parks'].append(park_data)
                    
                    # Add park to green_spaces
                    if park_data.get('park_polygon'):
                        stage2_result['green_spaces'].append(park_data['park_polygon'])
                    
                    # Track roundabout
                    if park_data.get('roundabout'):
                        amenities['roundabouts'].append(park_data['roundabout'])
            
            # Enhanced landscape features - NOW with controlled sizing
            try:
                from core.amenities.landscape_generator import (
                    create_complete_landscape_package
                )
                
                # Organize blocks by zone for landscape planning
                zoned_blocks = {}
                for block in all_blocks:
                    zone = self.classify_block_zone(
                        block, main_roads, all_blocks
                    )
                    if zone not in zoned_blocks:
                        zoned_blocks[zone] = []
                    zoned_blocks[zone].append(block)
                
                # Generate landscape with reduced sizing (5m buffers)
                landscape = create_complete_landscape_package(
                    site_boundary=self.land_poly,
                    blocks=all_blocks,
                    zoned_blocks=zoned_blocks,
                    main_roads=main_roads
                )
                
                amenities['landscape'] = landscape
                
                # Add ONLY corner parks to green spaces
                # Skip perimeter buffers to preserve lot space
                corner_parks = landscape.get('corner_parks', [])
                stage2_result['green_spaces'].extend(corner_parks[:2])
                
                logger.info(
                    f"Landscape: {len(corner_parks)} parks added"
                )
                
            except ImportError as e:
                logger.warning(f"Enhanced landscape features unavailable: {e}")
        
        # DISABLED FOR DEBUGGING - SKIP ALL LANDSCAPE GENERATION
        logger.info("[DEBUG] Landscape generation DISABLED")
        if False:  # Completely disable
            logger.info(f"Created {len(lakes)} lakes, {len(amenities['parks'])} parks")
        
        # === CONSTRAINT: CLIP LOTS TO AVOID GREEN SPACES & WATER ===
        # Cut plots that overlap with green buffers, parks, or lakes
        logger.info("[CLIP] Applying green space constraints to lots...")
        
        # Collect ALL green spaces (green buffers + parks + lakes)
        all_green_spaces = stage2_result['green_spaces'].copy()
        
        if all_green_spaces:
            # Merge all green spaces into one unified polygon
            try:
                merged_green = unary_union(all_green_spaces)
                logger.info(f"[CLIP] Merged {len(all_green_spaces)} green spaces into constraint area: {merged_green.area:.0f}m²")
                
                # Clip each lot to remove overlap with green spaces
                clipped_lots = []
                clipped_count = 0
                removed_count = 0
                
                for lot in stage2_result['lots']:
                    lot_geom = lot['geometry']
                    
                    # Check if lot overlaps with green spaces
                    if lot_geom.intersects(merged_green):
                        # Cut away the overlapping part
                        clipped_geom = lot_geom.difference(merged_green)
                        
                        # Only keep if still has significant area (>100m²)
                        if clipped_geom.area > 100:
                            lot['geometry'] = clipped_geom
                            clipped_lots.append(lot)
                            clipped_count += 1
                        else:
                            # Lot became too small, remove it
                            removed_count += 1
                    else:
                        # No overlap, keep as-is
                        clipped_lots.append(lot)
                
                # Update lots list
                original_count = len(stage2_result['lots'])
                stage2_result['lots'] = clipped_lots
                
                logger.info(
                    f"[CLIP] Processed {original_count} lots: "
                    f"{clipped_count} clipped, {removed_count} removed (too small), "
                    f"{original_count - clipped_count - removed_count} unchanged"
                )
                
            except Exception as e:
                logger.warning(f"[CLIP] Failed to clip lots: {e}")
        else:
            logger.info("[CLIP] No green spaces to avoid, skipping constraint")
        
        # Collect all polygons for infrastructure
        all_network_nodes = stage2_result['lots'] + \
            [{'geometry': b, 'type': 'service'} for b in service_blocks_voronoi] + \
            [{'geometry': b, 'type': 'xlnt'} for b in xlnt_blocks]
        
        infra_polys = [item['geometry'] for item in all_network_nodes]
        
        # === PARKING GENERATION (QCVN 01:2021/BXD) ===
        parking_areas = []
        if HAS_AMENITIES:
            try:
                logger.info("[PARKING] Generating parking areas for lots...")
                parking_areas = generate_parking_areas(stage2_result['lots'], self.settings)
                logger.info(f"[PARKING] Generated {len(parking_areas)} parking areas")
            except Exception as e:
                logger.warning(f"[PARKING] Failed to generate parking: {e}")
        
        # Stage 3: Infrastructure
        points, connections = generate_loop_network(infra_polys)
        transformers = generate_transformers(infra_polys)
        
        wwtp_center = xlnt_blocks[0].centroid if xlnt_blocks else None
        drainage = calculate_drainage(infra_polys, wwtp_center)
        
        logger.info(f"Pipeline complete: {len(stage2_result['lots'])} lots, {len(connections)} connections")
        
        return {
            'stage1': {
                'blocks': commercial_blocks_voronoi + service_blocks_voronoi + xlnt_blocks,
                'metrics': {
                    'total_blocks': len(commercial_blocks_voronoi) + len(service_blocks_voronoi) + len(xlnt_blocks)
                },
                'spacing': spacing_for_subdivision,
                'angle': 0.0
            },
            'stage2': stage2_result,
            'classification': {
                'xlnt_count': len(xlnt_blocks),
                'service_count': len(service_blocks_voronoi),
                'commercial_count': len(commercial_blocks_voronoi),
                'xlnt': xlnt_blocks,
                'service': service_blocks_voronoi
            },
            'stage3': {
                'points': points,
                'connections': [list(line.coords) for line in connections],
                'drainage': drainage,
                'transformers': transformers,
                'road_network': mapping(road_network)
            },
            'amenities': {
                'lakes': [{'coords': self._safe_coords(l['geometry']), 'type': 'WATER', 'color': '#1E88E5'} 
                          for l in amenities.get('lakes', [])],
                'parks': [{'coords': self._safe_coords(p.get('park_polygon', Polygon())), 'type': 'GREEN', 'color': '#43A047'} 
                          for p in amenities.get('parks', []) if p.get('park_polygon')],
                'parking': [{'coords': self._safe_coords(p['geometry']), 'type': 'PARKING', 'color': '#BDBDBD', 'zone': p.get('zone', 'WAREHOUSE')} 
                            for p in parking_areas],
                'roundabouts': len(amenities.get('roundabouts', []))
            },
            'total_lots': stage2_result['metrics']['total_lots'],
            'service_blocks': [self._safe_coords(b) for b in service_blocks_voronoi],
            'xlnt_blocks': [self._safe_coords(b) for b in xlnt_blocks]
        }
