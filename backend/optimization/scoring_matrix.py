"""
Comprehensive Scoring Matrix System for Industrial Park Designs

Provides weighted scoring across multiple dimensions:
- IEAT Thailand Compliance (25%)
- Financial ROI (20%)
- Lot Efficiency (15%)
- Infrastructure Cost (15%)
- Construction Timeline (10%)
- Customer Satisfaction (10%)
- Risk Assessment (5%)

Enables design comparison and sensitivity analysis.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScoreWeights:
    """Configurable weights for scoring dimensions."""
    ieat_compliance: float = 0.25     # 25%
    financial_roi: float = 0.20        # 20%
    lot_efficiency: float = 0.15       # 15%
    infrastructure_cost: float = 0.15  # 15%
    construction_timeline: float = 0.10 # 10%
    customer_satisfaction: float = 0.10 # 10%
    risk_assessment: float = 0.05      # 5%
    
    def validate(self):
        """Ensure weights sum to 1.0."""
        total = (
            self.ieat_compliance +
            self.financial_roi +
            self.lot_efficiency +
            self.infrastructure_cost +
            self.construction_timeline +
            self.customer_satisfaction +
            self.risk_assessment
        )
        if not np.isclose(total, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total:.3f}")


class DesignScorer:
    """
    Score industrial park designs across multiple dimensions.
    
    Provides:
    - Individual dimension scores (0-100)
    - Weighted total score
    - Design comparison
    - Sensitivity analysis
    """
    
    def __init__(self, weights: Optional[ScoreWeights] = None):
        """
        Initialize scorer with custom weights.
        
        Args:
            weights: Custom score weights (default: standard IEAT-focused)
        """
        self.weights = weights or ScoreWeights()
        self.weights.validate()
    
    def score_design(self, design: Dict) -> Dict:
        """
        Calculate comprehensive score for a design.
        
        Args:
            design: {
                "site_boundary": Polygon,
                "lots": List[Polygon],
                "roads": List[LineString],
                "infrastructure": Dict,
                "financial": Dict,
                "timeline": Dict,
                "compliance": Dict
            }
        
        Returns:
            {
                "total_score": float (0-100),
                "weighted_score": float (0-100),
                "dimension_scores": {
                    "ieat_compliance": float,
                    "financial_roi": float,
                    ...
                },
                "breakdown": Dict (detailed metrics),
                "grade": str (A+, A, B+, ...)
            }
        """
        logger.info("[SCORING] Calculating design score")
        
        # Calculate individual dimension scores
        scores = {
            "ieat_compliance": self._score_ieat_compliance(design),
            "financial_roi": self._score_financial_roi(design),
            "lot_efficiency": self._score_lot_efficiency(design),
            "infrastructure_cost": self._score_infrastructure_cost(design),
            "construction_timeline": self._score_construction_timeline(design),
            "customer_satisfaction": self._score_customer_satisfaction(design),
            "risk_assessment": self._score_risk_assessment(design)
        }
        
        # Calculate weighted total
        weighted_total = (
            scores["ieat_compliance"] * self.weights.ieat_compliance +
            scores["financial_roi"] * self.weights.financial_roi +
            scores["lot_efficiency"] * self.weights.lot_efficiency +
            scores["infrastructure_cost"] * self.weights.infrastructure_cost +
            scores["construction_timeline"] * self.weights.construction_timeline +
            scores["customer_satisfaction"] * self.weights.customer_satisfaction +
            scores["risk_assessment"] * self.weights.risk_assessment
        )
        
        # Simple average for total score
        total_score = np.mean(list(scores.values()))
        
        # Assign grade
        grade = self._assign_grade(weighted_total)
        
        logger.info(f"[SCORING] Weighted score: {weighted_total:.1f}/100 (Grade: {grade})")
        
        return {
            "total_score": round(total_score, 2),
            "weighted_score": round(weighted_total, 2),
            "dimension_scores": {k: round(v, 2) for k, v in scores.items()},
            "grade": grade,
            "weights": {
                "ieat_compliance": self.weights.ieat_compliance,
                "financial_roi": self.weights.financial_roi,
                "lot_efficiency": self.weights.lot_efficiency,
                "infrastructure_cost": self.weights.infrastructure_cost,
                "construction_timeline": self.weights.construction_timeline,
                "customer_satisfaction": self.weights.customer_satisfaction,
                "risk_assessment": self.weights.risk_assessment
            }
        }
    
    def compare_designs(self, designs: List[Dict]) -> Dict:
        """
        Compare multiple designs side-by-side.
        
        Args:
            designs: List of design dicts (2-5 designs recommended)
        
        Returns:
            {
                "scores": List[Dict],
                "best_overall": int (index),
                "best_by_dimension": Dict[str, int],
                "comparison_matrix": Dict
            }
        """
        logger.info(f"[COMPARISON] Comparing {len(designs)} designs")
        
        # Score all designs
        scores = [self.score_design(d) for d in designs]
        
        # Find best overall
        best_overall_idx = max(
            range(len(scores)),
            key=lambda i: scores[i]["weighted_score"]
        )
        
        # Find best by dimension
        best_by_dimension = {}
        for dim in scores[0]["dimension_scores"].keys():
            best_by_dimension[dim] = max(
                range(len(scores)),
                key=lambda i: scores[i]["dimension_scores"][dim]
            )
        
        # Create comparison matrix
        comparison = self._create_comparison_matrix(designs, scores)
        
        logger.info(f"[COMPARISON] Best design: #{best_overall_idx + 1} (score: {scores[best_overall_idx]['weighted_score']:.1f})")
        
        return {
            "scores": scores,
            "best_overall": best_overall_idx,
            "best_by_dimension": best_by_dimension,
            "comparison_matrix": comparison
        }
    
    def sensitivity_analysis(
        self,
        design: Dict,
        parameter: str,
        value_range: Tuple[float, float],
        num_steps: int = 10
    ) -> Dict:
        """
        Analyze how score changes with parameter variation.
        
        Args:
            design: Base design
            parameter: Parameter to vary (e.g., "salable_area_pct")
            value_range: (min, max) values
            num_steps: Number of steps to test
        
        Returns:
            {
                "parameter": str,
                "values": List[float],
                "scores": List[float],
                "optimal_value": float,
                "score_delta": float
            }
        """
        logger.info(f"[SENSITIVITY] Analyzing {parameter}")
        
        values = np.linspace(value_range[0], value_range[1], num_steps)
        scores = []
        
        for val in values:
            # Create modified design
            modified = design.copy()
            self._set_parameter(modified, parameter, val)
            
            # Score modified design
            score_result = self.score_design(modified)
            scores.append(score_result["weighted_score"])
        
        # Find optimal value
        optimal_idx = np.argmax(scores)
        optimal_value = values[optimal_idx]
        optimal_score = scores[optimal_idx]
        
        # Calculate score delta
        base_score = scores[0]
        score_delta = optimal_score - base_score
        
        logger.info(f"[SENSITIVITY] Optimal {parameter}: {optimal_value:.2f} (score: {optimal_score:.1f}, Δ{score_delta:+.1f})")
        
        return {
            "parameter": parameter,
            "values": values.tolist(),
            "scores": scores,
            "optimal_value": float(optimal_value),
            "optimal_score": float(optimal_score),
            "score_delta": float(score_delta)
        }
    
    # ==================== SCORING METHODS ====================
    
    def _score_ieat_compliance(self, design: Dict) -> float:
        """
        Score IEAT Thailand compliance (0-100).
        
        Checks:
        - Salable area ≥75%
        - Green space ≥10%
        - Plot dimensions (40m frontage, 1600m² min)
        - Road ROW (20m min)
        - Infrastructure provision
        """
        score = 0.0
        compliance = design.get("compliance", {})
        
        # Salable area (30 points)
        salable_pct = compliance.get("salable_area_pct", 0)
        if salable_pct >= 0.75:
            score += 30
        elif salable_pct >= 0.70:
            score += 20
        elif salable_pct >= 0.65:
            score += 10
        
        # Green space (25 points)
        green_pct = compliance.get("green_space_pct", 0)
        if green_pct >= 0.10:
            score += 25
        elif green_pct >= 0.08:
            score += 15
        elif green_pct >= 0.05:
            score += 5
        
        # Plot dimensions (20 points)
        invalid_plots = compliance.get("invalid_plots", [])
        if len(invalid_plots) == 0:
            score += 20
        elif len(invalid_plots) <= 2:
            score += 10
        
        # Road standards (15 points)
        road_compliance = compliance.get("road_standards_met", False)
        if road_compliance:
            score += 15
        
        # Infrastructure (10 points)
        infra_compliance = compliance.get("infrastructure_complete", False)
        if infra_compliance:
            score += 10
        
        return min(score, 100.0)
    
    def _score_financial_roi(self, design: Dict) -> float:
        """
        Score financial ROI (0-100).
        
        Factors:
        - Revenue per rai
        - Development cost per rai
        - ROI percentage
        - Payback period
        """
        score = 0.0
        financial = design.get("financial", {})
        
        # ROI percentage (40 points)
        roi = financial.get("roi_percent", 0)
        if roi >= 35:
            score += 40
        elif roi >= 25:
            score += 30
        elif roi >= 15:
            score += 20
        elif roi >= 10:
            score += 10
        
        # Revenue per rai (30 points)
        revenue_per_rai = financial.get("revenue_per_rai_thb", 0) / 1_000_000  # millions
        if revenue_per_rai >= 10:
            score += 30
        elif revenue_per_rai >= 7:
            score += 20
        elif revenue_per_rai >= 5:
            score += 10
        
        # Payback period (20 points)
        payback = financial.get("payback_years", 999)
        if payback <= 3:
            score += 20
        elif payback <= 5:
            score += 15
        elif payback <= 7:
            score += 10
        
        # Salable lots (10 points)
        salable_lots = financial.get("salable_lots", 0)
        if salable_lots >= 30:
            score += 10
        elif salable_lots >= 20:
            score += 5
        
        return min(score, 100.0)
    
    def _score_lot_efficiency(self, design: Dict) -> float:
        """
        Score lot layout efficiency (0-100).
        
        Factors:
        - Lot area utilization
        - Lot count
        - Average lot size
        - Frontage utilization
        """
        score = 0.0
        lots = design.get("lots", [])
        site_area = design.get("site_boundary").area if design.get("site_boundary") else 1
        
        # Lot count (25 points)
        num_lots = len(lots)
        if num_lots >= 40:
            score += 25
        elif num_lots >= 30:
            score += 20
        elif num_lots >= 20:
            score += 15
        elif num_lots >= 10:
            score += 10
        
        # Area utilization (30 points)
        total_lot_area = sum(lot.area for lot in lots) if lots else 0
        utilization = total_lot_area / site_area if site_area > 0 else 0
        if utilization >= 0.75:
            score += 30
        elif utilization >= 0.70:
            score += 20
        elif utilization >= 0.65:
            score += 10
        
        # Average lot size (25 points) - target 3000-5000 m²
        avg_lot_size = total_lot_area / num_lots if num_lots > 0 else 0
        if 3000 <= avg_lot_size <= 5000:
            score += 25
        elif 2000 <= avg_lot_size <= 6000:
            score += 15
        elif 1600 <= avg_lot_size <= 8000:
            score += 10
        
        # Lot regularity (20 points) - prefer rectangular lots
        regularity_score = self._calculate_lot_regularity(lots)
        score += regularity_score * 0.2
        
        return min(score, 100.0)
    
    def _score_infrastructure_cost(self, design: Dict) -> float:
        """
        Score infrastructure cost efficiency (0-100).
        
        Lower cost = higher score.
        Factors:
        - Total infrastructure cost
        - Cost per rai
        - Cost per salable lot
        """
        score = 0.0
        financial = design.get("financial", {})
        site_area_rai = design.get("site_boundary").area / 1600 if design.get("site_boundary") else 1
        
        # Cost per rai (50 points)
        infra_cost_per_rai = financial.get("infrastructure_cost_per_rai_thb", 0) / 1_000_000  # millions
        if infra_cost_per_rai <= 1.5:
            score += 50
        elif infra_cost_per_rai <= 2.0:
            score += 40
        elif infra_cost_per_rai <= 2.5:
            score += 30
        elif infra_cost_per_rai <= 3.0:
            score += 20
        else:
            score += 10
        
        # Infrastructure ratio (30 points) - prefer < 25% of total cost
        total_cost = financial.get("total_cost_thb", 1)
        infra_cost = financial.get("infrastructure_cost_thb", 0)
        infra_ratio = infra_cost / total_cost if total_cost > 0 else 1
        if infra_ratio <= 0.20:
            score += 30
        elif infra_ratio <= 0.25:
            score += 20
        elif infra_ratio <= 0.30:
            score += 10
        
        # Efficiency metrics (20 points)
        road_length = financial.get("road_length_km", 0)
        road_efficiency = road_length / site_area_rai if site_area_rai > 0 else 999
        if road_efficiency <= 0.5:  # ≤0.5 km road per rai
            score += 20
        elif road_efficiency <= 0.7:
            score += 10
        
        return min(score, 100.0)
    
    def _score_construction_timeline(self, design: Dict) -> float:
        """
        Score construction timeline (0-100).
        
        Shorter = better.
        Target: ≤12 months
        """
        score = 0.0
        timeline = design.get("timeline", {})
        
        # Total duration (60 points)
        total_months = timeline.get("total_months", 999)
        if total_months <= 10:
            score += 60
        elif total_months <= 12:
            score += 50
        elif total_months <= 15:
            score += 40
        elif total_months <= 18:
            score += 30
        elif total_months <= 24:
            score += 20
        else:
            score += 10
        
        # Critical path efficiency (20 points)
        critical_path_pct = timeline.get("critical_path_pct", 100)
        if critical_path_pct <= 70:
            score += 20
        elif critical_path_pct <= 85:
            score += 10
        
        # Parallelization (20 points)
        parallel_tasks = timeline.get("parallel_tasks", 0)
        if parallel_tasks >= 5:
            score += 20
        elif parallel_tasks >= 3:
            score += 10
        
        return min(score, 100.0)
    
    def _score_customer_satisfaction(self, design: Dict) -> float:
        """
        Score expected customer satisfaction (0-100).
        
        Factors:
        - Plot sizes meet demand
        - Industry fit
        - Amenities
        - Flexibility
        """
        score = 50.0  # Base score
        
        customer = design.get("customer", {})
        
        # Plot size diversity (25 points)
        size_diversity = customer.get("lot_size_diversity", 0)
        if size_diversity >= 3:  # 3+ size categories
            score += 25
        elif size_diversity >= 2:
            score += 15
        
        # Industry compatibility (25 points)
        industry_fit = customer.get("industry_compatibility_score", 0)
        score += industry_fit * 0.25
        
        return min(score, 100.0)
    
    def _score_risk_assessment(self, design: Dict) -> float:
        """
        Score risk factors (0-100).
        
        Lower risk = higher score.
        """
        score = 100.0  # Start perfect, deduct for risks
        
        risks = design.get("risks", {})
        
        # Compliance risk
        if not risks.get("ieat_compliant", True):
            score -= 30
        
        # Financial risk
        if risks.get("roi_percent", 20) < 10:
            score -= 20
        
        # Timeline risk
        if risks.get("construction_complexity", "medium") == "high":
            score -= 15
        
        # Environmental risk
        if risks.get("environmental_impact", "low") == "high":
            score -= 20
        
        # Market risk
        if risks.get("market_demand", "medium") == "low":
            score -= 15
        
        return max(score, 0.0)
    
    # ==================== HELPER METHODS ====================
    
    def _calculate_lot_regularity(self, lots: List) -> float:
        """Calculate lot shape regularity (0-100)."""
        if not lots:
            return 0.0
        
        regularities = []
        for lot in lots:
            # Compare area to bounding box area
            bounds = lot.bounds
            bbox_area = (bounds[2] - bounds[0]) * (bounds[3] - bounds[1])
            regularity = lot.area / bbox_area if bbox_area > 0 else 0
            regularities.append(regularity * 100)
        
        return np.mean(regularities)
    
    def _assign_grade(self, score: float) -> str:
        """Assign letter grade based on score."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 65:
            return "D+"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _create_comparison_matrix(self, designs: List[Dict], scores: List[Dict]) -> Dict:
        """Create detailed comparison matrix."""
        matrix = {
            "designs": [],
            "dimensions": {}
        }
        
        # Add design summaries
        for i, (design, score) in enumerate(zip(designs, scores)):
            matrix["designs"].append({
                "id": i,
                "name": design.get("name", f"Design {i+1}"),
                "weighted_score": score["weighted_score"],
                "grade": score["grade"]
            })
        
        # Add dimension comparisons
        for dim in scores[0]["dimension_scores"].keys():
            matrix["dimensions"][dim] = [
                s["dimension_scores"][dim] for s in scores
            ]
        
        return matrix
    
    def _set_parameter(self, design: Dict, parameter: str, value: float):
        """Set design parameter for sensitivity analysis."""
        # This is a simplified version
        # In production, would need more sophisticated parameter handling
        if parameter in design:
            design[parameter] = value


# Example usage
if __name__ == "__main__":
    # Mock design for testing
    test_design = {
        "name": "Test Design 1",
        "site_boundary": type('obj', (object,), {'area': 800000})(),  # Mock polygon
        "lots": [type('obj', (object,), {'area': 3000})() for _ in range(35)],
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
    
    scorer = DesignScorer()
    result = scorer.score_design(test_design)
    
    print(f"\n✓ Design Scoring Complete")
    print(f"  • Weighted Score: {result['weighted_score']:.1f}/100 (Grade: {result['grade']})")
    print(f"  • Total Score: {result['total_score']:.1f}/100")
    print(f"\n  Dimension Scores:")
    for dim, score in result['dimension_scores'].items():
        print(f"    - {dim}: {score:.1f}/100")
