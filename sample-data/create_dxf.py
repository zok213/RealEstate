"""
Script tạo file DXF cho lô đất KCN May Mặc 50ha - Sóng Thần 1
Chuyển đổi tọa độ WGS84 sang hệ mét cục bộ (Local Metric)
"""

import ezdxf
import math
import os

# --- CẤU HÌNH ---
# Tọa độ WGS84 của lô đất giả định ~50ha ở trung tâm KCN
# Thứ tự: Tây Bắc -> Đông Bắc -> Đông Nam -> Tây Nam
wgs84_plot = [
    (10.900000, 106.751000),  # P1 (NW)
    (10.900000, 106.759000),  # P2 (NE)
    (10.894000, 106.759000),  # P3 (SE)
    (10.894000, 106.751000)   # P4 (SW) - Điểm mốc để tính toán
]

# Lấy thư mục hiện tại của script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_filename = os.path.join(script_dir, "lo_dat_50ha_songthien.dxf")

# --- HÀM CHUYỂN ĐỔI TỌA ĐỘ (Giả lập sang Mét) ---
# Lấy điểm Tây Nam làm gốc để tính khoảng cách mét
ref_lat = wgs84_plot[3][0] 
ref_lon = wgs84_plot[3][1]

def wgs84_to_local_metric(lat, lon, ref_lat, ref_lon):
    """
    Chuyển đổi tọa độ WGS84 (lat/lon) sang tọa độ mét cục bộ.
    Lấy điểm tham chiếu làm gốc (0,0).
    """
    # Bán kính trái đất ước tính (mét)
    R = 6378137 
    
    # Chuyển đổi độ sang radian
    dLat = math.radians(lat - ref_lat)
    dLon = math.radians(lon - ref_lon)
    lat1 = math.radians(ref_lat)
    lat2 = math.radians(lat)
    
    # Công thức tính khoảng cách (đơn giản hóa cho vùng nhỏ)
    # Tính tọa độ Y (vĩ độ)
    y = R * dLat
    # Tính tọa độ X (kinh độ), điều chỉnh theo vĩ độ hiện tại
    x = R * dLon * math.cos((lat1 + lat2) / 2)
    
    return (x, y)


def calculate_polygon_area(points):
    """Tính diện tích polygon bằng công thức Shoelace"""
    n = len(points)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2.0


def main():
    # --- XỬ LÝ CHÍNH ---
    print("=" * 60)
    print("TẠO FILE DXF CHO LÔ ĐẤT KCN MAY MẶC 50HA")
    print("=" * 60)
    
    # 1. Chuyển đổi các điểm WGS84 sang tọa độ mét cục bộ (X, Y)
    metric_points = []
    print("\n📍 Chuyển đổi tọa độ WGS84 -> Mét cục bộ:")
    print("-" * 40)
    
    for i, (lat, lon) in enumerate(wgs84_plot):
        point_metric = wgs84_to_local_metric(lat, lon, ref_lat, ref_lon)
        metric_points.append(point_metric)
        print(f"  P{i+1}: ({lat:.6f}, {lon:.6f}) -> ({point_metric[0]:.2f}m, {point_metric[1]:.2f}m)")
    
    # Tính diện tích
    area_m2 = calculate_polygon_area(metric_points)
    area_ha = area_m2 / 10000
    
    print(f"\n📐 Diện tích lô đất:")
    print(f"  - {area_m2:,.2f} m²")
    print(f"  - {area_ha:.2f} ha")
    
    # Tính kích thước
    width = abs(metric_points[1][0] - metric_points[0][0])
    height = abs(metric_points[0][1] - metric_points[3][1])
    print(f"\n📏 Kích thước:")
    print(f"  - Chiều rộng (Đông-Tây): {width:.2f}m")
    print(f"  - Chiều dài (Nam-Bắc): {height:.2f}m")
    
    # Đóng vòng lặp polygon
    closed_points = metric_points + [metric_points[0]]
    
    # 2. Tạo file DXF
    print(f"\n🔧 Tạo file DXF...")
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Tạo các layer
    doc.layers.add('RANH_LO_DAT', color=2)  # Vàng
    doc.layers.add('CHU_THICH', color=7)     # Trắng
    doc.layers.add('THONG_TIN', color=3)     # Xanh lá
    
    # Vẽ đường Polyline khép kín (ranh lô đất)
    polyline = msp.add_lwpolyline(
        closed_points, 
        dxfattribs={
            'layer': 'RANH_LO_DAT', 
            'color': 2,
            'lineweight': 50  # Đường dày
        }
    )
    polyline.closed = True
    
    # Thêm chú thích góc
    corner_labels = ['NW (Tây Bắc)', 'NE (Đông Bắc)', 'SE (Đông Nam)', 'SW (Tây Nam)']
    for i, (point, label) in enumerate(zip(metric_points, corner_labels)):
        # Điểm đánh dấu
        msp.add_circle(center=point, radius=5, dxfattribs={'layer': 'CHU_THICH', 'color': 1})
        # Nhãn
        msp.add_text(
            f"P{i+1}: {label}",
            dxfattribs={'layer': 'CHU_THICH', 'height': 15}
        ).set_placement(
            (point[0] + 10, point[1] + 10),
            align=ezdxf.enums.TextEntityAlignment.LEFT
        )
    
    # Thêm thông tin dự án ở giữa
    center_x = width / 2
    center_y = height / 2
    
    info_lines = [
        "KCN MAY MẶC SÓNG THẦN",
        f"Diện tích: {area_ha:.2f} ha ({area_m2:,.0f} m²)",
        f"Kích thước: {width:.0f}m x {height:.0f}m",
        "Vị trí: KCN Sóng Thần 1, Bình Dương"
    ]
    
    for i, line in enumerate(info_lines):
        y_offset = center_y + 50 - (i * 25)
        msp.add_text(
            line,
            dxfattribs={'layer': 'THONG_TIN', 'height': 20 if i == 0 else 12}
        ).set_placement(
            (center_x, y_offset),
            align=ezdxf.enums.TextEntityAlignment.CENTER
        )
    
    # Lưu file
    doc.saveas(output_filename)
    
    print(f"✅ Đã tạo xong file: {output_filename}")
    print("\n📋 Hướng dẫn sử dụng trong AutoCAD:")
    print("  1. Mở file DXF trong AutoCAD")
    print("  2. Zoom Extents (lệnh ZE) để xem toàn bộ")
    print("  3. Dùng lệnh AREA hoặc LIST để kiểm tra diện tích")
    print("  4. Đơn vị: Mét (m)")
    print("\n⚠️  Lưu ý: Tọa độ trong file DXF này là tọa độ cục bộ")
    print("    (Local Metric) tính từ góc Tây Nam của lô đất.")


if __name__ == "__main__":
    main()
