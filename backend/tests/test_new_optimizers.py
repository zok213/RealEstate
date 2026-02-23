"""
Comprehensive Tests for New Optimization Modules

Test coverage for:
- Financial Optimizer
- Utility Router
- Terrain Analyzer
"""

import pytest
import numpy as np
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shapely.geometry import Polygon, LineString, Point, box

# Import modules to test
from optimization.financial_optimizer import (
    FinancialModel,
    CostParameters,
    RevenueParameters,
    MultiObjectiveFinancialOptimizer
)
from optimization.utility_router import UtilityNetworkDesigner
from optimization.terrain_analyzer import (
    TerrainAnalyzer,
    GradingOptimizer,
    create_synthetic_terrain
)


# ============================================================================
# FINANCIAL OPTIMIZER TESTS
# ============================================================================

class TestFinancialOptimizer:
    """Test financial optimization module"""
    
    def test_construction_cost_calculation(self):
        """Test cost calculation accuracy"""
        
        design = {
            'total_area': 100000,  # 10 hectares
            'roads': [
                {'type': 'main', 'length': 500},
                {'type': 'internal', 'length': 1200}
            ],
            'lots': [{'id': i, 'geometry': box(0, 0, 50, 50)} for i in range(50)],
            'green_space_area': 15000
        }
        
        model = FinancialModel()
        costs = model.calculate_construction_cost(design)
        
        assert costs['total_construction_cost'] > 0
        assert costs['roads'] > 0
        assert costs['site_clearing'] > 0
        assert 'contingency' in costs
        assert costs['contingency'] > 0
        
        print(f"✓ Construction cost: {costs['total_construction_cost']/1e9:.2f}B VND")
    
    def test_revenue_calculation(self):
        """Test revenue projection with premiums/discounts"""
        
        lots = [
            {
                'id': 1,
                'geometry': box(0, 0, 50, 50),  # 2500m²
                'quality_score': 90,
                'is_corner': True,
                'frontage': 50,
                'zone_type': 'FACTORY'
            },
            {
                'id': 2,
                'geometry': box(100, 100, 200, 200),  # 10000m²
                'quality_score': 55,
                'is_corner': False,
                'frontage': 100,
                'zone_type': 'WAREHOUSE'
            }
        ]
        
        model = FinancialModel()
        revenue = model.calculate_revenue(lots)
        
        assert revenue['total_revenue'] > 0
        assert revenue['num_lots'] == 2
        assert len(revenue['lots']) == 2
        
        # Check premiums applied to lot 1
        lot1_breakdown = revenue['lots'][0]
        assert lot1_breakdown['adjustments']['corner_premium'] > 0
        assert lot1_breakdown['adjustments']['quality_premium'] > 0
        
        # Check discounts applied to lot 2
        lot2_breakdown = revenue['lots'][1]
        assert lot2_breakdown['adjustments']['large_lot_discount'] < 0
        assert lot2_breakdown['adjustments']['irregular_shape_discount'] < 0
        
        print(f"✓ Total revenue: {revenue['total_revenue']/1e9:.2f}B VND")
    
    def test_roi_metrics(self):
        """Test ROI calculation"""
        
        design = {
            'total_area': 50000,
            'roads': [{'type': 'internal', 'length': 800}],
            'lots': [
                {
                    'id': i,
                    'geometry': box(i*50, 0, i*50+50, 50),
                    'quality_score': 80,
                    'is_corner': i < 2,
                    'frontage': 50,
                    'zone_type': 'FACTORY'
                }
                for i in range(20)
            ],
            'green_space_area': 7500
        }
        
        model = FinancialModel()
        metrics = model.calculate_roi_metrics(design)
        
        assert 'roi_percentage' in metrics
        assert 'gross_profit' in metrics
        assert metrics['gross_profit'] == (
            metrics['total_revenue'] - metrics['total_cost']
        )
        
        print(f"✓ ROI: {metrics['roi_percentage']:.1f}%")
        print(f"✓ Profit: {metrics['gross_profit']/1e9:.2f}B VND")
        
        assert metrics['roi_percentage'] > 0  # Should be profitable
    
    def test_multi_objective_fitness(self):
        """Test multi-objective financial fitness evaluation"""
        
        design = {
            'total_area': 30000,
            'roads': [{'type': 'internal', 'length': 500}],
            'lots': [
                {'id': i, 'geometry': box(i*40, 0, i*40+40, 40), 'quality_score': 75}
                for i in range(15)
            ]
        }
        
        optimizer = MultiObjectiveFinancialOptimizer()
        roi, quality, efficiency, revenue = optimizer.evaluate_financial_fitness(design)
        
        assert roi > 0
        assert quality > 0
        assert efficiency > 0
        assert revenue > 0
        
        print(f"✓ Fitness: ROI={roi:.1f}%, Quality={quality:.1f}, Efficiency={efficiency:.2f}")


# ============================================================================
# UTILITY ROUTER TESTS
# ============================================================================

class TestUtilityRouter:
    """Test utility network routing"""
    
    def setup_method(self):
        """Setup test data"""
        # Create simple road network that covers the lots area
        self.roads = [
            {
                'id': 1,
                'geometry': LineString([(0, 0), (150, 0)]),
                'type': 'main'
            },
            {
                'id': 2,
                'geometry': LineString([(0, 0), (0, 150)]),
                'type': 'main'
            },
            {
                'id': 3,
                'geometry': LineString([(150, 0), (150, 150)]),
                'type': 'internal'
            },
            {
                'id': 4,
                'geometry': LineString([(0, 150), (150, 150)]),
                'type': 'internal'
            }
        ]
        
        # Create test lots within the road grid
        self.lots = [
            {'id': 1, 'geometry': box(20, 20, 40, 40)},
            {'id': 2, 'geometry': box(60, 20, 80, 40)},
            {'id': 3, 'geometry': box(100, 20, 120, 40)},
            {'id': 4, 'geometry': box(20, 100, 40, 120)},
            {'id': 5, 'geometry': box(100, 100, 120, 120)}
        ]
    
    def test_water_network_design(self):
        """Test water network routing"""
        
        designer = UtilityNetworkDesigner()
        water_source = Point(0, 0)
        
        network = designer.design_water_network(
            self.lots,
            self.roads,
            water_source
        )
        
        assert network['type'] == 'water'
        assert network['total_length'] > 0
        assert network['cost'] > 0
        assert len(network['pipes']) > 0
        
        print(f"✓ Water network: {len(network['pipes'])} pipes, {network['total_length']:.0f}m")
    
    def test_sewer_network_design(self):
        """Test sewer network routing"""
        
        designer = UtilityNetworkDesigner()
        sewer_outlet = Point(100, 100)
        
        network = designer.design_sewer_network(
            self.lots,
            self.roads,
            sewer_outlet
        )
        
        assert network['type'] == 'sewer'
        assert network['total_length'] > 0
        assert len(network['pipes']) > 0
        
        print(f"✓ Sewer network: {len(network['pipes'])} pipes, {network['total_length']:.0f}m")
    
    def test_electrical_network_design(self):
        """Test electrical network routing"""
        
        designer = UtilityNetworkDesigner()
        substation = Point(0, 0)
        
        network = designer.design_electrical_network(
            self.lots,
            self.roads,
            substation
        )
        
        assert network['type'] == 'electrical'
        assert network['total_length'] > 0
        assert len(network['cables']) > 0
        
        print(f"✓ Electrical network: {len(network['cables'])} cables, {network['total_length']:.0f}m")
    
    def test_utility_cost_calculation(self):
        """Test utility cost estimation"""
        
        designer = UtilityNetworkDesigner()
        water_source = Point(0, 0)
        
        network = designer.design_water_network(
            self.lots,
            self.roads,
            water_source
        )
        
        # Cost should be reasonable (500K VND/m for water)
        expected_cost = network['total_length'] * 500_000
        assert network['cost'] >= expected_cost * 0.8  # Within 20% (includes junctions)
        
        print(f"✓ Water cost: {network['cost']/1e6:.1f}M VND")


# ============================================================================
# TERRAIN ANALYZER TESTS
# ============================================================================

class TestTerrainAnalyzer:
    """Test terrain analysis and grading optimization"""
    
    def setup_method(self):
        """Setup test terrain"""
        site = box(0, 0, 200, 200)
        self.site = site
        
        # Create synthetic terrain with 2% slope
        self.elevation_points = create_synthetic_terrain(
            site,
            base_elevation=100.0,
            slope=0.02,
            roughness=0.5
        )
    
    def test_elevation_grid_creation(self):
        """Test DEM processing from point cloud"""
        
        analyzer = TerrainAnalyzer(grid_resolution=10.0)
        grid = analyzer.process_elevation_data(
            self.elevation_points,
            self.site
        )
        
        assert isinstance(grid, np.ndarray)
        assert grid.shape[0] > 0
        assert grid.shape[1] > 0
        assert not np.all(np.isnan(grid))
        
        print(f"✓ Created {grid.shape} elevation grid")
    
    def test_slope_calculation(self):
        """Test slope analysis"""
        
        analyzer = TerrainAnalyzer()
        grid = analyzer.process_elevation_data(self.elevation_points, self.site)
        slope_map = analyzer.calculate_slope_map(grid)
        
        assert isinstance(slope_map, np.ndarray)
        assert slope_map.shape == grid.shape
        assert np.max(slope_map) > 0  # Should have some slope
        
        print(f"✓ Calculated slope map, max slope: {np.max(slope_map):.1f}%")
    
    def test_buildable_area_identification(self):
        """Test buildable area detection"""
        
        analyzer = TerrainAnalyzer()
        grid = analyzer.process_elevation_data(self.elevation_points, self.site)
        slope_map = analyzer.calculate_slope_map(grid)
        buildable = analyzer.identify_buildable_areas(slope_map, max_slope=15.0)
        
        assert isinstance(buildable, np.ndarray)
        assert buildable.dtype == bool
        
        buildable_percentage = (np.sum(buildable) / buildable.size) * 100
        assert buildable_percentage > 50  # Most should be buildable
        
        print(f"✓ Buildable area: {buildable_percentage:.1f}%")
    
    def test_cut_fill_volumes(self):
        """Test earthwork volume calculation"""
        
        analyzer = TerrainAnalyzer()
        existing = analyzer.process_elevation_data(self.elevation_points, self.site)
        
        # Create proposed elevation (balanced)
        proposed = np.full_like(existing, np.nanmean(existing))
        
        volumes = analyzer.calculate_cut_fill_volumes(existing, proposed)
        
        assert 'cut' in volumes
        assert 'fill' in volumes
        assert 'net' in volumes
        assert volumes['cut'] >= 0
        assert volumes['fill'] >= 0
        
        print(f"✓ Cut: {volumes['cut']:.0f}m³, Fill: {volumes['fill']:.0f}m³")
    
    def test_grading_optimization(self):
        """Test grading cost optimization"""
        
        analyzer = TerrainAnalyzer()
        existing = analyzer.process_elevation_data(self.elevation_points, self.site)
        
        optimizer = GradingOptimizer()
        plan = optimizer.optimize_grading_plan(
            existing,
            site_area=40000  # 200x200
        )
        
        assert 'volumes' in plan
        assert 'cost_breakdown' in plan
        assert plan['cost_breakdown']['total'] > 0
        
        print(f"✓ Grading cost: {plan['cost_breakdown']['total']/1e6:.1f}M VND")


# ============================================================================
# RUN ALL TESTS
# ============================================================================

def run_all_tests():
    """Run all test suites"""
    
    print("=" * 70)
    print("RUNNING COMPREHENSIVE TESTS")
    print("=" * 70)
    
    # Financial tests
    print("\n[1/3] FINANCIAL OPTIMIZER TESTS")
    print("-" * 70)
    test_financial = TestFinancialOptimizer()
    test_financial.test_construction_cost_calculation()
    test_financial.test_revenue_calculation()
    test_financial.test_roi_metrics()
    test_financial.test_multi_objective_fitness()
    
    # Utility tests
    print("\n[2/3] UTILITY ROUTER TESTS")
    print("-" * 70)
    test_utility = TestUtilityRouter()
    test_utility.setup_method()
    test_utility.test_water_network_design()
    test_utility.test_sewer_network_design()
    test_utility.test_electrical_network_design()
    test_utility.test_utility_cost_calculation()
    
    # Terrain tests
    print("\n[3/3] TERRAIN ANALYZER TESTS")
    print("-" * 70)
    test_terrain = TestTerrainAnalyzer()
    test_terrain.setup_method()
    test_terrain.test_elevation_grid_creation()
    test_terrain.test_slope_calculation()
    test_terrain.test_buildable_area_identification()
    test_terrain.test_cut_fill_volumes()
    test_terrain.test_grading_optimization()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
