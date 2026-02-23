"""Debug API vs direct call."""
from pipeline.land_redistribution import LandRedistributionPipeline
from shapely.geometry import Polygon
import requests
import json

# Use real coords
coords = [[[106.743785,10.903274],[106.758410,10.905615],[106.761352,10.906560],[106.762880,10.902580],[106.764850,10.898950],[106.766320,10.888520],[106.760250,10.887250],[106.754800,10.886120],[106.746550,10.887850],[106.745120,10.894520],[106.743785,10.903274]]]

site = Polygon(coords[0])
pipe = LandRedistributionPipeline([site], {'spacing_min': 80, 'skeleton_branches': 20})

result = pipe.run_full_pipeline(layout_method='skeleton', num_branches=20)

lots = result['stage2']['lots']

# Zone distribution
zones = {}
for lot in lots:
    z = lot.get('zone', 'UNKNOWN')
    zones[z] = zones.get(z, 0) + 1
    
print(f"Direct call - Total lots: {len(lots)}")
print(f"Direct call - Zone distribution: {zones}")
