"""
Analyze Pilot DXF file to extract area and create optimal design scenario
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import ezdxf
    
    # Read the DXF file
    doc = ezdxf.readfile('Pilot_Existing Topo _ Boundary.dxf')
    msp = doc.modelspace()
    
    # Get all polylines and lines to find boundary
    polylines = []
    for entity in msp:
        if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
            points = list(entity.get_points())
            if len(points) > 2:
                polylines.append(points)
    
    print(f"Found {len(polylines)} polylines total")
    
    # Calculate area using shoelace formula
    def calculate_area(points):
        n = len(points)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0
    
    # Find largest polyline BY AREA (not by point count)
    if polylines:
        largest = None
        max_area = 0
        
        for poly in polylines:
            area = calculate_area(poly)
            if area > max_area:
                max_area = area
                largest = poly
        
        area_m2 = max_area
        area_ha = area_m2 / 10000
        
        print(f"\n🏗️ THÔNG TIN KHU ĐẤT:")
        print(f"Diện tích: {area_ha:.2f} ha ({area_m2:,.0f} m²)")
        print(f"Số điểm boundary: {len(largest)}")
        
        # Get bounds
        xs = [p[0] for p in largest]
        ys = [p[1] for p in largest]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        print(f"Kích thước: {width:.0f}m × {height:.0f}m")
        
        # Create optimal scenario based on area
        print(f"\n🎯 KỊCH BẢN THIẾT KẾ TỐI ƯU:")
        print(f"=" * 60)
        
        # Calculate optimal distribution
        total_gfa = area_m2 * 0.4  # 40% GFA
        
        # Distribution: 60% industrial, 30% warehouse, 10% admin
        industrial_gfa = total_gfa * 0.6
        warehouse_gfa = total_gfa * 0.3
        admin_gfa = total_gfa * 0.1
        
        print(f"""
THAM SỐ DỰ ÁN:
- Diện tích khu đất: {area_ha:.1f} ha
- Tổng diện tích sàn (GFA): {total_gfa/10000:.1f} ha
- FAR (Hệ số sử dụng đất): 0.4
- Độ phủ xanh: 15%
- Hành lang giao thông: 20m

PHÂN BỔ CÔNG NĂNG:
1. Nhà máy sản xuất (Industrial):
   - Diện tích sàn: {industrial_gfa:,.0f} m²
   - Số tầng: 1-2 tầng
   - Chiều cao: 8-12m
   - Mật độ: 60% tổng GFA
   
2. Kho bãi (Warehouse):
   - Diện tích sàn: {warehouse_gfa:,.0f} m²
   - Số tầng: 1 tầng
   - Chiều cao: 6-10m
   - Mật độ: 30% tổng GFA
   
3. Văn phòng & Hành chính (Admin):
   - Diện tích sàn: {admin_gfa:,.0f} m²
   - Số tầng: 2-3 tầng
   - Chiều cao: 12-15m
   - Mật độ: 10% tổng GFA

YÊU CẦU KỞ THUẬT IEAT THAILAND:
✅ Khoảng cách an toàn giữa các tòa nhà: ≥12m
✅ Chiều rộng đường nội bộ: ≥12m (đường chính), ≥6m (ngõ)
✅ Diện tích cây xanh: ≥15% tổng diện tích
✅ Hệ số sử dụng đất (FAR): 0.3-0.5
✅ Mật độ xây dựng: ≤40%

MÔ TẢ CHI TIẾT:
Khu công nghiệp được quy hoạch với mục tiêu tối ưu hóa hiệu quả sử dụng 
đất và đảm bảo tuân thủ các quy chuẩn IEAT Thailand. Bố cục được thiết kế với:

- Khu sản xuất: Tập trung ở phía trung tâm, tận dụng không gian lớn
- Khu kho bãi: Bố trí gần đường vào chính, thuận tiện logistics
- Khu hành chính: Đặt ở vị trí dễ tiếp cận, tách biệt với sản xuất
- Cây xanh: Phân bố đều khắp khu vực, tạo vành đai xanh
- Hệ thống giao thông: Đường chính 20m, đường nội bộ 12m, ngõ 6m

PROMPT ĐỀ XUẤT CHO AI:
"Thiết kế khu công nghiệp {area_ha:.1f} ha với phân bổ: 60% nhà máy sản 
xuất (1-2 tầng, 8-12m cao), 30% kho bãi (1 tầng, 6-10m cao), 10% văn phòng 
(2-3 tầng, 12-15m cao). FAR 0.4, độ phủ xanh 15%, đường nội bộ 12-20m. 
Tổng diện tích sàn {total_gfa/10000:.1f} ha. Tuân thủ IEAT Thailand về khoảng 
cách an toàn (≥12m giữa các tòa nhà) và mật độ xây dựng (≤40%)."
""")
        
    else:
        print("❌ Không tìm thấy polyline boundary trong file DXF")
        
except Exception as e:
    print(f"❌ Lỗi: {e}")
    import traceback
    traceback.print_exc()
