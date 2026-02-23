"""
DXF Upload and Georeferencing API Endpoints

Endpoints:
- POST /api/dxf/upload: Upload DXF file
- POST /api/dxf/georeference: Set control points and georeference
- GET /api/dxf/{file_id}/features: Get detected existing features
- POST /api/dxf/{file_id}/classify-reusability: Classify feature reusability
- GET /api/dxf/{file_id}/geojson: Get georeferenced GeoJSON
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Dict, Optional
import os
import uuid
import logging

from cad.dxf_georeferencer import DXFGeoreferencer
from cad.existing_features_detector import ExistingFeaturesDetector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dxf", tags=["dxf"])

# Storage for uploaded files (in production, use database)
UPLOAD_DIR = "uploads/dxf"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Storage for georeferencing instances
georef_instances = {}
feature_cache = {}


class ControlPointsRequest(BaseModel):
    """Request to set georeferencing control points."""
    file_id: str
    dxf_points: List[Tuple[float, float]]
    geo_points: List[Tuple[float, float]]


class FeatureReusabilityRequest(BaseModel):
    """Request to manually override feature reusability."""
    file_id: str
    keep_as_is: List[str]
    reuse_modified: List[str]
    demolish: List[str]


@router.post("/upload")
async def upload_dxf(file: UploadFile = File(...)):
    """
    Upload DXF file for georeferencing and feature extraction.
    
    Returns file_id for subsequent operations.
    """
    try:
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Save uploaded file
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.dxf")
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"[DXF API] Uploaded file {file.filename} as {file_id}")
        
        # Try automatic georeferencing
        georef = DXFGeoreferencer()
        auto_success = georef.auto_georeference_from_dxf(file_path)
        
        if auto_success:
            logger.info(
                f"[DXF API] Auto-georeferencing successful for {file_id}"
            )
            georef_instances[file_id] = georef
            needs_manual = False
        else:
            logger.info(
                f"[DXF API] Manual georeferencing required for {file_id}"
            )
            needs_manual = True
        
        return {
            "file_id": file_id,
            "filename": file.filename,
            "needs_manual_georeferencing": needs_manual,
            "message": (
                "Auto-georeferenced successfully"
                if auto_success
                else "Please provide 3+ control points for georeferencing"
            )
        }
    
    except Exception as e:
        logger.error(f"[DXF API] Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/georeference")
async def georeference_dxf(request: ControlPointsRequest):
    """
    Set control points for manual georeferencing.
    
    Requires at least 3 control points.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{request.file_id}.dxf")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if len(request.dxf_points) < 3:
            raise HTTPException(
                status_code=400,
                detail="Need at least 3 control points"
            )
        
        # Create georeferencer
        georef = DXFGeoreferencer()
        georef.set_manual_control_points(
            request.dxf_points,
            request.geo_points
        )
        
        # Store instance
        georef_instances[request.file_id] = georef
        
        logger.info(
            f"[DXF API] Georeferenced {request.file_id} with "
            f"{len(request.dxf_points)} control points"
        )
        
        return {
            "file_id": request.file_id,
            "status": "georeferenced",
            "control_points_count": len(request.dxf_points),
            "message": "Georeferencing successful"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[DXF API] Georeferencing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/features")
async def get_features(file_id: str):
    """
    Detect existing features from DXF file.
    
    Returns water bodies, buildings, roads, vegetation, obstacles.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.dxf")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check cache
        if file_id in feature_cache:
            logger.info(f"[DXF API] Returning cached features for {file_id}")
            return feature_cache[file_id]
        
        # Detect features
        detector = ExistingFeaturesDetector()
        features = detector.detect_features(file_path)
        
        # Convert Shapely geometries to GeoJSON-compatible dicts
        result = {
            "water_bodies": [
                {
                    **wb,
                    "polygon": wb["polygon"].__geo_interface__
                }
                for wb in features["water_bodies"]
            ],
            "buildings": [
                {
                    **b,
                    "polygon": b["polygon"].__geo_interface__
                }
                for b in features["buildings"]
            ],
            "roads": [
                {
                    **r,
                    "linestring": r["linestring"].__geo_interface__
                }
                for r in features["roads"]
            ],
            "vegetation": [
                {
                    **v,
                    "polygon": v["polygon"].__geo_interface__
                }
                for v in features["vegetation"]
            ],
            "obstacles": [
                {
                    **o,
                    "polygon": o["polygon"].__geo_interface__
                }
                for o in features["obstacles"]
            ],
            "boundary": (
                features["boundary"].__geo_interface__
                if features["boundary"]
                else None
            ),
            "summary": features["summary"]
        }
        
        # Cache result
        feature_cache[file_id] = result
        
        logger.info(
            f"[DXF API] Detected features for {file_id}: "
            f"{len(result['water_bodies'])} water, "
            f"{len(result['buildings'])} buildings"
        )
        
        return result
    
    except Exception as e:
        logger.error(f"[DXF API] Feature detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{file_id}/classify-reusability")
async def classify_reusability(file_id: str):
    """
    Classify existing features by reusability.
    
    Returns keep_as_is, reuse_modified, demolish lists and constraints.
    """
    try:
        # Get features
        if file_id not in feature_cache:
            # Fetch features first
            await get_features(file_id)
        
        features_data = feature_cache[file_id]
        
        # Reconstruct Shapely geometries
        from shapely.geometry import shape
        
        features = {
            "water_bodies": [
                {
                    **wb,
                    "polygon": shape(wb["polygon"])
                }
                for wb in features_data["water_bodies"]
            ],
            "buildings": [
                {
                    **b,
                    "polygon": shape(b["polygon"])
                }
                for b in features_data["buildings"]
            ],
            "roads": [
                {
                    **r,
                    "linestring": shape(r["linestring"])
                }
                for r in features_data["roads"]
            ],
            "vegetation": [
                {
                    **v,
                    "polygon": shape(v["polygon"])
                }
                for v in features_data["vegetation"]
            ],
            "obstacles": features_data["obstacles"]
        }
        
        # Classify
        detector = ExistingFeaturesDetector()
        reusability = detector.classify_reusability(features)
        
        # Convert constraint polygons/linestrings to GeoJSON
        constraints_json = []
        for constraint in reusability["constraints"]:
            constraint_copy = constraint.copy()
            if "polygon" in constraint_copy:
                constraint_copy["polygon"] = constraint_copy[
                    "polygon"
                ].__geo_interface__
            if "linestring" in constraint_copy:
                constraint_copy["linestring"] = constraint_copy[
                    "linestring"
                ].__geo_interface__
            constraints_json.append(constraint_copy)
        
        result = {
            **reusability,
            "constraints": constraints_json
        }
        
        logger.info(
            f"[DXF API] Classified reusability for {file_id}: "
            f"{len(result['keep_as_is'])} keep, "
            f"{len(result['reuse_modified'])} reuse, "
            f"{len(result['demolish'])} demolish"
        )
        
        return result
    
    except Exception as e:
        logger.error(
            f"[DXF API] Reusability classification error: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{file_id}/geojson")
async def get_geojson(file_id: str):
    """
    Get georeferenced GeoJSON for Mapbox display.
    
    Requires file to be georeferenced first.
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}.dxf")
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        if file_id not in georef_instances:
            raise HTTPException(
                status_code=400,
                detail="File not georeferenced. "
                       "Upload and georeference first."
            )
        
        georef = georef_instances[file_id]
        
        # Convert to GeoJSON
        geojson = georef.dxf_to_geojson(file_path)
        
        # Calculate bounds for Mapbox viewport
        bounds = georef.calculate_bounds(geojson)
        
        logger.info(
            f"[DXF API] Generated GeoJSON for {file_id}, "
            f"{len(geojson['features'])} features"
        )
        
        return {
            "geojson": geojson,
            "bounds": bounds
        }
    
    except Exception as e:
        logger.error(f"[DXF API] GeoJSON generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{file_id}/reusability-override")
async def override_reusability(request: FeatureReusabilityRequest):
    """
    Manually override automatic reusability classification.
    
    Allows user to customize which features to keep/reuse/demolish.
    """
    try:
        logger.info(
            f"[DXF API] Reusability override for {request.file_id}: "
            f"keep={len(request.keep_as_is)}, "
            f"reuse={len(request.reuse_modified)}, "
            f"demolish={len(request.demolish)}"
        )
        
        # Store user preferences (in production, save to database)
        override_key = f"{request.file_id}_reusability"
        feature_cache[override_key] = {
            "keep_as_is": request.keep_as_is,
            "reuse_modified": request.reuse_modified,
            "demolish": request.demolish
        }
        
        return {
            "file_id": request.file_id,
            "status": "override_saved",
            "message": "Reusability preferences saved"
        }
    
    except Exception as e:
        logger.error(f"[DXF API] Override error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
