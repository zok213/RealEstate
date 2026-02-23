"""
DWG Topography Extractor - Extract elevation and terrain data from DWG/DXF files

This module extracts comprehensive topography information including:
- Contour lines with elevation values
- 3D polylines with Z-coordinates
- Point cloud elevation data
- Elevation text annotations
- Existing site features

Optimized for demo performance with 10m grid resolution.
"""

import ezdxf
import numpy as np
import re
import logging
from typing import List, Dict, Tuple, Optional
from shapely.geometry import Polygon, LineString, Point
from scipy.interpolate import griddata
from pathlib import Path

logger = logging.getLogger(__name__)


class DWGTopographyExtractor:
    """Extract topography data from DWG/DXF files"""
    
    # Layer name patterns for topography detection
    CONTOUR_LAYERS = [
        'CONTOUR', 'TOPO', 'ELEVATION', 'C-TOPO', 
        'EXISTING_TOPO', 'EXISTING TOPO', 'TOPOGRAPHY'
    ]
    
    ELEVATION_POINT_LAYERS = [
        'SPOT_ELEVATION', 'SPOT ELEVATION', 'BENCHMARK', 
        'SURVEY_POINTS', 'SURVEY POINTS', 'SPOT_ELEV'
    ]
    
    # Regex patterns for elevation text parsing
    ELEVATION_TEXT_PATTERNS = [
        r'RL\s*[:\-]?\s*(\d+\.?\d*)',      # RL 105.5, RL:105.5
        r'EL\.?\s*(\d+\.?\d*)',             # EL.105.5, EL 105.5
        r'^(\d+\.?\d*)\s*m?$',              # 105.5, 105.5m
        r'ELEV\s*[:\-]?\s*(\d+\.?\d*)',    # ELEV:105.5
    ]
    
    def __init__(self, grid_resolution: float = 10.0):
        """
        Initialize extractor
        
        Args:
            grid_resolution: Grid cell size in meters (default 10m for demo speed)
        """
        self.grid_resolution = grid_resolution
        self.doc = None
        
    def extract_from_file(self, file_path: str) -> Dict:
        """
        Extract all topography data from DWG/DXF file
        
        Args:
            file_path: Path to DWG or DXF file
            
        Returns:
            Dictionary containing:
                - elevation_points: List[(x, y, z)]
                - contour_lines: List[{'elevation': float, 'geometry': LineString}]
                - existing_features: Dict with water, buildings, roads, vegetation
                - elevation_range: Tuple(min_elev, max_elev)
                - point_count: int
        """
        logger.info(f"Extracting topography from: {file_path}")
        
        # Load DXF file (DWG should be converted to DXF first)
        try:
            self.doc = ezdxf.readfile(file_path)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise
            
        msp = self.doc.modelspace()
        
        # Extract different types of elevation data
        elevation_points = []
        contour_lines = []
        
        # 1. Extract contour lines
        contours = self._extract_contour_lines(msp)
        contour_lines.extend(contours)
        logger.info(f"Extracted {len(contours)} contour lines")
        
        # 2. Extract 3D polylines
        polyline_points = self._extract_3d_polylines(msp)
        elevation_points.extend(polyline_points)
        logger.info(f"Extracted {len(polyline_points)} points from 3D polylines")
        
        # 3. Extract elevation points
        point_entities = self._extract_elevation_points(msp)
        elevation_points.extend(point_entities)
        logger.info(f"Extracted {len(point_entities)} elevation point entities")
        
        # 4. Parse elevation text annotations
        text_points = self._parse_elevation_text(msp)
        elevation_points.extend(text_points)
        logger.info(f"Extracted {len(text_points)} points from text annotations")
        
        # 5. Extract points from contour lines for grid interpolation
        contour_points = self._sample_points_from_contours(contour_lines)
        elevation_points.extend(contour_points)
        logger.info(f"Sampled {len(contour_points)} points from contours")
        
        # Calculate elevation range
        if elevation_points:
            elevations = [p[2] for p in elevation_points]
            elevation_range = (min(elevations), max(elevations))
        else:
            elevation_range = (0.0, 0.0)
            logger.warning("No elevation data found!")
        
        result = {
            'elevation_points': elevation_points,
            'contour_lines': contour_lines,
            'elevation_range': elevation_range,
            'point_count': len(elevation_points),
            'contour_count': len(contour_lines)
        }
        
        logger.info(f"Extraction complete: {len(elevation_points)} points, "
                   f"elevation range {elevation_range[0]:.1f}m - {elevation_range[1]:.1f}m")
        
        return result
    
    def _extract_contour_lines(self, msp) -> List[Dict]:
        """
        Extract contour lines from DXF
        
        Returns:
            List of dicts with 'elevation' and 'geometry' (LineString)
        """
        contours = []
        
        for entity in msp:
            # Check if entity is on a contour layer
            layer_name = entity.dxf.layer.upper()
            
            is_contour_layer = any(
                pattern in layer_name 
                for pattern in self.CONTOUR_LAYERS
            )
            
            if not is_contour_layer:
                continue
                
            # Extract polylines
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                try:
                    points = list(entity.get_points())
                    if len(points) < 2:
                        continue
                    
                    # Convert to 2D coordinates
                    coords_2d = [(p[0], p[1]) for p in points]
                    
                    # Try to extract elevation from layer name
                    elevation = self._parse_elevation_from_layer(layer_name)
                    
                    # If no elevation in layer name, try to get from Z-coordinate
                    if elevation is None and len(points[0]) > 2:
                        # Use average Z of all points
                        z_values = [p[2] for p in points if len(p) > 2]
                        if z_values:
                            elevation = np.mean(z_values)
                    
                    if elevation is not None:
                        contours.append({
                            'elevation': elevation,
                            'geometry': LineString(coords_2d)
                        })
                        
                except Exception as e:
                    logger.debug(f"Failed to extract contour: {e}")
                    continue
        
        return contours
    
    def _extract_3d_polylines(self, msp) -> List[Tuple[float, float, float]]:
        """
        Extract elevation points from 3D polylines
        
        Returns:
            List of (x, y, z) tuples
        """
        points_3d = []
        
        for entity in msp:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                try:
                    points = list(entity.get_points())
                    
                    for point in points:
                        # Check if point has Z-coordinate
                        if len(point) > 2 and point[2] != 0:
                            points_3d.append((point[0], point[1], point[2]))
                            
                except Exception as e:
                    logger.debug(f"Failed to extract 3D polyline: {e}")
                    continue
        
        return points_3d
    
    def _extract_elevation_points(self, msp) -> List[Tuple[float, float, float]]:
        """
        Extract POINT entities with elevation
        
        Returns:
            List of (x, y, z) tuples
        """
        elevation_points = []
        
        for entity in msp:
            # Check if on elevation point layer
            layer_name = entity.dxf.layer.upper()
            
            is_elevation_layer = any(
                pattern in layer_name 
                for pattern in self.ELEVATION_POINT_LAYERS
            )
            
            if entity.dxftype() == 'POINT':
                try:
                    location = entity.dxf.location
                    
                    # Only include if has Z-coordinate or on elevation layer
                    if len(location) > 2 and (location[2] != 0 or is_elevation_layer):
                        z = location[2] if len(location) > 2 else 0
                        elevation_points.append((location[0], location[1], z))
                        
                except Exception as e:
                    logger.debug(f"Failed to extract point: {e}")
                    continue
        
        return elevation_points
    
    def _parse_elevation_text(self, msp) -> List[Tuple[float, float, float]]:
        """
        Parse elevation values from text annotations
        
        Returns:
            List of (x, y, z) tuples
        """
        text_elevations = []
        
        for entity in msp:
            if entity.dxftype() in ['TEXT', 'MTEXT']:
                try:
                    # Get text content
                    text = entity.dxf.text if entity.dxftype() == 'TEXT' else entity.text
                    text = text.strip()
                    
                    # Try to parse elevation from text
                    elevation = self._parse_elevation_from_text(text)
                    
                    if elevation is not None:
                        # Get text insertion point
                        insert = entity.dxf.insert
                        text_elevations.append((insert[0], insert[1], elevation))
                        
                except Exception as e:
                    logger.debug(f"Failed to parse text elevation: {e}")
                    continue
        
        return text_elevations
    
    def _parse_elevation_from_layer(self, layer_name: str) -> Optional[float]:
        """
        Try to extract elevation value from layer name
        
        Examples:
            "CONTOUR_105.5" -> 105.5
            "TOPO-100" -> 100.0
            "C-ELEV-110.25" -> 110.25
        """
        # Try to find numbers in layer name
        numbers = re.findall(r'\d+\.?\d*', layer_name)
        
        if numbers:
            try:
                # Take the last number (most likely the elevation)
                return float(numbers[-1])
            except ValueError:
                pass
        
        return None
    
    def _parse_elevation_from_text(self, text: str) -> Optional[float]:
        """
        Parse elevation value from text string
        
        Examples:
            "RL 105.5" -> 105.5
            "EL.100.0" -> 100.0
            "105.5m" -> 105.5
        """
        for pattern in self.ELEVATION_TEXT_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def _sample_points_from_contours(
        self, 
        contour_lines: List[Dict], 
        sample_distance: float = 20.0
    ) -> List[Tuple[float, float, float]]:
        """
        Sample elevation points along contour lines
        
        Args:
            contour_lines: List of contour dicts
            sample_distance: Distance between samples in meters
            
        Returns:
            List of (x, y, z) tuples
        """
        sampled_points = []
        
        for contour in contour_lines:
            elevation = contour['elevation']
            line = contour['geometry']
            
            # Sample points along the line
            line_length = line.length
            num_samples = max(2, int(line_length / sample_distance))
            
            for i in range(num_samples):
                # Interpolate point along line
                distance = (i / (num_samples - 1)) * line_length
                point = line.interpolate(distance)
                
                sampled_points.append((point.x, point.y, elevation))
        
        return sampled_points
    
    def create_elevation_grid(
        self, 
        elevation_points: List[Tuple[float, float, float]],
        boundary: Polygon
    ) -> Dict:
        """
        Create interpolated elevation grid from sparse points
        
        Args:
            elevation_points: List of (x, y, z) tuples
            boundary: Site boundary polygon
            
        Returns:
            Dict with:
                - grid: 2D numpy array of elevations
                - x_coords: 1D array of x coordinates
                - y_coords: 1D array of y coordinates
                - resolution: grid resolution in meters
        """
        if not elevation_points:
            logger.warning("No elevation points to create grid")
            return None
        
        # Get boundary bounds
        minx, miny, maxx, maxy = boundary.bounds
        
        # Create grid coordinates
        x_coords = np.arange(minx, maxx, self.grid_resolution)
        y_coords = np.arange(miny, maxy, self.grid_resolution)
        
        grid_x, grid_y = np.meshgrid(x_coords, y_coords)
        
        # Extract point coordinates and elevations
        points_xy = np.array([(p[0], p[1]) for p in elevation_points])
        elevations = np.array([p[2] for p in elevation_points])
        
        # Interpolate elevation grid
        logger.info(f"Interpolating elevation grid: {len(x_coords)}x{len(y_coords)} cells")
        
        try:
            grid_z = griddata(
                points_xy, 
                elevations, 
                (grid_x, grid_y), 
                method='linear',
                fill_value=np.nan
            )
            
            # Fill NaN values with nearest neighbor
            mask = np.isnan(grid_z)
            if mask.any():
                grid_z_nearest = griddata(
                    points_xy, 
                    elevations, 
                    (grid_x, grid_y), 
                    method='nearest'
                )
                grid_z[mask] = grid_z_nearest[mask]
            
        except Exception as e:
            logger.error(f"Grid interpolation failed: {e}")
            raise
        
        return {
            'grid': grid_z,
            'x_coords': x_coords,
            'y_coords': y_coords,
            'resolution': self.grid_resolution,
            'shape': grid_z.shape
        }
    
    def calculate_slope_map(self, elevation_grid: np.ndarray) -> np.ndarray:
        """
        Calculate slope percentage for each grid cell
        
        Args:
            elevation_grid: 2D array of elevations
            
        Returns:
            2D array of slope percentages
        """
        # Calculate gradients in x and y directions
        dy, dx = np.gradient(elevation_grid, self.grid_resolution)
        
        # Calculate slope magnitude (rise/run)
        slope = np.sqrt(dx**2 + dy**2)
        
        # Convert to percentage
        slope_percent = slope * 100
        
        return slope_percent
    
    def identify_buildable_areas(
        self, 
        slope_map: np.ndarray, 
        max_slope: float = 15.0
    ) -> np.ndarray:
        """
        Identify areas suitable for building
        
        Args:
            slope_map: 2D array of slope percentages
            max_slope: Maximum allowable slope (default 15%)
            
        Returns:
            Boolean mask where True = buildable
        """
        buildable = slope_map <= max_slope
        
        buildable_percent = (buildable.sum() / buildable.size) * 100
        logger.info(f"Buildable area: {buildable_percent:.1f}% of site (slope ≤{max_slope}%)")
        
        return buildable
    
    def calculate_terrain_metrics(self, elevation_grid_data: Dict) -> Dict:
        """
        Calculate comprehensive terrain metrics
        
        Args:
            elevation_grid_data: Output from create_elevation_grid()
            
        Returns:
            Dict with slope_map, buildable_areas, statistics
        """
        grid = elevation_grid_data['grid']
        
        # Calculate slope
        slope_map = self.calculate_slope_map(grid)
        
        # Identify buildable areas
        buildable_areas = self.identify_buildable_areas(slope_map)
        
        # Calculate statistics
        metrics = {
            'slope_map': slope_map,
            'buildable_areas': buildable_areas,
            'avg_slope': float(np.mean(slope_map)),
            'max_slope': float(np.max(slope_map)),
            'min_elevation': float(np.min(grid)),
            'max_elevation': float(np.max(grid)),
            'elevation_range': float(np.max(grid) - np.min(grid)),
            'buildable_percentage': float((buildable_areas.sum() / buildable_areas.size) * 100)
        }
        
        logger.info(f"Terrain metrics: avg slope {metrics['avg_slope']:.1f}%, "
                   f"elevation range {metrics['elevation_range']:.1f}m, "
                   f"buildable {metrics['buildable_percentage']:.1f}%")
        
        return metrics


# Convenience function
def extract_topography(
    file_path: str, 
    boundary: Polygon,
    grid_resolution: float = 10.0
) -> Dict:
    """
    Extract and process topography data from DWG/DXF file
    
    Args:
        file_path: Path to DWG/DXF file
        boundary: Site boundary polygon
        grid_resolution: Grid cell size in meters
        
    Returns:
        Complete topography data including grid and metrics
    """
    extractor = DWGTopographyExtractor(grid_resolution=grid_resolution)
    
    # Extract raw data
    topo_data = extractor.extract_from_file(file_path)
    
    # Create elevation grid
    if topo_data['elevation_points']:
        grid_data = extractor.create_elevation_grid(
            topo_data['elevation_points'],
            boundary
        )
        
        # Calculate terrain metrics
        if grid_data:
            metrics = extractor.calculate_terrain_metrics(grid_data)
            
            # Combine all data
            result = {
                **topo_data,
                'elevation_grid': grid_data,
                'terrain_metrics': metrics
            }
            
            return result
    
    # Return raw data if grid creation failed
    return topo_data
