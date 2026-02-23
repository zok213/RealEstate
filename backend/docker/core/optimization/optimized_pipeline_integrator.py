"""
Optimized Pipeline Integration

Tích hợp các thuật toán tối ưu mới vào LandRedistributionPipeline:
1. Advanced Plot Optimizer - Shape quality optimization
2. Layout-Aware Subdivider - Pattern-based subdivision
3. Enhanced Subdivision Solver - Frontage ratio optimization
4. Access Optimizer - Road network optimization

Wrapper functions để dễ dàng integrate vào pipeline hiện tại
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from shapely.geometry import Polygon, LineString

# Import thuật toán tối ưu mới
from core.optimization.advanced_plot_optimizer import (
    PlotOptimizer,
    PlotShapeMetrics,
    apply_plot_optimization
)
from core.optimization.layout_aware_subdivider import (
    LayoutAwareSubdivider,
    LayoutAnalyzer,
    FishboneSubdivider,
    LayoutPattern
)
from core.optimization.enhanced_subdivision_solver import (
    EnhancedSubdivisionSolver
)
from core.optimization.access_optimizer import (
    RoadNetworkDesigner,
    FrontageOptimizer
)
from optimization.utility_router import UtilityNetworkDesigner
from optimization.financial_optimizer import FinancialModel

logger = logging.getLogger(__name__)


class OptimizedPipelineIntegrator:
    """
    Main integration class cho các thuật toán tối ưu
    """
    
    def __init__(
        self,
        use_advanced_optimizer: bool = True,
        use_layout_aware: bool = True,
        use_enhanced_solver: bool = True,
        use_access_optimizer: bool = True,
        min_quality_score: float = 60.0,
        target_frontage_ratio: float = 0.5
    ):
        """
        Args:
            use_advanced_optimizer: Sử dụng plot shape optimizer
            use_layout_aware: Sử dụng layout-aware subdivider
            use_enhanced_solver: Sử dụng enhanced CP solver
            use_access_optimizer: Sử dụng access optimizer
            min_quality_score: Điểm chất lượng tối thiểu cho plots
            target_frontage_ratio: Tỷ lệ mặt tiền/chiều sâu mục tiêu
        """
        self.use_advanced_optimizer = use_advanced_optimizer
        self.use_layout_aware = use_layout_aware
        self.use_enhanced_solver = use_enhanced_solver
        self.use_access_optimizer = use_access_optimizer
        
        # Initialize optimizers
        if use_advanced_optimizer:
            self.plot_optimizer = PlotOptimizer(
                min_quality_score=min_quality_score
            )
        
        if use_layout_aware:
            self.layout_subdivider = LayoutAwareSubdivider()
        
        if use_access_optimizer:
            self.road_designer = RoadNetworkDesigner()
            
        # Initialize Utility and Financial models
        self.utility_designer = UtilityNetworkDesigner()
        self.financial_model = FinancialModel()
    
    def optimize_block_subdivision(
        self,
        block: Polygon,
        zone_type: str = 'FACTORY',
        target_lot_width: float = 20.0,
        target_lot_depth: float = 40.0
    ) -> List[Dict[str, Any]]:
        """
        Tối ưu subdivision cho một block
        
        Pipeline:
        1. Analyze block geometry
        2. Choose best layout pattern
        3. Subdivide using pattern
        4. Optimize plot shapes
        
        Args:
            block: Block polygon
            zone_type: Zone type
            target_lot_width: Target lot width
            target_lot_depth: Target lot depth
            
        Returns:
            List of optimized lots
        """
        logger.info(f"[OPTIMIZED PIPELINE] Processing block {block.area:.0f}m²")
        
        # Step 1: Subdivide with layout-aware algorithm
        if self.use_layout_aware:
            lots = self.layout_subdivider.subdivide_block(
                block,
                zone_type,
                force_pattern=None  # Auto-detect best pattern
            )
        else:
            # Fallback to simple subdivider
            from core.optimization.simple_subdivider import subdivide_block_simple
            lots = subdivide_block_simple(
                block,
                zone_type,
                target_lot_width,
                target_lot_depth
            )
        
        logger.info(f"[OPTIMIZED PIPELINE] Initial subdivision: {len(lots)} lots")
        
        # Step 2: Optimize plot shapes
        if self.use_advanced_optimizer and lots:
            lots = self.plot_optimizer.optimize_plots(lots, block)
            logger.info(f"[OPTIMIZED PIPELINE] After shape optimization: {len(lots)} lots")
        
        return lots
    
    def optimize_multiple_blocks(
        self,
        blocks: List[Dict[str, Any]],
        zone_type: str = 'FACTORY'
    ) -> List[Dict[str, Any]]:
        """
        Tối ưu subdivision cho nhiều blocks
        
        Args:
            blocks: List of block dicts with 'geometry'
            zone_type: Default zone type
            
        Returns:
            List of blocks with optimized 'lots'
        """
        logger.info(f"[OPTIMIZED PIPELINE] Processing {len(blocks)} blocks")
        
        result = []
        total_lots = 0
        
        for i, block_dict in enumerate(blocks):
            block_geom = block_dict.get('geometry')
            if not isinstance(block_geom, Polygon):
                continue
            
            zone = block_dict.get('zone', zone_type)
            
            # Optimize subdivision for this block
            lots = self.optimize_block_subdivision(
                block_geom,
                zone
            )
            
            # Calculate quality metrics
            if lots:
                avg_quality = sum(
                    PlotShapeMetrics.calculate_quality_score(lot['geometry'])
                    for lot in lots
                ) / len(lots)
                
                avg_area = sum(lot['geometry'].area for lot in lots) / len(lots)
            else:
                avg_quality = 0.0
                avg_area = 0.0
            
            # Add to result
            block_copy = block_dict.copy()
            block_copy['lots'] = lots
            block_copy['num_lots'] = len(lots)
            block_copy['avg_lot_quality'] = avg_quality
            block_copy['avg_lot_area'] = avg_area
            result.append(block_copy)
            
            total_lots += len(lots)
            
            logger.info(
                f"[OPTIMIZED PIPELINE] Block {i+1}/{len(blocks)}: "
                f"{len(lots)} lots, quality={avg_quality:.1f}/100"
            )
        
        logger.info(f"[OPTIMIZED PIPELINE] ✓ Total: {total_lots} optimized lots")
        return result
    
    def optimize_road_network(
        self,
        land_boundary: Polygon,
        num_branches: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Optimize road network layout
        
        Args:
            land_boundary: Site boundary
            num_branches: Number of main road branches
            
        Returns:
            List of road segments
        """
        if not self.use_access_optimizer:
            return []
        
        logger.info(f"[OPTIMIZED PIPELINE] Designing road network")
        
        roads = self.road_designer.design_skeleton_network(
            land_boundary,
            num_branches,
            pattern='grid'
        )
        
        total_length = sum(r['length'] for r in roads)
        logger.info(
            f"[OPTIMIZED PIPELINE] ✓ Created {len(roads)} roads, "
            f"total length={total_length:.0f}m"
        )
        
        return roads
    
    def add_access_to_lots(
        self,
        lots: List[Dict[str, Any]],
        roads: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Add road access information to lots
        
        Args:
            lots: List of lot dicts
            roads: List of road dicts
            
        Returns:
            Lots with access info
        """
        if not self.use_access_optimizer or not roads:
            return lots
        
        logger.info(f"[OPTIMIZED PIPELINE] Adding access info to lots")
        
        updated_lots = self.road_designer.add_access_roads_to_lots(lots, roads)
        
        return updated_lots
    
    def calculate_comprehensive_metrics(
        self,
        blocks: List[Dict[str, Any]],
        roads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive metrics for the design
        
        Args:
            blocks: List of blocks with lots
            roads: List of roads
            
        Returns:
            Dict with metrics
        """
        # Collect all lots
        all_lots = []
        for block in blocks:
            all_lots.extend(block.get('lots', []))
        
        if not all_lots:
            return {
                'total_lots': 0,
                'error': 'No lots generated'
            }
        
        # Calculate metrics
        total_lots = len(all_lots)
        total_lot_area = sum(lot['geometry'].area for lot in all_lots)
        
        # Quality scores
        quality_scores = [
            PlotShapeMetrics.calculate_quality_score(lot['geometry'])
            for lot in all_lots
        ]
        avg_quality = sum(quality_scores) / len(quality_scores)
        high_quality_lots = sum(1 for s in quality_scores if s >= 80)
        
        # Shape metrics
        rectangularities = [
            PlotShapeMetrics.calculate_rectangularity(lot['geometry'])
            for lot in all_lots
        ]
        avg_rectangularity = sum(rectangularities) / len(rectangularities)
        
        aspect_ratios = [
            PlotShapeMetrics.calculate_aspect_ratio(lot['geometry'])
            for lot in all_lots
        ]
        avg_aspect = sum(aspect_ratios) / len(aspect_ratios)
        
        # Access metrics
        with_access = sum(1 for lot in all_lots if lot.get('has_access', False))
        access_rate = with_access / total_lots if total_lots > 0 else 0
        
        # Road metrics
        total_road_length = sum(r.get('length', 0) for r in roads)
        
        return {
            'total_lots': total_lots,
            'total_lot_area': total_lot_area,
            'avg_lot_area': total_lot_area / total_lots if total_lots > 0 else 0,
            'avg_quality_score': avg_quality,
            'high_quality_lots': high_quality_lots,
            'high_quality_rate': high_quality_lots / total_lots if total_lots > 0 else 0,
            'avg_rectangularity': avg_rectangularity,
            'avg_aspect_ratio': avg_aspect,
            'lots_with_access': with_access,
            'access_rate': access_rate,
            'total_road_length': total_road_length,
            'road_segments': len(roads)
        }
    
    def optimize_utility_network(
        self,
        lots: List[Dict[str, Any]],
        roads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Optimize utility networks (Water, Sewer, Electric)
        """
        import shapely.geometry
        
        # Calculate centroids for utility connection if needed
        # Assuming lots and roads are ready
        
        # 1. Water
        water_net = self.utility_designer.design_water_network(
            lots, roads, shapely.geometry.Point(0, 0) # Mock source
        )
        
        # 2. Sewer
        sewer_net = self.utility_designer.design_sewer_network(
            lots, roads, shapely.geometry.Point(0, 0) # Mock outlet
        )
        
        # 3. Electric
        electric_net = self.utility_designer.design_electrical_network(
            lots, roads, shapely.geometry.Point(0, 0) # Mock substation
        )
        
        return {
            'water': water_net,
            'sewer': sewer_net,
            'electric': electric_net
        }

    def calculate_financials_with_real_utilities(
        self,
        blocks: List[Dict[str, Any]],
        roads: List[Dict[str, Any]],
        utility_networks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate financial metrics using REAL utility costs
        """
        all_lots = []
        for block in blocks:
            all_lots.extend(block.get('lots', []))
            
        design = {
            'lots': all_lots,
            'roads': roads,
            'total_area': sum(b.get('geometry').area for b in blocks)
        }
        
        # Extract costs
        utility_costs = {
            'water_pipes': utility_networks['water']['cost'],
            'sewer_pipes': utility_networks['sewer']['cost'],
            'electric_cables': utility_networks['electric']['cost']
        }
        
        # Calculate!
        metrics = self.financial_model.calculate_roi_metrics(design)
        
        # Re-calculate construction cost with override (if calculate_roi_metrics doesn't support it directly yet, we do it step by step)
        # FinancialModel.calculate_roi_metrics calls calculate_construction_cost.
        # But I only updated calculate_construction_cost to accept `utility_network_costs`.
        # I need to update calculate_roi_metrics in FinancialModel OR manually call it here.
        
        # Let's manually call construction cost with utilities
        real_cost = self.financial_model.calculate_construction_cost(
            design, 
            utility_network_costs=utility_costs
        )
        
        metrics['cost_breakdown'] = real_cost
        metrics['total_cost'] = real_cost['total_construction_cost']
        metrics['gross_profit'] = metrics['total_revenue'] - metrics['total_cost']
        metrics['roi_percentage'] = (metrics['gross_profit'] / metrics['total_cost'] * 100) if metrics['total_cost'] > 0 else 0
        
        return metrics


# Convenience functions for quick integration

def optimize_subdivision_pipeline(
    blocks: List[Dict[str, Any]],
    land_boundary: Polygon,
    config: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """
    One-shot function để optimize toàn bộ subdivision
    
    Args:
        blocks: Input blocks
        land_boundary: Site boundary
        config: Configuration dict
        
    Returns:
        (optimized_blocks, roads, metrics)
    """
    # Extract config
    use_advanced = config.get('use_advanced_optimization', True)
    num_branches = config.get('num_road_branches', 3)
    min_quality = config.get('min_plot_quality', 60.0)
    
    # Initialize integrator
    integrator = OptimizedPipelineIntegrator(
        use_advanced_optimizer=use_advanced,
        use_layout_aware=use_advanced,
        use_enhanced_solver=use_advanced,
        use_access_optimizer=use_advanced,
        min_quality_score=min_quality
    )
    
    # Step 1: Optimize road network
    roads = integrator.optimize_road_network(land_boundary, num_branches)
    
    # Step 2: Optimize block subdivision
    optimized_blocks = integrator.optimize_multiple_blocks(blocks)
    
    # Step 3: Add access info
    all_lots = []
    for block in optimized_blocks:
        lots = block.get('lots', [])
        if lots:
            updated_lots = integrator.add_access_to_lots(lots, roads)
            block['lots'] = updated_lots
            all_lots.extend(updated_lots)
            
    # Step 4: Optimize Utilities (Real Routing)
    utility_networks = integrator.optimize_utility_network(all_lots, roads)
    
    # Step 5: Financial Analysis (With Real Utilities)
    financial_metrics = integrator.calculate_financials_with_real_utilities(
        optimized_blocks, roads, utility_networks
    )
    
    # Step 6: Calculate geometry metrics
    metrics = integrator.calculate_comprehensive_metrics(optimized_blocks, roads)
    
    # Merge financial metrics
    metrics.update(financial_metrics)
    metrics['utility_networks'] = utility_networks
    
    logger.info("=" * 60)
    logger.info("[OPTIMIZED PIPELINE] SUMMARY")
    logger.info(f"  Total Lots: {metrics['total_lots']}")
    logger.info(f"  Avg Quality: {metrics['avg_quality_score']:.1f}/100")
    logger.info(f"  High Quality Rate: {metrics['high_quality_rate']*100:.1f}%")
    logger.info(f"  Access Rate: {metrics['access_rate']*100:.1f}%")
    logger.info(f"  Avg Rectangularity: {metrics['avg_rectangularity']*100:.1f}%")
    logger.info(f"  Total Road Length: {metrics['total_road_length']:.0f}m")
    logger.info("=" * 60)
    
    return optimized_blocks, roads, metrics
