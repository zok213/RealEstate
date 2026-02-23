"""
Financial Analysis API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import sys
import os

# Add backend path
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from optimization.financial_optimizer import (
    FinancialModel,
    CostParameters,
    RevenueParameters
)

router = APIRouter()
financial_model = FinancialModel()


class FinancialAnalysisRequest(BaseModel):
    """Request for financial analysis"""
    design: Dict[str, Any]
    cost_params: Optional[Dict[str, float]] = None
    revenue_params: Optional[Dict[str, float]] = None


class DesignComparison(BaseModel):
    """Multiple designs for comparison"""
    designs: List[Dict[str, Any]]


@router.post("/api/financial/analyze")
async def analyze_financial(request: FinancialAnalysisRequest):
    """
    Analyze financial metrics for a design
    
    **Parameters:**
    - design: Design object with lots, roads, utilities
    - cost_params: Optional custom cost parameters
    - revenue_params: Optional custom revenue parameters
    
    **Returns:**
    - Financial metrics including ROI, costs, revenue breakdown
    """
    try:
        # Create custom model if parameters provided
        if request.cost_params or request.revenue_params:
            cost_params = CostParameters(**request.cost_params) if request.cost_params else CostParameters()
            revenue_params = RevenueParameters(**request.revenue_params) if request.revenue_params else RevenueParameters()
            model = FinancialModel(cost_params, revenue_params)
        else:
            model = financial_model
        
        metrics = model.calculate_roi_metrics(request.design)
        
        return {
            "success": True,
            "metrics": metrics,
            "summary": {
                "roi_percentage": metrics['roi_percentage'],
                "gross_profit": metrics['gross_profit'],
                "total_cost": metrics['total_cost'],
                "total_revenue": metrics['total_revenue'],
                "is_profitable": metrics['gross_profit'] > 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Financial analysis failed: {str(e)}")


@router.post("/api/financial/compare")
async def compare_designs(comparison: DesignComparison):
    """
    Compare multiple designs financially
    
    **Parameters:**
    - designs: List of design objects to compare
    
    **Returns:**
    - Ranked comparison with best design highlighted
    """
    try:
        comparisons = []
        
        for i, design in enumerate(comparison.designs):
            metrics = financial_model.calculate_roi_metrics(design)
            comparisons.append({
                "design_id": i,
                "design_name": design.get('name', f'Design {i+1}'),
                "roi": metrics['roi_percentage'],
                "profit": metrics['gross_profit'],
                "cost": metrics['total_cost'],
                "revenue": metrics['total_revenue'],
                "profit_margin": metrics['profit_margin'],
                "num_lots": len(design.get('lots', []))
            })
        
        # Rank by ROI
        comparisons.sort(key=lambda x: x['roi'], reverse=True)
        
        return {
            "success": True,
            "comparisons": comparisons,
            "best_design": comparisons[0] if comparisons else None,
            "worst_design": comparisons[-1] if comparisons else None,
            "roi_range": {
                "min": comparisons[-1]['roi'] if comparisons else 0,
                "max": comparisons[0]['roi'] if comparisons else 0,
                "average": sum(c['roi'] for c in comparisons) / len(comparisons) if comparisons else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/api/financial/parameters")
async def get_default_parameters():
    """
    Get default cost and revenue parameters
    
    **Returns:**
    - Default CostParameters and RevenueParameters
    """
    return {
        "success": True,
        "cost_parameters": {
            "site_clearing_per_m2": 50_000,
            "grading_per_m2": 30_000,
            "road_cost_per_meter": 8_000_000,
            "main_road_multiplier": 1.5,
            "water_pipe_per_meter": 500_000,
            "sewer_pipe_per_meter": 800_000,
            "electric_cable_per_meter": 400_000,
            "utility_connection_per_lot": 100_000_000,
            "landscaping_per_m2": 150_000,
            "tree_planting_per_unit": 2_000_000,
            "design_fee_percentage": 0.03,
            "contingency_percentage": 0.10
        },
        "revenue_parameters": {
            "base_price_factory": 3_000_000,
            "base_price_warehouse": 2_500_000,
            "base_price_office": 4_000_000,
            "corner_lot_premium": 0.20,
            "high_quality_premium": 0.15,
            "frontage_premium_per_meter": 50_000,
            "large_lot_discount": 0.10,
            "irregular_shape_discount": 0.05,
            "market_demand_multiplier": 1.0
        },
        "currency": "THB",
        "note": "All prices in Thai Baht (THB)"
    }


@router.post("/api/financial/quick-estimate")
async def quick_estimate(
    total_area: float,
    num_lots: int,
    road_length: float = 0,
    zone_type: str = "FACTORY"
):
    """
    Quick financial estimate without full design
    
    **Parameters:**
    - total_area: Total site area in m²
    - num_lots: Number of lots
    - road_length: Total road length in meters (optional, estimated if 0)
    - zone_type: FACTORY, WAREHOUSE, or OFFICE
    
    **Returns:**
    - Quick cost and revenue estimates
    """
    try:
        # Estimate road length if not provided (roughly 20% of perimeter per lot)
        if road_length == 0:
            perimeter = 4 * (total_area ** 0.5)  # Approximate perimeter
            road_length = perimeter * 0.2 * num_lots
        
        # Create simplified design
        avg_lot_area = total_area / num_lots if num_lots > 0 else 0
        
        design = {
            'total_area': total_area,
            'roads': [{'length': road_length, 'type': 'internal'}],
            'lots': [
                {
                    'id': i,
                    'area': avg_lot_area,
                    'zone_type': zone_type,
                    'quality_score': 75,
                    'is_corner': i < 4,  # Assume first 4 are corners
                    'frontage': (avg_lot_area ** 0.5) * 0.5  # Estimate frontage
                }
                for i in range(num_lots)
            ],
            'green_space_area': total_area * 0.15
        }
        
        metrics = financial_model.calculate_roi_metrics(design)
        
        return {
            "success": True,
            "estimates": {
                "total_cost": metrics['total_cost'],
                "total_revenue": metrics['total_revenue'],
                "gross_profit": metrics['gross_profit'],
                "roi_percentage": metrics['roi_percentage'],
                "cost_per_lot": metrics['cost_per_lot'],
                "revenue_per_lot": metrics['revenue_per_lot'],
                "profit_per_lot": metrics['profit_per_lot']
            },
            "assumptions": {
                "avg_lot_area_m2": avg_lot_area,
                "estimated_road_length_m": road_length,
                "green_space_ratio": 0.15,
                "zone_type": zone_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Estimation failed: {str(e)}")


def get_router():
    """Export router for main.py"""
    return router
