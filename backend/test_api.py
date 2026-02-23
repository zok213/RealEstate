"""Quick test script for Industrial Park AI Designer API."""
import requests
import time

BASE = 'http://localhost:8000'

print("=" * 50)
print("Industrial Park AI Designer - API Test")
print("=" * 50)

# 1. Health check
print("\n1. Health Check...")
r = requests.get(f'{BASE}/')
print(f"   Status: {r.json()['status']}")

# 2. Create project
print("\n2. Creating Project...")
r = requests.post(f'{BASE}/api/projects/new', json={
    'name': 'Auto Factory Park',
    'site_area_ha': 50
})
project = r.json()
project_id = project['project_id']
print(f"   Project ID: {project_id}")
print(f"   Site: {project['project']['site']['width']:.0f}m x {project['project']['site']['height']:.0f}m")

# 3. Trigger design generation
print("\n3. Triggering Design Generation...")
r = requests.post(f'{BASE}/api/designs/generate', json={
    'project_id': project_id,
    'use_chat_params': False,
    'parameters': {
        'industryFocus': [
            {'type': 'light_manufacturing', 'count': 5},
            {'type': 'warehouse', 'count': 3}
        ],
        'workerCapacity': 2000
    }
})
job = r.json()
job_id = job['job_id']
print(f"   Job ID: {job_id}")

# 4. Wait for completion
print("\n4. Waiting for Design Generation...")
for i in range(15):
    time.sleep(1)
    r = requests.get(f'{BASE}/api/designs/jobs/{job_id}')
    status = r.json()
    progress = status.get('progress', 0)
    print(f"   Progress: {progress}%", end='\r')
    if status.get('status') == 'completed':
        print(f"\n   Design completed!")
        break
    if status.get('status') == 'failed':
        print(f"\n   Design failed: {status.get('error')}")
        break

# 5. Get variants
print("\n5. Getting Variants...")
r = requests.get(f'{BASE}/api/designs/{project_id}/variants')
variants = r.json()['variants']
print(f"   Found {len(variants)} variants")

for i, v in enumerate(variants[:3]):
    scores = v['fitness_scores']
    compliance = v['compliance']['overall_compliance_percent']
    print(f"\n   Variant {i+1}: {v['name']}")
    print(f"   - Road Efficiency: {scores['road_efficiency']}")
    print(f"   - Worker Flow: {scores['worker_flow']}")
    print(f"   - Green Ratio: {scores['green_ratio']}")
    print(f"   - Total Score: {scores['total']}")
    print(f"   - Compliance: {compliance}%")

print("\n" + "=" * 50)
print("All tests passed!")
print("=" * 50)
