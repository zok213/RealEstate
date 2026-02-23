# BỘ CÂU HỎI XÁC NHẬN CUỐI CÙNG VỚI KHÁCH HÀNG
# FINAL CUSTOMER CONFIRMATION QUESTIONNAIRE

**Ngày tạo:** 23 Tháng 1, 2026  
**Phiên bản:** 1.0  
**Mục đích:** Xác nhận toàn diện yêu cầu và kỳ vọng trước khi triển khai chính thức

---

## 📋 HƯỚNG DẪN SỬ DỤNG

### Cách sử dụng bộ câu hỏi này:
1. **Gửi trước:** Gửi file này cho khách hàng trước cuộc họp 3-5 ngày
2. **Họp trực tiếp:** Đi qua từng phần, ghi chú câu trả lời chi tiết
3. **Ưu tiên:** Tập trung vào các phần đánh dấu ⚠️ (có rủi ro cao)
4. **Ghi chép:** Sử dụng cột "Câu trả lời khách hàng" và "Hành động tiếp theo"
5. **Sign-off:** Yêu cầu khách hàng ký xác nhận ở cuối document

---

## PHẦN A: THÔNG TIN DỰ ÁN & PHẠM VI

### A1. Thông tin cơ bản dự án ✅

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 1. Tên chính thức của dự án? | Đặt tên hệ thống, báo cáo | | |
| 2. Vị trí dự án (tỉnh/thành, quận/huyện, xã/phường)? | Xác định quy chuẩn địa phương | | |
| 3. Diện tích đất (rai/ha)? | Tính toán quy mô, ràng buộc IEAT | | |
| 4. Loại hình khu công nghiệp? (Đa ngành/chuyên biệt) | Thiết lập ràng buộc ngành | | |
| 5. Timeline dự kiến triển khai? (tháng/năm bắt đầu-kết thúc) | Lập lịch phát triển | | |
| 6. Ngân sách tổng dự án? (triệu/tỷ THB) | Tối ưu hóa chi phí | | |
| 7. Mục tiêu ROI mong muốn? (%) | Thiết lập hàm mục tiêu tài chính | | |

### A2. Phạm vi dự án và ranh giới ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 8. Hệ thống có thiết kế TOÀN BỘ khu công nghiệp từ đầu? Hay chỉ mở rộng/tái thiết kế một phần? | Xác định scope | | |
| 9. Có cơ sở hạ tầng sẵn có cần giữ lại không? (đường, điện, nước, thoát nước, ao) | Feature reuse system | | |
| 10. Có phải tích hợp với các khu hiện tại không? Nếu có, ở đâu? | Ràng buộc kết nối | | |
| 11. Có yêu cầu phân khu/phân giai đoạn phát triển không? | Incremental design | | |

### A3. Người dùng cuối và stakeholder ✅

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 12. Ai sẽ sử dụng hệ thống này? (KTS, kỹ sư, PM, giám đốc) | User persona, UI/UX | | |
| 13. Bao nhiêu người dùng đồng thời? | Cấu hình server, database | | |
| 14. Người phê duyệt cuối cùng là ai? | Workflow approval | | |
| 15. Có cần training người dùng không? Bao nhiêu người? | Lập kế hoạch đào tạo | | |

---

## PHẦN B: YÊU CẦU KỸ THUẬT & DỮ LIỆU

### B1. Dữ liệu đầu vào ⚠️ (CAO NHẤT)

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 16. Dữ liệu boundary/ranh giới: Có sẵn không? Định dạng gì? (DXF/DWG/SHP/KML) | Parser selection | | |
| 17. Dữ liệu địa hình/topo: Có contour lines không? Khoảng cách đường đồng mức? (1m/2m/5m) | DEM resolution | | |
| 18. Nếu không có topo, có chấp nhận dùng DEM công khai (độ phân giải 30m) không? | Fallback option | | |
| 19. Có điểm cao độ (spot elevations) không? Mật độ như thế nào? | Accuracy improvement | | |
| 20. Có dữ liệu thủy văn (sông, kênh, ao, hồ) không? Layer tên gì? | Water feature detection | | |
| 21. Có dữ liệu đất (soil data, bearing capacity) không? | Foundation analysis | | |
| 22. Có dữ liệu hạ tầng sẵn có (đường, điện, nước) không? Trong DXF hay file riêng? | Reuse system | | |
| 23. Có dữ liệu về đường cao tốc/đường chính xung quanh không? Vị trí entrance mong muốn? | Entrance placement | | |

### B2. Chất lượng và độ chính xác dữ liệu ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 24. Hệ tọa độ của DXF/DWG? (UTM Zone 47/48, WGS84, VN2000) | Coordinate transformation | | |
| 25. Đơn vị trong file DXF? (meters/millimeters) | Unit conversion | | |
| 26. Dữ liệu được đo đạc khi nào? Có cập nhật không? | Data freshness | | |
| 27. Độ chính xác yêu cầu? (cm/dm/m) | Tolerance settings | | |
| 28. Có kiểm tra chất lượng DXF trước khi import không? | Pre-validation | | |

### B3. Định dạng đầu ra ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 29. Output format mong muốn? (DXF/DWG/GeoJSON/SHP/PDF) | Exporter implementation | | |
| 30. Có cần AutoCAD version cụ thể không? (2018/2020/2024) | DXF version | | |
| 31. Layer structure mong muốn trong DXF output? (tên layer, màu, linetype) | Layer naming convention | | |
| 32. Có cần 3D model (3D DXF, SKP, FBX) không? | 3D export | | |
| 33. Có cần báo cáo PDF tự động không? Template như thế nào? | Report generation | | |

---

## PHẦN C: YÊU CẦU THIẾT KẾ & TỐI ƯU HÓA

### C1. Mục tiêu tối ưu hóa chính ✅

**Xin khách hàng xếp hạng từ 1-5 (1 = không quan trọng, 5 = cực kỳ quan trọng):**

| Mục tiêu | Mức độ (1-5) | Trọng số % | Ghi chú | Hành động |
|----------|-------------|-----------|---------|-----------|
| 34. Số lượng lô (maximize lots) | | | | |
| 35. ROI/lợi nhuận (maximize profit) | | | | |
| 36. Chất lượng lô (lot quality - hình dạng, slope) | | | | |
| 37. Hiệu suất đường (road efficiency - minimize length) | | | | |
| 38. Chi phí xây dựng (minimize cost) | | | | |
| 39. Thời gian thi công (minimize timeline) | | | | |
| 40. Tuân thủ quy chuẩn (compliance score) | | | | |

⚠️ **LƯU Ý:** Tổng trọng số phải = 100%. Nếu có conflict, ưu tiên theo thứ tự nào?

### C2. Ràng buộc về lô đất (Lot Constraints) ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 41. Diện tích lô tối thiểu? (m²) | Min lot size | | |
| 42. Diện tích lô tối đa? (m²) | Max lot size | | |
| 43. Diện tích lô MỤC TIÊU? (m² - phổ biến nhất) | Target lot size | | |
| 44. Độ lệch cho phép? (± m² hoặc ± %) | Lot size tolerance | | |
| 45. Tỷ lệ chiều dài/rộng? (1:1.5, 1:2, custom) | Aspect ratio | | |
| 46. Chiều rộng mặt tiền tối thiểu? (m) | Min frontage | | |
| 47. Độ dốc tối đa cho phép? (%) | Max slope | | |
| 48. Có yêu cầu hướng lô (orientation) không? (Bắc, Nam, tránh Tây) | Orientation constraint | | |

### C3. Phân loại lô theo ngành công nghiệp ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 49. Có cần phân loại lô theo ngành không? (Ô tô, thực phẩm, điện tử, logistics, dệt may) | Industry templates | | |
| 50. Nếu có, tỷ lệ % cho mỗi ngành? | Lot type distribution | | |
| 51. Có ràng buộc vị trí cho từng ngành không? (VD: thực phẩm gần nguồn nước, logistics gần entrance) | Spatial constraints | | |
| 52. Có yêu cầu đặc biệt nào? (clean room, cold storage, heavy loads) | Custom requirements | | |

### C4. Hạ tầng và tiện ích ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 53. Hệ thống đường: Độ rộng ROW mong muốn? (m) | Road width | | |
| 54. Có yêu cầu về phân cấp đường không? (Main road, secondary, access) | Road hierarchy | | |
| 55. Có cần vòng xuyến (roundabout) không? | Intersection type | | |
| 56. Hệ thống thoát nước: Tỷ lệ ao/diện tích? (1:20 default) | Retention pond ratio | | |
| 57. Vị trí ao: Tập trung hay phân tán? | Pond placement strategy | | |
| 58. Trạm xử lý nước: Công suất yêu cầu? (cmd/rai hoặc total cmd) | Water treatment capacity | | |
| 59. Trạm xử lý nước thải: Công suất yêu cầu? (cmd/rai) | Wastewater capacity | | |
| 60. Trạm điện phụ: Công suất yêu cầu? (MVA) hoặc để hệ thống tự tính? | Substation sizing | | |
| 61. Có yêu cầu vị trí cụ thể cho các tiện ích này không? | Infrastructure location | | |

### C5. Entrance và kết nối giao thông ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 62. Số lượng entrance mong muốn? (1 chính + 1 phụ, hoặc nhiều hơn) | Entrance count | | |
| 63. Vị trí entrance ưu tiên? (phía nào của boundary) | Entrance location | | |
| 64. Khoảng cách an toàn từ ngã tư/khúc cua? (m) | Safety distance | | |
| 65. Có yêu cầu về góc vuông với đường cao tốc không? (80-100°) | Perpendicular entrance | | |
| 66. Có kế hoạch mở rộng entrance trong tương lai không? | Future expansion | | |

---

## PHẦN D: QUY CHUẨN & TUÂN THỦ

### D1. Quy chuẩn IEAT Thailand ✅

**Xác nhận lại các quy chuẩn áp dụng:**

| Quy chuẩn | Giá trị hiện tại | Có thay đổi không? | Giá trị mới | Hành động |
|-----------|------------------|-------------------|-------------|-----------|
| 67. Diện tích bán được (Salable area) | ≥75% | | | |
| 68. Không gian xanh (Green area) | ≥10% | | | |
| 69. Tiện ích + xanh (U+G) cho TA >1000 rai | ≥250 rai | | | |
| 70. Tiện ích + xanh (U+G) cho TA ≤1000 rai | ≥25% | | | |
| 71. Dải đệm xanh (Buffer strip) | ≥10m | | | |
| 72. Tỷ lệ lô (Plot ratio) | 1:1.5 to 1:2 | | | |
| 73. Chiều rộng mặt tiền tối thiểu | ≥90m | | | |
| 74. ROW đường chính | ≥25m | | | |

### D2. Quy chuẩn địa phương ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 75. Có quy hoạch địa phương (local zoning) đặc biệt không? | Local compliance | | |
| 76. Có yêu cầu đặc biệt từ ONEP (Office of Natural Resources and Environmental Policy and Planning)? | Water compliance | | |
| 77. Có yêu cầu EIA (Environmental Impact Assessment) không? | Environmental check | | |
| 78. Có quy định về phòng cháy chữa cháy (fire code) cụ thể không? | Fire safety | | |
| 79. Có quy định về khoảng cách đến khu dân cư? (m) | Buffer zone | | |

---

## PHẦN E: GIAO DIỆN VÀ TRẢI NGHIỆM NGƯỜI DÙNG

### E1. Yêu cầu giao diện người dùng ✅

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 80. Ngôn ngữ chính? (Tiếng Thái, Tiếng Anh, Tiếng Việt) | Localization | | |
| 81. Có cần hỗ trợ đa ngôn ngữ không? | i18n implementation | | |
| 82. Thiết bị sử dụng chính? (Desktop, tablet, cả hai) | Responsive design | | |
| 83. Trình duyệt chính? (Chrome, Edge, Safari) | Browser compatibility | | |
| 84. Có yêu cầu về màu sắc/brand identity không? | UI theming | | |

### E2. Tính năng mong muốn ⚠️

**Xin khách hàng đánh dấu các tính năng cần thiết:**

| Tính năng | Cần thiết? | Ưu tiên | Ghi chú | Hành động |
|-----------|-----------|---------|---------|-----------|
| 85. Upload DXF/DWG | ☐ Có ☐ Không | P0/P1/P2 | | |
| 86. Xem 2D map (MapBox) | ☐ Có ☐ Không | | | |
| 87. Xem 3D (Three.js) | ☐ Có ☐ Không | | | |
| 88. Constraint editor (UI form) | ☐ Có ☐ Không | | | |
| 89. Constraint từ text (AI parsing) | ☐ Có ☐ Không | | | |
| 90. Chạy optimization | ☐ Có ☐ Không | | | |
| 91. So sánh nhiều design | ☐ Có ☐ Không | | | |
| 92. Scoring matrix dashboard | ☐ Có ☐ Không | | | |
| 93. Financial metrics panel | ☐ Có ☐ Không | | | |
| 94. Timeline estimator | ☐ Có ☐ Không | | | |
| 95. Export DXF/PDF | ☐ Có ☐ Không | | | |
| 96. Chatbot support | ☐ Có ☐ Không | | | |
| 97. Lưu/tải project | ☐ Có ☐ Không | | | |
| 98. Versioning (lịch sử thiết kế) | ☐ Có ☐ Không | | | |
| 99. Collaboration (multi-user) | ☐ Có ☐ Không | | | |
| 100. Mobile app | ☐ Có ☐ Không | | | |

### E3. Workflow mong muốn ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 101. Người dùng có muốn chỉnh tay (manual editing) sau khi AI generate không? | Manual override | | |
| 102. Có cần approval workflow không? (Design → Review → Approve) | Workflow engine | | |
| 103. Có cần comment/feedback trên design không? | Collaboration feature | | |
| 104. Có cần export intermediate results không? (DEM, road network only, etc.) | Partial export | | |

---

## PHẦN F: HIỆU NĂNG & KHẢ NĂNG MỞ RỘNG

### F1. Yêu cầu hiệu năng ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 105. Thời gian optimization chấp nhận được? (giây/phút) | Algorithm tuning | | |
| 106. Quy mô dự án lớn nhất? (rai/ha) | Scalability testing | | |
| 107. Số lượng lô tối đa trong 1 design? | Memory allocation | | |
| 108. Có chấp nhận tối ưu lâu hơn để có kết quả tốt hơn không? | GA generations | | |

### F2. Triển khai và môi trường ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 109. Deploy ở đâu? (Cloud/On-premise/Hybrid) | Infrastructure setup | | |
| 110. Nếu cloud, provider nào? (AWS/Azure/GCP) | Cloud configuration | | |
| 111. Có yêu cầu về security/authentication không? (SSO, LDAP, OAuth) | Auth implementation | | |
| 112. Có yêu cầu về backup/disaster recovery không? | Backup strategy | | |
| 113. Có cần API cho hệ thống khác tích hợp không? | API documentation | | |

---

## PHẦN G: TÀI CHÍNH VÀ ROI

### G1. Tính toán chi phí ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 114. Chi phí san lấp (cut/fill): Đơn giá? (THB/m³) | Cost calculation | | |
| 115. Chi phí đường: Đơn giá? (THB/m²) | Road cost | | |
| 116. Chi phí hệ thống nước: Đơn giá? (THB/m hoặc lump sum) | Water cost | | |
| 117. Chi phí hệ thống điện: Đơn giá? (THB/m hoặc lump sum) | Electrical cost | | |
| 118. Chi phí thoát nước: Đơn giá? (THB/m) | Drainage cost | | |
| 119. Chi phí cây xanh: Đơn giá? (THB/m²) | Green space cost | | |
| 120. Chi phí các tiện ích khác? (retention pond, treatment plant) | Infrastructure cost | | |

### G2. Tính toán doanh thu ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 121. Giá bán lô dự kiến? (THB/m² hoặc theo ngành) | Revenue calculation | | |
| 122. Có phân biệt giá theo vị trí không? (premium, standard) | Price tiers | | |
| 123. Có phí dịch vụ hàng tháng không? (THB/m²/tháng) | Recurring revenue | | |
| 124. Timeline bán hết dự kiến? (năm) | NPV calculation | | |
| 125. Discount rate cho NPV? (%) | Financial modeling | | |

---

## PHẦN H: RỦI RO VÀ XỬ LÝ LỖI

### H1. Xử lý dữ liệu lỗi/thiếu ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 126. Nếu DXF không có topo, hệ thống nên làm gì? (Dừng/Cảnh báo/Dùng DEM công khai) | Error handling | | |
| 127. Nếu boundary không hợp lệ (self-intersecting), hệ thống nên làm gì? (Dừng/Tự động sửa/Hỏi user) | Validation strategy | | |
| 128. Nếu optimization không tìm được giải pháp khả thi, hệ thống nên làm gì? (Báo lỗi/Đề xuất nới lỏng constraint) | Infeasibility handling | | |
| 129. Nếu có nhiều boundary trong DXF, chọn cái nào? (Lớn nhất/Layer name/Hỏi user) | Multi-boundary handling | | |

### H2. Rủi ro dự án ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 130. Rủi ro lớn nhất khách hàng lo ngại? | Risk mitigation | | |
| 131. Có timeline cứng không thể thay đổi không? | Schedule risk | | |
| 132. Có stakeholder nào có thể block project không? | Political risk | | |
| 133. Có khả năng thay đổi yêu cầu giữa chừng không? | Scope creep | | |

---

## PHẦN I: TIÊU CHÍ THÀNH CÔNG & NGHIỆM THU

### I1. Định nghĩa "hoàn thành" ⚠️ (QUAN TRỌNG NHẤT)

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 134. Tiêu chí nào để coi dự án này là "thành công"? | Success criteria | | |
| 135. Làm thế nào để đo lường "chất lượng design tốt"? | Quality metrics | | |
| 136. Tiêu chí nghiệm thu (acceptance criteria)? | UAT checklist | | |
| 137. Ai là người ký duyệt cuối cùng? | Sign-off authority | | |

### I2. Test cases mong muốn ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 138. Có dự án mẫu để test không? (dữ liệu thực) | Test data | | |
| 139. Có baseline design để so sánh không? (thiết kế thủ công trước đó) | Benchmark | | |
| 140. Kết quả nào là "đủ tốt"? (X lô, Y% ROI, Z giây) | Performance target | | |

### I3. Đào tạo và tài liệu ✅

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 141. Cần tài liệu hướng dẫn sử dụng không? (User manual) | Documentation | | |
| 142. Cần tài liệu kỹ thuật không? (API docs, system architecture) | Technical docs | | |
| 143. Cần đào tạo trực tiếp không? Bao nhiêu buổi? | Training plan | | |
| 144. Cần video hướng dẫn không? | Video tutorials | | |

---

## PHẦN J: HỖ TRỢ VÀ BẢO TRÌ

### J1. Hỗ trợ sau triển khai ✅

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 145. Thời gian bảo hành/hỗ trợ mong muốn? (tháng) | Support SLA | | |
| 146. Kênh hỗ trợ ưu tiên? (Email, phone, chat, ticket system) | Support channel | | |
| 147. Thời gian phản hồi mong muốn? (giờ/ngày) | Response time | | |
| 148. Có cần hotline 24/7 không? | Availability | | |

### J2. Cập nhật và nâng cấp ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 149. Có kế hoạch nâng cấp trong tương lai không? | Roadmap planning | | |
| 150. Tính năng nào muốn thêm trong phase 2? | Future features | | |
| 151. Có ngân sách cho maintenance hàng năm không? | Maintenance contract | | |

---

## PHẦN K: VẤN ĐỀ MỞ (OPEN-ENDED)

### K1. Câu hỏi mở ⚠️

| Câu hỏi | Mục đích | Câu trả lời khách hàng | Hành động |
|---------|----------|------------------------|-----------|
| 152. Có điều gì khách hàng lo lắng mà chúng tôi chưa hỏi? | Uncover hidden concerns | | |
| 153. Có điều gì khách hàng mong đợi mà chúng tôi chưa đề cập? | Expectation gap | | |
| 154. Có kinh nghiệm thất bại nào với dự án tương tự trước đây? Nguyên nhân? | Learn from past | | |
| 155. Có reference project nào khách hàng muốn làm mẫu? | Inspiration | | |
| 156. 3 điều QUAN TRỌNG NHẤT với khách hàng trong dự án này? | Priority ranking | | |

---

## PHẦN L: XÁC NHẬN VÀ KÝ DUYỆT

### L1. Checklist cuối cùng ✅

**Xin khách hàng xác nhận:**

- [ ] Tôi/chúng tôi đã đọc và trả lời TẤT CẢ các câu hỏi phía trên
- [ ] Tôi/chúng tôi hiểu rằng thay đổi yêu cầu sau khi ký duyệt có thể ảnh hưởng timeline và chi phí
- [ ] Tôi/chúng tôi cam kết cung cấp dữ liệu đầu vào đầy đủ và chính xác
- [ ] Tôi/chúng tôi sẽ tham gia UAT (User Acceptance Testing) trước khi chấp nhận
- [ ] Tôi/chúng tôi hiểu scope, timeline, và deliverables của dự án

### L2. Ký xác nhận ✅

```
Tên người đại diện khách hàng: _________________________________

Chức vụ: _________________________________

Công ty: _________________________________

Ngày: ____________________

Chữ ký: _________________________________
```

---

## PHẦN M: HÀNH ĐỘNG TIẾP THEO

### M1. Action items từ cuộc họp

| STT | Hành động | Người phụ trách | Deadline | Trạng thái |
|-----|-----------|----------------|----------|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### M2. Tài liệu cần bổ sung

| STT | Tài liệu | Người cung cấp | Deadline | Trạng thái |
|-----|----------|---------------|----------|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

### M3. Quyết định còn đang chờ

| STT | Quyết định | Người quyết định | Deadline | Trạng thái |
|-----|-----------|------------------|----------|------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

---

## PHỤ LỤC: MA TRẬN RỦI RO

### Bảng đánh giá rủi ro

| Rủi ro | Khả năng (L/M/H) | Tác động (L/M/H) | Mức độ (L/M/H/C) | Phương án giảm thiểu | Trạng thái |
|--------|------------------|------------------|------------------|---------------------|------------|
| Dữ liệu DXF kém chất lượng | | | | Validation trước, fallback options | |
| Thay đổi yêu cầu giữa chừng | | | | Change control process, SOW rõ ràng | |
| Optimization không hội tụ | | | | Multi-start, parameter tuning | |
| Performance không đáp ứng | | | | Load testing, optimization | |
| Khách hàng không hài lòng UI | | | | Wireframe approval trước | |
| Timeline delay | | | | Buffer time, agile approach | |

**Mức độ rủi ro:**
- **L** (Low): Khả năng thấp, tác động nhỏ
- **M** (Medium): Khả năng vừa, tác động vừa
- **H** (High): Khả năng cao, tác động lớn
- **C** (Critical): Khả năng cao, tác động rất lớn (có thể dừng project)

---

## GHI CHÚ CUỘC HỌP

**Ngày họp:** _____________________  
**Địa điểm:** _____________________  
**Người tham dự:**
- Phía khách hàng: _____________________
- Phía nhà thầu: _____________________

**Ghi chú chính:**
```
[Ghi chú tự do về các điểm quan trọng, quyết định, thay đổi, v.v.]








```

---

## TÀI LIỆU THAM KHẢO

### Tài liệu kỹ thuật hiện tại:
1. `CUSTOMER_REQUIREMENTS_FINAL_VALIDATION.md` - Trạng thái fulfillment 100%
2. `CUSTOMER_REQUIREMENTS_FULFILLMENT.md` - Gap analysis
3. `PRODUCT_DATAFLOW_AND_USER_JOURNEY.md` - System architecture
4. `API_DOCUMENTATION.md` - API specs
5. `DXF_IMPLEMENTATION_SUMMARY.md` - DXF parsing
6. `DEPLOYMENT_READINESS_CHECKLIST.md` - Deployment guide

### Contact:
- **Project Manager:** [Tên PM]
- **Technical Lead:** [Tên Tech Lead]
- **Email:** [Email support]
- **Phone:** [Số điện thoại]

---

**Phiên bản tài liệu:** 1.0  
**Ngày tạo:** 23 Tháng 1, 2026  
**Người tạo:** GitHub Copilot  
**Trạng thái:** DRAFT - Chờ xác nhận từ khách hàng

---

**LƯU Ý QUAN TRỌNG:**  
⚠️ Tài liệu này là bản DRAFT. Vui lòng điền đầy đủ thông tin và gửi lại cho team development trước khi bắt đầu implementation phase tiếp theo.

✅ Các phần đánh dấu ⚠️ là CỰC KỲ QUAN TRỌNG và cần được xác nhận kỹ lưỡng để tránh rủi ro cao.
