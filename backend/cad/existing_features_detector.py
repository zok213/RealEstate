"""
Existing Features Detector

Extracts existing site features from DXF files:
- Water bodies (ponds, lakes, rivers)
- Buildings (existing structures)
- Roads (existing road network)
- Obstacles (trees, utilities, restricted areas)

Used to identify reusable features and constraints for industrial park design.
"""

from typing import List, Dict, Optional
import ezdxf
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ExistingFeaturesDetector:
    """
    Detect existing site features from DXF.
    
    Features:
    - Water body detection (by layer name or closed polylines)
    - Building detection (rectangular closed polylines)
    - Road detection (long linear features)
    - Obstacle detection (any existing structures)
    """
    
    # Layer name patterns for automatic detection
    WATER_LAYERS = [
        'WATER', 'POND', 'LAKE', 'RIVER', 'STREAM',
        'HO', 'NUOC', 'ทางน้ำ', 'บ่อน้ำ'  # Vietnamese, Thai
    ]
    
    BUILDING_LAYERS = [
        'BUILDING', 'STRUCTURE', 'EXISTING_BUILDING',
        'TOA_NHA', 'NHA', 'อาคาร'  # Vietnamese, Thai
    ]
    
    ROAD_LAYERS = [
        'ROAD', 'STREET', 'PATH', 'DUONG', 'ถนน'
    ]
    
    VEGETATION_LAYERS = [
        'TREE', 'VEGETATION', 'GREEN', 'CAY', 'ต้นไม้'
    ]
    
    def __init__(self):
        """Initialize detector."""
        pass
    
    def detect_features(self, dxf_path: str) -> Dict:
        """
        Detect all existing features from DXF.
        
        Args:
            dxf_path: Path to DXF file
        
        Returns:
            {
                "water_bodies": List[Dict],
                "buildings": List[Dict],
                "roads": List[Dict],
                "vegetation": List[Dict],
                "obstacles": List[Dict],
                "boundary": Polygon,
                "summary": Dict
            }
        """
        logger.info(f"[FEATURES] Detecting existing features in {dxf_path}")
        
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        
        # Collect entities by type
        water_bodies = []
        buildings = []
        roads = []
        vegetation = []
        obstacles = []
        
        for entity in msp:
            layer = entity.dxf.layer.upper()
            
            # Water bodies
            if self._is_water_layer(layer):
                feature = self._extract_water_body(entity)
                if feature:
                    water_bodies.append(feature)
            
            # Buildings
            elif self._is_building_layer(layer):
                feature = self._extract_building(entity)
                if feature:
                    buildings.append(feature)
            
            # Roads
            elif self._is_road_layer(layer):
                feature = self._extract_road(entity)
                if feature:
                    roads.append(feature)
            
            # Vegetation
            elif self._is_vegetation_layer(layer):
                feature = self._extract_vegetation(entity)
                if feature:
                    vegetation.append(feature)
            
            # Other obstacles (not in specific layers)
            else:
                feature = self._extract_obstacle(entity)
                if feature:
                    obstacles.append(feature)
        
        # Detect site boundary (largest closed polyline)
        boundary = self._detect_boundary(msp)
        
        # Calculate summary statistics
        summary = self._calculate_summary(
            water_bodies,
            buildings,
            roads,
            vegetation,
            obstacles,
            boundary
        )
        
        logger.info(
            f"[FEATURES] Detected: {len(water_bodies)} water bodies, "
            f"{len(buildings)} buildings, {len(roads)} roads, "
            f"{len(vegetation)} vegetation areas"
        )
        
        return {
            "water_bodies": water_bodies,
            "buildings": buildings,
            "roads": roads,
            "vegetation": vegetation,
            "obstacles": obstacles,
            "boundary": boundary,
            "summary": summary
        }
    
    def classify_reusability(self, features: Dict) -> Dict:
        """
        Classify features by reusability for industrial park design.
        
        Returns:
            {
                "keep_as_is": List[str],      # Feature IDs to preserve
                "reuse_modified": List[str],   # Features to adapt
                "demolish": List[str],         # Features to remove
                "constraints": List[Dict]      # Design constraints
            }
        """
        keep_as_is = []
        reuse_modified = []
        demolish = []
        constraints = []
        
        # Water bodies: Usually keep (expensive to remove)
        for wb in features['water_bodies']:
            if wb['area_m2'] > 5000:  # Large ponds
                keep_as_is.append(wb['id'])
                constraints.append({
                    "type": "exclusion_zone",
                    "polygon": wb['polygon'],
                    "buffer_m": 20,
                    "reason": "Existing water body (expensive to fill)"
                })
            else:  # Small ponds
                reuse_modified.append(wb['id'])
                constraints.append({
                    "type": "optional_retention_pond",
                    "polygon": wb['polygon'],
                    "reason": "Existing small pond (can be expanded)"
                })
        
        # Buildings: Check condition and size
        for bldg in features['buildings']:
            if bldg['area_m2'] > 2000 and bldg.get('condition') != 'poor':
                reuse_modified.append(bldg['id'])
                constraints.append({
                    "type": "existing_building",
                    "polygon": bldg['polygon'],
                    "reason": "Large building (consider reuse)",
                    "reusable": True
                })
            else:
                demolish.append(bldg['id'])
        
        # Roads: Reuse if in good alignment
        for road in features['roads']:
            if road['length_m'] > 100:
                reuse_modified.append(road['id'])
                constraints.append({
                    "type": "existing_road_alignment",
                    "linestring": road['linestring'],
                    "width_m": road.get('width_m', 10),
                    "reason": "Existing road (can be upgraded)"
                })
        
        # Vegetation: Protect significant trees
        for veg in features['vegetation']:
            if veg.get('significant', False):
                keep_as_is.append(veg['id'])
                constraints.append({
                    "type": "protected_vegetation",
                    "polygon": veg['polygon'],
                    "buffer_m": 15,
                    "reason": "Protected trees/vegetation"
                })
        
        logger.info(
            f"[REUSABILITY] Keep: {len(keep_as_is)}, "
            f"Reuse: {len(reuse_modified)}, "
            f"Demolish: {len(demolish)}"
        )
        
        return {
            "keep_as_is": keep_as_is,
            "reuse_modified": reuse_modified,
            "demolish": demolish,
            "constraints": constraints
        }
    
    # ==================== HELPER METHODS ====================
    
    def _is_water_layer(self, layer: str) -> bool:
        """Check if layer name indicates water."""
        return any(pattern in layer for pattern in self.WATER_LAYERS)
    
    def _is_building_layer(self, layer: str) -> bool:
        """Check if layer name indicates building."""
        return any(pattern in layer for pattern in self.BUILDING_LAYERS)
    
    def _is_road_layer(self, layer: str) -> bool:
        """Check if layer name indicates road."""
        return any(pattern in layer for pattern in self.ROAD_LAYERS)
    
    def _is_vegetation_layer(self, layer: str) -> bool:
        """Check if layer name indicates vegetation."""
        return any(pattern in layer for pattern in self.VEGETATION_LAYERS)
    
    def _extract_water_body(self, entity) -> Optional[Dict]:
        """Extract water body feature."""
        try:
            if entity.dxftype() in ['POLYLINE', 'LWPOLYLINE']:
                if not entity.is_closed:
                    return None
                
                points = [(p[0], p[1]) for p in entity.get_points()]
                if len(points) < 3:
                    return None
                
                polygon = Polygon(points)
                
                return {
                    "id": f"water_{id(entity)}",
                    "type": "water_body",
                    "polygon": polygon,
                    "area_m2": polygon.area,
                    "perimeter_m": polygon.length,
                    "centroid": polygon.centroid.coords[0],
                    "layer": entity.dxf.layer
                }
            
            return None
            
        except Exception as e:
            logger.warning(
                f"[FEATURES] Error extracting water body: {str(e)}"
            )
            return None
    
    def _extract_building(self, entity) -> Optional[Dict]:
        """Extract building feature."""
        try:
            if entity.dxftype() in ['POLYLINE', 'LWPOLYLINE']:
                if not entity.is_closed:
                    return None
                
                points = [(p[0], p[1]) for p in entity.get_points()]
                if len(points) < 3:
                    return None
                
                polygon = Polygon(points)
                
                # Check if rectangular (likely building)
                is_rectangular = self._is_rectangular(polygon)
                
                return {
                    "id": f"building_{id(entity)}",
                    "type": "building",
                    "polygon": polygon,
                    "area_m2": polygon.area,
                    "centroid": polygon.centroid.coords[0],
                    "is_rectangular": is_rectangular,
                    "layer": entity.dxf.layer
                }
            
            return None
            
        except Exception as e:
            logger.warning(
                f"[FEATURES] Error extracting building: {str(e)}"
            )
            return None
    
    def _extract_road(self, entity) -> Optional[Dict]:
        """Extract road feature."""
        try:
            if entity.dxftype() in ['POLYLINE', 'LWPOLYLINE', 'LINE']:
                if entity.dxftype() == 'LINE':
                    points = [
                        (entity.dxf.start[0], entity.dxf.start[1]),
                        (entity.dxf.end[0], entity.dxf.end[1])
                    ]
                else:
                    points = [(p[0], p[1]) for p in entity.get_points()]
                
                if len(points) < 2:
                    return None
                
                linestring = LineString(points)
                
                return {
                    "id": f"road_{id(entity)}",
                    "type": "road",
                    "linestring": linestring,
                    "length_m": linestring.length,
                    "start": points[0],
                    "end": points[-1],
                    "layer": entity.dxf.layer
                }
            
            return None
            
        except Exception as e:
            logger.warning(f"[FEATURES] Error extracting road: {str(e)}")
            return None
    
    def _extract_vegetation(self, entity) -> Optional[Dict]:
        """Extract vegetation feature."""
        try:
            if entity.dxftype() == 'CIRCLE':
                center = (entity.dxf.center[0], entity.dxf.center[1])
                radius = entity.dxf.radius
                
                # Create polygon approximation of circle
                num_segments = 16
                angles = np.linspace(0, 2*np.pi, num_segments+1)
                points = [
                    (center[0] + radius * np.cos(a),
                     center[1] + radius * np.sin(a))
                    for a in angles
                ]
                polygon = Polygon(points)
                
                # Significant if large (>5m radius)
                significant = radius > 5
                
                return {
                    "id": f"tree_{id(entity)}",
                    "type": "vegetation",
                    "polygon": polygon,
                    "center": center,
                    "radius_m": radius,
                    "area_m2": np.pi * radius**2,
                    "significant": significant,
                    "layer": entity.dxf.layer
                }
            
            return None
            
        except Exception as e:
            logger.warning(
                f"[FEATURES] Error extracting vegetation: {str(e)}"
            )
            return None
    
    def _extract_obstacle(self, entity) -> Optional[Dict]:
        """Extract generic obstacle."""
        # Only extract closed polylines not in specific layers
        try:
            if entity.dxftype() in ['POLYLINE', 'LWPOLYLINE']:
                if entity.is_closed:
                    points = [(p[0], p[1]) for p in entity.get_points()]
                    if len(points) >= 3:
                        polygon = Polygon(points)
                        return {
                            "id": f"obstacle_{id(entity)}",
                            "type": "obstacle",
                            "polygon": polygon,
                            "area_m2": polygon.area,
                            "layer": entity.dxf.layer
                        }
            return None
        except Exception:
            return None
    
    def _detect_boundary(self, msp) -> Optional[Polygon]:
        """Detect site boundary (largest closed polyline)."""
        try:
            closed_polylines = []
            
            for entity in msp:
                if entity.dxftype() in ['POLYLINE', 'LWPOLYLINE']:
                    if entity.is_closed:
                        points = [(p[0], p[1]) for p in entity.get_points()]
                        if len(points) >= 3:
                            poly = Polygon(points)
                            closed_polylines.append(poly)
            
            if not closed_polylines:
                return None
            
            # Largest polygon is likely the boundary
            boundary = max(closed_polylines, key=lambda p: p.area)
            
            logger.info(
                f"[FEATURES] Detected boundary: "
                f"{boundary.area/10000:.2f} ha"
            )
            
            return boundary
            
        except Exception as e:
            logger.error(f"[FEATURES] Error detecting boundary: {str(e)}")
            return None
    
    def _is_rectangular(self, polygon: Polygon) -> bool:
        """Check if polygon is approximately rectangular."""
        coords = list(polygon.exterior.coords)[:-1]  # Remove duplicate
        if len(coords) != 4:
            return False
        
        # Check angles (should be ~90 degrees)
        angles = []
        for i in range(4):
            p1 = np.array(coords[i])
            p2 = np.array(coords[(i+1) % 4])
            p3 = np.array(coords[(i+2) % 4])
            
            v1 = p2 - p1
            v2 = p3 - p2
            
            angle = np.abs(
                np.arctan2(v2[1], v2[0]) - np.arctan2(v1[1], v1[0])
            )
            angle = np.abs(angle - np.pi/2)  # Distance from 90 degrees
            angles.append(angle)
        
        # All angles should be close to 90 degrees
        return all(a < np.radians(15) for a in angles)  # Within 15 degrees
    
    def _calculate_summary(
        self,
        water_bodies: List,
        buildings: List,
        roads: List,
        vegetation: List,
        obstacles: List,
        boundary: Optional[Polygon]
    ) -> Dict:
        """Calculate summary statistics."""
        total_water_area = sum(wb['area_m2'] for wb in water_bodies)
        total_building_area = sum(b['area_m2'] for b in buildings)
        total_road_length = sum(r['length_m'] for r in roads)
        total_vegetation_area = sum(v['area_m2'] for v in vegetation)
        
        site_area = boundary.area if boundary else 0
        
        return {
            "site_area_m2": site_area,
            "site_area_rai": site_area / 1600,
            "water_bodies_count": len(water_bodies),
            "water_area_m2": total_water_area,
            "water_area_pct": (
                total_water_area / site_area * 100 if site_area > 0 else 0
            ),
            "buildings_count": len(buildings),
            "building_area_m2": total_building_area,
            "building_coverage_pct": (
                total_building_area / site_area * 100
                if site_area > 0 else 0
            ),
            "roads_count": len(roads),
            "road_length_m": total_road_length,
            "vegetation_count": len(vegetation),
            "vegetation_area_m2": total_vegetation_area,
            "obstacles_count": len(obstacles)
        }


# Example usage
if __name__ == "__main__":
    detector = ExistingFeaturesDetector()
    
    # Detect features
    features = detector.detect_features("site_with_existing.dxf")
    
    print(f"\n✓ Feature Detection Complete")
    print(f"  • Water Bodies: {len(features['water_bodies'])}")
    print(f"  • Buildings: {len(features['buildings'])}")
    print(f"  • Roads: {len(features['roads'])}")
    print(f"  • Vegetation: {len(features['vegetation'])}")
    
    # Classify reusability
    reusability = detector.classify_reusability(features)
    
    print(f"\n✓ Reusability Analysis")
    print(f"  • Keep as-is: {len(reusability['keep_as_is'])}")
    print(f"  • Reuse modified: {len(reusability['reuse_modified'])}")
    print(f"  • Demolish: {len(reusability['demolish'])}")
    print(f"  • Constraints: {len(reusability['constraints'])}")
