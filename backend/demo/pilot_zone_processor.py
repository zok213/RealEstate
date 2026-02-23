"""
Pilot Zone Processor - Divide Pilot DWG into zones and extract topography

Handles:
- Boundary extraction from Pilot DWG/DXF
- Zone division (4 quadrants)
- Topography extraction per zone
- Zone parameter calculation
"""

import ezdxf
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Polygon, box, mapping
from shapely.ops import unary_union
from pathlib import Path

from .dwg_topography_extractor import extract_topography

logger = logging.getLogger(__name__)


class PilotZoneProcessor:
    """Process Pilot DWG file and divide into zones"""
    
    def __init__(self):
        self.boundary = None
        self.zones = []
        self.topography_data = None
        
    def extract_pilot_boundary(self, file_path: str) -> Polygon:
        """
        Extract site boundary from Pilot DWG/DXF
        
        Args:
            file_path: Path to DWG/DXF file
            
        Returns:
            Boundary polygon
        """
        logger.info(f"Extracting boundary from: {file_path}")
        
        try:
            doc = ezdxf.readfile(file_path)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise
            
        msp = doc.modelspace()
        
        # Find all polylines
        polylines = []
        for entity in msp:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                try:
                    points = list(entity.get_points())
                    if len(points) > 2:
                        # Convert to 2D
                        points_2d = [(p[0], p[1]) for p in points]
                        polylines.append(points_2d)
                except Exception as e:
                    logger.debug(f"Failed to extract polyline: {e}")
                    continue
        
        if not polylines:
            raise ValueError("No polylines found in DXF file")
        
        logger.info(f"Found {len(polylines)} polylines")
        
        # Find largest polyline by area (this is the boundary)
        def calc_area(points):
            try:
                poly = Polygon(points)
                return poly.area if poly.is_valid else 0
            except:
                return 0
        
        largest_points = max(polylines, key=calc_area)
        boundary = Polygon(largest_points)
        
        # Validate and fix if needed
        if not boundary.is_valid:
            logger.warning("Invalid boundary detected, attempting to fix...")
            boundary = boundary.buffer(0)
        
        area_ha = boundary.area / 10000
        logger.info(f"Extracted boundary: {area_ha:.2f} ha ({boundary.area:,.0f} m²)")
        
        self.boundary = boundary
        return boundary
    
    def extract_topography_data(self, file_path: str) -> Dict:
        """
        Extract topography data from DWG file
        
        Args:
            file_path: Path to DWG/DXF file
            
        Returns:
            Topography data dict
        """
        if self.boundary is None:
            raise ValueError("Must extract boundary first")
        
        logger.info("Extracting topography data...")
        
        # Use topography extractor
        topo_data = extract_topography(
            file_path=file_path,
            boundary=self.boundary,
            grid_resolution=10.0  # 10m for demo speed
        )
        
        self.topography_data = topo_data
        return topo_data
    
    def divide_into_zones(
        self, 
        boundary: Optional[Polygon] = None,
        elevation_data: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Divide site into 4 equal quadrants
        
        Args:
            boundary: Site boundary (uses self.boundary if None)
            elevation_data: Optional topography data
            
        Returns:
            List of 4 zone dicts with id, geometry, area, bounds
        """
        if boundary is None:
            boundary = self.boundary
            
        if boundary is None:
            raise ValueError("No boundary available")
        
        # Get bounding box
        minx, miny, maxx, maxy = boundary.bounds
        
        # Calculate midpoints
        mid_x = (minx + maxx) / 2
        mid_y = (miny + maxy) / 2
        
        # Create 4 quadrants
        quadrants = [
            # Zone 1: Northwest (top-left)
            {
                'id': 1,
                'name': 'Northwest',
                'box': box(minx, mid_y, mid_x, maxy)
            },
            # Zone 2: Northeast (top-right)
            {
                'id': 2,
                'name': 'Northeast',
                'box': box(mid_x, mid_y, maxx, maxy)
            },
            # Zone 3: Southwest (bottom-left)
            {
                'id': 3,
                'name': 'Southwest',
                'box': box(minx, miny, mid_x, mid_y)
            },
            # Zone 4: Southeast (bottom-right)
            {
                'id': 4,
                'name': 'Southeast',
                'box': box(mid_x, miny, maxx, mid_y)
            }
        ]
        
        # Intersect each quadrant with actual boundary
        zones = []
        for quad in quadrants:
            zone_poly = boundary.intersection(quad['box'])
            
            if zone_poly.is_empty:
                continue
            
            # Handle MultiPolygon case
            if zone_poly.geom_type == 'MultiPolygon':
                # Take largest polygon
                zone_poly = max(zone_poly.geoms, key=lambda p: p.area)
            
            if zone_poly.geom_type != 'Polygon':
                logger.warning(f"Zone {quad['id']} is not a polygon, skipping")
                continue
            
            area_ha = zone_poly.area / 10000
            
            zone = {
                'id': quad['id'],
                'name': quad['name'],
                'geometry': zone_poly,
                'area_m2': zone_poly.area,
                'area_ha': area_ha,
                'bounds': zone_poly.bounds,
                'centroid': (zone_poly.centroid.x, zone_poly.centroid.y)
            }
            
            zones.append(zone)
            logger.info(f"Zone {quad['id']} ({quad['name']}): {area_ha:.2f} ha")
        
        self.zones = zones
        return zones
    
    def extract_zone(
        self, 
        zone_id: int,
        elevation_data: Optional[Dict] = None
    ) -> Dict:
        """
        Extract specific zone with terrain data
        
        Args:
            zone_id: Zone ID (1-4)
            elevation_data: Optional topography data
            
        Returns:
            Zone dict with geometry and terrain data
        """
        if not self.zones:
            raise ValueError("Must divide into zones first")
        
        # Find zone
        zone = next((z for z in self.zones if z['id'] == zone_id), None)
        
        if zone is None:
            raise ValueError(f"Zone {zone_id} not found")
        
        logger.info(f"Extracting Zone {zone_id} ({zone['name']}): {zone['area_ha']:.2f} ha")
        
        # If we have topography data, extract zone-specific terrain
        if elevation_data and 'elevation_grid' in elevation_data:
            zone_terrain = self._extract_zone_terrain(zone, elevation_data)
            zone['terrain_data'] = zone_terrain
        
        return zone
    
    def _extract_zone_terrain(self, zone: Dict, elevation_data: Dict) -> Dict:
        """
        Extract terrain data for specific zone
        
        Args:
            zone: Zone dict with geometry
            elevation_data: Full site topography data
            
        Returns:
            Zone-specific terrain data
        """
        zone_geom = zone['geometry']
        zone_bounds = zone_geom.bounds
        
        # Get elevation grid data
        grid_data = elevation_data['elevation_grid']
        full_grid = grid_data['grid']
        x_coords = grid_data['x_coords']
        y_coords = grid_data['y_coords']
        resolution = grid_data['resolution']
        
        # Find grid indices for zone bounds
        minx, miny, maxx, maxy = zone_bounds
        
        x_start = np.searchsorted(x_coords, minx)
        x_end = np.searchsorted(x_coords, maxx)
        y_start = np.searchsorted(y_coords, miny)
        y_end = np.searchsorted(y_coords, maxy)
        
        # Extract zone grid
        zone_grid = full_grid[y_start:y_end, x_start:x_end]
        zone_x = x_coords[x_start:x_end]
        zone_y = y_coords[y_start:y_end]
        
        # Calculate zone slope map
        dy, dx = np.gradient(zone_grid, resolution)
        zone_slope = np.sqrt(dx**2 + dy**2) * 100
        
        # Identify buildable areas
        zone_buildable = zone_slope <= 15.0
        
        terrain_data = {
            'elevation_grid': zone_grid,
            'x_coords': zone_x,
            'y_coords': zone_y,
            'slope_map': zone_slope,
            'buildable_areas': zone_buildable,
            'resolution': resolution,
            'avg_elevation': float(np.mean(zone_grid)),
            'min_elevation': float(np.min(zone_grid)),
            'max_elevation': float(np.max(zone_grid)),
            'avg_slope': float(np.mean(zone_slope)),
            'buildable_percentage': float((zone_buildable.sum() / zone_buildable.size) * 100)
        }
        
        logger.info(f"Zone terrain: avg elevation {terrain_data['avg_elevation']:.1f}m, "
                   f"avg slope {terrain_data['avg_slope']:.1f}%, "
                   f"buildable {terrain_data['buildable_percentage']:.1f}%")
        
        return terrain_data
    
    def calculate_zone_parameters(
        self, 
        zone: Dict,
        terrain_data: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate design parameters for zone
        
        Args:
            zone: Zone dict
            terrain_data: Optional terrain data
            
        Returns:
            Design parameters dict
        """
        area_ha = zone['area_ha']
        area_m2 = zone['area_m2']
        
        # Calculate plot count (0.4 plots per hectare for industrial)
        # For demo: target ~20 plots for 50 ha zone
        plot_count = max(15, min(25, int(area_ha * 0.4)))
        
        # Calculate GFA (40% of site area)
        total_gfa_m2 = area_m2 * 0.4
        
        # Industry distribution
        industrial_gfa = total_gfa_m2 * 0.6  # 60%
        warehouse_gfa = total_gfa_m2 * 0.3   # 30%
        admin_gfa = total_gfa_m2 * 0.1       # 10%
        
        # Plot distribution
        industrial_plots = int(plot_count * 0.6)  # 60%
        warehouse_plots = int(plot_count * 0.25)  # 25%
        support_plots = int(plot_count * 0.1)     # 10%
        admin_plots = max(1, plot_count - industrial_plots - warehouse_plots - support_plots)
        
        # Green space requirement
        green_ratio = 0.15  # 15%
        green_area_m2 = area_m2 * green_ratio
        
        # Fire safety level based on area
        if area_ha < 30:
            fire_level = 'basic'
            fire_stations = 2
        elif area_ha < 70:
            fire_level = 'enhanced'
            fire_stations = 3
        else:
            fire_level = 'comprehensive'
            fire_stations = 4
        
        params = {
            'area_ha': area_ha,
            'area_m2': area_m2,
            'plot_count': plot_count,
            'total_gfa_m2': total_gfa_m2,
            'industry_distribution': {
                'light_manufacturing': {
                    'gfa_m2': industrial_gfa,
                    'plot_count': industrial_plots,
                    'percentage': 60
                },
                'logistics': {
                    'gfa_m2': warehouse_gfa,
                    'plot_count': warehouse_plots,
                    'percentage': 25
                },
                'support': {
                    'gfa_m2': admin_gfa * 0.5,
                    'plot_count': support_plots,
                    'percentage': 10
                },
                'admin': {
                    'gfa_m2': admin_gfa * 0.5,
                    'plot_count': admin_plots,
                    'percentage': 5
                }
            },
            'green_ratio': green_ratio,
            'green_area_m2': green_area_m2,
            'fire_safety_level': fire_level,
            'fire_stations': fire_stations,
            'road_width_main': 20.0,  # meters
            'road_width_secondary': 12.0,  # meters
            'min_plot_spacing': 15.0,  # fire safety spacing
        }
        
        # Add terrain parameters if available
        if terrain_data:
            params['terrain'] = {
                'avg_elevation': terrain_data.get('avg_elevation', 0),
                'elevation_range': terrain_data.get('max_elevation', 0) - terrain_data.get('min_elevation', 0),
                'avg_slope': terrain_data.get('avg_slope', 0),
                'buildable_percentage': terrain_data.get('buildable_percentage', 100),
                'terrain_strategy': 'balanced_cut_fill'
            }
        
        logger.info(f"Zone parameters: {plot_count} plots, "
                   f"{industrial_plots} industrial, {warehouse_plots} warehouse, "
                   f"{support_plots} support, {admin_plots} admin")
        
        return params


# Convenience function
def process_pilot_zone(
    file_path: str,
    zone_id: int = 1,
    extract_terrain: bool = True
) -> Dict:
    """
    Process Pilot DWG and extract specific zone
    
    Args:
        file_path: Path to Pilot DWG/DXF
        zone_id: Zone to extract (1-4)
        extract_terrain: Whether to extract topography
        
    Returns:
        Complete zone data with parameters
    """
    processor = PilotZoneProcessor()
    
    # Extract boundary
    boundary = processor.extract_pilot_boundary(file_path)
    
    # Extract topography if requested
    topo_data = None
    if extract_terrain:
        topo_data = processor.extract_topography_data(file_path)
    
    # Divide into zones
    zones = processor.divide_into_zones(boundary, topo_data)
    
    # Extract specific zone
    zone = processor.extract_zone(zone_id, topo_data)
    
    # Calculate parameters
    terrain_data = zone.get('terrain_data')
    params = processor.calculate_zone_parameters(zone, terrain_data)
    
    # Combine all data
    result = {
        'zone': zone,
        'parameters': params,
        'all_zones': zones,
        'full_boundary': boundary,
        'topography': topo_data
    }
    
    return result
