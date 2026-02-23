# Industrial Park AI Designer

AI-powered industrial park subdivision design system with genetic algorithm optimization, financial analysis, and regulatory compliance checking.

## 🎯 Overview

This system generates optimized industrial park layouts from CAD files (DXF/DWG), balancing multiple objectives:

- Number of lots
- Design quality
- Road network efficiency
- Return on investment (ROI)
- Regulatory compliance (IEAT Thailand Standards)

## ✨ Features

### Core Functionality

- 🎯 **AI-Powered Subdivision Design**: Genetic algorithm optimization for industrial park layouts
- 📊 **Financial Analysis**: Comprehensive ROI calculation with cost/revenue modeling
- 🗺️ **DXF/DWG Processing**: Parse CAD files and extract boundary/constraint data
- 🏗️ **Multi-Objective Optimization**: Balance lot count, quality, road efficiency, and profitability
- ⚡ **Real-time Visualization**: Interactive 2D/3D design preview

### Advanced Features

- 💰 **Financial Optimization Module** (NEW):
  - Detailed cost breakdown (11 cost categories)
  - Revenue projection with premiums/discounts
  - ROI/profit margin calculation
  - Design comparison and ranking
  
- 🔧 **Utility Routing System** (NEW):
  - Water network design (Steiner tree algorithm)
  - Sewer network design (gravity flow optimization)
  - Electrical distribution (MST with redundancy)
  - Cost estimation per meter in VND
  
- 🏔️ **Terrain Analysis** (NEW):
  - DEM interpolation from point cloud
  - Slope calculation and buildable area identification
  - Cut/fill volume optimization
  - Grading cost estimation
  
- 📋 **Advanced Constraint Editor** (NEW):
  - Visual rule builder with 14 parameters
  - Pre-built templates (IEAT Thailand, Custom)
  - Hard/soft constraint priorities
  - JSON import/export

### Compliance

- ✅ **IEAT Thailand Standards**: Green space (15%), setbacks (50m), parking (10%), fire access (30m)
- ✅ **TCVN 7144 Vietnam Standards**: Lot sizes (500m²), frontage (20m), roads (12m), utilities (3m)
- 📈 **Real-time Compliance Checking**: Automated validation during design generation

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.12+
- pnpm (for frontend)
- Docker (optional, for containerized deployment)

### Installation

1. **Clone repository:**

```bash
git clone https://github.com/yourusername/new-realestate.git
cd new-realestate
```

1. **Install frontend dependencies:**

```bash
pnpm install
```

1. **Install backend dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

1. **Set up environment variables:**

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (backend/.env)
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/realestate
```

### Running the Application

**Development Mode:**

```bash
# Terminal 1: Frontend
pnpm dev

# Terminal 2: Backend
cd backend
uvicorn api.main:app --reload
```

**Production Mode:**

```bash
docker-compose up
```

Access the application:

- Frontend: <http://localhost:5701>
- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

## 📖 Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - REST API endpoints and usage
- [Testing Guide](TESTING_GUIDE.md) - Testing strategies and test suite
- [Backend Plan](docs/backend_plan.md) - System architecture and design
- [Compliance Standards](docs/PILOT_PROJECT_IEAT_COMPLIANCE.md) - IEAT Thailand requirements
- [User Stories](docs/USER_STORIES.md) - Feature requirements and use cases

## 🧪 Testing

Run comprehensive test suite:

```bash
cd backend
python -m pytest tests/test_new_optimizers.py -v
```

Test coverage:

- Financial Optimizer: 4 tests (cost, revenue, ROI, multi-objective)
- Utility Router: 4 tests (water, sewer, electrical, cost estimation)
- Terrain Analyzer: 5 tests (DEM, slope, buildable areas, cut/fill, grading)

**Result: 13/13 tests passing ✅**

## 🏗️ Architecture

```
├── app/                    # Next.js frontend
│   ├── api/               # API route handlers
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── backend/               # Python backend
│   ├── ai/               # AI/ML modules
│   │   ├── dxf_analyzer.py
│   │   └── llm_orchestrator.py
│   ├── api/              # FastAPI routes
│   │   ├── main.py
│   │   └── financial_endpoints.py
│   ├── optimization/     # Optimization modules
│   │   ├── financial_optimizer.py
│   │   ├── utility_router.py
│   │   └── terrain_analyzer.py
│   ├── design/           # Design modules
│   │   └── compliance_checker.py
│   └── tests/            # Test suite
├── components/           # React components
│   ├── financial-metrics-panel.tsx
│   ├── advanced-constraint-editor.tsx
│   └── industrial-park-designer.tsx
├── docs/                 # Documentation
└── examples/             # Sample DXF files
```

## 🎨 Usage Examples

### 1. Generate Optimized Design

```typescript
import { runOptimizedSubdivision } from '@/utils/optimization-api';

const result = await runOptimizedSubdivision(dxfFile, {
  population_size: 50,
  generations: 100,
  constraints: {
    min_lot_size: 500,
    green_space_min: 0.15
  },
  objectives: {
    maximize_lots: 1.0,
    maximize_roi: 1.2
  }
});
```

### 2. Analyze Financial Metrics

```typescript
import { analyzeFinancial } from '@/utils/optimization-api';

const analysis = await analyzeFinancial(design);
console.log(`ROI: ${analysis.roi_percentage}%`);
console.log(`Profit: ${formatBillionVND(analysis.gross_profit)}`);
```

### 3. Route Utility Networks

```python
from optimization.utility_router import UtilityNetworkDesigner

designer = UtilityNetworkDesigner()
water_network = designer.design_water_network(
    lots, roads, water_source=Point(0, 0)
)
print(f"Water cost: {water_network['cost']/1e6:.1f}M VND")
```

## 🔧 Configuration

### Optimization Parameters

```json
{
  "population_size": 50,
  "generations": 100,
  "mutation_rate": 0.1,
  "crossover_rate": 0.8,
  "tournament_size": 3,
  "elitism_rate": 0.1
}
```

### Cost Parameters (VND)

```json
{
  "site_clearing": 80000,
  "grading": 120000,
  "roads_main": 2500000,
  "utilities_water": 500000,
  "utilities_sewer": 800000,
  "utilities_electrical": 400000
}
```

### Revenue Parameters

```json
{
  "base_price_per_sqm": 3500000,
  "factory_premium": 1.2,
  "corner_premium": 1.15,
  "quality_premium": 1.1
}
```

## 📊 Performance

- Design generation: ~45 seconds (100 generations, 50 population)
- Financial analysis: <2 seconds
- Utility routing: ~5 seconds (50 lots)
- Terrain analysis: ~10 seconds (1000 elevation points)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Authors

- Development Team - Industrial Park AI Designer

## 🙏 Acknowledgments

- IEAT Thailand for regulatory standards
- IEAT Thailand for industrial estate standards and regulations
- NetworkX for graph algorithms
- Shapely for geometric operations
