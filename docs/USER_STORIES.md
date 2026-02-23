# User Stories - Industrial Park AI Designer
## Kịch bản sử dụng thực tế cho hệ thống thiết kế KCN AI

---

## 🤖 AI Processing Architecture

### Hệ Thống Xử Lý AI - 4 Layers

```
┌──────────────────────────────────────────────────────┐
│  LAYER 1: User Input & Intent Recognition           │
│  • Natural Language Understanding (Vietnamese/EN)  │
│  • Extract: Area, Type, Constraints, Standards     │
│  • Clarifying Questions Generator                  │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 2: Regulation Engine                         │
│  • Load IEAT/TCVN standards from config           │
│  • Calculate min/max thresholds                    │
│  • Suggest optimal parameters                      │
│  • Generate design constraints                     │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 3: Layout Generation                         │
│  • CSP Solver: Building placement                 │
│  • Genetic Algorithm: Road network optimization   │
│  • Graph Algorithm: Infrastructure routing        │
│  • Compliance Checker: Real-time validation       │
└──────────────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 4: Output Generation                         │
│  • DXF Generator: CAD files                       │
│  • 3D Renderer: WebGL visualization              │
│  • Report Generator: PDF/Excel                    │
│  • Compliance Report: Detailed checklist          │
└──────────────────────────────────────────────────────┘
```

### Quy Trình Xử Lý Chi Tiết

#### 📥 **Phase 1: Input Processing** (1-2s)
```python
# 1. Parse user input
user_input = "Thiết kế KCN logistics 50 ha, gần cao tốc, muốn dự án xanh"

# 2. LLM Orchestrator extracts intent
extracted = {
    "total_area": 50,  # ha
    "industry_type": "logistics",
    "location_hint": "near highway",
    "sustainability": "green project",
    "standard": None  # Chưa xác định -> cần hỏi
}

# 3. Generate clarifying question
if not extracted["standard"]:
    ask_user("Chọn tiêu chuẩn: IEAT hay TCVN?")
```

#### 📋 **Phase 2: Regulation Mapping** (0.5-1s)
```python
# 4. Load regulation config
if user_choice == "IEAT":
    regs = INDUSTRIAL_PARK_REGULATIONS["ieat_thailand"]
    
# 5. Calculate area distribution
min_salable = regs["land_use"]["salable_area_min_percent"]  # 75%
min_green = regs["land_use"]["green_min_percent"]  # 10%

# 6. Apply user preference ("green project")
suggested_green = 20%  # Hơn min 10%
suggested_salable = 75%  # Đúng min

# 7. Generate suggestion with reasoning
suggestion = {
    "salable": 37.5 ha,  # 75% of 50 ha
    "green": 10 ha,      # 20% of 50 ha
    "road": 7.5 ha,      # 15%
    "utilities": 5 ha,   # 10%
    "reasoning": {
        "salable": "IEAT requires min 75% for financial viability",
        "green": "User wants 'green project', suggest 20% vs min 10%"
    }
}
```

#### 🏭 **Phase 3: Layout Generation** (10-15s)
```python
# 8. Initialize design parameters
params = {
    "total_area": 50,
    "salable_area": 37.5,
    "building_type": "warehouse",
    "constraints": {
        "min_spacing": 12,  # m (IEAT fire safety)
        "max_height": 12,   # m
        "road_width": 25,   # m (IEAT standard)
        "green_buffer": 10  # m
    }
}

# 9. CSP Solver: Place buildings
buildings = place_buildings_csp(
    area=params["salable_area"],
    min_size=2000,  # m²
    max_size=5000,  # m²
    min_spacing=12
)
# Result: 15-20 buildings with valid spacing

# 10. Genetic Algorithm: Optimize road network
roads = optimize_road_network_ga(
    buildings=buildings,
    main_road_width=25,
    secondary_road_width=15,
    generations=50  # iterations
)
# Result: Minimal total road length with full connectivity

# 11. Graph Algorithm: Route utilities
utilities = route_utilities(
    buildings=buildings,
    roads=roads,
    types=["water", "electricity", "wastewater"]
)

# 12. Place infrastructure
infra = place_infrastructure(
    retention_pond=2.5 ha,  # 1:20 ratio
    substation=10 rai,
    green_zones=10 ha
)
```

#### ✅ **Phase 4: Compliance Check** (1-2s)
```python
# 13. Real-time validation
compliance_report = ComplianceChecker.validate(
    design=current_design,
    standard="IEAT"
)

# 14. Generate detailed report
report = {
    "passed": 42,
    "warnings": 3,
    "errors": 2,
    "details": [
        {"check": "Green area", "status": "pass", "value": "20%", "required": "≥10%"},
        {"check": "Building #7 spacing", "status": "error", "value": "8m", "required": "≥12m"},
        # ...
    ]
}

# 15. Auto-fix if possible
if user_requests_autofix:
    for error in report["errors"]:
        apply_fix(error)
    # Re-validate
    final_report = ComplianceChecker.validate(design, "IEAT")
```

#### 📤 **Phase 5: Output Generation** (2-3s)
```python
# 16. Generate DXF (CAD format)
dxf = DXFGenerator.create(
    buildings=buildings,
    roads=roads,
    utilities=utilities,
    layers=["BUILDINGS", "ROADS", "GREEN", "UTILITIES"]
)

# 17. Generate 3D model (WebGL)
threeD_model = ThreeJSRenderer.render(
    design=current_design,
    camera_position="isometric",
    materials=["concrete", "glass", "grass", "water"]
)

# 18. Generate PDF report
pdf = ReportGenerator.create(
    design_summary=summary,
    compliance_report=compliance_report,
    financial_analysis=roi_calculation,
    charts=["area_distribution", "building_schedule"]
)
```

### Multi-LLM Rotation Strategy

```python
# LLM Orchestrator sử dụng multi-model rotation
class IndustrialParkLLMOrchestrator:
    def process_user_input(self, user_message):
        providers = ["megallm", "gemini", "groq", "mistral", "cerebras"]
        
        for provider in providers:
            try:
                # Try each provider in order
                response = self.llm_client.chat(
                    messages=conversation_history,
                    provider=provider
                )
                return self.extract_parameters(response)
            except RateLimitError:
                # Rotate to next provider
                continue
            except Exception as e:
                # Log and try next
                log_error(provider, e)
                continue
        
        raise AllProvidersFailedError()
```

---

## 👤 Personas

### 1. **Nhà Đầu Tư BĐS Công Nghiệp** - Anh Minh (35 tuổi)
- CEO công ty phát triển KCN, có 15 năm kinh nghiệm
- Cần thiết kế nhanh để trình bày cho hội đồng quản trị
- Quan tâm: Diện tích bán được, ROI, compliance với quy chuẩn

### 2. **Kiến Trúc Sư Quy Hoạch** - Chị Lan (42 tuổi)
- Giám đốc thiết kế tại công ty tư vấn, 20 năm kinh nghiệm
- Cần tool hỗ trợ tạo masterplan nhanh, điều chỉnh chi tiết
- Quan tâm: Tính thẩm mỹ, tiêu chuẩn TCVN/IEAT, file DXF/CAD

### 3. **Chuyên Viên Phát Triển Dự Án** - Anh Tuấn (28 tuổi)
- Làm việc cho tập đoàn BĐS, phụ trách feasibility study
- Cần phân tích nhiều phương án, so sánh nhanh
- Quan tâm: Chi phí, timeline, tối ưu hóa layout

---

## 📖 User Story #1: Thiết Kế KCN Mới Từ Đầu

### Persona: Anh Minh (Nhà Đầu Tư)

**Bối cảnh:**
> *Thứ Hai, 8:30 sáng. Anh Minh vừa mua được lô đất 50 ha tại Bình Dương, cần trình bày phương án sơ bộ cho HĐQT vào chiều thứ Năm (3 ngày nữa). Anh cần một masterplan tuân thủ IEAT để xin giấy phép.*

### Kịch bản sử dụng:

#### 🎬 Bước 1: Khởi động và Upload
```
[8:35 AM] Anh Minh mở trình duyệt: http://localhost:3000
- Click "New Design" 
- Upload file: "lo_dat_50ha_songthien.dxf" (file boundary từ GIS team)
- Hệ thống tự động nhận diện: 50.2 ha, tọa độ (10.85°N, 106.75°E)
```

#### 💬 Bước 2: Chat với AI (Tiếng Việt)
```
Anh Minh: "Thiết kế KCN logistics 50 ha, gần cao tốc, 
muốn dự án xanh"

AI: "Chào anh! Em hiểu anh muốn thiết kế KCN logistics 50 ha 
với định hướng bền vững. Để em hỏi thêm vài thông tin:

1. Anh muốn xin giấy phép theo tiêu chuẩn nào?
   • IEAT Thailand (phổ biến ở Đông Nam Á)
   • TCVN 7144 Vietnam
   • Cả hai"

Anh Minh: "IEAT Thailand"

AI: "✓ Được ạ! Với IEAT Thailand cho dự án 50 ha:

📋 Em check quy chuẩn và suggest như sau:

📊 PHÂN BỔ DIỆN TÍCH (theo IEAT):
• Diện tích bán (Salable): 37.5 ha (75%)
  → IEAT yêu cầu tối thiểu 75% để khả thi về tài chính
• Cây xanh (Green): 10 ha (20%)
  → IEAT min 10%, anh muốn "dự án xanh" nên em suggest 20%
• Đường nội bộ: 7.5 ha (15%)
• Hạ tầng (utilities + pond): 5 ha (10%)

🏭 LOẠI HÌNH CÔNG TRÌNH:
• Warehouse/Kho bãi: Chiếm 85% diện tích bán
  - Quy mô: 2,000-5,000 m² mỗi tòa
  - Chiều cao: 8-12m (1-2 tầng)
  - Khoảng cách: ≥12m (IEAT fire safety)
• Office/Văn phòng: 15% (hỗ trợ)
  - Quy mô: 500-1,000 m²
  - Chiều cao: 12-15m (2-3 tầng)

🚗 HẠ TẦNG:
• Đường chính: 25-30m (IEAT standard)
• Đường nội bộ: 15m
• Retention pond: 2.5 ha (tỷ lệ 1:20)
• Trạm biến áp: 10 rai tại trung tâm

💡 Có điều gì cần điều chỉnh không anh?"

Anh Minh: "OK, thiết kế đi"

AI: "⏱️ Đang generate theo IEAT standards... (15-20 giây)"

[AI Processing - Behind the scenes]
🤖 Step 1: CSP Solver placing 18 buildings... (5s)
   • Warehouse: 15 tòa (2,000-5,000 m²)
   • Office: 3 tòa (500-1,000 m²)
   • Min spacing: 12m ✓
   
🤖 Step 2: GA optimizing road network... (6s)
   • Main road: 25m width, 2.1 km
   • Secondary: 15m width, 5.4 km
   • Total coverage: 7.5 ha ✓
   
🤖 Step 3: Placing infrastructure... (2s)
   • Retention pond: 2.5 ha at southeast
   • Substation: 10 rai at center
   • Green zones: 10 ha distributed
   
🤖 Step 4: Compliance check... (1s)
   • IEAT checklist: 47/47 passed ✓
   
🤖 Step 5: Generating outputs... (2s)
   • DXF file: ✓
   • 3D WebGL model: ✓
   • Compliance report: ✓
```

#### 🎨 Bước 3: Xem Kết Quả 3D
```
[8:37 AM] Màn hình hiện:
- Left Panel: Design parameters (có thể edit)
- Center: Interactive 3D view với:
  * 15 warehouse buildings (1000-5000m² mỗi tòa)
  * Road network màu xám
  * Green zones màu xanh lá
  * Retention pond màu xanh dương
- Right Panel: Compliance Report
  ✓ IEAT Green Area: 30% (≥10% required)
  ✓ IEAT Salable: 70% (≥75% but adjustable)
  ✓ Road width: 25m (meets 25-30m standard)
  ⚠️ Warning: Salable area below 75% optimal
```

#### 🔧 Bước 4: Điều Chỉnh Nhanh
```
Anh Minh: "Giảm green xuống 20%, tăng diện tích bán lên 78%"

AI: "✓ Đã update!
• Green: 20% → 10 ha
• Salable: 78% → 39 ha
• Added 3 more buildings
• Compliance: All green ✓

Có thay đổi gì thêm không anh?"
```

#### 📥 Bước 5: Export & Present
```
[8:45 AM] Anh Minh click:
- "Export DXF" → lo_dat_50ha_final.dxf (cho kiến trúc sư)
- "Export PDF Report" → Feasibility_Report.pdf (cho HĐQT)
- "Save Design" → Lưu vào cloud để team review

Total time: 10 phút ⚡
```

### ✅ Success Metrics:
- ⏰ Thời gian: 10 phút (thay vì 2-3 ngày với phương pháp truyền thống)
- 📊 Compliance: 100% tuân thủ IEAT
- 💰 Cost: Free (thay vì $3,000 thuê tư vấn)

---

## 📖 User Story #2: Tối Ưu Hóa Thiết Kế Hiện Có

### Persona: Chị Lan (Kiến Trúc Sư)

**Bối cảnh:**
> *Chị Lan đã có bản vẽ sơ bộ từ team, nhưng khách hàng phản hồi "diện tích xanh quá nhiều, cần thêm 5 lô đất nữa để bán". Cần điều chỉnh trong vòng 1 giờ.*

### Kịch bản:

#### 🎬 Bước 1: Import Design Hiện Có
```
[2:00 PM] Chị Lan:
- Upload: "existing_design_v2.dxf"
- Hệ thống analyze: 25 buildings, 15% green, 80% salable
- AI: "Em đã load xong thiết kế. Chị muốn điều chỉnh gì?"
```

#### 💬 Bước 2: Incremental Adjustment
```
Chị Lan: "Cần thêm 5 lô đất nữa"

AI: "Em hiểu chị muốn tăng diện tích bán. Để em check compliance:

📊 HIỆN TẠI:
• 25 lô, 80% salable, 15% green
• Tuân thủ: TCVN 7144 Vietnam ✓

🎯 MỤC TIÊU: Thêm 5 lô → 30 lô

🔍 EM PHÂN TÍCH THEO TCVN 7144:
• Green area min: 12% (có thể giảm từ 15%)
• Salable area max: 85% (hiện tại 80%)
• Fire spacing: ≥12m (phải giữ)

💡 ĐỀ XUẤT:
Option A: Conservative (85% salable, 12% green)
  • Giảm green buffer: 15% → 12% (-3%)
  • Thêm 5 lô: 2,000-3,000m² mỗi lô
  • Giữ nguyên road network
  • Trade-off: Giảm không gian xanh
  
Option B: Balanced (83% salable, 13% green)
  • Giảm green: 15% → 13% (-2%)
  • Thêm 4 lô thay vì 5
  • Tối ưu layout để compact hơn
  • Trade-off: Ít lô hơn mục tiêu 1 lô

Chị chọn option nào?"

Chị Lan: "Option A, cần đủ 5 lô"

AI: "🔄 Đang optimize theo Option A...

[AI Processing]
🤖 Analyzing current layout... (1s)
   • 25 buildings: Total 62,500 m²
   • Green buffer: 7.5 ha (can reduce to 6 ha)
   • Road network: 7.5 ha (keep)
   
🤖 Running CSP solver with new constraints... (4s)
   • Target: +5 buildings (2,000-3,000 m² each)
   • Free space from green: 1.5 ha
   • Valid positions found: 7 candidates
   • Selected best 5 locations ✓
   
🤖 Adjusting layout for spacing... (3s)
   • Moved 3 existing buildings slightly
   • All spacing ≥12m maintained ✓
   • Road access: All connected ✓
   
🤖 Re-validating TCVN 7144... (1s)
   • Green: 12% (min 12%) ✓
   • Salable: 85% (max 85%) ✓
   • Fire safety: All passed ✓

✓ Solution found:
• Shrunk green buffer: 15% → 12%
• Rearranged buildings: More compact layout
• Added 5 new plots: 2,000-3,000m² each
• Road network: Minimal changes
• Compliance TCVN 7144: ✓ All passed

Chị xem kết quả nhé!"
```

#### 🔍 Bước 3: Compare Versions
```
[2:05 PM] Màn hình split-screen:
Left: Old design (v2)
Right: New design (v3)

Highlights:
- Red: Removed green areas
- Green: New building plots
- Yellow: Modified roads

Chị Lan review và approve
```

#### 💾 Bước 4: Export & Handoff
```
[2:10 PM] Export options:
✓ DXF (AutoCAD 2018 format)
✓ GeoJSON (for GIS team)
✓ PDF Report (design rationale)
✓ Excel (building schedule)

Send to: client@company.com
Subject: "Updated masterplan v3 - added 5 plots"
```

### ✅ Success Metrics:
- ⏰ Time: 10 phút (vs 4 giờ manually)
- 🎯 Accuracy: 100% compliance
- 👥 Collaboration: Easy version control

---

## 📖 User Story #3: So Sánh Nhiều Phương Án

### Persona: Anh Tuấn (Chuyên Viên Dự Án)

**Bối cảnh:**
> *Sếp giao task: "So sánh 3 scenarios - Heavy Industrial, Logistics, Mixed-use. Tính ROI và trình bày vào sáng mai."*

### Kịch bản:

#### 🎬 Bước 1: Batch Generate
```
[4:00 PM] Anh Tuấn:
"So sánh 3 phương án cho lô đất 100 ha: công nghiệp nặng, 
logistics, và hỗn hợp. Tính cả ROI"

AI: "Hiểu rồi anh! Em sẽ tạo 3 scenarios dựa trên regulations:

🏭 SCENARIO A: Heavy Industrial
• Auto-apply TCVN 7144 for heavy industry
• Nhà máy lớn: 8,000-12,000m² (tối ưu cho sản xuất)
• Worker capacity: ~5,000 người
• Green: 15% (min required)
• Salable: 75%

📦 SCENARIO B: Logistics Hub
• Auto-apply IEAT Thailand (phù hợp logistics)
• Warehouse: 3,000-8,000m² (flexible sizing)
• Priority: Road access + loading docks
• Green: 12%
• Salable: 78% (tối ưu hóa)

🏢 SCENARIO C: Mixed-Use (50/50)
• Hybrid: TCVN + IEAT best practices
• 50% Light Manufacturing + 50% Logistics
• Green: 20% (premium project)
• Salable: 76%

⏱️ Generating 3 designs + ROI analysis... (30 giây)"

→ AI tự động áp dụng regulations và tính toán
```

#### 📊 Bước 2: Auto Comparison Table
```
[4:02 PM] AI tự động generate comparison:

| Metric               | Scenario A | Scenario B | Scenario C |
|----------------------|-----------|-----------|-----------|
| Salable Area         | 75 ha     | 78 ha     | 76 ha     |
| # Buildings          | 12        | 25        | 20        |
| Avg Building Size    | 8,500m²   | 4,200m²   | 5,800m²   |
| Green %              | 15%       | 12%       | 20%       |
| Road Network (km)    | 8.5       | 12.3      | 10.2      |
| Worker Capacity      | 5,000     | 2,800     | 4,200     |
| Estimated ROI*       | 18%       | 22%       | 20%       |
| Construction Time    | 18 mo     | 12 mo     | 15 mo     |

*Preliminary calculation
```

#### 💬 Bước 3: Ask Follow-up Questions
```
Anh Tuấn: "Scenario B có thể tăng worker capacity không 
mà không giảm ROI?"

AI: "💡 Suggestion:
- Add 5 smaller warehouses (1500m² each)
- Convert 10% logistics → light manufacturing
- Result: Worker capacity 2,800 → 3,800 (+35%)
- ROI: 22% → 21.5% (-2.3%)

Generate updated Scenario B2?"

Anh Tuấn: "OK, generate"
```

#### 📑 Bước 4: Executive Summary
```
[4:15 PM] Click "Generate Executive Summary"

AI creates:
📄 PowerPoint (10 slides):
1. Cover
2. Project Overview
3. Scenario Comparison Table
4. Site Plans (3 layouts side-by-side)
5. Financial Summary
6. Compliance Status
7. Risk Analysis
8. Timeline Gantt Chart
9. Recommendation: Scenario B2
10. Next Steps

Ready for morning presentation ✓
```

### ✅ Success Metrics:
- ⏰ Time: 15 phút (vs 2 days)
- 📊 Quality: Professional presentation
- 💼 Business Impact: Faster decision making

---

## 📖 User Story #4: Real-time Collaboration

### Personas: Team of 3 (Investor + Architect + Engineer)

**Bối cảnh:**
> *Video call đang diễn ra, cả 3 người cùng xem màn hình, discuss và adjust design real-time.*

### Kịch bản:

#### 🎬 Collaborative Session
```
[10:00 AM] WebSocket connection established

Anh Minh (Investor): "Green area 25% is too much, 
reduce to 15% please"

→ AI updates → All 3 screens update simultaneously

Chị Lan (Architect): "Wait, that building near the pond 
looks too close. Move it 20m north"

→ AI adjusts → Real-time 3D view updates

Anh Tuấn (Engineer): "Can we fit a 10,000m³ water tank here?"
[Clicks location on map]

→ AI: "✓ Yes, space available. Added to design."

[10:15 AM] All approved → Save version "v5_team_consensus"
```

### ✅ Success Metrics:
- 👥 Team satisfaction: High
- ⚡ Speed: Instant feedback
- 🎯 Accuracy: No miscommunication

---

## 📖 User Story #5: Compliance Check & Fix

### Persona: Anh Minh (Pre-submission)

**Bối cảnh:**
> *Trước khi nộp hồ sơ xin phép, cần check lần cuối xem có vi phạm quy chuẩn nào không.*

### Kịch bản:

#### 🔍 Deep Compliance Scan
```
[Final Day, 3:00 PM]

Anh Minh: "Kiểm tra toàn bộ compliance IEAT và TCVN 7144"

AI: "🔍 Đang scan 47 checkpoints...

📋 Results:

✅ PASSED (42/47):
• Green area: 15.2% (>10% required)
• Salable area: 75.8% (75-85% optimal)
• Road width: 25-30m (meets standard)
• Fire safety spacing: 12-25m (✓)
• Building heights: All <25m (✓)
• Parking ratios: Adequate (✓)
...

⚠️ WARNINGS (3):
1. Retention pond: 2.3 ha (should be 2.5 ha for 50 ha project)
2. Substation: Missing 10 rai allocation
3. Green buffer: 8m in north side (should be ≥10m)

❌ ERRORS (2):
1. Building #7: Spacing to pond = 8m (min 12m required)
2. Road R3: Width 22m (min 25m for primary road)
"
```

#### 🔧 Auto-Fix
```
Anh Minh: "Tự động fix hết"

AI: "🔄 Applying fixes...

Fix #1: Moved Building #7 → 5m north (now 13m from pond)
Fix #2: Widened Road R3 → 25m (removed green strip)
Fix #3: Enlarged retention pond → 2.5 ha (removed 1 small plot)
Fix #4: Added substation → 10 rai at center
Fix #5: Widened north green buffer → 10m

⚠️ Trade-offs:
- Lost 0.3 ha salable area (75.8% → 75.2%)
- Removed 1 building plot (Building #23)

Re-checking compliance...
✅ ALL PASSED (47/47)

Ready for submission? ✓"
```

### ✅ Success Metrics:
- 📋 Compliance: 100%
- ⚡ Time to fix: 2 phút
- 💼 Risk: Zero non-compliance

---

## 🎯 Key Features Demonstrated:

1. **Natural Language Input** (Vietnamese + English)
2. **Fast Generation** (15-30 seconds)
3. **Interactive 3D Visualization**
4. **Real-time Collaboration** (WebSocket)
5. **Compliance Checking** (IEAT + TCVN)
6. **Incremental Adjustments**
7. **Multi-scenario Comparison**
8. **Auto-fix Non-compliance**
9. **Export Multiple Formats** (DXF, PDF, Excel)
10. **Version Control** (Save/Load designs)

---

## 📊 Success Metrics Summary:

| Metric | Traditional | With AI | Improvement |
|--------|-------------|---------|-------------|
| Design Time | 2-5 days | 10-30 min | **~99% faster** |
| Cost | $2k-5k | Free | **100% savings** |
| Iterations | 2-3 rounds | Unlimited | **~10x more** |
| Compliance | 85-90% | 100% | **Perfect** |
| Collaboration | Email/meetings | Real-time | **Instant** |

---

## 🚀 Next Steps:

1. **Testing**: Run these scenarios with actual users
2. **Refinement**: Collect feedback and improve UX
3. **Training**: Create video tutorials for each persona
4. **Integration**: Connect with CAD software (AutoCAD, Revit)
5. **Mobile**: Build responsive mobile version

---

*Last updated: January 16, 2026*
