"""
API endpoints for design scoring and comparison.

Endpoints:
- POST /api/scoring/score-design: Score a single design
- POST /api/scoring/compare-designs: Compare multiple designs
- POST /api/scoring/sensitivity: Sensitivity analysis
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Tuple
import logging

from backend.optimization.scoring_matrix import DesignScorer, ScoreWeights

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scoring", tags=["scoring"])


class ScoreDesignRequest(BaseModel):
    """Request to score a single design."""
    design_id: str
    design_data: Optional[dict] = None  # If not provided, load from database
    custom_weights: Optional[dict] = None


class CompareDesignsRequest(BaseModel):
    """Request to compare multiple designs."""
    design_ids: List[str]
    custom_weights: Optional[dict] = None


class SensitivityRequest(BaseModel):
    """Request for sensitivity analysis."""
    design_id: str
    design_data: Optional[dict] = None
    parameter: str
    value_range: Tuple[float, float]
    num_steps: int = 10


@router.post("/score-design")
async def score_design(request: ScoreDesignRequest):
    """
    Score a single industrial park design.
    
    Returns comprehensive scores across 7 dimensions.
    """
    try:
        logger.info(f"[SCORING API] Scoring design {request.design_id}")
        
        # Load design data
        if request.design_data:
            design = request.design_data
        else:
            # In production, load from database
            design = _load_design_from_db(request.design_id)
        
        # Create scorer with custom weights if provided
        if request.custom_weights:
            weights = ScoreWeights(**request.custom_weights)
            scorer = DesignScorer(weights)
        else:
            scorer = DesignScorer()
        
        # Calculate score
        result = scorer.score_design(design)
        
        score = result['weighted_score']
        logger.info(
            f"[SCORING API] Design {request.design_id} scored: {score:.1f}/100"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"[SCORING API] Error scoring design: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-designs")
async def compare_designs(request: CompareDesignsRequest):
    """
    Compare multiple industrial park designs.
    
    Returns side-by-side comparison with best design identification.
    """
    try:
        num_designs = len(request.design_ids)
        logger.info(f"[COMPARISON API] Comparing {num_designs} designs")
        
        # Load all designs
        designs = [
            _load_design_from_db(design_id)
            for design_id in request.design_ids
        ]
        
        # Create scorer
        if request.custom_weights:
            weights = ScoreWeights(**request.custom_weights)
            scorer = DesignScorer(weights)
        else:
            scorer = DesignScorer()
        
        # Compare designs
        result = scorer.compare_designs(designs)
        
        best_idx = result['best_overall'] + 1
        logger.info(f"[COMPARISON API] Best design: #{best_idx}")
        
        return result
    
    except Exception as e:
        logger.error(f"[COMPARISON API] Error comparing designs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sensitivity")
async def sensitivity_analysis(request: SensitivityRequest):
    """
    Perform sensitivity analysis on a design parameter.
    
    Shows how score changes with parameter variation.
    """
    try:
        logger.info(
            f"[SENSITIVITY API] Analyzing {request.parameter} "
            f"for design {request.design_id}"
        )
        
        # Load design
        if request.design_data:
            design = request.design_data
        else:
            design = _load_design_from_db(request.design_id)
        
        # Create scorer
        scorer = DesignScorer()
        
        # Run sensitivity analysis
        result = scorer.sensitivity_analysis(
            design,
            request.parameter,
            request.value_range,
            request.num_steps
        )
        
        opt_val = result['optimal_value']
        logger.info(
            f"[SENSITIVITY API] Optimal {request.parameter}: {opt_val:.3f}"
        )
        
        return result
    
    except Exception as e:
        logger.error(
            f"[SENSITIVITY API] Error in sensitivity analysis: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


def _load_design_from_db(design_id: str) -> dict:
    """
    Load design data from database.
    
    In production, this would query the actual database.
    For now, returns mock data.
    """
    # Mock data for testing
    from shapely.geometry import Polygon
    
    return {
        "name": f"Design {design_id}",
        "site_boundary": Polygon(
            [(0, 0), (1000, 0), (1000, 800), (0, 800)]
        ),
        "lots": [
            Polygon([
                (i*50, j*50),
                (i*50+40, j*50),
                (i*50+40, j*50+40),
                (i*50, j*50+40)
            ])
            for i in range(15) for j in range(12)
        ],
        "compliance": {
            "salable_area_pct": 0.76,
            "green_space_pct": 0.12,
            "invalid_plots": [],
            "road_standards_met": True,
            "infrastructure_complete": True
        },
        "financial": {
            "roi_percent": 28,
            "revenue_per_rai_thb": 9_500_000,
            "payback_years": 4.2,
            "salable_lots": 35,
            "infrastructure_cost_per_rai_thb": 1_800_000,
            "total_cost_thb": 120_000_000,
            "infrastructure_cost_thb": 22_000_000,
            "road_length_km": 2.8
        },
        "timeline": {
            "total_months": 11,
            "critical_path_pct": 75,
            "parallel_tasks": 4
        },
        "customer": {
            "lot_size_diversity": 3,
            "industry_compatibility_score": 85
        },
        "risks": {
            "ieat_compliant": True,
            "roi_percent": 28,
            "construction_complexity": "medium",
            "environmental_impact": "low",
            "market_demand": "high"
        }
    }
