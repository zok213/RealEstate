"""
Script phân tích diện tích và đưa ra khuyến nghị thông số cho KCN Sóng Thần
"""
import ezdxf
import json
from pathlib import Path
from shapely.geometry import shape, Polygon
import math

def analyze_dxf(dxf_path):
    """Phân tích file DXF"""
    print(f"\n{'='*60}")
    print(f"ANALYZING DXF FILE: {dxf_path.name}")
    print(f"{'='*60}")
    
    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()
    
    # Find boundary polygon
    boundary = None
    max_area = 0
    
    for entity in msp:
        if entity.dxftype() == 'LWPOLYLINE' and entity.is_closed:
            pts = list(entity.get_points(format='xy'))
            if len(pts) >= 3:
                poly = Polygon(pts)
                if poly.is_valid and poly.area > max_area:
                    max_area = poly.area
                    boundary = poly
    
    if boundary:
        # Get dimensions
        bounds = boundary.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        area_m2 = boundary.area
        area_ha = area_m2 / 10000
        perimeter = boundary.length
        
        print(f"\n📐 DIMENSIONS (Metric Coordinates):")
        print(f"   Width:      {width:,.1f} m")
        print(f"   Height:     {height:,.1f} m")
        print(f"   Area:       {area_m2:,.1f} m² ({area_ha:,.2f} ha)")
        print(f"   Perimeter:  {perimeter:,.1f} m")
        print(f"   Vertices:   {len(boundary.exterior.coords)} points")
        
        return {
            'width_m': width,
            'height_m': height,
            'area_m2': area_m2,
            'area_ha': area_ha,
            'perimeter_m': perimeter,
            'boundary': boundary
        }
    else:
        print("❌ No boundary polygon found!")
        return None

def analyze_geojson(geojson_path):
    """Phân tích file GeoJSON"""
    print(f"\n{'='*60}")
    print(f"ANALYZING GEOJSON FILE: {geojson_path.name}")
    print(f"{'='*60}")
    
    with open(geojson_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find boundary feature
    boundary_feature = None
    for feature in data['features']:
        if feature.get('properties', {}).get('type') == 'boundary':
            boundary_feature = feature
            break
    
    if not boundary_feature:
        print("❌ No boundary feature found!")
        return None
    
    # Convert to Shapely polygon
    geom = shape(boundary_feature['geometry'])
    
    # Calculate area in m² (assuming coordinates are in degrees)
    # Need to convert from geographic to metric
    coords = list(geom.exterior.coords)
    
    # Use first point as reference
    origin_lat = coords[0][1]
    origin_lng = coords[0][0]
    
    # Convert to meters
    METERS_PER_DEGREE_LAT = 111320
    METERS_PER_DEGREE_LNG = 111320 * math.cos(math.radians(origin_lat))
    
    metric_coords = []
    for lng, lat in coords:
        x = (lng - origin_lng) * METERS_PER_DEGREE_LNG
        y = (lat - origin_lat) * METERS_PER_DEGREE_LAT
        metric_coords.append((x, y))
    
    metric_poly = Polygon(metric_coords)
    
    bounds = metric_poly.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    area_m2 = metric_poly.area
    area_ha = area_m2 / 10000
    perimeter = metric_poly.length
    
    print(f"\n📐 DIMENSIONS (Converted from Geographic):")
    print(f"   Width:      {width:,.1f} m")
    print(f"   Height:     {height:,.1f} m")
    print(f"   Area:       {area_m2:,.1f} m² ({area_ha:,.2f} ha)")
    print(f"   Perimeter:  {perimeter:,.1f} m")
    print(f"   Vertices:   {len(coords)} points")
    
    # Also show declared area
    declared_area = boundary_feature['properties'].get('area_ha', 0)
    print(f"   Declared:   {declared_area} ha (from metadata)")
    
    return {
        'width_m': width,
        'height_m': height,
        'area_m2': area_m2,
        'area_ha': area_ha,
        'perimeter_m': perimeter,
        'boundary': metric_poly
    }

def recommend_parameters(dxf_data, geojson_data):
    """Đưa ra khuyến nghị thông số dựa trên diện tích"""
    print(f"\n{'='*60}")
    print("📊 PARAMETER RECOMMENDATIONS")
    print(f"{'='*60}")
    
    # Use DXF data as primary (metric coordinates)
    area_ha = dxf_data['area_ha']
    width = dxf_data['width_m']
    height = dxf_data['height_m']
    
    print(f"\n🎯 Based on area: {area_ha:.2f} hectares ({area_ha * 10000:,.0f} m²)")
    
    # Calculate optimal parameters
    # For industrial parks, typical lot sizes:
    # - Small factories: 1,000 - 5,000 m² (lot width 20-40m)
    # - Medium factories: 5,000 - 20,000 m² (lot width 40-80m)
    # - Large factories: 20,000+ m² (lot width 80-150m)
    
    # Grid spacing (affects road network density)
    # Rule: spacing should be 1-2% of smallest dimension
    min_dim = min(width, height)
    spacing_min = max(15, min_dim * 0.01)
    spacing_max = max(25, min_dim * 0.02)
    
    # Lot width based on total area
    if area_ha < 50:  # Small park
        lot_min = 15
        lot_target = 30
        lot_max = 60
        road_width = 6
    elif area_ha < 200:  # Medium park
        lot_min = 20
        lot_target = 40
        lot_max = 80
        road_width = 8
    else:  # Large park
        lot_min = 30
        lot_target = 50
        lot_max = 100
        road_width = 10
    
    # Block depth (how deep lots go from road)
    block_depth = min(80, width / 3)
    
    # Optimization parameters
    # More complex shapes need more generations
    complexity = len(dxf_data['boundary'].exterior.coords)
    
    if complexity <= 5:  # Simple rectangle
        population = 30
        generations = 50
    elif complexity <= 10:  # Moderate
        population = 50
        generations = 100
    else:  # Complex
        population = 80
        generations = 150
    
    print(f"\n🔧 RECOMMENDED CONFIGURATION:")
    print(f"\n   Grid Spacing:")
    print(f"      Min: {spacing_min:.1f} m")
    print(f"      Max: {spacing_max:.1f} m")
    
    print(f"\n   Lot Dimensions:")
    print(f"      Min Width:    {lot_min} m")
    print(f"      Target Width: {lot_target} m")
    print(f"      Max Width:    {lot_max} m")
    
    print(f"\n   Infrastructure:")
    print(f"      Road Width:   {road_width} m")
    print(f"      Block Depth:  {block_depth:.1f} m")
    
    print(f"\n   Optimization:")
    print(f"      Population:   {population}")
    print(f"      Generations:  {generations}")
    print(f"      Time Limit:   5.0 seconds")
    
    print(f"\n💡 ESTIMATED RESULTS:")
    # Rough estimate: usable area = 70-80% (after roads, setbacks)
    usable_area = area_ha * 0.75
    avg_lot_area = (lot_target ** 2) / 10000  # Convert to ha
    estimated_lots = int(usable_area / avg_lot_area)
    
    print(f"   Usable Area:    ~{usable_area:.1f} ha (75% of total)")
    print(f"   Average Lot:    ~{lot_target}m x {lot_target}m ({lot_target**2} m²)")
    print(f"   Estimated Lots: ~{estimated_lots} plots")
    
    # Return as JSON config
    config = {
        "spacing_min": round(spacing_min, 1),
        "spacing_max": round(spacing_max, 1),
        "min_lot_width": lot_min,
        "target_lot_width": lot_target,
        "max_lot_width": lot_max,
        "road_width": road_width,
        "block_depth": round(block_depth, 1),
        "population_size": population,
        "generations": generations,
        "ortools_time_limit": 5.0
    }
    
    print(f"\n📋 JSON CONFIG (copy to modal):")
    print(json.dumps(config, indent=2))
    
    return config

if __name__ == "__main__":
    base_path = Path(__file__).parent
    dxf_file = base_path / "kcn_song_than_binh_duong.dxf"
    geojson_file = base_path / "kcn_song_than_binh_duong.geojson"
    
    # Analyze both files
    dxf_data = analyze_dxf(dxf_file)
    geojson_data = analyze_geojson(geojson_file)
    
    if dxf_data and geojson_data:
        # Compare
        print(f"\n{'='*60}")
        print("📊 COMPARISON")
        print(f"{'='*60}")
        print(f"\n   DXF Area:     {dxf_data['area_ha']:,.2f} ha")
        print(f"   GeoJSON Area: {geojson_data['area_ha']:,.2f} ha")
        print(f"   Difference:   {abs(dxf_data['area_ha'] - geojson_data['area_ha']):.2f} ha")
        
        # Recommend parameters
        config = recommend_parameters(dxf_data, geojson_data)
        
        # Save to file
        config_file = base_path / "kcn_song_than_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved to: {config_file}")
