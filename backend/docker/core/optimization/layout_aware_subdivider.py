"""
Layout-Aware Subdivider

Thuật toán chia plots thông minh dựa trên các pattern layout thực tế:
1. Fishbone Pattern - Xương cá (lots dọc 2 bên đường chính)
2. Herringbone Pattern - Chữ nhân (lots góc nghiêng)
3. Perimeter Pattern - Viền ngoài (lots dọc biên)
4. Grid Pattern - Lưới (lots vuông góc)
5. Cul-de-sac - Đường chết (tối đa frontage)

Mục tiêu: Maximize road frontage, minimize dead space, optimize access
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from shapely.geometry import Polygon, LineString, Point, MultiLineString
from shapely.ops import unary_union, split, linemerge
from shapely.affinity import rotate as rotate_geom, translate
import numpy as np
import math

logger = logging.getLogger(__name__)


class LayoutPattern:
    """Các pattern layout chuẩn cho industrial estates"""
    
    FISHBONE = "fishbone"          # Xương cá - most efficient
    HERRINGBONE = "herringbone"    # Chữ nhân - for wide blocks
    PERIMETER = "perimeter"        # Viền - for irregular shapes
    GRID = "grid"                  # Lưới - simple, regular
    CUL_DE_SAC = "cul_de_sac"     # Đường chết - maximize frontage


class LayoutAnalyzer:
    """Phân tích block để chọn pattern phù hợp"""
    
    @staticmethod
    def analyze_block_geometry(block: Polygon) -> Dict[str, Any]:
        """
        Phân tích hình dạng block để đề xuất pattern
        
        Returns:
            Dict with 'shape_type', 'dimensions', 'recommended_pattern'
        """
        # Get OBB dimensions
        obb = block.minimum_rotated_rectangle
        coords = list(obb.exterior.coords[:-1])
        
        if len(coords) < 4:
            return {
                'shape_type': 'irregular',
                'recommended_pattern': LayoutPattern.PERIMETER
            }
        
        # Calculate dimensions
        side1 = Point(coords[0]).distance(Point(coords[1]))
        side2 = Point(coords[1]).distance(Point(coords[2]))
        
        width = min(side1, side2)
        length = max(side1, side2)
        aspect = length / width if width > 0 else 1.0
        
        # Calculate shape regularity
        rectangularity = block.area / obb.area if obb.area > 0 else 0
        
        # Determine shape type and recommend pattern
        if rectangularity > 0.9:
            # Regular rectangular block
            if aspect > 4.0:
                # Very elongated - fishbone is best
                shape_type = 'elongated_rectangle'
                pattern = LayoutPattern.FISHBONE
            elif aspect > 2.5:
                # Moderately elongated - fishbone or herringbone
                shape_type = 'rectangle'
                pattern = LayoutPattern.FISHBONE
            else:
                # Square-ish - grid works well
                shape_type = 'square'
                pattern = LayoutPattern.GRID
        else:
            # Irregular shape - use perimeter
            shape_type = 'irregular'
            pattern = LayoutPattern.PERIMETER
        
        return {
            'shape_type': shape_type,
            'width': width,
            'length': length,
            'aspect_ratio': aspect,
            'rectangularity': rectangularity,
            'recommended_pattern': pattern
        }
    
    @staticmethod
    def get_primary_axis(block: Polygon) -> LineString:
        """
        Tìm trục chính của block (đường dài nhất)
        """
        obb = block.minimum_rotated_rectangle
        coords = list(obb.exterior.coords[:-1])
        
        if len(coords) < 4:
            # Fallback to centroid axis
            centroid = block.centroid
            bounds = block.bounds
            return LineString([
                (bounds[0], centroid.y),
                (bounds[2], centroid.y)
            ])
        
        # Find longest side
        sides = []
        for i in range(4):
            p1 = Point(coords[i])
            p2 = Point(coords[(i+1) % 4])
            length = p1.distance(p2)
            sides.append((length, p1, p2))
        
        # Sort by length (first element of tuple)
        sides.sort(key=lambda x: x[0], reverse=True)
        longest = sides[0]
        
        # Create axis through longest side
        return LineString([longest[1], longest[2]])


class FishboneSubdivider:
    """
    Fishbone Pattern Subdivider
    
    Layout: Đường chính chạy giữa, lots xếp 2 bên như xương cá
    - Most efficient use of space
    - Maximum frontage for lots
    - Best for elongated blocks
    """
    
    @staticmethod
    def subdivide(
        block: Polygon,
        zone_type: str,
        target_lot_width: float = 20.0,
        target_lot_depth: float = 40.0,
        spine_road_width: float = 12.0
    ) -> List[Dict[str, Any]]:
        """
        Create fishbone layout
        
        Args:
            block: Block polygon
            zone_type: Zone type
            target_lot_width: Lot width along road
            target_lot_depth: Lot depth perpendicular to road
            spine_road_width: Width of spine road
            
        Returns:
            List of lot dicts
        """
        logger.info(f"[FISHBONE] Creating fishbone layout for {block.area:.0f}m² block")
        
        # Get primary axis (spine road)
        axis = LayoutAnalyzer.get_primary_axis(block)
        
        # Get block bounds and orientation
        bounds = block.bounds
        minx, miny, maxx, maxy = bounds
        width = maxx - minx
        height = maxy - miny
        
        lots = []
        lot_id = 1
        
        # Determine if horizontal or vertical layout
        if width > height:
            # Horizontal spine
            spine_y = (miny + maxy) / 2
            
            # Create lots above spine (north side)
            current_x = minx
            while current_x < maxx:
                lot_width = min(target_lot_width, maxx - current_x)
                lot_depth = min(target_lot_depth, spine_y - miny - spine_road_width/2)
                
                if lot_depth < 15.0:  # Too shallow
                    break
                
                # Create lot
                lot_box = Polygon([
                    (current_x, spine_y + spine_road_width/2),
                    (current_x + lot_width, spine_y + spine_road_width/2),
                    (current_x + lot_width, spine_y + spine_road_width/2 + lot_depth),
                    (current_x, spine_y + spine_road_width/2 + lot_depth)
                ])
                
                # Clip to block
                lot_clipped = lot_box.intersection(block)
                
                if (not lot_clipped.is_empty and 
                    lot_clipped.geom_type == 'Polygon' and
                    lot_clipped.area > 200):
                    
                    lots.append({
                        'id': lot_id,
                        'geometry': lot_clipped,
                        'zone': zone_type,
                        'area': lot_clipped.area,
                        'width': lot_width,
                        'depth': lot_depth,
                        'side': 'north'
                    })
                    lot_id += 1
                
                current_x += lot_width
            
            # Create lots below spine (south side)
            current_x = minx
            while current_x < maxx:
                lot_width = min(target_lot_width, maxx - current_x)
                lot_depth = min(target_lot_depth, spine_y - miny - spine_road_width/2)
                
                if lot_depth < 15.0:
                    break
                
                lot_box = Polygon([
                    (current_x, spine_y - spine_road_width/2 - lot_depth),
                    (current_x + lot_width, spine_y - spine_road_width/2 - lot_depth),
                    (current_x + lot_width, spine_y - spine_road_width/2),
                    (current_x, spine_y - spine_road_width/2)
                ])
                
                lot_clipped = lot_box.intersection(block)
                
                if (not lot_clipped.is_empty and 
                    lot_clipped.geom_type == 'Polygon' and
                    lot_clipped.area > 200):
                    
                    lots.append({
                        'id': lot_id,
                        'geometry': lot_clipped,
                        'zone': zone_type,
                        'area': lot_clipped.area,
                        'width': lot_width,
                        'depth': lot_depth,
                        'side': 'south'
                    })
                    lot_id += 1
                
                current_x += lot_width
        
        else:
            # Vertical spine
            spine_x = (minx + maxx) / 2
            
            # Similar logic for vertical orientation
            # Create lots on east side
            current_y = miny
            while current_y < maxy:
                lot_width = min(target_lot_width, maxy - current_y)
                lot_depth = min(target_lot_depth, maxx - spine_x - spine_road_width/2)
                
                if lot_depth < 15.0:
                    break
                
                lot_box = Polygon([
                    (spine_x + spine_road_width/2, current_y),
                    (spine_x + spine_road_width/2 + lot_depth, current_y),
                    (spine_x + spine_road_width/2 + lot_depth, current_y + lot_width),
                    (spine_x + spine_road_width/2, current_y + lot_width)
                ])
                
                lot_clipped = lot_box.intersection(block)
                
                if (not lot_clipped.is_empty and 
                    lot_clipped.geom_type == 'Polygon' and
                    lot_clipped.area > 200):
                    
                    lots.append({
                        'id': lot_id,
                        'geometry': lot_clipped,
                        'zone': zone_type,
                        'area': lot_clipped.area,
                        'width': lot_width,
                        'depth': lot_depth,
                        'side': 'east'
                    })
                    lot_id += 1
                
                current_y += lot_width
            
            # Create lots on west side
            current_y = miny
            while current_y < maxy:
                lot_width = min(target_lot_width, maxy - current_y)
                lot_depth = min(target_lot_depth, spine_x - minx - spine_road_width/2)
                
                if lot_depth < 15.0:
                    break
                
                lot_box = Polygon([
                    (spine_x - spine_road_width/2 - lot_depth, current_y),
                    (spine_x - spine_road_width/2, current_y),
                    (spine_x - spine_road_width/2, current_y + lot_width),
                    (spine_x - spine_road_width/2 - lot_depth, current_y + lot_width)
                ])
                
                lot_clipped = lot_box.intersection(block)
                
                if (not lot_clipped.is_empty and 
                    lot_clipped.geom_type == 'Polygon' and
                    lot_clipped.area > 200):
                    
                    lots.append({
                        'id': lot_id,
                        'geometry': lot_clipped,
                        'zone': zone_type,
                        'area': lot_clipped.area,
                        'width': lot_width,
                        'depth': lot_depth,
                        'side': 'west'
                    })
                    lot_id += 1
                
                current_y += lot_width
        
        logger.info(f"[FISHBONE] ✓ Created {len(lots)} lots in fishbone pattern")
        return lots


class LayoutAwareSubdivider:
    """
    Main subdivider that intelligently selects and applies layout pattern
    """
    
    def __init__(
        self,
        min_lot_area: float = 500.0,
        target_lot_width: float = 20.0,
        target_lot_depth: float = 40.0
    ):
        self.min_lot_area = min_lot_area
        self.target_lot_width = target_lot_width
        self.target_lot_depth = target_lot_depth
    
    def subdivide_block(
        self,
        block: Polygon,
        zone_type: str = 'FACTORY',
        force_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Subdivide block using best layout pattern
        
        Args:
            block: Block polygon
            zone_type: Zone type
            force_pattern: Force specific pattern (optional)
            
        Returns:
            List of optimized lots
        """
        # Analyze block
        analysis = LayoutAnalyzer.analyze_block_geometry(block)
        
        # Choose pattern
        if force_pattern:
            pattern = force_pattern
        else:
            pattern = analysis['recommended_pattern']
        
        logger.info(
            f"[LAYOUT SUBDIVIDER] Block {block.area:.0f}m², "
            f"shape={analysis.get('shape_type', 'unknown')}, "
            f"using {pattern} pattern"
        )
        
        # Apply pattern
        if pattern == LayoutPattern.FISHBONE:
            lots = FishboneSubdivider.subdivide(
                block,
                zone_type,
                self.target_lot_width,
                self.target_lot_depth
            )
        elif pattern == LayoutPattern.GRID:
            # Use existing grid subdivider
            from .simple_subdivider import subdivide_block_simple
            lots = subdivide_block_simple(
                block,
                zone_type,
                self.target_lot_width,
                self.target_lot_depth
            )
        else:
            # Fallback to fishbone for other patterns (implement later)
            logger.warning(f"[LAYOUT SUBDIVIDER] Pattern {pattern} not implemented, using fishbone")
            lots = FishboneSubdivider.subdivide(
                block,
                zone_type,
                self.target_lot_width,
                self.target_lot_depth
            )
        
        return lots
    
    def subdivide_blocks(
        self,
        blocks: List[Dict[str, Any]],
        zone_type: str = 'FACTORY'
    ) -> List[Dict[str, Any]]:
        """
        Subdivide multiple blocks
        
        Args:
            blocks: List of block dicts with 'geometry'
            zone_type: Default zone type
            
        Returns:
            List of blocks with 'lots' added
        """
        result = []
        
        for block_dict in blocks:
            block_geom = block_dict.get('geometry')
            if not isinstance(block_geom, Polygon):
                continue
            
            zone = block_dict.get('zone', zone_type)
            
            # Subdivide
            lots = self.subdivide_block(block_geom, zone)
            
            # Add to result
            block_copy = block_dict.copy()
            block_copy['lots'] = lots
            block_copy['num_lots'] = len(lots)
            result.append(block_copy)
        
        total_lots = sum(b.get('num_lots', 0) for b in result)
        logger.info(f"[LAYOUT SUBDIVIDER] ✓ Subdivided {len(blocks)} blocks → {total_lots} lots")
        
        return result
