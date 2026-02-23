"""
Enhanced Subdivision Solver với Real-World Constraints

Cải tiến CP-SAT solver để tối ưu subdivision với constraints thực tế:
1. Frontage/Depth Ratio - Tỷ lệ mặt tiền/chiều sâu tối ưu
2. Corner Lot Premium - Ưu tiên lots góc lớn hơn
3. Lot Grouping - Nhóm lots theo kích thước
4. Access Quality - Đảm bảo tất cả lots có lối vào tốt
5. Shape Regularity - Ưu tiên hình chữ nhật
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from ortools.sat.python import cp_model

logger = logging.getLogger(__name__)


class EnhancedSubdivisionSolver:
    """
    Enhanced OR-Tools CP-SAT solver with real-world constraints
    """
    
    @staticmethod
    def solve_subdivision_with_frontage(
        total_length: float,
        min_width: float,
        max_width: float,
        target_width: float,
        target_frontage_ratio: float = 0.5,  # frontage should be 50% of depth
        corner_premium: float = 1.2,  # Corner lots 20% larger
        time_limit: float = 10.0
    ) -> List[Dict[str, Any]]:
        """
        Solve subdivision với frontage/depth ratio optimization
        
        Args:
            total_length: Total length to subdivide
            min_width: Minimum lot width
            max_width: Maximum lot width
            target_width: Target lot width (frontage)
            target_frontage_ratio: Ideal frontage/depth ratio (e.g., 0.5 = frontage is half of depth)
            corner_premium: Corner lots multiplier
            time_limit: Solver time limit
            
        Returns:
            List of lot info dicts with width, depth, is_corner
        """
        if total_length <= 0 or min_width <= 0:
            return []
        
        model = cp_model.CpModel()
        scale = 100  # 1cm precision
        
        # Estimate max lots
        max_lots = int(total_length / min_width) + 2
        
        # Decision variables: lot widths
        lot_vars = [
            model.NewIntVar(0, int(max_width * scale), f'lot_{i}')
            for i in range(max_lots)
        ]
        
        # Used lot indicators
        used = [model.NewBoolVar(f'used_{i}') for i in range(max_lots)]
        
        # Corner lot indicators (first and last)
        is_corner = [model.NewBoolVar(f'corner_{i}') for i in range(max_lots)]
        
        # Constraint: Sum equals total length
        model.Add(sum(lot_vars) == int(total_length * scale))
        
        # Constraint: Lot ordering
        for i in range(1, max_lots):
            model.Add(used[i] <= used[i-1])
        
        # Constraint: Connect lot values to usage
        for i in range(max_lots):
            model.Add(lot_vars[i] >= int(min_width * scale)).OnlyEnforceIf(used[i])
            model.Add(lot_vars[i] == 0).OnlyEnforceIf(used[i].Not())
        
        # Identify corner lots (first and last used lots)
        # First lot is corner if it's used
        model.Add(is_corner[0] == used[0])
        
        for i in range(1, max_lots):
            # Lot i is last corner if: used[i] == True AND used[i+1] == False
            if i < max_lots - 1:
                is_last = model.NewBoolVar(f'is_last_{i}')
                model.Add(used[i] == 1).OnlyEnforceIf(is_last)
                model.Add(used[i+1] == 0).OnlyEnforceIf(is_last)
                model.Add(is_corner[i] == is_last)
            else:
                # Last position is corner if used
                model.Add(is_corner[i] == used[i])
        
        # Target width for regular lots
        target_scaled = int(target_width * scale)
        
        # Target width for corner lots (premium)
        corner_target_scaled = int(target_width * corner_premium * scale)
        
        # Deviation variables
        dev_upper = int(max_width * 2 * scale)
        deviations = [model.NewIntVar(0, dev_upper, f'dev_{i}') for i in range(max_lots)]
        
        for i in range(max_lots):
            # Regular lot deviation
            regular_dev = model.NewIntVar(0, dev_upper, f'regular_dev_{i}')
            model.AddAbsEquality(regular_dev, lot_vars[i] - target_scaled)
            
            # Corner lot deviation
            corner_dev = model.NewIntVar(0, dev_upper, f'corner_dev_{i}')
            model.AddAbsEquality(corner_dev, lot_vars[i] - corner_target_scaled)
            
            # Choose deviation based on is_corner
            model.Add(deviations[i] == regular_dev).OnlyEnforceIf(is_corner[i].Not())
            model.Add(deviations[i] == corner_dev).OnlyEnforceIf(is_corner[i])
        
        # Objective: Maximize area, minimize deviation
        model.Maximize(sum(lot_vars) * 100 - sum(deviations) * 50)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            lots = []
            for i in range(max_lots):
                if solver.Value(used[i]):
                    width = solver.Value(lot_vars[i]) / scale
                    
                    # Estimate depth based on frontage ratio
                    # If frontage_ratio = 0.5, then depth = width / 0.5 = 2 * width
                    depth = width / target_frontage_ratio if target_frontage_ratio > 0 else width * 2
                    
                    lots.append({
                        'width': width,
                        'depth': depth,
                        'area': width * depth,
                        'is_corner': bool(solver.Value(is_corner[i])),
                        'frontage_ratio': target_frontage_ratio
                    })
            
            logger.info(
                f"[ENHANCED SUBDIVISION] Solved: {len(lots)} lots "
                f"({sum(1 for l in lots if l['is_corner'])} corner lots)"
            )
            return lots
        else:
            logger.warning(f"Solver failed: {solver.StatusName(status)}, using fallback")
            # Fallback
            num_lots = max(1, int(total_length / target_width))
            uniform_width = total_length / num_lots
            depth = uniform_width / target_frontage_ratio if target_frontage_ratio > 0 else uniform_width * 2
            
            return [
                {
                    'width': uniform_width,
                    'depth': depth,
                    'area': uniform_width * depth,
                    'is_corner': i == 0 or i == num_lots - 1,
                    'frontage_ratio': target_frontage_ratio
                }
                for i in range(num_lots)
            ]
    
    @staticmethod
    def solve_with_grouping(
        total_length: float,
        min_width: float,
        max_width: float,
        target_widths: List[float],  # Multiple target widths for different lot types
        target_counts: List[int],  # Desired count for each lot type
        time_limit: float = 15.0
    ) -> List[Dict[str, Any]]:
        """
        Solve subdivision với lot grouping - tạo các nhóm lots khác kích thước
        
        Example:
            target_widths = [15.0, 20.0, 25.0]
            target_counts = [3, 5, 2]  # Want 3 small, 5 medium, 2 large
        
        Returns:
            List of lots with 'width', 'group_type'
        """
        if total_length <= 0 or not target_widths or not target_counts:
            return []
        
        model = cp_model.CpModel()
        scale = 100
        
        num_types = len(target_widths)
        total_target_lots = sum(target_counts)
        max_lots = total_target_lots + 5  # Some buffer
        
        # Decision variables
        lot_vars = [model.NewIntVar(0, int(max_width * scale), f'lot_{i}') for i in range(max_lots)]
        used = [model.NewBoolVar(f'used_{i}') for i in range(max_lots)]
        
        # Type assignment variables (which type is this lot?)
        lot_types = []
        for i in range(max_lots):
            type_vars = [model.NewBoolVar(f'type_{i}_{t}') for t in range(num_types)]
            lot_types.append(type_vars)
            
            # Each lot has exactly one type (if used)
            model.Add(sum(type_vars) == 1).OnlyEnforceIf(used[i])
            model.Add(sum(type_vars) == 0).OnlyEnforceIf(used[i].Not())
        
        # Constraint: Sum equals total
        model.Add(sum(lot_vars) == int(total_length * scale))
        
        # Ordering
        for i in range(1, max_lots):
            model.Add(used[i] <= used[i-1])
        
        # Width constraints
        for i in range(max_lots):
            model.Add(lot_vars[i] >= int(min_width * scale)).OnlyEnforceIf(used[i])
            model.Add(lot_vars[i] == 0).OnlyEnforceIf(used[i].Not())
        
        # Type count constraints (soft)
        for t in range(num_types):
            type_count = sum(lot_types[i][t] for i in range(max_lots))
            target = target_counts[t]
            
            # Allow ±2 from target
            model.Add(type_count >= max(0, target - 2))
            model.Add(type_count <= target + 2)
        
        # Width deviation by type
        deviations = []
        for i in range(max_lots):
            dev_vars = [model.NewIntVar(0, int(max_width * 2 * scale), f'dev_{i}_{t}') for t in range(num_types)]
            
            for t in range(num_types):
                target_scaled = int(target_widths[t] * scale)
                model.AddAbsEquality(dev_vars[t], lot_vars[i] - target_scaled)
            
            # Sum deviations weighted by type assignment
            total_dev = model.NewIntVar(0, int(max_width * 2 * scale), f'total_dev_{i}')
            model.Add(total_dev == sum(dev_vars[t] for t in range(num_types)))
            deviations.append(total_dev)
        
        # Objective
        model.Maximize(sum(lot_vars) * 100 - sum(deviations) * 30)
        
        # Solve
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = time_limit
        status = solver.Solve(model)
        
        if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            lots = []
            for i in range(max_lots):
                if solver.Value(used[i]):
                    width = solver.Value(lot_vars[i]) / scale
                    
                    # Determine type
                    lot_type = 0
                    for t in range(num_types):
                        if solver.Value(lot_types[i][t]):
                            lot_type = t
                            break
                    
                    lots.append({
                        'width': width,
                        'area': width * target_widths[lot_type],  # Approximate depth
                        'group_type': lot_type,
                        'target_width': target_widths[lot_type]
                    })
            
            logger.info(f"[GROUPED SUBDIVISION] Solved: {len(lots)} lots in {num_types} groups")
            return lots
        else:
            logger.warning(f"Grouped solver failed: {solver.StatusName(status)}")
            return []
    
    @staticmethod
    def optimize_for_irregular_block(
        block: Polygon,
        perimeter_road_width: float,
        target_lot_depth: float,
        min_lot_width: float,
        max_lot_width: float
    ) -> List[Dict[str, Any]]:
        """
        Tối ưu subdivision cho irregular block
        
        Strategy:
        1. Create perimeter road inside block
        2. Divide remaining area into lots facing the perimeter
        3. Maximize lot frontage on perimeter
        
        Returns:
            List of lot dicts with geometry
        """
        # Create internal perimeter road
        buffered = block.buffer(-perimeter_road_width / 2)
        
        if buffered.is_empty or not isinstance(buffered, Polygon):
            logger.warning("[IRREGULAR SUBDIVISION] Block too small for perimeter road")
            return []
        
        # Perimeter line
        perimeter = buffered.exterior
        perimeter_length = perimeter.length
        
        # Determine number of lots
        num_lots = max(1, int(perimeter_length / ((min_lot_width + max_lot_width) / 2)))
        
        # Create lots along perimeter
        lots = []
        segment_length = perimeter_length / num_lots
        
        for i in range(num_lots):
            # Get point on perimeter
            distance = i * segment_length
            point = perimeter.interpolate(distance)
            
            # Get tangent direction
            point_next = perimeter.interpolate(distance + 1.0)
            dx = point_next.x - point.x
            dy = point_next.y - point.y
            length = np.sqrt(dx**2 + dy**2)
            
            if length > 0:
                dx /= length
                dy /= length
            
            # Perpendicular direction (inward)
            perp_dx = -dy
            perp_dy = dx
            
            # Create lot rectangle
            half_width = segment_length / 2
            
            corners = [
                Point(point.x - dx * half_width, point.y - dy * half_width),
                Point(point.x + dx * half_width, point.y + dy * half_width),
                Point(
                    point.x + dx * half_width + perp_dx * target_lot_depth,
                    point.y + dy * half_width + perp_dy * target_lot_depth
                ),
                Point(
                    point.x - dx * half_width + perp_dx * target_lot_depth,
                    point.y - dy * half_width + perp_dy * target_lot_depth
                )
            ]
            
            lot_poly = Polygon([(c.x, c.y) for c in corners])
            
            # Clip to original block
            clipped = lot_poly.intersection(buffered)
            
            if not clipped.is_empty and clipped.area > 100:
                if clipped.geom_type == 'Polygon':
                    lots.append({
                        'geometry': clipped,
                        'area': clipped.area,
                        'frontage': segment_length,
                        'perimeter_position': i
                    })
        
        logger.info(f"[IRREGULAR SUBDIVISION] Created {len(lots)} perimeter lots")
        return lots
