# 🏗️ Hướng Dẫn Thiết Kế Khu Công Nghiệp với AI

## 📁 File Mẫu

Hệ thống cung cấp các file mẫu trong thư mục `examples/`:

| File | Mô tả | Kích thước |
|------|-------|------------|
| [`kcn_song_than_binh_duong.geojson`](../examples/kcn_song_than_binh_duong.geojson) | KCN Sóng Thần, Bình Dương - GeoJSON đầy đủ | ~11KB |
| [`kcn_song_than_binh_duong.dxf`](../examples/kcn_song_than_binh_duong.dxf) | KCN Sóng Thần - DXF format | ~44KB |

---

## 🎯 Cách Sử Dụng

### Bước 1: Tải file khu đất
1. Click vào vùng **"📁 TẢI FILE DXF / GEOJSON"** ở sidebar trái
2. Chọn file `.geojson` hoặc `.dxf` của khu đất
3. Hệ thống sẽ tự động:
   - Hiển thị thông tin diện tích (ha)
   - Hiển thị chu vi (km)
   - Di chuyển bản đồ đến vị trí khu đất
   - Vẽ ranh giới polygon màu xanh lá

### Bước 2: Bật chế độ AI
1. Click **"Chuyển sang chế độ AI"**
2. Một cửa sổ chat AI sẽ xuất hiện ở phần dưới màn hình

### Bước 3: Nhập yêu cầu thiết kế
Sử dụng các mẫu prompt bên dưới để mô tả yêu cầu của bạn.

---

## 💬 MẪU PROMPT THIẾT KẾ

### 📋 Prompt Cơ Bản (Beginner)

#### Mô tả đơn giản
```
Thiết kế khu công nghiệp 50 hectare cho 5 nhà máy sản xuất ô tô với 3000 công nhân.
```

#### Với vị trí cụ thể
```
Thiết kế khu công nghiệp tại Bình Dương, diện tích 100 ha, 
chuyên về điện tử và linh kiện, dự kiến 5000 công nhân.
```

---

### 📋 Prompt Trung Bình (Intermediate)

#### Đa ngành nghề
```
Tôi cần thiết kế khu công nghiệp 80 hectare với:
- 3 nhà máy sản xuất điện tử (mỗi nhà máy 2 ha)
- 2 nhà máy dệt may (mỗi nhà máy 1.5 ha)  
- 4 kho hàng logistics (mỗi kho 3 ha)
- 1 trung tâm hành chính

Yêu cầu:
- Khoảng cách an toàn theo TCVN 7144
- Diện tích xanh tối thiểu 25%
- Đường nội bộ rộng 24m
```

#### Ưu tiên xanh sạch
```
Thiết kế khu công nghiệp sinh thái 120 ha tại Đồng Nai:
- 8 nhà máy sản xuất thực phẩm chế biến
- 4000 công nhân
- Ưu tiên: DIỆN TÍCH XANH CAO (>30%)
- Yêu cầu: Hệ thống xử lý nước thải tập trung
- Tiêu chuẩn: LEED Silver hoặc tương đương
```

---

### 📋 Prompt Nâng Cao (Expert)

#### Khu công nghiệp ô tô
```
Tôi đang quy hoạch khu công nghiệp chuyên ngành ô tô tại Bình Dương:

📍 THÔNG TIN KHU ĐẤT:
- Diện tích: 212 hectare (2,120,000 m²)
- Vị trí: Phường Dĩ An, TP. Dĩ An, Bình Dương
- File ranh giới: kcn_song_than_binh_duong.geojson (đã upload)

🏭 YÊU CẦU NHÀ MÁY:
1. Nhà máy lắp ráp ô tô chính: 25 ha, 2000 công nhân
2. 3 nhà máy linh kiện: mỗi cái 8-10 ha, mỗi cái 500 công nhân
3. 2 nhà máy sơn và xử lý bề mặt: mỗi cái 5 ha (cấp nguy hại CAO)
4. 1 trung tâm R&D: 3 ha, 300 kỹ sư
5. 4 kho logistics: mỗi cái 6 ha

🛣️ YÊU CẦU HẠ TẦNG:
- Đường chính: 30m rộng, 2 làn mỗi hướng
- Đường nội bộ: 12m rộng
- Đường PCCC: 8m, kết nối tất cả nhà máy
- Bãi đỗ xe tải: 200 chỗ
- Bãi đỗ xe con: 1500 chỗ

⚡ YÊU CẦU TIỆN ÍCH:
- Trạm biến áp 110kV, công suất 50 MVA
- Trạm cấp nước: 30,000 m³/ngày
- Xử lý nước thải tập trung: 25,000 m³/ngày
- 3 trạm cứu hỏa trong khu

🌳 YÊU CẦU MÔI TRƯỜNG:
- Diện tích xanh: ≥25% (theo TCVN 7144)
- Vành đai xanh: 50m từ ranh ngoài
- Lối đi bộ xanh kết nối các khu
- Hồ điều hòa: 2 ha

📋 TIÊU CHUẨN ÁP DỤNG:
- TCVN 7144:2014 (Quy hoạch KCN)
- TCVN 6778:2007 (PCCC)
- QCVN 40:2011 (Xả thải nước)
- QCVN 05:2013 (Khí thải)

🎯 ƯU TIÊN:
1. An toàn PCCC (nhà máy sơn cách xa khu lắp ráp)
2. Hiệu quả logistics (kho gần cổng và đường chính)
3. Tiện nghi công nhân (bãi xe gần nhà máy)
```

---

### 📋 Prompt Theo Tình Huống

#### Mở rộng KCN hiện có
```
Tôi đã có file GeoJSON của KCN Sóng Thần với:
- Tổng diện tích: 212 ha
- Đã cho thuê: 85%
- Còn trống: 15% (~32 ha)

Hãy thiết kế phương án quy hoạch cho phần đất còn trống với:
- 2 nhà máy điện tử: 8 ha mỗi cái
- 3 kho hàng: 4 ha mỗi cái
- Đảm bảo kết nối với hạ tầng hiện có
- Không được phá vỡ quy hoạch đã có
```

#### So sánh phương án
```
Với khu đất 50 ha đã upload, hãy tạo 3 phương án thiết kế:

PHƯƠNG ÁN A - Tối ưu chi phí:
- Ít đường nhất có thể
- Mật độ xây dựng cao (55-60%)
- Diện tích xanh tối thiểu (20%)

PHƯƠNG ÁN B - Cân bằng:
- Mật độ xây dựng 45-50%
- Diện tích xanh 25%
- Chi phí trung bình

PHƯƠNG ÁN C - Xanh sạch:
- Mật độ xây dựng thấp (35-40%)
- Diện tích xanh cao (35%+)
- Ưu tiên không gian mở

So sánh 3 phương án theo: chi phí hạ tầng, điểm TCVN, hiệu quả logistics.
```

---

## 📊 Các Thông Số Quan Trọng

### Diện tích theo ngành nghề (m² / công nhân)
| Ngành | Diện tích/CN | Ví dụ |
|-------|-------------|-------|
| Điện tử | 25-35 m² | Samsung: 35 m²/CN |
| Ô tô | 50-80 m² | Toyota: 60 m²/CN |
| Dệt may | 12-18 m² | Nike: 15 m²/CN |
| Thực phẩm | 20-30 m² | Unilever: 25 m²/CN |
| Logistics | 100-150 m² | DHL: 120 m²/vị trí |

### Tỷ lệ phân bổ đất (theo TCVN 7144)
| Hạng mục | Tỷ lệ tối thiểu | Tỷ lệ khuyến nghị |
|----------|-----------------|-------------------|
| Nhà máy + kho | - | 50-60% |
| Đường giao thông | 8-10% | 12-15% |
| Diện tích xanh | 20% | 25-30% |
| Tiện ích công cộng | 3-5% | 5-8% |
| Không gian mở | - | 5-10% |

### Khoảng cách an toàn PCCC
| Cấp nguy hại | Khoảng cách tối thiểu |
|--------------|----------------------|
| Thấp (điện tử, may mặc) | 15m |
| Trung bình (cơ khí, thực phẩm) | 20m |
| Cao (hóa chất, sơn, dầu mỡ) | 25-30m |

---

## 🔧 Tùy Chỉnh Kết Quả

Sau khi AI tạo thiết kế, bạn có thể yêu cầu điều chỉnh:

```
Di chuyển nhà máy A1 sang phía Đông 50m
```

```
Tăng diện tích xanh lên 30%
```

```
Thêm 1 trạm cứu hỏa ở góc Tây Nam
```

```
Mở rộng bãi đỗ xe tải thêm 50 chỗ
```

---

## 📤 Xuất Kết Quả

Sau khi hoàn thành thiết kế:

1. **Xuất DXF**: Click "Xuất DXF" để mở trong AutoCAD
2. **Xuất GeoJSON**: Click "Xuất GeoJSON" để dùng với GIS
3. **Xem báo cáo tuân thủ**: Kiểm tra TCVN 7144 và các quy chuẩn

---

## 📚 Tài Liệu Tham Khảo

- [TCVN 7144:2014](https://vanban.chinhphu.vn) - Quy hoạch xây dựng khu công nghiệp
- [TCVN 6778:2007](https://vanban.chinhphu.vn) - Phòng cháy chữa cháy nhà công nghiệp
- [QCVN 40:2011/BTNMT](https://vanban.chinhphu.vn) - Quy chuẩn nước thải công nghiệp
