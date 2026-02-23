"""
IEAT Thailand Compliance Checker for Pilot Project
Based on Master Plan Design Criteria_vSent15Sep25_MFEC
"""
import ezdxf

# IEAT Thailand Standards (from customer requirements)
IEAT_STANDARDS = {
    "land_use_ratios": {
        "total_area": 3415.57,  # rai (191.42 ha)
        "salable_area_min": 0.7759,  # 77.59%
        "utility_area": 0.1236,  # 12.36%
        "green_area_min": 0.1002,  # 10.02%
    },
    "plot_design": {
        "shape": "rectangular",
        "width_to_depth_ratio": (1.0, 2.0),  # 1:1.5 to 1:2
        "min_frontage_width": 90,  # meters
        "rectangular_ratio_range": (0.5, 0.6),  # W/L ratio
    },
    "road_standards": {
        "traffic_lane_width": 3.5,  # meters
        "min_right_of_way": 25,  # meters
        "main_road_row": "IEAT_ROW + safety_factor",
        "secondary_roads": "double_loaded",
    },
    "green_buffer": {
        "min_percentage": 10,  # % of GA
        "min_strip_width": 10,  # meters from boundary
        "large_project_rule": {
            "threshold": 1000,  # rai
            "utility_plus_green_min": 250,  # rai when TA > 1000
            "utility_plus_green_percentage": 25,  # % when TA <= 1000
        }
    },
    "utilities": {
        "retention_pond": {
            "ratio": 20,  # rai GA per 1 rai pond
            "elevation": "higher_than_downstream",
        },
        "water_treatment": {
            "capacity_per_rai": 2000,  # cmd/rai
            "demand": {
                "commercial": 3,  # cmd/rai
                "standard_industrial": 4,  # cmd/rai
                "power_plant": 50,  # cmd/rai
            }
        },
        "wastewater_treatment": {
            "capacity_per_rai": 500,  # cmd/rai
            "general_ratio": 0.80,  # 80% of water demand
            "powerplant_ratio": 0.50,  # 50% of water demand
        },
        "substation": {
            "area": 10,  # rai
            "dimension": 90,  # meters
            "location": "center",
        }
    },
    "cut_and_fill": {
        "elevation": "higher_than_frontage_road",
        "max_cut_depth": 5,  # meters
        "volume_ratio": 1.05,  # cut/fill ratio
    },
    "design_priorities": [
        "1. Engineering information (Title deeds, Topo, Hydro, Soil)",
        "2. Regulatory Requirements (IEAT, ONEP, etc.)",
        "3. Industry Practices",
        "4. Target customers' requirements",
        "5. Estimated land grading cost (price*volume)",
    ]
}


def analyze_pilot_project(dxf_file='Pilot_Existing Topo _ Boundary.dxf'):
    """Analyze DXF and check IEAT compliance"""
    
    try:
        doc = ezdxf.readfile(dxf_file)
        msp = doc.modelspace()
        
        # Get all polylines
        polylines = []
        for entity in msp:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = list(entity.get_points())
                if len(points) > 2:
                    polylines.append(points)
        
        print(f"Found {len(polylines)} polylines")
        
        # Find boundary (largest area)
        def calculate_area(points):
            n = len(points)
            area = 0.0
            for i in range(n):
                j = (i + 1) % n
                area += points[i][0] * points[j][1]
                area -= points[j][0] * points[i][1]
            return abs(area) / 2.0
        
        max_area = 0
        largest = None
        for poly in polylines:
            area = calculate_area(poly)
            if area > max_area:
                max_area = area
                largest = poly
        
        # Convert to rai (1 rai = 1600 m²)
        area_m2 = max_area
        area_rai = area_m2 / 1600
        area_ha = area_m2 / 10000
        
        print(f"\n{'='*70}")
        print(f"📊 PILOT PROJECT ANALYSIS (IEAT THAILAND STANDARDS)")
        print(f"{'='*70}")
        
        print(f"\n🏗️ SITE INFORMATION:")
        print(f"   Total Area: {area_rai:.2f} rai ({area_ha:.2f} ha)")
        print(f"   Area (m²): {area_m2:,.0f} m²")
        print(f"   Boundary Points: {len(largest)}")
        
        xs = [p[0] for p in largest]
        ys = [p[1] for p in largest]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        print(f"   Dimensions: {width:.0f}m × {height:.0f}m")
        
        # Calculate IEAT-compliant land use
        std = IEAT_STANDARDS["land_use_ratios"]
        
        salable_rai = area_rai * std["salable_area_min"]
        utility_rai = area_rai * std["utility_area"]
        green_rai = area_rai * std["green_area_min"]
        
        print(f"\n📋 IEAT LAND USE BREAKDOWN:")
        print(f"   ├─ Salable Area: {salable_rai:.2f} rai "
              f"({std['salable_area_min']*100:.2f}%)")
        print(f"   ├─ Utility Area:  {utility_rai:.2f} rai "
              f"({std['utility_area']*100:.2f}%)")
        print(f"   └─ Green Area:   {green_rai:.2f} rai "
              f"({std['green_area_min']*100:.2f}%)")
        
        # Utility breakdown
        util = IEAT_STANDARDS["utilities"]
        retention_pond_rai = area_rai / util["retention_pond"]["ratio"]
        
        print(f"\n🏭 UTILITY INFRASTRUCTURE:")
        print(f"   ├─ Retention Pond: {retention_pond_rai:.2f} rai")
        print(f"   ├─ Water Treatment: "
              f"{salable_rai * util['water_treatment']['demand']['standard_industrial']:.0f} cmd")
        print(f"   ├─ Wastewater Treatment: "
              f"{salable_rai * util['wastewater_treatment']['capacity_per_rai']:.0f} cmd")
        print(f"   └─ Substation: {util['substation']['area']} rai "
              f"({util['substation']['dimension']}m)")
        
        # Road standards
        road = IEAT_STANDARDS["road_standards"]
        print(f"\n🛣️ ROAD STANDARDS:")
        print(f"   ├─ Traffic Lane: {road['traffic_lane_width']}m width")
        print(f"   ├─ Min ROW: {road['min_right_of_way']}m")
        print(f"   └─ Layout: {road['secondary_roads']}")
        
        # Green buffer
        green = IEAT_STANDARDS["green_buffer"]
        print(f"\n🌳 GREEN REQUIREMENTS:")
        print(f"   ├─ Min %: {green['min_percentage']}% of GA")
        print(f"   ├─ Buffer Width: {green['min_strip_width']}m from boundary")
        
        if area_rai > green["large_project_rule"]["threshold"]:
            util_green_min = green["large_project_rule"]["utility_plus_green_min"]
            print(f"   └─ U+G Requirement: ≥{util_green_min} rai "
                  f"(project > 1000 rai)")
        else:
            util_green_pct = \
                green["large_project_rule"]["utility_plus_green_percentage"]
            print(f"   └─ U+G Requirement: ≥{util_green_pct}% "
                  f"(project ≤ 1000 rai)")
        
        # Plot design
        plot = IEAT_STANDARDS["plot_design"]
        print(f"\n📐 PLOT DESIGN STANDARDS:")
        print(f"   ├─ Shape: {plot['shape'].title()}")
        print(f"   ├─ W:D Ratio: 1:{plot['width_to_depth_ratio'][0]:.1f} "
              f"to 1:{plot['width_to_depth_ratio'][1]:.1f}")
        print(f"   ├─ Min Frontage: {plot['min_frontage_width']}m")
        print(f"   └─ Rectangular Ratio: "
              f"{plot['rectangular_ratio_range'][0]}-"
              f"{plot['rectangular_ratio_range'][1]}")
        
        # Generate prompt
        print(f"\n💬 AI DESIGN PROMPT (IEAT COMPLIANT):")
        print(f"{'─'*70}")
        prompt = f"""Thiết kế masterplan khu công nghiệp {area_rai:.0f} rai \
({area_ha:.1f} ha) theo chuẩn IEAT Thailand:

📊 Phân bổ diện tích:
- Salable: {salable_rai:.0f} rai ({std['salable_area_min']*100:.1f}%)
- Utility: {utility_rai:.0f} rai ({std['utility_area']*100:.1f}%)
- Green: {green_rai:.0f} rai ({std['green_area_min']*100:.1f}%)

🏭 Cơ sở hạ tầng:
- Retention pond: {retention_pond_rai:.1f} rai
- Substation: {util['substation']['area']} rai tại trung tâm
- Water treatment: {util['water_treatment']['capacity_per_rai']} cmd/rai
- Wastewater: {util['wastewater_treatment']['capacity_per_rai']} cmd/rai

📐 Tiêu chuẩn lô đất:
- Hình chữ nhật, tỷ lệ W:D = 1:1.5 đến 1:2
- Frontage tối thiểu: {plot['min_frontage_width']}m
- Double-loaded roads

🛣️ Giao thông:
- ROW tối thiểu: {road['min_right_of_way']}m
- Traffic lane: {road['traffic_lane_width']}m

🌳 Cây xanh:
- Buffer strip: {green['min_strip_width']}m dọc biên giới
- Tối thiểu: {green['min_percentage']}% tổng diện tích
"""
        print(prompt)
        print(f"{'─'*70}")
        
        return {
            "area_rai": area_rai,
            "area_ha": area_ha,
            "area_m2": area_m2,
            "salable_rai": salable_rai,
            "utility_rai": utility_rai,
            "green_rai": green_rai,
            "compliance": "IEAT_THAILAND",
            "prompt": prompt
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = analyze_pilot_project()
    if result:
        print(f"\n✅ Analysis complete. Use the prompt above for AI design.")
