"""
Visualize Optimization Results

Tạo visualization để xem kết quả tối ưu hóa
"""
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPLPolygon
from matplotlib.collections import PatchCollection
import numpy as np

print("=" * 70)
print("VISUALIZATION: Optimization Results")
print("=" * 70)

# Read GeoJSON
geojson_file = Path(__file__).parent / 'output' / 'simple_test_result.geojson'

if not geojson_file.exists():
    print(f"❌ File not found: {geojson_file}")
    print("Run simple_test_dxf.py first!")
    exit(1)

with open(geojson_file, 'r') as f:
    data = json.load(f)

print(f"✓ Loaded: {len(data['features'])} features")

# Separate features
boundary_geom = None
block_geom = None
lots = []

for feature in data['features']:
    ftype = feature['properties'].get('type')
    coords = feature['geometry']['coordinates']
    
    if ftype == 'boundary':
        boundary_geom = coords[0]
    elif ftype == 'block':
        block_geom = coords[0]
    elif ftype == 'lot':
        lots.append({
            'coords': coords[0],
            'quality': feature['properties'].get('quality', 0),
            'area': feature['properties'].get('area', 0)
        })

print(f"\n📊 Data:")
print(f"  Boundary: {'✓' if boundary_geom else '✗'}")
print(f"  Block: {'✓' if block_geom else '✗'}")
print(f"  Lots: {len(lots)}")

# Create figure
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

# Plot 1: All lots colored by quality
ax1 = axes[0]
ax1.set_title('Lot Quality Scores', fontsize=14, fontweight='bold')
ax1.set_xlabel('X (m)')
ax1.set_ylabel('Y (m)')
ax1.set_aspect('equal')

# Draw boundary
if boundary_geom:
    boundary_patch = MPLPolygon(boundary_geom, fill=False, edgecolor='black', linewidth=2, linestyle='--')
    ax1.add_patch(boundary_patch)

# Draw block
if block_geom:
    block_patch = MPLPolygon(block_geom, fill=False, edgecolor='blue', linewidth=1.5)
    ax1.add_patch(block_patch)

# Draw lots colored by quality
if lots:
    lot_patches = []
    lot_colors = []
    
    for lot in lots:
        patch = MPLPolygon(lot['coords'], closed=True)
        lot_patches.append(patch)
        lot_colors.append(lot['quality'])
    
    collection = PatchCollection(lot_patches, cmap='RdYlGn', alpha=0.7, edgecolors='gray', linewidths=0.3)
    collection.set_array(np.array(lot_colors))
    collection.set_clim(0, 100)
    ax1.add_collection(collection)
    
    # Add colorbar
    cbar1 = plt.colorbar(collection, ax=ax1)
    cbar1.set_label('Quality Score', rotation=270, labelpad=20)

# Plot 2: Quality distribution
ax2 = axes[1]
ax2.set_title('Quality Score Distribution', fontsize=14, fontweight='bold')
ax2.set_xlabel('Quality Score')
ax2.set_ylabel('Number of Lots')

if lots:
    qualities = [lot['quality'] for lot in lots]
    
    # Histogram
    ax2.hist(qualities, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    
    # Statistics
    avg_quality = np.mean(qualities)
    median_quality = np.median(qualities)
    
    ax2.axvline(avg_quality, color='red', linestyle='--', linewidth=2, label=f'Mean: {avg_quality:.1f}')
    ax2.axvline(median_quality, color='orange', linestyle='--', linewidth=2, label=f'Median: {median_quality:.1f}')
    
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    # Add statistics text
    stats_text = f"""
    Total Lots: {len(lots)}
    Avg Quality: {avg_quality:.1f}/100
    Min: {min(qualities):.1f}
    Max: {max(qualities):.1f}
    
    High Quality (>80): {sum(1 for q in qualities if q > 80)}
    Good Quality (60-80): {sum(1 for q in qualities if 60 < q <= 80)}
    Low Quality (<60): {sum(1 for q in qualities if q < 60)}
    """
    
    ax2.text(0.02, 0.98, stats_text.strip(), transform=ax2.transAxes,
             verticalalignment='top', fontsize=9, family='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()

# Save figure
output_file = Path(__file__).parent / 'output' / 'optimization_visualization.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')

print(f"\n💾 Saved visualization: {output_file}")

# Show plot
plt.show()

print("\n✓ Visualization complete!")
