"""
Advanced Plot Shape Optimizer

Thuật toán tối ưu hóa hình dạng plots để:
1. Maximize usable plot area (minimize weird shapes)
2. Maximize regular rectangular plots
3. Minimize narrow/unusable plots
4. Optimize plot orientations
5. Smart merging of small/irregular plots
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, Point, LineString, MultiPolygon, box
from shapely.ops import unary_union
from shapely.affinity import rotate as rotate_geom
import numpy as np
import math

logger = logging.getLogger(__name__)


class PlotShapeMetrics:
    """Đánh giá chất lượng hình dạng plot"""
    
    @staticmethod
    def calculate_rectangularity(polygon: Polygon) -> float:
        """
        Tính độ "chữ nhật" của polygon (0-1, 1 = perfect rectangle)
        
        Sử dụng minimum rotated rectangle (OBB - Oriented Bounding Box)
        """
        if polygon.area == 0:
            return 0.0
        
        # Get minimum rotated rectangle
        mbr = polygon.minimum_rotated_rectangle
        
        # Rectangularity = actual area / MBR area
        rectangularity = polygon.area / mbr.area if mbr.area > 0 else 0.0
        
        return min(1.0, rectangularity)
    
    @staticmethod
    def calculate_aspect_ratio(polygon: Polygon) -> float:
        """
        Tính tỷ lệ chiều dài/rộng (aspect ratio)
        Ideal: 1.5 - 3.0 cho industrial plots
        """
        # Get OBB dimensions
        mbr = polygon.minimum_rotated_rectangle
        coords = list(mbr.exterior.coords[:-1])
        
        if len(coords) < 4:
            return 1.0
        
        # Calculate side lengths
        side1 = Point(coords[0]).distance(Point(coords[1]))
        side2 = Point(coords[1]).distance(Point(coords[2]))
        
        if min(side1, side2) == 0:
            return 10.0
        
        aspect = max(side1, side2) / min(side1, side2)
        return aspect
    
    @staticmethod
    def calculate_compactness(polygon: Polygon) -> float:
        """
        Tính độ compact (0-1, 1 = perfect circle/square)
        Using Polsby-Popper measure: 4π * Area / Perimeter²
        """
        if polygon.length == 0:
            return 0.0
        
        compactness = (4 * math.pi * polygon.area) / (polygon.length ** 2)
        return min(1.0, compactness)
    
    @staticmethod
    def calculate_convexity(polygon: Polygon) -> float:
        """
        Tính độ lồi (0-1, 1 = convex)
        Convexity = Area / Convex Hull Area
        """
        convex_hull = polygon.convex_hull
        if convex_hull.area == 0:
            return 0.0
        
        return polygon.area / convex_hull.area
    
    @staticmethod
    def calculate_quality_score(polygon: Polygon, target_aspect: float = 2.0) -> float:
        """
        Tổng hợp điểm chất lượng plot (0-100)
        
        Weights:
        - Rectangularity: 40%
        - Aspect ratio fitness: 30%
        - Compactness: 15%
        - Convexity: 15%
        """
        rect = PlotShapeMetrics.calculate_rectangularity(polygon)
        aspect = PlotShapeMetrics.calculate_aspect_ratio(polygon)
        compact = PlotShapeMetrics.calculate_compactness(polygon)
        convex = PlotShapeMetrics.calculate_convexity(polygon)
        
        # Aspect ratio fitness (penalize too narrow or too wide)
        aspect_fitness = 1.0 - min(1.0, abs(aspect - target_aspect) / target_aspect)
        
        # Weighted score
        score = (
            rect * 40.0 +
            aspect_fitness * 30.0 +
            compact * 15.0 +
            convex * 15.0
        )
        
        return score


class PlotOptimizer:
    """Tối ưu hóa plots thông minh"""
    
    def __init__(
        self,
        min_plot_area: float = 500.0,  # 500m² minimum
        min_plot_width: float = 15.0,  # 15m minimum width
        min_quality_score: float = 60.0,  # 60/100 minimum quality
        target_aspect_ratio: float = 2.0,  # 2:1 ideal (20m x 40m)
        merge_threshold: float = 0.8  # Merge if combined quality > 80%
    ):
        """
        Args:
            min_plot_area: Diện tích tối thiểu của plot
            min_plot_width: Chiều rộng tối thiểu
            min_quality_score: Điểm chất lượng tối thiểu
            target_aspect_ratio: Tỷ lệ chiều dài/rộng mục tiêu
            merge_threshold: Ngưỡng để merge plots
        """
        self.min_plot_area = min_plot_area
        self.min_plot_width = min_plot_width
        self.min_quality_score = min_quality_score
        self.target_aspect_ratio = target_aspect_ratio
        self.merge_threshold = merge_threshold
    
    def optimize_plots(
        self, 
        plots: List[Dict[str, Any]],
        block_boundary: Optional[Polygon] = None
    ) -> List[Dict[str, Any]]:
        """
        Tối ưu hóa danh sách plots
        
        Steps:
        1. Filter out low-quality plots
        2. Attempt to merge adjacent low-quality plots
        3. Re-square plots to be more rectangular
        4. Final quality check
        
        Args:
            plots: List of plot dicts with 'geometry' key
            block_boundary: Optional boundary for clipping
            
        Returns:
            Optimized list of plots
        """
        logger.info(f"[PLOT OPTIMIZER] Optimizing {len(plots)} plots")
        
        if not plots:
            return []
        
        # Step 1: Score all plots
        scored_plots = []
        for plot in plots:
            geom = plot['geometry']
            if not isinstance(geom, Polygon) or geom.area < self.min_plot_area:
                continue
            
            score = PlotShapeMetrics.calculate_quality_score(
                geom, 
                self.target_aspect_ratio
            )
            
            plot_copy = plot.copy()
            plot_copy['quality_score'] = score
            scored_plots.append(plot_copy)
        
        logger.info(f"[PLOT OPTIMIZER] After area filter: {len(scored_plots)} plots")
        
        # Step 2: Identify and merge low-quality plots
        optimized = self._merge_low_quality_plots(scored_plots, block_boundary)
        
        # Step 3: Try to improve plot shapes (rotate to align)
        improved = self._improve_plot_shapes(optimized)
        
        # Step 4: Final filter
        final_plots = []
        for plot in improved:
            geom = plot['geometry']
            score = PlotShapeMetrics.calculate_quality_score(
                geom,
                self.target_aspect_ratio
            )
            
            # More lenient for larger plots
            area_factor = min(1.2, geom.area / 2000.0)  # Bonus for large plots
            adjusted_threshold = self.min_quality_score * (1.0 - 0.1 * (area_factor - 1.0))
            
            if score >= adjusted_threshold:
                plot['quality_score'] = score
                final_plots.append(plot)
            else:
                logger.debug(
                    f"[PLOT OPTIMIZER] Rejected plot {plot.get('id', '?')}: "
                    f"score={score:.1f} < {adjusted_threshold:.1f}"
                )
        
        logger.info(
            f"[PLOT OPTIMIZER] ✓ Final: {len(final_plots)} high-quality plots "
            f"(rejection rate: {(1 - len(final_plots)/len(plots))*100:.1f}%)"
        )
        
        return final_plots
    
    def _merge_low_quality_plots(
        self, 
        plots: List[Dict[str, Any]], 
        boundary: Optional[Polygon]
    ) -> List[Dict[str, Any]]:
        """
        Merge adjacent low-quality plots into better plots
        """
        if len(plots) < 2:
            return plots
        
        # Separate high/low quality
        high_quality = [p for p in plots if p['quality_score'] >= self.min_quality_score]
        low_quality = [p for p in plots if p['quality_score'] < self.min_quality_score]
        
        logger.info(
            f"[PLOT OPTIMIZER] Quality split: {len(high_quality)} good, "
            f"{len(low_quality)} need improvement"
        )
        
        if not low_quality:
            return high_quality
        
        # Try to merge low-quality plots with neighbors
        merged_plots = []
        used_indices = set()
        
        for i, plot1 in enumerate(low_quality):
            if i in used_indices:
                continue
            
            geom1 = plot1['geometry']
            best_merge = None
            best_score = plot1['quality_score']
            best_idx = None
            
            # Find best merge candidate
            for j, plot2 in enumerate(low_quality[i+1:], start=i+1):
                if j in used_indices:
                    continue
                
                geom2 = plot2['geometry']
                
                # Check if adjacent (within 1m)
                if geom1.distance(geom2) > 1.0:
                    continue
                
                # Try merging
                merged = unary_union([geom1, geom2])
                
                if merged.geom_type != 'Polygon':
                    continue
                
                # Check if merge improves quality
                merged_score = PlotShapeMetrics.calculate_quality_score(
                    merged,
                    self.target_aspect_ratio
                )
                
                if merged_score > best_score and merged_score >= self.merge_threshold * 100:
                    best_merge = merged
                    best_score = merged_score
                    best_idx = j
            
            if best_merge is not None:
                # Accept merge
                merged_plots.append({
                    'geometry': best_merge,
                    'zone': plot1.get('zone', 'FACTORY'),
                    'id': f"{plot1.get('id', '')}_merged",
                    'quality_score': best_score,
                    'area': best_merge.area
                })
                used_indices.add(i)
                used_indices.add(best_idx)
                logger.debug(f"[PLOT OPTIMIZER] Merged plots: score {best_score:.1f}")
            else:
                # Cannot merge, check if salvageable
                if geom1.area >= self.min_plot_area * 1.5:  # Give some leniency
                    merged_plots.append(plot1)
                used_indices.add(i)
        
        result = high_quality + merged_plots
        logger.info(f"[PLOT OPTIMIZER] After merging: {len(result)} plots")
        
        return result
    
    def _improve_plot_shapes(
        self, 
        plots: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Improve plot shapes by straightening and simplifying
        """
        improved = []
        
        for plot in plots:
            geom = plot['geometry']
            
            # Use minimum rotated rectangle for highly irregular plots
            score = PlotShapeMetrics.calculate_quality_score(
                geom,
                self.target_aspect_ratio
            )
            
            if score < 70.0:  # Try to improve
                # Option 1: Use OBB (minimum rotated rectangle)
                obb = geom.minimum_rotated_rectangle
                
                # Check if OBB is better
                obb_score = PlotShapeMetrics.calculate_quality_score(
                    obb,
                    self.target_aspect_ratio
                )
                
                # Use OBB only if it doesn't lose too much area (>90% retained)
                area_retention = obb.area / geom.area if geom.area > 0 else 0
                
                if obb_score > score and area_retention > 0.90:
                    plot['geometry'] = obb
                    logger.debug(
                        f"[PLOT OPTIMIZER] Improved plot via OBB: "
                        f"{score:.1f} → {obb_score:.1f}"
                    )
            
            improved.append(plot)
        
        return improved


def apply_plot_optimization(
    blocks_with_lots: List[Dict[str, Any]],
    min_plot_area: float = 500.0,
    min_quality_score: float = 60.0
) -> List[Dict[str, Any]]:
    """
    Apply plot optimization to all blocks
    
    Args:
        blocks_with_lots: List of blocks, each with 'geometry' and 'lots' keys
        min_plot_area: Minimum plot area
        min_quality_score: Minimum quality score
        
    Returns:
        Blocks with optimized lots
    """
    optimizer = PlotOptimizer(
        min_plot_area=min_plot_area,
        min_quality_score=min_quality_score
    )
    
    optimized_blocks = []
    total_before = 0
    total_after = 0
    
    for block in blocks_with_lots:
        block_geom = block.get('geometry')
        lots = block.get('lots', [])
        
        total_before += len(lots)
        
        # Optimize lots in this block
        optimized_lots = optimizer.optimize_plots(lots, block_geom)
        
        total_after += len(optimized_lots)
        
        # Update block
        block_copy = block.copy()
        block_copy['lots'] = optimized_lots
        optimized_blocks.append(block_copy)
    
    logger.info(
        f"[PLOT OPTIMIZATION] Overall: {total_before} plots → {total_after} plots "
        f"({(1 - total_after/total_before)*100:.1f}% removed)"
    )
    
    return optimized_blocks
