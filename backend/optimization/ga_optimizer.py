"""
Genetic Algorithm (GA) Optimizer for Industrial Park Layout.
Multi-objective optimization: road efficiency, worker flow, green ratio.
"""

from deap import base, creator, tools, algorithms
import random
import numpy as np
from typing import List, Dict, Tuple, Optional
import math

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TCVN_7144_REGULATIONS


class IndustrialParkGA:
    """
    Genetic Algorithm for industrial park layout optimization.
    Multi-objective: maximize road efficiency, flow, green ratio, etc.
    """
    
    def __init__(
        self,
        site_params: Dict,
        regulations: Dict = None,
        feasible_layouts: List[Dict] = None
    ):
        self.site = site_params
        self.regs = regulations or TCVN_7144_REGULATIONS
        self.feasible_layouts = feasible_layouts or []
        self.buildings: List[Dict] = []
        
        # GA parameters
        self.population_size = 50
        self.generations = 50
        self.mutation_rate = 0.3
        self.crossover_rate = 0.7
        
        self._initialized = False
    
    def set_buildings(self, buildings: List[Dict]):
        """Set buildings to optimize."""
        self.buildings = buildings
        self._init_deap()
    
    def _init_deap(self):
        """Initialize DEAP framework for multi-objective optimization."""
        if self._initialized:
            return
            
        # Clean up any existing creator attributes
        if hasattr(creator, "FitnessMax"):
            del creator.FitnessMax
        if hasattr(creator, "Individual"):
            del creator.Individual
        
        # Define multi-objective fitness (3 objectives)
        # weights=(1.0, 1.0, 1.0) = maximize all three
        creator.create("FitnessMax", base.Fitness, weights=(1.0, 1.0, 1.0))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        
        # Create individuals
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list,
                             self.toolbox.individual)
        
        # Genetic operators
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
        self._initialized = True
    
    def _create_individual(self) -> "creator.Individual":
        """
        Create random individual (layout).
        Chromosome: [x1, y1, rot1, x2, y2, rot2, ..., road_config]
        """
        grid_size = 10  # meters
        buffer = 50  # boundary buffer
        max_x = int((self.site['width'] - 2 * buffer) / grid_size)
        max_y = int((self.site['height'] - 2 * buffer) / grid_size)
        
        individual = creator.Individual()
        
        # Random positions for each building
        for building in self.buildings:
            # Ensure building fits
            b_width_grid = int(math.ceil(building['width'] / grid_size))
            b_height_grid = int(math.ceil(building['height'] / grid_size))
            
            individual.append(random.randint(0, max(1, max_x - b_width_grid)))  # x
            individual.append(random.randint(0, max(1, max_y - b_height_grid)))  # y
            individual.append(random.choice([0, 90]))  # rotation
        
        # Road configuration (simplified: main road position)
        individual.append(random.uniform(0.3, 0.7))  # Normalized position
        
        return individual
    
    def _evaluate_fitness(
        self,
        individual: "creator.Individual"
    ) -> Tuple[float, float, float]:
        """
        Multi-objective fitness function:
        1. Road Efficiency Score (0-10)
        2. Worker Flow Score (0-10)
        3. Green Ratio Score (0-10)
        
        Also includes constraint violation penalty.
        """
        layout = self._individual_to_layout(individual)
        
        # Objective 1: Road Efficiency
        road_efficiency = self._calculate_road_efficiency(layout)
        
        # Objective 2: Worker Flow
        worker_flow = self._calculate_worker_flow(layout)
        
        # Objective 3: Green Ratio
        green_ratio = self._calculate_green_ratio(layout)
        
        # Constraint violation penalty
        violations = self._count_constraint_violations(layout)
        penalty = violations * 3  # 3 points per violation
        
        # Apply penalty to all objectives
        road_efficiency = max(0, road_efficiency - penalty)
        worker_flow = max(0, worker_flow - penalty)
        green_ratio = max(0, green_ratio - penalty)
        
        return (road_efficiency, worker_flow, green_ratio)
    
    def _calculate_road_efficiency(self, layout: Dict) -> float:
        """
        Measure road network efficiency.
        High score = minimal total road length while connecting all buildings.
        """
        buildings = layout['buildings']
        if len(buildings) < 2:
            return 5.0
        
        # Estimate road length needed
        road_length = self._estimate_road_length(layout)
        total_area = self.site['total_area_m2']
        
        # Assume 15m average road width
        road_area = road_length * 15
        road_ratio = road_area / total_area
        
        # Best score when road_ratio = 15% (target)
        ideal_ratio = 0.15
        deviation = abs(road_ratio - ideal_ratio)
        
        score = max(0, 10 * (1 - deviation * 5))
        return min(10, score)
    
    def _calculate_worker_flow(self, layout: Dict) -> float:
        """
        Measure worker flow optimization.
        High score = short average distance between facilities.
        """
        buildings = layout['buildings']
        
        # Find amenity buildings
        amenity_types = ['canteen', 'medical', 'parking', 'admin']
        amenities = [b for b in buildings if b.get('type') in amenity_types]
        factories = [b for b in buildings if 'manufacturing' in b.get('type', '') or 
                    b.get('type') in ['warehouse', 'logistics']]
        
        if not amenities or not factories:
            return 5.0
        
        # Calculate average distance from amenities to factories
        total_distance = 0
        count = 0
        
        for amenity in amenities:
            for factory in factories:
                dist = math.sqrt(
                    (amenity['x'] - factory['x'])**2 +
                    (amenity['y'] - factory['y'])**2
                )
                total_distance += dist
                count += 1
        
        avg_distance = total_distance / max(1, count)
        
        # Score: 10 × (1 - avg_distance / max_distance)
        # Target max distance: 500m (acceptable walking)
        max_acceptable = 500
        score = max(0, 10 * (1 - avg_distance / max_acceptable))
        
        return min(10, score)
    
    def _calculate_green_ratio(self, layout: Dict) -> float:
        """
        Calculate green space ratio score.
        Score: 10 if green_ratio >= 25%, linear decrease below.
        """
        buildings = layout['buildings']
        
        # Calculate building footprint
        building_area = sum(b['width'] * b['height'] for b in buildings)
        
        total_area = self.site['total_area_m2']
        
        # Estimate road area (15% of total)
        road_area = total_area * 0.15
        
        # Infrastructure area (3% of total)
        infra_area = total_area * 0.03
        
        # Green area = total - building - road - infra
        green_area = total_area - building_area - road_area - infra_area
        green_ratio = green_area / total_area
        
        # Score based on how much green relative to target (25%)
        min_green_ratio = 0.20
        target_green_ratio = 0.25
        
        if green_ratio >= target_green_ratio:
            score = 10
        elif green_ratio >= min_green_ratio:
            score = 8 + 2 * ((green_ratio - min_green_ratio) / 
                            (target_green_ratio - min_green_ratio))
        else:
            score = 8 * (green_ratio / min_green_ratio)
        
        return min(10, max(0, score))
    
    def _estimate_road_length(self, layout: Dict) -> float:
        """Estimate total road length needed to connect all buildings."""
        buildings = layout['buildings']
        
        if len(buildings) < 2:
            return 0
        
        # Simplified: Minimum Spanning Tree approximation
        total_distance = 0
        for i, b1 in enumerate(buildings):
            min_dist = float('inf')
            for j, b2 in enumerate(buildings):
                if i != j:
                    dist = math.sqrt((b1['x'] - b2['x'])**2 + (b1['y'] - b2['y'])**2)
                    min_dist = min(min_dist, dist)
            if min_dist != float('inf'):
                total_distance += min_dist
        
        # Estimate road network = sum of nearest neighbor distances × 1.5
        return total_distance * 1.5
    
    def _count_constraint_violations(self, layout: Dict) -> int:
        """Count how many constraints are violated."""
        violations = 0
        buildings = layout['buildings']
        
        # Check 1: No overlap (with spacing)
        for i, b1 in enumerate(buildings):
            for b2 in buildings[i+1:]:
                # Check overlap
                min_spacing = 12  # meters
                
                # Simple AABB check with spacing
                if not (b1['x'] + b1['width'] + min_spacing < b2['x'] or
                        b2['x'] + b2['width'] + min_spacing < b1['x'] or
                        b1['y'] + b1['height'] + min_spacing < b2['y'] or
                        b2['y'] + b2['height'] + min_spacing < b1['y']):
                    violations += 1
        
        # Check 2: Buildings within boundary
        buffer = 50
        for b in buildings:
            if (b['x'] < buffer or 
                b['y'] < buffer or
                b['x'] + b['width'] > self.site['width'] - buffer or
                b['y'] + b['height'] > self.site['height'] - buffer):
                violations += 1
        
        # Check 3: Green area >= 20%
        green_score = self._calculate_green_ratio(layout)
        if green_score < 8:  # Corresponds to ~20%
            violations += 1
        
        return violations
    
    def _crossover(
        self,
        ind1: "creator.Individual",
        ind2: "creator.Individual"
    ) -> Tuple["creator.Individual", "creator.Individual"]:
        """Two-point crossover."""
        size = len(ind1)
        if size < 3:
            return ind1, ind2
            
        point1 = random.randint(1, size - 2)
        point2 = random.randint(point1, size - 1)
        
        # Swap segments
        temp = ind1[point1:point2]
        ind1[point1:point2] = ind2[point1:point2]
        ind2[point1:point2] = temp
        
        return ind1, ind2
    
    def _mutate(
        self,
        individual: "creator.Individual"
    ) -> Tuple["creator.Individual"]:
        """Random mutation."""
        if random.random() < self.mutation_rate and len(individual) > 1:
            idx = random.randint(0, len(individual) - 2)
            
            grid_size = 10
            buffer = 50
            max_x = int((self.site['width'] - 2 * buffer) / grid_size)
            max_y = int((self.site['height'] - 2 * buffer) / grid_size)
            
            if idx % 3 == 0:  # X coordinate
                individual[idx] = random.randint(0, max(1, max_x))
            elif idx % 3 == 1:  # Y coordinate
                individual[idx] = random.randint(0, max(1, max_y))
            else:  # Rotation
                individual[idx] = random.choice([0, 90])
        
        return (individual,)
    
    def _individual_to_layout(self, individual: "creator.Individual") -> Dict:
        """Convert GA individual to layout object."""
        buildings = []
        grid_size = 10
        buffer = 50
        
        for i, building in enumerate(self.buildings):
            idx = i * 3
            if idx + 2 >= len(individual):
                break
                
            rotation = individual[idx + 2]
            width = building['width'] if rotation == 0 else building['height']
            height = building['height'] if rotation == 0 else building['width']
            
            buildings.append({
                'id': building.get('id', f'b{i}'),
                'x': buffer + individual[idx] * grid_size,
                'y': buffer + individual[idx + 1] * grid_size,
                'rotation': rotation,
                'type': building.get('type', 'unknown'),
                'width': width,
                'height': height,
                'label': building.get('label', f'Building {i+1}')
            })
        
        return {
            'buildings': buildings,
            'road_position': individual[-1] if len(individual) > 0 else 0.5,
            'site': self.site
        }
    
    def optimize(
        self,
        population_size: int = None,
        generations: int = None
    ) -> List[Tuple[Dict, Tuple[float, float, float]]]:
        """
        Run GA optimization.
        
        Args:
            population_size: Override default population size
            generations: Override default generations
            
        Returns:
            List of (layout, fitness_scores) tuples, sorted by overall fitness
        """
        if not self.buildings:
            return []
        
        if not self._initialized:
            self._init_deap()
        
        pop_size = population_size or self.population_size
        num_gen = generations or self.generations
        
        # Create initial population
        pop = self.toolbox.population(n=pop_size)
        
        # Seed with feasible layouts if available
        for i, layout in enumerate(self.feasible_layouts[:5]):
            if i < len(pop):
                pop[i] = self._layout_to_individual(layout)
        
        # Statistics
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("max", np.max)
        
        # Run GA
        try:
            pop, logbook = algorithms.eaSimple(
                pop, self.toolbox,
                cxpb=self.crossover_rate,
                mutpb=self.mutation_rate,
                ngen=num_gen,
                stats=stats,
                verbose=False
            )
        except Exception as e:
            print(f"GA optimization error: {e}")
            # Return fallback
            return [(self._individual_to_layout(self.toolbox.individual()), (5.0, 5.0, 5.0))]
        
        # Get best solutions
        # Sort by sum of fitness values
        sorted_pop = sorted(pop, key=lambda x: sum(x.fitness.values), reverse=True)
        
        # Convert to layouts with scores
        results = []
        seen_layouts = set()
        
        for individual in sorted_pop[:10]:  # Top 10
            layout = self._individual_to_layout(individual)
            
            # Create a hash to avoid duplicates
            layout_hash = tuple((b['x'], b['y']) for b in layout['buildings'])
            if layout_hash in seen_layouts:
                continue
            seen_layouts.add(layout_hash)
            
            fitness = individual.fitness.values
            results.append((layout, fitness))
            
            if len(results) >= 5:
                break
        
        return results
    
    def _layout_to_individual(self, layout: Dict) -> "creator.Individual":
        """Convert layout back to individual for seeding."""
        individual = creator.Individual()
        grid_size = 10
        buffer = 50
        
        for building in layout.get('buildings', []):
            x_grid = int((building['x'] - buffer) / grid_size)
            y_grid = int((building['y'] - buffer) / grid_size)
            individual.append(max(0, x_grid))
            individual.append(max(0, y_grid))
            individual.append(building.get('rotation', 0))
        
        individual.append(layout.get('road_position', 0.5))
        
        return individual


# Quick test
if __name__ == "__main__":
    # Create test site
    site_params = {
        'width': 1000,
        'height': 500,
        'total_area_m2': 500000
    }
    
    # Create test buildings
    buildings = [
        {'id': 'b1', 'type': 'light_manufacturing', 'width': 80, 'height': 60, 'label': 'Factory 1'},
        {'id': 'b2', 'type': 'warehouse', 'width': 60, 'height': 40, 'label': 'Warehouse 1'},
        {'id': 'b3', 'type': 'logistics', 'width': 100, 'height': 80, 'label': 'Logistics Hub'},
        {'id': 'b4', 'type': 'canteen', 'width': 40, 'height': 30, 'label': 'Canteen'},
    ]
    
    # Run GA
    ga = IndustrialParkGA(site_params)
    ga.set_buildings(buildings)
    
    print("Running GA optimization...")
    results = ga.optimize(population_size=30, generations=20)
    
    print(f"\nFound {len(results)} optimized layouts")
    for i, (layout, scores) in enumerate(results):
        print(f"\nVariant {i+1}:")
        print(f"  Scores: Road={scores[0]:.1f}, Flow={scores[1]:.1f}, Green={scores[2]:.1f}")
        print(f"  Total: {sum(scores):.1f}")
