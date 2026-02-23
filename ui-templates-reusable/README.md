# UI Templates Reusable

Bộ sưu tập các giao diện UI có thể tái sử dụng cho các dự án Real Estate khác.

## 📁 Cấu trúc

```
ui-templates-reusable/
├── static-ui/           # 6 giao diện HTML tĩnh
│   ├── css/
│   │   └── main.css    # Global styles
│   ├── js/
│   │   ├── api.js      # API client
│   │   ├── utils.js    # Utility functions
│   │   ├── estate-detail.js
│   │   ├── estate-map.js
│   │   └── estate-nav.js
│   ├── index.html
│   ├── upload.html
│   ├── estate-detail.html
│   ├── estate-map-view.html
│   ├── estate-plot-list.html
│   └── full-screen-map-view.html
│
└── modern-framework/    # React + TypeScript framework
    ├── src/
    ├── package.json
    ├── vite.config.ts
    └── tsconfig.json
```

## 🎨 Static UI Templates

### 1. **index.html** - Trang chủ
- Landing page với hero section
- Navigation menu
- Feature highlights

### 2. **upload.html** - Upload DXF Files
- Drag & drop upload interface
- Progress bar
- File validation

### 3. **estate-detail.html** - Chi tiết khu công nghiệp
- Thông tin chi tiết dự án
- Image gallery
- Specifications table

### 4. **estate-map-view.html** - Xem bản đồ
- Interactive map view
- Plot selection
- Zoom controls

### 5. **estate-plot-list.html** - Danh sách lô đất
- Grid/List view toggle
- Filter & sort options
- Status badges

### 6. **full-screen-map-view.html** - Bản đồ toàn màn hình
- Full-screen map interface
- Advanced controls
- Layer management

## 🚀 Modern Framework (React + TypeScript + Vite)

### Tech Stack
- **React 19.2.0** - UI library
- **TypeScript 5.9.3** - Type safety
- **Vite** - Build tool
- **Konva & React-Konva** - Canvas rendering
- **Axios** - HTTP client
- **Lucide React** - Icon library

### Features
- Professional map visualization
- Canvas-based rendering
- Type-safe development
- Hot module replacement
- Modern build optimization

## 📦 Cài đặt

### Static UI
Không cần cài đặt, copy files và sử dụng trực tiếp:
```bash
# Copy toàn bộ folder static-ui vào project mới
cp -r static-ui /path/to/new-project/
```

### Modern Framework
```bash
cd modern-framework
npm install
npm run dev      # Development server
npm run build    # Production build
```

## 🔧 Tùy chỉnh

### Static UI
1. **Colors**: Sửa CSS variables trong `css/main.css`
```css
:root {
    --primary: #36e27b;
    --background-dark: #112117;
    --surface-dark: #1b3224;
    --surface-border: #254632;
}
```

2. **API Endpoint**: Sửa trong `js/api.js`
```javascript
const API_BASE_URL = window.location.origin;
// hoặc
const API_BASE_URL = 'https://your-api.com';
```

### Modern Framework
1. **Configuration**: Sửa `vite.config.ts`
2. **Environment**: Tạo `.env` file
```
VITE_API_URL=http://localhost:8000
VITE_MAP_API_KEY=your_key
```

## 🎯 Sử dụng với Project mới

### Option 1: Copy toàn bộ
```bash
cp -r ui-templates-reusable /path/to/new-project/ui
```

### Option 2: Copy từng phần
```bash
# Chỉ copy Static UI
cp -r ui-templates-reusable/static-ui /path/to/new-project/

# Chỉ copy Modern Framework
cp -r ui-templates-reusable/modern-framework /path/to/new-project/frontend
```

### Option 3: Symlink (để cập nhật đồng bộ)
```bash
ln -s /absolute/path/to/ui-templates-reusable /path/to/new-project/ui-shared
```

## 🌟 Features

### Static UI
- ✅ Responsive design
- ✅ Dark theme
- ✅ Smooth animations
- ✅ Custom scrollbar
- ✅ Loading states
- ✅ Error handling
- ✅ No build required

### Modern Framework
- ✅ TypeScript type safety
- ✅ Component-based architecture
- ✅ State management (React hooks)
- ✅ Canvas rendering for maps
- ✅ Modern tooling (Vite, ESLint)
- ✅ Hot reload
- ✅ Production-ready builds

## 📝 Dependencies

### Static UI
- **Font**: Spline Sans (Google Fonts)
- **Map Libraries**: Leaflet.js (optional)
- **Icons**: Lucide Icons (optional)

### Modern Framework
```json
{
  "react": "^19.2.0",
  "typescript": "~5.9.3",
  "vite": "^5.x",
  "konva": "^10.0.12",
  "axios": "^1.13.2"
}
```

## 🔄 Cập nhật

Khi có thay đổi trong template gốc, sync lại:
```bash
# Từ project gốc
cd BID25-013
git pull

# Copy files mới nhất
cp -r ui-templates-reusable /path/to/other-project/
```

## 📄 License

MIT - Tự do sử dụng và tùy chỉnh cho các dự án khác.

## 🤝 Contributing

Nếu có improvements, vui lòng update trong project gốc BID25-013 và sync lại.

---

**Created**: January 2026  
**Source Project**: BID25-013 - Industrial Estate Master Plan Optimizer
