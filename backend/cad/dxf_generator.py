"""
DXF Generator for Industrial Park Layouts.
Generates industry-standard DXF files compatible with AutoCAD.
"""

import ezdxf
from ezdxf import new
from ezdxf.addons import geo
from typing import Dict, List, Tuple, Optional
import math
import os
import numpy as np
from shapely.geometry import Polygon, LineString, Point


class DXFGenerator:
    """
    Generate industry-standard DXF files from layout objects.
    Output compatible with AutoCAD, CAD2Map, and other CAD software.
    """
    
    # Color mapping for building types (AutoCAD color index)
    BUILDING_COLORS = {
        'light_manufacturing': 3,      # Green (IEAT standard)
        'medium_manufacturing': 5,     # Magenta
        'heavy_manufacturing': 1,      # Red
        'warehouse': 2,                # Yellow
        'logistics': 5,                # Blue
        'support': 2,                  # Yellow
        'canteen': 7,                  # White
        'medical': 6,                  # Blue
        'parking': 8,                  # Gray
        'admin': 8,                    # Gray
        'green_space': 3,              # Green
        'default': 256                 # ByLayer
    }
    
    def __init__(self, output_dir: str = "exports"):
        self.doc = None
        self.msp = None
        self.output_dir = output_dir
        
        # Create output directory if not exists
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, layout: Dict, filename: str = None) -> str:
        """
        Generate DXF from layout.
        
        Args:
            layout: Design layout dictionary
            filename: Output DXF filename (without path)
            
        Returns:
            Path to generated DXF file
        """
        # Create new DXF document
        self.doc = new(dxfversion='R2010')
        self.msp = self.doc.modelspace()
        
        # Create layers
        self._create_layers()
        
        # 1. Draw site boundary
        self._draw_boundary(layout)
        
        # 2. Draw terrain data (if available)
        if layout.get('terrain_data'):
            self._draw_terrain_layers(layout)
        
        # 3. Draw buildings (colored by type)
        self._draw_buildings(layout)
        
        # 4. Draw road network
        self._draw_roads(layout)
        
        # 5. Draw green areas
        self._draw_green_areas(layout)
        
        # 6. Draw fire stations
        if layout.get('fire_stations'):
            self._draw_fire_stations(layout)
        
        # 7. Draw utilities
        self._draw_utilities(layout)
        
        # 8. Add annotations
        self._add_annotations(layout)
        
        # Generate filename if not provided
        if not filename:
            project_name = layout.get('name', 'industrial_park')
            variant_id = layout.get('variant_id', 'v1')
            filename = f"{project_name}_{variant_id}.dxf"
        
        # Ensure .dxf extension
        if not filename.endswith('.dxf'):
            filename += '.dxf'
        
        # Full path
        filepath = os.path.join(self.output_dir, filename)
        
        # Save
        self.doc.saveas(filepath)
        
        return filepath
    
    def _create_layers(self):
        """Create standard layers for the drawing."""
        layers = [
            # Standard layers
            ('SITE_BOUNDARY', 7),          # White
            ('BUILDINGS', 256),            # ByLayer
            ('LIGHT_MANUFACTURING', 3),    # Green
            ('MEDIUM_MANUFACTURING', 5),   # Magenta
            ('HEAVY_MANUFACTURING', 1),    # Red
            ('WAREHOUSE', 2),              # Yellow
            ('LOGISTICS', 5),              # Blue
            ('SUPPORT', 2),                # Yellow
            ('ADMIN', 8),                  # Gray
            ('AMENITIES', 6),              # Blue
            ('ROADS_MAIN', 8),             # Gray
            ('ROADS_SEC', 9),              # Light gray
            ('GREEN_SPACE', 3),            # Green
            ('FIRE_STATIONS', 1),          # Red
            ('UTILITIES', 4),              # Cyan
            ('LABELS', 7),                 # White
            ('INFO', 7),                   # White
            # Terrain layers
            ('CONTOURS', 30),              # Brown
            ('SPOT_ELEVATIONS', 5),        # Blue
            ('CUT_ZONES', 1),              # Red
            ('FILL_ZONES', 5),             # Blue
            ('GRADING_PLAN', 3),           # Green
        ]
        
        for layer_name, color in layers:
            self.doc.layers.add(layer_name, color=color)
    
    def _draw_boundary(self, layout: Dict):
        """Draw site boundary as polyline."""
        site = layout.get('site', {})
        width = site.get('width', 1000)
        height = site.get('height', 500)
        
        # Create boundary polygon
        boundary = [
            (0, 0),
            (width, 0),
            (width, height),
            (0, height),
            (0, 0)  # Close the polygon
        ]
        
        self.msp.add_lwpolyline(
            boundary,
            dxfattribs={
                'layer': 'SITE_BOUNDARY',
                'color': 7,  # White
                'lineweight': 50
            },
            close=True
        )
        
        # Draw buffer zone (50m from boundary)
        buffer = 50
        buffer_boundary = [
            (buffer, buffer),
            (width - buffer, buffer),
            (width - buffer, height - buffer),
            (buffer, height - buffer),
            (buffer, buffer)
        ]
        
        self.msp.add_lwpolyline(
            buffer_boundary,
            dxfattribs={
                'layer': 'GREEN_SPACE',
                'color': 3,  # Green
                'lineweight': 25,
                'linetype': 'DASHED'
            },
            close=True
        )
    
    def _draw_buildings(self, layout: Dict):
        """Draw buildings with color-coding by type."""
        buildings = layout.get('buildings', [])
        
        for building in buildings:
            btype = building.get('type', 'default')
            color = self.BUILDING_COLORS.get(btype, 256)
            
            # Determine layer
            layer = btype.upper() if btype.upper() in ['LIGHT_MANUFACTURING', 'MEDIUM_MANUFACTURING', 
                                                        'HEAVY_MANUFACTURING', 'WAREHOUSE', 'LOGISTICS'] else 'BUILDINGS'
            if btype in ['canteen', 'medical', 'admin', 'parking']:
                layer = 'AMENITIES'
            
            # Draw rectangle (building footprint)
            x = building.get('x', 0)
            y = building.get('y', 0)
            w = building.get('width', 50)
            h = building.get('height', 50)
            
            rectangle = [
                (x, y),
                (x + w, y),
                (x + w, y + h),
                (x, y + h),
                (x, y)
            ]
            
            # Draw building outline
            self.msp.add_lwpolyline(
                rectangle,
                dxfattribs={
                    'layer': layer,
                    'color': color,
                    'lineweight': 25
                },
                close=True
            )
            
            # Add solid hatch for fill (optional)
            hatch = self.msp.add_hatch(
                color=color,
                dxfattribs={'layer': layer}
            )
            hatch.paths.add_polyline_path(rectangle, is_closed=True)
            hatch.set_pattern_fill('SOLID')
            
            # Add building label
            label = building.get('label', building.get('id', 'Building'))
            label_x = x + w / 2
            label_y = y + h / 2
            
            # Calculate appropriate text height
            text_height = min(w, h) * 0.08
            text_height = max(2, min(text_height, 5))  # Between 2 and 5 meters
            
            self.msp.add_text(
                label,
                dxfattribs={
                    'height': text_height,
                    'layer': 'LABELS',
                    'color': 0,  # Black
                    'style': 'Standard'
                }
            ).set_placement((label_x, label_y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    
    def _draw_roads(self, layout: Dict):
        """Draw road network."""
        site = layout.get('site', {})
        buildings = layout.get('buildings', [])
        
        if not buildings:
            return
        
        # Generate simplified road network
        road_width = 15  # meters
        buffer = 50
        
        width = site.get('width', 1000)
        height = site.get('height', 500)
        
        # Main horizontal road through center
        main_road_y = height / 2
        self._draw_road_segment(
            (buffer, main_road_y - road_width/2),
            (width - buffer, main_road_y + road_width/2)
        )
        
        # Vertical roads connecting to perimeter
        for x_pos in [width * 0.25, width * 0.5, width * 0.75]:
            self._draw_road_segment(
                (x_pos - road_width/2, buffer),
                (x_pos + road_width/2, height - buffer)
            )
    
    def _draw_road_segment(self, start: Tuple[float, float], end: Tuple[float, float]):
        """Draw a road segment as a filled rectangle."""
        x1, y1 = start
        x2, y2 = end
        
        road_rect = [
            (x1, y1),
            (x2, y1),
            (x2, y2),
            (x1, y2),
            (x1, y1)
        ]
        
        self.msp.add_lwpolyline(
            road_rect,
            dxfattribs={
                'layer': 'ROADS',
                'color': 8,  # Gray
                'lineweight': 18
            },
            close=True
        )
    
    def _draw_green_areas(self, layout: Dict):
        """Draw green space areas."""
        site = layout.get('site', {})
        buffer = 50
        
        width = site.get('width', 1000)
        height = site.get('height', 500)
        
        # Buffer zones are already drawn as dashed lines in boundary
        # Add corner green areas
        corner_size = 80
        corners = [
            [(0, 0), (corner_size, 0), (corner_size, corner_size), (0, corner_size)],
            [(width - corner_size, 0), (width, 0), (width, corner_size), (width - corner_size, corner_size)],
            [(0, height - corner_size), (corner_size, height - corner_size), (corner_size, height), (0, height)],
            [(width - corner_size, height - corner_size), (width, height - corner_size), (width, height), (width - corner_size, height)]
        ]
        
        for corner in corners:
            corner.append(corner[0])  # Close
            hatch = self.msp.add_hatch(
                color=3,  # Green
                dxfattribs={'layer': 'GREEN_SPACE'}
            )
            hatch.paths.add_polyline_path(corner, is_closed=True)
            hatch.set_pattern_fill('GRASS')
    
    def _draw_utilities(self, layout: Dict):
        """Draw utility locations (power, water, wastewater)."""
        site = layout.get('site', {})
        width = site.get('width', 1000)
        height = site.get('height', 500)
        
        # Simplified utility placement
        utilities = [
            {'type': 'power', 'x': width * 0.1, 'y': height * 0.9, 'label': 'Power Substation'},
            {'type': 'water', 'x': width * 0.9, 'y': height * 0.9, 'label': 'Water Tank'},
            {'type': 'wastewater', 'x': width * 0.1, 'y': height * 0.1, 'label': 'Wastewater'},
        ]
        
        util_colors = {
            'power': 4,        # Cyan
            'water': 4,        # Cyan
            'wastewater': 3,   # Green
            'waste': 1         # Red
        }
        
        for util in utilities:
            color = util_colors.get(util['type'], 256)
            
            # Draw as circle
            self.msp.add_circle(
                (util['x'], util['y']),
                radius=10,
                dxfattribs={
                    'layer': 'UTILITIES',
                    'color': color
                }
            )
            
            # Add label
            self.msp.add_text(
                util['label'],
                dxfattribs={
                    'height': 3,
                    'layer': 'LABELS',
                    'color': color
                }
            ).set_placement((util['x'], util['y'] - 15), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    
    def _add_annotations(self, layout: Dict):
        """Add design statistics and notes."""
        site = layout.get('site', {})
        buildings = layout.get('buildings', [])
        
        width = site.get('width', 1000)
        height = site.get('height', 500)
        total_area_ha = site.get('total_area_m2', width * height) / 10000
        
        # Title block position (top-left)
        title_x = width * 0.02
        title_y = height * 0.98
        
        # Project title
        project_name = layout.get('name', 'Industrial Park Design')
        self.msp.add_text(
            project_name,
            dxfattribs={
                'height': 8,
                'layer': 'INFO',
                'color': 7
            }
        ).set_placement((title_x, title_y), align=ezdxf.enums.TextEntityAlignment.TOP_LEFT)
        
        # Statistics
        stats_lines = [
            f"Total Area: {total_area_ha:.1f} ha",
            f"Buildings: {len(buildings)}",
            f"Generated by: Industrial Park AI Designer"
        ]
        
        for i, line in enumerate(stats_lines):
            self.msp.add_text(
                line,
                dxfattribs={
                    'height': 4,
                    'layer': 'INFO',
                    'color': 7
                }
            ).set_placement((title_x, title_y - 15 - i * 8), align=ezdxf.enums.TextEntityAlignment.TOP_LEFT)
        
        # Legend
        legend_x = width * 0.85
        legend_y = height * 0.98
        
        self.msp.add_text(
            "LEGEND",
            dxfattribs={
                'height': 5,
                'layer': 'INFO',
                'color': 7
            }
        ).set_placement((legend_x, legend_y), align=ezdxf.enums.TextEntityAlignment.TOP_LEFT)
        
        legend_items = [
            ("Manufacturing", 1),
            ("Warehouse", 2),
            ("Logistics", 4),
            ("Amenities", 6),
            ("Green Space", 3),
            ("Roads", 8)
        ]
        
        for i, (label, color) in enumerate(legend_items):
            y_pos = legend_y - 10 - i * 6
            
            # Color box
            box_size = 4
            self.msp.add_lwpolyline(
                [
                    (legend_x, y_pos),
                    (legend_x + box_size, y_pos),
                    (legend_x + box_size, y_pos + box_size),
                    (legend_x, y_pos + box_size)
                ],
                dxfattribs={'layer': 'INFO', 'color': color},
                close=True
            )
            
            # Label
            self.msp.add_text(
                label,
                dxfattribs={
                    'height': 3,
                    'layer': 'INFO',
                    'color': 7
                }
            ).set_placement((legend_x + 8, y_pos + 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_LEFT)


# Quick test
if __name__ == "__main__":
    # Test layout
    layout = {
        "name": "Test Industrial Park",
        "variant_id": "v1",
        "buildings": [
            {"id": "b1", "type": "light_manufacturing", "x": 100, "y": 100, "width": 80, "height": 60, "label": "Factory 1"},
            {"id": "b2", "type": "warehouse", "x": 250, "y": 100, "width": 60, "height": 40, "label": "Warehouse 1"},
            {"id": "b3", "type": "logistics", "x": 400, "y": 100, "width": 100, "height": 80, "label": "Logistics Hub"},
            {"id": "b4", "type": "canteen", "x": 100, "y": 250, "width": 40, "height": 30, "label": "Canteen"},
        ],
        "site": {
            "width": 1000,
            "height": 500,
            "total_area_m2": 500000
        }
    }
    
    generator = DXFGenerator("./test_exports")
    filepath = generator.generate(layout)
    print(f"DXF generated: {filepath}")
