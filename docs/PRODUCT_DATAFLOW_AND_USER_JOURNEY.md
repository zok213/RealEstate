# Dataflow & User Journey - Industrial Park AI Designer

**Audience:** Product Managers, Business Stakeholders
**Last Updated:** January 2026
**Version:** 1.0

---

## Table of Contents

1. [Executive Overview](#executive-overview)
2. [System Architecture](#system-architecture)
3. [End-to-End User Journey](#end-to-end-user-journey)
4. [Detailed Dataflow](#detailed-dataflow)
5. [Processing Pipeline](#processing-pipeline)
6. [API Integration Flow](#api-integration-flow)
7. [Data Transformations](#data-transformations)
8. [Error Handling & Recovery](#error-handling--recovery)

---

## Executive Overview

### Product Purpose
Hệ thống AI tự động thiết kế khu công nghiệp (Industrial Park Designer) giúp các nhà phát triển BĐS tối ưu hóa thiết kế phân lô, tính toán ROI, và đảm bảo tuân thủ quy chuẩn IEAT Thailand.

### Key Value Propositions
- **Thời gian:** Giảm 95% thời gian thiết kế (từ 2-3 tuần → 45 giây)
- **Chi phí:** Tối ưu ROI trung bình 40-50% qua thuật toán genetic
- **Tuân thủ:** Tự động kiểm tra 100% quy chuẩn IEAT Thailand
- **Chất lượng:** Đa mục tiêu (số lô, chất lượng, hiệu suất đường, ROI)

### Technical Stack
- **Frontend:** Next.js 16 + React + TypeScript + Tailwind CSS
- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **AI/ML:** Genetic Algorithm (NSGA-II) + Gemini AI
- **Visualization:** MapBox + DeckGL + Three.js
- **Storage:** PostgreSQL + File Storage (DXF/DWG)

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER BROWSER                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Next.js Frontend (Port 3000)                │  │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────────────┐  │  │
│  │  │  File      │  │   Map    │  │  Financial      │  │  │
│  │  │  Upload    │  │  Canvas  │  │  Metrics Panel  │  │  │
│  │  └────────────┘  └──────────┘  └─────────────────┘  │  │
│  │  ┌────────────┐  ┌──────────┐  ┌─────────────────┐  │  │
│  │  │ Constraint │  │ 3D Viewer│  │  Chat Interface │  │  │
│  │  │  Editor    │  │          │  │                 │  │  │
│  │  └────────────┘  └──────────┘  └─────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   API Layer                           │  │
│  │  /api/designs    /api/financial   /api/optimization  │  │
│  └─────────┬────────────────────────────────────────────┘  │
│            │                                                 │
│  ┌─────────▼─────────────────────────────────────────┐     │
│  │              Core Processing Engine                │     │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │     │
│  │  │   DXF    │  │ Genetic  │  │   Financial    │  │     │
│  │  │ Analyzer │  │Algorithm │  │   Optimizer    │  │     │
│  │  └──────────┘  └──────────┘  └────────────────┘  │     │
│  │  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │     │
│  │  │  Utility │  │ Terrain  │  │  Compliance    │  │     │
│  │  │  Router  │  │ Analyzer │  │   Checker      │  │     │
│  │  └──────────┘  └──────────┘  └────────────────┘  │     │
│  └────────────────────────────────────────────────────┘     │
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │              AI/LLM Integration                     │     │
│  │         Gemini AI (Constraint Extraction)          │     │
│  └────────────────────────────────────────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Storage Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PostgreSQL  │  │ File Storage │  │  Cache (Redis)   │  │
│  │  Database   │  │  (DXF/DWG)   │  │   (Optional)     │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## End-to-End User Journey

### User Personas

**1. Project Manager (PM)**
- **Goal:** Tạo thiết kế khu công nghiệp tối ưu với ROI cao
- **Pain Point:** Mất nhiều thời gian thiết kế thủ công, khó so sánh các phương án
- **Success Metric:** ROI > 40%, thiết kế trong <1 phút

**2. Financial Analyst**
- **Goal:** Đánh giá khả thi tài chính của dự án
- **Pain Point:** Khó ước tính chi phí chính xác, thiếu công cụ phân tích
- **Success Metric:** Dự toán chính xác ±10%, báo cáo ROI chi tiết

**3. Design Engineer**
- **Goal:** Tạo thiết kế tuân thủ quy chuẩn kỹ thuật
- **Pain Point:** Phải kiểm tra thủ công nhiều tiêu chuẩn
- **Success Metric:** 100% tuân thủ IEAT Thailand, tự động hóa kiểm tra

---

### Journey Map: Tạo Thiết Kế Khu Công Nghiệp Mới

#### **Step 1: Upload DXF File**

**User Action:**
1. Truy cập trang chủ http://localhost:3000
2. Nhấn "Upload DXF/DWG File"
3. Chọn file từ máy tính (ví dụ: `lo_dat_50ha_songthien.dxf`)
4. Chờ file upload (2-5 giây)

**System Processing:**
```
Frontend (file-upload-zone.tsx)
   │
   ├─→ Validate file type (.dxf, .dwg)
   ├─→ Check file size (< 50MB)
   ├─→ Create FormData object
   │
   ▼
POST /api/designs/upload
   │
   ├─→ Save file to backend/uploads/
   ├─→ Generate unique design_id
   ├─→ Store metadata in database
   │
   ▼
DXF Analyzer (dxf_analyzer.py)
   │
   ├─→ Parse DXF entities (LWPOLYLINE, LINE, CIRCLE)
   ├─→ Extract boundary polygon
   ├─→ Detect existing roads
   ├─→ Calculate total area (hectares)
   │
   ▼
Response: { design_id, boundary, area, preview_url }
```

**User Sees:**
- ✅ "File uploaded successfully"
- Map hiển thị boundary màu xanh
- Thông tin: "50 hectares, Boundary detected"

---

#### **Step 2: AI Constraint Extraction (Optional)**

**User Action:**
1. Nhấn "Extract Constraints with AI"
2. Nhập mô tả dự án (tiếng Việt/Anh):
   ```
   "Khu công nghiệp 50ha tại Bình Dương, tuân thủ IEAT Thailand.
   Cần tối thiểu 15% cây xanh, lô tối thiểu 500m², đường chính 20m."
   ```
3. Chờ AI phân tích (5-10 giây)

**System Processing:**
```
Frontend (chat-interface.tsx)
   │
   ├─→ Send user message to backend
   │
   ▼
POST /api/design-chat
   │
   ├─→ Call Gemini AI API
   │   │
   │   ├─→ System prompt: "Extract design constraints"
   │   ├─→ User message: Project description
   │   │
   │   ▼
   │   Gemini AI Response:
   │   {
   │     "min_lot_size": 500,
   │     "green_space_min": 0.15,
   │     "road_width_main": 20,
   │     "setback_front": 50
   │   }
   │
   ├─→ Parse JSON from AI response
   ├─→ Validate constraints
   ├─→ Merge with default parameters
   │
   ▼
Response: { constraints, templates: ["IEAT_Thailand"] }
```

**User Sees:**
- Constraint Editor auto-filled:
  - ✅ Min lot size: 500 m²
  - ✅ Green space: 15%
  - ✅ Road width: 20m
  - ✅ Setback: 50m
- Gợi ý template: "IEAT Thailand"

---

#### **Step 3: Configure Optimization Parameters**

**User Action:**
1. Điều chỉnh constraints trong Advanced Constraint Editor:
   - Min lot size: 500 → 800 m²
   - Max lot size: 10,000 m²
   - Green space: 15%
   - Parking ratio: 10%
   
2. Điều chỉnh objectives:
   - Maximize lots: 1.0 (cao nhất)
   - Maximize quality: 0.8
   - Maximize ROI: 1.2 (ưu tiên tài chính)
   - Road efficiency: 0.6

3. Chọn advanced options:
   - ☑ Include financial analysis
   - ☑ Include utility routing
   - ☐ Include terrain analysis (tắt nếu không có DEM)

4. Nhấn "Generate Optimized Design"

**System Processing:**
```
Frontend (industrial-park-designer.tsx)
   │
   ├─→ Validate all parameters
   ├─→ Build optimization request
   │
   ▼
POST /api/optimization/run
   │
   Content-Type: multipart/form-data
   │
   Fields:
   - file: DXF file
   - parameters: JSON {
       population_size: 50,
       generations: 100,
       constraints: {...},
       objectives: {...}
     }
   │
   ▼
Optimization Pipeline (optimized_pipeline_integrator.py)
```

---

#### **Step 4: Genetic Algorithm Optimization**

**System Processing (Deep Dive):**

```
INITIALIZATION PHASE (0-5 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4.1: Parse DXF Boundary
   │
   ├─→ Load DXF file with ezdxf
   ├─→ Extract LWPOLYLINE for boundary
   ├─→ Convert to Shapely Polygon
   ├─→ Simplify geometry (Douglas-Peucker)
   │
   ▼ boundary: Polygon(area=500,000m²)

Step 4.2: Create Initial Population (50 individuals)
   │
   ├─→ Generate random lot configurations
   │   │
   │   For each individual:
   │   ├─→ Random cut points along boundary
   │   ├─→ Split into road grid (Voronoi diagram)
   │   ├─→ Generate lots between roads
   │   ├─→ Ensure constraints (min/max size)
   │   │
   │   ▼ Individual: { lots: [50-80 lots], roads: [...] }
   │
   ▼ population: [individual_1, ..., individual_50]


EVOLUTION PHASE (5-40 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For generation 1 to 100:
   │
   Step 4.3: Evaluate Fitness (all individuals)
   │   │
   │   For each individual:
   │   │
   │   ├─→ Count valid lots
   │   │   └─→ fitness_lots = num_valid_lots
   │   │
   │   ├─→ Calculate quality score
   │   │   ├─→ Check lot regularity (rectangularity)
   │   │   ├─→ Check road access (all lots have frontage)
   │   │   ├─→ Check constraint satisfaction
   │   │   └─→ fitness_quality = avg_score (0-100)
   │   │
   │   ├─→ Calculate road efficiency
   │   │   ├─→ road_length = sum(all road segments)
   │   │   ├─→ efficiency = saleable_area / road_area
   │   │   └─→ fitness_road = efficiency (0-1)
   │   │
   │   ├─→ Calculate financial metrics (NEW!)
   │   │   ├─→ Call FinancialModel.calculate_roi_metrics()
   │   │   ├─→ total_cost = site + roads + utilities
   │   │   ├─→ total_revenue = sum(lot_prices)
   │   │   └─→ fitness_roi = roi_percentage
   │   │
   │   ▼ fitness = (lots, quality, road_eff, roi)
   │
   Step 4.4: Selection (Tournament)
   │   │
   │   ├─→ Pick 3 random individuals
   │   ├─→ Compare fitness tuples (Pareto dominance)
   │   ├─→ Select winner
   │   │
   │   Repeat 50 times → selected_parents
   │
   Step 4.5: Crossover (80% rate)
   │   │
   │   For each pair of parents:
   │   ├─→ Random crossover point
   │   ├─→ Child1 = parent1[:point] + parent2[point:]
   │   ├─→ Child2 = parent2[:point] + parent1[point:]
   │   │
   │   ▼ offspring
   │
   Step 4.6: Mutation (10% rate)
   │   │
   │   For each offspring:
   │   ├─→ Random chance (10%)
   │   ├─→ If mutate:
   │   │   ├─→ Randomly modify 1-2 cut points
   │   │   ├─→ Regenerate affected lots
   │   │
   │   ▼ mutated_offspring
   │
   Step 4.7: Elitism (keep top 10%)
   │   │
   │   ├─→ Sort population by fitness
   │   ├─→ Keep best 5 individuals
   │   ├─→ Add to next generation
   │   │
   │   ▼ next_generation
   │
   ├─→ Check convergence
   │   ├─→ If fitness plateau for 10 generations → STOP
   │   └─→ If generation == 100 → STOP
   │
   ▼ Continue to next generation


FINALIZATION PHASE (40-45 seconds)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 4.8: Select Best Solution
   │
   ├─→ Sort final population by fitness
   ├─→ Pick Pareto optimal solutions
   ├─→ Select highest ROI among optimal set
   │
   ▼ best_design: { lots: [...], roads: [...] }

Step 4.9: Post-Processing
   │
   ├─→ Smooth road geometry
   ├─→ Adjust lot boundaries
   ├─→ Add green space polygons (15%)
   ├─→ Add parking areas (10%)
   │
   ▼ refined_design

Step 4.10: Compliance Check (IEAT Thailand)
   │
   ├─→ Check IEAT Thailand standards
   │   ├─→ Green space ≥ 15% ✅
   │   ├─→ Setback ≥ 50m ✅
   │   ├─→ Parking ≥ 10% ✅
   │   ├─→ Fire access ≤ 30m ✅
   │   ├─→ Industrial lot slope ≤ 15% ✅
   │   ├─→ Road slope ≤ 12% ✅
   │   ├─→ Min lot ≥ 500m² ✅
   │   ├─→ Min frontage ≥ 20m ✅
   │   └─→ Road width ≥ 12m ✅
   │
   ▼ compliance_report: { passed: true, violations: [] }
```

**User Sees (During Generation):**
- Progress bar: "Generating... Generation 45/100"
- Real-time updates: "Current best ROI: 38.5%"
- Live preview: Thiết kế tốt nhất hiện tại trên map

---

#### **Step 5: Financial Analysis**

**System Processing:**

```
POST /api/financial/analyze
   │
   ▼
FinancialModel.calculate_roi_metrics(design)
   │
   Step 5.1: Calculate Construction Costs
   │   │
   │   ├─→ Site clearing
   │   │   area = 500,000 m²
   │   │   cost = area × 80,000 VND/m²
   │   │   = 40,000,000,000 VND (40B VND)
   │   │
   │   ├─→ Roads
   │   │   main_roads = 800m × 2,500,000 VND/m = 2B VND
   │   │   internal = 2,000m × 1,500,000 VND/m = 3B VND
   │   │   subtotal = 5B VND
   │   │
   │   ├─→ Utilities (water + sewer + electrical)
   │   │   water = 2,500m × 500,000 = 1.25B VND
   │   │   sewer = 2,800m × 800,000 = 2.24B VND
   │   │   electrical = 3,200m × 400,000 = 1.28B VND
   │   │   subtotal = 4.77B VND
   │   │
   │   ├─→ Grading & drainage
   │   │   cut = 15,000m³ × 50,000 = 0.75B VND
   │   │   fill = 14,800m³ × 80,000 = 1.18B VND
   │   │   drainage = 500,000m² × 300,000 = 1.5B VND
   │   │   subtotal = 3.43B VND
   │   │
   │   ├─→ Other costs
   │   │   lighting = 150,000 × area = 0.75B VND
   │   │   landscaping = 200,000 × area = 1B VND
   │   │   fees = 5% × total = 3B VND
   │   │
   │   ├─→ Contingency (15%)
   │   │   = 0.15 × subtotal = 9B VND
   │   │
   │   ▼ total_cost = 66.95B VND (~67B VND)
   │
   Step 5.2: Calculate Revenue
   │   │
   │   For each lot:
   │   │
   │   ├─→ Base price
   │   │   area = 2,500 m²
   │   │   base = 3,500,000 VND/m²
   │   │   base_revenue = 8,750,000,000 VND (8.75B)
   │   │
   │   ├─→ Apply premiums
   │   │   ├─→ Factory zone: +20% = +1.75B
   │   │   ├─→ Corner lot: +15% = +1.31B
   │   │   ├─→ High quality (>80): +10% = +0.88B
   │   │   └─→ Good frontage (>30m): +5% = +0.44B
   │   │
   │   ├─→ Apply discounts
   │   │   ├─→ Large lot (>5000m²): -5% = -0.44B
   │   │   └─→ Irregular shape: -8% = -0.70B
   │   │
   │   ▼ final_price = 11.99B VND per lot
   │
   │   Sum all 65 lots:
   │   total_revenue = 65 × avg(11.99B) = 120B VND
   │
   Step 5.3: Calculate ROI
   │   │
   │   gross_profit = revenue - cost
   │                 = 120B - 67B = 53B VND
   │   
   │   roi_percentage = (profit / cost) × 100
   │                   = (53 / 67) × 100
   │                   = 79.1%
   │   
   │   profit_margin = (profit / revenue) × 100
   │                  = (53 / 120) × 100
   │                  = 44.2%
   │   
   │   payback_period = cost / (revenue / 5 years)
   │                   = 67 / 24 = 2.79 years
   │   
   │   ▼ metrics: {
   │       roi: 79.1%,
   │       profit: 53B VND,
   │       margin: 44.2%,
   │       payback: 2.79 years
   │     }
```

**User Sees:**
- Financial Metrics Panel hiển thị:
  ```
  ┌────────────────────────────────────────┐
  │   💰 ROI: 79.1%    [Excellent ████]   │
  │   📊 Profit: 53B VND                   │
  │   📈 Margin: 44.2%                     │
  │   ⏱️  Payback: 2.8 years               │
  └────────────────────────────────────────┘
  
  Cost Breakdown:
  ▓▓▓▓▓▓▓▓░░ Site Clearing: 40B VND (60%)
  ▓▓░░░░░░░░ Roads: 5B VND (7%)
  ▓▓░░░░░░░░ Utilities: 4.8B VND (7%)
  ▓▓░░░░░░░░ Grading: 3.4B VND (5%)
  ▓▓▓░░░░░░░ Other: 4.75B VND (7%)
  ▓▓▓░░░░░░░ Contingency: 9B VND (14%)
  ```

---

#### **Step 6: Utility Network Design**

**System Processing:**

```
UtilityNetworkDesigner.design_all_networks(design)
   │
   Step 6.1: Design Water Network
   │   │
   │   ├─→ Build graph from roads
   │   │   G = nx.Graph()
   │   │   Add road segments as edges
   │   │   Weight = distance
   │   │
   │   ├─→ Add water source (main connection)
   │   │   source = Point(0, 0)  # Lower-left corner
   │   │
   │   ├─→ Connect all lots to nearest road
   │   │   For each lot:
   │   │   ├─→ Find nearest road point
   │   │   ├─→ Add edge from lot to road
   │   │
   │   ├─→ Solve Steiner tree problem
   │   │   # Connect source to all lots with minimum pipe length
   │   │   mst = nx.minimum_spanning_tree(G)
   │   │   steiner_tree = approximate_steiner_tree(mst, terminals)
   │   │
   │   ├─→ Convert to pipe network
   │   │   pipes = []
   │   │   For each edge in steiner_tree:
   │   │   ├─→ Create pipe segment
   │   │   ├─→ Calculate length
   │   │   └─→ Add to pipes list
   │   │
   │   ├─→ Calculate cost
   │   │   total_length = 2,500m
   │   │   cost = 2,500 × 500,000 VND/m = 1.25B VND
   │   │
   │   ▼ water_network: {
   │       pipes: 78 segments,
   │       length: 2,500m,
   │       cost: 1.25B VND
   │     }
   │
   Step 6.2: Design Sewer Network
   │   │
   │   ├─→ Build graph (same as water)
   │   │
   │   ├─→ Add sewer outlet (lowest point)
   │   │   outlet = Point(200, 200)  # Upper-right
   │   │
   │   ├─→ Route each lot to outlet
   │   │   For each lot:
   │   │   ├─→ Find shortest path to outlet
   │   │   │   path = nx.shortest_path(G, lot, outlet)
   │   │   ├─→ Follow gravity (downward slope)
   │   │   └─→ Add pipes along path
   │   │
   │   ├─→ Merge duplicate pipes
   │   │   # Multiple lots may share same pipe
   │   │   Remove duplicates, keep unique segments
   │   │
   │   ├─→ Calculate cost
   │   │   total_length = 2,800m
   │   │   cost = 2,800 × 800,000 = 2.24B VND
   │   │
   │   ▼ sewer_network: {
   │       pipes: 82 segments,
   │       length: 2,800m,
   │       cost: 2.24B VND
   │     }
   │
   Step 6.3: Design Electrical Network
   │   │
   │   ├─→ Add substation (main power source)
   │   │   substation = Point(0, 200)  # Upper-left
   │   │
   │   ├─→ Create minimum spanning tree
   │   │   # Connect all lots with minimum cable
   │   │   mst = nx.minimum_spanning_tree(G)
   │   │
   │   ├─→ Add redundancy (10% extra cables)
   │   │   For critical connections:
   │   │   └─→ Add backup cables
   │   │
   │   ├─→ Calculate cost
   │   │   total_length = 3,200m
   │   │   cost = 3,200 × 400,000 = 1.28B VND
   │   │
   │   ▼ electrical_network: {
   │       cables: 95 segments,
   │       length: 3,200m,
   │       cost: 1.28B VND
   │     }
   │
   ▼ Total utility cost: 4.77B VND
```

**User Sees:**
- Map layers with color-coded utilities:
  - 💧 Blue lines: Water pipes
  - 🚰 Brown lines: Sewer pipes
  - ⚡ Yellow lines: Electrical cables
- Utility summary:
  ```
  Water: 2.5km, 1.25B VND
  Sewer: 2.8km, 2.24B VND
  Electrical: 3.2km, 1.28B VND
  Total: 4.77B VND
  ```

---

#### **Step 7: View & Download Results**

**User Action:**
1. Explore thiết kế trên map:
   - Zoom in/out
   - Click vào từng lô để xem chi tiết
   - Toggle layers (lots, roads, utilities, green space)

2. Xem 3D visualization:
   - Nhấn "3D View"
   - Rotate, pan, zoom
   - Xem độ cao, terrain

3. Export thiết kế:
   - Nhấn "Export DXF" → Download DXF file
   - Nhấn "Export PDF" → Download báo cáo PDF
   - Nhấn "Export JSON" → Download data JSON

4. Share với team:
   - Nhấn "Share" → Generate link
   - Copy link và gửi cho đồng nghiệp

**System Processing:**

```
Export DXF:
   │
   ├─→ DXFGenerator.create_dxf(design)
   │   ├─→ Create new DXF document
   │   ├─→ Add layers (LOTS, ROADS, BOUNDARY)
   │   ├─→ Draw polylines for each lot
   │   ├─→ Draw lines for roads
   │   ├─→ Add text labels (lot IDs, areas)
   │   └─→ Save to file
   │
   ▼ Download: industrial_park_design_20260122.dxf

Export PDF Report:
   │
   ├─→ Generate report with ReportLab
   │   ├─→ Cover page (project info)
   │   ├─→ Design summary (area, lots, roads)
   │   ├─→ Financial analysis (tables, charts)
   │   ├─→ Compliance checklist (IEAT Thailand)
   │   ├─→ Map images (PNG exports)
   │   └─→ Appendix (parameters, constraints)
   │
   ▼ Download: industrial_park_report_20260122.pdf

Share Link:
   │
   ├─→ Save design to database
   │   design_id = UUID.generate()
   │   INSERT INTO designs (id, data, created_at)
   │
   ├─→ Generate public URL
   │   url = https://app.com/designs/{design_id}
   │
   ▼ Copy link to clipboard
```

---

## Detailed Dataflow

### Data Flow Diagram (DFD Level 0)

```
┌──────────┐                    ┌─────────────────────┐
│   USER   │───── DXF File ────→│   UPLOAD SERVICE    │
└──────────┘                    └──────────┬──────────┘
     │                                     │
     │                                     ▼
     │                          ┌──────────────────────┐
     │                          │   FILE STORAGE       │
     │                          │   /uploads/*.dxf     │
     │                          └──────────┬───────────┘
     │                                     │
     │                                     ▼
     │                          ┌──────────────────────┐
     │                          │   DXF ANALYZER       │
     │                          │  (Parse boundary)    │
     │                          └──────────┬───────────┘
     │                                     │
     │                          ┌──────────▼───────────┐
     │◄─── Preview Data ────────│   DATABASE           │
     │                          │  (Design metadata)   │
     │                          └──────────┬───────────┘
     │                                     │
     ├──── Optimization Params ───────────┤
     │                                     │
     │                                     ▼
     │                          ┌──────────────────────┐
     │                          │  GENETIC ALGORITHM   │
     │                          │  (100 generations)   │
     │                          └──────────┬───────────┘
     │                                     │
     │                          ┌──────────▼───────────┐
     │                          │  FINANCIAL ANALYZER  │
     │                          │  (Calculate ROI)     │
     │                          └──────────┬───────────┘
     │                                     │
     │                          ┌──────────▼───────────┐
     │                          │  UTILITY ROUTER      │
     │                          │  (Network design)    │
     │                          └──────────┬───────────┘
     │                                     │
     │                          ┌──────────▼───────────┐
     │◄─── Final Design ────────│  COMPLIANCE CHECKER  │
     │                          │  (Validate rules)    │
     │                          └──────────────────────┘
     │
     ▼
┌──────────────────────┐
│   VISUALIZATION      │
│  (Map + 3D + Charts) │
└──────────────────────┘
```

### Data Flow Diagram (DFD Level 1 - Optimization)

```
┌────────────────────────────────────────────────────────────┐
│             GENETIC ALGORITHM OPTIMIZATION                  │
│                                                             │
│  ┌──────────┐                                              │
│  │  INPUT   │                                              │
│  │ Design   │                                              │
│  │ Request  │                                              │
│  └────┬─────┘                                              │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────┐                                      │
│  │  INITIALIZATION  │                                      │
│  │  • Parse DXF     │                                      │
│  │  • Create pop    │                                      │
│  └────┬─────────────┘                                      │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────┐       ┌──────────────────┐          │
│  │   EVALUATION     │◄──────┤  CONSTRAINT      │          │
│  │  • Count lots    │       │  CHECKER         │          │
│  │  • Quality score │       │  • Min/max size  │          │
│  │  • Road eff      │       │  • Setbacks      │          │
│  │  • ROI calc      │       │  • Green space   │          │
│  └────┬─────────────┘       └──────────────────┘          │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────┐                                      │
│  │   SELECTION      │                                      │
│  │  Tournament      │                                      │
│  └────┬─────────────┘                                      │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────┐                                      │
│  │   CROSSOVER      │                                      │
│  │  Single-point    │                                      │
│  └────┬─────────────┘                                      │
│       │                                                     │
│       ▼                                                     │
│  ┌──────────────────┐                                      │
│  │   MUTATION       │                                      │
│  │  Random modify   │                                      │
│  └────┬─────────────┘                                      │
│       │                                                     │
│       ├───────────┐                                        │
│       │           │ Next generation                        │
│       ▼           │                                        │
│  ┌──────────┐    │                                        │
│  │ Converged?├────┘ No (continue)                         │
│  └────┬──────┘                                             │
│       │ Yes                                                │
│       ▼                                                     │
│  ┌──────────────────┐                                      │
│  │  OUTPUT          │                                      │
│  │  Best design     │                                      │
│  └──────────────────┘                                      │
└────────────────────────────────────────────────────────────┘
```

---

## Processing Pipeline

### Pipeline Stages

```
Stage 1: UPLOAD & PARSE
━━━━━━━━━━━━━━━━━━━━━━
Input:  DXF file (binary)
Output: Boundary polygon + metadata
Time:   2-5 seconds
Status: ✅ Complete

Stage 2: AI CONSTRAINT EXTRACTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  User description (text)
Output: Constraint JSON
Time:   5-10 seconds
Status: ✅ Complete

Stage 3: GENETIC OPTIMIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Boundary + constraints
Output: Optimized lot layout
Time:   35-45 seconds
Status: ✅ Complete

Stage 4: FINANCIAL ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Design layout
Output: ROI metrics
Time:   1-2 seconds
Status: ✅ Complete

Stage 5: UTILITY ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Lots + roads
Output: Water/sewer/electrical networks
Time:   3-5 seconds
Status: ✅ Complete

Stage 6: COMPLIANCE CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━
Input:  Final design
Output: Pass/fail report
Time:   <1 second
Status: ✅ Complete

Stage 7: VISUALIZATION
━━━━━━━━━━━━━━━━━━━━━━
Input:  All design data
Output: Map + 3D + charts
Time:   2-3 seconds
Status: ✅ Complete

Total End-to-End Time: ~60 seconds
```

---

## API Integration Flow

### API Endpoints & Data Format

#### 1. Upload DXF File

```http
POST /api/designs/upload
Content-Type: multipart/form-data

Request:
------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="site.dxf"
Content-Type: application/octet-stream

[DXF binary data]
------WebKitFormBoundary--

Response: 200 OK
{
  "design_id": "d1234-5678-90ab-cdef",
  "filename": "site.dxf",
  "area_hectares": 50.0,
  "boundary": {
    "type": "Polygon",
    "coordinates": [[[0,0], [1000,0], [1000,500], [0,500], [0,0]]]
  },
  "preview_url": "/uploads/d1234_preview.png",
  "created_at": "2026-01-22T10:30:00Z"
}
```

#### 2. Run Optimization

```http
POST /api/optimization/run
Content-Type: multipart/form-data

Request:
- file: [DXF file]
- parameters: {
    "population_size": 50,
    "generations": 100,
    "mutation_rate": 0.1,
    "constraints": {
      "min_lot_size": 500,
      "max_lot_size": 10000,
      "green_space_min": 0.15,
      "setback_front": 50
    },
    "objectives": {
      "maximize_lots": 1.0,
      "maximize_quality": 0.8,
      "maximize_roi": 1.2
    },
    "include_financial_analysis": true,
    "include_utility_routing": true
  }

Response: 200 OK
{
  "design": {
    "lots": [
      {
        "id": 1,
        "geometry": { "type": "Polygon", "coordinates": [...] },
        "area": 2500.0,
        "frontage": 50.0,
        "quality_score": 85.3,
        "zone_type": "FACTORY",
        "is_corner": true
      },
      // ... 64 more lots
    ],
    "roads": [
      {
        "id": 1,
        "geometry": { "type": "LineString", "coordinates": [...] },
        "type": "main",
        "width": 20.0,
        "length": 800.0
      },
      // ... more roads
    ],
    "green_spaces": [...],
    "parking_areas": [...]
  },
  "fitness_scores": {
    "num_lots": 65,
    "quality_score": 82.5,
    "road_efficiency": 0.78,
    "roi_percentage": 79.1
  },
  "financial_analysis": {
    "total_cost": 67000000000,
    "total_revenue": 120000000000,
    "gross_profit": 53000000000,
    "roi_percentage": 79.1,
    "profit_margin": 44.2,
    "cost_breakdown": {...},
    "revenue_breakdown": {...}
  },
  "utility_networks": {
    "water": {
      "pipes": [...],
      "total_length": 2500,
      "cost": 1250000000
    },
    "sewer": {...},
    "electrical": {...}
  },
  "compliance_check": {
    "ieat_thailand": {
      "green_space_min_15%": true,
      "setback_50m": true,
      "parking_10%": true,
      "fire_access_30m": true,
      "lot_slope_15%": true,
      "road_slope_12%": true,
      "min_lot_500m2": true,
      "min_frontage_20m": true,
      "road_width_12m": true
    }
  },
  "generation_time": 45.3,
  "convergence_generation": 67
}
```

#### 3. Financial Analysis

```http
POST /api/financial/analyze
Content-Type: application/json

Request:
{
  "total_area": 500000,
  "roads": [
    { "type": "main", "length": 800 },
    { "type": "internal", "length": 2000 }
  ],
  "lots": [
    {
      "id": 1,
      "geometry": {...},
      "quality_score": 85,
      "is_corner": true,
      "zone_type": "FACTORY"
    },
    // ... more lots
  ],
  "green_space_area": 75000
}

Response: 200 OK
{
  "roi_percentage": 79.1,
  "total_cost": 67000000000,
  "total_revenue": 120000000000,
  "gross_profit": 53000000000,
  "cost_breakdown": {
    "site_clearing": 40000000000,
    "roads": 5000000000,
    "utilities": 4770000000,
    "grading": 3430000000,
    "drainage": 1500000000,
    "lighting": 750000000,
    "landscaping": 1000000000,
    "fees_permits": 3000000000,
    "contingency": 9000000000,
    "total_construction_cost": 67000000000
  },
  "revenue_breakdown": {
    "num_lots": 65,
    "total_revenue": 120000000000,
    "average_price_per_sqm": 3560000,
    "lots": [...]
  },
  "efficiency_metrics": {
    "cost_per_sqm": 1340000,
    "revenue_per_sqm": 2400000,
    "profit_margin": 44.2
  }
}
```

---

## Data Transformations

### DXF → Internal Format

```python
# Input: DXF file
dxf_file = "site_boundary.dxf"

# Step 1: Parse with ezdxf
import ezdxf
doc = ezdxf.readfile(dxf_file)
msp = doc.modelspace()

# Step 2: Extract entities
entities = []
for entity in msp.query('LWPOLYLINE'):
    coords = [(p[0], p[1]) for p in entity.get_points()]
    entities.append({
        'type': 'polyline',
        'layer': entity.dxf.layer,
        'coordinates': coords,
        'closed': entity.closed
    })

# Step 3: Find boundary (largest polygon)
from shapely.geometry import Polygon
polygons = [Polygon(e['coordinates']) for e in entities if e['closed']]
boundary = max(polygons, key=lambda p: p.area)

# Step 4: Convert to GeoJSON
geojson = {
    'type': 'Feature',
    'geometry': {
        'type': 'Polygon',
        'coordinates': [list(boundary.exterior.coords)]
    },
    'properties': {
        'area': boundary.area,
        'perimeter': boundary.length
    }
}

# Output: GeoJSON format for frontend
```

### Design → DXF Export

```python
# Input: Optimized design
design = {
    'lots': [...],
    'roads': [...],
    'boundary': Polygon(...)
}

# Step 1: Create DXF document
import ezdxf
doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Step 2: Add layers
doc.layers.new('BOUNDARY', dxfattribs={'color': 1})  # Red
doc.layers.new('LOTS', dxfattribs={'color': 3})      # Green
doc.layers.new('ROADS', dxfattribs={'color': 5})     # Blue

# Step 3: Draw boundary
coords = list(design['boundary'].exterior.coords)
msp.add_lwpolyline(coords, dxfattribs={'layer': 'BOUNDARY'})

# Step 4: Draw lots
for lot in design['lots']:
    coords = list(lot['geometry'].exterior.coords)
    msp.add_lwpolyline(coords, dxfattribs={'layer': 'LOTS'})
    
    # Add text label
    centroid = lot['geometry'].centroid
    msp.add_text(
        f"LOT {lot['id']}\n{lot['area']:.0f}m²",
        dxfattribs={
            'layer': 'LOTS',
            'height': 5.0
        }
    ).set_pos((centroid.x, centroid.y), align='CENTER')

# Step 5: Draw roads
for road in design['roads']:
    coords = list(road['geometry'].coords)
    msp.add_lwpolyline(coords, dxfattribs={'layer': 'ROADS'})

# Step 6: Save file
doc.saveas('optimized_design.dxf')
```

### Frontend ↔ Backend Data Format

```typescript
// Frontend Request
interface OptimizationRequest {
  file: File;                    // DXF file object
  parameters: {
    population_size: number;     // 50
    generations: number;         // 100
    mutation_rate: number;       // 0.1
    constraints: {
      min_lot_size: number;      // 500 m²
      max_lot_size: number;      // 10000 m²
      green_space_min: number;   // 0.15 (15%)
      setback_front: number;     // 50 m
      // ... more constraints
    };
    objectives: {
      maximize_lots: number;     // 1.0 (weight)
      maximize_quality: number;  // 0.8
      maximize_roi: number;      // 1.2
    };
  };
}

// Backend Response
interface OptimizationResponse {
  design: {
    lots: Array<{
      id: number;
      geometry: GeoJSON.Polygon;
      area: number;
      frontage: number;
      quality_score: number;
      zone_type: 'FACTORY' | 'WAREHOUSE' | 'OFFICE';
      is_corner: boolean;
    }>;
    roads: Array<{
      id: number;
      geometry: GeoJSON.LineString;
      type: 'main' | 'internal' | 'service';
      width: number;
      length: number;
    }>;
    green_spaces: GeoJSON.Polygon[];
    parking_areas: GeoJSON.Polygon[];
  };
  fitness_scores: {
    num_lots: number;
    quality_score: number;
    road_efficiency: number;
    roi_percentage: number;
  };
  financial_analysis: FinancialAnalysis;
  utility_networks: UtilityNetworks;
  compliance_check: ComplianceReport;
  generation_time: number;
  convergence_generation: number;
}
```

---

## Error Handling & Recovery

### Error Scenarios

#### 1. DXF Parse Error

```
Scenario: User uploads corrupted DXF file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Frontend:
  ├─→ Upload file
  ├─→ Show loading spinner
  │
Backend:
  ├─→ Receive file
  ├─→ Try to parse with ezdxf
  ├─→ Exception: DXFStructureError
  │
  ├─→ Log error
  │   logger.error(f"DXF parse failed: {e}")
  │
  ├─→ Return 400 Bad Request
  │   {
  │     "detail": "Invalid DXF file format",
  │     "error_code": "DXF_PARSE_001",
  │     "suggestion": "Please upload a valid DXF or DWG file"
  │   }
  │
Frontend:
  ├─→ Catch error in API client
  ├─→ Hide loading spinner
  ├─→ Show error toast:
  │   "❌ Invalid file format. Please upload a valid DXF/DWG file."
  ├─→ Allow user to retry
```

#### 2. Optimization Timeout

```
Scenario: Optimization takes >120 seconds
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend:
  ├─→ Start optimization
  ├─→ Set timeout = 120 seconds
  │
  ├─→ After 120s:
  │   ├─→ Kill optimization process
  │   ├─→ Save partial results
  │   ├─→ Log timeout
  │       logger.warning(f"Optimization timeout: {design_id}")
  │
  ├─→ Return 504 Gateway Timeout
  │   {
  │     "detail": "Optimization timed out",
  │     "error_code": "OPT_TIMEOUT_001",
  │     "partial_results": {
  │       "generations_completed": 67,
  │       "best_roi": 38.5
  │     },
  │     "suggestion": "Reduce generations or simplify constraints"
  │   }
  │
Frontend:
  ├─→ Show timeout message:
  │   "⏱️ Optimization timed out after 2 minutes.
  │   Completed 67/100 generations.
  │   Best ROI: 38.5%
  │   
  │   [Use Partial Results] [Retry with Fewer Generations]"
  ├─→ Allow user to use partial results
  ├─→ Or adjust parameters and retry
```

#### 3. Financial Calculation Error

```
Scenario: Missing cost parameters
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Backend:
  ├─→ Calculate financial metrics
  ├─→ Missing 'grading' cost parameter
  │
  ├─→ Use default value
  │   logger.warning("Missing grading cost, using default")
  │   cost_params['grading'] = 120000  # Default
  │
  ├─→ Continue calculation
  ├─→ Add warning to response
  │   {
  │     "roi_percentage": 79.1,
  │     "warnings": [
  │       "Used default grading cost (120,000 VND/m²)"
  │     ]
  │   }
  │
Frontend:
  ├─→ Show financial metrics
  ├─→ Display warning icon with tooltip:
  │   "ℹ️ Some costs estimated with defaults"
```

### Recovery Strategies

**Strategy 1: Auto-Retry with Exponential Backoff**
```typescript
async function runOptimizationWithRetry(
  file: File,
  params: OptimizationParams,
  maxRetries = 3
): Promise<OptimizationResponse> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await runOptimizedSubdivision(file, params);
    } catch (error) {
      if (attempt === maxRetries) throw error;
      
      const delay = Math.pow(2, attempt) * 1000;  // 2s, 4s, 8s
      await new Promise(resolve => setTimeout(resolve, delay));
      
      console.log(`Retry attempt ${attempt}/${maxRetries}...`);
    }
  }
}
```

**Strategy 2: Graceful Degradation**
```python
def calculate_roi_metrics(design: Dict) -> Dict:
    try:
        # Try full analysis with all modules
        financial = FinancialModel().calculate_roi_metrics(design)
        utilities = UtilityNetworkDesigner().design_all_networks(design)
        
        return {
            'roi': financial['roi_percentage'],
            'cost': financial['total_cost'],
            'utilities': utilities
        }
    except Exception as e:
        logger.warning(f"Full analysis failed: {e}, using simplified model")
        
        # Fallback to simplified calculation
        simple_cost = design['total_area'] * 1_000_000  # Rough estimate
        simple_revenue = len(design['lots']) * 10_000_000_000
        simple_roi = (simple_revenue - simple_cost) / simple_cost * 100
        
        return {
            'roi': simple_roi,
            'cost': simple_cost,
            'note': 'Simplified calculation due to error'
        }
```

**Strategy 3: Partial Results**
```python
def optimize_design(boundary, constraints, generations=100):
    best_design = None
    
    try:
        for gen in range(generations):
            # Optimization loop
            population = evolve(population)
            best_design = select_best(population)
            
            # Save checkpoint every 10 generations
            if gen % 10 == 0:
                save_checkpoint(best_design, gen)
                
    except KeyboardInterrupt:
        logger.info(f"Optimization interrupted at generation {gen}")
        return load_checkpoint()  # Return last saved state
    
    return best_design
```

---

## Performance Optimization

### Caching Strategy

```python
# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def calculate_lot_quality(lot_geometry: str) -> float:
    """Cache quality scores for identical geometries"""
    geom = from_wkt(lot_geometry)
    return compute_quality_score(geom)

# Cache financial parameters
import redis
redis_client = redis.Redis(host='localhost', port=6379)

def get_cost_parameters(country: str) -> Dict:
    cache_key = f"cost_params:{country}"
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Load from database
    params = load_from_db(country)
    
    # Cache for 1 hour
    redis_client.setex(cache_key, 3600, json.dumps(params))
    
    return params
```

### Parallel Processing

```python
from concurrent.futures import ProcessPoolExecutor

def evaluate_population_parallel(population: List[Design]) -> List[Tuple]:
    """Evaluate fitness of all individuals in parallel"""
    
    with ProcessPoolExecutor(max_workers=8) as executor:
        fitness_scores = list(executor.map(evaluate_fitness, population))
    
    return fitness_scores

# Batch utility routing
def route_utilities_batch(designs: List[Design]) -> List[UtilityNetwork]:
    """Route utilities for multiple designs in parallel"""
    
    with ProcessPoolExecutor() as executor:
        networks = list(executor.map(design_all_utilities, designs))
    
    return networks
```

---

## Conclusion

### System Capabilities Summary

**Input Processing:**
- ✅ DXF/DWG file parsing (2-5s)
- ✅ AI constraint extraction (5-10s)
- ✅ Boundary detection & validation

**Optimization:**
- ✅ Genetic algorithm (35-45s for 100 gen)
- ✅ Multi-objective (lots, quality, road, ROI)
- ✅ Constraint satisfaction (IEAT Thailand)

**Analysis:**
- ✅ Financial ROI calculation (1-2s)
- ✅ Utility network routing (3-5s)
- ✅ Terrain analysis (optional)
- ✅ Compliance checking (<1s)

**Output:**
- ✅ Interactive map visualization
- ✅ 3D rendering with Three.js
- ✅ DXF export for CAD
- ✅ PDF reports
- ✅ JSON data export

### Business Value Delivered

**For Developers:**
- 95% faster design iteration
- Automated compliance checking
- Data-driven decision making

**For Financial Teams:**
- Accurate ROI projections
- Detailed cost breakdowns
- Scenario comparison

**For Stakeholders:**
- Professional presentations
- Regulatory confidence
- Optimized land use

---

**Document Version:** 1.0
**Author:** Product Team
**Review Date:** January 2026
