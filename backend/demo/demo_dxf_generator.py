"""
Demo DXF Generator - Extended version with terrain support

Extends the base DXFGenerator to support:
- Terrain layers (contours, spot elevations, cut/fill zones)
- Shapely geometry handling
- Platform elevations as extended data
- Demo-specific color coding
"""

import ezdxf
from typing import Dict, List
from shapely.geometry import Polygon, LineString, Point
import numpy as np

from cad.dxf_generator import DXFGenerator


class DemoDXFGenerator(DXFGenerator):
    """Extended DXF generator for demo system with terrain support"""
    
    def _draw_boundary(self, layout: Dict):
        """Draw site boundary - supports both dict and Shapely Polygon."""
        # Check if we have a Shapely polygon boundary
        site_boundary = layout.get('site_boundary')
        
        if site_boundary and isinstance(site_boundary, Polygon):
            # Extract coordinates from Shapely polygon
            coords = list(site_boundary.exterior.coords)
            
            self.msp.add_lwpolyline(
                coords,
                dxfattribs={
                    'layer': 'SITE_BOUNDARY',
                    'color': 7,  # White
                    'lineweight': 50
                },
                close=True
            )
        else:
            # Fallback to parent method
            super()._draw_boundary(layout)
    
    def _draw_buildings(self, layout: Dict):
        """Draw buildings with platform elevations and industry color coding."""
        buildings = layout.get('buildings', [])
        
        for building in buildings:
            # Handle both dict and Shapely geometry
            geometry = building.get('geometry')
            
            if geometry and isinstance(geometry, Polygon):
                # Extract coordinates from Shapely polygon
                coords = list(geometry.exterior.coords)
            else:
                # Fallback to x, y, width, height
                x = building.get('x', 0)
                y = building.get('y', 0)
                w = building.get('width', 50)
                h = building.get('height', 50)
                
                coords = [
                    (x, y),
                    (x + w, y),
                    (x + w, y + h),
                    (x, y + h),
                    (x, y)
                ]
            
            # Get industry type and color
            industry_type = building.get('industry_type', building.get('type', 'default'))
            color_hex = building.get('color', '#FFFFFF')
            
            # Map industry type to layer
            layer_map = {
                'light_manufacturing': 'LIGHT_MANUFACTURING',
                'logistics': 'LOGISTICS',
                'support': 'SUPPORT',
                'admin': 'ADMIN',
                'warehouse': 'WAREHOUSE'
            }
            
            layer = layer_map.get(industry_type, 'BUILDINGS')
            color = self.BUILDING_COLORS.get(industry_type, 256)
            
            # Draw building outline
            polyline = self.msp.add_lwpolyline(
                coords,
                dxfattribs={
                    'layer': layer,
                    'color': color,
                    'lineweight': 25
                },
                close=True
            )
            
            # Add extended data for platform elevation
            platform_elev = building.get('platform_elevation')
            # NOTE: XDATA disabled for AutoCAD compatibility
            # if platform_elev is not None:
            #     polyline.set_xdata('PLATFORM_ELEV', [(1040, platform_elev)])
            #     cut_vol = building.get('cut_volume_m3', 0)
            #     fill_vol = building.get('fill_volume_m3', 0)
            #     if cut_vol > 0 or fill_vol > 0:
            #         polyline.set_xdata('CUT_VOLUME', [(1040, cut_vol)])
            #         polyline.set_xdata('FILL_VOLUME', [(1040, fill_vol)])
            
            # Add solid hatch for fill
            hatch = self.msp.add_hatch(
                color=color,
                dxfattribs={'layer': layer}
            )
            hatch.paths.add_polyline_path(coords, is_closed=True)
            hatch.set_pattern_fill('SOLID')
            
            # Add building label with platform elevation
            label = building.get('label', building.get('id', f"Plot {building.get('id', '')}"))
            
            # Calculate centroid
            if geometry and isinstance(geometry, Polygon):
                centroid = geometry.centroid
                label_x, label_y = centroid.x, centroid.y
            else:
                label_x = coords[0][0] + (coords[2][0] - coords[0][0]) / 2
                label_y = coords[0][1] + (coords[2][1] - coords[0][1]) / 2
            
            # Add label with elevation
            if platform_elev is not None:
                label_text = f"{label}\nElev: {platform_elev:.1f}m"
            else:
                label_text = label
            
            self.msp.add_text(
                label_text,
                dxfattribs={
                    'height': 3,
                    'layer': 'LABELS',
                    'color': 0,  # Black
                    'style': 'Standard'
                }
            ).set_placement((label_x, label_y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    
    def _draw_roads(self, layout: Dict):
        """Draw road network from demo layout."""
        roads = layout.get('roads', [])
        
        if not roads:
            # Fallback to parent method
            super()._draw_roads(layout)
            return
        
        for road in roads:
            geometry = road.get('geometry')
            road_type = road.get('type', 'secondary')
            width = road.get('width', 12)
            grade = road.get('grade', 0)
            
            if not geometry or not isinstance(geometry, LineString):
                continue
            
            # Get coordinates
            coords = list(geometry.coords)
            
            # Determine layer
            layer = 'ROADS_MAIN' if road_type == 'main' else 'ROADS_SEC'
            color = 8 if road_type == 'main' else 9
            
            # Draw road as buffered line
            # Create perpendicular offsets for road width
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                
                # Calculate perpendicular vector
                dx = x2 - x1
                dy = y2 - y1
                length = (dx**2 + dy**2)**0.5
                
                if length == 0:
                    continue
                
                # Normalize and rotate 90 degrees
                px = -dy / length * (width / 2)
                py = dx / length * (width / 2)
                
                # Create road segment rectangle
                road_rect = [
                    (x1 + px, y1 + py),
                    (x2 + px, y2 + py),
                    (x2 - px, y2 - py),
                    (x1 - px, y1 - py),
                    (x1 + px, y1 + py)
                ]
                
                self.msp.add_lwpolyline(
                    road_rect,
                    dxfattribs={
                        'layer': layer,
                        'color': color,
                        'lineweight': 18
                    },
                    close=True
                )
            
            # Add grade label if significant
            if abs(grade) > 1.0:
                mid_point = geometry.interpolate(0.5, normalized=True)
                self.msp.add_text(
                    f"{grade:.1f}%",
                    dxfattribs={
                        'height': 2,
                        'layer': 'LABELS',
                        'color': 1 if grade > 8 else 7  # Red if over limit
                    }
                ).set_placement((mid_point.x, mid_point.y))
    
    def _draw_green_areas(self, layout: Dict):
        """Draw green space areas from demo layout."""
        green_areas = layout.get('green_areas', [])
        
        if not green_areas:
            # Fallback to parent method
            super()._draw_green_areas(layout)
            return
        
        for green in green_areas:
            geometry = green.get('geometry')
            
            if not geometry or not isinstance(geometry, Polygon):
                continue
            
            coords = list(geometry.exterior.coords)
            
            # Draw outline
            self.msp.add_lwpolyline(
                coords,
                dxfattribs={
                    'layer': 'GREEN_SPACE',
                    'color': 3,  # Green
                    'lineweight': 13
                },
                close=True
            )
            
            # Add hatch
            hatch = self.msp.add_hatch(
                color=3,
                dxfattribs={'layer': 'GREEN_SPACE'}
            )
            hatch.paths.add_polyline_path(coords, is_closed=True)
            hatch.set_pattern_fill('ANSI31')  # Diagonal lines
    
    def _draw_fire_stations(self, layout: Dict):
        """Draw fire station locations."""
        fire_stations = layout.get('fire_stations', [])
        
        for station in fire_stations:
            location = station.get('location')
            if not location:
                continue
            
            x, y = location[0], location[1]
            
            # Draw fire station as red square
            size = 15
            square = [
                (x - size/2, y - size/2),
                (x + size/2, y - size/2),
                (x + size/2, y + size/2),
                (x - size/2, y + size/2),
                (x - size/2, y - size/2)
            ]
            
            self.msp.add_lwpolyline(
                square,
                dxfattribs={
                    'layer': 'FIRE_STATIONS',
                    'color': 1,  # Red
                    'lineweight': 35
                },
                close=True
            )
            
            # Add solid hatch
            hatch = self.msp.add_hatch(
                color=1,
                dxfattribs={'layer': 'FIRE_STATIONS'}
            )
            hatch.paths.add_polyline_path(square, is_closed=True)
            hatch.set_pattern_fill('SOLID')
            
            # Add label
            self.msp.add_text(
                f"FS{station.get('id', '')}",
                dxfattribs={
                    'height': 3,
                    'layer': 'LABELS',
                    'color': 0  # Black
                }
            ).set_placement((x, y), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
            
            # Draw coverage radius
            coverage = station.get('coverage_radius', 150)
            self.msp.add_circle(
                (x, y),
                radius=coverage,
                dxfattribs={
                    'layer': 'FIRE_STATIONS',
                    'color': 1,
                    'linetype': 'DASHED'
                }
            )
    
    def _draw_terrain_layers(self, layout: Dict):
        """Draw terrain visualization layers."""
        terrain_data = layout.get('terrain_data')
        topography = layout.get('topography')
        
        if not terrain_data and not topography:
            return
        
        # Draw contours if available
        if topography:
            contour_lines = topography.get('contour_lines', [])
            for contour in contour_lines:
                elevation = contour.get('elevation')
                geometry = contour.get('geometry')
                
                if geometry and isinstance(geometry, LineString):
                    coords = list(geometry.coords)
                    
                    self.msp.add_lwpolyline(
                        coords,
                        dxfattribs={
                            'layer': 'CONTOURS',
                            'color': 30,  # Brown
                            'lineweight': 13
                        }
                    )
                    
                    # Add elevation label
                    if len(coords) > 2:
                        mid_point = geometry.interpolate(0.5, normalized=True)
                        self.msp.add_text(
                            f"{elevation:.1f}m",
                            dxfattribs={
                                'height': 2,
                                'layer': 'SPOT_ELEVATIONS',
                                'color': 30
                            }
                        ).set_placement((mid_point.x, mid_point.y))
            
            # Draw spot elevations
            elevation_points = topography.get('elevation_points', [])
            for i, point in enumerate(elevation_points[:100]):  # Limit to 100
                if len(point) >= 3:
                    x, y, z = point[0], point[1], point[2]
                    
                    # Draw point
                    self.msp.add_circle(
                        (x, y),
                        radius=1,
                        dxfattribs={
                            'layer': 'SPOT_ELEVATIONS',
                            'color': 5
                        }
                    )
                    
                    # Label every 10th point
                    if i % 10 == 0:
                        self.msp.add_text(
                            f"{z:.1f}",
                            dxfattribs={
                                'height': 1.5,
                                'layer': 'SPOT_ELEVATIONS',
                                'color': 5
                            }
                        ).set_placement((x + 2, y))
