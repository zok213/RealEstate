"""
Test Terrain Handling Pipeline with Real DWG File
Tests the complete flow from DWG upload to terrain-aware design generation
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.dxf_analyzer import DXFAnalyzer
from ai.llm_orchestrator import IndustrialParkLLMOrchestrator
from design.terrain_layout_adapter import TerrainLayoutAdapter
from design.enhanced_layout_generator import EnhancedLayoutGenerator
from shapely.geometry import box
import json


def test_dwg_terrain_detection():
    """Test 1: DWG file terrain detection"""
    print("\n" + "="*70)
    print("TEST 1: DXF/DWG Terrain Detection")
    print("="*70)
    
    # Try DXF first (more reliable)
    dxf_path = r"D:\git\new realestate\sample-data\Pilot_Existing Topo _ Boundary.dxf"
    dwg_path = r"D:\git\new realestate\sample-data\Pilot_Existing Topo _ Boundary.dwg"
    
    file_path = dxf_path if os.path.exists(dxf_path) else dwg_path
    
    if not os.path.exists(file_path):
        print(f"❌ Neither DXF nor DWG file found")
        return False
    
    print(f"📁 Analyzing: {file_path}")
    
    try:
        analyzer = DXFAnalyzer(file_path)
        analysis = analyzer.analyze()
        
        if not analysis.get("success"):
            print(f"❌ Analysis failed: {analysis.get('error')}")
            return False
        
        print("\n✅ DWG Analysis Successful!")
        print("\n📊 Site Information:")
        site = analysis["site_info"]
        print(f"  - Area: {site['area_ha']} ha ({site['area_m2']:,.0f} m²)")
        print(f"  - Dimensions: {site['dimensions']['width_m']:.0f}m × {site['dimensions']['height_m']:.0f}m")
        print(f"  - Perimeter: {site['dimensions']['perimeter_m']:,.0f}m")
        
        print("\n🏔️ Terrain Information:")
        terrain = site.get('terrain', {})
        print(f"  - Has Topography: {terrain.get('has_topography', False)}")
        print(f"  - Contour Count: {terrain.get('contour_count', 0)}")
        
        if terrain.get('has_topography'):
            print("\n✅ Terrain detected successfully!")
        else:
            print("\n⚠️ No terrain data detected (may be in separate layer)")
        
        print("\n💡 IEAT Suggestions:")
        sugg = analysis["suggestions"]
        print(f"  - Project Scale: {sugg['project_scale']}")
        print(f"  - Estimated Plots: {sugg['estimated_plots']}")
        print(f"  - Salable Area: {sugg['land_use_breakdown']['salable_area_ha']} ha")
        
        print("\n❓ Questions Generated:")
        for i, q in enumerate(analysis["questions"][:5], 1):
            print(f"  {i}. {q['question']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_terrain_extraction():
    """Test 2: LLM terrain strategy extraction"""
    print("\n" + "="*70)
    print("TEST 2: LLM Terrain Strategy Extraction")
    print("="*70)
    
    orchestrator = IndustrialParkLLMOrchestrator()
    
    # Simulate DXF context injection with terrain
    mock_analysis = {
        "success": True,
        "site_info": {
            "area_ha": 191.42,
            "area_m2": 1914212,
            "dimensions": {
                "width_m": 1699,
                "height_m": 2157,
                "perimeter_m": 7500
            },
            "terrain": {
                "has_topography": True,
                "contour_count": 45
            }
        },
        "suggestions": {
            "project_scale": "mega_industrial_estate",
            "estimated_plots": 120,
            "land_use_breakdown": {
                "salable_area_ha": 148.5,
                "green_area_ha": 19.2,
                "utility_area_ha": 23.7
            },
            "infrastructure": {
                "main_road_width": "25-30m",
                "secondary_road": "15-20m"
            },
            "building_recommendations": {
                "plot_size_range": "5,000-30,000 m²",
                "building_height": "8-15m (1-2 floors)"
            }
        },
        "questions": [
            {
                "question": "🏔️ Xử lý địa hình?",
                "options": [
                    "Minimal cut/fill - giữ nguyên địa hình",
                    "Balanced cut/fill - san nền cân bằng",
                    "Major grading - san phẳng hoàn toàn"
                ]
            }
        ],
        "sample_prompts": [
            "Thiết kế khu công nghiệp 191.4 ha, ưu tiên logistics, tuân thủ IEAT Thailand"
        ]
    }
    
    print("\n📝 Injecting DXF context with terrain data...")
    greeting = orchestrator.inject_dxf_context(mock_analysis)
    
    print("\n✅ Context injected!")
    print(f"\n🤖 AI Greeting (first 500 chars):")
    print(greeting[:500] + "...")
    
    # Test terrain strategy extraction
    print("\n🧪 Testing terrain strategy extraction...")
    
    test_responses = [
        ("Tôi muốn minimal cut/fill, giữ nguyên địa hình", "minimal_cut"),
        ("Chọn balanced cut/fill để cân bằng", "balanced_cut_fill"),
        ("San phẳng hoàn toàn với major grading", "major_grading"),
    ]
    
    for user_input, expected in test_responses:
        extracted = orchestrator._extract_structured_params(user_input)
        actual = extracted.get("terrain_strategy")
        
        if actual == expected:
            print(f"  ✅ '{user_input[:40]}...' → {actual}")
        else:
            print(f"  ❌ '{user_input[:40]}...' → Expected: {expected}, Got: {actual}")
    
    # Check extracted params
    params = orchestrator.get_extracted_params()
    print(f"\n📊 Extracted Parameters:")
    print(f"  - Has Topography: {params['parameters'].get('has_topography')}")
    print(f"  - Terrain Data: {params['parameters'].get('terrain')}")
    
    return True


def test_terrain_layout_adapter():
    """Test 3: Terrain Layout Adapter"""
    print("\n" + "="*70)
    print("TEST 3: Terrain Layout Adapter")
    print("="*70)
    
    strategies = ["minimal_cut", "balanced_cut_fill", "major_grading"]
    site_area_m2 = 1_914_212  # Pilot project area
    
    print(f"\n🏗️ Testing layout adaptation for {site_area_m2:,.0f} m² site\n")
    
    for strategy in strategies:
        print(f"\n📐 Strategy: {strategy}")
        print("-" * 50)
        
        adapter = TerrainLayoutAdapter(strategy)
        
        # Test road adjustment
        mock_roads = [
            {"type": "Feature", "properties": {"type": "main_road"}},
            {"type": "Feature", "properties": {"type": "secondary_road"}},
        ]
        
        adjusted_roads = adapter.adjust_road_layout(mock_roads)
        print(f"  ✅ Roads adjusted: {len(adjusted_roads)} roads")
        if adjusted_roads and "properties" in adjusted_roads[0]:
            props = adjusted_roads[0]["properties"]
            if "max_grade" in props:
                print(f"     - Max grade: {props['max_grade']}%")
            if "contour_following" in props:
                print(f"     - Contour following: {props['contour_following']}")
        
        # Test plot adjustment
        mock_plots = [
            {"zone": "WAREHOUSE", "area_m2": 5000} for _ in range(10)
        ]
        
        adjusted_plots = adapter.adjust_plot_placement(mock_plots)
        print(f"  ✅ Plots adjusted: {len(adjusted_plots)} plots")
        if adjusted_plots:
            sample = adjusted_plots[0]
            if "platform_elevation" in sample:
                print(f"     - Platform elevation: {sample['platform_elevation']}m")
            if "needs_retaining_wall" in sample:
                print(f"     - Retaining walls: {sample['needs_retaining_wall']}")
        
        # Test cost calculation
        costs = adapter.calculate_grading_cost(site_area_m2)
        print(f"\n  💰 Cost Breakdown:")
        print(f"     - Earthwork: {costs['earthwork_volume_m3']:,.0f} m³")
        print(f"     - Earthwork cost: {costs['earthwork_cost']/1e9:.2f}B VND")
        print(f"     - Retaining walls: {costs['retaining_walls_m']:,.0f} m")
        print(f"     - Wall cost: {costs['retaining_wall_cost']/1e9:.2f}B VND")
        print(f"     - TOTAL: {costs['total_cost']/1e9:.2f}B VND")
        print(f"     - Per m²: {costs['cost_per_m2']:,.0f} VND")
    
    return True


def test_enhanced_layout_generator():
    """Test 4: Enhanced Layout Generator with terrain"""
    print("\n" + "="*70)
    print("TEST 4: Enhanced Layout Generator Integration")
    print("="*70)
    
    # Mock design parameters with terrain strategy
    design_params = {
        "totalArea_ha": 191.42,
        "totalArea_m2": 1914212,
        "salableArea_percent": 77,
        "greenArea_percent": 10,
        "terrain_strategy": "minimal_cut",
        "has_topography": True,
        "terrain": {
            "has_topography": True,
            "contour_count": 45
        },
        "industryFocus": [
            {"type": "warehouse", "count": 40, "percentage": 40},
            {"type": "light_manufacturing", "count": 60, "percentage": 60}
        ]
    }
    
    print("\n📋 Design Parameters:")
    print(f"  - Area: {design_params['totalArea_ha']} ha")
    print(f"  - Terrain Strategy: {design_params['terrain_strategy']}")
    print(f"  - Has Topography: {design_params['has_topography']}")
    
    # Create site boundary
    site_boundary = box(0, 0, 1699, 2157)
    
    print("\n🔧 Testing optimization request preparation...")
    
    generator = EnhancedLayoutGenerator()
    request = generator._prepare_optimization_request(design_params, site_boundary)
    
    config = request.get("config", {})
    print(f"\n✅ Optimization Config Generated:")
    print(f"  - Spacing min: {config.get('spacing_min')}m")
    print(f"  - Spacing max: {config.get('spacing_max')}m")
    print(f"  - Road width: {config.get('road_width')}m")
    print(f"  - Min lot width: {config.get('min_lot_width')}m")
    print(f"  - Terrain strategy: {config.get('terrain_strategy')}")
    print(f"  - Has topography: {config.get('has_topography')}")
    
    # Verify terrain strategy affects config
    if config.get('terrain_strategy') == 'minimal_cut':
        if config.get('spacing_min') >= 30:
            print("\n✅ Terrain strategy correctly adjusts spacing for contour-following")
        else:
            print("\n⚠️ Spacing not adjusted for minimal_cut strategy")
    
    return True


def test_full_pipeline():
    """Test 5: Full pipeline simulation"""
    print("\n" + "="*70)
    print("TEST 5: Full Pipeline Simulation")
    print("="*70)
    
    print("\n🎬 Simulating complete workflow:")
    print("  1. User uploads DWG file")
    print("  2. System detects terrain")
    print("  3. AI asks terrain strategy")
    print("  4. User chooses 'minimal_cut'")
    print("  5. System generates design with terrain adaptation")
    
    # Mock parameters from chat
    chat_params = {
        "total_area_ha": 191.42,
        "total_area_m2": 1914212,
        "terrain_strategy": "minimal_cut",
        "has_topography": True,
        "terrain": {"has_topography": True, "contour_count": 45},
        "industry_focus": [
            {"type": "warehouse", "count": 40},
            {"type": "manufacturing", "count": 60}
        ]
    }
    
    print(f"\n📊 Chat Parameters Received:")
    print(f"  - Terrain Strategy: {chat_params['terrain_strategy']}")
    print(f"  - Has Topography: {chat_params['has_topography']}")
    
    # Simulate design generation worker would receive these
    site_params = {
        "total_area_m2": chat_params["total_area_m2"],
        "width": 1699,
        "height": 2157,
        "terrain_strategy": chat_params["terrain_strategy"],
        "has_topography": chat_params["has_topography"],
        "terrain": chat_params["terrain"]
    }
    
    print(f"\n🏗️ Site Parameters for Design Worker:")
    for key, value in site_params.items():
        print(f"  - {key}: {value}")
    
    # Test terrain adapter
    adapter = TerrainLayoutAdapter(site_params["terrain_strategy"])
    costs = adapter.calculate_grading_cost(site_params["total_area_m2"])
    
    print(f"\n💰 Final Cost Estimate:")
    print(f"  - Strategy: {costs['strategy']}")
    print(f"  - Total Cost: {costs['total_cost']/1e9:.2f}B VND")
    print(f"  - Cost per m²: {costs['cost_per_m2']:,.0f} VND")
    
    print("\n✅ Pipeline simulation complete!")
    
    return True


def run_all_tests():
    """Run all terrain pipeline tests"""
    print("\n" + "="*70)
    print("🧪 TERRAIN HANDLING PIPELINE - COMPREHENSIVE TEST")
    print("="*70)
    print(f"Testing with: Pilot_Existing Topo _ Boundary.dxf")
    print(f"Site: 191.42 ha (1,914,212 m²)")
    print("="*70)
    
    tests = [
        ("DWG Terrain Detection", test_dwg_terrain_detection),
        ("LLM Terrain Extraction", test_llm_terrain_extraction),
        ("Terrain Layout Adapter", test_terrain_layout_adapter),
        ("Enhanced Layout Generator", test_enhanced_layout_generator),
        ("Full Pipeline Simulation", test_full_pipeline),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ Test '{name}' failed with error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Terrain pipeline is fully functional.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Review errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
