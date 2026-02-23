"""
Simple test to debug API endpoint
"""

import requests
from pathlib import Path

BASE_URL = "http://localhost:8000/api/demo"
DWG_FILE = "Pilot_Existing Topo _ Boundary.dxf"

print("Testing API endpoint...")
print(f"File: {DWG_FILE}")
print(f"File exists: {Path(DWG_FILE).exists()}")
print()

try:
    with open(DWG_FILE, 'rb') as f:
        files = {'file': (DWG_FILE, f, 'application/octet-stream')}
        params = {'target_plot_count': 200}
        
        print(f"Sending POST to {BASE_URL}/analyze-full-site")
        print(f"Params: {params}")
        print()
        
        response = requests.post(
            f"{BASE_URL}/analyze-full-site",
            files=files,
            params=params,
            timeout=30
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Job ID: {result['job_id']}")
        else:
            print(f"Error: {response.status_code}")
            
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
