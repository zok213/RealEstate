# Professional CAD-Style Map Visualization

Hệ thống hiển thị bản đồ quy hoạch KCN theo phong cách chuyên nghiệp CAD với các tính năng:

## 🎨 Tính năng

### 1. **Phong cách Plot chuyên nghiệp**
- ✅ Hiển thị parking spaces (bãi đỗ xe) dạng ô nhỏ bên trong mỗi lô
- ✅ Grid parking pattern theo QCVN (2.5m x 5m mỗi chỗ)
- ✅ Màu sắc zone theo tiêu chuẩn:
  - 🔴 **FACTORY** (Nhà máy sản xuất) - Đỏ
  - 🟠 **WAREHOUSE** (Kho bãi) - Cam
  - 🔵 **SERVICE** (Dịch vụ hành chính) - Xanh dương
  - 🟢 **GREEN** (Cây xanh công viên) - Xanh lá
  - 💧 **WATER** (Mặt nước hồ) - Xanh nước biển

### 2. **Định dạng cây xanh**
- ✅ Tree pattern (mẫu cây) trên các khu vực green zones
- ✅ Circular tree symbols với spacing 10m
- ✅ SVG overlay cho hiệu suất cao

### 3. **Layers theo tiêu chuẩn CAD**
- LAYER 1: Green zones (parks, buffers) với tree pattern
- LAYER 2: Water features (lakes)
- LAYER 3: Lots với zone colors
- LAYER 4: Parking areas (dedicated parking zones)

### 4. **Tuân thủ QCVN 01:2021/BXD**
- ✅ Không có RESIDENTIAL trong KCN (đã loại bỏ)
- ✅ Phân bổ zone: FACTORY 40%, WAREHOUSE 30%, SERVICE 25%, GREEN 5%
- ✅ Green buffer 30m tại perimeter
- ✅ Parking 15% lot depth

## 🚀 Cách sử dụng

### Bước 1: Chạy Backend API
```powershell
cd D:\git\RealEstate\BID25-013\algorithms\backend
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Bước 2: Tạo Optimization Result
1. Mở trình duyệt: http://127.0.0.1:8000/static/index.html
2. Upload file DXF (boundary)
3. Click "Optimize Layout"
4. Đợi pipeline hoàn thành

### Bước 3: Xem Professional Map View
```powershell
cd D:\git\RealEstate\BID25-013\frontend
npm run dev
```

Mở trình duyệt:
- **Main App**: http://localhost:5173
- **Professional Map**: http://localhost:5173?view=professional

## 🎛️ Controls

Trên Professional Map View, bạn có thể:
- 🅿️ **Toggle Parking Spaces** - Bật/tắt hiển thị parking grid
- 🌳 **Toggle Tree Pattern** - Bật/tắt hiển thị tree pattern
- 🔄 **Reload** - Tải lại optimization result mới nhất

## 📊 Legend

Bên phải map có legend hiển thị:
- **ZONE TYPES**: Màu sắc từng loại zone
- **DISPLAY OPTIONS**: Checkboxes để toggle layers

## 🏗️ Kiến trúc Code

### Frontend Components

**OptimizationResultLayer.tsx** (mới tạo)
```
frontend/src/components/MapView/OptimizationResultLayer.tsx
```
- Render lots với zone colors
- Generate parking pattern grid
- Render tree pattern cho green zones
- Layers rendering (parks → water → lots → parking)

**ProfessionalMapDemo.tsx** (mới tạo)
```
frontend/src/ProfessionalMapDemo.tsx
```
- Load optimization result từ API
- Controls panel (parking, trees toggle)
- Statistics display
- Error handling

**MapView.tsx** (đã cập nhật)
```
frontend/src/components/MapView/MapView.tsx
```
- Nhận `optimizationResult` prop
- Tích hợp OptimizationResultLayer
- Updated legend với QCVN zones

### Backend API

**optimization_routes.py** (đã cập nhật)
```
algorithms/backend/api/routes/optimization_routes.py
```
- `GET /api/last-optimization` - Endpoint mới trả về optimization result
- Global storage `_last_optimization_result`
- Separate lots, parks, lakes, parking từ features

**api.ts** (đã cập nhật)
```
frontend/src/services/api.ts
```
- `getOptimizationResult()` - Method mới fetch optimization data

## 🎯 So sánh với phiên bản cũ

| Tính năng | Streamlit (cũ) | React Professional (mới) |
|-----------|----------------|--------------------------|
| Parking spaces | ❌ | ✅ Grid pattern inside lots |
| Tree visualization | ❌ | ✅ SVG pattern |
| Zone colors | ✅ | ✅ (QCVN compliant) |
| Interactive controls | ❌ | ✅ Toggle parking/trees |
| Legend | Basic | Professional với QCVN zones |
| Layer ordering | Manual | Automatic (parks → water → lots → parking) |
| CAD-style | ❌ Marketing | ✅ Professional CAD |

## 📝 Ghi chú kỹ thuật

### Parking Grid Generation
```typescript
// Parameters (QCVN compliant)
const spotWidth = 2.5;  // 2.5m per spot
const spotDepth = 5.0;  // 5m depth
const rowSpacing = 6.0; // 6m between rows
const parkingDepthRatio = 0.15; // 15% of lot depth
```

### Tree Pattern
```typescript
// Tree spacing
const treeSpacing = 0.0001; // ~10m between trees
// Limited to 10x10 grid for performance
const maxRows = 10;
const maxCols = 10;
```

### Zone Color Mapping
```typescript
const ZONE_COLORS = {
  FACTORY: '#ef4444',      // Red
  WAREHOUSE: '#f59e0b',    // Orange
  SERVICE: '#06b6d4',      // Teal
  GREEN: '#22c55e',        // Green
  WATER: '#3b82f6',        // Blue
};
```

## 🔧 Troubleshooting

### Lỗi "No optimization result available"
→ Chạy optimization trước bằng cách upload DXF tại http://127.0.0.1:8000/static/index.html

### Không thấy parking spaces
→ Check toggle "Parking Spaces" đang bật
→ Kiểm tra console log có parking data không

### Không thấy tree pattern
→ Check toggle "Tree Pattern" đang bật
→ Tree chỉ hiển thị trên green zones (parks)

### Map không load
→ Kiểm tra backend đang chạy trên port 8000
→ Kiểm tra frontend dev server đang chạy
→ Check console logs

## 📞 API Endpoints

```
GET  /api/last-optimization     - Get optimization result
POST /api/optimize              - Run optimization (creates result)
GET  /api/health                - Health check
```

## ✨ Next Steps

Để tăng cường thêm:
1. **Export to DXF/DWG** - Xuất ra file CAD với layers
2. **Dimension labels** - Thêm kích thước, tọa độ
3. **Scale bar** - Thước tỷ lệ chuyên nghiệp
4. **North arrow** - Hướng Bắc
5. **Layer management** - Toggle từng layer riêng lẻ
6. **Print layout** - Template in ấn A0/A1

## 🎓 Tài liệu tham khảo

- QCVN 01:2021/BXD - Quy chuẩn kỹ thuật quốc gia về quy hoạch xây dựng
- Leaflet.js - Map library
- React Leaflet - React components for Leaflet
