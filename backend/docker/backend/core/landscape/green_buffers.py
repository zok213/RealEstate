"""
Green Buffer Zone Generator

Creates green separation buffers between functional zones and around perimeter
according to QCVN 01:2021/BXD requirements.
"""

from typing import List, Dict, Any, Tuple
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import unary_union
import logging

logger = logging.getLogger(__name__)


def create_perimeter_green_buffer(
    site_boundary: Polygon,
    buffer_width: float = 30.0
) -> Polygon:
    """
    Create green buffer around site perimeter.
    
    Args:
        site_boundary: Site boundary polygon
        buffer_width: Width of green buffer (default 30m)
        
    Returns:
        Polygon representing perimeter green buffer zone
    """
    try:
        # Create inner boundary (site - buffer)
        inner_boundary = site_boundary.buffer(-buffer_width)
        
        if inner_boundary.is_empty:
            logger.warning("Site too small for perimeter buffer")
            return Polygon()
        
        # Green buffer = site - inner
        green_buffer = site_boundary.difference(inner_boundary)
        
        logger.info(f"[GREEN BUFFER] Perimeter: {green_buffer.area:.0f} m² ({buffer_width}m width)")
        return green_buffer
        
    except Exception as e:
        logger.error(f"[GREEN BUFFER] Error creating perimeter: {e}")
        return Polygon()


def create_zone_separation_buffers(
    blocks: List[Dict[str, Any]],
    buffer_width: float = 20.0
) -> List[Polygon]:
    """
    Create green buffers between different functional zones.
    
    Args:
        blocks: List of blocks with 'geometry' and 'zone' properties
        buffer_width: Width of separation buffer (default 20m)
        
    Returns:
        List of green buffer polygons
    """
    from shapely.geometry import shape
    
    buffers = []
    
    try:
        # Group blocks by zone type
        zones = {}
        for block in blocks:
            zone = block.get('properties', {}).get('zone', 'UNKNOWN')
            geom = shape(block['geometry'])
            
            if zone not in zones:
                zones[zone] = []
            zones[zone].append(geom)
        
        # Merge blocks by zone
        zone_polygons = {}
        for zone_name, geoms in zones.items():
            if geoms:
                zone_polygons[zone_name] = unary_union(geoms)
        
        # Create buffers between different zones
        zone_names = list(zone_polygons.keys())
        for i in range(len(zone_names)):
            for j in range(i + 1, len(zone_names)):
                zone_a = zone_names[i]
                zone_b = zone_names[j]
                
                poly_a = zone_polygons[zone_a]
                poly_b = zone_polygons[zone_b]
                
                # Find boundary between zones
                # Buffer each zone and find intersection
                buffer_a = poly_a.buffer(buffer_width / 2.0)
                buffer_b = poly_b.buffer(buffer_width / 2.0)
                
                # Green buffer = intersection of buffers
                green_buffer = buffer_a.intersection(buffer_b)
                
                if not green_buffer.is_empty and green_buffer.area > 100:  # Min 100 m²
                    buffers.append(green_buffer)
                    logger.info(f"[GREEN BUFFER] {zone_a}-{zone_b}: {green_buffer.area:.0f} m²")
        
        logger.info(f"[GREEN BUFFER] Created {len(buffers)} zone separation buffers")
        return buffers
        
    except Exception as e:
        logger.error(f"[GREEN BUFFER] Error creating zone buffers: {e}")
        return []


def create_green_corridors(
    road_network: Polygon,
    corridor_width: float = 10.0
) -> List[Polygon]:
    """
    Create green corridors along major roads.
    
    Args:
        road_network: Road network polygon
        corridor_width: Width of green corridor on each side (default 10m)
        
    Returns:
        List of green corridor polygons
    """
    try:
        if road_network.is_empty:
            return []
        
        # Get road centerlines
        if isinstance(road_network, MultiPolygon):
            roads = list(road_network.geoms)
        else:
            roads = [road_network]
        
        corridors = []
        
        for road in roads:
            if road.area > 1000:  # Only major roads > 1000 m²
                # Extract skeleton/centerline (simplified)
                centroid = road.centroid
                bounds = road.bounds
                
                # Create corridor along road edges
                road_buffer = road.buffer(corridor_width)
                corridor = road_buffer.difference(road)
                
                if not corridor.is_empty and corridor.area > 50:
                    corridors.append(corridor)
        
        logger.info(f"[GREEN CORRIDOR] Created {len(corridors)} road corridors")
        return corridors
        
    except Exception as e:
        logger.error(f"[GREEN CORRIDOR] Error: {e}")
        return []


def merge_green_spaces(
    perimeter_buffer: Polygon,
    zone_buffers: List[Polygon],
    existing_parks: List[Polygon]
) -> List[Dict[str, Any]]:
    """
    Merge all green spaces and create GeoJSON features.
    
    Args:
        perimeter_buffer: Perimeter green buffer
        zone_buffers: Zone separation buffers
        existing_parks: Existing park polygons
        
    Returns:
        List of GeoJSON feature dicts for green spaces
    """
    from shapely.geometry import mapping
    
    features = []
    
    try:
        # Collect all green polygons
        all_green = []
        
        if not perimeter_buffer.is_empty:
            all_green.append(perimeter_buffer)
        
        all_green.extend(zone_buffers)
        all_green.extend(existing_parks)
        
        # Merge overlapping greens
        if all_green:
            merged = unary_union(all_green)
            
            # Convert to features
            if isinstance(merged, MultiPolygon):
                green_polys = list(merged.geoms)
            else:
                green_polys = [merged]
            
            for idx, green_poly in enumerate(green_polys):
                if green_poly.area > 100:  # Min 100 m²
                    features.append({
                        'type': 'Feature',
                        'geometry': mapping(green_poly),
                        'properties': {
                            'type': 'park',
                            'subtype': 'green_buffer',
                            'id': f'green_{idx}',
                            'area': green_poly.area,
                            'description': 'Green buffer zone'
                        }
                    })
        
        total_area = sum(f['properties']['area'] for f in features)
        logger.info(f"[GREEN MERGE] Total green area: {total_area:.0f} m² ({len(features)} polygons)")
        return features
        
    except Exception as e:
        logger.error(f"[GREEN MERGE] Error: {e}")
        return []


def add_green_buffers_to_layout(
    final_layout: Dict[str, Any],
    site_boundary: Polygon,
    perimeter_buffer_width: float = 30.0,
    zone_buffer_width: float = 20.0
) -> Dict[str, Any]:
    """
    Add green buffer zones to final layout.
    
    Args:
        final_layout: Existing layout with features
        site_boundary: Site boundary polygon
        perimeter_buffer_width: Perimeter buffer width (default 30m)
        zone_buffer_width: Zone separation buffer width (default 20m)
        
    Returns:
        Updated layout with green buffers
    """
    from shapely.geometry import shape
    
    try:
        features = final_layout.get('features', [])
        
        # Extract existing parks
        existing_parks = []
        blocks = []
        
        for feature in features:
            ftype = feature.get('properties', {}).get('type', '')
            geom = shape(feature['geometry'])
            
            if ftype == 'park':
                existing_parks.append(geom)
            elif ftype in ['block', 'lot']:
                blocks.append(feature)
        
        # Create buffers
        logger.info("[GREEN BUFFER] Creating perimeter buffer...")
        perimeter_buffer = create_perimeter_green_buffer(site_boundary, perimeter_buffer_width)
        
        logger.info("[GREEN BUFFER] Creating zone separation buffers...")
        zone_buffers = create_zone_separation_buffers(blocks, zone_buffer_width)
        
        # Merge all green spaces
        logger.info("[GREEN BUFFER] Merging green spaces...")
        green_features = merge_green_spaces(perimeter_buffer, zone_buffers, existing_parks)
        
        # Remove old parks and add new merged greens
        features_without_parks = [f for f in features if f.get('properties', {}).get('type') != 'park']
        features_without_parks.extend(green_features)
        
        final_layout['features'] = features_without_parks
        
        logger.info(f"[GREEN BUFFER] Added {len(green_features)} green buffer features")
        return final_layout
        
    except Exception as e:
        logger.error(f"[GREEN BUFFER] Error adding to layout: {e}")
        return final_layout
