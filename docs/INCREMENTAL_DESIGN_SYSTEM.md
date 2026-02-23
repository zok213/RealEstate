# Incremental Design System - Multi-Turn Chatbot

## Overview

Hệ thống thiết kế tăng dần cho phép người dùng:
- ✅ **Không cần prompt hoàn chỉnh** - Có thể tinh chỉnh từng parameter nhỏ
- ✅ **Multi-turn conversation** - Chat nhiều lượt để xây dựng design
- ✅ **IEAT Thailand compliance** - Validate mọi thay đổi theo chuẩn IEAT
- ✅ **Design iteration tracking** - Lưu lịch sử mọi thay đổi
- ✅ **Offline fallback** - Hoạt động khi API hết quota

## Features

### 1. Incremental Parameter Updates

```python
# Tăng green area từ 10% lên 12%
orchestrator.update_parameter(
    param_path="parameters.greenArea_percent",
    value=12,
    user_request="Tăng cây xanh lên 12%"
)
```

**Output:**
```json
{
  "status": "success",
  "message": "Updated parameters.greenArea_percent from 10 to 12",
  "param_path": "parameters.greenArea_percent",
  "old_value": 10,
  "new_value": 12,
  "validation": {
    "compliant": true,
    "rules": {
      "salable_area": {
        "compliant": true,
        "status": "Salable 77.6% (min 75%)"
      },
      "green_area": {
        "compliant": true,
        "status": "Green 12% (min 10%)"
      }
    }
  }
}
```

### 2. AI-Powered Suggestions

```python
# User: "Thêm 3 nhà máy nữa"
suggestions = orchestrator.suggest_adjustment(
    "Thêm 3 nhà máy light manufacturing nữa"
)
```

**Output:**
```json
{
  "action": "adjust_parameter",
  "target": "factory_count",
  "understood": "Thêm 3 nhà máy light manufacturing nữa",
  "changes": [
    {
      "param": "parameters.industryFocus[0].count",
      "from": 15,
      "to": 18
    }
  ],
  "impact": "Increased factory count. Check plot capacity.",
  "compliant": true
}
```

### 3. Batch Apply Changes

```python
# Apply multiple changes at once
changes = {
    "greenArea_percent": 12,
    "salableArea_percent": 76,
    "industryFocus[0].count": 18
}

result = orchestrator.apply_suggestions(changes)
```

**Output:**
```json
{
  "status": "success",
  "applied_count": 3,
  "failed": [],
  "updated_params": { ... },
  "validation": { ... }
}
```

### 4. IEAT Compliance Validation

Every update automatically validates against IEAT Thailand standards:

```python
validation = orchestrator._validate_ieat_compliance()
```

**Output:**
```json
{
  "compliant": true,
  "rules": {
    "salable_area": {
      "compliant": true,
      "status": "Salable 77.6% (min 75%)"
    },
    "green_area": {
      "compliant": true,
      "status": "Green 12% (min 10%)"
    },
    "ug_combined": {
      "compliant": true,
      "status": "U+G 267.2 rai (min 250 rai)"
    },
    "plot_frontage": {
      "compliant": true,
      "status": "Frontage 100m (min 90m)"
    }
  },
  "warnings": [],
  "errors": [],
  "recommendations": [
    "✅ Design meets IEAT Thailand standards",
    "💡 Consider optimizing plot layout for logistics"
  ]
}
```

## Usage Examples

### Scenario 1: Initial Design (Full Specification)

**User:** "Tôi có 191 hecta đất ở Thailand, muốn làm khu công nghiệp theo chuẩn IEAT"

**AI Response:**
```
Chào bạn! Tôi giúp thiết kế khu công nghiệp 191 hecta theo chuẩn IEAT Thailand.

Để bắt đầu, cho tôi biết thêm:
1. Ngành nghề chính: Sản xuất nhẹ, warehouse, logistics...?
2. Quy mô công nhân dự kiến?
3. Đặc điểm đất: Phẳng, có mặt nước, gần đường lớn?
```

### Scenario 2: Incremental Refinement

**User:** "Tăng diện tích cây xanh lên 12%"

**AI Response:**
```json
{
  "understood": "Tăng green area từ 10% lên 12%",
  "changes": [
    {"param": "greenArea_percent", "from": 10, "to": 12}
  ],
  "impact": "Green area tăng 2%. Salable area giảm còn 75.6%. Vẫn đạt chuẩn IEAT ✅",
  "validation": {
    "compliant": true,
    "rules": {
      "green_area": "✅ Green 12% (min 10%)",
      "salable_area": "✅ Salable 75.6% (min 75%)"
    }
  }
}
```

**User:** "Thêm 2 nhà máy nữa"

**AI Response:**
```json
{
  "understood": "Thêm 2 nhà máy vào industryFocus",
  "changes": [
    {"param": "industryFocus[0].count", "from": 15, "to": 17}
  ],
  "impact": "Tăng từ 15 lên 17 nhà máy. Cần kiểm tra diện tích plot.",
  "validation": {
    "compliant": true
  }
}
```

**User:** "Giảm frontage xuống 95m"

**AI Response:**
```json
{
  "understood": "Giảm plot frontage từ 100m xuống 95m",
  "changes": [
    {"param": "plotDimensions.frontageWidth_m", "from": 100, "to": 95}
  ],
  "impact": "Frontage 95m vẫn đạt chuẩn IEAT (min 90m) ✅",
  "validation": {
    "compliant": true,
    "rules": {
      "plot_frontage": "✅ Frontage 95m (min 90m)"
    }
  }
}
```

### Scenario 3: Design Review

**User:** "Xem lại toàn bộ thiết kế hiện tại"

**AI Response:**
```
📋 THIẾT KẾ HIỆN TẠI - Pilot Industrial Estate

Diện tích:
- Tổng: 191.42 ha (1,196 rai)
- Salable: 77.6% (148.5 ha)
- Utility: 12.4% (23.7 ha)  
- Green: 10% (19.1 ha)

Công trình:
- Light manufacturing: 15 nhà máy (40%)
- Warehouse: 8 kho (25%)
- Logistics: 3 trung tâm (15%)

Infrastructure:
- Retention pond: 20 rai
- Substation: 10 rai
- Roads: ROW 25m

✅ IEAT Compliance: 100% PASS
- ✅ Salable ≥ 75%
- ✅ Green ≥ 10%
- ✅ U+G ≥ 250 rai (large project)
- ✅ Plot frontage ≥ 90m

📊 Design Iterations: 3 changes
1. [2026-01-16 21:05] Tăng green area: 10% → 12%
2. [2026-01-16 21:06] Thêm nhà máy: 15 → 17
3. [2026-01-16 21:07] Giảm frontage: 100m → 95m
```

## API Endpoints

### POST /api/design-chat

Multi-turn conversation endpoint:

```typescript
// Request
{
  "message": "Tăng green area lên 12%",
  "sessionId": "pilot-191ha-v1",
  "mode": "incremental"  // or "full" for complete spec
}

// Response
{
  "response": "✅ Đã tăng green area lên 12%...",
  "parameters": { ... },
  "validation": { ... },
  "readyForGeneration": false
}
```

### POST /api/designs/update-parameter

Direct parameter update:

```typescript
// Request
{
  "sessionId": "pilot-191ha-v1",
  "param_path": "parameters.greenArea_percent",
  "value": 12,
  "user_request": "Tăng cây xanh lên 12%"
}

// Response
{
  "status": "success",
  "message": "Updated greenArea_percent: 10 → 12",
  "validation": { ... }
}
```

### POST /api/designs/suggest

Get AI suggestions:

```typescript
// Request
{
  "sessionId": "pilot-191ha-v1",
  "query": "Thêm 3 nhà máy nữa"
}

// Response
{
  "action": "adjust_parameter",
  "target": "factory_count",
  "understood": "Thêm 3 nhà máy",
  "changes": [
    {"param": "industryFocus[0].count", "from": 15, "to": 18}
  ],
  "impact": "...",
  "compliant": true
}
```

### POST /api/designs/apply

Apply suggestions:

```typescript
// Request
{
  "sessionId": "pilot-191ha-v1",
  "suggestions": {
    "changes": [
      {"param": "greenArea_percent", "to": 12},
      {"param": "industryFocus[0].count", "to": 18}
    ]
  }
}

// Response
{
  "status": "success",
  "applied_count": 2,
  "failed": [],
  "updated_params": { ... },
  "validation": { ... }
}
```

## System Architecture

```
┌─────────────────┐
│   Chat UI       │ Next.js Frontend
│  (user input)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  IndustrialParkLLMOrchestrator │ Backend
│  - Multi-turn conversation   │
│  - Parameter tracking        │
│  - IEAT validation          │
└────────┬────────────────────┘
         │
    ┌────┴────────────────┐
    │                     │
    ▼                     ▼
┌─────────┐      ┌──────────────┐
│  LLM    │      │   IEAT       │
│ Gemini  │      │  Compliance  │
│ MegaLLM │      │   Checker    │
└─────────┘      └──────────────┘
```

## IEAT Thailand Standards

System validates all changes against:

### Land Use Ratios
- ✅ Salable Area: ≥ 75%
- ✅ Green Area: ≥ 10%
- ✅ Utility Area: ~12-15%
- ✅ Green Buffer: 10m strip

### Large Project Rules (> 1000 rai)
- ✅ U+G Combined: ≥ 250 rai

### Plot Design
- ✅ Shape: Rectangular
- ✅ W:D Ratio: 1:1.5 to 1:2
- ✅ Min Frontage: 90m
- ✅ Preferred: > 100m

### Road Standards
- ✅ Traffic Lane: 3.5m
- ✅ Min ROW: 25m
- ✅ Layout: Double-loaded secondary roads

### Infrastructure
- ✅ Retention Pond: 1 rai per 60 rai gross
- ✅ Water Treatment: 0.5 cmd/rai
- ✅ Wastewater: 0.4 cmd/rai
- ✅ Substation: 10 rai at center

## Testing

Run comprehensive test:

```bash
cd backend
python test_incremental.py
```

**Test Coverage:**
1. ✅ Parameter updates (single value)
2. ✅ IEAT compliance validation
3. ✅ AI-powered suggestions
4. ✅ Batch apply changes
5. ✅ Design iteration history
6. ✅ Offline fallback mode

## Conversation Modes

### MODE 1: Initial Planning (Full Specification)
- Ask about: area, target customers, industry focus
- Extract: totalArea_ha, salableArea_percent, greenArea_percent
- Validate against IEAT standards
- When complete, set readyForGeneration: true

### MODE 2: Incremental Refinement (Small Adjustments)
Examples:
- "Tăng green area lên 12%" → greenArea_percent: 12
- "Thêm 2 nhà máy nữa" → Update industryFocus count
- "Giảm frontage xuống 95m" → frontage_width_m: 95
- "Thay đổi plot ratio thành 1:1.8" → Update aspect ratio

For each adjustment:
1. Understand the specific change requested
2. Update ONLY the affected parameter
3. Validate new value against IEAT standards
4. Warn if non-compliant
5. Suggest alternatives if needed

### MODE 3: Design Review & Optimization
- Review current parameters
- Suggest improvements
- Optimize for cost, logistics, or customer requirements

## Next Steps

1. ✅ Backend orchestrator implemented
2. 🔄 Add API endpoints to main.py
3. 🔄 Update chat-interface.tsx for incremental UI
4. 🔄 Add parameter adjustment buttons
5. 🔄 Test end-to-end with Pilot DXF file

## Files Modified

- ✅ `backend/ai/llm_orchestrator.py` - Added incremental methods
- ✅ `backend/test_incremental.py` - Comprehensive tests
- ✅ `docs/INCREMENTAL_DESIGN_SYSTEM.md` - This document
- 🔄 `backend/api/main.py` - Need to add endpoints
- 🔄 `components/chat-interface.tsx` - Need UI updates

---

**Last Updated:** 2026-01-16  
**Status:** ✅ Backend Complete | 🔄 Frontend Integration Pending  
**Test Results:** 6/6 PASS (with offline fallback)
