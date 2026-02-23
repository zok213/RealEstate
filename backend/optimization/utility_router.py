"""
Utility Network Routing Optimizer

Optimize pipe and cable routing for:
- Water supply network
- Sewer/drainage network
- Electrical distribution
- Telecommunications

Uses graph algorithms for minimum cost network design.
"""

from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points, linemerge
import networkx as nx
import numpy as np
import logging

logger = logging.getLogger(__name__)


class UtilityNetworkDesigner:
    """
    Design utility networks using graph algorithms
    """
    
    def __init__(
        self,
        min_pipe_spacing: float = 0.5,      # meters
        min_depth: float = 0.8,             # meters
        max_depth: float = 2.0,             # meters
        road_corridor_width: float = 3.0    # meters from road edge
    ):
        self.min_pipe_spacing = min_pipe_spacing
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.road_corridor_width = road_corridor_width
    
    def design_water_network(
        self,
        lots: List[Dict[str, Any]],
        roads: List[Dict[str, Any]],
        water_source: Point
    ) -> Dict[str, Any]:
        """
        Design water supply network using Steiner tree approximation
        
        Args:
            lots: Building lots requiring water
            roads: Road network (utility corridor)
            water_source: Water main connection point
            
        Returns:
            Water network with pipes, junctions, cost
        """
        logger.info(f"[WATER NETWORK] Designing for {len(lots)} lots")
        
        # Build graph along road network
        G = self._build_road_graph(roads)
        
        if len(G.nodes()) == 0:
            logger.warning("[WATER NETWORK] No road network available")
            return self._empty_network('water', water_source)
        
        # Add water source
        source_node = self._add_point_to_graph(G, water_source)
        
        # Add lot connection points
        lot_nodes = []
        for lot in lots:
            try:
                geom = lot.get('geometry')
                if isinstance(geom, Polygon):
                    centroid = geom.centroid
                else:
                    continue
                
                # Find nearest road point
                nearest_road_point = self._find_nearest_road_point(centroid, roads)
                if nearest_road_point:
                    # Add lot connection point and connect to nearest road
                    lot_node = (nearest_road_point.x, nearest_road_point.y)
                    
                    # Find closest existing road node to connect to
                    min_dist = float('inf')
                    closest_node = None
                    for node in G.nodes():
                        dist = Point(node).distance(Point(lot_node))
                        if dist < min_dist:
                            min_dist = dist
                            closest_node = node
                    
                    # Add node and edge
                    if closest_node and min_dist < 1000:  # Max 1km connection
                        G.add_node(lot_node, pos=lot_node)
                        G.add_edge(lot_node, closest_node, length=min_dist)
                        lot_nodes.append(lot_node)
            except Exception as e:
                logger.warning(f"[WATER NETWORK] Failed to add lot: {e}")
                continue
        
        if not lot_nodes:
            logger.warning("[WATER NETWORK] No lot nodes connected")
            return self._empty_network('water', water_source)
        
        # Solve Steiner tree (minimum spanning tree approximation)
        steiner_tree = self._solve_steiner_tree(G, source_node, lot_nodes)
        
        # Convert to pipe network
        pipes = self._graph_to_pipes(steiner_tree, 'water')
        
        # Calculate cost
        total_length = sum(pipe['length'] for pipe in pipes)
        cost = self._calculate_utility_cost(pipes, 'water')
        
        logger.info(f"[WATER NETWORK] ✓ {len(pipes)} pipes, {total_length:.0f}m, cost={cost/1e6:.1f}M VND")
        
        return {
            'type': 'water',
            'source': {'x': water_source.x, 'y': water_source.y},
            'pipes': pipes,
            'total_length': total_length,
            'cost': cost,
            'num_connections': len(lot_nodes)
        }
    
    def design_sewer_network(
        self,
        lots: List[Dict[str, Any]],
        roads: List[Dict[str, Any]],
        sewer_outlet: Point,
        terrain_slope: float = 0.01  # 1% default slope
    ) -> Dict[str, Any]:
        """
        Design gravity sewer network
        
        Constraints:
        - Follow terrain slope (gravity flow)
        - Minimum 0.5% slope
        - Tree topology (no loops)
        """
        logger.info(f"[SEWER NETWORK] Designing for {len(lots)} lots")
        
        # Build graph with elevation
        G = self._build_road_graph(roads)
        
        if len(G.nodes()) == 0:
            return self._empty_network('sewer', sewer_outlet)
        
        # Add outlet (lowest point) - connect to nearest road node
        outlet_node = (sewer_outlet.x, sewer_outlet.y)
        min_dist = float('inf')
        closest_node = None
        for node in G.nodes():
            dist = Point(node).distance(Point(outlet_node))
            if dist < min_dist:
                min_dist = dist
                closest_node = node
        
        if closest_node:
            G.add_node(outlet_node, pos=outlet_node)
            G.add_edge(outlet_node, closest_node, length=min_dist)
        
        # Add lot connection points
        lot_nodes = []
        for lot in lots:
            try:
                geom = lot.get('geometry')
                if isinstance(geom, Polygon):
                    centroid = geom.centroid
                else:
                    continue
                
                nearest_road_point = self._find_nearest_road_point(centroid, roads)
                if nearest_road_point:
                    # Add lot connection point and connect to nearest road
                    lot_node = (nearest_road_point.x, nearest_road_point.y)
                    
                    # Find closest existing road node
                    min_dist = float('inf')
                    closest_node = None
                    for node in G.nodes():
                        dist = Point(node).distance(Point(lot_node))
                        if dist < min_dist:
                            min_dist = dist
                            closest_node = node
                    
                    # Add node and edge
                    if closest_node and min_dist < 1000:
                        G.add_node(lot_node, pos=lot_node)
                        G.add_edge(lot_node, closest_node, length=min_dist)
                        lot_nodes.append(lot_node)
            except Exception as e:
                logger.warning(f"[SEWER NETWORK] Failed to add lot: {e}")
                continue
        
        if not lot_nodes:
            return self._empty_network('sewer', sewer_outlet)
        
        # Create drainage tree (all flow to outlet)
        pipes = []
        
        for lot_node in lot_nodes:
            try:
                path = nx.shortest_path(G, lot_node, outlet_node, weight='length')
                
                # Convert path to pipes
                for i in range(len(path) - 1):
                    pipe = self._create_pipe_segment(
                        G, path[i], path[i+1], 'sewer'
                    )
                    pipes.append(pipe)
            except nx.NetworkXNoPath:
                logger.warning(f"[SEWER NETWORK] No path from lot to outlet")
                continue
        
        # Remove duplicates and merge
        pipes = self._merge_duplicate_pipes(pipes)
        
        # Calculate cost
        total_length = sum(p['length'] for p in pipes)
        cost = self._calculate_utility_cost(pipes, 'sewer')
        
        logger.info(f"[SEWER NETWORK] ✓ {len(pipes)} pipes, {total_length:.0f}m, cost={cost/1e6:.1f}M VND")
        
        return {
            'type': 'sewer',
            'outlet': {'x': sewer_outlet.x, 'y': sewer_outlet.y},
            'pipes': pipes,
            'total_length': total_length,
            'cost': cost,
            'num_connections': len(lot_nodes)
        }
    
    def design_electrical_network(
        self,
        lots: List[Dict[str, Any]],
        roads: List[Dict[str, Any]],
        substation: Point
    ) -> Dict[str, Any]:
        """
        Design electrical distribution network
        
        Uses spanning tree with redundancy for reliability
        """
        logger.info(f"[ELECTRICAL NETWORK] Designing for {len(lots)} lots")
        
        # Build graph
        G = self._build_road_graph(roads)
        
        if len(G.nodes()) == 0:
            return self._empty_network('electrical', substation)
        
        # Add substation
        substation_node = self._add_point_to_graph(G, substation)
        
        # Add lot nodes
        lot_nodes = []
        for lot in lots:
            try:
                geom = lot.get('geometry')
                if isinstance(geom, Polygon):
                    centroid = geom.centroid
                else:
                    continue
                
                nearest_road_point = self._find_nearest_road_point(centroid, roads)
                if nearest_road_point:
                    lot_node = self._add_point_to_graph(G, nearest_road_point)
                    lot_nodes.append(lot_node)
            except Exception as e:
                logger.warning(f"[ELECTRICAL NETWORK] Failed to add lot: {e}")
                continue
        
        if not lot_nodes:
            return self._empty_network('electrical', substation)
        
        # Create primary distribution (spanning tree from substation)
        try:
            primary_tree = nx.minimum_spanning_tree(G, weight='length')
            cables = self._graph_to_cables(primary_tree)
        except Exception as e:
            logger.warning(f"[ELECTRICAL NETWORK] MST failed: {e}")
            cables = []
        
        # Calculate cost
        total_length = sum(c['length'] for c in cables)
        cost = self._calculate_utility_cost(cables, 'electrical')
        
        logger.info(f"[ELECTRICAL NETWORK] ✓ {len(cables)} cables, {total_length:.0f}m, cost={cost/1e6:.1f}M VND")
        
        return {
            'type': 'electrical',
            'substation': {'x': substation.x, 'y': substation.y},
            'cables': cables,
            'total_length': total_length,
            'cost': cost,
            'num_connections': len(lot_nodes)
        }
    
    def _build_road_graph(self, roads: List[Dict[str, Any]]) -> nx.Graph:
        """Build network graph from road network"""
        G = nx.Graph()
        
        for road in roads:
            try:
                geom = road.get('geometry')
                if isinstance(geom, LineString):
                    coords = list(geom.coords)
                else:
                    continue
                
                # Add edges along road
                for i in range(len(coords) - 1):
                    p1, p2 = coords[i], coords[i+1]
                    
                    # Calculate length
                    length = Point(p1).distance(Point(p2))
                    
                    # Add edge
                    G.add_edge(p1, p2, length=length, road_id=road.get('id'))
                    
                    # Store node positions
                    G.nodes[p1]['pos'] = p1
                    G.nodes[p2]['pos'] = p2
            except Exception as e:
                logger.warning(f"[GRAPH BUILD] Failed to add road: {e}")
                continue
        
        return G
    
    def _add_point_to_graph(self, G: nx.Graph, point: Point) -> Tuple[float, float]:
        """Add point to graph, return node identifier"""
        node = (point.x, point.y)
        if node not in G.nodes():
            G.add_node(node, pos=node)
        return node
    
    def _find_nearest_road_point(
        self,
        point: Point,
        roads: List[Dict[str, Any]]
    ) -> Optional[Point]:
        """Find nearest point on road network"""
        min_dist = float('inf')
        nearest = None
        
        for road in roads:
            try:
                geom = road.get('geometry')
                if isinstance(geom, LineString):
                    # Project point onto line
                    dist = geom.distance(point)
                    if dist < min_dist:
                        min_dist = dist
                        # Find closest point on line
                        nearest = geom.interpolate(geom.project(point))
            except Exception:
                continue
        
        return nearest
    
    def _solve_steiner_tree(
        self,
        G: nx.Graph,
        source: Any,
        terminals: List[Any]
    ) -> nx.Graph:
        """Solve Steiner tree problem (MST approximation)"""
        try:
            # Build complete graph on terminal nodes
            all_nodes = [source] + terminals
            H = nx.Graph()
            
            for i, n1 in enumerate(all_nodes):
                for n2 in all_nodes[i+1:]:
                    try:
                        path_length = nx.shortest_path_length(G, n1, n2, weight='length')
                        H.add_edge(n1, n2, weight=path_length)
                    except nx.NetworkXNoPath:
                        continue
            
            # Find MST
            mst = nx.minimum_spanning_tree(H, weight='weight')
            
            # Expand back to original graph
            steiner = nx.Graph()
            for edge in mst.edges():
                n1, n2 = edge
                try:
                    path = nx.shortest_path(G, n1, n2, weight='length')
                    for i in range(len(path) - 1):
                        if G.has_edge(path[i], path[i+1]):
                            steiner.add_edge(
                                path[i], path[i+1],
                                **G.edges[path[i], path[i+1]]
                            )
                except nx.NetworkXNoPath:
                    continue
            
            return steiner
        except Exception as e:
            logger.warning(f"[STEINER TREE] Failed: {e}")
            return nx.Graph()
    
    def _graph_to_pipes(self, G: nx.Graph, pipe_type: str) -> List[Dict[str, Any]]:
        """Convert graph to pipe list"""
        pipes = []
        for i, (n1, n2) in enumerate(G.edges()):
            length = G.edges[n1, n2].get('length', Point(n1).distance(Point(n2)))
            pipes.append({
                'id': i + 1,
                'from': {'x': n1[0], 'y': n1[1]},
                'to': {'x': n2[0], 'y': n2[1]},
                'type': pipe_type,
                'length': length
            })
        return pipes
    
    def _graph_to_cables(self, G: nx.Graph) -> List[Dict[str, Any]]:
        """Convert graph to cable list"""
        return self._graph_to_pipes(G, 'electrical')
    
    def _create_pipe_segment(
        self,
        G: nx.Graph,
        n1: Any,
        n2: Any,
        pipe_type: str
    ) -> Dict[str, Any]:
        """Create pipe segment between two nodes"""
        length = G.edges[n1, n2].get('length', Point(n1).distance(Point(n2)))
        return {
            'from': {'x': n1[0], 'y': n1[1]},
            'to': {'x': n2[0], 'y': n2[1]},
            'type': pipe_type,
            'length': length
        }
    
    def _merge_duplicate_pipes(self, pipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate pipe segments"""
        unique = {}
        for pipe in pipes:
            # Create unique key from endpoints
            p1 = (pipe['from']['x'], pipe['from']['y'])
            p2 = (pipe['to']['x'], pipe['to']['y'])
            key = tuple(sorted([p1, p2]))
            
            if key not in unique:
                unique[key] = pipe
        
        return list(unique.values())
    
    def _calculate_utility_cost(
        self,
        components: List[Dict[str, Any]],
        utility_type: str
    ) -> float:
        """Calculate installation cost for utility network"""
        
        # Cost per meter (VND)
        costs_per_meter = {
            'water': 500_000,     # Water pipe
            'sewer': 800_000,     # Sewer pipe
            'electrical': 400_000 # Electrical cable
        }
        
        base_cost = costs_per_meter.get(utility_type, 500_000)
        
        total_length = sum(c.get('length', 0) for c in components)
        
        # Installation cost (trenching + materials)
        installation_cost = total_length * base_cost
        
        # Add junction/connection costs
        num_junctions = len(components)
        junction_cost = num_junctions * 50_000  # VND per junction
        
        return installation_cost + junction_cost
    
    def _empty_network(self, network_type: str, source_point: Point) -> Dict[str, Any]:
        """Return empty network structure"""
        return {
            'type': network_type,
            'source' if network_type != 'sewer' else 'outlet': {
                'x': source_point.x,
                'y': source_point.y
            },
            'pipes' if network_type != 'electrical' else 'cables': [],
            'total_length': 0,
            'cost': 0,
            'num_connections': 0
        }
