"""Debug API response directly."""
import requests
import json

payload = {
    'config': {
        'spacing_min': 80,
        'spacing_max': 100,
        'min_lot_width': 40,
        'target_lot_width': 80,
        'max_lot_width': 150,
        'road_width': 10,
        'block_depth': 80,
        'population_size': 10,
        'generations': 15,
        'ortools_time_limit': 10,
        'skeleton_branches': 20
    },
    'land_plots': [{
        'type': 'Polygon',
        'coordinates': [[[106.743785,10.903274],[106.758410,10.905615],[106.761352,10.906560],[106.762880,10.902580],[106.764850,10.898950],[106.766320,10.888520],[106.760250,10.887250],[106.754800,10.886120],[106.746550,10.887850],[106.745120,10.894520],[106.743785,10.903274]]],
        'properties': {}
    }]
}

resp = requests.post('http://localhost:8000/api/optimize', json=payload, timeout=120)
data = resp.json()

# Find subdivision stage
for stage in data.get('stages', []):
    if 'Subdivision' in stage.get('stage_name', ''):
        features = stage.get('geometry', {}).get('features', [])
        lots = [f for f in features if f.get('properties', {}).get('type') == 'lot']
        
        zones = {}
        for lot in lots:
            z = lot.get('properties', {}).get('zone', 'MISSING')
            zones[z] = zones.get(z, 0) + 1
        
        print(f"API - Total lots: {len(lots)}")
        print(f"API - Zone distribution: {zones}")
        
        # Show sample lot
        if lots:
            print(f"Sample lot: {lots[0].get('properties')}")
        break
