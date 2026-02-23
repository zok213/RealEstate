"""
Full-Site Analyzer for Pilot DWG

Analyzes entire site (191.42 ha) to identify optimal development zones
and generate multiple development scenarios.
"""

import logging
from typing import Dict, List, Tuple, Optional
import numpy as np
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
import time

from demo.dwg_topography_extractor import DWGTopographyExtractor

logger = logging.getLogger(__name__)


class FullSiteAnalyzer:
    """
    Analyze entire Pilot site to find optimal development zones.
    
    Key objectives:
    1. Identify all buildable areas (slope <= 15%)
    2. Score zones based on multiple criteria
    3. Find optimal contiguous development areas
    4. Generate development scenarios
    """
    
    def __init__(self, grid_resolution: float = 20.0):
        """
        Initialize analyzer.
        
        Args:
            grid_resolution: Grid resolution in meters (20m for speed)
        """
        self.grid_resolution = grid_resolution
        self.topo_extractor = DWGTopographyExtractor(grid_resolution=grid_resolution)
        
    def analyze_entire_site(self, dwg_file: str, site_boundary: Polygon) -> Dict:
        """
        Analyze entire site to find optimal development zones.
        
        Args:
            dwg_file: Path to DWG/DXF file
            site_boundary: Site boundary polygon
            
        Returns:
            {
                'site_area_ha': float,
                'terrain_data': Dict,
                'buildable_zones': List[Dict],
                'optimal_zones': List[Dict],
                'recommendations': Dict
            }
        """
        logger.info(f"Analyzing full site: {site_boundary.area / 10000:.2f} ha")
        start_time = time.time()
        
        # Extract topography for entire site
        logger.info("Extracting topography data...")
        topo_start = time.time()
        terrain_data = self.topo_extractor.extract_from_file(dwg_file)
        logger.info(f"Topography extracted in {time.time() - topo_start:.1f}s")
        
        # Create elevation grid for entire site
        logger.info("Creating elevation grid...")
        grid_start = time.time()
        elevation_grid_data = self.topo_extractor.create_elevation_grid(
            terrain_data['elevation_points'],
            site_boundary
        )
        logger.info(f"Elevation grid created in {time.time() - grid_start:.1f}s")
        
        # Calculate slope map
        logger.info("Calculating slope map...")
        slope_start = time.time()
        slope_map = self.topo_extractor.calculate_slope_map(
            elevation_grid_data['grid']
        )
        logger.info(f"Slope map calculated in {time.time() - slope_start:.1f}s")
        
        # Identify buildable areas
        logger.info("Identifying buildable zones...")
        buildable_start = time.time()
        buildable_mask = self.topo_extractor.identify_buildable_areas(
            slope_map, 
            max_slope=15.0
        )
        logger.info(f"Buildable zones identified in {time.time() - buildable_start:.1f}s")
        
        # Find contiguous buildable zones
        logger.info("Finding contiguous buildable zones...")
        zones_start = time.time()
        buildable_zones = self._find_contiguous_zones(
            buildable_mask,
            elevation_grid_data,
            slope_map,
            site_boundary
        )
        logger.info(f"Found {len(buildable_zones)} contiguous zones in {time.time() - zones_start:.1f}s")
        
        # Score and rank zones
        logger.info("Scoring zones...")
        score_start = time.time()
        scored_zones = self._score_zones(
            buildable_zones,
            elevation_grid_data,
            slope_map,
            site_boundary
        )
        logger.info(f"Zones scored in {time.time() - score_start:.1f}s")
        
        # Select optimal zones
        optimal_zones = self._select_optimal_zones(scored_zones)
        
        total_time = time.time() - start_time
        logger.info(f"Full site analysis completed in {total_time:.1f}s")
        
        # Calculate statistics
        total_buildable_area = sum(z['area_ha'] for z in buildable_zones)
        site_area_ha = site_boundary.area / 10000
        
        return {
            'site_area_ha': site_area_ha,
            'terrain_data': {
                'elevation_grid': elevation_grid_data,
                'grid': elevation_grid_data['grid'],
                'slope_map': slope_map,
                'buildable_mask': buildable_mask,
                'avg_elevation': float(np.nanmean(elevation_grid_data['grid'])),
                'avg_slope': float(np.nanmean(slope_map)),
                'elevation_range': [
                    float(np.nanmin(elevation_grid_data['grid'])),
                    float(np.nanmax(elevation_grid_data['grid']))
                ],
                'x_min': elevation_grid_data['x_coords'][0],
                'y_min': elevation_grid_data['y_coords'][0],
                'resolution': elevation_grid_data['resolution']
            },
            'buildable_zones': buildable_zones,
            'optimal_zones': optimal_zones,
            'statistics': {
                'total_buildable_area_ha': total_buildable_area,
                'buildable_percentage': (total_buildable_area / site_area_ha) * 100,
                'num_zones': len(buildable_zones),
                'num_optimal_zones': len(optimal_zones)
            },
            'processing_time_s': total_time
        }
    
    def _find_contiguous_zones(
        self, 
        buildable_mask: np.ndarray,
        elevation_data: Dict,
        slope_map: np.ndarray,
        site_boundary: Polygon
    ) -> List[Dict]:
        """
        Find contiguous buildable zones using connected components.
        
        Args:
            buildable_mask: Boolean mask of buildable cells
            elevation_data: Elevation grid data
            slope_map: Slope map
            site_boundary: Site boundary
            
        Returns:
            List of zone dictionaries with geometry and metrics
        """
        from scipy import ndimage
        
        # Label connected components
        labeled_array, num_features = ndimage.label(buildable_mask)
        
        zones = []
        grid_resolution = self.grid_resolution
        x_min = elevation_data['x_coords'][0]
        y_min = elevation_data['y_coords'][0]
        
        for zone_id in range(1, num_features + 1):
            # Get cells for this zone
            zone_mask = (labeled_array == zone_id)
            zone_cells = np.argwhere(zone_mask)
            
            if len(zone_cells) < 4:  # Skip tiny zones
                continue
            
            # Calculate zone area
            zone_area_m2 = len(zone_cells) * (grid_resolution ** 2)
            zone_area_ha = zone_area_m2 / 10000
            
            # Skip zones smaller than 5 ha
            if zone_area_ha < 5.0:
                continue
            
            # Create polygon for zone
            # Get boundary cells
            from scipy.ndimage import binary_erosion
            boundary_mask = zone_mask & ~binary_erosion(zone_mask)
            boundary_cells = np.argwhere(boundary_mask)
            
            # Convert to coordinates
            coords = []
            for i, j in boundary_cells:
                x = x_min + j * grid_resolution
                y = y_min + i * grid_resolution
                coords.append((x, y))
            
            if len(coords) < 3:
                continue
            
            # Create convex hull as approximation
            try:
                from shapely.geometry import MultiPoint
                zone_polygon = MultiPoint(coords).convex_hull
                
                # Intersect with site boundary
                zone_polygon = zone_polygon.intersection(site_boundary)
                
                if zone_polygon.is_empty or zone_polygon.area < 50000:  # 5 ha minimum
                    continue
                
            except Exception as e:
                logger.warning(f"Failed to create polygon for zone {zone_id}: {e}")
                continue
            
            # Calculate zone metrics
            zone_elevations = elevation_data['grid'][zone_mask]
            zone_slopes = slope_map[zone_mask]
            
            zone_info = {
                'id': zone_id,
                'geometry': zone_polygon,
                'area_ha': zone_polygon.area / 10000,
                'area_m2': zone_polygon.area,
                'centroid': zone_polygon.centroid,
                'metrics': {
                    'avg_elevation': float(np.nanmean(zone_elevations)),
                    'min_elevation': float(np.nanmin(zone_elevations)),
                    'max_elevation': float(np.nanmax(zone_elevations)),
                    'elevation_range': float(np.nanmax(zone_elevations) - np.nanmin(zone_elevations)),
                    'avg_slope': float(np.nanmean(zone_slopes)),
                    'max_slope': float(np.nanmax(zone_slopes)),
                    'slope_std': float(np.nanstd(zone_slopes))
                }
            }
            
            zones.append(zone_info)
        
        # Sort by area (largest first)
        zones.sort(key=lambda z: z['area_ha'], reverse=True)
        
        logger.info(f"Found {len(zones)} contiguous buildable zones (>5 ha)")
        
        return zones
    
    def _score_zones(
        self,
        zones: List[Dict],
        elevation_data: Dict,
        slope_map: np.ndarray,
        site_boundary: Polygon
    ) -> List[Dict]:
        """
        Score zones based on multiple criteria.
        
        Scoring criteria:
        1. Size (larger is better)
        2. Flatness (lower slope is better)
        3. Elevation uniformity (less variation is better)
        4. Shape regularity (more compact is better)
        5. Accessibility (closer to boundary is better)
        
        Args:
            zones: List of zone dictionaries
            elevation_data: Elevation grid data
            slope_map: Slope map
            site_boundary: Site boundary
            
        Returns:
            Zones with added 'score' and 'rank' fields
        """
        for zone in zones:
            metrics = zone['metrics']
            geometry = zone['geometry']
            
            # 1. Size score (0-100): Larger zones score higher
            # Normalize by max zone area
            max_area = max(z['area_ha'] for z in zones)
            size_score = (zone['area_ha'] / max_area) * 100
            
            # 2. Flatness score (0-100): Lower average slope is better
            # Slope range: 0-15% (buildable), map to 100-0
            flatness_score = max(0, 100 - (metrics['avg_slope'] / 15.0) * 100)
            
            # 3. Elevation uniformity score (0-100): Less variation is better
            # Normalize by max elevation range
            max_elev_range = max(z['metrics']['elevation_range'] for z in zones)
            if max_elev_range > 0:
                uniformity_score = max(0, 100 - (metrics['elevation_range'] / max_elev_range) * 100)
            else:
                uniformity_score = 100
            
            # 4. Shape regularity score (0-100): More compact is better
            # Use isoperimetric quotient: 4π*Area / Perimeter²
            perimeter = geometry.length
            if perimeter > 0:
                compactness = (4 * np.pi * geometry.area) / (perimeter ** 2)
                shape_score = min(100, compactness * 100)
            else:
                shape_score = 0
            
            # 5. Accessibility score (0-100): Closer to boundary is better
            # Distance from centroid to nearest boundary point
            boundary_line = site_boundary.exterior
            distance_to_boundary = zone['centroid'].distance(boundary_line)
            # Normalize by site size
            max_distance = np.sqrt(site_boundary.area) / 2
            accessibility_score = max(0, 100 - (distance_to_boundary / max_distance) * 100)
            
            # Weighted total score
            weights = {
                'size': 0.30,
                'flatness': 0.25,
                'uniformity': 0.20,
                'shape': 0.15,
                'accessibility': 0.10
            }
            
            total_score = (
                size_score * weights['size'] +
                flatness_score * weights['flatness'] +
                uniformity_score * weights['uniformity'] +
                shape_score * weights['shape'] +
                accessibility_score * weights['accessibility']
            )
            
            zone['scores'] = {
                'size': size_score,
                'flatness': flatness_score,
                'uniformity': uniformity_score,
                'shape': shape_score,
                'accessibility': accessibility_score,
                'total': total_score
            }
        
        # Sort by total score
        zones.sort(key=lambda z: z['scores']['total'], reverse=True)
        
        # Add rank
        for rank, zone in enumerate(zones, 1):
            zone['rank'] = rank
        
        return zones
    
    def _select_optimal_zones(self, scored_zones: List[Dict]) -> List[Dict]:
        """
        Select top optimal zones for development.
        
        Selection criteria:
        - Top 3-5 zones by score
        - Minimum 20 ha each
        - Non-overlapping
        
        Args:
            scored_zones: Zones with scores
            
        Returns:
            List of optimal zones
        """
        optimal = []
        
        for zone in scored_zones:
            # Must be at least 20 ha
            if zone['area_ha'] < 20.0:
                continue
            
            # Must score at least 60/100
            if zone['scores']['total'] < 60.0:
                continue
            
            # Check for overlap with already selected zones
            overlaps = False
            for selected in optimal:
                if zone['geometry'].intersects(selected['geometry']):
                    overlaps = True
                    break
            
            if not overlaps:
                optimal.append(zone)
            
            # Stop at 5 optimal zones
            if len(optimal) >= 5:
                break
        
        logger.info(f"Selected {len(optimal)} optimal zones for development")
        
        return optimal
