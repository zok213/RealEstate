"""
Enhanced Layout Generator - Integrates Land Redistribution Pipeline
Combines AI chat parameters with advanced optimization algorithms
"""

import logging
import requests
from typing import Dict, List, Optional, Any
from shapely.geometry import Polygon, mapping, shape
import json
from .terrain_layout_adapter import TerrainLayoutAdapter

logger = logging.getLogger(__name__)


class EnhancedLayoutGenerator:
    """
    Orchestrates comprehensive industrial park layout generation.
    Workflow: Chat AI Parameters → Land Redistribution → Enhanced Elements
    """
    
    def __init__(self, redistribution_api_url: str = "http://localhost:7860"):
        self.redistribution_api_url = redistribution_api_url
        
    def generate_comprehensive_layout(
        self, 
        design_params: Dict[str, Any],
        site_boundary: Polygon
    ) -> Dict[str, Any]:
        """
        Generate complete industrial park layout with diverse elements.
        
        Args:
            design_params: Parameters extracted from AI chat
                - totalArea_ha: Site area in hectares
                - industryFocus: List of industry types with counts
                - salableArea_percent: Target salable area percentage
                - greenArea_percent: Target green area percentage
                - utilityArea_percent: Utility infrastructure percentage
                - plotDimensions: Plot size requirements
                - infrastructure: Infrastructure specifications
                
            site_boundary: Shapely Polygon of site boundary
            
        Returns:
            Comprehensive layout with:
            - Optimized road network (hierarchical)
            - Industrial plots with zone classification
            - Green spaces and parks
            - Utility infrastructure
            - Drainage system
            - Parking areas
            - Service facilities
        """
        logger.info(f"[ENHANCED] Starting comprehensive layout generation")
        logger.info(f"[ENHANCED] Site area: {design_params.get('totalArea_ha')} ha")
        
        # Step 1: Prepare optimization request
        optim_request = self._prepare_optimization_request(
            design_params, 
            site_boundary
        )
        
        # Step 2: Call Land Redistribution API
        try:
            layout_result = self._call_redistribution_api(optim_request)
        except Exception as e:
            logger.error(f"[ENHANCED] Redistribution API failed: {e}")
            # Fallback to simple grid layout
            layout_result = self._generate_fallback_layout(
                design_params, 
                site_boundary
            )
        
        # Step 3: Enhance with additional elements
        enhanced_layout = self._enhance_layout_elements(
            layout_result, 
            design_params
        )
        
        # Step 3.5: Apply terrain-aware adjustments
        terrain_strategy = design_params.get("terrain_strategy", "balanced_cut_fill")
        has_topography = design_params.get("has_topography", False)
        
        if has_topography:
            logger.info(f"[ENHANCED] Applying terrain strategy: {terrain_strategy}")
            terrain_adapter = TerrainLayoutAdapter(terrain_strategy)
            
            # Adjust roads
            if enhanced_layout.get("road_network"):
                enhanced_layout["road_network"]["features"] = \
                    terrain_adapter.adjust_road_layout(
                        enhanced_layout["road_network"].get("features", []),
                        design_params.get("terrain", {})
                    )
            
            # Adjust plots
            if enhanced_layout.get("plots"):
                enhanced_layout["plots"] = terrain_adapter.adjust_plot_placement(
                    enhanced_layout["plots"],
                    design_params.get("terrain", {})
                )
            
            # Calculate terrain costs
            total_area = design_params.get("totalArea_ha", 100) * 10000
            grading_costs = terrain_adapter.calculate_grading_cost(
                total_area,
                design_params.get("terrain", {})
            )
            enhanced_layout["grading_costs"] = grading_costs
        
        # Step 4: Validate against IEAT standards
        validation = self._validate_ieat_compliance(
            enhanced_layout, 
            design_params
        )
        
        return {
            "layout": enhanced_layout,
            "validation": validation,
            "parameters": design_params,
            "metadata": {
                "method": "land_redistribution_pipeline",
                "stages": ["grid_optimization", "subdivision", "infrastructure"],
                "total_plots": len(enhanced_layout.get("plots", [])),
                "road_length_km": enhanced_layout.get("road_network", {}).get("total_length_km", 0)
            }
        }
    
    def _prepare_optimization_request(
        self, 
        design_params: Dict, 
        site_boundary: Polygon
    ) -> Dict:
        """Convert AI chat parameters to optimization API format."""
        
        # Extract key parameters
        total_area_ha = design_params.get("totalArea_ha", 100)
        salable_percent = design_params.get("salableArea_percent", 77)
        green_percent = design_params.get("greenArea_percent", 10)
        terrain_strategy = design_params.get("terrain_strategy", "balanced_cut_fill")
        has_topography = design_params.get("has_topography", False)
        
        # Calculate target areas
        total_area_m2 = total_area_ha * 10000
        salable_area_m2 = total_area_m2 * (salable_percent / 100)
        
        # Determine plot sizes based on industry focus
        industry_focus = design_params.get("industryFocus", [])
        min_lot_width = self._calculate_min_lot_width(industry_focus)
        
        # Adjust spacing based on terrain strategy
        if terrain_strategy == "minimal_cut" and has_topography:
            # Wider spacing to allow for contour-following roads
            spacing_min = 30
            spacing_max = 45
            road_width = 20  # Narrower roads that curve
        elif terrain_strategy == "major_grading":
            # Standard spacing with flat terrain
            spacing_min = 25
            spacing_max = 35
            road_width = 25
        else:  # balanced_cut_fill
            spacing_min = 25
            spacing_max = 40
            road_width = 22
        
        # Build config for optimization engine
        config = {
            "spacing_min": spacing_min,
            "spacing_max": spacing_max,
            "road_width": road_width,
            "min_lot_width": min_lot_width,
            "target_salable_percent": salable_percent,
            "green_area_percent": green_percent,
            "skeleton_branches": self._calculate_skeleton_branches(total_area_ha),
            "enable_amenities": True,
            "enable_advanced_zoning": True,
            "terrain_strategy": terrain_strategy,
            "has_topography": has_topography
        }
        
        # Convert boundary to GeoJSON
        boundary_geojson = {
            "type": "Polygon",
            "coordinates": [[[x, y] for x, y in site_boundary.exterior.coords]]
        }
        
        return {
            "land_plots": [
                {
                    "type": "Polygon",
                    "coordinates": boundary_geojson["coordinates"]
                }
            ],
            "config": config
        }
    
    def _calculate_min_lot_width(self, industry_focus: List[Dict]) -> float:
        """Calculate minimum lot width based on industry types."""
        # Default widths by industry type
        width_by_type = {
            "light_manufacturing": 90,
            "medium_manufacturing": 120,
            "heavy_manufacturing": 150,
            "warehouse": 80,
            "logistics": 100,
            "food_processing": 70
        }
        
        if not industry_focus:
            return 90  # Default
        
        # Use weighted average
        total_percentage = sum(ind.get("percentage", 0) for ind in industry_focus)
        if total_percentage == 0:
            return 90
        
        weighted_width = sum(
            width_by_type.get(ind.get("type", ""), 90) * ind.get("percentage", 0)
            for ind in industry_focus
        ) / total_percentage
        
        return round(weighted_width)
    
    def _calculate_skeleton_branches(self, area_ha: float) -> int:
        """Calculate number of skeleton road branches based on site area."""
        # Rule of thumb: 1 branch per 10-15 hectares
        if area_ha < 50:
            return 8
        elif area_ha < 100:
            return 12
        elif area_ha < 200:
            return 18
        else:
            return max(20, int(area_ha / 10))
    
    def _call_redistribution_api(self, request: Dict) -> Dict:
        """Call Land Redistribution API endpoint."""
        url = f"{self.redistribution_api_url}/api/optimize"
        
        logger.info(f"[ENHANCED] Calling redistribution API: {url}")
        
        response = requests.post(
            url, 
            json=request,
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code != 200:
            raise Exception(f"API returned {response.status_code}: {response.text}")
        
        result = response.json()
        logger.info(f"[ENHANCED] Received {len(result.get('stages', []))} optimization stages")
        
        return result
    
    def _generate_fallback_layout(
        self, 
        design_params: Dict, 
        site_boundary: Polygon
    ) -> Dict:
        """Generate simple grid layout when redistribution API unavailable."""
        logger.warning("[ENHANCED] Using fallback grid layout")
        
        from optimization.csp_solver import IndustrialParkCSP
        
        # Use existing CSP solver as fallback
        total_area = design_params.get("totalArea_ha", 100) * 10000
        
        csp = IndustrialParkCSP(
            site_boundary=site_boundary,
            total_area_m2=total_area,
            constraints=design_params.get("constraints", {})
        )
        
        solution = csp.solve()
        
        return {
            "stages": [
                {
                    "stage_name": "Grid Layout (Fallback)",
                    "geometry": {
                        "type": "FeatureCollection",
                        "features": solution.get("features", [])
                    }
                }
            ]
        }
    
    def _enhance_layout_elements(
        self, 
        layout_result: Dict, 
        design_params: Dict
    ) -> Dict:
        """Add enhanced elements to optimize layout."""
        
        # Extract plots from optimization result
        plots = []
        road_network = {}
        infrastructure = []
        amenities = []
        
        for stage in layout_result.get("stages", []):
            stage_name = stage.get("stage_name", "")
            features = stage.get("geometry", {}).get("features", [])
            
            if "Subdivision" in stage_name or "lots" in stage_name.lower():
                # Extract industrial plots
                for feature in features:
                    props = feature.get("properties", {})
                    if props.get("type") == "lot":
                        plots.append({
                            "geometry": feature["geometry"],
                            "zone": props.get("zone", "WAREHOUSE"),
                            "area_m2": props.get("area", 0),
                            "width_m": props.get("width", 0),
                            "zone_color": props.get("zone_color", "#9E9E9E")
                        })
            
            elif "road" in stage_name.lower():
                # Extract road network
                road_features = [f for f in features if f["properties"].get("type") in ["road", "main_road", "internal_road"]]
                road_network = {
                    "features": road_features,
                    "total_length_km": sum(
                        self._calculate_line_length(f["geometry"]) / 1000 
                        for f in road_features
                    )
                }
            
            elif "infrastructure" in stage_name.lower():
                # Infrastructure elements
                infrastructure.extend(features)
            
            # Look for amenities (parks, water features)
            amenity_types = ["park", "green", "water", "lake", "amenity"]
            for feature in features:
                if any(t in feature["properties"].get("type", "").lower() for t in amenity_types):
                    amenities.append(feature)
        
        # Add parking areas based on plot zones
        parking_areas = self._generate_parking_areas(plots, design_params)
        
        # Add service facilities
        service_facilities = self._generate_service_facilities(plots, design_params)
        
        # Calculate area distribution
        area_stats = self._calculate_area_distribution(
            plots, 
            road_network, 
            amenities,
            design_params.get("totalArea_ha", 100) * 10000
        )
        
        return {
            "plots": plots,
            "road_network": road_network,
            "infrastructure": infrastructure,
            "amenities": amenities,
            "parking_areas": parking_areas,
            "service_facilities": service_facilities,
            "area_statistics": area_stats
        }
    
    def _calculate_line_length(self, geom: Dict) -> float:
        """Calculate length of LineString geometry."""
        line = shape(geom)
        return line.length if hasattr(line, 'length') else 0
    
    def _generate_parking_areas(self, plots: List[Dict], design_params: Dict) -> List[Dict]:
        """Generate parking areas near plots."""
        parking = []
        
        # Rule: 10% of each plot area for parking
        for plot in plots[:5]:  # Sample first 5 plots
            plot_geom = shape(plot["geometry"])
            # Create small parking polygon adjacent to plot
            centroid = plot_geom.centroid
            parking_size = 20  # 20m x 20m parking
            
            parking_poly = Polygon([
                (centroid.x - parking_size/2, centroid.y - parking_size/2),
                (centroid.x + parking_size/2, centroid.y - parking_size/2),
                (centroid.x + parking_size/2, centroid.y + parking_size/2),
                (centroid.x - parking_size/2, centroid.y + parking_size/2),
            ])
            
            parking.append({
                "type": "Feature",
                "geometry": mapping(parking_poly),
                "properties": {
                    "type": "parking",
                    "capacity": 50,
                    "associated_plot": plot.get("zone")
                }
            })
        
        return parking
    
    def _generate_service_facilities(self, plots: List[Dict], design_params: Dict) -> List[Dict]:
        """Generate service facilities (fire station, admin, cafeteria)."""
        facilities = []
        
        # Calculate site center
        if not plots:
            return facilities
        
        all_coords = []
        for plot in plots:
            geom = shape(plot["geometry"])
            all_coords.extend(list(geom.exterior.coords))
        
        if not all_coords:
            return facilities
        
        center_x = sum(x for x, y in all_coords) / len(all_coords)
        center_y = sum(y for x, y in all_coords) / len(all_coords)
        
        # Add facilities
        facility_types = [
            {"type": "fire_station", "size": 50, "offset_x": -100, "offset_y": 0},
            {"type": "admin_building", "size": 40, "offset_x": 0, "offset_y": 100},
            {"type": "cafeteria", "size": 30, "offset_x": 100, "offset_y": 0},
        ]
        
        for fac in facility_types:
            fac_poly = Polygon([
                (center_x + fac["offset_x"] - fac["size"]/2, center_y + fac["offset_y"] - fac["size"]/2),
                (center_x + fac["offset_x"] + fac["size"]/2, center_y + fac["offset_y"] - fac["size"]/2),
                (center_x + fac["offset_x"] + fac["size"]/2, center_y + fac["offset_y"] + fac["size"]/2),
                (center_x + fac["offset_x"] - fac["size"]/2, center_y + fac["offset_y"] + fac["size"]/2),
            ])
            
            facilities.append({
                "type": "Feature",
                "geometry": mapping(fac_poly),
                "properties": {
                    "type": fac["type"],
                    "name": fac["type"].replace("_", " ").title()
                }
            })
        
        return facilities
    
    def _calculate_area_distribution(
        self, 
        plots: List[Dict], 
        road_network: Dict,
        amenities: List[Dict],
        total_area_m2: float
    ) -> Dict:
        """Calculate area distribution statistics."""
        
        salable_area = sum(plot.get("area_m2", 0) for plot in plots)
        road_area = road_network.get("total_length_km", 0) * 1000 * 25  # Assume 25m width
        green_area = sum(
            shape(am["geometry"]).area 
            for am in amenities 
            if am["properties"].get("type") in ["park", "green"]
        )
        
        return {
            "total_area_m2": total_area_m2,
            "salable_area_m2": salable_area,
            "salable_percent": (salable_area / total_area_m2) * 100 if total_area_m2 > 0 else 0,
            "road_area_m2": road_area,
            "road_percent": (road_area / total_area_m2) * 100 if total_area_m2 > 0 else 0,
            "green_area_m2": green_area,
            "green_percent": (green_area / total_area_m2) * 100 if total_area_m2 > 0 else 0,
            "plot_count": len(plots),
            "average_plot_size_m2": salable_area / len(plots) if plots else 0
        }
    
    def _validate_ieat_compliance(
        self, 
        layout: Dict, 
        design_params: Dict
    ) -> Dict:
        """Validate layout against IEAT Thailand standards."""
        
        stats = layout.get("area_statistics", {})
        total_area_rai = design_params.get("totalArea_ha", 100) * 6.25
        
        validation = {
            "compliant": True,
            "rules": {},
            "warnings": [],
            "recommendations": []
        }
        
        # Check salable area
        salable_pct = stats.get("salable_percent", 0)
        validation["rules"]["salable_area"] = {
            "compliant": salable_pct >= 75,
            "actual": f"{salable_pct:.1f}%",
            "target": "≥75%"
        }
        
        # Check green area
        green_pct = stats.get("green_percent", 0)
        validation["rules"]["green_area"] = {
            "compliant": green_pct >= 10,
            "actual": f"{green_pct:.1f}%",
            "target": "≥10%"
        }
        
        # Check plot sizes
        avg_plot = stats.get("average_plot_size_m2", 0)
        validation["rules"]["plot_size"] = {
            "compliant": avg_plot >= 8100,  # 90m x 90m min
            "actual": f"{avg_plot:.0f} m²",
            "target": "≥8,100 m²"
        }
        
        validation["compliant"] = all(r["compliant"] for r in validation["rules"].values())
        
        if validation["compliant"]:
            validation["recommendations"].append("✅ Layout meets all IEAT Thailand standards")
        
        return validation
