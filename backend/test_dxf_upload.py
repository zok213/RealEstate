"""
Test DXF Upload and Analysis API
"""
import requests
import os
from pathlib import Path

# API endpoint
API_URL = "http://localhost:8001"

def test_dxf_upload():
    """Test DXF upload and analysis endpoint"""
    
    # Find pilot DXF file
    dxf_file = Path(__file__).parent.parent / "sample-data" / "Pilot_Existing Topo _ Boundary.dxf"
    
    if not dxf_file.exists():
        print(f"❌ DXF file not found: {dxf_file}")
        return
    
    print(f"📁 Testing with file: {dxf_file.name}")
    print(f"📍 API: {API_URL}/api/upload-dxf")
    print()
    
    # Upload DXF
    with open(dxf_file, 'rb') as f:
        files = {'file': (dxf_file.name, f, 'application/dxf')}
        
        try:
            response = requests.post(f"{API_URL}/api/upload-dxf", files=files)
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Upload thành công!")
                print()
                print("📊 THÔNG TIN KHU ĐẤT:")
                site = result['site_info']
                print(f"   Diện tích: {site['area_ha']} ha ({site['area_m2']:,.0f} m²)")
                print(f"   Kích thước: {site['dimensions']['width_m']:.0f}m × {site['dimensions']['height_m']:.0f}m")
                print()
                
                print("💡 GỢI Ý THIẾT KẾ:")
                sugg = result['suggestions']
                print(f"   Quy mô: {sugg['project_scale']}")
                print(f"   Số plots: ~{sugg['estimated_plots']}")
                print(f"   Salable: {sugg['land_use_breakdown']['salable_area_ha']:.1f} ha")
                print(f"   Green: {sugg['land_use_breakdown']['green_area_ha']:.1f} ha")
                print()
                
                print("❓ CÂU HỎI HỖ TRỢ:")
                for i, q in enumerate(result['questions'][:3], 1):
                    print(f"   {i}. {q['question']}")
                print()
                
                print("📝 PROMPT MẪU:")
                for i, p in enumerate(result['sample_prompts'][:2], 1):
                    print(f"   {i}. \"{p[:80]}...\"")
                print()
                
                if result.get('ai_greeting'):
                    print("🤖 AI GREETING:")
                    print(result['ai_greeting'][:300] + "...")
                
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING DXF UPLOAD & ANALYSIS API")
    print("=" * 60)
    print()
    
    test_dxf_upload()
