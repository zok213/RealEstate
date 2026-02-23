"""
Test DWG file upload and terrain analysis
"""
import sys
sys.path.insert(0, 'D:/git/new realestate/backend')

from pathlib import Path
from ai.dxf_analyzer import DXFAnalyzer
import json

# Test file path
dwg_file = r"D:\git\new realestate\sample-data\Pilot_Existing Topo _ Boundary.dwg"

print("=" * 80)
print("DWG TERRAIN ANALYSIS TEST")
print("=" * 80)
print(f"\nFile: {dwg_file}")
print(f"Exists: {Path(dwg_file).exists()}")
print(f"Size: {Path(dwg_file).stat().st_size / 1024:.1f} KB\n")

# Try to analyze
try:
    print("🔍 Analyzing DWG file...")
    analyzer = DXFAnalyzer(dwg_file)
    result = analyzer.analyze()
    
    print("\n✅ ANALYSIS COMPLETE\n")
    print("=" * 80)
    
    if result.get("success"):
        site = result["site_info"]
        
        print("📊 SITE INFORMATION:")
        print(f"  Area: {site['area_ha']:.2f} ha ({site['area_m2']:,.0f} m²)")
        print(f"  Area (rai): {site['area_rai']:.2f} rai")
        print(f"  Dimensions: {site['dimensions']['width_m']:.0f}m × {site['dimensions']['height_m']:.0f}m")
        print(f"  Perimeter: {site['dimensions']['perimeter_m']:.0f}m")
        print(f"  Boundary points: {site['boundary_points_count']}")
        
        print("\n🏔️ TERRAIN INFORMATION:")
        terrain = site.get('terrain', {})
        print(f"  Has topography: {terrain.get('has_topography', False)}")
        print(f"  Contour lines found: {terrain.get('contour_count', 0)}")
        
        if terrain.get('has_topography'):
            print("\n  ✅ TERRAIN DETECTED - System will ask user about grading strategy")
        else:
            print("\n  ℹ️ No terrain contours detected - assuming flat site")
        
        print("\n💡 DESIGN SUGGESTIONS:")
        sugg = result["suggestions"]
        print(f"  Project scale: {sugg['project_scale']}")
        print(f"  Estimated plots: ~{sugg['estimated_plots']} buildings")
        print(f"  Salable area: ~{sugg['land_use_breakdown']['salable_area_ha']:.2f} ha (77%)")
        print(f"  Green area: ~{sugg['land_use_breakdown']['green_area_ha']:.2f} ha (12%)")
        
        print("\n❓ QUESTIONS FOR USER:")
        for i, q in enumerate(result["questions"][:5], 1):
            print(f"  {i}. {q['question']}")
            if q.get('options'):
                for opt in q['options'][:3]:
                    print(f"     - {opt}")
        
        print("\n📝 SAMPLE PROMPTS:")
        for i, prompt in enumerate(result["sample_prompts"][:3], 1):
            print(f"  {i}. {prompt}")
        
        print("\n" + "=" * 80)
        print("🎯 TERRAIN STRATEGY OPTIONS:")
        print("  1. Minimal cut/fill - giữ nguyên địa hình")
        print("     → Đường cong theo contour, terraced buildings")
        print("     → Chi phí earthwork: ~30% standard")
        print("     → Retaining walls: ~2% perimeter")
        print()
        print("  2. Balanced cut/fill - cân bằng")
        print("     → Moderate grading, some retaining walls")
        print("     → Chi phí earthwork: ~100% standard")
        print("     → Retaining walls: ~1% perimeter")
        print()
        print("  3. Major grading - san phẳng hoàn toàn")
        print("     → Flatten site completely")
        print("     → Chi phí earthwork: ~250% standard")
        print("     → No retaining walls needed")
        
    else:
        print(f"❌ ANALYSIS FAILED: {result.get('error')}")
        if result.get('suggestions'):
            print("\nSuggestions:")
            for sugg in result['suggestions']:
                print(f"  - {sugg}")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Test complete!")
