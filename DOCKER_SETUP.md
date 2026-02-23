# Industrial Park AI Designer - Docker Setup

## 📦 Docker Images

Có 2 images đã được tạo:

### 1. Backend Docker Image

**Location:** `d:\git\new realestate\backend\Dockerfile`

**Build:**
```bash
cd backend
docker build -t industrial-park-backend:latest .
```

**Features:**
- Python 3.13-slim base
- Multi-stage build (giảm size image)
- FastAPI backend với AI orchestrator
- Port: 8001
- Health check endpoint: `/health`

### 2. Frontend Docker Image

**Location:** `d:\git\new realestate\Dockerfile.frontend`

**Build:**
```bash
docker build -f Dockerfile.frontend -t industrial-park-frontend:latest .
```

**Features:**
- Node 20 Alpine base
- Next.js 16.0.10 với Turbopack
- Standalone output mode
- Port: 3000

---

## 🚀 Cách sử dụng

### Option 1: Docker Compose (Recommended)

Chạy cả backend + frontend cùng lúc:

```bash
# Build và start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Services:**
- Backend API: http://localhost:8001
- Frontend UI: http://localhost:3000
- Backend API Docs: http://localhost:8001/docs

### Option 2: Docker riêng lẻ

#### Backend Only:
```bash
cd backend
docker build -t industrial-park-backend .

docker run -d \
  --name backend \
  -p 8001:8001 \
  -e GOOGLE_API_KEY=AIzaSyAIbeJTLQcqt-MX_QFMDvGTMTuz8AFh_do \
  -e MEGALLM_API_KEY=sk-mega-... \
  -v $(pwd)/examples:/app/examples:ro \
  industrial-park-backend
```

#### Frontend Only:
```bash
docker build -f Dockerfile.frontend -t industrial-park-frontend .

docker run -d \
  --name frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_BACKEND_URL=http://localhost:8001 \
  industrial-park-frontend
```

---

## 🔧 Docker Image đã có sẵn

Kiểm tra images hiện tại:
```bash
docker images
```

**Output:**
```
REPOSITORY                   TAG         SIZE
your-api                     latest      1.11GB   # Land Redistribution API (docker folder)
algorithms-backend           latest      1.11GB   # Old algorithms backend
```

### Image `your-api:latest`

Đây là image cho **Land Redistribution Algorithm API** (trong folder `backend/docker`), khác với project chính.

**Chạy image này:**
```bash
docker run -d \
  --name land-redistribution \
  -p 7860:7860 \
  your-api:latest
```

**Endpoints:**
- API: http://localhost:7860
- Docs: http://localhost:7860/docs
- Health: http://localhost:7860/health

**Features:**
- DXF upload và phân tích
- NSGA-II genetic algorithm optimization
- OR-Tools constraint programming
- Block subdivision
- GeoJSON export

---

## 🎯 So sánh 2 Systems

| Feature | Main Project | Land Redistribution (`your-api`) |
|---------|-------------|----------------------------------|
| **Purpose** | Industrial park design chatbot | Land subdivision algorithm |
| **Port** | 8001 (backend), 3000 (frontend) | 7860 |
| **AI** | Gemini 2.0 Flash, MegaLLM | NSGA-II + OR-Tools |
| **Input** | Chat conversation | DXF file upload |
| **Output** | Design parameters + layout | Optimized grid + GeoJSON |
| **Standards** | IEAT Thailand | Generic optimization |

---

## 🔄 Tích hợp 2 systems

Có thể kết hợp cả 2 để có workflow hoàn chỉnh:

```yaml
# docker-compose.full.yml
services:
  # Main AI Designer Backend
  backend:
    build: ./backend
    ports:
      - "8001:8001"
  
  # Frontend UI
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
  
  # Land Redistribution Engine
  redistribution:
    image: your-api:latest
    ports:
      - "7860:7860"
```

**Workflow:**
1. User chat với AI (port 3000) → Xác định parameters
2. Backend (8001) gọi optimization engine
3. Redistribution API (7860) chạy NSGA-II + OR-Tools
4. Kết quả trả về qua chat interface

---

## 📝 Environment Variables

### Backend:
```bash
GOOGLE_API_KEY=AIzaSyAIbeJTLQcqt-MX_QFMDvGTMTuz8AFh_do
MEGALLM_API_KEY=sk-mega-3290d012aeebdb8ae4857f31ecb44d1f23745ea713a34090cc3d1803ed0444af
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

### Frontend:
```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8001
```

---

## 🐛 Troubleshooting

### Port conflicts:
```bash
# Check what's using port
netstat -ano | findstr ":8001"
netstat -ano | findstr ":3000"

# Kill process
Stop-Process -Id <PID> -Force
```

### Docker logs:
```bash
docker logs industrial-park-backend -f
docker logs industrial-park-frontend -f
```

### Rebuild without cache:
```bash
docker-compose build --no-cache
docker-compose up -d --force-recreate
```

---

## ✅ Next Steps

1. **Build images mới:**
   ```bash
   cd d:\git\new realestate
   docker-compose build
   ```

2. **Test chạy:**
   ```bash
   docker-compose up -d
   ```

3. **Verify:**
   - Backend: http://localhost:8001/health
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8001/docs

4. **Integrate redistribution:**
   - Call `your-api:7860` từ backend khi cần optimization
   - Pass DXF data qua API
   - Nhận GeoJSON results

---

**Status:** ✅ Docker setup complete  
**Images:** 2 existing + 2 new (backend + frontend)  
**Ready to deploy:** Yes (local or cloud)
