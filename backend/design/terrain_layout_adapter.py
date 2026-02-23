"""
Terrain-Aware Layout Adapter
Adjusts layout generation based on terrain strategy
"""

import logging
from typing import Dict, List, Any
from shapely.geometry import Polygon, Point, LineString
import numpy as np

logger = logging.getLogger(__name__)


class TerrainLayoutAdapter:
    """
    Adapts layout generation strategies based on terrain conditions.
    Supports: minimal_cut, balanced_cut_fill, major_grading
    """
    
    def __init__(self, terrain_strategy: str = "balanced_cut_fill"):
        """
        Args:
            terrain_strategy: One of:
                - minimal_cut: Follow natural contours, minimal earthwork
                - balanced_cut_fill: Moderate grading, balance cut/fill
                - major_grading: Flatten site, maximize buildable area
        """
        self.strategy = terrain_strategy
        
    def adjust_road_layout(
        self,
        roads: List[Dict],
        elevation_data: Dict = None
    ) -> List[Dict]:
        """
        Adjust road routing based on terrain strategy.
        
        Args:
            roads: List of road features
            elevation_data: Optional elevation grid data
            
        Returns:
            Adjusted roads
        """
        if self.strategy == "minimal_cut":
            logger.info("[TERRAIN] Adjusting roads for minimal cut/fill")
            return self._follow_contours(roads, elevation_data)
        elif self.strategy == "major_grading":
            logger.info("[TERRAIN] Using straight roads (flat terrain)")
            return roads  # No adjustment needed
        else:  # balanced_cut_fill
            logger.info("[TERRAIN] Moderate road adjustment")
            return self._balance_road_grades(roads, elevation_data)
    
    def adjust_plot_placement(
        self,
        plots: List[Dict],
        elevation_data: Dict = None
    ) -> List[Dict]:
        """
        Adjust building plot placement based on terrain.
        
        Args:
            plots: List of plot polygons
            elevation_data: Optional elevation grid
            
        Returns:
            Adjusted plots with platform elevations
        """
        if self.strategy == "minimal_cut":
            logger.info("[TERRAIN] Creating terraced plot layout")
            return self._create_terraced_plots(plots, elevation_data)
        elif self.strategy == "major_grading":
            logger.info("[TERRAIN] Flat platform for all plots")
            return self._flatten_plots(plots, elevation_data)
        else:  # balanced
            logger.info("[TERRAIN] Balanced plot grading")
            return self._balanced_plot_grading(plots, elevation_data)
    
    def calculate_grading_cost(
        self,
        site_area_m2: float,
        elevation_data: Dict = None
    ) -> Dict[str, float]:
        """
        Estimate grading costs based on strategy.
        
        Args:
            site_area_m2: Site area in square meters
            elevation_data: Optional elevation data
            
        Returns:
            Cost breakdown
        """
        # Cost parameters (VND)
        cut_cost_per_m3 = 50_000
        fill_cost_per_m3 = 80_000
        retaining_wall_per_m = 2_000_000
        
        if self.strategy == "minimal_cut":
            # Minimal earthwork, more retaining walls
            estimated_cut_fill_m3 = site_area_m2 * 0.3  # 30cm avg
            retaining_wall_length_m = site_area_m2 * 0.02  # 2% perimeter
            
            earthwork_cost = estimated_cut_fill_m3 * cut_cost_per_m3
            wall_cost = retaining_wall_length_m * retaining_wall_per_m
            total = earthwork_cost + wall_cost
            
            logger.info(f"[TERRAIN] Minimal cut cost: {total/1e9:.2f}B VND")
            
            return {
                "strategy": "minimal_cut",
                "earthwork_volume_m3": estimated_cut_fill_m3,
                "earthwork_cost": earthwork_cost,
                "retaining_walls_m": retaining_wall_length_m,
                "retaining_wall_cost": wall_cost,
                "total_cost": total,
                "cost_per_m2": total / site_area_m2
            }
            
        elif self.strategy == "major_grading":
            # Maximum earthwork, flatten everything
            estimated_cut_fill_m3 = site_area_m2 * 2.0  # 2m avg depth
            retaining_wall_length_m = 0  # No walls needed
            
            earthwork_cost = estimated_cut_fill_m3 * \
                (cut_cost_per_m3 + fill_cost_per_m3) / 2
            total = earthwork_cost
            
            logger.info(f"[TERRAIN] Major grading cost: {total/1e9:.2f}B VND")
            
            return {
                "strategy": "major_grading",
                "earthwork_volume_m3": estimated_cut_fill_m3,
                "earthwork_cost": earthwork_cost,
                "retaining_walls_m": 0,
                "retaining_wall_cost": 0,
                "total_cost": total,
                "cost_per_m2": total / site_area_m2
            }
            
        else:  # balanced_cut_fill
            # Moderate earthwork
            estimated_cut_fill_m3 = site_area_m2 * 1.0  # 1m avg
            retaining_wall_length_m = site_area_m2 * 0.01  # 1% perimeter
            
            earthwork_cost = estimated_cut_fill_m3 * \
                (cut_cost_per_m3 + fill_cost_per_m3) / 2
            wall_cost = retaining_wall_length_m * retaining_wall_per_m
            total = earthwork_cost + wall_cost
            
            logger.info(f"[TERRAIN] Balanced cost: {total/1e9:.2f}B VND")
            
            return {
                "strategy": "balanced_cut_fill",
                "earthwork_volume_m3": estimated_cut_fill_m3,
                "earthwork_cost": earthwork_cost,
                "retaining_walls_m": retaining_wall_length_m,
                "retaining_wall_cost": wall_cost,
                "total_cost": total,
                "cost_per_m2": total / site_area_m2
            }
    
    def _follow_contours(
        self,
        roads: List[Dict],
        elevation_data: Dict
    ) -> List[Dict]:
        """Make roads follow natural contours."""
        # Simplified: Add slight curves to roads
        adjusted = []
        for road in roads:
            road_copy = road.copy()
            # Mark as contour-following
            if "properties" not in road_copy:
                road_copy["properties"] = {}
            road_copy["properties"]["contour_following"] = True
            road_copy["properties"]["max_grade"] = 8.0  # 8% max slope
            adjusted.append(road_copy)
        return adjusted
    
    def _balance_road_grades(
        self,
        roads: List[Dict],
        elevation_data: Dict
    ) -> List[Dict]:
        """Balance road grades for moderate terrain."""
        adjusted = []
        for road in roads:
            road_copy = road.copy()
            if "properties" not in road_copy:
                road_copy["properties"] = {}
            road_copy["properties"]["max_grade"] = 10.0  # 10% max slope
            adjusted.append(road_copy)
        return adjusted
    
    def _create_terraced_plots(
        self,
        plots: List[Dict],
        elevation_data: Dict
    ) -> List[Dict]:
        """Create terraced building platforms."""
        # Group plots by elevation bands
        adjusted = []
        for i, plot in enumerate(plots):
            plot_copy = plot.copy()
            # Assign to elevation band (3m intervals)
            band = i % 5  # Simplified: 5 elevation bands
            plot_copy["elevation_band"] = band
            plot_copy["platform_elevation"] = 100 + (band * 3)  # Base 100m
            plot_copy["needs_retaining_wall"] = True
            plot_copy["retaining_wall_height"] = 2.5  # meters
            adjusted.append(plot_copy)
        
        logger.info(f"[TERRAIN] Created {len(adjusted)} terraced plots")
        return adjusted
    
    def _flatten_plots(
        self,
        plots: List[Dict],
        elevation_data: Dict
    ) -> List[Dict]:
        """Flatten all plots to single elevation."""
        adjusted = []
        target_elevation = 100.0  # Base elevation
        
        for plot in plots:
            plot_copy = plot.copy()
            plot_copy["platform_elevation"] = target_elevation
            plot_copy["needs_retaining_wall"] = False
            adjusted.append(plot_copy)
        
        logger.info(f"[TERRAIN] Flattened {len(adjusted)} plots")
        return adjusted
    
    def _balanced_plot_grading(
        self,
        plots: List[Dict],
        elevation_data: Dict
    ) -> List[Dict]:
        """Moderate grading for plots."""
        adjusted = []
        for i, plot in enumerate(plots):
            plot_copy = plot.copy()
            # Gentle slope across site
            plot_copy["platform_elevation"] = 100 + (i * 0.5)
            plot_copy["needs_retaining_wall"] = (i % 3 == 0)  # 1/3 need walls
            plot_copy["retaining_wall_height"] = 1.5  # Lower walls
            adjusted.append(plot_copy)
        
        return adjusted
