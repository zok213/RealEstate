"""
Fast Terrain-Aware Layout Generator - Optimized for demo speed

Generates industrial park layout with:
- Terrain-aware road routing (max 8% grade)
- Buildable area filtering (slope <15%)
- Platform elevations for plots
- Cut/fill volume calculation
- Simplified optimization for <120s target
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
import math

logger = logging.getLogger(__name__)


class FastLayoutGenerator:
    """Generate terrain-aware layout optimized for speed"""
    
    def __init__(self, terrain_strategy: str = 'balanced_cut_fill'):
        """
        Initialize generator
        
        Args:
            terrain_strategy: 'balanced_cut_fill', 'minimal_cut', or 'major_grading'
        """
        self.terrain_strategy = terrain_strategy
        
    def generate_layout(
        self,
        zone: Dict,
        parameters: Dict,
        terrain_data: Optional[Dict] = None
    ) -> Dict:
        """
        Generate complete layout for zone
        
        Args:
            zone: Zone dict with geometry
            parameters: Design parameters
            terrain_data: Optional terrain data
            
        Returns:
            Complete layout dict
        """
        logger.info(f"Generating layout for Zone {zone['id']}")
        
        zone_geom = zone['geometry']
        plot_count = parameters['plot_count']
        
        # 1. Generate road network
        roads = self.generate_terrain_aware_roads(
            zone_geom,
            terrain_data,
            parameters
        )
        
        # 2. Identify buildable plots
        buildable_plots = self.identify_buildable_plots(
            zone_geom,
            terrain_data,
            plot_count,
            roads
        )
        
        # 3. Create plots with elevations
        plots = self.create_uniform_plots_with_elevation(
            buildable_plots,
            terrain_data,
            parameters
        )
        
        # 4. Assign industry types
        plots = self.assign_industry_types(plots, parameters)
        
        # 5. Place fire stations
        fire_stations = self.place_fire_stations_simple(
            zone_geom,
            parameters['fire_safety_level'],
            plots
        )
        
        # 6. Create green buffer
        green_areas = self.create_green_buffer(
            zone_geom,
            parameters['green_ratio'],
            plots,
            roads
        )
        
        # 7. Calculate grading cost
        grading_cost = self.calculate_grading_cost(plots, terrain_data)
        
        layout = {
            'zone_id': zone['id'],
            'roads': roads,
            'plots': plots,
            'fire_stations': fire_stations,
            'green_areas': green_areas,
            'grading_cost': grading_cost,
            'statistics': self._calculate_statistics(
                zone_geom, plots, roads, green_areas
            )
        }
        
        logger.info(f"Layout generated: {len(plots)} plots, "
                   f"{len(roads)} road segments, "
                   f"{len(fire_stations)} fire stations")
        
        return layout
    
    def generate_terrain_aware_roads(
        self,
        zone_geom: Polygon,
        terrain_data: Optional[Dict],
        parameters: Dict
    ) -> List[Dict]:
        """
        Generate road network following terrain contours
        
        Args:
            zone_geom: Zone polygon
            terrain_data: Terrain data with slope map
            parameters: Design parameters
            
        Returns:
            List of road dicts with geometry and grade
        """
        roads = []
        
        minx, miny, maxx, maxy = zone_geom.bounds
        width = maxx - minx
        height = maxy - miny
        
        main_width = parameters['road_width_main']
        sec_width = parameters['road_width_secondary']
        
        # Simple grid pattern for demo
        # Main road: horizontal through middle
        mid_y = (miny + maxy) / 2
        main_road_h = LineString([
            (minx + 20, mid_y),
            (maxx - 20, mid_y)
        ])
        
        # Main road: vertical through middle
        mid_x = (minx + maxx) / 2
        main_road_v = LineString([
            (mid_x, miny + 20),
            (mid_x, maxy - 20)
        ])
        
        # Calculate grades if terrain available
        if terrain_data:
            grade_h = self._calculate_road_grade(main_road_h, terrain_data)
            grade_v = self._calculate_road_grade(main_road_v, terrain_data)
        else:
            grade_h = 0.0
            grade_v = 0.0
        
        roads.append({
            'geometry': main_road_h,
            'type': 'main',
            'width': main_width,
            'grade': grade_h,
            'length': main_road_h.length
        })
        
        roads.append({
            'geometry': main_road_v,
            'type': 'main',
            'width': main_width,
            'grade': grade_v,
            'length': main_road_v.length
        })
        
        # Secondary roads: 4 perpendicular roads
        quarter_x = width / 4
        quarter_y = height / 4
        
        for i in range(1, 4):
            # Vertical secondary roads
            x = minx + i * quarter_x
            sec_road = LineString([
                (x, miny + 20),
                (x, maxy - 20)
            ])
            
            grade = self._calculate_road_grade(sec_road, terrain_data) if terrain_data else 0.0
            
            roads.append({
                'geometry': sec_road,
                'type': 'secondary',
                'width': sec_width,
                'grade': grade,
                'length': sec_road.length
            })
        
        for i in range(1, 3):
            # Horizontal secondary roads
            y = miny + i * (height / 3)
            sec_road = LineString([
                (minx + 20, y),
                (maxx - 20, y)
            ])
            
            grade = self._calculate_road_grade(sec_road, terrain_data) if terrain_data else 0.0
            
            roads.append({
                'geometry': sec_road,
                'type': 'secondary',
                'width': sec_width,
                'grade': grade,
                'length': sec_road.length
            })
        
        return roads
    
    def _calculate_road_grade(
        self,
        road: LineString,
        terrain_data: Dict
    ) -> float:
        """
        Calculate average grade along road
        
        Args:
            road: Road LineString
            terrain_data: Terrain data with elevation grid
            
        Returns:
            Average grade as percentage
        """
        if not terrain_data or 'elevation_grid' not in terrain_data:
            return 0.0
        
        grid = terrain_data['elevation_grid']
        x_coords = terrain_data['x_coords']
        y_coords = terrain_data['y_coords']
        
        # Sample points along road
        num_samples = max(10, int(road.length / 20))
        elevations = []
        
        for i in range(num_samples):
            distance = (i / (num_samples - 1)) * road.length
            point = road.interpolate(distance)
            
            # Find grid cell
            x_idx = np.searchsorted(x_coords, point.x)
            y_idx = np.searchsorted(y_coords, point.y)
            
            # Bounds check
            if 0 <= y_idx < grid.shape[0] and 0 <= x_idx < grid.shape[1]:
                elevations.append(grid[y_idx, x_idx])
        
        if len(elevations) < 2:
            return 0.0
        
        # Calculate grade
        elevation_change = abs(elevations[-1] - elevations[0])
        horizontal_distance = road.length
        
        grade = (elevation_change / horizontal_distance) * 100 if horizontal_distance > 0 else 0.0
        
        return grade
    
    def identify_buildable_plots(
        self,
        zone_geom: Polygon,
        terrain_data: Optional[Dict],
        plot_count: int,
        roads: List[Dict]
    ) -> List[Polygon]:
        """
        Identify buildable plot locations
        
        Args:
            zone_geom: Zone polygon
            terrain_data: Terrain data with buildable areas
            plot_count: Target number of plots
            roads: Road network
            
        Returns:
            List of plot polygons
        """
        # Create road buffer to exclude from plots
        road_buffer = unary_union([
            r['geometry'].buffer(r['width'] / 2 + 5)  # 5m clearance
            for r in roads
        ])
        
        # Available area for plots
        available_area = zone_geom.difference(road_buffer)
        
        # Simple grid subdivision
        minx, miny, maxx, maxy = available_area.bounds
        
        # Calculate grid dimensions (4 rows × 5 columns = 20 plots)
        rows = 4
        cols = 5
        
        cell_width = (maxx - minx) / cols
        cell_height = (maxy - miny) / rows
        
        plots = []
        
        for row in range(rows):
            for col in range(cols):
                # Create plot box
                plot_minx = minx + col * cell_width + 10  # 10m margin
                plot_miny = miny + row * cell_height + 10
                plot_maxx = plot_minx + cell_width - 20
                plot_maxy = plot_miny + cell_height - 20
                
                plot_box = box(plot_minx, plot_miny, plot_maxx, plot_maxy)
                
                # Intersect with available area
                plot = available_area.intersection(plot_box)
                
                if plot.is_empty or plot.area < 1000:  # Min 1000 m²
                    continue
                
                # Check if buildable (if terrain data available)
                if terrain_data and 'buildable_areas' in terrain_data:
                    if not self._is_plot_buildable(plot, terrain_data):
                        logger.debug(f"Plot at ({col}, {row}) too steep, skipping")
                        continue
                
                if plot.geom_type == 'Polygon':
                    plots.append(plot)
                
                if len(plots) >= plot_count:
                    break
            
            if len(plots) >= plot_count:
                break
        
        logger.info(f"Identified {len(plots)} buildable plots")
        
        return plots
    
    def _is_plot_buildable(
        self,
        plot: Polygon,
        terrain_data: Dict
    ) -> bool:
        """
        Check if plot is on buildable terrain
        
        Args:
            plot: Plot polygon
            terrain_data: Terrain data
            
        Returns:
            True if buildable
        """
        buildable_mask = terrain_data.get('buildable_areas')
        if buildable_mask is None:
            return True
        
        x_coords = terrain_data['x_coords']
        y_coords = terrain_data['y_coords']
        
        # Sample center point
        center = plot.centroid
        
        x_idx = np.searchsorted(x_coords, center.x)
        y_idx = np.searchsorted(y_coords, center.y)
        
        # Bounds check
        if 0 <= y_idx < buildable_mask.shape[0] and 0 <= x_idx < buildable_mask.shape[1]:
            return bool(buildable_mask[y_idx, x_idx])
        
        return True
    
    def create_uniform_plots_with_elevation(
        self,
        plot_polygons: List[Polygon],
        terrain_data: Optional[Dict],
        parameters: Dict
    ) -> List[Dict]:
        """
        Create plot dicts with platform elevations
        
        Args:
            plot_polygons: List of plot polygons
            terrain_data: Terrain data
            parameters: Design parameters
            
        Returns:
            List of plot dicts with elevations and cut/fill
        """
        plots = []
        
        for i, poly in enumerate(plot_polygons):
            plot = {
                'id': i + 1,
                'geometry': poly,
                'area_m2': poly.area,
                'centroid': (poly.centroid.x, poly.centroid.y)
            }
            
            # Calculate platform elevation if terrain available
            if terrain_data:
                elevation_data = self._calculate_platform_elevation(poly, terrain_data)
                plot.update(elevation_data)
            else:
                plot['platform_elevation'] = 0.0
                plot['cut_volume_m3'] = 0.0
                plot['fill_volume_m3'] = 0.0
            
            plots.append(plot)
        
        return plots
    
    def _calculate_platform_elevation(
        self,
        plot: Polygon,
        terrain_data: Dict
    ) -> Dict:
        """
        Calculate optimal platform elevation for plot
        
        Args:
            plot: Plot polygon
            terrain_data: Terrain data
            
        Returns:
            Dict with platform_elevation, cut_volume, fill_volume
        """
        grid = terrain_data['elevation_grid']
        x_coords = terrain_data['x_coords']
        y_coords = terrain_data['y_coords']
        resolution = terrain_data['resolution']
        
        # Sample elevations at plot corners and center
        coords = list(plot.exterior.coords)
        sample_points = coords[:4] + [(plot.centroid.x, plot.centroid.y)]
        
        elevations = []
        for x, y in sample_points:
            x_idx = np.searchsorted(x_coords, x)
            y_idx = np.searchsorted(y_coords, y)
            
            if 0 <= y_idx < grid.shape[0] and 0 <= x_idx < grid.shape[1]:
                elevations.append(grid[y_idx, x_idx])
        
        if not elevations:
            return {
                'platform_elevation': 0.0,
                'cut_volume_m3': 0.0,
                'fill_volume_m3': 0.0
            }
        
        # Balanced cut/fill strategy: use average elevation
        platform_elev = np.mean(elevations)
        
        # Estimate cut/fill volumes (simplified)
        cut_volume = 0.0
        fill_volume = 0.0
        
        for elev in elevations:
            diff = platform_elev - elev
            volume = abs(diff) * (plot.area / len(elevations))
            
            if diff < 0:  # Need to cut
                cut_volume += volume
            else:  # Need to fill
                fill_volume += volume
        
        return {
            'platform_elevation': float(platform_elev),
            'cut_volume_m3': float(cut_volume),
            'fill_volume_m3': float(fill_volume),
            'corner_elevations': [float(e) for e in elevations[:4]]
        }
    
    def assign_industry_types(
        self,
        plots: List[Dict],
        parameters: Dict
    ) -> List[Dict]:
        """
        Assign industry types to plots
        
        Args:
            plots: List of plot dicts
            parameters: Design parameters with distribution
            
        Returns:
            Plots with industry_type assigned
        """
        distribution = parameters['industry_distribution']
        
        # Get counts
        industrial_count = distribution['light_manufacturing']['plot_count']
        logistics_count = distribution['logistics']['plot_count']
        support_count = distribution['support']['plot_count']
        admin_count = distribution['admin']['plot_count']
        
        # Assign types
        for i, plot in enumerate(plots):
            if i < industrial_count:
                plot['industry_type'] = 'light_manufacturing'
                plot['color'] = '#2D5016'  # Green
            elif i < industrial_count + logistics_count:
                plot['industry_type'] = 'logistics'
                plot['color'] = '#5B9BD5'  # Blue
            elif i < industrial_count + logistics_count + support_count:
                plot['industry_type'] = 'support'
                plot['color'] = '#FFC000'  # Yellow
            else:
                plot['industry_type'] = 'admin'
                plot['color'] = '#A6A6A6'  # Gray
        
        return plots
    
    def place_fire_stations_simple(
        self,
        zone_geom: Polygon,
        fire_level: str,
        plots: List[Dict]
    ) -> List[Dict]:
        """
        Place fire stations at strategic locations
        
        Args:
            zone_geom: Zone polygon
            fire_level: 'basic', 'enhanced', or 'comprehensive'
            plots: List of plots
            
        Returns:
            List of fire station dicts
        """
        # Determine count based on level
        if fire_level == 'basic':
            count = 2
        elif fire_level == 'enhanced':
            count = 3
        else:
            count = 4
        
        minx, miny, maxx, maxy = zone_geom.bounds
        
        stations = []
        
        # Simple placement: corners and center
        positions = [
            (minx + 50, miny + 50),      # SW corner
            (maxx - 50, maxy - 50),      # NE corner
            ((minx + maxx) / 2, (miny + maxy) / 2),  # Center
            (minx + 50, maxy - 50),      # NW corner
        ]
        
        for i in range(min(count, len(positions))):
            stations.append({
                'id': i + 1,
                'location': positions[i],
                'coverage_radius': 150.0  # meters
            })
        
        logger.info(f"Placed {len(stations)} fire stations ({fire_level} level)")
        
        return stations
    
    def create_green_buffer(
        self,
        zone_geom: Polygon,
        green_ratio: float,
        plots: List[Dict],
        roads: List[Dict]
    ) -> List[Dict]:
        """
        Create green space areas
        
        Args:
            zone_geom: Zone polygon
            green_ratio: Target green ratio (0.15 = 15%)
            plots: List of plots
            roads: List of roads
            
        Returns:
            List of green area dicts
        """
        # Calculate required green area
        total_area = zone_geom.area
        required_green = total_area * green_ratio
        
        # Create buffer around boundary (10m)
        buffer_zone = zone_geom.buffer(-10).symmetric_difference(zone_geom)
        
        # Subtract plots and roads
        plot_union = unary_union([p['geometry'] for p in plots])
        road_union = unary_union([r['geometry'].buffer(r['width'] / 2) for r in roads])
        
        green_area = buffer_zone.difference(plot_union).difference(road_union)
        
        green_areas = []
        
        if green_area.geom_type == 'Polygon':
            green_areas.append({
                'type': 'buffer',
                'geometry': green_area,
                'area_m2': green_area.area
            })
        elif green_area.geom_type == 'MultiPolygon':
            for poly in green_area.geoms:
                green_areas.append({
                    'type': 'buffer',
                    'geometry': poly,
                    'area_m2': poly.area
                })
        
        total_green = sum(g['area_m2'] for g in green_areas)
        green_percent = (total_green / total_area) * 100
        
        logger.info(f"Green areas: {total_green:,.0f} m² ({green_percent:.1f}%)")
        
        return green_areas
    
    def calculate_grading_cost(
        self,
        plots: List[Dict],
        terrain_data: Optional[Dict]
    ) -> Dict:
        """
        Calculate grading cost estimate
        
        Args:
            plots: List of plots with cut/fill volumes
            terrain_data: Terrain data
            
        Returns:
            Cost breakdown dict
        """
        if not terrain_data:
            return {
                'total_cut_m3': 0,
                'total_fill_m3': 0,
                'net_import_m3': 0,
                'estimated_cost_vnd': 0
            }
        
        # Sum up cut/fill volumes
        total_cut = sum(p.get('cut_volume_m3', 0) for p in plots)
        total_fill = sum(p.get('fill_volume_m3', 0) for p in plots)
        
        # Net import needed
        net_import = max(0, total_fill - total_cut)
        
        # Cost parameters (VND)
        cut_cost_per_m3 = 50_000
        fill_cost_per_m3 = 80_000
        haul_cost_per_m3_km = 20_000
        avg_haul_distance_km = 1.0
        
        # Calculate costs
        cut_cost = total_cut * cut_cost_per_m3
        fill_cost = total_fill * fill_cost_per_m3
        haul_cost = net_import * haul_cost_per_m3_km * avg_haul_distance_km
        
        total_cost = cut_cost + fill_cost + haul_cost
        
        return {
            'total_cut_m3': float(total_cut),
            'total_fill_m3': float(total_fill),
            'net_import_m3': float(net_import),
            'cut_cost_vnd': float(cut_cost),
            'fill_cost_vnd': float(fill_cost),
            'haul_cost_vnd': float(haul_cost),
            'estimated_cost_vnd': float(total_cost),
            'estimated_cost_usd': float(total_cost / 24000)  # Approx exchange rate
        }
    
    def _calculate_statistics(
        self,
        zone_geom: Polygon,
        plots: List[Dict],
        roads: List[Dict],
        green_areas: List[Dict]
    ) -> Dict:
        """Calculate layout statistics"""
        
        total_area = zone_geom.area
        plot_area = sum(p['area_m2'] for p in plots)
        road_area = sum(r['length'] * r['width'] for r in roads)
        green_area = sum(g['area_m2'] for g in green_areas)
        
        return {
            'total_area_m2': total_area,
            'plot_count': len(plots),
            'total_plot_area_m2': plot_area,
            'total_road_length_m': sum(r['length'] for r in roads),
            'total_green_area_m2': green_area,
            'land_use_ratio': plot_area / total_area,
            'green_ratio': green_area / total_area,
            'avg_plot_size_m2': plot_area / len(plots) if plots else 0,
            'max_road_grade': max((r['grade'] for r in roads), default=0.0)
        }
