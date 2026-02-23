"""
Existing Features Integration Module

Integrates detected existing site features (ponds, buildings, roads, vegetation) 
into the design optimization process as constraints and reusable elements.

This module bridges the DXF feature detection and the design optimizer,
ensuring designs respect existing site conditions.
"""

from typing import Dict, List, Optional, Any, Tuple
from shapely.geometry import Polygon, LineString, Point, MultiPolygon, shape
from shapely.ops import unary_union
import logging

logger = logging.getLogger(__name__)


class ExistingFeaturesIntegrator:
    """
    Integrates existing site features into design constraints.
    
    Workflow:
    1. Load detected features from DXF (water, buildings, roads, vegetation)
    2. Load user reusability classifications (keep/reuse/demolish)
    3. Generate design constraints:
       - Exclusion zones (keep as-is features + buffers)
       - Preferred zones (reuse features - adapt existing)
       - Demolition zones (remove features)
    4. Pass constraints to lot generator and infrastructure placer
    """
    
    def __init__(self):
        self.constraints = {
            'exclusion_zones': [],  # Areas to avoid completely
            'preferred_zones': [],  # Areas to prioritize
            'existing_roads': [],   # Roads to align with
            'existing_ponds': [],   # Water bodies to preserve/expand
            'demolition_areas': [], # Features to remove
            'protected_trees': []   # Vegetation to buffer
        }
    
    def load_features(
        self,
        features: Dict[str, Any],
        reusability: Dict[str, List[str]]
    ) -> None:
        """
        Load detected features and reusability classifications.
        
        Args:
            features: Dict with water_bodies, buildings, roads, vegetation
            reusability: Dict with keep_as_is, reuse_modified, demolish lists
        """
        self._process_water_bodies(features.get('water_bodies', []), reusability)
        self._process_buildings(features.get('buildings', []), reusability)
        self._process_roads(features.get('roads', []), reusability)
        self._process_vegetation(features.get('vegetation', []), reusability)
        
        logger.info(
            f"Loaded constraints: "
            f"{len(self.constraints['exclusion_zones'])} exclusion zones, "
            f"{len(self.constraints['existing_roads'])} existing roads, "
            f"{len(self.constraints['existing_ponds'])} existing ponds"
        )
    
    def _process_water_bodies(
        self,
        water_bodies: List[Dict],
        reusability: Dict[str, List[str]]
    ) -> None:
        """Process water bodies based on reusability."""
        keep_as_is = set(reusability.get('keep_as_is', []))
        reuse_modified = set(reusability.get('reuse_modified', []))
        
        for wb in water_bodies:
            wb_id = wb['id']
            polygon = shape(wb['polygon']) if 'polygon' in wb else None
            
            if polygon is None:
                continue
            
            if wb_id in keep_as_is:
                # Keep as-is: Large pond, add 20m buffer exclusion zone
                buffer_zone = polygon.buffer(20)  # 20m buffer
                self.constraints['exclusion_zones'].append({
                    'geometry': buffer_zone,
                    'type': 'water_body',
                    'id': wb_id,
                    'reason': 'Large water body preserved (expensive to fill)',
                    'cost_to_remove': wb['area_m2'] * 100  # 100 THB/m²
                })
                
                # Store for infrastructure optimization
                self.constraints['existing_ponds'].append({
                    'geometry': polygon,
                    'id': wb_id,
                    'area_m2': wb['area_m2'],
                    'can_expand': False  # Keep exact size
                })
                
            elif wb_id in reuse_modified:
                # Reuse/modify: Small pond, can expand as retention pond
                self.constraints['existing_ponds'].append({
                    'geometry': polygon,
                    'id': wb_id,
                    'area_m2': wb['area_m2'],
                    'can_expand': True,  # Can expand for retention
                    'expansion_capacity_m3': wb['area_m2'] * 2  # 2m depth
                })
            
            # Demolish: Will be filled, no constraints
    
    def _process_buildings(
        self,
        buildings: List[Dict],
        reusability: Dict[str, List[str]]
    ) -> None:
        """Process buildings based on reusability."""
        keep_as_is = set(reusability.get('keep_as_is', []))
        reuse_modified = set(reusability.get('reuse_modified', []))
        demolish = set(reusability.get('demolish', []))
        
        for b in buildings:
            b_id = b['id']
            polygon = shape(b['polygon']) if 'polygon' in b else None
            
            if polygon is None:
                continue
            
            if b_id in keep_as_is or b_id in reuse_modified:
                # Keep/reuse: Add as exclusion zone, but note as reusable
                self.constraints['exclusion_zones'].append({
                    'geometry': polygon.buffer(5),  # 5m buffer
                    'type': 'building',
                    'id': b_id,
                    'reason': 'Existing building reusable',
                    'reusable': True,
                    'area_m2': b['area_m2'],
                    'is_rectangular': b.get('is_rectangular', False)
                })
                
                # If rectangular and large, suggest as admin building
                if b.get('is_rectangular') and b['area_m2'] > 2000:
                    self.constraints['preferred_zones'].append({
                        'geometry': polygon,
                        'type': 'admin_building',
                        'id': b_id,
                        'suggestion': 'Convert to admin/office building'
                    })
            
            elif b_id in demolish:
                # Demolish: Mark area, but no constraints
                self.constraints['demolition_areas'].append({
                    'geometry': polygon,
                    'type': 'building',
                    'id': b_id,
                    'area_m2': b['area_m2']
                })
    
    def _process_roads(
        self,
        roads: List[Dict],
        reusability: Dict[str, List[str]]
    ) -> None:
        """Process existing roads for alignment."""
        reuse_modified = set(reusability.get('reuse_modified', []))
        
        for r in roads:
            r_id = r['id']
            
            if r_id in reuse_modified:
                # Reuse road: Store alignment for new road network
                linestring = shape(r['linestring']) if 'linestring' in r else None
                
                if linestring and r['length_m'] > 100:  # Only significant roads
                    self.constraints['existing_roads'].append({
                        'geometry': linestring,
                        'id': r_id,
                        'length_m': r['length_m'],
                        'alignment': self._extract_alignment(linestring),
                        'width_m': 12,  # Assume standard width, can upgrade
                        'can_widen': True
                    })
    
    def _process_vegetation(
        self,
        vegetation: List[Dict],
        reusability: Dict[str, List[str]]
    ) -> None:
        """Process significant vegetation for protection."""
        keep_as_is = set(reusability.get('keep_as_is', []))
        
        for v in vegetation:
            v_id = v['id']
            
            if v_id in keep_as_is and v.get('significant', False):
                # Significant tree: Add 15m buffer protection zone
                polygon = shape(v['polygon']) if 'polygon' in v else None
                
                if polygon:
                    buffer_zone = polygon.buffer(15)  # 15m protection buffer
                    
                    self.constraints['exclusion_zones'].append({
                        'geometry': buffer_zone,
                        'type': 'protected_vegetation',
                        'id': v_id,
                        'reason': 'Significant tree protected',
                        'radius_m': v.get('radius_m', 5)
                    })
                    
                    self.constraints['protected_trees'].append({
                        'geometry': polygon,
                        'id': v_id,
                        'radius_m': v.get('radius_m', 5)
                    })
    
    def _extract_alignment(self, linestring: LineString) -> Dict[str, Any]:
        """Extract alignment parameters from existing road."""
        coords = list(linestring.coords)
        
        if len(coords) < 2:
            return {}
        
        # Calculate bearing (direction)
        import math
        dx = coords[-1][0] - coords[0][0]
        dy = coords[-1][1] - coords[0][1]
        bearing = math.atan2(dy, dx) * 180 / math.pi
        
        return {
            'start': coords[0],
            'end': coords[-1],
            'bearing': bearing,
            'waypoints': coords
        }
    
    def get_lot_placement_constraints(self) -> Dict[str, Any]:
        """
        Get constraints for lot placement algorithm.
        
        Returns:
            Dict with:
            - exclusion_polygons: Polygons to avoid
            - preferred_polygons: Polygons to prioritize
            - alignment_guides: Road alignments to follow
        """
        # Merge all exclusion zones into multipolygon
        exclusion_geoms = [c['geometry'] for c in self.constraints['exclusion_zones']]
        
        if exclusion_geoms:
            exclusion_union = unary_union(exclusion_geoms)
        else:
            exclusion_union = Polygon()
        
        return {
            'exclusion_polygons': exclusion_union,
            'preferred_polygons': [
                c['geometry'] for c in self.constraints['preferred_zones']
            ],
            'alignment_guides': [
                c['alignment'] for c in self.constraints['existing_roads']
            ],
            'buffer_zones': exclusion_geoms,  # Individual zones
            'total_excluded_area_m2': exclusion_union.area if exclusion_geoms else 0
        }
    
    def get_infrastructure_constraints(self) -> Dict[str, Any]:
        """
        Get constraints for infrastructure placement.
        
        Returns:
            Dict with:
            - existing_ponds: Ponds to reuse/expand
            - existing_roads: Roads to align with
            - protected_areas: Areas to avoid
        """
        return {
            'existing_ponds': self.constraints['existing_ponds'],
            'existing_roads': self.constraints['existing_roads'],
            'protected_trees': self.constraints['protected_trees'],
            'exclusion_zones': self.constraints['exclusion_zones']
        }
    
    def calculate_cost_savings(self) -> Dict[str, float]:
        """
        Calculate cost savings from reusing existing features.
        
        Returns:
            Dict with savings breakdown in THB
        """
        savings = {
            'ponds_preserved': 0,
            'roads_reused': 0,
            'buildings_adapted': 0,
            'total_savings': 0
        }
        
        # Pond preservation savings
        for pond in self.constraints['existing_ponds']:
            if not pond.get('can_expand', True):  # Keep as-is
                area_m2 = pond['area_m2']
                savings['ponds_preserved'] += area_m2 * 100  # 100 THB/m² to fill
        
        # Road reuse savings
        for road in self.constraints['existing_roads']:
            length_m = road['length_m']
            width_m = road.get('width_m', 12)
            area_m2 = length_m * width_m
            # Savings: Avoid full reconstruction, only upgrade
            savings['roads_reused'] += area_m2 * 800  # 800 THB/m² construction cost
        
        # Building adaptation savings
        for zone in self.constraints['exclusion_zones']:
            if zone['type'] == 'building' and zone.get('reusable', False):
                area_m2 = zone['area_m2']
                # Savings: Renovation vs. demolish + rebuild
                demolish_cost = area_m2 * 1500
                rebuild_cost = area_m2 * 5000
                renovation_cost = area_m2 * 3000
                savings['buildings_adapted'] += (demolish_cost + rebuild_cost) - renovation_cost
        
        savings['total_savings'] = sum(
            v for k, v in savings.items() if k != 'total_savings'
        )
        
        return savings
    
    def generate_design_report(self) -> str:
        """
        Generate human-readable report of existing features integration.
        
        Returns:
            Markdown-formatted report
        """
        report_lines = [
            "# Existing Features Integration Report\n",
            "## Summary\n",
            f"- **Exclusion Zones**: {len(self.constraints['exclusion_zones'])} areas",
            f"- **Existing Ponds**: {len(self.constraints['existing_ponds'])} water bodies",
            f"- **Existing Roads**: {len(self.constraints['existing_roads'])} road segments",
            f"- **Protected Trees**: {len(self.constraints['protected_trees'])} significant trees\n",
            "## Cost Savings\n"
        ]
        
        savings = self.calculate_cost_savings()
        report_lines.extend([
            f"- **Ponds Preserved**: ฿{savings['ponds_preserved']:,.0f}",
            f"- **Roads Reused**: ฿{savings['roads_reused']:,.0f}",
            f"- **Buildings Adapted**: ฿{savings['buildings_adapted']:,.0f}",
            f"- **Total Savings**: ฿{savings['total_savings']:,.0f}\n",
            "## Constraints Details\n"
        ])
        
        # Exclusion zones
        if self.constraints['exclusion_zones']:
            report_lines.append("### Exclusion Zones\n")
            for zone in self.constraints['exclusion_zones']:
                report_lines.append(
                    f"- **{zone['type']}** ({zone['id'][:8]}...): {zone['reason']}"
                )
            report_lines.append("")
        
        # Existing ponds
        if self.constraints['existing_ponds']:
            report_lines.append("### Existing Water Bodies\n")
            for pond in self.constraints['existing_ponds']:
                expandable = "Can expand" if pond.get('can_expand') else "Keep exact size"
                area_rai = pond['area_m2'] / 1600
                report_lines.append(
                    f"- **Pond {pond['id'][:8]}...**: {area_rai:.2f} rai - {expandable}"
                )
            report_lines.append("")
        
        # Existing roads
        if self.constraints['existing_roads']:
            report_lines.append("### Existing Road Network\n")
            for road in self.constraints['existing_roads']:
                report_lines.append(
                    f"- **Road {road['id'][:8]}...**: {road['length_m']:.0f}m - Align new roads with existing"
                )
            report_lines.append("")
        
        return "\n".join(report_lines)


# Helper function to integrate with design optimizer
def apply_existing_features_constraints(
    design_params: Dict[str, Any],
    features: Dict[str, Any],
    reusability: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Apply existing features as constraints to design parameters.
    
    Usage:
        features = fetch_from_dxf_api(file_id)
        reusability = fetch_reusability(file_id)
        
        updated_params = apply_existing_features_constraints(
            design_params, features, reusability
        )
        
        layout = generator.generate_comprehensive_layout(
            updated_params, site_boundary
        )
    
    Args:
        design_params: Original design parameters from AI chat
        features: Detected features from DXF
        reusability: User classifications
    
    Returns:
        Updated design parameters with constraints
    """
    integrator = ExistingFeaturesIntegrator()
    integrator.load_features(features, reusability)
    
    # Add constraints to design params
    design_params['existing_features'] = {
        'lot_constraints': integrator.get_lot_placement_constraints(),
        'infrastructure_constraints': integrator.get_infrastructure_constraints(),
        'cost_savings': integrator.calculate_cost_savings(),
        'report': integrator.generate_design_report()
    }
    
    return design_params


# Export
__all__ = [
    'ExistingFeaturesIntegrator',
    'apply_existing_features_constraints'
]
