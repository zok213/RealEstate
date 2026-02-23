# DXF Terrain Overlay - Usage Guide

## Overview

This feature enables **context-aware industrial park design** by:
1. Displaying uploaded DXF files on real Mapbox satellite/terrain imagery
2. Detecting existing site features (ponds, buildings, roads, vegetation)
3. Classifying features as reusable vs. obstacles
4. Integrating into design optimizer to preserve valuable features

## Workflow

### 1. Upload DXF File

**Frontend (React)**:
```typescript
// In your page or component
import DXFMapboxViewer from '@/components/dxf-mapbox-viewer';

function DesignPage() {
  return (
    <div className="flex">
      <DXFMapboxViewer />
    </div>
  );
}
```

**API Call**:
```typescript
const formData = new FormData();
formData.append('file', dxfFile);

const response = await fetch('/api/dxf/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
// data.file_id: "abc-123-def"
// data.needs_manual_georeferencing: false (or true if requires control points)
```

### 2. Manual Georeferencing (if needed)

If `needs_manual_georeferencing = true`, provide ≥3 control points:

```typescript
// User clicks 3 points on DXF preview, then 3 corresponding points on map
const dxfPoints = [[100, 200], [500, 200], [300, 600]]; // DXF coordinates
const geoPoints = [[100.5, 13.75], [100.52, 13.75], [100.51, 13.77]]; // Lat/lng

await fetch('/api/dxf/georeference', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: 'abc-123-def',
    dxf_points: dxfPoints,
    geo_points: geoPoints
  })
});

// Response includes RMSE (root mean square error) for accuracy validation
```

### 3. View Features on Mapbox

**Load GeoJSON**:
```typescript
const response = await fetch('/api/dxf/abc-123-def/geojson');
const data = await response.json();

// data.geojson: GeoJSON FeatureCollection with all DXF entities
// data.bounds: { west, south, east, north }
// data.center: { lng, lat }

// Add to Mapbox
map.addSource('dxf-layer', {
  type: 'geojson',
  data: data.geojson
});

// Fit map to bounds
map.fitBounds([
  [data.bounds.west, data.bounds.south],
  [data.bounds.east, data.bounds.north]
], { padding: 50 });
```

**Feature Detection**:
```typescript
const response = await fetch('/api/dxf/abc-123-def/features');
const features = await response.json();

console.log(features.water_bodies); // Array of detected ponds
console.log(features.buildings);    // Array of buildings
console.log(features.roads);        // Array of road segments
console.log(features.vegetation);   // Array of trees/vegetation
console.log(features.summary);      // Statistics (site area, coverage, etc.)

// Example output:
{
  water_bodies: [
    {
      id: "water_001",
      polygon: { type: "Polygon", coordinates: [...] },
      area_m2: 8000,
      perimeter_m: 350,
      centroid: [100.51, 13.76]
    }
  ],
  summary: {
    site_area_m2: 800000,
    site_area_rai: 500,
    water_area_pct: 5.2,
    building_coverage_pct: 12.5
  }
}
```

### 4. Classify Reusability

**Auto-classification**:
```typescript
const response = await fetch(
  '/api/dxf/abc-123-def/classify-reusability',
  { method: 'POST' }
);

const reusability = await response.json();

console.log(reusability.keep_as_is);     // ["water_001", "tree_005", ...]
console.log(reusability.reuse_modified); // ["building_002", "road_010", ...]
console.log(reusability.demolish);       // ["building_003", "building_004", ...]
console.log(reusability.constraints);    // Array of design constraints
```

**Reusability Logic**:
- **Keep As-Is**:
  - Water bodies >5000m² (expensive to fill, ~500K THB)
  - Significant trees (environmental protection)
  - Adds 20m buffer exclusion zones

- **Reuse/Modified**:
  - Large buildings >2000m² (can renovate)
  - Small ponds <5000m² (can expand as retention ponds)
  - Roads >100m (can upgrade/widen)

- **Demolish**:
  - Small buildings <2000m²
  - Poor condition structures
  - Minor obstacles

### 5. User Override (Optional)

**Reusable Features Manager**:
```tsx
import ReusableFeaturesManager from '@/components/reusable-features-manager';

<ReusableFeaturesManager
  fileId="abc-123-def"
  features={features}
  reusability={reusability}
  onUpdate={(overrides) => {
    console.log('User changed classifications:', overrides);
    // overrides: { "water_001": "keep", "building_002": "demolish", ... }
  }}
  onFeatureHover={(featureId) => {
    // Highlight feature on map when hovering in UI
    if (featureId) {
      map.setFeatureState(
        { source: 'features', id: featureId },
        { hover: true }
      );
    }
  }}
/>
```

**API Override**:
```typescript
await fetch('/api/dxf/reusability-override', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_id: 'abc-123-def',
    overrides: {
      "water_001": "keep",      // Changed from reuse to keep
      "building_002": "demolish" // Changed from reuse to demolish
    }
  })
});
```

### 6. Integrate with Design Optimizer

**Backend Integration**:
```python
from backend.optimization.existing_features_integrator import (
    ExistingFeaturesIntegrator,
    apply_existing_features_constraints
)

# Load features and reusability
features = load_features_from_cache(file_id)
reusability = load_reusability_classifications(file_id)

# Apply constraints to design parameters
design_params = {
    'totalArea_ha': 50,
    'industryFocus': [{'type': 'automotive', 'count': 20}],
    'salableArea_percent': 60,
    # ... other params
}

updated_params = apply_existing_features_constraints(
    design_params,
    features,
    reusability
)

# Now design optimizer respects existing features
from backend.design.enhanced_layout_generator import EnhancedLayoutGenerator

generator = EnhancedLayoutGenerator()
layout = generator.generate_comprehensive_layout(
    updated_params,
    site_boundary
)

# Layout will:
# - Avoid exclusion zones (kept ponds, protected trees)
# - Reuse existing road alignments
# - Expand existing ponds instead of creating new
# - Adapt existing buildings for admin/offices
```

**Constraints Structure**:
```python
updated_params['existing_features'] = {
    'lot_constraints': {
        'exclusion_polygons': <MultiPolygon>,  # Areas to avoid
        'preferred_polygons': [<Polygon>, ...], # Areas to prioritize
        'alignment_guides': [                   # Road alignments
            {
                'start': [x, y],
                'end': [x, y],
                'bearing': 45.0,
                'waypoints': [[x, y], ...]
            }
        ],
        'total_excluded_area_m2': 15000
    },
    'infrastructure_constraints': {
        'existing_ponds': [
            {
                'geometry': <Polygon>,
                'area_m2': 8000,
                'can_expand': True,  # Small pond, can expand
                'expansion_capacity_m3': 16000  # 2m depth
            }
        ],
        'existing_roads': [
            {
                'geometry': <LineString>,
                'length_m': 500,
                'width_m': 12,
                'can_widen': True
            }
        ],
        'protected_trees': [...],
        'exclusion_zones': [...]
    },
    'cost_savings': {
        'ponds_preserved': 800000,      # THB
        'roads_reused': 4800000,        # THB
        'buildings_adapted': 12000000,  # THB
        'total_savings': 17600000       # THB (~$500K USD)
    },
    'report': "# Existing Features Integration Report\n..."
}
```

### 7. View Design Output

**Frontend Display**:
```tsx
// Design output includes preserved features
{
  lots: [...],
  roads: [...],
  green_spaces: [...],
  existing_features: {
    preserved_ponds: [
      {
        id: "water_001",
        geometry: {...},
        status: "kept_as_is",
        savings_thb: 800000
      }
    ],
    reused_roads: [...],
    adapted_buildings: [...]
  },
  cost_analysis: {
    construction_cost: 250000000,
    cost_savings_from_reuse: 17600000,
    net_construction_cost: 232400000
  }
}
```

## Full Example

### Page Component

```tsx
'use client';

import { useState } from 'react';
import DXFMapboxViewer from '@/components/dxf-mapbox-viewer';
import ReusableFeaturesManager from '@/components/reusable-features-manager';
import { Button } from '@/components/ui/button';

export default function ContextAwareDesignPage() {
  const [fileId, setFileId] = useState<string | null>(null);
  const [features, setFeatures] = useState(null);
  const [reusability, setReusability] = useState(null);
  const [designParams, setDesignParams] = useState({});

  const handleFileUploaded = async (fid: string) => {
    setFileId(fid);
    
    // Load features
    const featuresRes = await fetch(`/api/dxf/${fid}/features`);
    const featuresData = await featuresRes.json();
    setFeatures(featuresData);
    
    // Classify reusability
    const reusabilityRes = await fetch(
      `/api/dxf/${fid}/classify-reusability`,
      { method: 'POST' }
    );
    const reusabilityData = await reusabilityRes.json();
    setReusability(reusabilityData);
  };

  const handleGenerateDesign = async () => {
    const response = await fetch('/api/designs/generate-with-constraints', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_id: fileId,
        design_params: designParams
      })
    });

    const layout = await response.json();
    console.log('Generated layout:', layout);
  };

  return (
    <div className="flex h-screen">
      <div className="w-96 overflow-y-auto">
        {fileId && features && reusability && (
          <>
            <ReusableFeaturesManager
              fileId={fileId}
              features={features}
              reusability={reusability}
              onUpdate={(overrides) => console.log('Updated:', overrides)}
            />
            <div className="p-4">
              <Button onClick={handleGenerateDesign} className="w-full">
                Generate Context-Aware Design
              </Button>
            </div>
          </>
        )}
      </div>
      
      <DXFMapboxViewer onFileUploaded={handleFileUploaded} />
    </div>
  );
}
```

### Backend API Endpoint

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.optimization.existing_features_integrator import (
    apply_existing_features_constraints
)

router = APIRouter(prefix="/api/designs")

class DesignWithConstraintsRequest(BaseModel):
    file_id: str
    design_params: dict

@router.post("/generate-with-constraints")
async def generate_with_constraints(request: DesignWithConstraintsRequest):
    """Generate design respecting existing site features."""
    
    # Load features from cache
    features = feature_cache.get(request.file_id)
    if not features:
        raise HTTPException(404, "Features not found")
    
    # Load reusability (from database or cache)
    reusability = load_reusability(request.file_id)
    
    # Apply constraints
    updated_params = apply_existing_features_constraints(
        request.design_params,
        features,
        reusability
    )
    
    # Generate layout
    from backend.design.enhanced_layout_generator import EnhancedLayoutGenerator
    
    generator = EnhancedLayoutGenerator()
    layout = generator.generate_comprehensive_layout(
        updated_params,
        site_boundary
    )
    
    # Add cost savings report
    layout['cost_savings_report'] = updated_params['existing_features']['report']
    layout['total_savings_thb'] = updated_params['existing_features']['cost_savings']['total_savings']
    
    return layout
```

## Cost Savings Example

**Typical 50 rai (80,000 m²) industrial park**:

- **3 large ponds preserved** (15,000 m² total):
  - Filling cost avoided: 15,000 × 100 = **฿1,500,000** (~$42K)
  
- **500m existing road reused**:
  - Reconstruction avoided: 500 × 12 × 800 = **฿4,800,000** (~$135K)
  
- **2 large buildings adapted** (4,000 m² total):
  - Demolish+rebuild: 4,000 × (1,500 + 5,000) = ฿26,000,000
  - Renovation: 4,000 × 3,000 = ฿12,000,000
  - Savings: **฿14,000,000** (~$390K)

**Total savings: ฿20,300,000 (~$570K USD)**

Plus environmental benefits:
- Preserved water resources
- Protected mature vegetation
- Reduced construction waste

## Benefits

1. **Cost Reduction**: Reuse existing infrastructure saves 10-20% of construction costs
2. **Faster Approval**: Preserving water bodies and trees helps environmental clearance
3. **Better Client Satisfaction**: Respects site history and context
4. **Competitive Advantage**: "Context-aware design" vs. competitors' clean-slate approach
5. **Sustainability**: Reduces waste and environmental impact

## Configuration

### Mapbox Token

Set in `.env.local`:
```
NEXT_PUBLIC_MAPBOX_TOKEN=pk.your_mapbox_token_here
```

### Thresholds (customizable in code)

```python
# backend/cad/existing_features_detector.py

WATER_KEEP_THRESHOLD = 5000  # m² - ponds above this: keep as-is
BUILDING_REUSE_THRESHOLD = 2000  # m² - buildings above this: reuse
ROAD_REUSE_THRESHOLD = 100  # m - roads longer than this: reuse
SIGNIFICANT_TREE_RADIUS = 5  # m - trees with radius above this: protect

WATER_BUFFER = 20  # m - exclusion zone buffer
VEGETATION_BUFFER = 15  # m - protection zone buffer
```

## Troubleshooting

### Georeferencing fails
- Check DXF has coordinate system info in header
- Use manual georeferencing with ≥3 control points
- Ensure control points well-distributed (not colinear)

### Features not detected
- Check layer names match patterns (WATER, POND, HO, NUOC, ทางน้ำ, etc.)
- Verify entities are closed polylines (for water/buildings)
- Use DXF viewer to inspect layer structure

### Map not displaying
- Check Mapbox token is valid
- Verify GeoJSON bounds are reasonable (not too large/small)
- Check browser console for errors

### Constraints not applied
- Verify `apply_existing_features_constraints` is called before design generation
- Check `updated_params['existing_features']` exists
- Enable debug logging to see constraint processing

## API Reference

### POST /api/dxf/upload
Upload DXF file, attempt auto-georeferencing

### POST /api/dxf/georeference
Set manual control points (≥3 required)

### GET /api/dxf/{file_id}/features
Get detected features (cached)

### POST /api/dxf/{file_id}/classify-reusability
Auto-classify feature reusability

### GET /api/dxf/{file_id}/geojson
Get georeferenced GeoJSON for Mapbox

### POST /api/dxf/reusability-override
User manual override of classifications
