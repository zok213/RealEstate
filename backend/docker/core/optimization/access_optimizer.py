"""
Road Network & Access Optimizer

Tối ưu hóa hệ thống đường nội bộ và access cho industrial estate:
1. Skeleton Road Network - Đường chính hình xương
2. Internal Access Roads - Đường nội bộ kết nối lots
3. Cul-de-sac Optimization - Tối ưu đường chết
4. Frontage Maximization - Tối đa mặt tiền đường
5. Traffic Flow - Luồng giao thông hợp lý
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, LineString, Point, MultiLineString
from shapely.ops import linemerge, unary_union, split
import numpy as np
import math

logger = logging.getLogger(__name__)


class RoadNetworkDesigner:
    """
    Thiết kế hệ thống đường nội bộ tối ưu
    """
    
    def __init__(
        self,
        main_road_width: float = 12.0,
        internal_road_width: float = 8.0,
        access_road_width: float = 6.0,
        cul_de_sac_radius: float = 10.0
    ):
        """
        Args:
            main_road_width: Width of main skeleton roads
            internal_road_width: Width of internal distribution roads
            access_road_width: Width of access roads to lots
            cul_de_sac_radius: Turning radius for cul-de-sac
        """
        self.main_road_width = main_road_width
        self.internal_road_width = internal_road_width
        self.access_road_width = access_road_width
        self.cul_de_sac_radius = cul_de_sac_radius
    
    def design_skeleton_network(
        self,
        land_boundary: Polygon,
        num_branches: int = 3,
        pattern: str = 'grid'
    ) -> List[Dict[str, Any]]:
        """
        Thiết kế mạng lưới đường chính (skeleton)
        
        Args:
            land_boundary: Ranh giới đất
            num_branches: Số nhánh đường chính
            pattern: Pattern ('grid', 'radial', 'organic')
            
        Returns:
            List of road segments with LineString geometry
        """
        logger.info(f"[ROAD NETWORK] Designing skeleton with {num_branches} branches, pattern={pattern}")
        
        roads = []
        
        if pattern == 'grid':
            roads = self._create_grid_skeleton(land_boundary, num_branches)
        elif pattern == 'radial':
            roads = self._create_radial_skeleton(land_boundary, num_branches)
        else:
            roads = self._create_grid_skeleton(land_boundary, num_branches)
        
        logger.info(f"[ROAD NETWORK] Created {len(roads)} skeleton roads")
        return roads
    
    def _create_grid_skeleton(
        self,
        boundary: Polygon,
        num_branches: int
    ) -> List[Dict[str, Any]]:
        """
        Tạo skeleton dạng lưới (grid)
        
        Most common for industrial estates
        """
        bounds = boundary.bounds
        minx, miny, maxx, maxy = bounds
        
        width = maxx - minx
        height = maxy - miny
        
        roads = []
        road_id = 1
        
        # Determine orientation
        if width > height:
            # Horizontal main roads
            spacing = height / (num_branches + 1)
            
            for i in range(1, num_branches + 1):
                y = miny + i * spacing
                road_line = LineString([
                    (minx, y),
                    (maxx, y)
                ])
                
                # Clip to boundary
                clipped = road_line.intersection(boundary)
                
                if not clipped.is_empty:
                    if clipped.geom_type == 'LineString':
                        roads.append({
                            'id': road_id,
                            'geometry': clipped,
                            'type': 'main',
                            'width': self.main_road_width,
                            'length': clipped.length
                        })
                        road_id += 1
                    elif clipped.geom_type == 'MultiLineString':
                        for line in clipped.geoms:
                            roads.append({
                                'id': road_id,
                                'geometry': line,
                                'type': 'main',
                                'width': self.main_road_width,
                                'length': line.length
                            })
                            road_id += 1
            
            # Add perpendicular connectors
            num_connectors = max(2, num_branches - 1)
            conn_spacing = width / (num_connectors + 1)
            
            for i in range(1, num_connectors + 1):
                x = minx + i * conn_spacing
                connector = LineString([
                    (x, miny),
                    (x, maxy)
                ])
                
                clipped = connector.intersection(boundary)
                
                if not clipped.is_empty and clipped.geom_type == 'LineString':
                    roads.append({
                        'id': road_id,
                        'geometry': clipped,
                        'type': 'connector',
                        'width': self.internal_road_width,
                        'length': clipped.length
                    })
                    road_id += 1
        
        else:
            # Vertical main roads
            spacing = width / (num_branches + 1)
            
            for i in range(1, num_branches + 1):
                x = minx + i * spacing
                road_line = LineString([
                    (x, miny),
                    (x, maxy)
                ])
                
                clipped = road_line.intersection(boundary)
                
                if not clipped.is_empty and clipped.geom_type == 'LineString':
                    roads.append({
                        'id': road_id,
                        'geometry': clipped,
                        'type': 'main',
                        'width': self.main_road_width,
                        'length': clipped.length
                    })
                    road_id += 1
            
            # Connectors
            num_connectors = max(2, num_branches - 1)
            conn_spacing = height / (num_connectors + 1)
            
            for i in range(1, num_connectors + 1):
                y = miny + i * conn_spacing
                connector = LineString([
                    (minx, y),
                    (maxx, y)
                ])
                
                clipped = connector.intersection(boundary)
                
                if not clipped.is_empty and clipped.geom_type == 'LineString':
                    roads.append({
                        'id': road_id,
                        'geometry': clipped,
                        'type': 'connector',
                        'width': self.internal_road_width,
                        'length': clipped.length
                    })
                    road_id += 1
        
        return roads
    
    def _create_radial_skeleton(
        self,
        boundary: Polygon,
        num_branches: int
    ) -> List[Dict[str, Any]]:
        """
        Tạo skeleton dạng radial (hình tỏa tròn)
        
        Used for special layouts or roundabouts
        """
        center = boundary.centroid
        roads = []
        road_id = 1
        
        # Find max radius
        bounds = boundary.bounds
        max_radius = max(
            Point(center).distance(Point(bounds[0], bounds[1])),
            Point(center).distance(Point(bounds[2], bounds[3]))
        )
        
        # Create radial spokes
        for i in range(num_branches):
            angle = (2 * math.pi * i) / num_branches
            
            end_x = center.x + max_radius * math.cos(angle)
            end_y = center.y + max_radius * math.sin(angle)
            
            spoke = LineString([
                (center.x, center.y),
                (end_x, end_y)
            ])
            
            clipped = spoke.intersection(boundary)
            
            if not clipped.is_empty and clipped.geom_type == 'LineString':
                roads.append({
                    'id': road_id,
                    'geometry': clipped,
                    'type': 'radial',
                    'width': self.main_road_width,
                    'length': clipped.length
                })
                road_id += 1
        
        # Add circular ring road
        circle = center.buffer(max_radius * 0.5)
        ring = circle.exterior
        
        clipped = ring.intersection(boundary)
        
        if not clipped.is_empty:
            if clipped.geom_type == 'LineString':
                roads.append({
                    'id': road_id,
                    'geometry': clipped,
                    'type': 'ring',
                    'width': self.internal_road_width,
                    'length': clipped.length
                })
            elif clipped.geom_type == 'MultiLineString':
                for line in clipped.geoms:
                    roads.append({
                        'id': road_id,
                        'geometry': line,
                        'type': 'ring',
                        'width': self.internal_road_width,
                        'length': line.length
                    })
                    road_id += 1
        
        return roads
    
    def add_access_roads_to_lots(
        self,
        lots: List[Dict[str, Any]],
        skeleton_roads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Thêm đường access cho từng lot
        
        Ensures every lot has road frontage
        
        Args:
            lots: List of lot dicts with 'geometry'
            skeleton_roads: List of main road dicts
            
        Returns:
            Updated lots with 'road_frontage' info
        """
        logger.info(f"[ROAD ACCESS] Adding access roads to {len(lots)} lots")
        
        # Combine all roads into one geometry
        all_roads = []
        for road in skeleton_roads:
            all_roads.append(road['geometry'].buffer(road['width'] / 2))
        
        if not all_roads:
            logger.warning("[ROAD ACCESS] No skeleton roads provided")
            return lots
        
        road_union = unary_union(all_roads)
        
        # Check each lot for road access
        updated_lots = []
        
        for lot in lots:
            lot_geom = lot['geometry']
            
            # Find intersection with roads
            road_touch = lot_geom.intersection(road_union)
            
            if not road_touch.is_empty:
                # Calculate frontage length
                if road_touch.geom_type in ['LineString', 'MultiLineString']:
                    frontage = road_touch.length
                else:
                    # Approximation for other geometries
                    frontage = road_touch.boundary.length / 4
                
                lot_copy = lot.copy()
                lot_copy['has_access'] = True
                lot_copy['road_frontage'] = frontage
                updated_lots.append(lot_copy)
            else:
                # No direct access - needs internal road
                lot_copy = lot.copy()
                lot_copy['has_access'] = False
                lot_copy['road_frontage'] = 0.0
                lot_copy['needs_access_road'] = True
                updated_lots.append(lot_copy)
        
        # Summary
        with_access = sum(1 for lot in updated_lots if lot.get('has_access', False))
        logger.info(
            f"[ROAD ACCESS] ✓ {with_access}/{len(lots)} lots have direct road access "
            f"({with_access/len(lots)*100:.1f}%)"
        )
        
        return updated_lots
    
    def optimize_cul_de_sac(
        self,
        dead_end_lots: List[Dict[str, Any]],
        main_road: LineString
    ) -> Dict[str, Any]:
        """
        Tối ưu hóa cul-de-sac cho lots không có lối ra
        
        Args:
            dead_end_lots: Lots cần cul-de-sac
            main_road: Đường chính để kết nối
            
        Returns:
            Dict with cul-de-sac geometry and connected lots
        """
        if not dead_end_lots:
            return {'geometry': None, 'lots': []}
        
        # Find center of dead-end lots
        lot_geoms = [lot['geometry'] for lot in dead_end_lots]
        combined = unary_union(lot_geoms)
        center = combined.centroid
        
        # Find nearest point on main road
        nearest_point = main_road.interpolate(main_road.project(center))
        
        # Create cul-de-sac access road
        access = LineString([
            (nearest_point.x, nearest_point.y),
            (center.x, center.y)
        ])
        
        # Create turning circle at end
        turning_circle = center.buffer(self.cul_de_sac_radius)
        
        logger.info(
            f"[CUL-DE-SAC] Created for {len(dead_end_lots)} lots, "
            f"access length={access.length:.1f}m"
        )
        
        return {
            'geometry': turning_circle,
            'access_road': access,
            'lots': dead_end_lots,
            'radius': self.cul_de_sac_radius
        }


class FrontageOptimizer:
    """
    Tối ưu hóa mặt tiền đường cho lots
    """
    
    @staticmethod
    def calculate_lot_frontage(
        lot: Polygon,
        roads: List[LineString]
    ) -> float:
        """
        Tính chiều dài mặt tiền đường của lot
        
        Returns:
            Frontage length in meters
        """
        if not roads:
            return 0.0
        
        # Combine all roads
        road_union = unary_union([r.buffer(0.1) for r in roads])
        
        # Find lot boundary touching roads
        lot_boundary = lot.boundary
        touch = lot_boundary.intersection(road_union)
        
        if touch.is_empty:
            return 0.0
        
        if touch.geom_type == 'LineString':
            return touch.length
        elif touch.geom_type == 'MultiLineString':
            return sum(line.length for line in touch.geoms)
        else:
            return 0.0
    
    @staticmethod
    def maximize_frontage_distribution(
        lots: List[Dict[str, Any]],
        roads: List[LineString],
        target_min_frontage: float = 15.0
    ) -> List[Dict[str, Any]]:
        """
        Phân phối lại lots để maximize frontage
        
        Strategy: Prioritize lots with more frontage, merge small frontage lots
        
        Args:
            lots: Original lots
            roads: Road network
            target_min_frontage: Minimum desirable frontage
            
        Returns:
            Optimized lots with better frontage distribution
        """
        logger.info(f"[FRONTAGE OPTIMIZER] Optimizing frontage for {len(lots)} lots")
        
        # Calculate frontage for each lot
        scored_lots = []
        for lot in lots:
            frontage = FrontageOptimizer.calculate_lot_frontage(
                lot['geometry'],
                roads
            )
            
            lot_copy = lot.copy()
            lot_copy['frontage'] = frontage
            lot_copy['frontage_ratio'] = frontage / lot['geometry'].area * 100 if lot['geometry'].area > 0 else 0
            scored_lots.append(lot_copy)
        
        # Separate good vs poor frontage
        good_frontage = [l for l in scored_lots if l['frontage'] >= target_min_frontage]
        poor_frontage = [l for l in scored_lots if l['frontage'] < target_min_frontage]
        
        logger.info(
            f"[FRONTAGE OPTIMIZER] {len(good_frontage)} good, "
            f"{len(poor_frontage)} need improvement"
        )
        
        # TODO: Implement merging logic for poor frontage lots
        # For now, just flag them
        for lot in poor_frontage:
            lot['needs_frontage_improvement'] = True
        
        result = good_frontage + poor_frontage
        
        avg_frontage = np.mean([l['frontage'] for l in result]) if result else 0
        logger.info(f"[FRONTAGE OPTIMIZER] ✓ Average frontage: {avg_frontage:.1f}m")
        
        return result
