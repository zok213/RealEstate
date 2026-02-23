# Tính năng Hiển thị Địa hình Thực tế từ DXF/DWG

## Tổng quan

Tính năng này cho phép **thiết kế khu công nghiệp thông minh** bằng cách:
1. Hiển thị file DXF/DWG trực tiếp trên bản đồ Mapbox với ảnh vệ tinh và địa hình thực tế
2. Tự động phát hiện các đối tượng hiện có (hồ nước, tòa nhà, đường, cây cối)
3. Phân loại đối tượng nào có thể tái sử dụng, đối tượng nào cần phá dỡ
4. Tích hợp vào thuật toán thiết kế để tận dụng cơ sở hạ tầng hiện có thay vì xây mới

## Vấn đề được giải quyết

**Trước đây**: Hệ thống coi mọi khu đất như đất trống, thiết kế từ đầu, bỏ qua:
- Hồ nước hiện có (tốn 500K-1M THB để lấp)
- Đường đã có (tốn hàng triệu để xây lại)
- Tòa nhà còn tốt (phá + xây lại rất tốn kém)
- Cây cối lớn (vi phạm quy định môi trường)

**Giờ đây**: Hệ thống hiểu địa hình thực tế, tận dụng những gì có sẵn, tiết kiệm chi phí và thời gian.

## Quy trình sử dụng

### Bước 1: Tải file DXF/DWG

1. Mở giao diện thiết kế
2. Nhấn "Upload DXF/DWG File"
3. Chọn file bản vẽ hiện trạng (từ CAD)

Hệ thống sẽ:
- Tự động chuyển đổi tọa độ DXF sang tọa độ địa lý (lat/lng)
- Hiển thị trên bản đồ Mapbox với ảnh vệ tinh
- Phát hiện các đối tượng hiện có

### Bước 2: Xác định vị trí (nếu cần)

Nếu file DXF không có thông tin tọa độ, hệ thống yêu cầu bạn:
1. Nhấn 3 điểm trên bản vẽ DXF
2. Nhấn 3 điểm tương ứng trên bản đồ Mapbox
3. Hệ thống tự động tính toán chuyển đổi tọa độ

**Ví dụ**:
- Góc A trên DXF (100, 200) → Lat/Lng trên bản đồ (100.5000°, 13.7500°)
- Góc B trên DXF (500, 200) → Lat/Lng trên bản đồ (100.5200°, 13.7500°)
- Góc C trên DXF (300, 600) → Lat/Lng trên bản đồ (100.5100°, 13.7700°)

### Bước 3: Xem địa hình thực tế

Sau khi tải lên, bạn sẽ thấy:
- **Hình dạng khu đất** chồng lên ảnh vệ tinh thực tế
- **Các đối tượng phát hiện** được tô màu:
  - 🔵 **Màu xanh dương**: Hồ nước, ao
  - 🔶 **Màu xám**: Tòa nhà hiện có
  - 🟡 **Màu vàng**: Đường hiện có
  - 🟢 **Màu xanh lá**: Cây cối, th植vật
  - ⭕ **Đường viền trắng**: Ranh giới khu đất

### Bước 4: Kiểm tra phân tích tự động

Hệ thống tự động phân tích và đề xuất:

#### 🟢 Giữ nguyên (Keep as-is)
- Hồ nước lớn >5000 m² (>3 rai)
  - Lý do: Tốn 500K-1M THB để lấp
  - Tạo vùng cấm xây 20m xung quanh
- Cây cối lớn bán kính >5m
  - Lý do: Bảo vệ môi trường
  - Tạo vùng bảo vệ 15m

#### 🟡 Tái sử dụng/Cải tạo (Reuse/Modify)
- Tòa nhà lớn >2000 m² (>1.25 rai)
  - Chi phí sửa chữa: 3,000 THB/m²
  - Rẻ hơn phá + xây mới: 6,500 THB/m²
  - Có thể dùng làm văn phòng quản lý
- Hồ nhỏ <5000 m²
  - Có thể mở rộng thành bể chứa nước
- Đường dài >100m
  - Có thể nâng cấp, mở rộng
  - Tiết kiệm chi phí xây dựng mới

#### 🔴 Phá dỡ (Demolish)
- Tòa nhà nhỏ <2000 m²
  - Chi phí phá dỡ thấp
  - Không đáng để giữ lại

### Bước 5: Điều chỉnh phân loại (tùy chọn)

Bạn có thể thay đổi quyết định của hệ thống:

**Ví dụ**:
- Hồ nước nhỏ: Hệ thống đề xuất "Tái sử dụng"
  - Bạn muốn giữ nguyên → Nhấn "Keep" → Vùng cấm xây 20m
- Tòa nhà lớn: Hệ thống đề xuất "Tái sử dụng"
  - Bạn muốn phá dỡ → Nhấn "Demolish" → Khu vực trống

**Chi phí ước tính**:
- Mỗi đối tượng hiển thị chi phí:
  - ✅ Giữ nguyên: ฿0
  - 🔧 Sửa chữa: ฿XXX,XXX
  - ❌ Phá dỡ + xây mới: ฿XXX,XXX

### Bước 6: Tạo thiết kế thông minh

Nhấn "Generate Context-Aware Design" - Hệ thống sẽ:

1. **Tránh vùng cấm xây**:
   - Không xây lô đất gần hồ nước giữ lại
   - Tránh cây cối được bảo vệ

2. **Tận dụng cơ sở hạ tầng**:
   - Đường mới nối với đường cũ (thay vì xây hoàn toàn mới)
   - Mở rộng hồ nhỏ thành bể chứa nước (thay vì đào mới)

3. **Chuyển đổi tòa nhà**:
   - Tòa nhà vuông lớn → Văn phòng quản lý
   - Tòa nhà nhỏ → Phá dỡ, xây lô công nghiệp

## Ví dụ thực tế

### Khu công nghiệp 50 rai (80,000 m²)

**Phát hiện được**:
- 3 hồ nước lớn (tổng 15,000 m²)
- 1 đường nhựa dài 500m
- 2 tòa nhà lớn (4,000 m²)
- 5 cây cổ thụ

**Quyết định**:
- ✅ Giữ 3 hồ nước + 5 cây cổ thụ
- 🔧 Tận dụng đường cũ, nâng cấp
- 🔧 Sửa 2 tòa nhà làm văn phòng

**Tiết kiệm**:
1. **Hồ nước**: 15,000 m² × 100 THB/m² = **1.5 triệu THB**
2. **Đường**: 500m × 12m × 800 THB/m² = **4.8 triệu THB**
3. **Tòa nhà**: (Phá+xây: 26M) - (Sửa: 12M) = **14 triệu THB**
4. **Cây cối**: Tránh phạt vi phạm môi trường = **Vô giá**

**Tổng tiết kiệm: ~20 triệu THB (~$570K USD)**

## Lợi ích

### 💰 Chi phí
- Tiết kiệm 10-20% chi phí xây dựng
- Tránh chi phí lấp hồ (rất tốn kém)
- Giảm chi phí phá dỡ không cần thiết

### ⏱️ Thời gian
- Nhanh hơn 2-3 tháng (không cần lấp hồ, phá dỡ)
- Dễ dàng xin phép môi trường (giữ hồ nước, cây cối)

### 🌿 Môi trường
- Bảo vệ nguồn nước tự nhiên
- Giữ cây cối trưởng thành
- Giảm rác thải xây dựng

### 🏆 Cạnh tranh
- Khách hàng hài lòng (tôn trọng địa hình hiện có)
- Thiết kế "thông minh" hơn đối thủ
- Giá thành cạnh tranh hơn

## Công nghệ

### Chuyển đổi tọa độ
- **Affine Transformation**: Chuyển đổi tọa độ DXF (x, y) → Lat/Lng
- **Ma trận 3×3**: Rotation + Scale + Translation
- **Độ chính xác**: RMSE <10m (chấp nhận được)

### Phát hiện đối tượng
- **Layer-based detection**: Tìm theo tên layer (WATER, POND, HO, NUOC, ทางน้ำ)
- **Hình học**: Polyline kín = hồ/tòa nhà, Polyline mở = đường
- **Đa ngôn ngữ**: Hỗ trợ tiếng Anh, Việt, Thái

### Hiển thị bản đồ
- **Mapbox GL JS**: Hiển thị ảnh vệ tinh chất lượng cao
- **GeoJSON**: Format chuẩn cho web mapping
- **Layer toggles**: Bật/tắt từng loại đối tượng

## Cấu hình

### Token Mapbox
Tạo file `.env.local`:
```
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your_token_here
```

### Ngưỡng tùy chỉnh
Có thể điều chỉnh trong code:
```python
WATER_KEEP_THRESHOLD = 5000  # m² - Hồ >5000m² giữ lại
BUILDING_REUSE_THRESHOLD = 2000  # m² - Nhà >2000m² tái sử dụng
ROAD_REUSE_THRESHOLD = 100  # m - Đường >100m tận dụng
```

## Câu hỏi thường gặp

### Q: File DXF của tôi không có tọa độ?
A: Chọn 3 điểm trên bản vẽ, sau đó 3 điểm tương ứng trên bản đồ. Hệ thống tự tính.

### Q: Hệ thống không phát hiện hồ nước?
A: Kiểm tra:
- Layer có tên WATER, POND, HO, NUOC không?
- Hồ có phải polyline kín không?
- Kích thước hồ đủ lớn không? (>100 m²)

### Q: Tôi muốn giữ hồ nhỏ thay vì mở rộng?
A: Vào "Reusable Features Manager", tìm hồ đó, nhấn "Keep" thay vì "Reuse".

### Q: Chi phí ước tính có chính xác không?
A: Đây là ước tính sơ bộ dựa trên:
- Lấp hồ: 100 THB/m²
- Xây đường: 800 THB/m²/m
- Sửa nhà: 3,000 THB/m²
- Phá dỡ: 1,500 THB/m²

Chi phí thực tế phụ thuộc địa điểm, thời điểm.

### Q: Tôi có thể xuất bản đồ không?
A: Có, nhấn nút Export → Chọn định dạng (PNG, PDF, GeoJSON)

## Hỗ trợ

### Lỗi tải file
- Kiểm tra file .dxf hoặc .dwg
- Kích thước file <50MB
- File không bị hỏng

### Bản đồ không hiển thị
- Kiểm tra token Mapbox
- Kiểm tra kết nối internet
- Xóa cache trình duyệt

### Đối tượng phát hiện sai
- Kiểm tra tên layer trong DXF
- Sử dụng DWG Viewer để xem cấu trúc file
- Gửi file mẫu cho đội phát triển

## Kết luận

Tính năng này biến thiết kế khu công nghiệp từ **"xây mới hoàn toàn"** thành **"tận dụng thông minh"**.

Kết quả:
- ✅ Tiết kiệm chi phí 10-20%
- ✅ Nhanh hơn 2-3 tháng
- ✅ Thân thiện môi trường
- ✅ Khách hàng hài lòng hơn

**Đây là lợi thế cạnh tranh lớn so với các công ty thiết kế truyền thống!**
