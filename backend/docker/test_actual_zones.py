"""Test actual zone classification."""
from pipeline.land_redistribution import LandRedistributionPipeline
from shapely.geometry import Polygon

coords = [[[106.743785,10.903274],[106.758410,10.905615],[106.761352,10.906560],[106.762880,10.902580],[106.764850,10.898950],[106.766320,10.888520],[106.760250,10.887250],[106.754800,10.886120],[106.746550,10.887850],[106.745120,10.894520],[106.743785,10.903274]]]

site = Polygon(coords[0])
pipe = LandRedistributionPipeline([site], {'spacing_min': 80})

# Run pipeline
result = pipe.run_full_pipeline(layout_method='skeleton', num_branches=20)

# Check what zones are in the result
lots = result['stage2']['lots']
print(f"Total lots: {len(lots)}")

# Zone distribution
zones = {}
for lot in lots:
    z = lot.get('zone', 'NO_ZONE')
    zones[z] = zones.get(z, 0) + 1
    
print(f"Zone distribution: {zones}")

# Check if zone is a STRING or something else
if lots:
    first_zone = lots[0].get('zone')
    print(f"\nFirst lot zone: '{first_zone}' (type: {type(first_zone)})")
    print(f"First lot keys: {lots[0].keys()}")
