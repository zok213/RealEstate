"""
Compliance Checker for IEAT Thailand Standards.
Automated verification of industrial park layouts against IEAT regulations.
"""

from typing import Dict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ComplianceChecker:
    """
    Automated compliance verification against IEAT Thailand standards.
    Returns detailed report with violations and remediation suggestions.
    """
    
    def __init__(self,
                regulations: Dict = None,
                standard: str = "ieat_thailand"):
        """
        Args:
            regulations: Override regulations dict
            standard: "ieat_thailand" (default, only supported standard)
        """
        if regulations:
            self.all_regs = regulations
        else:
            from config import INDUSTRIAL_PARK_REGULATIONS
            self.all_regs = INDUSTRIAL_PARK_REGULATIONS

        self.standard = "ieat_thailand"  # Only IEAT Thailand supported
        self.regs = self.all_regs.get("ieat_thailand", {})
    
    def check_layout(self, layout: Dict) -> Dict:
        """
        Comprehensive compliance check against IEAT Thailand standards.
        
        Returns:
            {
                "standard_used": "ieat_thailand",
                "overall_compliance_percent": 95.5,
                "status": "PASS" | "WARNING" | "FAIL",
                "checks": {...},
                "violations": [...],
                "recommendations": [...]
            }
        """
        report = {
            "standard_used": "ieat_thailand",
            "overall_compliance_percent": 0,
            "status": "UNKNOWN",
            "checks": {},
            "violations": [],
            "recommendations": []
        }
        
        # Execute IEAT Thailand checks only
        report["checks"]["land_use"] = self._check_ieat_land_use(layout)
        report["checks"]["plot_dimensions"] = self._check_ieat_plot_dimensions(layout)
        report["checks"]["road_standards"] = self._check_ieat_roads(layout)
        report["checks"]["infrastructure"] = self._check_ieat_infrastructure(layout)
        report["checks"]["green_requirements"] = self._check_ieat_green(layout)
        
        # Calculate overall compliance
        checks = report["checks"]
        compliance_scores = [v.get("score", 0) for v in checks.values()]
        report["overall_compliance_percent"] = round(
            sum(compliance_scores) / len(compliance_scores) if compliance_scores else 0,
            1
        )
        
        # Determine status
        if report["overall_compliance_percent"] >= 95:
            report["status"] = "PASS"
        elif report["overall_compliance_percent"] >= 80:
            report["status"] = "WARNING"
        else:
            report["status"] = "FAIL"
        
        # Collect violations and recommendations
        for check_name, check_result in checks.items():
            if check_result.get("violations"):
                report["violations"].extend(check_result["violations"])
            if check_result.get("recommendations"):
                report["recommendations"].extend(check_result["recommendations"])
        
        return report
    
    # ==================== IEAT THAILAND CHECKS ====================
    
    def _check_ieat_land_use(self, layout: Dict) -> Dict:
        """
        IEAT Land Use Requirements:
        - Salable area >= 75%
        - Green >= 10%
        - U+G >= 250 rai (TA > 1000 rai) or >= 25% (TA <= 1000 rai)
        """
        site = layout.get('site', {})
        total_area_m2 = site.get('total_area_m2', 500000)
        total_area_rai = total_area_m2 / 1600  # 1 rai = 1600 mÂ²
        
        buildings = layout.get('buildings', [])
        salable_area = sum(b.get('area_m2', 0) for b in buildings)
        green_area = site.get('green_area_m2', total_area_m2 * 0.15)
        utility_area = site.get('utility_area_m2', total_area_m2 * 0.10)
        
        salable_percent = (salable_area / total_area_m2) * 100
        green_percent = (green_area / total_area_m2) * 100
        ug_area_rai = (utility_area + green_area) / 1600
        ug_percent = ((utility_area + green_area) / total_area_m2) * 100
        
        reqs = self.regs["land_use"]
        violations = []
        recommendations = []
        score = 100
        
        # Check salable area
        if salable_percent < reqs["salable_area_min_percent"]:
            deficit = reqs["salable_area_min_percent"] - salable_percent
            violations.append(
                f"Salable area {salable_percent:.1f}% < {reqs['salable_area_min_percent']}% (deficit: {deficit:.1f}%)"
            )
            recommendations.append(
                f"Increase salable plots by {deficit * total_area_m2 / 100:.0f} mÂ²"
            )
            score -= 30
        
        # Check green area
        if green_percent < reqs["green_min_percent"]:
            deficit = reqs["green_min_percent"] - green_percent
            violations.append(
                f"Green area {green_percent:.1f}% < {reqs['green_min_percent']}% (deficit: {deficit:.1f}%)"
            )
            recommendations.append(
                f"Add {deficit * total_area_m2 / 100:.0f} mÂ² of green space"
            )
            score -= 25
        
        # Check U+G requirement based on project size
        green_reqs = self.regs["green_requirements"]
        if total_area_rai > green_reqs["threshold_rai"]:
            # Large project: U+G >= 250 rai
            if ug_area_rai < green_reqs["large_project_min_rai"]:
                deficit = green_reqs["large_project_min_rai"] - ug_area_rai
                violations.append(
                    f"U+G {ug_area_rai:.1f} rai < {green_reqs['large_project_min_rai']} rai (large project)"
                )
                recommendations.append(
                    f"Add {deficit * 1600:.0f} mÂ² to utility+green areas"
                )
                score -= 20
        else:
            # Small project: U+G >= 25%
            if ug_percent < green_reqs["small_project_min_percent"]:
                deficit = green_reqs["small_project_min_percent"] - ug_percent
                violations.append(
                    f"U+G {ug_percent:.1f}% < {green_reqs['small_project_min_percent']}% (small project)"
                )
                recommendations.append(
                    f"Add {deficit * total_area_m2 / 100:.0f} mÂ² to U+G"
                )
                score -= 20
        
        return {
            "score": max(0, score),
            "violations": violations,
            "recommendations": recommendations,
            "metrics": {
                "total_area_rai": round(total_area_rai, 2),
                "salable_percent": round(salable_percent, 2),
                "green_percent": round(green_percent, 2),
                "ug_area_rai": round(ug_area_rai, 2),
                "ug_percent": round(ug_percent, 2)
            }
        }
    
    def _check_ieat_plot_dimensions(self, layout: Dict) -> Dict:
        """
        IEAT Plot Requirements:
        - Rectangular shape (1:1.5 to 1:2)
        - Min frontage width 90m (preferred 100m)
        """
        buildings = layout.get('buildings', [])
        reqs = self.regs["plot_dimensions"]
        violations = []
        recommendations = []
        score = 100
        
        for i, building in enumerate(buildings):
            width = building.get('width_m', 50)
            length = building.get('length_m', 80)
            
            # Calculate aspect ratio
            ratio = length / width if width > 0 else 1
            min_ratio, max_ratio = reqs["width_to_depth_ratio"]
            
            # Check aspect ratio (1:1.5 to 1:2)
            if ratio < min_ratio or ratio > max_ratio:
                violations.append(
                    f"Plot {i+1}: aspect ratio {ratio:.2f} outside range {min_ratio}-{max_ratio}"
                )
                recommendations.append(
                    f"Plot {i+1}: Adjust to {width}m Ã— {width * 1.5:.0f}m (optimal 1:1.5)"
                )
                score -= 5
            
            # Check frontage width
            if width < reqs["min_frontage_width_m"]:
                violations.append(
                    f"Plot {i+1}: frontage {width}m < {reqs['min_frontage_width_m']}m minimum"
                )
                recommendations.append(
                    f"Plot {i+1}: Increase frontage to {reqs['preferred_frontage_m']}m"
                )
                score -= 10
        
        return {
            "score": max(0, score),
            "violations": violations,
            "recommendations": recommendations
        }
    
    def _check_ieat_roads(self, layout: Dict) -> Dict:
        """
        IEAT Road Standards:
        - Traffic lane: 3.5m width
        - Min ROW: 25m
        - Main roads: 25-30m ROW
        """
        site = layout.get('site', {})
        road_network = site.get('road_network', [])
        reqs = self.regs["road_standards"]
        violations = []
        recommendations = []
        score = 100
        
        for i, road in enumerate(road_network):
            width = road.get('width_m', 12)
            road_type = road.get('type', 'secondary')
            
            if road_type == 'primary' or road_type == 'main':
                min_row, max_row = reqs["main_road_row_m"]
                if width < min_row:
                    violations.append(
                        f"Main road {i+1}: ROW {width}m < {min_row}m minimum"
                    )
                    recommendations.append(
                        f"Widen main road to {min_row}m ROW"
                    )
                    score -= 15
            else:
                if width < reqs["min_right_of_way_m"]:
                    violations.append(
                        f"Road {i+1}: ROW {width}m < {reqs['min_right_of_way_m']}m minimum"
                    )
                    score -= 5
        
        return {
            "score": max(0, score),
            "violations": violations,
            "recommendations": recommendations
        }
    
    def _check_ieat_infrastructure(self, layout: Dict) -> Dict:
        """
        IEAT Infrastructure Requirements:
        - Retention pond: 20 rai per 1 rai pond
        - Water treatment: 2000 cmd/rai
        - Wastewater: 500 cmd/rai
        - Substation: 10 rai at center
        """
        site = layout.get('site', {})
        total_area_rai = site.get('total_area_m2', 500000) / 1600
        infra_reqs = self.regs["infrastructure"]
        violations = []
        recommendations = []
        score = 100
        
        # Retention pond check
        pond_area_rai = site.get('retention_pond_rai', 0)
        required_pond_rai = total_area_rai / infra_reqs["retention_pond"]["ratio_rai"]
        if pond_area_rai < required_pond_rai * 0.8:  # 20% tolerance
            violations.append(
                f"Retention pond {pond_area_rai:.1f} rai insufficient (need ~{required_pond_rai:.1f} rai)"
            )
            recommendations.append(
                f"Add retention pond capacity: {required_pond_rai - pond_area_rai:.1f} rai"
            )
            score -= 20
        
        # Substation check
        if not site.get('has_substation'):
            recommendations.append(
                f"Add substation (10 rai) at project center for power distribution"
            )
            score -= 10
        
        return {
            "score": max(0, score),
            "violations": violations,
            "recommendations": recommendations,
            "metrics": {
                "total_area_rai": round(total_area_rai, 2),
                "required_pond_rai": round(required_pond_rai, 2),
                "actual_pond_rai": pond_area_rai
            }
        }
    
    def _check_ieat_green(self, layout: Dict) -> Dict:
        """
        IEAT Green Requirements:
        - Min 10% of GA
        - Min 10m green buffer strip
        """
        site = layout.get('site', {})
        total_area = site.get('total_area_m2', 500000)
        green_area = site.get('green_area_m2', 0)
        buffer_width = site.get('green_buffer_width_m', 10)
        
        reqs = self.regs["land_use"]
        violations = []
        recommendations = []
        score = 100
        
        green_percent = (green_area / total_area) * 100
        if green_percent < reqs["green_min_percent"]:
            deficit = reqs["green_min_percent"] - green_percent
            violations.append(
                f"Green {green_percent:.1f}% < {reqs['green_min_percent']}% minimum"
            )
            recommendations.append(
                f"Add {deficit * total_area / 100:.0f} mÂ² green space"
            )
            score -= 30
        
        if buffer_width < reqs["green_buffer_width_m"]:
            violations.append(
                f"Green buffer {buffer_width}m < {reqs['green_buffer_width_m']}m minimum"
            )
            recommendations.append(
                f"Increase buffer strip to {reqs['green_buffer_width_m']}m"
            )
            score -= 20
        
        return {
            "score": max(0, score),
            "violations": violations,
            "recommendations": recommendations,
            "metrics": {
                "green_percent": round(green_percent, 2),
                "buffer_width_m": buffer_width
            }
        }


# Test the compliance checker
if __name__ == "__main__":
    layout = {
        "buildings": [
            {"id": "b1", "type": "light_manufacturing", "x": 100, "y": 100, "width_m": 100, "length_m": 150, "area_m2": 15000, "label": "Factory 1"},
            {"id": "b2", "type": "warehouse", "x": 250, "y": 100, "width_m": 90, "length_m": 135, "area_m2": 12150, "label": "Warehouse 1"},
        ],
        "site": {
            "width": 1000,
            "height": 500,
            "total_area_m2": 500000,
            "green_area_m2": 75000,
            "utility_area_m2": 50000,
            "green_buffer_width_m": 10,
            "has_substation": True,
            "retention_pond_rai": 30,
            "road_network": [
                {"type": "main", "width_m": 25},
                {"type": "secondary", "width_m": 15}
            ]
        },
        "worker_capacity": 3000
    }
    
    checker = ComplianceChecker()
    report = checker.check_layout(layout)
    
    print(f"Overall Compliance: {report['overall_compliance_percent']}%")
    print(f"Status: {report['status']}")
    print(f"\nViolations ({len(report['violations'])}):")
    for v in report['violations']:
        print(f"  - {v}")
    print(f"\nRecommendations ({len(report['recommendations'])}):")
    for r in report['recommendations'][:5]:
        print(f"  - {r}")
