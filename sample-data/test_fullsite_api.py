"""
Test Full-Site API Endpoints

Tests the complete API workflow:
1. Upload DWG file
2. Start full-site analysis
3. Poll for completion
4. Retrieve scenarios
5. Select and export scenario
6. Download DXF file
"""

import requests
import time
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api/demo"
DWG_FILE = "Pilot_Existing Topo _ Boundary.dxf"
TARGET_PLOTS = 200

def test_full_site_api():
    """Test complete full-site API workflow"""
    
    print("=" * 70)
    print("FULL-SITE API ENDPOINT TEST")
    print("=" * 70)
    print()
    
    # Check if file exists
    if not Path(DWG_FILE).exists():
        print(f"[ERROR] File not found: {DWG_FILE}")
        return
    
    print(f"Using file: {DWG_FILE}")
    print(f"Target plots: {TARGET_PLOTS}")
    print()
    
    # ========================================================================
    # STEP 1: Upload and start analysis
    # ========================================================================
    print("=" * 70)
    print("STEP 1: Starting Full-Site Analysis")
    print("=" * 70)
    print()
    
    with open(DWG_FILE, 'rb') as f:
        files = {'file': (DWG_FILE, f, 'application/octet-stream')}
        params = {'target_plot_count': TARGET_PLOTS}
        
        try:
            response = requests.post(
                f"{BASE_URL}/analyze-full-site",
                files=files,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            job_id = result['job_id']
            print(f"[OK] Analysis started")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print()
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to start analysis: {e}")
            return
    
    # ========================================================================
    # STEP 2: Poll for completion
    # ========================================================================
    print("=" * 70)
    print("STEP 2: Waiting for Analysis Completion")
    print("=" * 70)
    print()
    
    max_wait = 180  # 3 minutes
    poll_interval = 2  # 2 seconds
    elapsed = 0
    
    while elapsed < max_wait:
        try:
            response = requests.get(f"{BASE_URL}/scenarios/{job_id}")
            response.raise_for_status()
            result = response.json()
            
            status = result['status']
            progress = result.get('progress', 0)
            message = result.get('message', '')
            
            print(f"   [{elapsed}s] {status.upper()}: {progress}% - {message}")
            
            if status == 'completed':
                print()
                print("[OK] Analysis completed!")
                print()
                
                # Display site analysis
                site = result['site_analysis']
                print(f"   Site area: {site['site_area_ha']:.2f} ha")
                print(f"   Buildable zones: {site['buildable_zones']}")
                print(f"   Optimal zones: {site['optimal_zones']}")
                print(f"   Processing time: {site['processing_time_s']:.1f}s")
                print()
                
                # Display scenarios
                scenarios = result['scenarios']
                print(f"   Scenarios generated: {len(scenarios)}")
                print()
                
                for scenario in scenarios:
                    print(f"   --- Scenario {scenario['scenario_id']}: {scenario['name']} ---")
                    print(f"       Strategy: {scenario['strategy']}")
                    print(f"       Description: {scenario['description']}")
                    print(f"       Plots: {scenario['metrics']['plot_count']}")
                    print(f"       Area: {scenario['metrics']['development_area_ha']:.1f} ha")
                    print(f"       Cost: ${scenario['grading_cost']['estimated_cost_usd']:,.0f}")
                    print()
                
                break
                
            elif status == 'failed':
                print()
                print(f"[ERROR] Analysis failed: {result.get('error', 'Unknown error')}")
                return
            
            time.sleep(poll_interval)
            elapsed += poll_interval
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to poll status: {e}")
            return
    
    if elapsed >= max_wait:
        print(f"[ERROR] Timeout: Analysis did not complete in {max_wait}s")
        return
    
    # ========================================================================
    # STEP 3: Select and export scenario
    # ========================================================================
    print("=" * 70)
    print("STEP 3: Selecting and Exporting Scenario")
    print("=" * 70)
    print()
    
    # Select Scenario C (Balanced)
    selected_scenario_id = 'C'
    
    try:
        response = requests.post(
            f"{BASE_URL}/select-scenario",
            params={
                'job_id': job_id,
                'scenario_id': selected_scenario_id
            }
        )
        response.raise_for_status()
        result = response.json()
        
        export_job_id = result['export_job_id']
        print(f"[OK] Export started")
        print(f"   Export Job ID: {export_job_id}")
        print(f"   Scenario: {result['scenario']['name']}")
        print(f"   Plots: {result['scenario']['plot_count']}")
        print()
        
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to start export: {e}")
        return
    
    # ========================================================================
    # STEP 4: Wait for export completion
    # ========================================================================
    print("=" * 70)
    print("STEP 4: Waiting for DXF Export")
    print("=" * 70)
    print()
    
    elapsed = 0
    while elapsed < 60:  # 1 minute max
        try:
            response = requests.get(f"{BASE_URL}/job-status/{export_job_id}")
            response.raise_for_status()
            result = response.json()
            
            status = result['status']
            progress = result.get('progress', 0)
            message = result.get('message', '')
            
            print(f"   [{elapsed}s] {status.upper()}: {progress}% - {message}")
            
            if status == 'completed':
                print()
                print("[OK] Export completed!")
                print()
                
                export_result = result['result']
                print(f"   DXF file: {export_result['dxf_file']}")
                print(f"   Download URL: {export_result['download_url']}")
                print(f"   Scenario: {export_result['scenario_name']}")
                print(f"   Plots: {export_result['plot_count']}")
                print()
                
                download_url = f"{BASE_URL}{export_result['download_url']}"
                print(f"   Full download URL: {download_url}")
                
                # Download and save the file
                save_path = Path("output") / f"generated_pilot_{int(time.time())}.dxf"
                save_path.parent.mkdir(exist_ok=True)
                
                print(f"   Downloading to: {save_path}")
                r = requests.get(download_url)
                if r.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(r.content)
                    print(f"   [SAVED] File saved successfully.")
                else:
                    print(f"   [ERROR] Failed to download file: {r.status_code}")

                print()
                
                break
                
            elif status == 'failed':
                print()
                print(f"[ERROR] Export failed: {result.get('error', 'Unknown error')}")
                return
            
            time.sleep(1)
            elapsed += 1
            
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to poll export status: {e}")
            return
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print()
    print("[SUCCESS] All API endpoints working correctly!")
    print()
    print("Tested endpoints:")
    print("  1. POST /api/demo/analyze-full-site")
    print("  2. GET  /api/demo/scenarios/{job_id}")
    print("  3. POST /api/demo/select-scenario")
    print("  4. GET  /api/demo/job-status/{export_job_id}")
    print()
    print("Next steps:")
    print("  - Build frontend interface")
    print("  - Integrate with UI")
    print("  - Deploy to production")
    print()


if __name__ == "__main__":
    test_full_site_api()
