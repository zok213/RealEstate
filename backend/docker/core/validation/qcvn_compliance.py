"""
QCVN Compliance Validation Module

Validates industrial estate design against QCVN 01:2021/BXD requirements:
- Land use ratios (roads, green space, infrastructure)
- Building density & green space in lots
- Parking requirements
- Environmental buffer zones
"""

from typing import Dict, List, Tuple, Any
from shapely.geometry import shape, Polygon
from dataclasses import dataclass
from core.config.settings import AlgorithmSettings


@dataclass
class ComplianceReport:
    """QCVN compliance validation report."""
    
    # Land use percentages
    total_area: float
    road_area: float
    road_ratio: float
    green_area: float
    green_ratio: float
    water_area: float
    water_ratio: float
    infrastructure_area: float
    infrastructure_ratio: float
    lot_area: float
    lot_ratio: float
    
    # Compliance status
    road_compliant: bool
    green_compliant: bool
    infrastructure_compliant: bool
    
    # Warnings and errors
    warnings: List[str]
    errors: List[str]
    
    def is_compliant(self) -> bool:
        """Check if design is fully compliant with QCVN."""
        return len(self.errors) == 0 and self.road_compliant and self.green_compliant and self.infrastructure_compliant
    
    def get_summary(self) -> str:
        """Get human-readable compliance summary."""
        lines = [
            "=" * 60,
            "QCVN 01:2021/BXD COMPLIANCE REPORT",
            "=" * 60,
            "",
            "LAND USE BREAKDOWN:",
            f"  Total Area:         {self.total_area:>12,.0f} m² (100.00%)",
            f"  Roads:              {self.road_area:>12,.0f} m² ({self.road_ratio*100:>5.2f}%) {'✅ PASS' if self.road_compliant else '❌ FAIL'}",
            f"  Green Space:        {self.green_area:>12,.0f} m² ({self.green_ratio*100:>5.2f}%) {'✅ PASS' if self.green_compliant else '❌ FAIL'}",
            f"  Water:              {self.water_area:>12,.0f} m² ({self.water_ratio*100:>5.2f}%)",
            f"  Infrastructure:     {self.infrastructure_area:>12,.0f} m² ({self.infrastructure_ratio*100:>5.2f}%) {'✅ PASS' if self.infrastructure_compliant else '❌ FAIL'}",
            f"  Lots (Build):       {self.lot_area:>12,.0f} m² ({self.lot_ratio*100:>5.2f}%)",
            "",
            "QCVN REQUIREMENTS:",
            f"  Roads:              15-20% (khuyến nghị)",
            f"  Green + Water:      7-15% (khuyến nghị)",
            f"  Infrastructure:     1-3% (khuyến nghị)",
            f"  Lots (Build):       50-70% (giới hạn)",
            "",
        ]
        
        if self.warnings:
            lines.append("⚠️ WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")
        
        if self.errors:
            lines.append("❌ ERRORS:")
            for error in self.errors:
                lines.append(f"  - {error}")
            lines.append("")
        
        if self.is_compliant():
            lines.append("✅ DESIGN IS FULLY COMPLIANT WITH QCVN 01:2021/BXD")
        else:
            lines.append("❌ DESIGN DOES NOT MEET QCVN REQUIREMENTS")
        
        lines.append("=" * 60)
        
        return "\n".join(lines)


def validate_land_use(
    features: List[Dict[str, Any]],
    site_boundary: Polygon,
    settings: AlgorithmSettings
) -> ComplianceReport:
    """
    Validate land use against QCVN 01:2021/BXD requirements.
    
    Args:
        features: GeoJSON features from final_layout
        site_boundary: Site boundary polygon
        settings: Algorithm settings with validation thresholds
        
    Returns:
        ComplianceReport with detailed breakdown
    """
    total_area = site_boundary.area
    
    # Initialize counters
    road_area = 0.0
    green_area = 0.0
    water_area = 0.0
    infrastructure_area = 0.0
    lot_area = 0.0
    
    # Sum up areas by type
    for feature in features:
        props = feature.get('properties', {})
        ftype = props.get('type', '')
        geom = shape(feature['geometry'])
        area = geom.area
        
        if ftype == 'road_network':
            road_area += area
        elif ftype == 'park':
            green_area += area
        elif ftype == 'water':
            water_area += area
        elif ftype in ['transformer', 'xlnt', 'service']:
            infrastructure_area += area
        elif ftype == 'lot':
            lot_area += area
    
    # Calculate ratios
    road_ratio = road_area / total_area if total_area > 0 else 0
    green_ratio = green_area / total_area if total_area > 0 else 0
    water_ratio = water_area / total_area if total_area > 0 else 0
    green_water_ratio = (green_area + water_area) / total_area if total_area > 0 else 0
    infrastructure_ratio = infrastructure_area / total_area if total_area > 0 else 0
    lot_ratio = lot_area / total_area if total_area > 0 else 0
    
    # Check compliance
    val = settings.validation
    warnings = []
    errors = []
    
    # Roads: 15-20%
    road_compliant = road_ratio >= val.min_road_ratio
    if not road_compliant:
        errors.append(f"Roads {road_ratio*100:.1f}% < minimum {val.min_road_ratio*100:.0f}% (QCVN requires 15-20%)")
    elif road_ratio > 0.20:
        warnings.append(f"Roads {road_ratio*100:.1f}% exceeds 20% - too much road area")
    elif road_ratio < val.target_road_ratio:
        warnings.append(f"Roads {road_ratio*100:.1f}% below recommended {val.target_road_ratio*100:.0f}%")
    
    # Green space + water: 7-15%
    green_compliant = green_water_ratio >= val.min_green_ratio
    if not green_compliant:
        errors.append(f"Green+Water {green_water_ratio*100:.1f}% < minimum {val.min_green_ratio*100:.0f}% (QCVN requires 7-15%)")
    elif green_water_ratio > 0.15:
        warnings.append(f"Green+Water {green_water_ratio*100:.1f}% exceeds 15%")
    elif green_water_ratio < val.target_green_ratio:
        warnings.append(f"Green+Water {green_water_ratio*100:.1f}% below recommended {val.target_green_ratio*100:.0f}%")
    
    # Infrastructure: 1-3%
    infrastructure_compliant = infrastructure_ratio >= val.min_infrastructure_ratio
    if not infrastructure_compliant:
        errors.append(f"Infrastructure {infrastructure_ratio*100:.1f}% < minimum {val.min_infrastructure_ratio*100:.0f}% (QCVN requires 1-3%)")
    elif infrastructure_ratio > 0.03:
        warnings.append(f"Infrastructure {infrastructure_ratio*100:.1f}% exceeds 3%")
    elif infrastructure_ratio < val.target_infra_ratio:
        warnings.append(f"Infrastructure {infrastructure_ratio*100:.1f}% below recommended {val.target_infra_ratio*100:.0f}%")
    
    # Lots: 50-70%
    if lot_ratio > 0.70:
        errors.append(f"Lots {lot_ratio*100:.1f}% exceeds maximum 70% (QCVN requires 50-70%)")
    elif lot_ratio < 0.50:
        warnings.append(f"Lots {lot_ratio*100:.1f}% below minimum 50%")
    
    return ComplianceReport(
        total_area=total_area,
        road_area=road_area,
        road_ratio=road_ratio,
        green_area=green_area,
        green_ratio=green_ratio,
        water_area=water_area,
        water_ratio=water_ratio,
        infrastructure_area=infrastructure_area,
        infrastructure_ratio=infrastructure_ratio,
        lot_area=lot_area,
        lot_ratio=lot_ratio,
        road_compliant=road_compliant,
        green_compliant=green_compliant,
        infrastructure_compliant=infrastructure_compliant,
        warnings=warnings,
        errors=errors
    )


def calculate_parking_requirements(
    lot_area: float,
    lot_type: str,
    settings: AlgorithmSettings
) -> Dict[str, int]:
    """
    Calculate parking requirements for a lot.
    
    Args:
        lot_area: Lot area in m²
        lot_type: 'FACTORY', 'WAREHOUSE', or 'SERVICE'
        settings: Algorithm settings
        
    Returns:
        Dict with car_spaces, motorcycle_spaces, bicycle_spaces, total_area
    """
    # Parking ratios by lot type (spaces per 1000 m²)
    PARKING_RATIOS = {
        'FACTORY': {'car': 2, 'motorcycle': 8, 'bicycle': 10},
        'WAREHOUSE': {'car': 1.5, 'motorcycle': 6, 'bicycle': 8},
        'SERVICE': {'car': 3, 'motorcycle': 10, 'bicycle': 12},
    }
    
    ratio = PARKING_RATIOS.get(lot_type, PARKING_RATIOS['FACTORY'])
    area_1000 = lot_area / 1000.0
    
    car_spaces = int(ratio['car'] * area_1000)
    motorcycle_spaces = int(ratio['motorcycle'] * area_1000)
    bicycle_spaces = int(ratio['bicycle'] * area_1000)
    
    # Calculate total parking area
    total_parking_area = (
        car_spaces * settings.subdivision.parking_car_area +
        motorcycle_spaces * settings.subdivision.parking_motorcycle_area +
        bicycle_spaces * settings.subdivision.parking_bicycle_area
    )
    
    return {
        'car_spaces': car_spaces,
        'motorcycle_spaces': motorcycle_spaces,
        'bicycle_spaces': bicycle_spaces,
        'total_area': total_parking_area,
        'ratio': total_parking_area / lot_area if lot_area > 0 else 0
    }


def validate_lot_density(
    lot_geom: Polygon,
    lot_type: str,
    settings: AlgorithmSettings
) -> Dict[str, Any]:
    """
    Validate building density and green space in a lot.
    
    Args:
        lot_geom: Lot polygon
        lot_type: Lot type/zone
        settings: Algorithm settings
        
    Returns:
        Dict with max_building_area, min_green_area, parking, compliant
    """
    lot_area = lot_geom.area
    
    # Maximum building coverage (70%)
    max_building_area = lot_area * settings.subdivision.max_building_coverage
    
    # Minimum green space (20%)
    min_green_area = lot_area * settings.subdivision.min_green_in_lot
    
    # Parking requirements
    parking = calculate_parking_requirements(lot_area, lot_type, settings)
    
    # Check if parking + green + building fits
    available_for_building = lot_area - min_green_area - parking['total_area']
    building_compliant = available_for_building >= (lot_area * 0.30)  # At least 30% for building
    
    return {
        'lot_area': lot_area,
        'max_building_area': max_building_area,
        'max_building_ratio': settings.subdivision.max_building_coverage,
        'min_green_area': min_green_area,
        'min_green_ratio': settings.subdivision.min_green_in_lot,
        'parking': parking,
        'available_for_building': available_for_building,
        'compliant': building_compliant,
        'warning': None if building_compliant else f"Parking area {parking['ratio']*100:.1f}% too large"
    }
