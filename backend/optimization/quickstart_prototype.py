import numpy as np
from shapely.geometry import Polygon, box
from shapely import constrained_delaunay_triangles
# import skgeom as sg  # Commented out for minimal prototype to avoid complex dependency
import networkx as nx
from dataclasses import dataclass
from typing import List, Tuple
import matplotlib.pyplot as plt

# ====================
# DATA STRUCTURES
# ====================

@dataclass
class Building:
    width: float
    height: float
    area: float
    type: str
    id: int

@dataclass
class LayoutResult:
    roads: list
    blocks: list
    buildings: list
    road_graph: nx.Graph
    efficiency: float

# ====================
# PHASE 1: SKELETON
# ====================

def generate_skeleton_simple(site_polygon: Polygon, 
                            buffer_distance: float = 20.0) -> dict:
    """
    Simplified skeleton using buffer method.
    Good enough for rectangular/circular sites.
    """
    blocks = []
    current_poly = site_polygon
    level = 0
    
    while current_poly.area > 100:  # Minimum area threshold
        buffered = current_poly.buffer(-buffer_distance)
        
        if buffered.is_empty or not buffered.is_valid:
            break
        
        blocks.append({
            'polygon': buffered,
            'level': level,
            'area': buffered.area
        })
        
        current_poly = buffered
        level += 1
    
    # Create simple road graph (perimeter)
    # This is a placeholder; real road graph would need actual skeleton edges
    G = nx.Graph()
    coords = list(site_polygon.exterior.coords)
    for i in range(len(coords)-1):
        G.add_edge(i, i+1, length=np.hypot(
            coords[i+1][0]-coords[i][0],
            coords[i+1][1]-coords[i][1]
        ))
    
    return {
        'blocks': blocks,
        'road_graph': G
    }

# ====================
# PHASE 2: ZONING (SIMPLIFIED)
# ====================

def simple_grid_zones(block_polygon: Polygon, 
                     grid_size: float = 50.0) -> List[Polygon]:
    """
    Divide block into grid cells for simplicity.
    """
    minx, miny, maxx, maxy = block_polygon.bounds
    
    zones = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + grid_size, y + grid_size)
            
            # Only keep cells mostly inside block
            intersection = cell.intersection(block_polygon)
            if intersection.area > cell.area * 0.7:
                zones.append(intersection)
            
            y += grid_size
        x += grid_size
    
    return zones

# ====================
# PHASE 3: PACKING (GREEDY)
# ====================

def pack_buildings_greedy(zone_polygon: Polygon, 
                         buildings: List[Building]) -> List[Tuple]:
    """
    Greedy first-fit packing.
    Not optimal but guaranteed valid.
    """
    placements = []
    minx, miny, maxx, maxy = zone_polygon.bounds
    
    # Sort by area (descending)
    buildings_sorted = sorted(buildings, key=lambda b: b.area, reverse=True)
    
    # Grid search for each building
    grid_step = 5.0
    
    for building in buildings_sorted:
        placed = False
        
        for x in np.arange(minx, maxx - building.width, grid_step):
            for y in np.arange(miny, maxy - building.height, grid_step):
                building_rect = box(x, y, 
                                   x + building.width, 
                                   y + building.height)
                
                # Check if valid
                if not zone_polygon.contains(building_rect):
                    continue
                
                # Check no overlap with existing
                overlaps = False
                for placed_b, px, py in placements:
                    placed_rect = box(px, py, 
                                     px + placed_b.width, 
                                     py + placed_b.height)
                    if building_rect.intersects(placed_rect):
                        overlaps = True
                        break
                
                if not overlaps:
                    placements.append((building, x, y))
                    placed = True
                    break
            
            if placed:
                break
    
    return placements

# ====================
# MAIN GENERATOR
# ====================

def generate_layout(site_polygon: Polygon,
                   buildings: List[Building],
                   buffer_distance: float = 20.0,
                   grid_size: float = 50.0) -> LayoutResult:
    """
    Simplified end-to-end generator.
    """
    print("Phase 1: Generating road skeleton...")
    skeleton = generate_skeleton_simple(site_polygon, buffer_distance)
    
    print(f"Phase 2: Creating {len(skeleton['blocks'])} zones...")
    all_zones = []
    for block in skeleton['blocks']:
        zones = simple_grid_zones(block['polygon'], grid_size)
        all_zones.extend(zones)
    
    print(f"Phase 3: Packing {len(buildings)} buildings...")
    all_placements = []
    for zone in all_zones:
        placements = pack_buildings_greedy(zone, buildings)
        all_placements.extend(placements)
    
    # Calculate efficiency
    total_building_area = sum(b.area for b, _, _ in all_placements)
    efficiency = total_building_area / site_polygon.area
    
    print(f"✓ Placed {len(all_placements)}/{len(buildings)} buildings")
    print(f"✓ Efficiency: {efficiency*100:.1f}%")
    
    return LayoutResult(
        roads=[],
        blocks=skeleton['blocks'],
        buildings=all_placements,
        road_graph=skeleton['road_graph'],
        efficiency=efficiency
    )

# ====================
# VISUALIZATION
# ====================

def visualize_layout(site: Polygon, result: LayoutResult):
    """
    Plot the generated layout.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Site boundary
    x, y = site.exterior.xy
    ax.plot(x, y, 'k-', linewidth=2, label='Site Boundary')
    
    # Blocks (light gray)
    for block in result.blocks:
        if hasattr(block['polygon'], 'exterior'):
            x, y = block['polygon'].exterior.xy
            ax.fill(x, y, color='lightgray', alpha=0.3)
    
    # Buildings (colored by type)
    colors = {'warehouse': 'steelblue', 'factory': 'orange', 'office': 'green'}
    
    for building, bx, by in result.buildings:
        rect = plt.Rectangle((bx, by), building.width, building.height,
                             facecolor=colors.get(building.type, 'gray'),
                             edgecolor='black',
                             alpha=0.7)
        ax.add_patch(rect)
    
    ax.set_aspect('equal')
    ax.set_title(f'Industrial Park Layout (Efficiency: {result.efficiency*100:.1f}%)')
    ax.legend()
    plt.tight_layout()
    plt.savefig('layout_output.png', dpi=150)
    print("✓ Saved visualization to layout_output.png")
    # plt.show() # Commented out to avoid blocking execution in headless env

# ====================
# EXAMPLE USAGE
# ====================

if __name__ == "__main__":
    # Define site (rectangular for simplicity)
    site = Polygon([
        (0, 0), (200, 0), (200, 150), (0, 150)
    ])
    
    # Generate buildings
    buildings = []
    np.random.seed(42) # Deterministic seed
    for i in range(30):
        buildings.append(Building(
            width=np.random.uniform(15, 25),
            height=np.random.uniform(15, 25),
            area=0,  # Will be calculated
            type=np.random.choice(['warehouse', 'factory', 'office']),
            id=i
        ))
    
    # Calculate areas
    for b in buildings:
        b.area = b.width * b.height
    
    # Generate layout
    result = generate_layout(site, buildings, 
                           buffer_distance=15.0,
                           grid_size=40.0)
    
    # Visualize
    visualize_layout(site, result)
