"""
Advanced Zoning Classifier for Industrial Estate Planning

Classifies blocks into functional zones based on:
1. Position (distance to center, boundary, corners)
2. Area (large factories vs small residential)
3. Distance to main roads (truck access)
4. Context (neighboring blocks, clustering)

Zones: FACTORY, WAREHOUSE, RESIDENTIAL, SERVICE, GREEN, WATER
"""

import logging
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

logger = logging.getLogger(__name__)


class AdvancedZoneClassifier:
    """
    Advanced classification of blocks into functional zones
    using multi-criteria analysis
    """
    
    def __init__(self, site_boundary: Polygon):
        """
        Initialize classifier with site context
        
        Args:
            site_boundary: The overall site polygon
        """
        self.site_boundary = site_boundary
        self.site_bounds = site_boundary.bounds
        self.site_centroid = site_boundary.centroid
        
        # Calculate site metrics
        width = self.site_bounds[2] - self.site_bounds[0]
        height = self.site_bounds[3] - self.site_bounds[1]
        self.site_diagonal = (width**2 + height**2) ** 0.5
        
        # Detect site orientation (horizontal vs vertical)
        # This adapts to rotated boundaries
        self.is_horizontal = width > height
        self.primary_dimension = max(width, height)
        self.secondary_dimension = min(width, height)
        
        logger.info(
            f"[CLASSIFIER] Site orientation: "
            f"{'HORIZONTAL' if self.is_horizontal else 'VERTICAL'} "
            f"({width:.0f}m x {height:.0f}m)"
        )
        
        # Corner points for corner detection
        self.corners = [
            Point(self.site_bounds[0], self.site_bounds[1]),  # SW
            Point(self.site_bounds[2], self.site_bounds[1]),  # SE
            Point(self.site_bounds[2], self.site_bounds[3]),  # NE
            Point(self.site_bounds[0], self.site_bounds[3]),  # NW
        ]
        
        # Zone thresholds (area in m²)
        self.VERY_LARGE_THRESHOLD = 20000  # 2 ha - Large factories
        self.LARGE_THRESHOLD = 10000       # 1 ha - Factories/Warehouses
        self.MEDIUM_THRESHOLD = 5000       # 0.5 ha - Warehouses/Service
        self.SMALL_THRESHOLD = 3000        # 0.3 ha - Green buffers
        
        # Distance thresholds (in meters)
        self.MAIN_ROAD_CLOSE = 60          # Close to main road
        self.MAIN_ROAD_MEDIUM = 100        # Medium distance
        self.BOUNDARY_BUFFER = 20          # Edge buffer zone
        self.CORNER_RADIUS = 0.15          # 15% of diagonal
        
        # Track assigned zones for balancing
        self.water_assigned = False
        self.entrance_detected = False
        self.entrance_side = None  # 'left', 'right', 'top', 'bottom'
    
    def _detect_entrance_side(self, main_roads: List[LineString]) -> str:
        """
        Detect which side of the site is the entrance based on main roads
        
        Args:
            main_roads: List of main road linestrings
            
        Returns:
            'left', 'right', 'top', or 'bottom'
        """
        if self.entrance_detected:
            return self.entrance_side
        
        if not main_roads:
            # Default: entrance at start of primary axis
            self.entrance_side = 'left' if self.is_horizontal else 'bottom'
            self.entrance_detected = True
            return self.entrance_side
        
        # Find which edge the main road is closest to
        bounds = self.site_bounds
        edges = {
            'left': LineString([(bounds[0], bounds[1]), (bounds[0], bounds[3])]),
            'right': LineString([(bounds[2], bounds[1]), (bounds[2], bounds[3])]),
            'bottom': LineString([(bounds[0], bounds[1]), (bounds[2], bounds[1])]),
            'top': LineString([(bounds[0], bounds[3]), (bounds[2], bounds[3])])
        }
        
        # Calculate average distance from main road to each edge
        edge_distances = {}
        main_road_union = unary_union(main_roads)
        
        for side, edge_line in edges.items():
            edge_distances[side] = edge_line.distance(main_road_union)
        
        # Entrance is on the side closest to main roads
        self.entrance_side = min(edge_distances, key=edge_distances.get)
        self.entrance_detected = True
        
        logger.info(
            f"[CLASSIFIER] Detected entrance: {self.entrance_side} "
            f"(distances: {edge_distances})"
        )
        
        return self.entrance_side
        
    def classify_block(
        self,
        block: Polygon,
        main_roads: List[LineString],
        all_blocks: Optional[List[Polygon]] = None
    ) -> str:
        """
        Classify a single block into a functional zone
        
        Args:
            block: Block polygon to classify
            main_roads: List of main road linestrings
            all_blocks: All blocks for context-aware classification
            
        Returns:
            Zone type: 'FACTORY', 'WAREHOUSE', 'RESIDENTIAL', 'SERVICE', 'GREEN', or 'WATER'
        """
        area = block.area
        centroid = block.centroid
        
        # Calculate position metrics
        distance_to_center = centroid.distance(self.site_centroid)
        relative_position = min(1.0, distance_to_center / (self.site_diagonal / 2))
        distance_to_boundary = block.distance(self.site_boundary.exterior)
        
        # Check if near corner
        near_corner = any(
            centroid.distance(c) < self.site_diagonal * self.CORNER_RADIUS 
            for c in self.corners
        )
        
        # Calculate distance to main roads
        if main_roads:
            main_roads_union = unary_union(main_roads)
            distance_to_main = block.distance(main_roads_union)
        else:
            distance_to_main = float('inf')
        
        # ===== CLASSIFICATION RULES (ADAPTIVE TO ORIENTATION) =====
        
        # Detect entrance side to position factories correctly
        entrance_side = self._detect_entrance_side(main_roads)
        
        # Reference pattern adapts to site orientation and entrance:
        # - Factories near entrance (good access for trucks)
        # - Warehouses in middle
        # - Residential far from entrance (quieter, away from heavy traffic)
        
        # Calculate position along primary axis FROM ENTRANCE
        bounds = self.site_boundary.bounds
        
        if self.is_horizontal:
            # Horizontal: use X-axis
            if entrance_side == 'left':
                # Left entrance: 0=left (entrance), 1=right (far)
                rel_primary = (centroid.x - bounds[0]) / (bounds[2] - bounds[0]) \
                    if (bounds[2] - bounds[0]) > 0 else 0.5
            else:
                # Right entrance: flip (0=right entrance, 1=left far)
                rel_primary = 1.0 - ((centroid.x - bounds[0]) / (bounds[2] - bounds[0])) \
                    if (bounds[2] - bounds[0]) > 0 else 0.5
            axis_label = f"X (entrance={entrance_side})"
        else:
            # Vertical: use Y-axis
            if entrance_side == 'bottom':
                # Bottom entrance: 0=bottom, 1=top
                rel_primary = (centroid.y - bounds[1]) / (bounds[3] - bounds[1]) \
                    if (bounds[3] - bounds[1]) > 0 else 0.5
            else:
                # Top entrance: flip
                rel_primary = 1.0 - ((centroid.y - bounds[1]) / (bounds[3] - bounds[1])) \
                    if (bounds[3] - bounds[1]) > 0 else 0.5
            axis_label = f"Y (entrance={entrance_side})"
        
        # Log first few classifications to verify orientation
        if not hasattr(self, '_log_count'):
            self._log_count = 0
        if self._log_count < 3:
            logger.info(
                f"[ZONE] Block at {rel_primary:.2f} from entrance via {axis_label}, "
                f"area={area:.0f}m²"
            )
            self._log_count += 1
        
        # Rule 1: GREEN BUFFER ZONES
        # - Very small blocks at corners or edges
        if area < self.SMALL_THRESHOLD:
            if distance_to_boundary < self.BOUNDARY_BUFFER or near_corner:
                return 'GREEN'
        
        # Rule 2: WATER FEATURES
        # - Small-medium central blocks
        if not self.water_assigned and area < self.MEDIUM_THRESHOLD:
            if relative_position < 0.3:  # Central
                self.water_assigned = True
                return 'WATER'
        
        # Rule 3: ENTRANCE ZONE - LARGE FACTORIES
        # - First 40% along primary axis (entrance side)
        # - Large blocks with good road access
        if rel_primary < 0.4:
            if area >= self.LARGE_THRESHOLD:
                return 'FACTORY'
            elif area >= self.MEDIUM_THRESHOLD:
                return 'WAREHOUSE'
        
        # Rule 4: MIDDLE ZONE - WAREHOUSES
        # - 40-70% along primary axis
        if 0.4 <= rel_primary < 0.7:
            if area >= self.VERY_LARGE_THRESHOLD:
                return 'FACTORY'  # Exception for very large
            elif area >= self.MEDIUM_THRESHOLD:
                return 'WAREHOUSE'
            else:
                return 'SERVICE'
        
        # Rule 5: FAR ZONE - RESIDENTIAL
        # - 70%+ along primary axis (furthest from entrance)
        # - Creates dense residential pattern like reference
        if rel_primary >= 0.7:
            if area >= self.LARGE_THRESHOLD:
                # Still factory if very large
                return 'FACTORY'
            elif area >= self.MEDIUM_THRESHOLD:
                # Medium = warehouse or residential based on road access
                if distance_to_main < self.MAIN_ROAD_CLOSE:
                    return 'WAREHOUSE'
                else:
                    return 'RESIDENTIAL'
            else:
                return 'RESIDENTIAL'
        
        # Rule 6: EDGE POSITIONS - SERVICE
        # - Outer perimeter regardless of primary position
        if relative_position > 0.8:
            return 'SERVICE'
        
        # Rule 7: FALLBACK
        # - Default warehouse for unclassified
        return 'WAREHOUSE'
    
    def classify_blocks_batch(
        self,
        blocks: List[Polygon],
        main_roads: List[LineString]
    ) -> Dict[str, List[Polygon]]:
        """
        Classify multiple blocks and return grouped results
        
        Args:
            blocks: List of block polygons
            main_roads: List of main road linestrings
            
        Returns:
            Dictionary mapping zone types to lists of blocks
        """
        results = {
            'FACTORY': [],
            'WAREHOUSE': [],
            'RESIDENTIAL': [],
            'SERVICE': [],
            'GREEN': [],
            'WATER': []
        }
        
        for block in blocks:
            zone = self.classify_block(block, main_roads, blocks)
            results[zone].append(block)
        
        # Log distribution
        logger.info("Zone Classification Results:")
        for zone, zone_blocks in results.items():
            if zone_blocks:
                total_area = sum(b.area for b in zone_blocks)
                logger.info(f"  {zone}: {len(zone_blocks)} blocks, {total_area/10000:.2f} ha")
        
        return results
    
    def get_zone_color(self, zone: str) -> str:
        """Get color hex code for zone type"""
        colors = {
            'FACTORY': '#FF6B6B',      # Red - Large industrial
            'WAREHOUSE': '#FFB84D',    # Orange - Medium industrial
            'RESIDENTIAL': '#4ECDC4',  # Teal - Residential
            'SERVICE': '#95E1D3',      # Light green - Service/utilities
            'GREEN': '#66D9A6',        # Green - Parks/buffers
            'WATER': '#5DADE2',        # Blue - Water features
        }
        return colors.get(zone, '#9E9E9E')  # Gray default
    
    def reset(self):
        """Reset classifier state (useful for multiple runs)"""
        self.water_assigned = False
