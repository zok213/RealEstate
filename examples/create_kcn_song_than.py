"""
Script để tạo file DXF cho KCN Sóng Thần bằng ezdxf library
Sử dụng tọa độ GPS thực tế của KCN Sóng Thần
"""
import ezdxf
from pathlib import Path
import math

# Tọa độ GPS thực tế của KCN Sóng Thần (lat, lng)
real_coords_latlon = [
    (10.903274, 106.743785),  # Góc phía Tây Bắc
    (10.905615, 106.758410),  # Dọc theo đường DT743
    (10.906560, 106.761352),  # Góc phía Đông Bắc
    (10.902580, 106.762880),  # Cổng ga Sóng Thần
    (10.898950, 106.764850),  # Phía Đông
    (10.888520, 106.766320),  # Góc phía Đông Nam
    (10.887250, 106.760250),  # Ranh giới phía Nam
    (10.886120, 106.754800),  # Đường bao phía Nam
    (10.887850, 106.746550),  # Góc phía Tây Nam
    (10.894520, 106.745120),  # Dọc Đại lộ Độc Lập
    (10.903274, 106.743785),  # Đóng ranh giới
]

# Convert lat/lng to metric coordinates (meters)
# Use first point as origin
origin_lat, origin_lng = real_coords_latlon[0]

# Conversion factors: 1 degree ≈ 111,320 meters
METERS_PER_DEGREE_LAT = 111320
METERS_PER_DEGREE_LNG = 111320 * math.cos(math.radians(origin_lat))

def latlon_to_meters(lat, lng, origin_lat, origin_lng):
    """Convert lat/lng to meters relative to origin"""
    x = (lng - origin_lng) * METERS_PER_DEGREE_LNG
    y = (lat - origin_lat) * METERS_PER_DEGREE_LAT
    return (x, y)

# Convert all points to metric
boundary_points = [
    latlon_to_meters(lat, lng, origin_lat, origin_lng) 
    for lat, lng in real_coords_latlon
]

print("Boundary points in meters:")
for i, (x, y) in enumerate(boundary_points):
    print(f"  {i+1}. ({x:.1f}, {y:.1f})")

# Calculate bounding box
xs = [p[0] for p in boundary_points]
ys = [p[1] for p in boundary_points]
min_x, max_x = min(xs), max(xs)
min_y, max_y = min(ys), max(ys)
width = max_x - min_x
height = max_y - min_y
center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

print(f"\nBoundary dimensions:")
print(f"  Width: {width:.1f}m")
print(f"  Height: {height:.1f}m")
print(f"  Center: ({center_x:.1f}, {center_y:.1f})")
print(f"  Area: ~{(width * height / 10000):.1f} hectares")

# Create a new DXF R2010 document
doc = ezdxf.new('R2010', setup=True)

# Get modelspace
msp = doc.modelspace()

# Add layers
doc.layers.add('BOUNDARY', color=3)  # Green
doc.layers.add('TEXT', color=4)      # Cyan

# Add boundary polygon
msp.add_lwpolyline(boundary_points, dxfattribs={'layer': 'BOUNDARY', 'closed': True})

# Add text label at center
msp.add_text(
    'KCN Song Than', 
    dxfattribs={'layer': 'TEXT', 'height': 200}
).set_placement((center_x, center_y))

# Set document metadata
doc.header['$INSUNITS'] = 4  # Millimeters

# Save the DXF file
output_path = Path(__file__).parent / 'kcn_song_than_binh_duong.dxf'
doc.saveas(output_path)

print(f"\n✅ Created DXF file: {output_path}")
print(f"   - Real boundary from GPS coordinates")
print(f"   - 11 boundary points")
print(f"   - Dimensions: {width:.1f}m x {height:.1f}m")
