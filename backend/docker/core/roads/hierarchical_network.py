"""
Hierarchical Road Network Generator

Creates multi-level road networks:
1. Main spine roads - Primary arterials (20-24m wide)
2. Secondary branches - Collector roads (12-16m wide)
3. Tertiary loops - Access roads (8-10m wide)
4. Roundabouts at major intersections

Features:
- Curved roads (not just orthogonal)
- Hierarchical structure
- Roundabout intersections
- Organic layout following terrain
"""

import logging
import math
from typing import List, Tuple, Dict, Optional
from shapely.geometry import (
    Polygon, LineString, Point, MultiLineString
)
from shapely.ops import unary_union, linemerge
import numpy as np

logger = logging.getLogger(__name__)


class HierarchicalRoadNetwork:
    """
    Generate hierarchical road networks with curved roads and roundabouts
    """
    
    def __init__(
        self,
        site_boundary: Polygon,
        main_width: float = 8.0,
        branch_width: float = 6.0,
        tertiary_width: float = 4.0
    ):
        """
        Initialize road network generator
        
        Args:
            site_boundary: Site polygon
            main_width: Width of main spine roads (m)
            branch_width: Width of secondary branches (m)
            tertiary_width: Width of tertiary/access roads (m)
        """
        self.site = site_boundary
        self.main_width = main_width
        self.branch_width = branch_width
        self.tertiary_width = tertiary_width
        
        self.main_roads = []
        self.branch_roads = []
        self.tertiary_roads = []
        self.roundabouts = []
        
    def generate_spine_road(self) -> LineString:
        """
        Generate main spine road through site
        
        Uses longest diagonal or major axis
        
        Returns:
            Main spine road as LineString
        """
        bounds = self.site.bounds
        minx, miny, maxx, maxy = bounds
        
        # Try horizontal spine first
        width = maxx - minx
        height = maxy - miny
        
        if width > height:
            # Horizontal spine
            y_center = (miny + maxy) / 2
            spine = LineString([
                (minx + width * 0.1, y_center),
                (maxx - width * 0.1, y_center)
            ])
        else:
            # Vertical spine
            x_center = (minx + maxx) / 2
            spine = LineString([
                (x_center, miny + height * 0.1),
                (x_center, maxy - height * 0.1)
            ])
        
        # Clip to site
        clipped = spine.intersection(self.site)
        
        if clipped.is_empty or not isinstance(clipped, LineString):
            # Fallback: diagonal
            spine = LineString([
                (minx + width * 0.1, miny + height * 0.1),
                (maxx - width * 0.1, maxy - height * 0.1)
            ])
            clipped = spine.intersection(self.site)
        
        return clipped if isinstance(clipped, LineString) else spine
    
    def generate_curved_branch(
        self,
        start: Point,
        direction: float,
        length: float,
        curvature: float = 0.3
    ) -> LineString:
        """
        Generate curved branch road
        
        Args:
            start: Starting point
            direction: Direction in radians
            length: Target length
            curvature: Curve factor (0=straight, 1=very curved)
            
        Returns:
            Curved LineString
        """
        # Create curved path using Bezier-like control points
        num_segments = 10
        points = []
        
        for i in range(num_segments + 1):
            t = i / num_segments
            
            # Base linear interpolation
            base_x = start.x + length * math.cos(direction) * t
            base_y = start.y + length * math.sin(direction) * t
            
            # Add curve (sine wave)
            perpendicular = direction + math.pi / 2
            curve_offset = math.sin(t * math.pi) * length * curvature
            
            x = base_x + curve_offset * math.cos(perpendicular)
            y = base_y + curve_offset * math.sin(perpendicular)
            
            points.append((x, y))
        
        line = LineString(points)
        
        # Clip to site
        clipped = line.intersection(self.site)
        
        return clipped if isinstance(clipped, LineString) else line
    
    def generate_branch_roads(
        self,
        spine: LineString,
        num_branches: int = 8,
        curve_factor: float = 0.2
    ) -> List[LineString]:
        """
        Generate perpendicular branch roads from spine
        
        Args:
            spine: Main spine road
            num_branches: Number of branches per side
            curve_factor: How curved the branches are
            
        Returns:
            List of branch road LineStrings
        """
        branches = []
        spine_length = spine.length
        
        # Place branches at regular intervals
        for i in range(1, num_branches + 1):
            # Alternate sides
            distance = (spine_length / (num_branches + 1)) * i
            
            # Get point on spine
            point = spine.interpolate(distance)
            
            # Get tangent direction at point
            before = spine.interpolate(max(0, distance - 1))
            after = spine.interpolate(min(spine_length, distance + 1))
            dx = after.x - before.x
            dy = after.y - before.y
            spine_angle = math.atan2(dy, dx)
            
            # Perpendicular directions (both sides)
            perp_angles = [
                spine_angle + math.pi / 2,
                spine_angle - math.pi / 2
            ]
            
            for angle in perp_angles:
                # Branch length (variable)
                branch_length = 80 + np.random.uniform(-20, 40)
                
                branch = self.generate_curved_branch(
                    Point(point.x, point.y),
                    angle,
                    branch_length,
                    curvature=curve_factor
                )
                
                if not branch.is_empty and branch.length > 20:
                    branches.append(branch)
        
        return branches
    
    def create_roundabout(
        self,
        center: Point,
        radius: float = 15.0,
        segments: int = 16
    ) -> Polygon:
        """
        Create circular roundabout at intersection
        
        Args:
            center: Center point of roundabout
            radius: Outer radius
            segments: Number of circle segments
            
        Returns:
            Roundabout as circular Polygon
        """
        # Create circle points
        points = []
        for i in range(segments):
            angle = 2 * math.pi * i / segments
            x = center.x + radius * math.cos(angle)
            y = center.y + radius * math.sin(angle)
            points.append((x, y))
        
        # Close the polygon
        points.append(points[0])
        
        return Polygon(points)
    
    def find_intersections(self, roads: List[LineString]) -> List[Point]:
        """
        Find intersection points between roads
        
        Args:
            roads: List of road LineStrings
            
        Returns:
            List of intersection Points
        """
        intersections = []
        
        for i, road1 in enumerate(roads):
            for road2 in roads[i+1:]:
                intersection = road1.intersection(road2)
                
                if not intersection.is_empty:
                    if isinstance(intersection, Point):
                        intersections.append(intersection)
        
        return intersections
    
    def generate_complete_network(
        self,
        num_branches: int = 8,
        add_roundabouts: bool = True
    ) -> Dict:
        """
        Generate complete hierarchical road network
        
        Args:
            num_branches: Number of branch roads
            add_roundabouts: Whether to add roundabouts at intersections
            
        Returns:
            Dictionary with roads and roundabouts
        """
        logger.info(f"Generating hierarchical network with {num_branches} branches")
        
        # 1. Generate main spine
        spine = self.generate_spine_road()
        self.main_roads = [spine]
        
        # 2. Generate branch roads
        branches = self.generate_branch_roads(
            spine,
            num_branches=num_branches,
            curve_factor=0.15
        )
        self.branch_roads = branches
        
        # 3. Find major intersections for roundabouts
        if add_roundabouts:
            all_roads = self.main_roads + self.branch_roads
            intersections = self.find_intersections(all_roads)
            
            # Create roundabouts at main intersections
            # (limit to spine-branch intersections)
            for point in intersections[:min(4, len(intersections))]:
                roundabout = self.create_roundabout(point, radius=12.0)
                
                # Check if roundabout fits in site
                if roundabout.within(self.site):
                    self.roundabouts.append(roundabout)
        
        logger.info(
            f"Network: {len(self.main_roads)} main roads, "
            f"{len(self.branch_roads)} branches, "
            f"{len(self.roundabouts)} roundabouts"
        )
        
        return {
            'main_roads': self.main_roads,
            'branch_roads': self.branch_roads,
            'tertiary_roads': self.tertiary_roads,
            'roundabouts': self.roundabouts
        }
    
    def get_road_network_polygon(self) -> Polygon:
        """
        Get combined road network as polygon (for block extraction)
        
        Returns:
            Unioned road buffers as Polygon
        """
        road_polys = []
        
        # Buffer main roads
        for road in self.main_roads:
            road_polys.append(road.buffer(self.main_width / 2, cap_style=2))
        
        # Buffer branch roads
        for road in self.branch_roads:
            road_polys.append(road.buffer(self.branch_width / 2, cap_style=2))
        
        # Add roundabouts
        road_polys.extend(self.roundabouts)
        
        # Union all
        if road_polys:
            network = unary_union(road_polys)
            # Smooth with small buffer
            return network.buffer(5, join_style=1).buffer(-5, join_style=1)
        
        return Polygon()
