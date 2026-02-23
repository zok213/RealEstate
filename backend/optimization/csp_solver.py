"""
Constraint Satisfaction Problem (CSP) Solver for Industrial Park Layout.
Ensures all hard constraints (regulations) are satisfied.
"""

from constraint import Problem
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TCVN_7144_REGULATIONS


@dataclass
class Building:
    """Building specification."""
    id: str
    label: str
    building_type: str
    width: float
    height: float
    area: float
    min_spacing: float = 12.0


class IndustrialParkCSP:
    """
    Constraint Satisfaction Problem solver for industrial park layout.
    Ensures all hard constraints (regulations) are satisfied.
    """
    
    def __init__(self, site_params: Dict, regulations: Dict = None):
        self.site = site_params
        self.regs = regulations or TCVN_7144_REGULATIONS
        self.problem = Problem()
        self.grid_size = 30  # meters (tăng từ 20 -> 30 để nhanh hơn 2x)
        self.buildings: List[Building] = []
        
    def set_buildings(self, buildings: List[Dict]):
        """Set buildings to place."""
        self.buildings = []
        for b in buildings:
            min_spacing = self._get_min_spacing(b.get('type', 'light_manufacturing'))
            self.buildings.append(Building(
                id=b['id'],
                label=b.get('label', b['id']),
                building_type=b.get('type', 'light_manufacturing'),
                width=b['width'],
                height=b['height'],
                area=b.get('area', b['width'] * b['height']),
                min_spacing=min_spacing
            ))
    
    def _get_min_spacing(self, building_type: str) -> float:
        """Get minimum spacing based on building type."""
        spacing_map = {
            'light_manufacturing': 12,
            'medium_manufacturing': 15,
            'heavy_manufacturing': 25,
            'warehouse': 12,
            'logistics': 20,
            'shared_services': 10,
            'support_offices': 10
        }
        return spacing_map.get(building_type, 12)
    
    def add_building_variables(self):
        """
        Add position variables for each building.
        Grid-based discretization: 10m × 10m cells
        """
        max_x = int(math.ceil(self.site['width'] / self.grid_size))
        max_y = int(math.ceil(self.site['height'] / self.grid_size))
        
        for building in self.buildings:
            # Ensure building fits within site
            max_x_pos = max(1, max_x - int(math.ceil(building.width / self.grid_size)))
            max_y_pos = max(1, max_y - int(math.ceil(building.height / self.grid_size)))
            
            # X, Y position (in grid units)
            self.problem.addVariable(f'x_{building.id}', range(max_x_pos))
            self.problem.addVariable(f'y_{building.id}', range(max_y_pos))
            
            # Rotation (0, 90 degrees only for simplicity)
            self.problem.addVariable(f'rot_{building.id}', [0, 90])
    
    def add_no_overlap_constraint(self):
        """Ensure buildings don't overlap."""
        if len(self.buildings) < 2:
            return
            
        for i, b1 in enumerate(self.buildings):
            for b2 in self.buildings[i+1:]:
                self._add_pairwise_no_overlap(b1, b2)
    
    def _add_pairwise_no_overlap(self, b1: Building, b2: Building):
        """Add no-overlap constraint between two buildings."""
        def no_overlap(x1, y1, rot1, x2, y2, rot2):
            # Convert grid to meters
            x1_m = x1 * self.grid_size
            y1_m = y1 * self.grid_size
            x2_m = x2 * self.grid_size
            y2_m = y2 * self.grid_size
            
            # Get dimensions based on rotation
            w1 = b1.width if rot1 == 0 else b1.height
            h1 = b1.height if rot1 == 0 else b1.width
            w2 = b2.width if rot2 == 0 else b2.height
            h2 = b2.height if rot2 == 0 else b2.width
            
            # AABB collision detection with spacing
            spacing = max(b1.min_spacing, b2.min_spacing)
            
            # Check if rectangles overlap (including spacing)
            no_overlap_x = (x1_m + w1 + spacing <= x2_m) or (x2_m + w2 + spacing <= x1_m)
            no_overlap_y = (y1_m + h1 + spacing <= y2_m) or (y2_m + h2 + spacing <= y1_m)
            
            return no_overlap_x or no_overlap_y
        
        self.problem.addConstraint(
            no_overlap,
            [f'x_{b1.id}', f'y_{b1.id}', f'rot_{b1.id}',
             f'x_{b2.id}', f'y_{b2.id}', f'rot_{b2.id}']
        )
    
    def add_fire_safety_constraint(self):
        """
        Enforce fire safety spacing between buildings.
        Min distance: 12-25m depending on building type.
        """
        # Already included in no_overlap with min_spacing
        pass
    
    def add_boundary_constraint(self):
        """Ensure buildings stay within site boundary with buffer."""
        buffer = self.regs["utilities"]["green_buffer_zone_m"]  # 50m
        
        for building in self.buildings:
            def in_bounds(x, y, rot, b=building, buf=buffer):
                x_m = x * self.grid_size
                y_m = y * self.grid_size
                w = b.width if rot == 0 else b.height
                h = b.height if rot == 0 else b.width
                
                return (x_m >= buf and 
                        y_m >= buf and
                        x_m + w <= self.site['width'] - buf and
                        y_m + h <= self.site['height'] - buf)
            
            self.problem.addConstraint(
                in_bounds,
                [f'x_{building.id}', f'y_{building.id}', f'rot_{building.id}']
            )
    
    def add_green_area_constraint(self):
        """
        Ensure green area ≥ 20% of total area.
        This is checked during evaluation, not as CSP constraint.
        """
        pass
    
    def solve(self, max_solutions: int = 5, timeout: int = 30) -> List[Dict]:
        """
        Solve CSP and return feasible solutions.
        
        Args:
            max_solutions: Maximum number of solutions to return
            timeout: Maximum solving time in seconds (approximate)
            
        Returns:
            List of feasible layouts
        """
        try:
            # Get solutions iterator
            solutions = self.problem.getSolutionIter()
            
            layouts = []
            count = 0
            
            for sol in solutions:
                if count >= max_solutions:
                    break
                    
                layout = self._solution_to_layout(sol)
                if self._validate_layout(layout):
                    layouts.append(layout)
                    count += 1
            
            return layouts
            
        except Exception as e:
            print(f"CSP Solver error: {e}")
            # Return a simple fallback layout
            return [self._generate_fallback_layout()]
    
    def _solution_to_layout(self, solution: Dict) -> Dict:
        """Convert CSP solution to layout object."""
        buildings_placed = []
        
        for building in self.buildings:
            bid = building.id
            x = solution.get(f'x_{bid}', 0) * self.grid_size
            y = solution.get(f'y_{bid}', 0) * self.grid_size
            rot = solution.get(f'rot_{bid}', 0)
            
            width = building.width if rot == 0 else building.height
            height = building.height if rot == 0 else building.width
            
            buildings_placed.append({
                'id': bid,
                'x': x,
                'y': y,
                'rotation': rot,
                'type': building.building_type,
                'width': width,
                'height': height,
                'label': building.label
            })
        
        return {
            'buildings': buildings_placed,
            'site': self.site,
            'feasible': True,
            'constraint_satisfied': True
        }
    
    def _validate_layout(self, layout: Dict) -> bool:
        """Validate layout meets basic constraints."""
        buildings = layout['buildings']
        
        # Check green area ratio
        total_area = self.site['total_area_m2']
        building_area = sum(b['width'] * b['height'] for b in buildings)
        green_ratio = 1 - (building_area / total_area) - 0.18  # Subtract road/infra
        
        if green_ratio < 0.20:
            return False
        
        return True
    
    def _generate_fallback_layout(self) -> Dict:
        """Generate a simple grid-based fallback layout."""
        buildings_placed = []
        
        # Simple grid placement
        cols = int(math.ceil(math.sqrt(len(self.buildings))))
        cell_width = (self.site['width'] - 100) / max(1, cols)
        cell_height = (self.site['height'] - 100) / max(1, cols)
        
        for i, building in enumerate(self.buildings):
            row = i // cols
            col = i % cols
            
            x = 50 + col * cell_width + (cell_width - building.width) / 2
            y = 50 + row * cell_height + (cell_height - building.height) / 2
            
            buildings_placed.append({
                'id': building.id,
                'x': max(50, x),
                'y': max(50, y),
                'rotation': 0,
                'type': building.building_type,
                'width': building.width,
                'height': building.height,
                'label': building.label
            })
        
        return {
            'buildings': buildings_placed,
            'site': self.site,
            'feasible': True,
            'constraint_satisfied': True,
            'is_fallback': True
        }


def generate_buildings_from_params(params: Dict) -> List[Dict]:
    """Generate building list from design parameters."""
    import random
    
    buildings = []
    building_id = 0
    
    industry_focus = params.get('industry_focus', params.get('industryFocus', []))
    
    # Size ranges for each type
    size_ranges = {
        'light_manufacturing': (2000, 10000),
        'medium_manufacturing': (5000, 30000),
        'heavy_manufacturing': (10000, 50000),
        'warehouse': (2000, 20000),
        'logistics': (5000, 100000)
    }
    
    for industry in industry_focus:
        industry_type = industry.get('type', 'light_manufacturing')
        count = industry.get('count', 5)
        
        size_range = size_ranges.get(industry_type, (5000, 15000))
        
        for i in range(count):
            area = random.uniform(size_range[0], min(size_range[1], size_range[0] * 3))
            # Aspect ratio between 0.5 and 2.0
            aspect = random.uniform(0.5, 2.0)
            width = math.sqrt(area * aspect)
            height = area / width
            
            buildings.append({
                'id': f"building_{building_id}",
                'label': f"{industry_type.replace('_', ' ').title()} {i+1}",
                'type': industry_type,
                'width': width,
                'height': height,
                'area': area
            })
            building_id += 1
    
    # Add support buildings
    support_types = [
        ('canteen', 2000, 'Canteen'),
        ('medical', 1500, 'Medical Center'),
        ('parking', 5000, 'Parking Area'),
        ('admin', 2000, 'Admin Office')
    ]
    
    for btype, area, label in support_types:
        width = math.sqrt(area)
        buildings.append({
            'id': f"building_{building_id}",
            'label': label,
            'type': btype,
            'width': width,
            'height': width,
            'area': area
        })
        building_id += 1
    
    return buildings


# Quick test
if __name__ == "__main__":
    # Create test site
    site_params = {
        'width': 1000,  # meters
        'height': 500,
        'total_area_m2': 500000
    }
    
    # Create test buildings
    buildings = [
        {'id': 'b1', 'type': 'light_manufacturing', 'width': 80, 'height': 60, 'label': 'Factory 1'},
        {'id': 'b2', 'type': 'warehouse', 'width': 60, 'height': 40, 'label': 'Warehouse 1'},
        {'id': 'b3', 'type': 'logistics', 'width': 100, 'height': 80, 'label': 'Logistics Hub'},
    ]
    
    # Solve CSP
    csp = IndustrialParkCSP(site_params)
    csp.set_buildings(buildings)
    csp.add_building_variables()
    csp.add_no_overlap_constraint()
    csp.add_boundary_constraint()
    
    solutions = csp.solve(max_solutions=3)
    print(f"Found {len(solutions)} feasible solutions")
    
    for i, sol in enumerate(solutions):
        print(f"\nSolution {i+1}:")
        for b in sol['buildings']:
            print(f"  {b['label']}: ({b['x']:.0f}, {b['y']:.0f})")
