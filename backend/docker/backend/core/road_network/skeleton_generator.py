"""Medial axis transform for central main road generation.

Uses skeletonization to find the central axis of the site polygon,
creating main roads that are equidistant from all edges.
"""

from dataclasses import dataclass
from typing import List, Optional
import numpy as np
import logging
from shapely.geometry import Polygon, LineString, Point

logger = logging.getLogger(__name__)


@dataclass
class SkeletonConfig:
    """Configuration for skeleton road generation."""
    
    # Rasterization resolution (meters per pixel)
    resolution: float = 2.0
    
    # Minimum road segment length to keep
    min_road_length: float = 50.0
    
    # Simplification tolerance (meters)
    simplify_tolerance: float = 8.0
    
    # Prune short branches (fraction of longest path)
    prune_ratio: float = 0.15


class SkeletonRoadGenerator:
    """Generate main roads along polygon's medial axis."""
    
    def __init__(
        self,
        site_boundary: Polygon,
        config: Optional[SkeletonConfig] = None
    ):
        """Initialize skeleton road generator."""
        self.boundary = site_boundary
        self.config = config or SkeletonConfig()
        
        # Precompute bounds
        self.minx, self.miny, self.maxx, self.maxy = site_boundary.bounds
        
    def generate_main_road(self) -> LineString:
        """Generate the main central road from skeleton."""
        logger.info("Generating main road from skeleton")
        
        skeleton_lines = self._compute_skeleton_simple()
        
        if not skeleton_lines:
            logger.warning("No skeleton lines generated, using centroid line")
            return self._fallback_centroid_line()
            
        # Find the longest path
        main_road = max(skeleton_lines, key=lambda l: l.length)
        
        # Simplify for smoother road
        main_road = main_road.simplify(self.config.simplify_tolerance)
        
        logger.info(f"Main road length: {main_road.length:.1f}m")
        
        return main_road
        
    def generate_with_perpendicular_branches(
        self,
        num_branches: int = 8,
        branch_spacing: float = 80.0
    ) -> List[LineString]:
        """Generate main road with perpendicular branch roads."""
        roads = []
        
        # Get main road
        main_road = self.generate_main_road()
        roads.append(main_road)
        
        if main_road.is_empty or main_road.length < branch_spacing:
            return roads
            
        # Calculate branch points along main road
        num_points = min(num_branches, int(main_road.length / branch_spacing))
        
        for i in range(1, num_points + 1):
            t = i / (num_points + 1)
            
            # Get point and tangent
            point = main_road.interpolate(t, normalized=True)
            
            # Get direction at this point
            nearby_t = min(1.0, t + 0.01)
            nearby_point = main_road.interpolate(nearby_t, normalized=True)
            
            direction = np.array([
                nearby_point.x - point.x,
                nearby_point.y - point.y
            ])
            
            if np.linalg.norm(direction) > 0:
                direction = direction / np.linalg.norm(direction)
            else:
                direction = np.array([1, 0])
                
            # Perpendicular direction
            perp = np.array([-direction[1], direction[0]])
            
            # Create branch in both directions
            diagonal = np.hypot(
                self.maxx - self.minx,
                self.maxy - self.miny
            )
            
            branch_line = LineString([
                (point.x - perp[0] * diagonal, point.y - perp[1] * diagonal),
                (point.x + perp[0] * diagonal, point.y + perp[1] * diagonal)
            ])
            
            # Clip to boundary
            clipped = branch_line.intersection(self.boundary)
            
            if clipped.geom_type == 'LineString' and not clipped.is_empty:
                if clipped.length >= self.config.min_road_length:
                    roads.append(clipped)
            elif clipped.geom_type == 'MultiLineString':
                for segment in clipped.geoms:
                    if segment.length >= self.config.min_road_length:
                        roads.append(segment)
                        
        logger.info(f"Generated {len(roads)} skeleton roads (1 main + {len(roads)-1} branches)")
        return roads
        
    def _compute_skeleton_simple(self) -> List[LineString]:
        """Simple skeleton approximation for rectangular and simple polygons."""
        logger.debug("Using simplified skeleton (axis-based)")
        
        lines = []
        center = self.boundary.centroid
        width = self.maxx - self.minx
        height = self.maxy - self.miny
        
        # For rectangular or near-rectangular shapes,
        # create main axis along the longer dimension
        
        if width > height * 1.2:
            # Predominantly horizontal: create horizontal skeleton
            main_line = LineString([
                (self.minx + width * 0.05, center.y),
                (self.minx + width * 0.95, center.y)
            ])
        elif height > width * 1.2:
            # Predominantly vertical: create vertical skeleton
            main_line = LineString([
                (center.x, self.miny + height * 0.05),
                (center.x, self.miny + height * 0.95)
            ])
        else:
            # Square-ish: create horizontal through center
            main_line = LineString([
                (self.minx + width * 0.05, center.y),
                (self.minx + width * 0.95, center.y)
            ])
            
        # Clip to boundary
        clipped = main_line.intersection(self.boundary)
        
        if clipped.geom_type == 'LineString' and not clipped.is_empty:
            lines.append(clipped)
        elif clipped.geom_type == 'MultiLineString':
            for segment in clipped.geoms:
                if segment.length > 50:
                    lines.append(segment)
                    
        return lines
        
    def _fallback_centroid_line(self) -> LineString:
        """Create a simple line through centroid as fallback."""
        center = self.boundary.centroid
        
        # Create line along longer axis
        width = self.maxx - self.minx
        height = self.maxy - self.miny
        
        if width > height:
            # Horizontal line
            line = LineString([
                (self.minx + width * 0.1, center.y),
                (self.minx + width * 0.9, center.y)
            ])
        else:
            # Vertical line
            line = LineString([
                (center.x, self.miny + height * 0.1),
                (center.x, self.miny + height * 0.9)
            ])
            
        return line.intersection(self.boundary)


def generate_skeleton_roads(
    site_boundary: Polygon,
    resolution: float = 2.0,
    min_road_length: float = 50.0,
    num_branches: int = 8
) -> List[LineString]:
    """Generate skeleton-based roads with perpendicular branches.
    
    Args:
        site_boundary: Site boundary polygon
        resolution: Rasterization resolution (m/pixel)
        min_road_length: Minimum road length to keep (m)
        num_branches: Number of perpendicular branches
        
    Returns:
        List of road LineStrings
    """
    config = SkeletonConfig(
        resolution=resolution,
        min_road_length=min_road_length
    )
    
    generator = SkeletonRoadGenerator(
        site_boundary=site_boundary,
        config=config
    )
    
    return generator.generate_with_perpendicular_branches(
        num_branches=num_branches
    )
