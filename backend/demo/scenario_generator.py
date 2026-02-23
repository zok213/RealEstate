"""
Scenario Generator for Full-Site Development

Generates multiple development scenarios based on different optimization strategies:
- Scenario A: Cost-Optimized (minimize grading cost)
- Scenario B: Maximum Capacity (maximize plot count)
- Scenario C: Balanced (balance cost and capacity)
"""

import logging
from typing import Dict, List, Optional
import numpy as np
from shapely.geometry import Polygon, Point
import time

from demo.fast_layout_generator import FastLayoutGenerator

logger = logging.getLogger(__name__)


class ScenarioGenerator:
    """
    Generate multiple development scenarios for optimal zones.
    
    Each scenario optimizes for different objectives:
    - Cost: Minimize grading/earthwork costs
    - Capacity: Maximize number of plots
    - Balanced: Optimize both cost and capacity
    """
    
    def __init__(self):
        """Initialize scenario generator."""
        self.layout_generator = FastLayoutGenerator()
        
    def generate_scenarios(
        self,
        site_analysis: Dict,
        target_plot_count: int = 200
    ) -> List[Dict]:
        """
        Generate 3 development scenarios.
        
        Args:
            site_analysis: Full site analysis from FullSiteAnalyzer
            target_plot_count: Target number of plots (default: 200)
            
        Returns:
            List of 3 scenario dictionaries
        """
        logger.info(f"Generating scenarios with target {target_plot_count} plots")
        start_time = time.time()
        
        optimal_zones = site_analysis['optimal_zones']
        terrain_data = site_analysis['terrain_data']
        
        if not optimal_zones:
            logger.error("No optimal zones found for scenario generation")
            return []
        
        # Generate 3 scenarios
        scenarios = []
        
        # Scenario A: Cost-Optimized
        logger.info("Generating Scenario A: Cost-Optimized...")
        scenario_a = self._generate_cost_optimized(
            optimal_zones,
            terrain_data,
            target_plot_count
        )
        scenarios.append(scenario_a)
        
        # Scenario B: Maximum Capacity
        logger.info("Generating Scenario B: Maximum Capacity...")
        scenario_b = self._generate_max_capacity(
            optimal_zones,
            terrain_data,
            target_plot_count
        )
        scenarios.append(scenario_b)
        
        # Scenario C: Balanced
        logger.info("Generating Scenario C: Balanced...")
        scenario_c = self._generate_balanced(
            optimal_zones,
            terrain_data,
            target_plot_count
        )
        scenarios.append(scenario_c)
        
        total_time = time.time() - start_time
        logger.info(f"Generated {len(scenarios)} scenarios in {total_time:.1f}s")
        
        return scenarios
    
    def _generate_cost_optimized(
        self,
        optimal_zones: List[Dict],
        terrain_data: Dict,
        target_plots: int
    ) -> Dict:
        """
        Generate cost-optimized scenario.
        
        Strategy:
        - Select flattest zones (lowest avg slope)
        - Minimize cut/fill volumes
        - Target: 70-80% of target plots
        - Focus on quality over quantity
        
        Args:
            optimal_zones: List of optimal zones
            terrain_data: Terrain data
            target_plots: Target plot count
            
        Returns:
            Scenario dictionary
        """
        start_time = time.time()
        
        # Sort zones by flatness (lowest slope first)
        sorted_zones = sorted(
            optimal_zones,
            key=lambda z: z['metrics']['avg_slope']
        )
        
        # Select flattest zones until we have enough area
        # Target: 150-180 plots (75-90% of target)
        target_area_ha = (target_plots * 0.75) * 0.5  # ~0.5 ha per plot
        selected_zones = []
        total_area = 0
        
        for zone in sorted_zones:
            selected_zones.append(zone)
            total_area += zone['area_ha']
            
            if total_area >= target_area_ha:
                break
        
        logger.info(f"Scenario A: Selected {len(selected_zones)} zones, {total_area:.1f} ha")
        
        # Generate layout for selected zones
        layout = self._generate_layout_for_zones(
            selected_zones,
            terrain_data,
            strategy='cost_optimized'
        )
        
        # Calculate costs
        grading_cost = self._calculate_grading_cost(layout, terrain_data)
        
        # Calculate metrics
        metrics = self._calculate_scenario_metrics(
            layout,
            selected_zones,
            grading_cost
        )
        
        generation_time = time.time() - start_time
        
        return {
            'scenario_id': 'A',
            'name': 'Cost-Optimized',
            'description': 'Tối ưu chi phí san nền - Chọn khu vực phẳng nhất',
            'strategy': 'cost_optimized',
            'selected_zones': selected_zones,
            'layout': layout,
            'metrics': metrics,
            'grading_cost': grading_cost,
            'generation_time_s': generation_time,
            'priority': 'Minimize cost',
            'target_market': 'Cost-sensitive developers'
        }
    
    def _generate_max_capacity(
        self,
        optimal_zones: List[Dict],
        terrain_data: Dict,
        target_plots: int
    ) -> Dict:
        """
        Generate maximum capacity scenario.
        
        Strategy:
        - Select largest zones (max area)
        - Maximize plot count
        - Target: 120-140% of target plots
        - Accept higher grading costs
        
        Args:
            optimal_zones: List of optimal zones
            terrain_data: Terrain data
            target_plots: Target plot count
            
        Returns:
            Scenario dictionary
        """
        start_time = time.time()
        
        # Sort zones by size (largest first)
        sorted_zones = sorted(
            optimal_zones,
            key=lambda z: z['area_ha'],
            reverse=True
        )
        
        # Select largest zones
        # Target: 250-280 plots (125-140% of target)
        target_area_ha = (target_plots * 1.3) * 0.5  # ~0.5 ha per plot
        selected_zones = []
        total_area = 0
        
        for zone in sorted_zones:
            selected_zones.append(zone)
            total_area += zone['area_ha']
            
            if total_area >= target_area_ha:
                break
        
        logger.info(f"Scenario B: Selected {len(selected_zones)} zones, {total_area:.1f} ha")
        
        # Generate layout for selected zones
        layout = self._generate_layout_for_zones(
            selected_zones,
            terrain_data,
            strategy='max_capacity'
        )
        
        # Calculate costs
        grading_cost = self._calculate_grading_cost(layout, terrain_data)
        
        # Calculate metrics
        metrics = self._calculate_scenario_metrics(
            layout,
            selected_zones,
            grading_cost
        )
        
        generation_time = time.time() - start_time
        
        return {
            'scenario_id': 'B',
            'name': 'Maximum Capacity',
            'description': 'Tối đa công suất - Sử dụng tối đa diện tích',
            'strategy': 'max_capacity',
            'selected_zones': selected_zones,
            'layout': layout,
            'metrics': metrics,
            'grading_cost': grading_cost,
            'generation_time_s': generation_time,
            'priority': 'Maximize plots',
            'target_market': 'High-demand areas'
        }
    
    def _generate_balanced(
        self,
        optimal_zones: List[Dict],
        terrain_data: Dict,
        target_plots: int
    ) -> Dict:
        """
        Generate balanced scenario.
        
        Strategy:
        - Balance between cost and capacity
        - Select zones with best overall score
        - Target: 100% of target plots
        - Moderate grading costs
        
        Args:
            optimal_zones: List of optimal zones
            terrain_data: Terrain data
            target_plots: Target plot count
            
        Returns:
            Scenario dictionary
        """
        start_time = time.time()
        
        # Sort zones by total score (best first)
        sorted_zones = sorted(
            optimal_zones,
            key=lambda z: z['scores']['total'],
            reverse=True
        )
        
        # Select best-scored zones
        # Target: 200-230 plots (100-115% of target)
        target_area_ha = target_plots * 0.5  # ~0.5 ha per plot
        selected_zones = []
        total_area = 0
        
        for zone in sorted_zones:
            selected_zones.append(zone)
            total_area += zone['area_ha']
            
            if total_area >= target_area_ha:
                break
        
        logger.info(f"Scenario C: Selected {len(selected_zones)} zones, {total_area:.1f} ha")
        
        # Generate layout for selected zones
        layout = self._generate_layout_for_zones(
            selected_zones,
            terrain_data,
            strategy='balanced'
        )
        
        # Calculate costs
        grading_cost = self._calculate_grading_cost(layout, terrain_data)
        
        # Calculate metrics
        metrics = self._calculate_scenario_metrics(
            layout,
            selected_zones,
            grading_cost
        )
        
        generation_time = time.time() - start_time
        
        return {
            'scenario_id': 'C',
            'name': 'Balanced',
            'description': 'Cân bằng - Tối ưu cả chi phí và công suất',
            'strategy': 'balanced',
            'selected_zones': selected_zones,
            'layout': layout,
            'metrics': metrics,
            'grading_cost': grading_cost,
            'generation_time_s': generation_time,
            'priority': 'Balance cost & capacity',
            'target_market': 'General market'
        }
    
    def _generate_layout_for_zones(
        self,
        zones: List[Dict],
        terrain_data: Dict,
        strategy: str
    ) -> Dict:
        """
        Generate layout for selected zones.
        
        Args:
            zones: List of selected zones
            terrain_data: Terrain data
            strategy: Strategy name
            
        Returns:
            Combined layout dictionary
        """
        # Combine all zones into single development area
        from shapely.ops import unary_union
        
        zone_polygons = [z['geometry'] for z in zones]
        combined_area = unary_union(zone_polygons)
        
        # Calculate total area
        total_area_ha = combined_area.area / 10000
        
        # Estimate plot count based on strategy
        if strategy == 'cost_optimized':
            plots_per_ha = 8  # Conservative
        elif strategy == 'max_capacity':
            plots_per_ha = 12  # Aggressive
        else:  # balanced
            plots_per_ha = 10  # Moderate
        
        target_plots = int(total_area_ha * plots_per_ha)
        
        # Create zone data structure for layout generator
        # Need to rename 'grid' to 'elevation_grid' for compatibility
        compatible_terrain = terrain_data['elevation_grid'].copy()
        compatible_terrain['elevation_grid'] = compatible_terrain.pop('grid')
        
        zone_data = {
            'id': 'combined',
            'geometry': combined_area,
            'area_ha': total_area_ha,
            'terrain_data': compatible_terrain
        }
        
        # Create parameters
        # Calculate plot distribution
        industrial_plots = int(target_plots * 0.60)
        logistics_plots = int(target_plots * 0.25)
        support_plots = int(target_plots * 0.10)
        admin_plots = max(1, target_plots - industrial_plots - logistics_plots - support_plots)
        
        # Fire safety based on area
        if total_area_ha < 30:
            fire_level = 'basic'
            fire_stations = 2
        elif total_area_ha < 70:
            fire_level = 'enhanced'
            fire_stations = 3
        else:
            fire_level = 'comprehensive'
            fire_stations = 4
        
        parameters = {
            'plot_count': target_plots,
            'industrial_ratio': 0.60,
            'warehouse_ratio': 0.20,
            'support_ratio': 0.10,
            'admin_ratio': 0.10,
            'min_plot_size_m2': 3000,
            'max_plot_size_m2': 8000,
            'road_width_main': 16,
            'road_width_secondary': 12,
            'green_ratio': 0.15,
            'fire_safety_level': fire_level,
            'fire_stations': fire_stations,
            'industry_distribution': {
                'light_manufacturing': {
                    'plot_count': industrial_plots,
                    'percentage': 60
                },
                'logistics': {
                    'plot_count': logistics_plots,
                    'percentage': 25
                },
                'support': {
                    'plot_count': support_plots,
                    'percentage': 10
                },
                'admin': {
                    'plot_count': admin_plots,
                    'percentage': 5
                }
            }
        }
        
        # Generate layout using FastLayoutGenerator
        terrain_strategy = 'balanced_cut_fill' if strategy == 'cost_optimized' else 'adaptive'
        generator = FastLayoutGenerator(terrain_strategy=terrain_strategy)
        
        layout = generator.generate_layout(
            zone=zone_data,
            parameters=parameters,
            terrain_data=compatible_terrain
        )
        
        return layout
    
    def _calculate_grading_cost(self, layout: Dict, terrain_data: Dict) -> Dict:
        """
        Calculate grading/earthwork costs.
        
        Args:
            layout: Layout dictionary
            terrain_data: Terrain data
            
        Returns:
            Cost dictionary
        """
        # Get grading cost from layout
        if 'grading_cost' in layout:
            return layout['grading_cost']
        
        # Fallback: estimate based on plot count
        plot_count = len(layout.get('plots', []))
        
        # Rough estimate: 250M VND per plot for grading
        total_cost_vnd = plot_count * 250_000_000
        total_cost_usd = total_cost_vnd / 25000  # 1 USD = 25,000 VND
        
        return {
            'total_cut_m3': 0,
            'total_fill_m3': 0,
            'estimated_cost_vnd': total_cost_vnd,
            'estimated_cost_usd': total_cost_usd
        }
    
    def _calculate_scenario_metrics(
        self,
        layout: Dict,
        zones: List[Dict],
        grading_cost: Dict
    ) -> Dict:
        """
        Calculate comprehensive metrics for scenario.
        
        Args:
            layout: Layout dictionary
            zones: Selected zones
            grading_cost: Grading cost data
            
        Returns:
            Metrics dictionary
        """
        # Calculate areas
        total_zone_area = sum(z['area_ha'] for z in zones)
        
        plots = layout.get('plots', [])
        roads = layout.get('roads', [])
        green_areas = layout.get('green_areas', [])
        
        # Calculate land use
        plot_area = sum(p['geometry'].area for p in plots if 'geometry' in p)
        road_area = sum(r['geometry'].buffer(r.get('width', 12)/2).area 
                       for r in roads if 'geometry' in r)
        green_area = sum(g['geometry'].area for g in green_areas if 'geometry' in g)
        
        total_developed = plot_area + road_area + green_area
        
        # Industry distribution
        industry_counts = {}
        for plot in plots:
            itype = plot.get('industry_type', 'unknown')
            industry_counts[itype] = industry_counts.get(itype, 0) + 1
        
        return {
            'development_area_ha': total_zone_area,
            'plot_count': len(plots),
            'road_count': len(roads),
            'fire_station_count': len(layout.get('fire_stations', [])),
            'green_area_count': len(green_areas),
            'land_use': {
                'plot_area_m2': plot_area,
                'road_area_m2': road_area,
                'green_area_m2': green_area,
                'plot_ratio': plot_area / total_developed if total_developed > 0 else 0,
                'road_ratio': road_area / total_developed if total_developed > 0 else 0,
                'green_ratio': green_area / total_developed if total_developed > 0 else 0
            },
            'industry_distribution': industry_counts,
            'avg_plot_size_m2': plot_area / len(plots) if plots else 0,
            'cost_per_plot_usd': grading_cost['estimated_cost_usd'] / len(plots) if plots else 0
        }
