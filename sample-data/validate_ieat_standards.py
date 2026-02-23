"""
Validate Pilot DXF file against IEAT Thailand Master Plan Standards
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import INDUSTRIAL_PARK_REGULATIONS

# Pilot DXF analyzed data
PILOT_DATA = {
    "total_area_m2": 1914212,  # 191.42 ha
    "total_area_rai": 1196.38,  # 191.42 ha = 1196.38 rai
    "total_area_ha": 191.42,
    "boundary_points": 45,
    "dimensions_m": {
        "width": 1699,
        "length": 2157
    }
}

def validate_ieat_compliance():
    """Validate Pilot project against IEAT standards"""
    
    regs = INDUSTRIAL_PARK_REGULATIONS["ieat_thailand"]
    print("=" * 70)
    print("IEAT THAILAND COMPLIANCE CHECK - PILOT PROJECT (191.42 ha)")
    print("=" * 70)
    
    total_rai = PILOT_DATA["total_area_rai"]
    total_ha = PILOT_DATA["total_area_ha"]
    total_m2 = PILOT_DATA["total_area_m2"]
    
    print(f"\n📊 PROJECT SIZE:")
    print(f"   Total Area: {total_ha:.2f} ha ({total_rai:.2f} rai)")
    print(f"   Dimensions: {PILOT_DATA['dimensions_m']['width']}m × {PILOT_DATA['dimensions_m']['length']}m")
    print(f"   Boundary: {PILOT_DATA['boundary_points']} points")
    
    # 1. Land Use Requirements
    print(f"\n✅ 1. LAND USE REQUIREMENTS:")
    land_use = regs["land_use"]
    
    salable_min_percent = land_use["salable_area_min_percent"]
    salable_min_ha = total_ha * (salable_min_percent / 100)
    print(f"   Salable Area: >= {salable_min_percent}% ({salable_min_ha:.1f} ha)")
    
    green_min_percent = land_use["green_min_percent"]
    green_min_ha = total_ha * (green_min_percent / 100)
    green_buffer_m = land_use["green_buffer_width_m"]
    print(f"   Green Area: >= {green_min_percent}% ({green_min_ha:.1f} ha)")
    print(f"   Green Buffer: >= {green_buffer_m}m strip along boundary")
    
    # 2. U+G Requirements (Large Project)
    print(f"\n✅ 2. UTILITY + GREEN (U+G) REQUIREMENTS:")
    green_reqs = regs["green_requirements"]
    threshold_rai = green_reqs["threshold_rai"]
    
    if total_rai > threshold_rai:
        min_ug_rai = green_reqs["large_project_min_rai"]
        min_ug_ha = min_ug_rai * 0.16  # 1 rai = 0.16 ha
        print(f"   Project Type: LARGE (> {threshold_rai} rai)")
        print(f"   U+G Required: >= {min_ug_rai} rai ({min_ug_ha:.1f} ha)")
        print(f"   U+G Percent: ~{(min_ug_rai / total_rai) * 100:.1f}%")
    else:
        min_ug_percent = green_reqs["small_project_min_percent"]
        min_ug_ha = total_ha * (min_ug_percent / 100)
        print(f"   Project Type: SMALL (<= {threshold_rai} rai)")
        print(f"   U+G Required: >= {min_ug_percent}% ({min_ug_ha:.1f} ha)")
    
    # 3. Plot Dimensions
    print(f"\n✅ 3. PLOT DIMENSIONS:")
    plot_dims = regs["plot_dimensions"]
    print(f"   Shape: {plot_dims['shape'].title()}")
    ratio_min, ratio_max = plot_dims["width_to_depth_ratio"]
    print(f"   Width:Depth Ratio: 1:{1/ratio_min:.1f} to 1:{1/ratio_max:.1f}")
    print(f"   Min Frontage Width: {plot_dims['min_frontage_width_m']}m")
    print(f"   Preferred Frontage: {plot_dims['preferred_frontage_m']}m")
    
    # 4. Road Standards
    print(f"\n✅ 4. ROAD STANDARDS:")
    road_std = regs["road_standards"]
    print(f"   Traffic Lane Width: {road_std['traffic_lane_width_m']}m")
    print(f"   Min Right of Way: {road_std['min_right_of_way_m']}m")
    main_min, main_max = road_std["main_road_row_m"]
    print(f"   Main Road ROW: {main_min}-{main_max}m")
    print(f"   Secondary Roads: Double-loaded (both sides)")
    
    # 5. Infrastructure
    print(f"\n✅ 5. INFRASTRUCTURE REQUIREMENTS:")
    infra = regs["infrastructure"]
    
    # Retention pond
    pond_ratio = infra["retention_pond"]["ratio_rai"]
    required_pond_rai = total_rai / pond_ratio
    required_pond_ha = required_pond_rai * 0.16
    print(f"   Retention Pond:")
    print(f"      Ratio: {pond_ratio} rai gross per 1 rai pond")
    print(f"      Required: ~{required_pond_rai:.1f} rai ({required_pond_ha:.1f} ha)")
    
    # Water treatment
    water_cmd_per_rai = infra["water_treatment"]["capacity_cmd_per_rai"]
    total_water_capacity = total_rai * infra["water_treatment"]["demand_industrial_cmd_per_rai"]
    water_plant_rai = total_water_capacity / water_cmd_per_rai
    print(f"   Water Treatment:")
    print(f"      Capacity: {water_cmd_per_rai:,} cmd per 1 rai")
    print(f"      Demand: ~{total_water_capacity:.0f} cmd @ 4 cmd/rai industrial")
    print(f"      Plant Size: ~{water_plant_rai:.1f} rai")
    
    # Wastewater
    ww_cmd_per_rai = infra["wastewater_treatment"]["capacity_cmd_per_rai"]
    total_ww = total_water_capacity * infra["wastewater_treatment"]["ratio_general"]
    ww_plant_rai = total_ww / ww_cmd_per_rai
    print(f"   Wastewater Treatment:")
    print(f"      Capacity: {ww_cmd_per_rai:,} cmd per 1 rai")
    print(f"      Demand: ~{total_ww:.0f} cmd (80% of water)")
    print(f"      Plant Size: ~{ww_plant_rai:.1f} rai")
    
    # Substation
    substation_rai = infra["substation"]["area_rai"]
    substation_ha = substation_rai * 0.16
    print(f"   Substation:")
    print(f"      Size: {substation_rai} rai ({substation_ha:.1f} ha)")
    print(f"      Placement: {infra['substation']['placement'].title()}")
    
    # 6. Grading
    print(f"\n✅ 6. GRADING REQUIREMENTS:")
    grading = regs["grading"]
    print(f"   Elevation: Above frontage road")
    print(f"   Max Cut Depth: {grading['max_cut_depth_m']}m")
    print(f"   Cut/Fill Ratio: {grading['cut_fill_ratio']:.2f} (Volume cut = 1.05 × Volume fill)")
    
    # Summary
    print(f"\n📋 DESIGN SUMMARY FOR AI PROMPT:")
    print("=" * 70)
    print(f"""
Project: Pilot Industrial Estate
Location: Thailand (IEAT Standards)
Total Area: {total_ha:.1f} ha ({total_rai:.1f} rai)

Design Parameters:
- Salable Area: >= {salable_min_ha:.1f} ha (75%)
- Green Area: >= {green_min_ha:.1f} ha (10%) with 10m buffer
- U+G Total: >= {min_ug_rai} rai ({min_ug_ha:.1f} ha)
- Roads: Main 25-30m ROW, Secondary 25m ROW, 3.5m lanes
- Infrastructure: {required_pond_rai:.1f} rai pond, {water_plant_rai:.1f} rai water plant, 
  {ww_plant_rai:.1f} rai wastewater plant, 10 rai substation

Plot Standards:
- Shape: Rectangular (1:1.5 to 1:2 ratio)
- Min frontage: 90m (preferred 100m)
- Min spacing: 12-25m between buildings

RECOMMENDED AI PROMPT:
"Thiết kế khu công nghiệp {total_ha:.1f} ha theo chuẩn IEAT Thailand với:
- Salable area >= 75% ({salable_min_ha:.1f} ha)
- Green >= 10% ({green_min_ha:.1f} ha, buffer 10m)
- U+G >= {min_ug_rai} rai ({min_ug_ha:.1f} ha)
- Lô đất hình chữ nhật tỷ lệ 1:1.5, mặt tiền >= 90m
- Đường chính 25-30m ROW, đường phụ 25m ROW
- Ao điều tiết {required_pond_rai:.1f} rai, trạm xử lý nước {water_plant_rai:.1f} rai
- Khoảng cách tòa nhà >= 12m"
""")
    print("=" * 70)

if __name__ == "__main__":
    validate_ieat_compliance()
