"""
FastAPI endpoint for optimized plot subdivision using advanced algorithms.
Tích hợp thuật toán tối ưu hóa subdivision đã phát triển vào API.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import tempfile
import os
import sys
import json

# Add backend path to sys.path for imports
backend_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Import DXF analyzer
sys.path.insert(0, backend_path)
from ai.dxf_analyzer import DXFAnalyzer

# Import optimized algorithms
docker_core_path = os.path.join(backend_path, 'docker', 'core')
docker_optimization_path = os.path.join(docker_core_path, 'optimization')

if docker_core_path not in sys.path:
    sys.path.insert(0, docker_core_path)
if docker_optimization_path not in sys.path:
    sys.path.insert(0, docker_optimization_path)

try:
    from optimization.optimized_pipeline_integrator import (
        optimize_subdivision_pipeline
    )
    OPTIMIZED_ALGORITHMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import optimized algorithms: {e}")
    OPTIMIZED_ALGORITHMS_AVAILABLE = False


router = APIRouter()


class SubdivisionRequest(BaseModel):
    """Request for plot subdivision optimization."""
    min_plot_size: float = 1000  # m²
    max_plot_size: float = 5000  # m²
    target_plot_size: float = 2500  # m²
    min_frontage: float = 30  # meters
    max_frontage: float = 100  # meters
    target_frontage_depth_ratio: float = 0.4  # frontage/depth
    use_advanced_optimizer: bool = True
    use_layout_patterns: bool = True
    use_cp_sat_solver: bool = True
    use_road_optimizer: bool = True


@router.post("/api/optimize-subdivision")
async def optimize_subdivision(
    file: UploadFile = File(...),
    min_plot_size: float = 1000,
    max_plot_size: float = 5000,
    target_plot_size: float = 2500,
    min_frontage: float = 30,
    max_frontage: float = 100,
    target_frontage_depth_ratio: float = 0.4,
    use_advanced_optimizer: bool = True,
    use_layout_patterns: bool = True,
    use_cp_sat_solver: bool = True,
    use_road_optimizer: bool = True
):
    """
    Upload DXF file and run optimized plot subdivision algorithms.
    
    Returns:
        - Optimized plot layouts
        - Quality metrics (rectangularity, aspect ratio, compactness)
        - Statistics (total plots, rejection rate, avg quality score)
        - GeoJSON for visualization on 2D/3D map
    """
    if not OPTIMIZED_ALGORITHMS_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Optimized algorithms not available. Check backend/docker/core/optimization path."
        )
    
    # Validate file type
    if not (file.filename.lower().endswith('.dxf') or file.filename.lower().endswith('.dwg')):
        raise HTTPException(
            status_code=400,
            detail="Only DXF/DWG files are supported. Please upload a .dxf or .dwg file."
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Step 1: Analyze DXF to get site boundary
        analyzer = DXFAnalyzer(tmp_path)
        analysis = analyzer.analyze()
        
        if not analysis.get("success"):
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=400,
                detail=analysis.get("error", "Failed to analyze DXF file")
            )
        
        # Extract boundary polygon
        boundary_points = analysis.get("boundary_points", [])
        if not boundary_points or len(boundary_points) < 3:
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=400,
                detail="No valid boundary polygon found in DXF file"
            )
        
        # Convert to shapely-compatible format: [(lon, lat), ...]
        from shapely.geometry import Polygon
        polygon_coords = [(pt["lon"], pt["lat"]) for pt in boundary_points]
        site_polygon = Polygon(polygon_coords)
        
        # Step 2: Run optimized subdivision pipeline
        result = optimize_subdivision_pipeline(
            site_polygon=site_polygon,
            min_lot_size=min_plot_size,
            max_lot_size=max_plot_size,
            target_lot_size=target_plot_size,
            min_frontage=min_frontage,
            max_frontage=max_frontage,
            target_frontage_ratio=target_frontage_depth_ratio,
            use_advanced_optimizer=use_advanced_optimizer,
            use_layout_patterns=use_layout_patterns,
            use_cp_sat=use_cp_sat_solver,
            use_road_optimizer=use_road_optimizer
        )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Step 3: Format response with GeoJSON for visualization
        features = []
        for idx, lot_info in enumerate(result["lots"]):
            lot_polygon = lot_info["polygon"]
            
            # Convert shapely polygon to GeoJSON coordinates
            coords = list(lot_polygon.exterior.coords)
            
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "id": idx + 1,
                    "area_m2": lot_info["area"],
                    "frontage_m": lot_info.get("frontage", 0),
                    "depth_m": lot_info.get("depth", 0),
                    "quality_score": lot_info["quality_score"],
                    "rectangularity": lot_info["quality_metrics"]["rectangularity"],
                    "aspect_ratio": lot_info["quality_metrics"]["aspect_ratio"],
                    "compactness": lot_info["quality_metrics"]["compactness"],
                    "pattern": lot_info.get("pattern", "grid")
                }
            })
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Return comprehensive result
        return {
            "success": True,
            "filename": file.filename,
            "site_info": {
                "area_ha": analysis["site_info"]["area_ha"],
                "area_m2": analysis["site_info"]["area_m2"],
                "perimeter_m": analysis["site_info"]["perimeter_m"],
                "center": analysis["site_info"]["center"]
            },
            "subdivision_result": {
                "total_lots": result["statistics"]["total_lots"],
                "total_area_m2": result["statistics"]["total_subdivided_area"],
                "average_lot_size": result["statistics"]["average_lot_size"],
                "average_quality_score": result["statistics"]["average_quality_score"],
                "rejection_rate": result["statistics"]["rejection_rate"],
                "rectangularity": result["statistics"]["average_rectangularity"],
                "aspect_ratio_score": result["statistics"]["average_aspect_ratio_score"],
                "compactness": result["statistics"]["average_compactness"]
            },
            "geojson": geojson,
            "algorithms_used": {
                "advanced_optimizer": use_advanced_optimizer,
                "layout_patterns": use_layout_patterns,
                "cp_sat_solver": use_cp_sat_solver,
                "road_optimizer": use_road_optimizer
            },
            "quality_summary": {
                "excellent_lots": sum(1 for lot in result["lots"] if lot["quality_score"] >= 90),
                "good_lots": sum(1 for lot in result["lots"] if 70 <= lot["quality_score"] < 90),
                "acceptable_lots": sum(1 for lot in result["lots"] if 50 <= lot["quality_score"] < 70),
                "poor_lots": sum(1 for lot in result["lots"] if lot["quality_score"] < 50)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Subdivision optimization failed: {str(e)}"
        )


@router.get("/api/optimize-subdivision/health")
async def check_health():
    """Check if optimized algorithms are available."""
    return {
        "optimized_algorithms_available": OPTIMIZED_ALGORITHMS_AVAILABLE,
        "backend_path": backend_path,
        "optimization_path": docker_optimization_path if OPTIMIZED_ALGORITHMS_AVAILABLE else None
    }


# Export router
def get_router():
    return router
