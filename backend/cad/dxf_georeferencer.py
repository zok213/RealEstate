"""
DXF Georeferencing Module

Converts DXF local coordinates to geographic coordinates (lat/lng) for Mapbox overlay.

Methods:
1. Manual georeferencing: User provides 3+ control points (DXF XY → lat/lng)
2. Automatic: Extract coordinate system from DXF header (if available)
3. Affine transformation for accurate conversion

Output: GeoJSON with proper coordinates for Mapbox display
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
import ezdxf
from shapely.geometry import Point, Polygon, LineString, mapping
import json
import logging

logger = logging.getLogger(__name__)


class DXFGeoreferencer:
    """
    Convert DXF coordinates to geographic coordinates.
    
    Features:
    - Manual georeferencing with control points
    - Affine transformation
    - GeoJSON output for Mapbox
    """
    
    def __init__(self):
        """Initialize georeferencer."""
        self.transformation_matrix = None
        self.control_points = []
        self.is_georeferenced = False
    
    def set_manual_control_points(
        self,
        dxf_points: List[Tuple[float, float]],
        geo_points: List[Tuple[float, float]]
    ):
        """
        Set control points for manual georeferencing.
        
        Args:
            dxf_points: List of (x, y) in DXF coordinates
            geo_points: List of (lng, lat) in geographic coordinates
        
        Requires at least 3 control points for affine transformation.
        """
        if len(dxf_points) < 3 or len(dxf_points) != len(geo_points):
            raise ValueError(
                "Need at least 3 control points, "
                "and same number of DXF and geo points"
            )
        
        self.control_points = list(zip(dxf_points, geo_points))
        
        # Calculate affine transformation matrix
        self.transformation_matrix = self._calculate_affine_transform(
            dxf_points,
            geo_points
        )
        
        self.is_georeferenced = True
        
        logger.info(
            f"[GEOREFERENCE] Set {len(dxf_points)} control points, "
            f"transformation ready"
        )
    
    def auto_georeference_from_dxf(self, dxf_path: str) -> bool:
        """
        Attempt automatic georeferencing from DXF header.
        
        Looks for coordinate system information in DXF file.
        Returns True if successful, False if manual georeferencing needed.
        """
        try:
            doc = ezdxf.readfile(dxf_path)
            
            # Check for EPSG code in header
            if '$EPSG' in doc.header:
                epsg_code = doc.header['$EPSG']
                logger.info(
                    f"[GEOREFERENCE] Found EPSG:{epsg_code} in DXF header"
                )
                
                # Convert using pyproj (would need implementation)
                # For now, return False to require manual georeferencing
                logger.warning(
                    "[GEOREFERENCE] Auto-georeferencing not yet implemented, "
                    "use manual control points"
                )
                return False
            
            # Check for geographic extent variables
            if '$EXTMIN' in doc.header and '$EXTMAX' in doc.header:
                extmin = doc.header['$EXTMIN']
                extmax = doc.header['$EXTMAX']
                
                # Check if coordinates look like lat/lng (small values)
                if abs(extmin[0]) < 180 and abs(extmin[1]) < 90:
                    logger.info(
                        "[GEOREFERENCE] DXF appears to have "
                        "geographic coordinates"
                    )
                    # Identity transformation (already in lat/lng)
                    self.transformation_matrix = np.array([
                        [1, 0, 0],
                        [0, 1, 0],
                        [0, 0, 1]
                    ])
                    self.is_georeferenced = True
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"[GEOREFERENCE] Error reading DXF: {str(e)}")
            return False
    
    def transform_point(
        self,
        x: float,
        y: float
    ) -> Tuple[float, float]:
        """
        Transform DXF point to geographic coordinates.
        
        Args:
            x, y: DXF coordinates
        
        Returns:
            (lng, lat) in geographic coordinates
        """
        if not self.is_georeferenced:
            raise RuntimeError(
                "Not georeferenced. Set control points first."
            )
        
        # Apply affine transformation
        point_homogeneous = np.array([x, y, 1])
        transformed = self.transformation_matrix @ point_homogeneous
        
        return (transformed[0], transformed[1])
    
    def transform_polyline(
        self,
        points: List[Tuple[float, float]]
    ) -> List[Tuple[float, float]]:
        """Transform list of DXF points to geographic coordinates."""
        return [self.transform_point(x, y) for x, y in points]
    
    def dxf_to_geojson(
        self,
        dxf_path: str,
        output_path: Optional[str] = None
    ) -> Dict:
        """
        Convert entire DXF file to GeoJSON.
        
        Args:
            dxf_path: Path to DXF file
            output_path: Optional path to save GeoJSON
        
        Returns:
            GeoJSON FeatureCollection dict
        """
        if not self.is_georeferenced:
            raise RuntimeError(
                "Not georeferenced. Set control points or "
                "run auto_georeference_from_dxf first."
            )
        
        logger.info(f"[GEOREFERENCE] Converting {dxf_path} to GeoJSON")
        
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        features = []
        
        # Process each entity
        for entity in msp:
            feature = self._entity_to_geojson_feature(entity)
            if feature:
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features,
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}
            }
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, indent=2)
            logger.info(f"[GEOREFERENCE] Saved GeoJSON to {output_path}")
        
        logger.info(
            f"[GEOREFERENCE] Converted {len(features)} features to GeoJSON"
        )
        
        return geojson
    
    def _calculate_affine_transform(
        self,
        src_points: List[Tuple[float, float]],
        dst_points: List[Tuple[float, float]]
    ) -> np.ndarray:
        """
        Calculate affine transformation matrix.
        
        Affine transformation: [x', y'] = A * [x, y] + b
        In homogeneous coordinates: [x', y', 1] = M * [x, y, 1]
        
        Matrix M:
        | a  b  tx |
        | c  d  ty |
        | 0  0  1  |
        """
        n = len(src_points)
        
        # Build matrices for least squares
        # A * x = b, where x = [a, b, tx, c, d, ty]
        A = np.zeros((2 * n, 6))
        b = np.zeros(2 * n)
        
        for i, ((x, y), (x_dst, y_dst)) in enumerate(
            zip(src_points, dst_points)
        ):
            # Equation for x'
            A[2*i] = [x, y, 1, 0, 0, 0]
            b[2*i] = x_dst
            
            # Equation for y'
            A[2*i+1] = [0, 0, 0, x, y, 1]
            b[2*i+1] = y_dst
        
        # Solve least squares
        params, residuals, rank, s = np.linalg.lstsq(A, b, rcond=None)
        
        # Build transformation matrix
        matrix = np.array([
            [params[0], params[1], params[2]],
            [params[3], params[4], params[5]],
            [0, 0, 1]
        ])
        
        # Calculate RMS error
        if len(residuals) > 0:
            rmse = np.sqrt(residuals[0] / n)
            logger.info(
                f"[GEOREFERENCE] Transformation RMSE: {rmse:.6f} degrees"
            )
        
        return matrix
    
    def _entity_to_geojson_feature(self, entity) -> Optional[Dict]:
        """Convert DXF entity to GeoJSON feature."""
        try:
            entity_type = entity.dxftype()
            layer = entity.dxf.layer
            
            # POLYLINE / LWPOLYLINE
            if entity_type in ['POLYLINE', 'LWPOLYLINE']:
                points = [
                    self.transform_point(p[0], p[1])
                    for p in entity.get_points()
                ]
                
                # Check if closed
                is_closed = entity.is_closed or (
                    len(points) > 2 and
                    points[0] == points[-1]
                )
                
                if is_closed and len(points) >= 3:
                    # Polygon
                    geometry = mapping(Polygon(points))
                else:
                    # LineString
                    geometry = mapping(LineString(points))
                
                return {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "layer": layer,
                        "type": entity_type,
                        "closed": is_closed
                    }
                }
            
            # LINE
            elif entity_type == 'LINE':
                start = self.transform_point(
                    entity.dxf.start[0],
                    entity.dxf.start[1]
                )
                end = self.transform_point(
                    entity.dxf.end[0],
                    entity.dxf.end[1]
                )
                
                geometry = mapping(LineString([start, end]))
                
                return {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "layer": layer,
                        "type": entity_type
                    }
                }
            
            # CIRCLE
            elif entity_type == 'CIRCLE':
                center = self.transform_point(
                    entity.dxf.center[0],
                    entity.dxf.center[1]
                )
                radius = entity.dxf.radius
                
                # Approximate circle as polygon
                num_segments = 32
                angles = np.linspace(0, 2*np.pi, num_segments+1)
                points = [
                    self.transform_point(
                        entity.dxf.center[0] + radius * np.cos(a),
                        entity.dxf.center[1] + radius * np.sin(a)
                    )
                    for a in angles
                ]
                
                geometry = mapping(Polygon(points))
                
                return {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "layer": layer,
                        "type": entity_type,
                        "center": center,
                        "radius": radius
                    }
                }
            
            # POINT
            elif entity_type == 'POINT':
                point = self.transform_point(
                    entity.dxf.location[0],
                    entity.dxf.location[1]
                )
                
                geometry = mapping(Point(point))
                
                return {
                    "type": "Feature",
                    "geometry": geometry,
                    "properties": {
                        "layer": layer,
                        "type": entity_type
                    }
                }
            
            else:
                # Unsupported entity type
                return None
                
        except Exception as e:
            logger.warning(
                f"[GEOREFERENCE] Error converting entity "
                f"{entity.dxftype()}: {str(e)}"
            )
            return None
    
    def calculate_bounds(self, geojson: Dict) -> Dict:
        """Calculate bounding box for GeoJSON."""
        all_coords = []
        
        for feature in geojson['features']:
            geom = feature['geometry']
            coords = geom['coordinates']
            
            if geom['type'] == 'Polygon':
                all_coords.extend(coords[0])
            elif geom['type'] == 'LineString':
                all_coords.extend(coords)
            elif geom['type'] == 'Point':
                all_coords.append(coords)
        
        if not all_coords:
            return None
        
        lngs = [c[0] for c in all_coords]
        lats = [c[1] for c in all_coords]
        
        return {
            "west": min(lngs),
            "south": min(lats),
            "east": max(lngs),
            "north": max(lats),
            "center": [
                (min(lngs) + max(lngs)) / 2,
                (min(lats) + max(lats)) / 2
            ]
        }


# Example usage
if __name__ == "__main__":
    # Example: Manual georeferencing
    georef = DXFGeoreferencer()
    
    # Control points: (DXF x,y) → (lng, lat)
    # Example for a site in Thailand
    dxf_points = [
        (0, 0),         # DXF origin
        (1000, 0),      # 1km east
        (0, 800)        # 800m north
    ]
    
    geo_points = [
        (100.5000, 13.7500),    # Bangkok area (example)
        (100.5100, 13.7500),    # ~1km east
        (100.5000, 13.7572)     # ~800m north
    ]
    
    georef.set_manual_control_points(dxf_points, geo_points)
    
    # Test transformation
    test_point = (500, 400)
    transformed = georef.transform_point(*test_point)
    print(f"DXF {test_point} → Geographic {transformed}")
    
    # Convert DXF to GeoJSON
    # geojson = georef.dxf_to_geojson(
    #     "site.dxf",
    #     "site_georeferenced.geojson"
    # )
    # bounds = georef.calculate_bounds(geojson)
    # print(f"Bounds: {bounds}")
