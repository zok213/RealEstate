"""
Main Entrance Placement Algorithm for Industrial Parks

Automatically places main entrance perpendicular to frontage highway
according to IEAT Thailand requirements and traffic engineering best practices.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import logging
from shapely.geometry import Point, LineString, Polygon
from shapely.ops import nearest_points

logger = logging.getLogger(__name__)


class EntrancePlacer:
    """
    Intelligent entrance placement for industrial park sites.
    
    Features:
    - Detects frontage highway orientation
    - Places entrance perpendicular to highway
    - Ensures minimum setback from corners (safety)
    - Considers site geometry and constraints
    - Generates entrance road geometry
    """
    
    def __init__(
        self,
        min_corner_setback_m: float = 50.0,
        entrance_width_m: float = 30.0,
        entrance_depth_m: float = 50.0
    ):
        """
        Args:
            min_corner_setback_m: Minimum distance from site corners (safety)
            entrance_width_m: Width of entrance gate/road
            entrance_depth_m: Depth of entrance zone from boundary
        """
        self.min_corner_setback = min_corner_setback_m
        self.entrance_width = entrance_width_m
        self.entrance_depth = entrance_depth_m
    
    def place_entrance(
        self,
        site_boundary: Polygon,
        frontage_highway: Optional[LineString] = None,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Place main entrance perpendicular to frontage highway.
        
        Args:
            site_boundary: Site boundary polygon
            frontage_highway: Highway line geometry (optional, will auto-detect)
            constraints: Additional constraints (e.g., no-entrance zones)
        
        Returns:
            {
                "entrance_point": (x, y),
                "entrance_angle": float (degrees from north),
                "entrance_polygon": Polygon,
                "entrance_road": LineString,
                "frontage_edge": LineString,
                "highway_orientation": float
            }
        """
        logger.info("[ENTRANCE PLACEMENT] Starting entrance placement analysis")
        
        # Step 1: Identify frontage edge
        frontage_edge = self._identify_frontage_edge(site_boundary, frontage_highway)
        logger.info(f"[ENTRANCE PLACEMENT] Frontage edge length: {frontage_edge.length:.1f}m")
        
        # Step 2: Calculate highway orientation
        highway_orientation = self._calculate_orientation(frontage_edge)
        logger.info(f"[ENTRANCE PLACEMENT] Highway orientation: {highway_orientation:.1f}°")
        
        # Step 3: Calculate perpendicular angle
        entrance_angle = self._calculate_perpendicular_angle(highway_orientation)
        logger.info(f"[ENTRANCE PLACEMENT] Entrance angle: {entrance_angle:.1f}°")
        
        # Step 4: Find optimal entrance location
        entrance_point = self._find_optimal_location(
            frontage_edge,
            site_boundary,
            constraints
        )
        logger.info(f"[ENTRANCE PLACEMENT] Entrance point: ({entrance_point.x:.1f}, {entrance_point.y:.1f})")
        
        # Step 5: Generate entrance geometry
        entrance_polygon = self._generate_entrance_zone(
            entrance_point,
            entrance_angle,
            self.entrance_width,
            self.entrance_depth
        )
        
        # Step 6: Create entrance road
        entrance_road = self._generate_entrance_road(
            entrance_point,
            entrance_angle,
            self.entrance_depth
        )
        
        return {
            "entrance_point": (entrance_point.x, entrance_point.y),
            "entrance_angle": entrance_angle,
            "entrance_polygon": entrance_polygon,
            "entrance_road": entrance_road,
            "frontage_edge": frontage_edge,
            "highway_orientation": highway_orientation,
            "entrance_width_m": self.entrance_width,
            "entrance_depth_m": self.entrance_depth
        }
    
    def _identify_frontage_edge(
        self,
        boundary: Polygon,
        highway: Optional[LineString] = None
    ) -> LineString:
        """
        Identify which edge of the site is the frontage (faces highway).
        
        If highway is provided, finds closest edge.
        Otherwise, assumes longest edge is frontage.
        """
        # Get all boundary edges
        coords = list(boundary.exterior.coords)
        edges = []
        
        for i in range(len(coords) - 1):
            edge = LineString([coords[i], coords[i+1]])
            edges.append(edge)
        
        if highway:
            # Find edge closest to highway
            min_dist = float('inf')
            frontage_edge = edges[0]
            
            for edge in edges:
                dist = edge.distance(highway)
                if dist < min_dist:
                    min_dist = dist
                    frontage_edge = edge
            
            logger.info(f"[ENTRANCE PLACEMENT] Found frontage edge {min_dist:.1f}m from highway")
            return frontage_edge
        else:
            # Use longest edge as frontage
            frontage_edge = max(edges, key=lambda e: e.length)
            logger.info(f"[ENTRANCE PLACEMENT] Using longest edge as frontage")
            return frontage_edge
    
    def _calculate_orientation(self, edge: LineString) -> float:
        """
        Calculate orientation of edge in degrees (0° = North, 90° = East).
        """
        coords = list(edge.coords)
        p1, p2 = coords[0], coords[-1]
        
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        
        # Calculate angle in degrees from north (clockwise)
        angle = np.degrees(np.arctan2(dx, dy))
        
        # Normalize to 0-360
        if angle < 0:
            angle += 360
        
        return angle
    
    def _calculate_perpendicular_angle(self, highway_orientation: float) -> float:
        """
        Calculate perpendicular angle to highway.
        
        Entrance should be 90° from highway orientation.
        """
        perpendicular = (highway_orientation + 90) % 360
        return perpendicular
    
    def _find_optimal_location(
        self,
        frontage_edge: LineString,
        boundary: Polygon,
        constraints: Optional[Dict] = None
    ) -> Point:
        """
        Find optimal location for entrance along frontage edge.
        
        Criteria:
        1. At least min_corner_setback from corners
        2. Avoid constraint zones
        3. Prefer center of frontage for symmetry
        4. Ensure good sightlines
        """
        coords = list(frontage_edge.coords)
        start_point = Point(coords[0])
        end_point = Point(coords[-1])
        
        # Calculate valid range (with corner setback)
        edge_length = frontage_edge.length
        if edge_length < 2 * self.min_corner_setback:
            logger.warning(f"[ENTRANCE PLACEMENT] Frontage too short ({edge_length:.1f}m) for ideal setback")
            # Use center anyway
            return frontage_edge.interpolate(0.5, normalized=True)
        
        # Prefer center, but check constraints
        center_point = frontage_edge.interpolate(0.5, normalized=True)
        
        if constraints and constraints.get('no_entrance_zones'):
            # Check if center conflicts with constraints
            for no_go_zone in constraints['no_entrance_zones']:
                if center_point.distance(no_go_zone) < self.entrance_width / 2:
                    logger.info("[ENTRANCE PLACEMENT] Center conflicts with constraint, finding alternative")
                    # Try 1/3 or 2/3 position
                    alt1 = frontage_edge.interpolate(0.33, normalized=True)
                    alt2 = frontage_edge.interpolate(0.67, normalized=True)
                    
                    if alt1.distance(no_go_zone) > self.entrance_width / 2:
                        return alt1
                    elif alt2.distance(no_go_zone) > self.entrance_width / 2:
                        return alt2
        
        return center_point
    
    def _generate_entrance_zone(
        self,
        entrance_point: Point,
        entrance_angle: float,
        width: float,
        depth: float
    ) -> Polygon:
        """
        Generate entrance zone polygon.
        
        Creates rectangular zone perpendicular to highway.
        """
        # Convert angle to radians
        angle_rad = np.radians(entrance_angle)
        
        # Calculate perpendicular direction (into site)
        dx = np.sin(angle_rad)
        dy = np.cos(angle_rad)
        
        # Calculate perpendicular direction (along frontage)
        perp_dx = -dy
        perp_dy = dx
        
        # Create rectangle corners
        half_width = width / 2
        
        corners = [
            # Front left
            (entrance_point.x - perp_dx * half_width,
             entrance_point.y - perp_dy * half_width),
            # Front right
            (entrance_point.x + perp_dx * half_width,
             entrance_point.y + perp_dy * half_width),
            # Back right
            (entrance_point.x + perp_dx * half_width + dx * depth,
             entrance_point.y + perp_dy * half_width + dy * depth),
            # Back left
            (entrance_point.x - perp_dx * half_width + dx * depth,
             entrance_point.y - perp_dy * half_width + dy * depth),
        ]
        
        return Polygon(corners)
    
    def _generate_entrance_road(
        self,
        entrance_point: Point,
        entrance_angle: float,
        depth: float
    ) -> LineString:
        """
        Generate entrance road centerline.
        """
        angle_rad = np.radians(entrance_angle)
        
        dx = np.sin(angle_rad)
        dy = np.cos(angle_rad)
        
        end_point = (
            entrance_point.x + dx * depth,
            entrance_point.y + dy * depth
        )
        
        return LineString([
            (entrance_point.x, entrance_point.y),
            end_point
        ])
    
    def place_multiple_entrances(
        self,
        site_boundary: Polygon,
        num_entrances: int = 2,
        **kwargs
    ) -> List[Dict]:
        """
        Place multiple entrances for large sites.
        
        IEAT: Sites >1000 rai may need multiple entrances.
        """
        logger.info(f"[ENTRANCE PLACEMENT] Placing {num_entrances} entrances")
        
        if num_entrances == 1:
            return [self.place_entrance(site_boundary, **kwargs)]
        
        # For multiple entrances, divide frontage edge
        frontage_edge = self._identify_frontage_edge(
            site_boundary,
            kwargs.get('frontage_highway')
        )
        
        entrances = []
        for i in range(num_entrances):
            # Place at 1/(n+1), 2/(n+1), etc. positions
            position = (i + 1) / (num_entrances + 1)
            entrance_point = frontage_edge.interpolate(position, normalized=True)
            
            entrance_angle = self._calculate_perpendicular_angle(
                self._calculate_orientation(frontage_edge)
            )
            
            entrance_polygon = self._generate_entrance_zone(
                entrance_point,
                entrance_angle,
                self.entrance_width,
                self.entrance_depth
            )
            
            entrance_road = self._generate_entrance_road(
                entrance_point,
                entrance_angle,
                self.entrance_depth
            )
            
            entrances.append({
                "entrance_point": (entrance_point.x, entrance_point.y),
                "entrance_angle": entrance_angle,
                "entrance_polygon": entrance_polygon,
                "entrance_road": entrance_road,
                "entrance_number": i + 1
            })
        
        logger.info(f"[ENTRANCE PLACEMENT] Placed {len(entrances)} entrances")
        return entrances


# Example usage and testing
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from shapely.plotting import plot_polygon, plot_line
    
    # Test site: rectangular 1000m x 500m
    test_boundary = Polygon([
        (0, 0),
        (1000, 0),
        (1000, 500),
        (0, 500)
    ])
    
    # Highway along bottom edge
    test_highway = LineString([(-100, -20), (1100, -20)])
    
    # Place entrance
    placer = EntrancePlacer(
        min_corner_setback_m=50,
        entrance_width_m=30,
        entrance_depth_m=50
    )
    
    result = placer.place_entrance(
        test_boundary,
        frontage_highway=test_highway
    )
    
    # Visualize
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot site boundary
    plot_polygon(test_boundary, ax=ax, add_points=False, color='lightgray', alpha=0.3)
    
    # Plot highway
    plot_line(test_highway, ax=ax, color='black', linewidth=3, label='Highway')
    
    # Plot frontage edge
    plot_line(result['frontage_edge'], ax=ax, color='blue', linewidth=2, label='Frontage Edge')
    
    # Plot entrance zone
    plot_polygon(result['entrance_polygon'], ax=ax, add_points=False, color='green', alpha=0.5, label='Entrance Zone')
    
    # Plot entrance road
    plot_line(result['entrance_road'], ax=ax, color='red', linewidth=2, linestyle='--', label='Entrance Road')
    
    # Plot entrance point
    ep = result['entrance_point']
    ax.plot(ep[0], ep[1], 'ro', markersize=10, label='Entrance Point')
    
    ax.set_aspect('equal')
    ax.legend()
    ax.set_title(f"Entrance Placement\nHighway: {result['highway_orientation']:.1f}°, Entrance: {result['entrance_angle']:.1f}°")
    ax.grid(True, alpha=0.3)
    
    print(f"✓ Entrance placed at ({ep[0]:.1f}, {ep[1]:.1f})")
    print(f"✓ Highway orientation: {result['highway_orientation']:.1f}°")
    print(f"✓ Entrance angle: {result['entrance_angle']:.1f}° (perpendicular)")
    print(f"✓ Entrance width: {result['entrance_width_m']}m")
    print(f"✓ Entrance depth: {result['entrance_depth_m']}m")
    
    plt.tight_layout()
    plt.savefig('entrance_placement_test.png', dpi=150)
    print("\n✓ Visualization saved to entrance_placement_test.png")
