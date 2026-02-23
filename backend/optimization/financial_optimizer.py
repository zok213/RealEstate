"""
Financial Optimization Module

Calculate construction costs, revenue projections, and ROI
for industrial park master plans.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from shapely.geometry import Polygon, LineString, Point
import numpy as np


@dataclass
class CostParameters:
    """Construction cost parameters (VND per unit)"""
    
    # Site preparation
    site_clearing_per_m2: float = 50_000  # VND/m² (~$2)
    grading_per_m2: float = 30_000        # VND/m²
    
    # Infrastructure
    road_cost_per_meter: float = 8_000_000   # VND/m (~$320/m)
    main_road_multiplier: float = 1.5        # 50% more for main roads
    
    # Utilities
    water_pipe_per_meter: float = 500_000    # VND/m
    sewer_pipe_per_meter: float = 800_000    # VND/m
    electric_cable_per_meter: float = 400_000 # VND/m
    utility_connection_per_lot: float = 100_000_000  # VND/lot (~$4,000)
    
    # Green space
    landscaping_per_m2: float = 150_000      # VND/m²
    tree_planting_per_unit: float = 2_000_000 # VND/tree
    
    # Overhead
    design_fee_percentage: float = 0.03      # 3% of total
    contingency_percentage: float = 0.10     # 10% buffer


@dataclass
class RevenueParameters:
    """Revenue parameters for lot sales"""
    
    # Base prices by zone type (VND per m²)
    base_price_factory: float = 3_000_000       # ~$120/m²
    base_price_warehouse: float = 2_500_000     # ~$100/m²
    base_price_office: float = 4_000_000        # ~$160/m²
    
    # Premiums
    corner_lot_premium: float = 0.20            # +20%
    high_quality_premium: float = 0.15          # +15% (score >85)
    frontage_premium_per_meter: float = 50_000  # VND per meter
    
    # Discounts
    large_lot_discount: float = 0.10            # -10% for >5000m²
    irregular_shape_discount: float = 0.05      # -5% for low quality
    
    # Market adjustments
    market_demand_multiplier: float = 1.0       # Adjust based on market


class FinancialModel:
    """
    Calculate comprehensive financial metrics for industrial park layouts
    """
    
    def __init__(
        self,
        cost_params: CostParameters = None,
        revenue_params: RevenueParameters = None
    ):
        self.cost_params = cost_params or CostParameters()
        self.revenue_params = revenue_params or RevenueParameters()
    
    def calculate_construction_cost(
        self,
        design: Dict[str, Any],
        terrain_strategy: str = "balanced_cut_fill",
        utility_network_costs: Dict[str, float] = None
    ) -> Dict[str, float]:
        """
        Calculate total construction cost breakdown
        
        Args:
            design: Design with lots, roads, utilities, green_spaces
            terrain_strategy: Grading strategy (minimal_cut, balanced, major)
            
        Returns:
            Dict with cost breakdown and total
        """
        costs = {}
        
        # 1. Site preparation
        total_area = design.get('total_area', 0)
        if total_area == 0 and 'lots' in design:
            # Calculate from lots if not provided
            total_area = sum(
                lot.get('geometry', Polygon()).area if isinstance(lot.get('geometry'), Polygon)
                else lot.get('area', 0)
                for lot in design.get('lots', [])
            )
        
        costs['site_clearing'] = total_area * self.cost_params.site_clearing_per_m2
        
        # Terrain-aware grading costs
        if terrain_strategy == "minimal_cut":
            # Lower earthwork, higher retaining walls
            costs['grading'] = total_area * (self.cost_params.grading_per_m2 * 0.3)
            costs['retaining_walls'] = total_area * 0.02 * 2_000_000  # THB
        elif terrain_strategy == "major_grading":
            # Maximum earthwork, no retaining walls
            costs['grading'] = total_area * (self.cost_params.grading_per_m2 * 2.5)
            costs['retaining_walls'] = 0
        else:  # balanced_cut_fill
            # Standard grading costs
            costs['grading'] = total_area * self.cost_params.grading_per_m2
            costs['retaining_walls'] = total_area * 0.01 * 2_000_000  # THB
        
        # 2. Road construction
        roads = design.get('roads', [])
        road_cost = 0
        total_road_length = 0
        
        for road in roads:
            if isinstance(road, dict):
                length = road.get('length', 0)
                road_type = road.get('type', 'internal')
            elif isinstance(road, LineString):
                length = road.length
                road_type = 'internal'
            else:
                continue
            
            base_cost = length * self.cost_params.road_cost_per_meter
            
            if road_type == 'main':
                base_cost *= self.cost_params.main_road_multiplier
            
            road_cost += base_cost
            total_road_length += length
        
        costs['roads'] = road_cost
        
        # 3. Utility infrastructure
        if utility_network_costs:
            costs['water_pipes'] = utility_network_costs.get('water_pipes', 0)
            costs['sewer_pipes'] = utility_network_costs.get('sewer_pipes', 0)
            costs['electric_cables'] = utility_network_costs.get('electric_cables', 0)
            # Use real values if provided, otherwise fallback (or 0 if not key)
        else:
            # Estimate utility length as same as road network
            costs['water_pipes'] = (
                total_road_length * self.cost_params.water_pipe_per_meter
            )
            costs['sewer_pipes'] = (
                total_road_length * self.cost_params.sewer_pipe_per_meter
            )
            costs['electric_cables'] = (
                total_road_length * self.cost_params.electric_cable_per_meter
            )
        
        # Utility connections per lot
        num_lots = len(design.get('lots', []))
        costs['utility_connections'] = (
            num_lots * self.cost_params.utility_connection_per_lot
        )
        
        # 4. Green space
        green_area = design.get('green_space_area', 0)
        if green_area == 0:
            # Estimate as 15% of total area (typical requirement)
            green_area = total_area * 0.15
        
        costs['landscaping'] = green_area * self.cost_params.landscaping_per_m2
        
        # Estimate 1 tree per 50m² of green space
        num_trees = int(green_area / 50)
        costs['tree_planting'] = num_trees * self.cost_params.tree_planting_per_unit
        
        # 5. Calculate subtotal
        subtotal = sum(costs.values())
        
        # 6. Add overhead
        costs['design_fee'] = subtotal * self.cost_params.design_fee_percentage
        costs['contingency'] = subtotal * self.cost_params.contingency_percentage
        
        # 7. Total
        costs['total_construction_cost'] = sum(costs.values())
        
        return costs
    
    def calculate_revenue(
        self,
        lots: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate revenue projection from lot sales
        
        Args:
            lots: List of lot dictionaries with geometry, quality, zone_type
            
        Returns:
            Dict with revenue breakdown and total
        """
        revenue_breakdown = []
        total_revenue = 0
        
        for lot in lots:
            lot_revenue = self._calculate_lot_revenue(lot)
            revenue_breakdown.append(lot_revenue)
            total_revenue += lot_revenue['revenue']
        
        total_area = sum(
            lot.get('geometry', Polygon()).area if isinstance(lot.get('geometry'), Polygon)
            else lot.get('area', 0)
            for lot in lots
        )
        
        return {
            'total_revenue': total_revenue,
            'lots': revenue_breakdown,
            'avg_price_per_m2': total_revenue / total_area if total_area > 0 else 0,
            'num_lots': len(lots)
        }
    
    def _calculate_lot_revenue(
        self,
        lot: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate revenue for single lot with premiums/discounts"""
        
        # Extract geometry and area
        geom = lot.get('geometry')
        if isinstance(geom, Polygon):
            area = geom.area
        else:
            area = lot.get('area', 0)
        
        if area == 0:
            return {
                'lot_id': lot.get('id', 0),
                'area': 0,
                'base_price_per_m2': 0,
                'adjustments': {},
                'revenue': 0,
                'price_per_m2': 0
            }
        
        zone_type = lot.get('zone_type', lot.get('zone', 'FACTORY'))
        quality_score = lot.get('quality_score', 70)
        is_corner = lot.get('is_corner', False)
        frontage = lot.get('frontage', 0)
        
        # Base price
        if zone_type in ['FACTORY', 'MANUFACTURING', 'INDUSTRIAL']:
            base_price = self.revenue_params.base_price_factory
        elif zone_type in ['WAREHOUSE', 'LOGISTICS', 'STORAGE']:
            base_price = self.revenue_params.base_price_warehouse
        elif zone_type in ['OFFICE', 'COMMERCIAL', 'ADMIN']:
            base_price = self.revenue_params.base_price_office
        else:
            base_price = self.revenue_params.base_price_factory
        
        base_revenue = area * base_price
        
        # Apply premiums
        adjustments = {'base': base_revenue}
        
        # Corner lot premium
        if is_corner:
            corner_premium = base_revenue * self.revenue_params.corner_lot_premium
            adjustments['corner_premium'] = corner_premium
        else:
            adjustments['corner_premium'] = 0
        
        # Quality premium
        if quality_score > 85:
            quality_premium = base_revenue * self.revenue_params.high_quality_premium
            adjustments['quality_premium'] = quality_premium
        else:
            adjustments['quality_premium'] = 0
        
        # Frontage premium
        if frontage > 0:
            frontage_premium = frontage * self.revenue_params.frontage_premium_per_meter
            adjustments['frontage_premium'] = frontage_premium
        else:
            adjustments['frontage_premium'] = 0
        
        # Apply discounts
        # Large lot discount
        if area > 5000:
            large_discount = -base_revenue * self.revenue_params.large_lot_discount
            adjustments['large_lot_discount'] = large_discount
        else:
            adjustments['large_lot_discount'] = 0
        
        # Irregular shape discount
        if quality_score < 60:
            shape_discount = -base_revenue * self.revenue_params.irregular_shape_discount
            adjustments['irregular_shape_discount'] = shape_discount
        else:
            adjustments['irregular_shape_discount'] = 0
        
        # Market adjustment
        market_adjustment = base_revenue * (
            self.revenue_params.market_demand_multiplier - 1.0
        )
        adjustments['market_adjustment'] = market_adjustment
        
        # Total revenue
        total_revenue = sum(adjustments.values())
        
        return {
            'lot_id': lot.get('id', 0),
            'area': area,
            'base_price_per_m2': base_price,
            'adjustments': adjustments,
            'revenue': total_revenue,
            'price_per_m2': total_revenue / area if area > 0 else 0
        }
    
    def calculate_roi_metrics(
        self,
        design: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive ROI metrics
        
        Args:
            design: Complete design with lots, roads, utilities
            
        Returns:
            Financial metrics dict
        """
        # Calculate costs
        cost_breakdown = self.calculate_construction_cost(design)
        total_cost = cost_breakdown['total_construction_cost']
        
        # Calculate revenue
        lots = design.get('lots', [])
        revenue_data = self.calculate_revenue(lots)
        total_revenue = revenue_data['total_revenue']
        
        # Calculate profit
        gross_profit = total_revenue - total_cost
        
        # ROI percentage
        roi_percentage = (gross_profit / total_cost * 100) if total_cost > 0 else 0
        
        # Profit margin
        profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Return metrics
        return {
            'total_cost': total_cost,
            'total_revenue': total_revenue,
            'gross_profit': gross_profit,
            'roi_percentage': roi_percentage,
            'profit_margin': profit_margin,
            'cost_breakdown': cost_breakdown,
            'revenue_breakdown': revenue_data,
            'cost_per_lot': total_cost / len(lots) if lots else 0,
            'revenue_per_lot': total_revenue / len(lots) if lots else 0,
            'profit_per_lot': gross_profit / len(lots) if lots else 0
        }


class MultiObjectiveFinancialOptimizer:
    """
    Optimize layout using multi-objective GA with financial objectives
    """
    
    def __init__(self, financial_model: FinancialModel = None):
        self.financial_model = financial_model or FinancialModel()
    
    def evaluate_financial_fitness(
        self,
        design: Dict[str, Any]
    ) -> tuple:
        """
        Evaluate design on multiple financial objectives
        
        Returns:
            (roi, quality_score, cost_efficiency, revenue)
        """
        # Calculate ROI metrics
        metrics = self.financial_model.calculate_roi_metrics(design)
        
        # Calculate average quality score
        lots = design.get('lots', [])
        if lots:
            avg_quality = np.mean([
                lot.get('quality_score', 70) for lot in lots
            ])
        else:
            avg_quality = 0
        
        # Cost efficiency (revenue per unit cost)
        cost_efficiency = (
            metrics['total_revenue'] / metrics['total_cost']
            if metrics['total_cost'] > 0 else 0
        )
        
        # Return tuple for NSGA-II
        return (
            metrics['roi_percentage'],      # Maximize ROI
            avg_quality,                    # Maximize quality
            cost_efficiency,                # Maximize efficiency
            metrics['total_revenue']        # Maximize revenue
        )
