# 🚀 TESTING GUIDE - DXF Auto-Analysis System

## ✅ Hệ thống đã sẵn sàng!

### 📊 Status Check:
- ✅ Backend API: http://localhost:8001 (Running)
- ✅ Frontend UI: http://localhost:3000 (Running)
- ✅ DXF Analyzer: Working
- ✅ API Endpoint: `/api/upload-dxf` (Tested)

---

## 🧪 TEST SCENARIOS

### Scenario 1: Upload DXF qua UI (Recommended)

**Bước thực hiện:**

1. Mở trình duyệt: http://localhost:3000

2. Trong chat interface, click button:
   ```
   📁 Upload file DXF để tự động phân tích
   ```

3. Chọn file: `sample-data/Pilot_Existing Topo _ Boundary.dxf`

4. **Expected Result:**
   - Hiển thị card phân tích DXF với:
     - ✅ Thông tin khu đất (191.42 ha, 1699m × 2157m)
     - 💡 Gợi ý IEAT (294 plots, 77% salable, 12% green)
     - 📝 3 prompt mẫu (Simple, Detailed, Advanced)
     - ❓ Câu hỏi hỗ trợ (4 questions)

5. Click vào một trong 3 prompt mẫu → Auto fill vào input

6. Click Send hoặc chỉnh sửa prompt trước khi gửi

7. AI sẽ generate thiết kế dựa trên thông tin từ DXF

---

### Scenario 2: Test API trực tiếp

**Chạy test script:**

```bash
cd backend
python test_dxf_upload.py
```

**Expected Output:**
```
✅ Upload thành công!

📊 THÔNG TIN KHU ĐẤT:
   Diện tích: 191.42 ha (1,914,212 m²)
   Kích thước: 1699m × 2157m

💡 GỢI Ý THIẾT KẾ:
   Quy mô: large_industrial_park
   Số plots: ~294
   Salable: 147.4 ha
   Green: 23.0 ha
```

---

### Scenario 3: Test với cURL

```bash
curl -X POST http://localhost:8001/api/upload-dxf \
  -F "file=@sample-data/Pilot_Existing Topo _ Boundary.dxf"
```

---

## 🎯 DEMO WORKFLOW

### Full User Journey:

```
1. User mở app → Chat interface
   ↓
2. Click "📁 Upload file DXF"
   ↓
3. Chọn file DXF (191.42 ha)
   ↓
4. Backend auto-analyze:
   - Parse boundary
   - Calculate area & dimensions
   - Apply IEAT standards
   - Generate suggestions & questions
   ↓
5. UI hiển thị DXF Analysis Card:
   ┌─────────────────────────────────┐
   │ ✅ Phân tích thành công!         │
   │ 📍 191.42 ha                    │
   │ 🏭 ~294 plots                   │
   │ 🌳 23.0 ha green                │
   │                                 │
   │ 📝 Prompt mẫu:                  │
   │ [🚀 Simple]                     │
   │ [📊 Detailed]                   │
   │ [🎯 Advanced]                   │
   └─────────────────────────────────┘
   ↓
6. User click "📊 Detailed" prompt
   → Input auto-fill với prompt
   ↓
7. User review & send
   ↓
8. AI extract parameters
   ↓
9. Generate design với CSP + GA
   ↓
10. Display variants trên map
```

---

## 🔍 VERIFICATION CHECKLIST

### Frontend (http://localhost:3000):

- [ ] Chat interface hiển thị đúng
- [ ] Upload button có icon 📁 và text "Upload file DXF"
- [ ] Click upload → File picker mở ra
- [ ] Chọn DXF file → Progress "Đang phân tích..."
- [ ] DXF Analysis Card hiển thị với:
  - [ ] Site info (area, dimensions)
  - [ ] Suggestions (plots, land use)
  - [ ] 3 prompt buttons (clickable)
  - [ ] Questions section
- [ ] Click prompt button → Input field được fill
- [ ] Send message → AI response

### Backend (http://localhost:8001/docs):

- [ ] API docs accessible
- [ ] `/api/upload-dxf` endpoint visible
- [ ] Can test upload từ docs UI
- [ ] Response format correct:
  ```json
  {
    "success": true,
    "filename": "...",
    "site_info": {...},
    "suggestions": {...},
    "questions": [...],
    "sample_prompts": [...]
  }
  ```

---

## 📝 TEST DATA

### Available DXF Files:

1. **Pilot Project** (Recommended for testing)
   - Path: `sample-data/Pilot_Existing Topo _ Boundary.dxf`
   - Size: 191.42 ha
   - Features: Complete boundary, topography

2. **KCN Song Than**
   - Path: `examples/kcn_song_than_binh_duong.dxf`
   - Size: ~50 ha

3. **Other samples**
   - `examples/663409.dxf`
   - `examples/930300.dxf`

---

## 🐛 TROUBLESHOOTING

### Issue: Upload button không hiển thị
**Fix:** 
```bash
cd frontend
pnpm install
pnpm dev
```

### Issue: API 500 error khi upload
**Fix:** Check backend logs:
```bash
# Backend terminal output
# Look for Python traceback
```

### Issue: DXF Analysis Card không hiển thị
**Fix:** 
- Check browser console (F12)
- Verify component import: `import { DXFAnalysisCard } from "@/components/dxf-analysis-card"`

### Issue: "Không thể phân tích file DXF"
**Fix:**
- Verify file là DXF format (R12-R2018)
- Check file có LWPOLYLINE hoặc POLYLINE
- File không bị corrupt

---

## 🎨 UI COMPONENTS ADDED

### New Files:
1. `components/dxf-analysis-card.tsx` - Display DXF analysis results
2. `backend/ai/dxf_analyzer.py` - DXF parsing & analysis logic
3. `backend/test_dxf_upload.py` - API test script

### Modified Files:
1. `components/chat-interface.tsx` - Added upload button + DXF integration
2. `utils/api-client.ts` - Added `uploadAndAnalyzeDXF()` method
3. `backend/api/main.py` - Added `/api/upload-dxf` endpoint
4. `backend/ai/llm_orchestrator.py` - Added `inject_dxf_context()` method
5. `backend/config.py` - Updated to IEAT as primary standard

---

## 📊 PERFORMANCE METRICS

### Expected Times:
- DXF Upload: < 1s
- DXF Analysis: < 2s
- AI Context Injection: < 0.5s
- Prompt Generation: < 0.1s
- **Total User Wait Time: ~3s**

---

## 🎉 SUCCESS CRITERIA

✅ User có thể upload DXF trong 1 click
✅ System tự động phân tích trong < 3s
✅ Hiển thị gợi ý rõ ràng, dễ hiểu
✅ 3 prompt mẫu sẵn sàng để dùng
✅ Câu hỏi hỗ trợ giúp refine yêu cầu
✅ One-click để bắt đầu thiết kế

---

## 🚀 NEXT STEPS (Optional Enhancements)

1. **Drag & Drop DXF** - Kéo thả file vào chat
2. **Preview DXF** - Hiển thị boundary trên map
3. **Multi-file Support** - Upload nhiều DXF cùng lúc
4. **DXF Validation** - Check file quality trước khi analyze
5. **History** - Lưu DXF đã upload

---

## 📞 SUPPORT

Nếu gặp issue, check:
1. Backend logs: Terminal running uvicorn
2. Frontend console: Browser DevTools (F12)
3. API response: http://localhost:8001/docs

Happy Testing! 🎊
