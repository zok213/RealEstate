# 🔄 DETAILED DATA FLOW PIPELINE
## Industrial Estate AI Master Planning System

**Date:** January 28, 2026  
**Version:** 1.0  
**Purpose:** Complete data transformation pipeline from user input to final output

---

## 📊 OVERVIEW DIAGRAM

```
┌─────────────────┐
│  USER INPUTS    │
│  - DXF/DWG File │
│  - Form Data    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                   PROCESSING PIPELINE                        │
│                                                              │
│  Step 1: File Upload & Validation                           │
│  Step 2: DXF Parsing & Boundary Extraction                  │
│  Step 3: Terrain Analysis                                   │
│  Step 4: Requirements Collection & Validation                │
│  Step 5: Constraint Resolution                               │
│  Step 6: AI Design Generation                                │
│  Step 7: Regulatory Compliance Check                         │
│  Step 8: Financial Calculation                               │
│  Step 9: Output Generation                                   │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  FINAL OUTPUT   │
│  - DXF/DWG File │
│  - PDF Report   │
│  - Web Preview  │
└─────────────────┘
```

---

## 🔍 STEP-BY-STEP DATA FLOW

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 1: FILE UPLOAD & VALIDATION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


**Input:**
```json
{
  "file": "site_boundary.dxf" // or "site_boundary.dwg",
  "file_size": 12_450_000,  // bytes
  "file_type": "application/dxf" // or "application/acad",
  "uploaded_by": "user_id_123",
  "timestamp": "2026-01-28T10:30:00Z"
}
```

**Processing:**
```python
# Validation checks
1. Check file size < 50MB
2. Check file extension (.dxf or .dwg)
3. Verify MIME type (application/dxf or application/acad)
4. Scan for malicious content
5. Generate unique file ID
```

**Output:**
```json
{
  "status": "validated",
  "file_id": "cad_20260128_103000_abc123",
  "file_path": "/uploads/cad_20260128_103000_abc123.dxf", // or .dwg
  "validation": {
    "size_ok": true,
    "format_ok": true,
    "mime_ok": true,
    "safe": true
  },
  "next_step": "parse_dxf"
}
```

**Error Handling:**
```json
// If validation fails
{
  "status": "error",
  "error_code": "FILE_TOO_LARGE",
  "message": "File size 65MB exceeds 50MB limit",
  "user_message": "Please upload a DXF or DWG file smaller than 50MB"
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 2: DXF PARSING & BOUNDARY EXTRACTION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "file_path": "/uploads/cad_20260128_103000_abc123.dxf", // or .dwg
  "file_id": "cad_20260128_103000_abc123"
}
```

**Processing:**


The DXF/DWG parsing process follows a multi-stage approach:

**Stage 1: File Reading and Layer Extraction**
The system opens the DXF or DWG file using a CAD library that supports both formats and accesses the modelspace (where all entities are stored). It then categorizes entities into logical groups based on layer names:
- Layers containing "boundary" or "perimeter" → Site boundary
- Layers with "contour" or "elevation" → Topographic data
- Layers named "roads", "utilities", "structures" → Existing infrastructure

**Stage 2: Entity Type Processing**
For each entity, the system identifies its type (polyline, circle, text, etc.) and extracts coordinates. Polylines and LWPolylines are the most common for boundaries - the system converts their vertices into coordinate arrays.

**Stage 3: Boundary Identification**
When multiple boundary candidates exist, the system applies logic to identify the main site boundary:
- Selects the largest closed polygon
- Validates it's actually closed (first and last points match)
- Checks for self-intersections (invalid geometry)
- Converts coordinates to standard CRS (WGS84)

**Stage 4: Area Calculation**
Using geodesic algorithms (accounting for Earth's curvature), the system calculates:
- Total area in square meters
- Conversion to rai (Thai land measurement: 1 rai = 1,600 sqm)
- Perimeter length

**Stage 5: Contour Extraction**
For elevation data, the system extracts contour lines and their associated elevation values from entity attributes or layer names (e.g., "CONTOUR-10M" indicates 10-meter elevation).

**Note:** The system supports both DXF and DWG files for all parsing and extraction steps. Some very old or proprietary DWG versions may have limited support depending on the CAD library used.

**Output:**
```json
{
  "status": "parsed",
  "file_id": "dxf_20260128_103000_abc123",
  "geometry": {
    "boundary": {
      "type": "Polygon",
      "coordinates": [
        [
          [100.5234, 13.7456],
          [100.5456, 13.7456],
          [100.5456, 13.7234],
          [100.5234, 13.7234],
          [100.5234, 13.7456]  // Closed polygon
        ]
      ],
      "crs": "EPSG:4326"  // WGS84
    },
    "area_sqm": 162_450.5,
    "area_rai": 101.53,
    "perimeter_m": 1_650.2
  },
  "layers_found": {
    "boundary": true,
    "contours": true,
    "existing_structures": false,
    "roads": false,
    "utilities": false
  },
  "contours": [
    {
      "elevation": 10.0,
      "coordinates": [[100.5235, 13.7457], ...]
    },
    {
      "elevation": 12.0,
      "coordinates": [[100.5238, 13.7460], ...]
    }
  ],
  "next_step": "analyze_terrain"
}
```

**Data Transformations:**
```
Raw DXF/DWG entities → Parsed geometry objects → Validated polygons
    ↓
- Convert coordinates to standard CRS (WGS84)
- Calculate area using geodesic algorithms
- Validate polygon (no self-intersections, closed)
- Extract metadata (units, coordinate system)
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 3: TERRAIN ANALYSIS**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "boundary": { /* Polygon from Step 2 */ },
  "contours": [
    {"elevation": 10.0, "coordinates": [...]},
    {"elevation": 12.0, "coordinates": [...]},
    {"elevation": 14.0, "coordinates": [...]}
  ]
}
```

**Processing:**

The terrain analysis module transforms contour data into actionable insights:

**Stage 1: Elevation Grid Creation**
The system creates a regular grid covering the entire site (typically 5-meter spacing). At each grid point, elevation is interpolated from nearby contour lines using weighted averaging. Points closer to a contour line are influenced more heavily by that contour's elevation.

**Stage 2: Slope Calculation**
For each grid cell, the system calculates slope percentage by comparing elevation with neighboring cells. Slope is computed in both X and Y directions, then combined to get the true slope vector. This produces a slope map showing where terrain is flat, gentle, moderate, or steep.

**Stage 3: Buildability Analysis**
Based on slope data, the system classifies areas:
- **Flat (0-5% slope):** Ideal for building, minimal grading needed
- **Gentle (5-10%):** Buildable with minor grading
- **Moderate (10-15%):** Challenging, requires significant earthwork
- **Steep (>15%):** Generally unbuildable or requires special engineering

The system creates a buildability mask indicating which areas are suitable for lot placement.

**Stage 4: Statistical Analysis**
The system computes summary statistics:
- Elevation range (min, max, mean, standard deviation)
- Average and maximum slopes
- Percentage of site in each slope category
- Identification of natural low points (drainage collection areas)

**Stage 5: Drainage Pattern Analysis**
By analyzing elevation gradients, the system determines natural water flow direction and identifies areas requiring drainage infrastructure.

**Output:**
```json
{
  "status": "analyzed",
  "terrain": {
    "elevation": {
      "min_m": 8.5,
      "max_m": 16.2,
      "mean_m": 12.3,
      "range_m": 7.7,
      "std_dev_m": 2.1
    },
    "slope": {
      "mean_percent": 3.2,
      "max_percent": 12.5,
      "areas_by_slope": {
        "flat_0_5_percent": 45.2,      // % of site
        "gentle_5_10_percent": 38.6,
        "moderate_10_15_percent": 14.8,
        "steep_15_plus_percent": 1.4
      }
    },
    "buildability": {
      "ideal_flat_areas_percent": 45.2,
      "buildable_with_minor_grading_percent": 38.6,
      "challenging_areas_percent": 14.8,
      "unbuildable_areas_percent": 1.4
    },
    "drainage": {
      "flow_direction": "northwest_to_southeast",
      "natural_low_points": 3,  // Number of natural collection points
      "requires_drainage_system": true
    }
  },
  "warnings": [
    {
      "type": "steep_area",
      "severity": "low",
      "message": "1.4% of site has slope >15%, may require special grading",
      "location": {"type": "Point", "coordinates": [100.5445, 13.7245]}
    }
  ],
  "next_step": "collect_requirements"
}
```

**Visualization Data (for frontend):**
```json
{
  "heatmaps": {
    "elevation": "base64_encoded_png...",
    "slope": "base64_encoded_png...",
    "buildability": "base64_encoded_png..."
  },
  "3d_mesh": {
    "vertices": [[x, y, z], ...],
    "faces": [[v1, v2, v3], ...],
    "format": "obj"
  }
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 4: REQUIREMENTS COLLECTION & VALIDATION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input (User Form Data):**
```json
{
  "project_info": {
    "project_name": "ABC Industrial Park",
    "location": "Rayong, Thailand",
    "developer": "XYZ Development Co."
  },
  "site_info": {
    "total_area_rai": 101.53,  // From Step 2
    "zoning": "industrial_estate",
    "ieat_approved": true
  },
  "design_requirements": {
    "industry_type": "light_manufacturing",
    "target_number_of_lots": 55,
    "lot_size_range": {
      "min_sqm": 1000,
      "max_sqm": 1500,
      "preferred_sqm": 1200
    },
    "infrastructure": {
      "road_standard": "ieat_standard",
      "green_space_percent": 12,  // User wants 12% (above 10% minimum)
      "utility_corridors": true,
      "central_utility_zone": true
    },
    "financial": {
      "target_salable_area_percent": 75,
      "lot_price_per_sqm": 8500,  // THB
      "development_budget": 250000000  // THB
    }
  }
}
```

**Processing (Validation):**

The system performs comprehensive validation on user inputs:

**Lot Count Feasibility Check:**
The system calculates maximum achievable lot count by accounting for required infrastructure (roads ~25%, green space 12%, buffer zones 5%, utilities 2%). If the user requests 55 lots but only 52 are feasible, the system returns an error with the suggested maximum.

**Regulatory Compliance Validation:**
All inputs are checked against IEAT standards. For example, if green space is below 10%, the system immediately flags this as a critical error with reference to the specific regulation clause.

**Salable Area Realism Check:**
If the user targets salable area above 80%, the system issues a warning that this is aggressive based on typical industrial park layouts (65-75% range). This is a warning, not an error, so the user can proceed.

**Cross-Validation:**
The system checks for internal consistency - for example, if lot size preferences combined with lot count exceed available area, it suggests adjustments.

All validation results include:
- Field that failed validation
- Specific error message
- Regulation reference (if applicable)
- Suggested corrected value
- Severity level (error vs warning)

**Output:**
```json
{
  "status": "validated",
  "validation_result": {
    "valid": true,
    "errors": [],
    "warnings": [
      {
        "field": "target_salable_area_percent",
        "severity": "medium",
        "message": "Target 75% salable area is aggressive. Typical range: 65-75%",
        "user_can_proceed": true
      }
    ]
  },
  "processed_requirements": {
    "industry_type": "light_manufacturing",
    "lot_configuration": {
      "target_count": 55,
      "size_range_sqm": [1000, 1500],
      "preferred_size_sqm": 1200,
      "estimated_achievable_count": 52  // After accounting for constraints
    },
    "infrastructure_standards": {
      "main_roads": {
        "width_m": 25,
        "row_m": 25,
        "material": "asphalt_concrete"
      },
      "secondary_roads": {
        "width_m": 15,
        "row_m": 15,
        "material": "asphalt_concrete"
      },
      "green_space_required_sqm": 19494,  // 12% of 162,450 sqm
      "buffer_zone_required_m": 10
    },
    "regulatory_constraints": {
      "green_space_min_percent": 10,
      "green_space_target_percent": 12,
      "buffer_zone_m": 10,
      "fire_clearance_m": 6,
      "building_setback_m": 5,
      "max_building_height_m": 15
    }
  },
  "next_step": "resolve_constraints"
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 5: CONSTRAINT RESOLUTION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "site_geometry": { /* From Step 2 */ },
  "terrain_analysis": { /* From Step 3 */ },
  "requirements": { /* From Step 4 */ },
  "regulations": { /* IEAT rules */ }
}
```

**Processing:**

The constraint resolver analyzes all competing requirements to determine what's achievable:

**Constraint 1: Buffer Zone Impact**
The system applies a 10-meter inward buffer to the site boundary (IEAT requirement). This creates a smaller "usable polygon" inside the site boundary. The area lost to buffer zones is typically 8-12% of total site area, depending on site shape (irregular sites lose more).

**Constraint 2: Green Space Allocation**
The user's requested green space percentage (minimum 10% per IEAT) is calculated against the usable area. The system allocates green space using a strategy:
- 60% as perimeter greenbelt (10m wide strip inside buffer)
- 30% as central parks (2-3 strategic locations)
- 10% as street trees and medians

**Constraint 3: Road Network Estimation**
The system estimates required road area based on:
- Number of lots (more lots = more roads needed for access)
- Lot size (larger lots may share longer roads)
- Road standards (25m for main roads, 15m for secondary)
- Site shape (irregular sites need more roads)
Typical road consumption: 20-30% of usable area.

**Constraint 4: Utility Corridors**
Space for utility infrastructure (transformer stations, water towers, treatment plants) is reserved, typically 2-3% of site area.

**Constraint 5: Terrain Buildability**
Areas with slopes >15% are subtracted from available lot area. Challenging terrain (10-15% slope) is noted for potential use with additional grading costs.

**Net Calculation:**
After accounting for all constraints, the system calculates net available area for lots:
```
Available for lots = Usable area - Green space - Roads - Utilities - Unbuildable terrain
```

This determines maximum achievable lot count and realistic salable area percentage.

**Feasibility Assessment:**
The system compares user requirements against calculated maximums and assigns a confidence level (high/medium/low) based on how close the request is to physical limits.

**Output:**
```json
{
  "status": "resolved",
  "constraint_summary": {
    "total_site_area_sqm": 162450,
    "usable_after_buffer_sqm": 146205,  // Lost 10% to buffer
    "allocations": {
      "buffer_zone": {
        "area_sqm": 16245,
        "percent": 10.0,
        "type": "mandatory"
      },
      "green_space": {
        "area_sqm": 19494,
        "percent": 12.0,
        "type": "mandatory"
      },
      "roads_estimated": {
        "area_sqm": 36563,
        "percent": 22.5,
        "type": "estimated"
      },
      "utilities_corridors": {
        "area_sqm": 3249,
        "percent": 2.0,
        "type": "estimated"
      },
      "available_for_lots": {
        "area_sqm": 86899,
        "percent": 53.5,
        "type": "calculated"
      }
    },
    "lot_feasibility": {
      "requested_lots": 55,
      "estimated_achievable_lots": 52,
      "average_lot_size_sqm": 1671,  // 86899 / 52
      "within_size_range": true,
      "feasible": true,
      "confidence": "high"
    },
    "conflicts": [],
    "recommendations": [
      {
        "type": "optimization",
        "message": "Consider reducing target from 55 to 52 lots for better lot sizes",
        "impact": "Increases average lot size from 1580 to 1671 sqm"
      }
    ]
  },
  "next_step": "generate_design"
}
```

**Constraint Hierarchy:**
```
Priority 1 (Cannot be violated):
- IEAT regulations (green space, buffer, road widths)
- Fire safety clearances
- Terrain buildability limits

Priority 2 (Should meet if possible):
- Target lot count
- Preferred lot sizes
- Target salable area %

Priority 3 (Nice to have):
- Specific lot orientations
- Aesthetic preferences
- Phasing requirements
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 6: AI DESIGN GENERATION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "site_geometry": { /* Polygon */ },
  "terrain_data": { /* Grid, slopes */ },
  "constraints": { /* From Step 5 */ },
  "requirements": { /* User inputs */ }
}
```

**Processing (Multi-stage AI Pipeline):**

The AI design generator uses a large language model (LLM) in multiple stages to create the complete industrial park layout:

**Stage 6.1: Road Network Generation**
The system sends a detailed prompt to the LLM describing:
- Site dimensions and shape
- Target number of lots
- Required road widths (25m main, 15m secondary per IEAT)
- Terrain characteristics (slope patterns, drainage)
- Constraints (must provide access to all lots, minimize total road length)

The LLM responds with a road network design consisting of:
- Main road centerlines (major circulation)
- Secondary road centerlines (lot access)
- Road hierarchy and connectivity

The system parses this response into geometric data structures and calculates total road area by buffering centerlines by half the road width.

**Stage 6.2: Lot Subdivision**
The road network divides the site into "zones" (areas between roads). For each zone, the system sends another LLM prompt requesting subdivision into lots with:
- Target lot size and acceptable range
- Preference for rectangular shapes (aspect ratio 1:1.5 to 1:2)
- Requirement that all lots have road frontage
- Building setback requirements (5m from property lines)

The LLM generates lot polygons that fill each zone efficiently. The system validates each lot geometry and adjusts if needed.

**Stage 6.3: Green Space Allocation**
With lots and roads defined, the system prompts the LLM to allocate the required green space area:
- Distribution strategy: 60% perimeter, 30% central parks, 10% street trees
- Locations that provide visual amenity and environmental benefit
- Integration with drainage patterns (low areas become retention ponds)

The LLM returns polygons for green spaces at strategic locations.

**Stage 6.4: Utility Planning**
Based on lot count and industry type, the system prompts for utility infrastructure placement:
- Transformer stations (1 per 20-25 lots, centrally located)
- Water towers/pumping stations (elevated locations for pressure)
- Wastewater treatment plant (at natural low point for gravity flow)

The LLM considers:
- Elevation data (for gravity-based systems)
- Equal distribution (minimize longest utility run)
- Avoiding premium lots (place utilities on less valuable land)

**Stage 6.5: Design Assembly and Validation**
All components are combined into a complete design. The system performs geometric validation:
- No overlapping lots
- All lots accessible from roads
- Green space meets area requirement
- Utilities properly distributed

Any issues trigger iterative refinement with the LLM until a valid design is achieved.

**Output:**
```json
{
  "status": "generated",
  "design_id": "design_20260128_123456",
  "generation_time_seconds": 42.5,
  "components": {
    "road_network": {
      "main_roads": [
        {
          "id": "main_01",
          "type": "main",
          "geometry": {
            "type": "LineString",
            "coordinates": [[100.5234, 13.7456], [100.5256, 13.7456], ...]
          },
          "width_m": 25,
          "length_m": 450.5,
          "area_sqm": 11262.5
        },
        {
          "id": "main_02",
          "type": "main",
          "geometry": {...},
          "width_m": 25,
          "length_m": 380.2,
          "area_sqm": 9505
        }
      ],
      "secondary_roads": [
        {
          "id": "sec_01",
          "type": "secondary",
          "geometry": {...},
          "width_m": 15,
          "length_m": 220.5,
          "area_sqm": 3307.5
        }
        // ... more secondary roads
      ],
      "total_length_m": 2145.8,
      "total_area_sqm": 36892.5,
      "road_efficiency": 0.87  // Low ratio = good (minimal road length)
    },
    
    "lots": [
      {
        "id": "lot_001",
        "geometry": {
          "type": "Polygon",
          "coordinates": [[...]]
        },
        "area_sqm": 1245.6,
        "dimensions": {
          "width_m": 35.2,
          "depth_m": 35.4,
          "aspect_ratio": 1.006  // Nearly square
        },
        "road_frontage": {
          "road_id": "main_01",
          "frontage_length_m": 35.2,
          "access_type": "direct"
        },
        "buildable_area_sqm": 1120.5,  // After 5m setbacks
        "terrain": {
          "avg_elevation_m": 12.1,
          "avg_slope_percent": 2.3,
          "buildability": "excellent"
        },
        "utilities_access": {
          "water": true,
          "electricity": true,
          "wastewater": true,
          "distance_to_main_utility_m": 125.5
        }
      },
      {
        "id": "lot_002",
        "geometry": {...},
        "area_sqm": 1189.4,
        "dimensions": {...},
        // ... same structure for all 52 lots
      }
      // ... total 52 lots
    ],
    
    "green_spaces": [
      {
        "id": "green_01",
        "type": "perimeter_buffer",
        "geometry": {...},
        "area_sqm": 11696.7,
        "width_m": 10,
        "planting_type": "mixed_trees_and_shrubs"
      },
      {
        "id": "green_02",
        "type": "central_park",
        "geometry": {...},
        "area_sqm": 5848.2,
        "features": ["playground", "seating_areas", "water_feature"]
      },
      {
        "id": "green_03",
        "type": "street_landscaping",
        "geometry": {...},
        "area_sqm": 1949.5,
        "features": ["street_trees", "medians"]
      }
    ],
    
    "utilities": [
      {
        "id": "transformer_01",
        "type": "transformer_station",
        "geometry": {
          "type": "Point",
          "coordinates": [100.5245, 13.7445]
        },
        "capacity_kva": 1000,
        "serves_lots": ["lot_001", "lot_002", ..., "lot_025"],
        "area_sqm": 100
      },
      {
        "id": "transformer_02",
        "type": "transformer_station",
        "capacity_kva": 1000,
        "serves_lots": ["lot_026", ..., "lot_052"]
      },
      {
        "id": "wwtp_01",
        "type": "wastewater_treatment_plant",
        "geometry": {...},
        "capacity_cmd": 5200,  // cubic meters per day
        "technology": "activated_sludge",
        "area_sqm": 2500,
        "location_rationale": "Located at natural low point for gravity flow"
      },
      {
        "id": "water_tower_01",
        "type": "water_storage",
        "capacity_m3": 500,
        "elevation_m": 16.5,
        "area_sqm": 150
      }
    ]
  },
  
  "summary": {
    "total_lots": 52,
    "total_lot_area_sqm": 64729.8,
    "average_lot_size_sqm": 1244.8,
    "lot_size_range_sqm": [1089.5, 1398.2],
    "road_area_sqm": 36892.5,
    "green_area_sqm": 19494.4,
    "utility_area_sqm": 2750.0,
    "buffer_area_sqm": 16245.0,
    "unallocated_sqm": 22338.3,
    "salable_area_percent": 39.8,  // Calculated: lots / total site
    "actual_salable_percent": 53.5  // Calculated: lots / usable area (after buffer)
  },
  
  "next_step": "validate_compliance"
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 7: REGULATORY COMPLIANCE CHECK**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "design": { /* Complete design from Step 6 */ },
  "regulations": { /* IEAT standards */ }
}
```

**Processing:**

The compliance checker runs a comprehensive rule-based validation against IEAT regulations and Thai building codes:

**Check 1: Green Space Percentage**
Calculates total green space area as percentage of total site. IEAT requires minimum 10%. The system checks actual percentage and reports pass/fail with margin (e.g., "12% actual vs 10% required = +2% margin").

**Check 2: Road Width Standards**
Iterates through every road segment, measuring width and comparing against standards:
- Main roads: Must be ≥25m
- Secondary roads: Must be ≥15m
Any road failing this check is flagged as critical violation.

**Check 3: Fire Safety Clearances**
For each lot, the system measures:
- Distance to nearest fire access road (must be within 150m)
- Width of nearest access (must be ≥6m for fire trucks)
- Overall site coverage by fire protection
Violations are marked critical as they affect life safety.

**Check 4: Buffer Zone Implementation**
Verifies that a 10-meter buffer strip exists around the entire site perimeter. The system checks that no lots or structures encroach into this buffer.

**Check 5: Lot Size Standards**
Validates that all lots meet minimum practical size (typically 800 sqm for industrial use). Lots below this threshold get warnings rather than hard failures.

**Check 6: Utility Access**
Ensures every lot has access to required utilities (water, electricity, wastewater). Measures distance from each lot to nearest utility connection point.

**Compliance Scoring:**
The system calculates:
- Total checks performed
- Number passed, failed, warnings
- Overall compliance rate percentage
- Certification status ("IEAT Compliant" if all critical checks pass)

**Severity Classification:**
- **Critical:** Regulatory violation, cannot proceed (red flag)
- **High:** Important issue, strongly recommend fixing (orange flag)
- **Medium:** Best practice violation, should address (yellow flag)
- **Low:** Minor optimization opportunity (info only)

**Output:**
```json
{
  "status": "compliant",
  "compliance_report": {
    "compliant": true,
    "checks": [
      {
        "category": "Environmental",
        "rule": "IEAT Green Space Minimum",
        "regulation_ref": "IEAT Standard 3.2",
        "requirement": "≥10% of total site area",
        "actual": "12.0%",
        "value": 12.0,
        "threshold": 10.0,
        "status": "pass",
        "margin": "+2.0%"
      },
      {
        "category": "Infrastructure",
        "rule": "Main Road Width",
        "regulation_ref": "IEAT Standard 4.1",
        "requirement": "≥25m for main roads",
        "actual": "25m",
        "status": "pass"
      },
      {
        "category": "Infrastructure",
        "rule": "Secondary Road Width",
        "regulation_ref": "IEAT Standard 4.1",
        "requirement": "≥15m for secondary roads",
        "actual": "15m",
        "status": "pass"
      },
      {
        "category": "Fire Safety",
        "rule": "Fire Access Distance",
        "regulation_ref": "Thai Building Code Section 38",
        "requirement": "All buildings within 150m of fire access road",
        "actual": "Max distance: 89m",
        "status": "pass"
      },
      {
        "category": "Fire Safety",
        "rule": "Fire Clearance",
        "regulation_ref": "Thai Building Code Section 38",
        "requirement": "Minimum 6m clearance for fire access",
        "actual": "All lots compliant",
        "status": "pass",
        "checked_lots": 52
      },
      {
        "category": "Site Layout",
        "rule": "Perimeter Buffer",
        "regulation_ref": "IEAT Standard 3.1",
        "requirement": "10m buffer strip around perimeter",
        "actual": "10m buffer implemented",
        "status": "pass"
      },
      {
        "category": "Lot Standards",
        "rule": "Minimum Lot Size",
        "regulation_ref": "Best Practice",
        "requirement": "≥800 sqm for industrial lots",
        "actual": "Min: 1089.5 sqm",
        "status": "pass"
      }
    ],
    "summary": {
      "total_checks": 7,
      "passed": 7,
      "failed": 0,
      "warnings": 0,
      "compliance_rate": 100.0,
      "certification": "IEAT_COMPLIANT"
    },
    "certifications": [
      {
        "authority": "IEAT",
        "status": "compliant",
        "confidence": "high"
      },
      {
        "authority": "Thai Building Code",
        "status": "compliant",
        "confidence": "high"
      }
    ]
  },
  "next_step": "calculate_financials"
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 8: FINANCIAL CALCULATION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "design": { /* Complete design */ },
  "pricing": {
    "lot_price_per_sqm": 8500,  // THB
    "development_costs": {
      "land_acquisition_per_rai": 2000000,
      "site_prep_per_sqm": 150,
      "road_construction_per_sqm": 800,
      "utility_installation_per_lot": 250000,
      "green_space_per_sqm": 200
    }
  }
}
```

**Processing:**

The financial calculator computes comprehensive project economics:

**Revenue Calculation:**
Total revenue is calculated by multiplying total salable lot area (sum of all lot areas) by the price per square meter provided by the user. For example: 64,730 sqm × 8,500 THB/sqm = 550.2 million THB.

**Cost Components:**

The system calculates costs in several categories:

1. **Land Acquisition:** Site area in rai × cost per rai. This is typically the largest cost component (60-75% of total project cost).

2. **Site Preparation:** Total site area × preparation cost per sqm. Includes clearing, basic grading, demolition of existing structures.

3. **Road Construction:** Total road area × construction cost per sqm. Accounts for excavation, base layers, asphalt, drainage.

4. **Utility Installation:** Number of lots × installation cost per lot. Covers water lines, electrical connections, sewage systems to each lot.

5. **Green Space Development:** Green space area × landscaping cost per sqm. Includes tree planting, irrigation, pathways, amenities.

6. **Soft Costs:** Calculated as 10% of construction costs. Covers engineering, permits, legal, marketing, financing costs.

**Profitability Metrics:**

From revenue and costs, the system calculates:

- **Gross Profit:** Total revenue minus total development cost
- **Profit Margin:** Gross profit as percentage of revenue (typical industrial parks: 40-55%)
- **ROI (Return on Investment):** Gross profit as percentage of total investment (typical: 80-120%)
- **Breakeven Point:** Percentage of lots that must be sold to recover costs
- **Profit per Lot:** Average profit contribution from each lot sold

**Development Timeline:**

The system estimates development phases:
- Phase 1 (6 months): Site preparation and initial infrastructure
- Phase 2 (8 months): Road construction and utility installation
- Phase 3 (4 months): Landscaping and finishing

Total: 18 months typical for industrial park development.

**Sales Projections:**

Three scenarios are modeled:
- **Pessimistic:** 2 lots/month → 26 months to sell out
- **Realistic:** 3 lots/month → 17 months to sell out
- **Optimistic:** 4 lots/month → 13 months to sell out

**Sensitivity Analysis:**

The system tests impact of price changes:
- -10% price: Shows reduced profit and ROI
- Base case: Planned pricing
- +10% price: Shows increased profit and ROI

This helps understand risk exposure to market price fluctuations.

**Output:**
```json
{
  "status": "calculated",
  "financial_summary": {
    "revenue": {
      "total_salable_area_sqm": 64729.8,
      "price_per_sqm_thb": 8500,
      "total_revenue_thb": 550203300,
      "revenue_per_rai_thb": 5418680
    },
    "costs": {
      "land_acquisition_thb": 203060000,
      "site_preparation_thb": 24367500,
      "road_construction_thb": 29514000,
      "utility_installation_thb": 13000000,
      "green_space_development_thb": 3898880,
      "soft_costs_thb": 7078038,
      "total_development_cost_thb": 280918418
    },
    "cost_breakdown_percent": {
      "land_acquisition": 72.3,
      "construction": 23.5,
      "soft_costs": 2.5,
      "green_space": 1.4,
      "utilities": 0.3
    },
    "profitability": {
      "gross_profit_thb": 269284882,
      "profit_margin_percent": 48.9,
      "roi_percent": 95.9,
      "cost_per_lot_thb": 5402662,
      "revenue_per_lot_thb": 10580833,
      "profit_per_lot_thb": 5178171
    },
    "risk_metrics": {
      "breakeven_occupancy_percent": 51.1,
      "breakeven_lots_sold": 27,
      "margin_of_safety_percent": 48.9
    },
    "development_timeline": {
      "estimated_months": 18,
      "phases": [
        {
          "phase": 1,
          "duration_months": 6,
          "activities": ["Site preparation", "Infrastructure Phase 1"],
          "cost_thb": 93639473
        },
        {
          "phase": 2,
          "duration_months": 8,
          "activities": ["Road construction", "Utilities installation"],
          "cost_thb": 140459209
        },
        {
          "phase": 3,
          "duration_months": 4,
          "activities": ["Green space", "Final touches"],
          "cost_thb": 46819736
        }
      ],
      "monthly_cost_average_thb": 15606579
    },
    "sales_projections": {
      "pessimistic": {
        "lots_per_month": 2,
        "sellout_months": 26,
        "total_revenue_thb": 550203300
      },
      "realistic": {
        "lots_per_month": 3,
        "sellout_months": 17,
        "total_revenue_thb": 550203300
      },
      "optimistic": {
        "lots_per_month": 4,
        "sellout_months": 13,
        "total_revenue_thb": 550203300
      }
    },
    "sensitivity_analysis": {
      "price_impact": {
        "minus_10_percent": {
          "revenue_thb": 495182970,
          "profit_thb": 214264552,
          "roi_percent": 76.3
        },
        "base": {
          "revenue_thb": 550203300,
          "profit_thb": 269284882,
          "roi_percent": 95.9
        },
        "plus_10_percent": {
          "revenue_thb": 605223630,
          "profit_thb": 324305212,
          "roi_percent": 115.5
        }
      }
    }
  },
  "next_step": "generate_output"
}
```

---

### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### **STEP 9: OUTPUT GENERATION**
### ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Input:**
```json
{
  "design": { /* Complete design */ },
  "compliance": { /* Compliance report */ },
  "financials": { /* Financial calculations */ }
}
```

**Processing:**

The output generator creates multiple deliverables in different formats:

**Output 1: DXF/DWG File**

The system creates a new AutoCAD-compatible file with organized layer structure:

**Layer Organization:**
- BOUNDARY: Site perimeter (gray)
- LOTS: Individual lot polygons (green)
- ROADS_MAIN: Main road polygons (red)
- ROADS_SECONDARY: Secondary roads (yellow)
- GREEN_SPACE: Parks and landscaping (dark green)
- UTILITIES: Transformer stations, water towers (magenta)
- LABELS: Text annotations with IDs and areas (gray)

**Drawing Process:**
For each component, the system converts coordinates into CAD entities:
- Lots and green spaces → Closed polylines (polygons)
- Roads → Polylines with width attribute
- Utilities → Circles or blocks with text labels
- Lot IDs → Text entities at centroid of each lot

**File Specifications:**
- Format: AutoCAD R2018 (compatible with most CAD software)
- Coordinate system: Preserved from original DXF input
- Units: Meters
- File size: Typically 2-5 MB depending on complexity

**Output 2: PDF Report**

A comprehensive document is generated with multiple sections:

1. **Cover Page:** Project name, location, date, designer
2. **Executive Summary:** Key metrics in 1-page format
3. **Site Analysis:** Maps showing terrain, constraints, opportunities
4. **Design Overview:** Master plan rendering with legend
5. **Lot Details:** Table listing all lots with areas, dimensions, pricing
6. **Infrastructure Plan:** Road network diagram with dimensions
7. **Compliance Report:** Checklist of regulations with pass/fail status
8. **Financial Analysis:** Charts and tables showing costs, revenue, ROI
9. **Development Timeline:** Gantt chart with phases and milestones
10. **Recommendations:** Actionable suggestions for optimization
11. **Appendices:** Technical specifications, calculation methodology

The PDF includes high-quality maps, charts, and professional formatting suitable for client presentations or permit applications.

**Output 3: Web Preview Data**

For interactive viewing in the web application, the system generates:

**GeoJSON Format:**
All geometries are converted to GeoJSON standard:
- Each lot, road, green space, utility becomes a "Feature"
- Features include geometry (coordinates) and properties (ID, area, type)
- Organized into a "FeatureCollection" for efficient loading

**Map Configuration:**
- Calculate optimal center point (centroid of site)
- Calculate bounding box (min/max coordinates)
- Determine zoom level for site to fill 80% of viewport
- Generate preview image (PNG thumbnail)

**Styling Information:**
Color codes and styles for rendering each feature type on the web map.

**Output 4: Data Export Files**

Additional structured data formats:

**JSON Export:** Complete design data in machine-readable format for API consumers or future imports.

**CSV Export:** Spreadsheet-compatible lot listing with columns: Lot ID, Area, Dimensions, Road Frontage, Price, Total Value.

**Excel Financial Model:** Detailed financial breakdown with formulas for "what-if" analysis by client.

All outputs are stored in the database with download URLs generated and returned to the user.

**Final Output:**

```json
{
  "status": "completed",
  "design_id": "design_20260128_123456",
  "processing_time_seconds": 87.3,
  "outputs": {
    "dxf_file": {
      "path": "/outputs/design_20260128_123456.dxf",
      "download_url": "https://api.example.com/downloads/design_20260128_123456.dxf",
      "format": "AutoCAD R2018 DXF",
      "size_mb": 2.8,
      "layers": [
        "BOUNDARY",
        "LOTS",
        "ROADS_MAIN",
        "ROADS_SECONDARY",
        "GREEN_SPACE",
        "UTILITIES",
        "LABELS"
      ],
      "entities_count": {
        "polylines": 67,
        "circles": 5,
        "text": 58
      }
    },
    
    "pdf_report": {
      "path": "/outputs/design_20260128_123456_report.pdf",
      "download_url": "https://api.example.com/downloads/design_20260128_123456_report.pdf",
      "size_mb": 4.5,
      "pages": 12,
      "sections": [
        "Cover Page",
        "Executive Summary",
        "Site Analysis",
        "Design Overview",
        "Lot Details",
        "Infrastructure Plan",
        "Compliance Report",
        "Financial Analysis",
        "Development Timeline",
        "Recommendations",
        "Appendices"
      ]
    },
    
    "web_preview": {
      "viewer_url": "https://app.example.com/viewer/design_20260128_123456",
      "map_center": [100.5345, 13.7345],
      "map_bounds": [[100.5234, 13.7234], [100.5456, 13.7456]],
      "zoom_level": 16,
      "geojson_url": "https://api.example.com/geojson/design_20260128_123456.json",
      "preview_image_url": "https://api.example.com/preview/design_20260128_123456.png"
    },
    
    "data_export": {
      "json_url": "https://api.example.com/exports/design_20260128_123456.json",
      "csv_lots_url": "https://api.example.com/exports/design_20260128_123456_lots.csv",
      "excel_financial_url": "https://api.example.com/exports/design_20260128_123456_financial.xlsx"
    }
  },
  
  "executive_summary": {
    "site": {
      "total_area_rai": 101.53,
      "location": "Rayong, Thailand",
      "terrain": "Mostly flat with gentle slopes"
    },
    "design": {
      "total_lots": 52,
      "average_lot_size_sqm": 1245,
      "salable_area_percent": 53.5,
      "road_length_m": 2146,
      "green_space_percent": 12.0
    },
    "compliance": {
      "ieat_compliant": true,
      "building_code_compliant": true,
      "compliance_rate_percent": 100.0
    },
    "financials": {
      "total_revenue_thb": 550203300,
      "total_cost_thb": 280918418,
      "gross_profit_thb": 269284882,
      "roi_percent": 95.9,
      "profit_margin_percent": 48.9,
      "payback_period_years": 1.9
    },
    "timeline": {
      "development_months": 18,
      "estimated_sellout_months": 17
    }
  },
  
  "recommendations": [
    {
      "category": "Design Optimization",
      "priority": "medium",
      "message": "Consider adjusting Lot 15 and Lot 16 boundaries to create more regular shapes for better usability."
    },
    {
      "category": "Financial",
      "priority": "low",
      "message": "Current design achieves 95.9% ROI. Small efficiency improvements in road layout could increase to 97%."
    },
    {
      "category": "Market Positioning",
      "priority": "high",
      "message": "Average lot size of 1,245 sqm is well-suited for light manufacturing. Consider marketing to electronics and automotive parts manufacturers."
    }
  ],
  
  "next_actions": [
    "Review design with client",
    "Obtain client approval",
    "Submit to IEAT for official review",
    "Begin detailed engineering design"
  ]
}
```

---

## 🔄 ERROR HANDLING & EDGE CASES

### Common Failure Points:

**1. CAD File Parsing Failure (DXF/DWG)**
```json
{
  "status": "error",
  "step": "parse_cad",
  "error_code": "BOUNDARY_NOT_FOUND",
  "message": "No valid boundary polygon detected in DXF or DWG file",
  "user_message": "Could not find site boundary. Please ensure boundary is on a layer named 'BOUNDARY' or 'PERIMETER' in your DXF or DWG file.",
  "recovery_options": [
    "Manual boundary selection",
    "Upload different file (DXF or DWG)",
    "Contact support"
  ]
}
```

**2. Infeasible Requirements**
```json
{
  "status": "error",
  "step": "constraint_resolution",
  "error_code": "REQUIREMENTS_INFEASIBLE",
  "message": "Requested 80 lots but maximum achievable is 52 given constraints",
  "conflicts": [
    {
      "constraint": "target_lot_count",
      "requested": 80,
      "maximum_possible": 52,
      "limiting_factors": ["terrain", "road_requirements", "green_space"]
    }
  ],
  "suggestions": [
    "Reduce target to 52 lots",
    "Reduce average lot size to 900 sqm (achieves 67 lots)",
    "Request site expansion or adjacent parcel"
  ]
}
```

**3. Compliance Violation**
```json
{
  "status": "error",
  "step": "compliance_check",
  "error_code": "REGULATION_VIOLATION",
  "violations": [
    {
      "rule": "Green Space Minimum",
      "required": "10%",
      "actual": "8.5%",
      "severity": "critical",
      "regulation": "IEAT Standard 3.2"
    }
  ],
  "message": "Design violates IEAT regulations and cannot proceed",
  "auto_fix_available": true,
  "auto_fix_impact": "Reduce lot count from 55 to 52 to accommodate additional green space"
}
```

---

## 📦 DATA PERSISTENCE

**Database Architecture (PostgreSQL with PostGIS Extension):**

The system uses a relational database with spatial capabilities to store all project data:

**Projects Table:**
Stores high-level project information:
- Unique project ID (UUID)
- User/owner ID (links to user account)
- Project name and location
- Creation and last update timestamps
- Current status (draft, in-progress, completed, archived)

**Site Geometries Table:**
Stores spatial data for each project:
- Site boundary as PostGIS geometry (polygon with coordinate reference system)
- Calculated area in square meters and rai
- Path to original uploaded DXF file
- Links to parent project

**Design Versions Table:**
Supports multiple design iterations per project:
- Version number (1, 2, 3, etc.)
- Complete design data stored as JSON (lots, roads, green spaces, utilities)
- Compliance report data as JSON
- Financial calculations as JSON
- Creation timestamp
- Links to parent project

This allows users to generate multiple designs for the same site and compare them.

**Lots Table:**
Detailed information for each lot in a design:
- Lot number/identifier
- Lot geometry as PostGIS polygon
- Calculated area
- Road frontage length
- Assigned price per square meter
- Links to parent design version

Having lots in a separate table enables efficient querying and analysis (e.g., "find all lots over 1,500 sqm").

**Spatial Indexing:**
The database uses spatial indexes on geometry columns for fast queries like:
- "Find lots within 100m of this point"
- "Calculate distance from lot to utility"
- "Check if polygons overlap"

**Backup and Versioning:**
All design versions are preserved, allowing users to:
- Revert to previous designs
- Compare different iterations
- Track design evolution over time

---

**Document Version:** 1.0  
**Date:** January 28, 2026  
**Prepared by:** Technical Team
