# API Documentation - Financial & Optimization Endpoints

## Financial Analysis API

Base URL: `http://localhost:8000/api/financial`

### 1. Analyze Design Financial Metrics

**POST** `/api/financial/analyze`

Calculate comprehensive ROI metrics for an industrial park design.

**Request Body:**
```json
{
  "total_area": 100000,
  "roads": [
    {
      "type": "main",
      "length": 500
    },
    {
      "type": "internal",
      "length": 1200
    }
  ],
  "lots": [
    {
      "id": 1,
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[0, 0], [50, 0], [50, 50], [0, 50], [0, 0]]]
      },
      "quality_score": 85,
      "is_corner": true,
      "frontage": 50,
      "zone_type": "FACTORY"
    }
  ],
  "green_space_area": 15000,
  "cost_params": {
    "site_clearing": 80000,
    "grading": 120000,
    "roads_main": 2500000,
    "roads_internal": 1500000,
    "utilities_water": 500000,
    "utilities_sewer": 800000,
    "utilities_electrical": 400000,
    "drainage": 300000,
    "lighting": 150000,
    "landscaping": 200000,
    "contingency_rate": 0.15
  },
  "revenue_params": {
    "base_price_per_sqm": 3500000,
    "factory_premium": 1.2,
    "warehouse_discount": 0.9,
    "corner_premium": 1.15,
    "quality_threshold": 80,
    "quality_premium": 1.1,
    "large_lot_discount": 0.95,
    "irregular_discount": 0.92
  }
}
```

**Response:**
```json
{
  "roi_percentage": 42.3,
  "total_cost": 125000000000,
  "total_revenue": 178000000000,
  "gross_profit": 53000000000,
  "cost_breakdown": {
    "site_clearing": 8000000000,
    "grading": 12000000000,
    "roads": 45000000000,
    "utilities": 35000000000,
    "drainage": 3000000000,
    "lighting": 1500000000,
    "landscaping": 2000000000,
    "fees_permits": 3000000000,
    "contingency": 15500000000,
    "total_construction_cost": 125000000000
  },
  "revenue_breakdown": {
    "num_lots": 50,
    "total_revenue": 178000000000,
    "average_price_per_sqm": 3560000,
    "lots": [
      {
        "lot_id": 1,
        "area": 2500,
        "base_revenue": 8750000000,
        "final_revenue": 11062500000,
        "adjustments": {
          "factory_premium": 1750000000,
          "corner_premium": 562500000,
          "quality_premium": 0,
          "large_lot_discount": 0,
          "irregular_shape_discount": 0
        }
      }
    ]
  },
  "efficiency_metrics": {
    "cost_per_sqm": 1250000,
    "revenue_per_sqm": 1780000,
    "profit_margin": 29.8,
    "cost_per_lot": 2500000000
  }
}
```

### 2. Compare Multiple Designs

**POST** `/api/financial/compare`

Compare financial metrics for multiple design alternatives.

**Request Body:**
```json
{
  "designs": [
    {
      "id": "design_a",
      "name": "High Density Layout",
      "total_area": 100000,
      "roads": [...],
      "lots": [...]
    },
    {
      "id": "design_b",
      "name": "Green Space Focus",
      "total_area": 100000,
      "roads": [...],
      "lots": [...]
    }
  ],
  "cost_params": {...},
  "revenue_params": {...}
}
```

**Response:**
```json
{
  "comparisons": [
    {
      "id": "design_a",
      "name": "High Density Layout",
      "roi_percentage": 45.2,
      "total_cost": 120000000000,
      "total_revenue": 174000000000,
      "gross_profit": 54000000000,
      "rank": 1
    },
    {
      "id": "design_b",
      "name": "Green Space Focus",
      "roi_percentage": 38.7,
      "total_cost": 130000000000,
      "total_revenue": 180000000000,
      "gross_profit": 50000000000,
      "rank": 2
    }
  ],
  "best_design_id": "design_a",
  "ranking_criteria": "roi_percentage"
}
```

### 3. Get Cost/Revenue Parameters

**GET** `/api/financial/parameters`

Retrieve default cost and revenue parameters for Thailand industrial parks.

**Response:**
```json
{
  "cost_params": {
    "site_clearing": 80000,
    "grading": 120000,
    "roads_main": 2500000,
    "roads_internal": 1500000,
    "utilities_water": 500000,
    "utilities_sewer": 800000,
    "utilities_electrical": 400000,
    "drainage": 300000,
    "lighting": 150000,
    "landscaping": 200000,
    "contingency_rate": 0.15
  },
  "revenue_params": {
    "base_price_per_sqm": 3500000,
    "factory_premium": 1.2,
    "warehouse_discount": 0.9,
    "corner_premium": 1.15,
    "quality_threshold": 80,
    "quality_premium": 1.1,
    "large_lot_discount": 0.95,
    "irregular_discount": 0.92
  }
}
```

### 4. Quick ROI Estimate

**POST** `/api/financial/quick-estimate`

Fast ROI calculation without full design details.

**Request Body:**
```json
{
  "total_area": 100000,
  "num_lots": 50,
  "avg_lot_size": 2000,
  "road_percentage": 20,
  "green_space_percentage": 15
}
```

**Response:**
```json
{
  "estimated_roi": 40.5,
  "estimated_cost": 125000000000,
  "estimated_revenue": 175000000000,
  "estimated_profit": 50000000000,
  "assumptions": {
    "base_price_per_sqm": 3500000,
    "cost_per_sqm": 1250000
  },
  "note": "Preliminary estimate. Use /analyze for detailed calculation."
}
```

## Optimization API

Base URL: `http://localhost:8000/api/optimization`

### 1. Run Optimized Subdivision

**POST** `/api/optimization/run`

Generate optimized industrial park layout using genetic algorithm.

**Request:**
- Content-Type: `multipart/form-data`
- Fields:
  - `file`: DXF/DWG file
  - `parameters`: JSON string with optimization settings

**Parameters JSON:**
```json
{
  "population_size": 50,
  "generations": 100,
  "mutation_rate": 0.1,
  "constraints": {
    "min_lot_size": 500,
    "max_lot_size": 10000,
    "min_frontage": 20,
    "setback_front": 50,
    "setback_side": 20,
    "road_width": 12,
    "green_space_min": 0.15,
    "parking_ratio": 0.1
  },
  "objectives": {
    "maximize_lots": 1.0,
    "maximize_quality": 0.8,
    "maximize_road_efficiency": 0.6,
    "maximize_roi": 1.2
  },
  "include_financial_analysis": true,
  "include_utility_routing": true,
  "include_terrain_analysis": false
}
```

**Response:**
```json
{
  "design": {
    "total_area": 100000,
    "lots": [...],
    "roads": [...],
    "green_spaces": [...]
  },
  "fitness_scores": {
    "num_lots": 50,
    "quality_score": 85.3,
    "road_efficiency": 0.78,
    "roi_percentage": 42.5
  },
  "financial_analysis": {
    "roi_percentage": 42.5,
    "total_cost": 125000000000,
    "total_revenue": 178000000000,
    "gross_profit": 53000000000
  },
  "utility_networks": {
    "water": {
      "total_length": 2500,
      "cost": 1375000000,
      "num_pipes": 78
    },
    "sewer": {
      "total_length": 2800,
      "cost": 2352000000,
      "num_pipes": 82
    },
    "electrical": {
      "total_length": 3200,
      "cost": 1344000000,
      "num_cables": 95
    }
  },
  "compliance_check": {
    "ieat_thailand": {
      "green_space_min_15%": true,
      "setback_50m": true,
      "parking_10%": true,
      "fire_access_30m": true
    },
    "tcvn_vietnam": {
      "min_lot_500m2": true,
      "min_frontage_20m": true,
      "road_width_12m": true,
      "utility_corridor_3m": true
    }
  },
  "generation_time": 45.3,
  "convergence_generation": 67
}
```

## Utility Routing API

### Design Water Network

**POST** `/api/utilities/water`

Design water supply network for industrial park.

**Request:**
```json
{
  "lots": [...],
  "roads": [...],
  "water_source": {"x": 0, "y": 0}
}
```

**Response:**
```json
{
  "type": "water",
  "source": {"x": 0, "y": 0},
  "pipes": [
    {
      "id": 1,
      "from": {"x": 0, "y": 0},
      "to": {"x": 100, "y": 50},
      "length": 111.8,
      "type": "water"
    }
  ],
  "total_length": 2500,
  "cost": 1375000000,
  "num_connections": 50
}
```

### Design Sewer Network

**POST** `/api/utilities/sewer`

Design gravity sewer network with terrain consideration.

### Design Electrical Network

**POST** `/api/utilities/electrical`

Design electrical distribution network with redundancy.

## Terrain Analysis API

### Analyze Terrain

**POST** `/api/terrain/analyze`

Process elevation data and identify buildable areas.

**Request:**
```json
{
  "elevation_points": [
    {"x": 0, "y": 0, "z": 100.5},
    {"x": 10, "y": 0, "z": 100.8}
  ],
  "site_boundary": {
    "type": "Polygon",
    "coordinates": [[[0, 0], [200, 0], [200, 200], [0, 200], [0, 0]]]
  },
  "grid_resolution": 10.0,
  "max_slope": 15.0
}
```

**Response:**
```json
{
  "elevation_grid": {...},
  "slope_map": {...},
  "buildable_percentage": 87.5,
  "statistics": {
    "min_elevation": 98.2,
    "max_elevation": 105.7,
    "mean_elevation": 101.4,
    "max_slope": 12.3
  }
}
```

### Optimize Grading

**POST** `/api/terrain/grading`

Calculate optimal grading plan with cut/fill analysis.

**Response:**
```json
{
  "volumes": {
    "cut": 15000,
    "fill": 14800,
    "net": 200
  },
  "cost_breakdown": {
    "cut_cost": 750000000,
    "fill_cost": 1184000000,
    "haul_cost": 4000000,
    "total": 1938000000
  },
  "balance_factor": 0.987,
  "proposed_elevation": 101.5
}
```

## Error Responses

All endpoints return standard error format:

```json
{
  "detail": "Error message description",
  "error_code": "FINANCIAL_001",
  "status_code": 400
}
```

**Common Error Codes:**
- `FINANCIAL_001`: Invalid design data
- `FINANCIAL_002`: Missing required parameters
- `OPTIMIZATION_001`: Optimization failed to converge
- `UTILITY_001`: Network routing failed
- `TERRAIN_001`: Invalid elevation data

## Rate Limits

- 100 requests per minute per IP
- Optimization endpoints: 10 requests per minute (compute-intensive)

## Authentication

Currently using basic API key authentication:
```
Authorization: Bearer YOUR_API_KEY
```

Contact admin for API key.
