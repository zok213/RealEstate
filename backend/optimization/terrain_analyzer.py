"""
Terrain Analysis & Grading Optimization

Process elevation data and optimize site grading for:
- Cut/fill volume calculation
- Slope analysis
- Buildable area identification
- Grading cost optimization
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from shapely.geometry import Polygon, Point
from scipy.interpolate import griddata
import logging

logger = logging.getLogger(__name__)


class TerrainAnalyzer:
    """
    Analyze terrain elevation and calculate slopes
    """
    
    def __init__(self, grid_resolution: float = 5.0):
        """
        Args:
            grid_resolution: Grid cell size in meters
        """
        self.grid_resolution = grid_resolution
    
    def process_elevation_data(
        self,
        elevation_points: List[Tuple[float, float, float]],
        site_boundary: Polygon
    ) -> np.ndarray:
        """
        Create elevation grid from point cloud
        
        Args:
            elevation_points: [(x, y, z), ...] - elevation data
            site_boundary: Site polygon
            
        Returns:
            2D elevation grid (numpy array)
        """
        logger.info(f"[TERRAIN] Processing {len(elevation_points)} elevation points")
        
        # Extract bounds
        minx, miny, maxx, maxy = site_boundary.bounds
        
        # Create grid
        x_coords = np.arange(minx, maxx, self.grid_resolution)
        y_coords = np.arange(miny, maxy, self.grid_resolution)
        grid_x, grid_y = np.meshgrid(x_coords, y_coords)
        
        # Interpolate elevations
        points = np.array([(p[0], p[1]) for p in elevation_points])
        values = np.array([p[2] for p in elevation_points])
        
        try:
            grid_z = griddata(
                points, values, (grid_x, grid_y),
                method='cubic',
                fill_value=np.nanmean(values)
            )
        except Exception as e:
            logger.warning(f"[TERRAIN] Cubic interpolation failed, using linear: {e}")
            grid_z = griddata(
                points, values, (grid_x, grid_y),
                method='linear',
                fill_value=np.nanmean(values)
            )
        
        logger.info(f"[TERRAIN] ✓ Created {grid_z.shape} elevation grid")
        return grid_z
    
    def calculate_slope_map(
        self,
        elevation_grid: np.ndarray
    ) -> np.ndarray:
        """
        Calculate slope percentage for each grid cell
        
        Args:
            elevation_grid: 2D elevation array
            
        Returns:
            Slope map (% grade)
        """
        # Calculate gradients
        dy, dx = np.gradient(elevation_grid, self.grid_resolution)
        
        # Calculate slope (rise/run as percentage)
        slope = np.sqrt(dx**2 + dy**2) * 100
        
        # Replace NaN with 0
        slope = np.nan_to_num(slope, nan=0.0)
        
        logger.info(f"[TERRAIN] ✓ Calculated slope map, max slope: {np.max(slope):.1f}%")
        return slope
    
    def identify_buildable_areas(
        self,
        slope_map: np.ndarray,
        max_slope: float = 15.0
    ) -> np.ndarray:
        """
        Identify areas suitable for building
        
        Args:
            slope_map: Slope percentage grid
            max_slope: Maximum allowable slope (%)
            
        Returns:
            Boolean mask of buildable areas
        """
        buildable = slope_map <= max_slope
        
        buildable_percentage = (np.sum(buildable) / buildable.size) * 100
        logger.info(f"[TERRAIN] ✓ Buildable area: {buildable_percentage:.1f}%")
        
        return buildable
    
    def calculate_cut_fill_volumes(
        self,
        existing_elevation: np.ndarray,
        proposed_elevation: np.ndarray
    ) -> Dict[str, float]:
        """
        Calculate earthwork volumes
        
        Args:
            existing_elevation: Current elevation grid
            proposed_elevation: Target elevation grid
            
        Returns:
            Dict with cut, fill, net volumes in m³
        """
        # Calculate difference
        diff = proposed_elevation - existing_elevation
        
        # Cell area
        cell_area = self.grid_resolution ** 2
        
        # Cut volume (where diff < 0)
        cut_volume = np.sum(np.abs(diff[diff < 0])) * cell_area
        
        # Fill volume (where diff > 0)
        fill_volume = np.sum(diff[diff > 0]) * cell_area
        
        # Net volume
        net_volume = fill_volume - cut_volume
        
        logger.info(
            f"[TERRAIN] Cut: {cut_volume:.0f}m³, Fill: {fill_volume:.0f}m³, "
            f"Net: {net_volume:+.0f}m³"
        )
        
        return {
            'cut': cut_volume,
            'fill': fill_volume,
            'net': net_volume,
            'balance': abs(net_volume)
        }


class GradingOptimizer:
    """
    Optimize site grading to minimize cost
    """
    
    def __init__(
        self,
        cut_cost_per_m3: float = 50_000,    # VND
        fill_cost_per_m3: float = 80_000,   # VND (more expensive)
        haul_cost_per_m3_km: float = 20_000 # VND
    ):
        """
        Args:
            cut_cost_per_m3: Cost to cut/excavate
            fill_cost_per_m3: Cost to fill/import material
            haul_cost_per_m3_km: Cost to transport material
        """
        self.cut_cost = cut_cost_per_m3
        self.fill_cost = fill_cost_per_m3
        self.haul_cost = haul_cost_per_m3_km
    
    def optimize_grading_plan(
        self,
        existing_elevation: np.ndarray,
        site_area: float,
        target_slope: float = 0.02  # 2% minimum for drainage
    ) -> Dict[str, Any]:
        """
        Create optimal grading plan
        
        Objectives:
        1. Balance cut/fill (minimize haul)
        2. Ensure drainage (min 2% slope)
        3. Minimize cost
        
        Args:
            existing_elevation: Current elevation grid
            site_area: Total site area in m²
            target_slope: Minimum slope for drainage
            
        Returns:
            Grading plan with costs
        """
        logger.info("[GRADING] Optimizing grading plan")
        
        # Calculate target elevation (balanced cut/fill)
        target_elevation = self._calculate_balanced_elevation(existing_elevation)
        
        # Apply drainage slope
        target_elevation = self._apply_drainage_slope(
            target_elevation,
            target_slope
        )
        
        # Calculate volumes
        analyzer = TerrainAnalyzer()
        volumes = analyzer.calculate_cut_fill_volumes(
            existing_elevation,
            target_elevation
        )
        
        # Calculate cost
        cut_cost = volumes['cut'] * self.cut_cost
        fill_cost = volumes['fill'] * self.fill_cost
        haul_cost = volumes['balance'] * self.haul_cost * 0.5  # avg 0.5km haul
        
        total_cost = cut_cost + fill_cost + haul_cost
        
        logger.info(f"[GRADING] ✓ Total grading cost: {total_cost/1e6:.1f}M VND")
        
        return {
            'existing_elevation': existing_elevation,
            'proposed_elevation': target_elevation,
            'volumes': volumes,
            'cost_breakdown': {
                'cut': cut_cost,
                'fill': fill_cost,
                'haul': haul_cost,
                'total': total_cost
            },
            'cost_per_m2': total_cost / site_area if site_area > 0 else 0
        }
    
    def _calculate_balanced_elevation(
        self,
        existing: np.ndarray
    ) -> np.ndarray:
        """
        Calculate target elevation that balances cut/fill
        
        Strategy: Use mean elevation with smoothing
        """
        # Remove NaN values
        valid = existing[~np.isnan(existing)]
        
        if len(valid) == 0:
            return existing.copy()
        
        # Target is median (more robust than mean)
        target_level = np.median(valid)
        
        # Create target elevation
        target = np.full_like(existing, target_level)
        
        # Smooth to avoid sharp transitions
        from scipy.ndimage import gaussian_filter
        try:
            target = gaussian_filter(target, sigma=2.0)
        except Exception:
            pass
        
        return target
    
    def _apply_drainage_slope(
        self,
        elevation: np.ndarray,
        min_slope: float
    ) -> np.ndarray:
        """
        Apply minimum slope for drainage
        
        Args:
            elevation: Elevation grid
            min_slope: Minimum slope (rise/run, e.g., 0.02 for 2%)
            
        Returns:
            Adjusted elevation with drainage slope
        """
        # For simplicity, apply uniform slope from high to low corner
        # In production, would use more sophisticated drainage design
        
        rows, cols = elevation.shape
        
        # Create slope gradient (high at top-left, low at bottom-right)
        for i in range(rows):
            for j in range(cols):
                # Apply diagonal slope
                distance = np.sqrt(i**2 + j**2)
                elevation[i, j] -= distance * min_slope * 5.0  # 5m grid resolution
        
        return elevation


def create_synthetic_terrain(
    site_boundary: Polygon,
    base_elevation: float = 100.0,
    slope: float = 0.01,
    roughness: float = 0.5
) -> List[Tuple[float, float, float]]:
    """
    Create synthetic terrain data for testing
    
    Args:
        site_boundary: Site polygon
        base_elevation: Base elevation in meters
        slope: Average slope (rise/run)
        roughness: Terrain roughness (0-1)
        
    Returns:
        List of (x, y, z) elevation points
    """
    minx, miny, maxx, maxy = site_boundary.bounds
    
    # Create grid of points
    x_points = np.linspace(minx, maxx, 20)
    y_points = np.linspace(miny, maxy, 20)
    
    elevation_points = []
    
    for x in x_points:
        for y in y_points:
            # Base elevation with slope
            z = base_elevation + (x - minx) * slope
            
            # Add roughness
            if roughness > 0:
                z += np.random.uniform(-roughness, roughness)
            
            elevation_points.append((x, y, z))
    
    return elevation_points
