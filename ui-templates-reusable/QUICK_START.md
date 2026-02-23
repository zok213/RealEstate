# 🎨 UI Templates - Quick Start Guide

## 📋 Tổng quan

Folder này chứa **9 giao diện UI** được tổ chức sẵn để tái sử dụng:

### Static UI (6 files HTML + CSS + JS)
- ✅ Đã copy đầy đủ 6 file HTML
- ✅ Đã copy CSS và JavaScript dependencies
- ✅ Sẵn sàng sử dụng ngay không cần build

### Modern Framework (React + Vite)
- ⚠️ Cần copy thủ công từ `frontend/` folder
- Bao gồm: React 19, TypeScript, Vite, Konva canvas

---

## 🚀 Cách sử dụng cho project mới

### Option 1: Copy Static UI (Nhanh nhất)

```powershell
# Copy toàn bộ static-ui vào project mới
Copy-Item -Recurse "ui-templates-reusable/static-ui/*" "path/to/new-project/static/"
```

### Option 2: Copy Modern Framework

```powershell
# Copy framework source
Copy-Item -Recurse "frontend/src" "path/to/new-project/frontend/"
Copy-Item "frontend/package.json" "path/to/new-project/frontend/"
Copy-Item "frontend/vite.config.ts" "path/to/new-project/frontend/"
Copy-Item "frontend/tsconfig.json" "path/to/new-project/frontend/"

# Install và chạy
cd path/to/new-project/frontend
npm install
npm run dev
```

### Option 3: Copy cả hai

```powershell
Copy-Item -Recurse "ui-templates-reusable" "path/to/new-project/ui-shared"
```

---

## 📁 Files đã có sẵn trong static-ui/

### HTML Pages (6 files)
1. `index.html` - Landing page
2. `upload.html` - Upload interface  
3. `estate-detail.html` - Chi tiết dự án
4. `estate-map-view.html` - Xem bản đồ
5. `estate-plot-list.html` - Danh sách lô đất
6. `full-screen-map-view.html` - Bản đồ toàn màn hình

### Styles
- `css/main.css` - Global styles với dark theme, animations, custom scrollbar

### JavaScript Libraries
- `js/api.js` - API client (upload, generate, export)
- `js/utils.js` - Utility functions (formatting, notifications, loading)
- `js/estate-nav.js` - Navigation helpers
- `js/estate-detail.js` - Estate detail logic
- `js/estate-map.js` - Map integration

---

## ⚙️ Tùy chỉnh cho project mới

### 1. Thay đổi màu sắc

Sửa trong `static-ui/css/main.css`:

```css
:root {
    --primary: #36e27b;           /* Màu chính */
    --background-dark: #112117;    /* Nền tối */
    --surface-dark: #1b3224;       /* Bề mặt */
    --surface-border: #254632;     /* Viền */
}
```

### 2. Cấu hình API endpoint

Sửa trong `static-ui/js/api.js`:

```javascript
const API_BASE_URL = window.location.origin;
// Hoặc hardcode
const API_BASE_URL = 'https://your-api.com';
```

### 3. Thay đổi navigation

Sửa trong `static-ui/js/utils.js`:

```javascript
function navigateToEstate(estateId) {
    window.location.href = `/estate/${estateId}`;
    // Đổi thành route của bạn
}
```

---

## 🎯 Features có sẵn

### Static UI
- ✅ Responsive design
- ✅ Dark theme
- ✅ Loading animations
- ✅ Toast notifications
- ✅ Progress bars
- ✅ Status badges
- ✅ Custom scrollbar
- ✅ Error handling
- ✅ API client

### Modern Framework
- ✅ TypeScript
- ✅ React 19 + Hooks
- ✅ Vite (fast builds)
- ✅ Canvas rendering (Konva)
- ✅ State management
- ✅ Hot reload

---

## 📦 Dependencies

### Static UI
**Không cần npm install!** Chỉ cần:
- Google Fonts (Spline Sans) - loaded qua CDN
- Browser modern (Chrome, Edge, Firefox)

### Modern Framework
```json
{
  "react": "^19.2.0",
  "typescript": "~5.9.3",
  "vite": "^5.x",
  "konva": "^10.0.12",
  "axios": "^1.13.2",
  "lucide-react": "^0.555.0"
}
```

---

## 🔧 Để copy Modern Framework

Modern Framework chưa được copy vào folder này. Để thêm:

```powershell
# Từ thư mục gốc BID25-013
robocopy "frontend" "ui-templates-reusable/modern-framework" /E /XD node_modules dist .git __pycache__
```

Hoặc thủ công:
1. Copy folder `frontend/src/`
2. Copy `frontend/package.json`
3. Copy `frontend/vite.config.ts`
4. Copy `frontend/tsconfig.json`
5. Copy `frontend/index.html`

---

## 📝 Checklist khi sử dụng cho project mới

- [ ] Copy files vào project mới
- [ ] Đổi API endpoint trong `api.js`
- [ ] Tùy chỉnh màu sắc trong `main.css`
- [ ] Update navigation routes nếu cần
- [ ] Test upload functionality
- [ ] Test map rendering
- [ ] Verify responsive design
- [ ] Check browser compatibility

---

## 🌟 Tips

1. **Giữ nguyên cấu trúc folder** để dễ maintain
2. **Không modify files gốc**, copy ra để tùy chỉnh
3. **Version control**: Commit changes từng bước
4. **Test trước khi deploy**: Check trên nhiều browser

---

**Created**: January 22, 2026  
**Source**: BID25-013 Industrial Estate Project  
**Status**: ✅ Static UI ready | ⚠️ Modern Framework cần copy thủ công
