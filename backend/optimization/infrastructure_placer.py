"""
Infrastructure Auto-Placement Module for Industrial Parks

Automatically places key infrastructure systems:
1. Retention ponds (based on rainfall, catchment area, elevation)
2. Water treatment plant (optimal location near water network)
3. Wastewater treatment plant (optimal location near sewer network)
4. Substation (10 rai at geometric center)

Follows IEAT Thailand standards and engineering best practices.
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import logging
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import unary_union
from scipy.spatial import ConvexHull

logger = logging.getLogger(__name__)


class InfrastructurePlacer:
    """
    Intelligent infrastructure placement for industrial parks.
    
    Features:
    - Retention ponds at low elevation points
    - Treatment plants near utility networks
    - Substation at geometric center
    - Considers site constraints and existing lots
    """
    
    def __init__(self):
        """Initialize infrastructure placer with IEAT standards."""
        # IEAT standards
        self.retention_pond_ratio = 20  # 20 rai per 1 rai of pond
        self.substation_area_rai = 10   # 10 rai substation
        self.substation_area_m2 = 10 * 1600  # 16,000 m²
        
        # Buffer zones (meters)
        self.pond_buffer = 20  # 20m buffer from ponds
        self.treatment_buffer = 50  # 50m buffer from treatment plants
        self.substation_buffer = 30  # 30m buffer from substation
    
    def place_all_infrastructure(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        terrain_data: Optional[Dict] = None,
        utility_networks: Optional[Dict] = None,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Place all infrastructure systems automatically.
        
        Args:
            site_boundary: Site boundary polygon
            existing_lots: List of existing lot polygons
            terrain_data: Elevation data (DEM, slope map)
            utility_networks: Existing water/sewer networks
            constraints: Site constraints (exclusion zones, etc.)
        
        Returns:
            {
                "retention_ponds": List[Dict],
                "water_treatment_plant": Dict,
                "wastewater_treatment_plant": Dict,
                "substation": Dict,
                "total_infrastructure_area_m2": float
            }
        """
        logger.info("[INFRASTRUCTURE] Starting infrastructure placement")
        
        # Calculate available space (excluding lots)
        available_space = self._calculate_available_space(
            site_boundary,
            existing_lots,
            constraints
        )
        
        # Step 1: Place retention ponds
        retention_ponds = self.place_retention_ponds(
            site_boundary,
            existing_lots,
            terrain_data,
            available_space
        )
        
        # Step 2: Place substation at center
        substation = self.place_substation(
            site_boundary,
            existing_lots,
            available_space
        )
        
        # Step 3: Place water treatment plant
        water_treatment = self.place_water_treatment_plant(
            site_boundary,
            existing_lots,
            utility_networks,
            available_space,
            [substation] + retention_ponds  # Avoid these
        )
        
        # Step 4: Place wastewater treatment plant
        wastewater_treatment = self.place_wastewater_treatment_plant(
            site_boundary,
            existing_lots,
            utility_networks,
            available_space,
            [substation, water_treatment] + retention_ponds  # Avoid these
        )
        
        # Calculate total infrastructure area
        total_area = (
            sum(p['area_m2'] for p in retention_ponds) +
            substation['area_m2'] +
            water_treatment['area_m2'] +
            wastewater_treatment['area_m2']
        )
        
        logger.info(f"[INFRASTRUCTURE] Total infrastructure area: {total_area/10000:.2f} ha")
        
        return {
            "retention_ponds": retention_ponds,
            "water_treatment_plant": water_treatment,
            "wastewater_treatment_plant": wastewater_treatment,
            "substation": substation,
            "total_infrastructure_area_m2": total_area
        }
    
    def place_retention_ponds(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        terrain_data: Optional[Dict],
        available_space: Polygon
    ) -> List[Dict]:
        """
        Place retention ponds at low elevation points.
        
        IEAT: 20 rai per 1 rai of retention pond.
        Should be at lowest elevation for gravity flow.
        """
        logger.info("[RETENTION PONDS] Calculating pond requirements")
        
        # Calculate required pond area
        site_area_rai = site_boundary.area / 1600
        required_pond_rai = site_area_rai / self.retention_pond_ratio
        required_pond_m2 = required_pond_rai * 1600
        
        logger.info(f"[RETENTION PONDS] Site: {site_area_rai:.1f} rai → Need {required_pond_rai:.1f} rai pond")
        
        # Find low elevation points
        if terrain_data and 'elevation_grid' in terrain_data:
            low_points = self._find_low_elevation_points(
                terrain_data['elevation_grid'],
                terrain_data.get('grid_bounds'),
                num_points=3
            )
        else:
            # No terrain data: place near corners (conservative)
            logger.warning("[RETENTION PONDS] No terrain data, using corner locations")
            low_points = self._find_corner_locations(site_boundary, num=3)
        
        # Place ponds at low points
        ponds = []
        remaining_area = required_pond_m2
        
        for i, point in enumerate(low_points):
            if remaining_area <= 0:
                break
            
            # Each pond: rectangular ~50m x variable length
            pond_width = 50  # meters
            pond_length = min(remaining_area / pond_width, 150)  # max 150m length
            pond_area = pond_width * pond_length
            
            # Check if point is in available space
            if not available_space.contains(point):
                # Find nearest point in available space
                from shapely.ops import nearest_points
                point = nearest_points(point, available_space)[1]
            
            # Create pond polygon
            pond_polygon = self._create_rectangular_pond(
                point,
                pond_width,
                pond_length,
                site_boundary
            )
            
            if pond_polygon and pond_polygon.intersects(available_space):
                ponds.append({
                    "id": f"pond_{i+1}",
                    "polygon": pond_polygon,
                    "area_m2": pond_area,
                    "area_rai": pond_area / 1600,
                    "center": (point.x, point.y),
                    "width_m": pond_width,
                    "length_m": pond_length,
                    "type": "retention_pond"
                })
                
                remaining_area -= pond_area
                logger.info(f"[RETENTION PONDS] Placed pond {i+1}: {pond_area/1600:.2f} rai")
        
        total_pond_area = sum(p['area_m2'] for p in ponds)
        logger.info(f"[RETENTION PONDS] Total pond area: {total_pond_area/1600:.2f} rai (target: {required_pond_rai:.2f} rai)")
        
        return ponds
    
    def place_substation(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        available_space: Polygon
    ) -> Dict:
        """
        Place substation (10 rai) at geometric center of site.
        
        IEAT: Substation should be central for optimal power distribution.
        """
        logger.info("[SUBSTATION] Placing substation at site center")
        
        # Calculate geometric center
        centroid = site_boundary.centroid
        
        # If centroid not in available space, find nearest available point
        if not available_space.contains(centroid):
            from shapely.ops import nearest_points
            centroid = nearest_points(centroid, available_space)[1]
            logger.info("[SUBSTATION] Centroid adjusted to available space")
        
        # Create square substation (10 rai = 16,000 m²)
        # √16000 ≈ 126m per side
        side_length = np.sqrt(self.substation_area_m2)
        
        substation_polygon = self._create_square_polygon(
            centroid,
            side_length
        )
        
        # Ensure within site boundary
        if not substation_polygon.within(site_boundary):
            substation_polygon = substation_polygon.intersection(site_boundary)
        
        logger.info(f"[SUBSTATION] Placed at ({centroid.x:.1f}, {centroid.y:.1f})")
        
        return {
            "id": "substation_main",
            "polygon": substation_polygon,
            "area_m2": self.substation_area_m2,
            "area_rai": self.substation_area_rai,
            "center": (centroid.x, centroid.y),
            "side_length_m": side_length,
            "type": "electrical_substation"
        }
    
    def place_water_treatment_plant(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        utility_networks: Optional[Dict],
        available_space: Polygon,
        avoid_zones: List[Dict]
    ) -> Dict:
        """
        Place water treatment plant near water source/network.
        
        Capacity: 2,000 cmd/rai (cubic meters per day per rai)
        """
        logger.info("[WATER TREATMENT] Placing water treatment plant")
        
        # Calculate required area (estimate: 2-3% of site area)
        site_area_m2 = site_boundary.area
        wtp_area_m2 = site_area_m2 * 0.02  # 2%
        
        # Find optimal location
        if utility_networks and 'water' in utility_networks:
            # Place near water source
            water_source = utility_networks['water'].get('source_point')
            if water_source:
                location = Point(water_source)
            else:
                location = site_boundary.centroid
        else:
            # Place near site entrance (water comes from outside)
            location = self._find_entrance_side(site_boundary)
        
        # Ensure location avoids other infrastructure
        location = self._adjust_for_conflicts(
            location,
            avoid_zones,
            available_space,
            min_distance=self.treatment_buffer
        )
        
        # Create rectangular plant
        width = np.sqrt(wtp_area_m2 * 0.6)  # 60% aspect ratio
        length = wtp_area_m2 / width
        
        wtp_polygon = self._create_rectangular_polygon(
            location,
            width,
            length,
            site_boundary
        )
        
        logger.info(f"[WATER TREATMENT] Placed WTP: {wtp_area_m2/1600:.2f} rai")
        
        return {
            "id": "water_treatment_plant",
            "polygon": wtp_polygon,
            "area_m2": wtp_area_m2,
            "area_rai": wtp_area_m2 / 1600,
            "center": (location.x, location.y),
            "width_m": width,
            "length_m": length,
            "capacity_cmd_per_rai": 2000,
            "type": "water_treatment"
        }
    
    def place_wastewater_treatment_plant(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        utility_networks: Optional[Dict],
        available_space: Polygon,
        avoid_zones: List[Dict]
    ) -> Dict:
        """
        Place wastewater treatment plant near sewer outlet.
        
        Capacity: 500 cmd/rai
        Should be at low elevation for gravity sewer flow.
        """
        logger.info("[WASTEWATER TREATMENT] Placing WWTP")
        
        # Calculate required area (estimate: 3-4% of site area)
        site_area_m2 = site_boundary.area
        wwtp_area_m2 = site_area_m2 * 0.03  # 3%
        
        # Find optimal location (low elevation, near boundary)
        if utility_networks and 'sewer' in utility_networks:
            # Place near sewer outlet
            sewer_outlet = utility_networks['sewer'].get('outlet_point')
            if sewer_outlet:
                location = Point(sewer_outlet)
            else:
                location = self._find_low_boundary_point(site_boundary)
        else:
            # Place at low corner
            location = self._find_low_boundary_point(site_boundary)
        
        # Ensure location avoids other infrastructure
        location = self._adjust_for_conflicts(
            location,
            avoid_zones,
            available_space,
            min_distance=self.treatment_buffer
        )
        
        # Create rectangular plant
        width = np.sqrt(wwtp_area_m2 * 0.6)  # 60% aspect ratio
        length = wwtp_area_m2 / width
        
        wwtp_polygon = self._create_rectangular_polygon(
            location,
            width,
            length,
            site_boundary
        )
        
        logger.info(f"[WASTEWATER TREATMENT] Placed WWTP: {wwtp_area_m2/1600:.2f} rai")
        
        return {
            "id": "wastewater_treatment_plant",
            "polygon": wwtp_polygon,
            "area_m2": wwtp_area_m2,
            "area_rai": wwtp_area_m2 / 1600,
            "center": (location.x, location.y),
            "width_m": width,
            "length_m": length,
            "capacity_cmd_per_rai": 500,
            "type": "wastewater_treatment"
        }
    
    # ==================== HELPER METHODS ====================
    
    def _calculate_available_space(
        self,
        site_boundary: Polygon,
        existing_lots: List[Polygon],
        constraints: Optional[Dict]
    ) -> Polygon:
        """Calculate available space for infrastructure."""
        # Start with full site
        available = site_boundary
        
        # Subtract existing lots
        if existing_lots:
            lots_union = unary_union(existing_lots)
            available = available.difference(lots_union)
        
        # Subtract constraint zones
        if constraints and 'exclusion_zones' in constraints:
            for zone in constraints['exclusion_zones']:
                available = available.difference(zone)
        
        return available
    
    def _find_low_elevation_points(
        self,
        elevation_grid: np.ndarray,
        grid_bounds: Tuple,
        num_points: int = 3
    ) -> List[Point]:
        """Find lowest elevation points in grid."""
        # Flatten grid and find N lowest points
        flat_elevations = elevation_grid.flatten()
        lowest_indices = np.argpartition(flat_elevations, num_points)[:num_points]
        
        # Convert indices back to (row, col)
        rows, cols = np.unravel_index(lowest_indices, elevation_grid.shape)
        
        # Convert to actual coordinates
        xmin, ymin, xmax, ymax = grid_bounds
        x_coords = xmin + (cols / elevation_grid.shape[1]) * (xmax - xmin)
        y_coords = ymin + (rows / elevation_grid.shape[0]) * (ymax - ymin)
        
        return [Point(x, y) for x, y in zip(x_coords, y_coords)]
    
    def _find_corner_locations(
        self,
        boundary: Polygon,
        num: int = 3
    ) -> List[Point]:
        """Find corner locations (fallback when no terrain data)."""
        coords = list(boundary.exterior.coords)[:-1]  # Remove duplicate last point
        
        if len(coords) >= num:
            # Return first N corners
            return [Point(coords[i]) for i in range(num)]
        else:
            return [Point(c) for c in coords]
    
    def _find_entrance_side(self, boundary: Polygon) -> Point:
        """Find location near site entrance (assume first edge)."""
        coords = list(boundary.exterior.coords)
        # Midpoint of first edge
        return Point(
            (coords[0][0] + coords[1][0]) / 2,
            (coords[0][1] + coords[1][1]) / 2
        )
    
    def _find_low_boundary_point(self, boundary: Polygon) -> Point:
        """Find point near boundary at low corner."""
        coords = list(boundary.exterior.coords)
        # Find corner with lowest Y coordinate (assuming Y increases upward)
        min_y_coord = min(coords, key=lambda c: c[1])
        return Point(min_y_coord)
    
    def _adjust_for_conflicts(
        self,
        location: Point,
        avoid_zones: List[Dict],
        available_space: Polygon,
        min_distance: float
    ) -> Point:
        """Adjust location to avoid conflicts."""
        for zone in avoid_zones:
            zone_polygon = zone.get('polygon')
            if zone_polygon and location.distance(zone_polygon) < min_distance:
                # Move away from conflict
                from shapely.ops import nearest_points
                _, far_point = nearest_points(zone_polygon, available_space.boundary)
                location = far_point
                logger.info(f"[INFRASTRUCTURE] Location adjusted to avoid {zone.get('type', 'zone')}")
        
        return location
    
    def _create_rectangular_pond(
        self,
        center: Point,
        width: float,
        length: float,
        boundary: Polygon
    ) -> Polygon:
        """Create rectangular pond polygon."""
        half_w = width / 2
        half_l = length / 2
        
        pond = Polygon([
            (center.x - half_w, center.y - half_l),
            (center.x + half_w, center.y - half_l),
            (center.x + half_w, center.y + half_l),
            (center.x - half_w, center.y + half_l)
        ])
        
        # Ensure within boundary
        if not pond.within(boundary):
            pond = pond.intersection(boundary)
        
        return pond
    
    def _create_square_polygon(self, center: Point, side_length: float) -> Polygon:
        """Create square polygon."""
        half_side = side_length / 2
        return Polygon([
            (center.x - half_side, center.y - half_side),
            (center.x + half_side, center.y - half_side),
            (center.x + half_side, center.y + half_side),
            (center.x - half_side, center.y + half_side)
        ])
    
    def _create_rectangular_polygon(
        self,
        center: Point,
        width: float,
        length: float,
        boundary: Polygon
    ) -> Polygon:
        """Create rectangular polygon."""
        return self._create_rectangular_pond(center, width, length, boundary)


# Example usage
if __name__ == "__main__":
    # Test site
    test_site = Polygon([
        (0, 0),
        (1000, 0),
        (1000, 800),
        (0, 800)
    ])
    
    # Some existing lots
    test_lots = [
        Polygon([(100, 100), (250, 100), (250, 200), (100, 200)]),
        Polygon([(300, 100), (450, 100), (450, 200), (300, 200)]),
    ]
    
    placer = InfrastructurePlacer()
    
    result = placer.place_all_infrastructure(
        test_site,
        test_lots,
        terrain_data=None,
        utility_networks=None,
        constraints=None
    )
    
    print(f"\n✓ Infrastructure Placement Complete")
    print(f"  • Retention ponds: {len(result['retention_ponds'])}")
    print(f"  • Substation: {result['substation']['area_rai']:.1f} rai")
    print(f"  • WTP: {result['water_treatment_plant']['area_rai']:.2f} rai")
    print(f"  • WWTP: {result['wastewater_treatment_plant']['area_rai']:.2f} rai")
    print(f"  • Total: {result['total_infrastructure_area_m2']/10000:.2f} ha")
