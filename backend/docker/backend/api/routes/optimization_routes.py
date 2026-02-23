"""Optimization API routes."""

import logging
import traceback
from fastapi import APIRouter, HTTPException, Request
from shapely.geometry import Polygon, mapping, LineString, Point, shape

from api.schemas.request_schemas import OptimizationRequest
from api.schemas.response_schemas import OptimizationResponse, StageResult
from pipeline.land_redistribution import LandRedistributionPipeline

logger = logging.getLogger(__name__)
router = APIRouter()

# Global storage for last optimization result (for frontend access)
_last_optimization_result = None


@router.post("/optimize-debug")
async def optimize_debug(request: Request):
    """Debug endpoint to see raw request body."""
    body = await request.json()
    logger.info(f"[DEBUG] Raw request body: {body}")
    return {"received": body}


@router.get("/test-logging")
async def test_logging():
    """Test endpoint to verify logging works."""
    logger.info("🟢🟢🟢 TEST ENDPOINT HIT! Logging works!")
    return {"status": "ok", "message": "CODE VERSION: 2025-12-15-13-42 ZONE FORCED"}


@router.get("/zone-test")
async def zone_test():
    """Return zone colors to test."""
    return {
        "version": "2025-12-15-13-42-FORCED", 
        "zones": ["FACTORY", "WAREHOUSE", "RESIDENTIAL", "SERVICE", "GREEN"]
    }


def land_plot_to_polygon(land_plot: dict) -> Polygon:
    """Convert LandPlot model to Shapely Polygon."""
    coords = land_plot['coordinates'][0]  # Exterior ring
    return Polygon(coords)


def polygon_to_geojson(poly: Polygon, pipeline=None) -> dict:
    """Convert Shapely Polygon to GeoJSON, converting back to geographic if needed."""
    if pipeline and hasattr(pipeline, 'to_geographic'):
        poly = pipeline.to_geographic(poly)
    return mapping(poly)


def geom_to_geojson(geom, pipeline=None) -> dict:
    """Convert any Shapely geometry to GeoJSON, converting back to geographic if needed."""
    if pipeline and hasattr(pipeline, 'to_geographic'):
        geom = pipeline.to_geographic(geom)
    return mapping(geom)


@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_full(request: OptimizationRequest):
    """
    Run complete land redistribution optimization pipeline.
    
    This endpoint executes all stages:
    1. Grid optimization (NSGA-II)
    2. Block subdivision (OR-Tools)
    3. Infrastructure planning
    """
    try:
        logger.info(f"🔵 [OPTIMIZE] === REQUEST START === Received request with {len(request.land_plots)} land plots")
        logger.info(f"🔵 [OPTIMIZE] Config: {request.config.dict()}")
        
        # Convert input land plots to Shapely polygons
        land_polygons = [land_plot_to_polygon(plot.dict()) for plot in request.land_plots]
        logger.info(f"🔵 [OPTIMIZE] Converted {len(land_polygons)} polygons")
        
        # Create pipeline
        config = request.config.dict()
        logger.info(f"API Request Config: Spacing=[{config.get('spacing_min')}, {config.get('spacing_max')}], RoadWidth={config.get('road_width')}")
        pipeline = LandRedistributionPipeline(land_polygons, config)
        logger.info(f"🔵 [OPTIMIZE] Pipeline created")
        
        # Run optimization with Skeleton layout method (hierarchical road network)
        # Use 20 branches for 425ha site (1 main spine + 20 perpendicular branches)
        num_branches = config.get('skeleton_branches', 20)
        logger.info(f"🔵 [OPTIMIZE] About to call run_full_pipeline with branches={num_branches}")
        result = pipeline.run_full_pipeline(layout_method='skeleton', num_branches=num_branches)
        logger.info(f"🔵 [OPTIMIZE] run_full_pipeline returned. Checking result...")
        logger.info(f"🔵 [OPTIMIZE] result keys: {result.keys()}")
        logger.info(f"🔵 [OPTIMIZE] stage2 lots count: {len(result.get('stage2', {}).get('lots', []))}")
        
        # Check first lot zone
        if result.get('stage2', {}).get('lots'):
            first_lot = result['stage2']['lots'][0]
            logger.info(f"🔵 [OPTIMIZE] First lot zone: {first_lot.get('zone', 'NO ZONE KEY')}")
        
        
        # Build stage results
        stages = []
        
        # Stage 1: Grid Optimization
        stage1_geoms = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": polygon_to_geojson(block, pipeline),
                    "properties": {"stage": "grid", "type": "block"}
                }
                for block in result['stage1']['blocks']
            ]
        }
        
        stages.append(StageResult(
            stage_name="Grid Optimization (NSGA-II)",
            geometry=stage1_geoms,
            metrics=result['stage1']['metrics'],
            parameters={
                "spacing": result['stage1']['spacing'],
                "angle": result['stage1']['angle']
            }
        ))
        
        # Stage 2: Subdivision
        stage2_features = []
        
        # Add lots with REAL zone data from advanced classifier
        for idx, lot in enumerate(result['stage2']['lots']):
            # Use real zone from pipeline (advanced classifier)
            # This creates coherent zone clusters like reference design
            real_zone = lot.get('zone', 'WAREHOUSE')  # Default if missing
            
            lot_props = {
                "stage": "subdivision",
                "type": "lot",
                "width": lot['width'],
                "area": lot.get('area', 0),
                "zone": real_zone,  # Use REAL zone from classifier
                "zone_color": lot.get('zone_color', '#9E9E9E')
            }
            geojson_geom = polygon_to_geojson(lot['geometry'], pipeline)
            # Debug first lot coordinates
            if idx == 0:
                coords = geojson_geom['coordinates'][0][0]  # First point
                logger.info(f"[OPTIMIZE] First lot: zone={real_zone}, coords={coords}")
            stage2_features.append({
                "type": "Feature",
                "geometry": geojson_geom,
                "properties": lot_props
            })
            
            # Setback
            if lot.get('buildable'):
                stage2_features.append({
                    "type": "Feature",
                    "geometry": polygon_to_geojson(lot['buildable'], pipeline),
                    "properties": {
                        "stage": "subdivision",
                        "type": "setback",
                        "parent_lot": str(lot['geometry'])
                    }
                })
        
        # Add parks
        for park in result['stage2']['parks']:
            stage2_features.append({
                "type": "Feature",
                "geometry": polygon_to_geojson(park, pipeline),
                "properties": {
                    "stage": "subdivision",
                    "type": "lot",  # Changed to lot so it uses zone coloring
                    "zone": "GREEN"
                }
            })
        
        # Add green_spaces (includes lakes from amenities)
        for green_space in result['stage2'].get('green_spaces', []):
            stage2_features.append({
                "type": "Feature",
                "geometry": polygon_to_geojson(green_space, pipeline),
                "properties": {
                    "stage": "subdivision",
                    "type": "lot",  # Use lot type so it uses zone coloring
                    "zone": "GREEN"
                }
            })
        
        # Add amenities (lakes with WATER zone)
        if 'amenities' in result:
            # Add parks/green buffers
            for park in result['amenities'].get('parks', []):
                if 'coords' in park:
                    stage2_features.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": park['coords']},
                        "properties": {
                            "stage": "subdivision",
                            "type": "park",
                            "park_type": park.get('type', 'park'),
                            "area": park.get('area', 0)
                        }
                    })
            
            # Add lakes
            for lake in result['amenities'].get('lakes', []):
                if 'coords' in lake:
                    stage2_features.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": lake['coords']},
                        "properties": {
                            "stage": "subdivision",
                            "type": "water",
                            "area": lake.get('area', 0)
                        }
                    })
            
            # Add parking areas
            for parking in result['amenities'].get('parking', []):
                if 'coords' in parking:
                    stage2_features.append({
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": parking['coords']},
                        "properties": {
                            "stage": "subdivision",
                            "type": "parking",
                            "zone": parking.get('zone', 'WAREHOUSE')
                        }
                    })
        
        # Add Service Blocks
        for block in result['classification'].get('service', []):
            stage2_features.append({
                "type": "Feature",
                "geometry": polygon_to_geojson(block, pipeline),
                "properties": {
                    "stage": "subdivision",
                    "type": "service",
                    "label": "Operating Center/Parking"
                }
            })

        # Add XLNT Block
        for block in result['classification'].get('xlnt', []):
            stage2_features.append({
                "type": "Feature",
                "geometry": polygon_to_geojson(block, pipeline),
                "properties": {
                    "stage": "subdivision",
                    "type": "xlnt",
                    "label": "Wastewater Treatment"
                }
            })

        stage2_geoms = {
            "type": "FeatureCollection",
            "features": stage2_features
        }
        
        stages.append(StageResult(
            stage_name="Block Subdivision (OR-Tools)",
            geometry=stage2_geoms,
            metrics={
                **result['stage2']['metrics'],
                "service_count": result['classification']['service_count'],
                "xlnt_count": result['classification']['xlnt_count']
            },
            parameters={
                "min_lot_width": config['min_lot_width'],
                "max_lot_width": config['max_lot_width'],
                "target_lot_width": config['target_lot_width']
            }
        ))
        
        # Stage 3: Infrastructure
        stage3_features = []
        
        # Add road network (also add to Stage 2 for visualization)
        if 'road_network' in result['stage3']:
            # Convert back from metric to geographic
            road_geom = shape(result['stage3']['road_network'])
            road_feat = {
                "type": "Feature",
                "geometry": geom_to_geojson(road_geom, pipeline),
                "properties": {
                    "stage": "subdivision",
                    "type": "road",
                    "label": "Road Network"
                }
            }
            # Add to both Stage 2 and Stage 3 for complete visualization
            stage2_features.insert(0, road_feat)
            stage3_features.insert(0, road_feat)

        # Add connection lines
        for conn_coords in result['stage3']['connections']:
            stage3_features.append({
                "type": "Feature",
                "geometry": geom_to_geojson(LineString(conn_coords), pipeline),
                "properties": {
                    "stage": "infrastructure",
                    "type": "connection",
                    "layer": "electricity_water"
                }
            })
            
        # Add Transformers
        if 'transformers' in result['stage3']:
            for tf_coords in result['stage3']['transformers']:
                stage3_features.append({
                    "type": "Feature",
                    "geometry": geom_to_geojson(Point(tf_coords), pipeline),
                    "properties": {
                        "stage": "infrastructure",
                        "type": "transformer",
                        "label": "Transformer Station"
                    }
                })

        # Add drainage
        for drainage in result['stage3']['drainage']:
            start = drainage['start']
            vec = drainage['vector']
            end = (start[0] + vec[0], start[1] + vec[1])
            stage3_features.append({
                "type": "Feature",
                "geometry": geom_to_geojson(LineString([start, end]), pipeline),
                "properties": {
                    "stage": "infrastructure",
                    "type": "drainage"
                }
            })
            
        stage3_geoms = {
            "type": "FeatureCollection",
            "features": stage3_features + stage2_features
        }
        
        stages.append(StageResult(
            stage_name="Infrastructure (MST & Drainage & Roads)",
            geometry=stage3_geoms,
            metrics={
                "total_connections": len(result['stage3']['connections']),
                "drainage_points": len(result['stage3']['drainage']),
                "transformers": len(result.get('stage3', {}).get('transformers', []))
            },
            parameters={}
        ))
        
        return OptimizationResponse(
            success=True,
            message="Optimization completed successfully",
            stages=stages,
            final_layout=stage3_geoms,
            total_lots=result['total_lots'],
            statistics={
                "total_blocks": result['stage1']['metrics']['total_blocks'],
                "total_lots": result['stage2']['metrics']['total_lots'],
                "total_parks": result['stage2']['metrics']['total_parks'],
                "optimal_spacing": result['stage1']['spacing'],
                "optimal_angle": result['stage1']['angle'],
                "avg_lot_width": result['stage2']['metrics']['avg_lot_width'],
                "service_area_count": result['classification']['service_count'] + result['classification']['xlnt_count']
            }
        )
        
        # Store result globally for frontend access
        global _last_optimization_result
        _last_optimization_result = response_obj
        logger.info(f"✅ [OPTIMIZE] Stored optimization result globally")
        
        return response_obj
        
    except Exception as e:
        error_msg = f"Optimization failed: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/last-optimization")
async def get_last_optimization():
    """Get the last optimization result for frontend rendering."""
    global _last_optimization_result
    
    if _last_optimization_result is None:
        raise HTTPException(status_code=404, detail="No optimization result available")
    
    # Extract lots and amenities from the response
    stage2_features = None
    for stage in _last_optimization_result.stages:
        if stage.stage_name in ["Subdivision (OR-Tools)", "Block Subdivision"]:
            stage2_features = stage.geometry.get("features", [])
            break
    
    if not stage2_features:
        raise HTTPException(status_code=404, detail="No subdivision stage found")
    
    # Separate lots and amenities
    lots = []
    parks = []
    lakes = []
    parking = []
    
    for feature in stage2_features:
        props = feature.get("properties", {})
        feature_type = props.get("type", "")
        
        if feature_type == "lot":
            lots.append({
                "geometry": feature.get("geometry"),
                "properties": props
            })
        elif feature_type == "park":
            parks.append({
                "type": "park",
                "geometry": feature.get("geometry"),
                "properties": props
            })
        elif feature_type == "water":
            lakes.append({
                "type": "water",
                "geometry": feature.get("geometry"),
                "properties": props
            })
        elif feature_type == "parking":
            parking.append({
                "type": "parking",
                "geometry": feature.get("geometry"),
                "properties": props
            })
    
    return {
        "success": True,
        "lots": lots,
        "amenities": {
            "parks": parks,
            "lakes": lakes,
            "parking": parking
        },
        "statistics": _last_optimization_result.statistics
    }


@router.post("/stage1", response_model=OptimizationResponse)
async def optimize_stage1(request: OptimizationRequest):
    """Run only grid optimization stage."""
    try:
        land_polygons = [land_plot_to_polygon(plot.dict()) for plot in request.land_plots]
        config = request.config.dict()
        pipeline = LandRedistributionPipeline(land_polygons, config)
        
        result = pipeline.run_stage1()
        
        stage_geoms = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": polygon_to_geojson(block),
                    "properties": {"stage": "grid", "type": "block"}
                }
                for block in result['blocks']
            ]
        }
        
        return OptimizationResponse(
            success=True,
            message="Stage 1 (Grid Optimization) completed",
            stages=[StageResult(
                stage_name="Grid Optimization (NSGA-II)",
                geometry=stage_geoms,
                metrics=result['metrics'],
                parameters={
                    "spacing": result['spacing'],
                    "angle": result['angle']
                }
            )],
            statistics=result['metrics']
        )
        
    except Exception as e:
        logger.error(f"Stage 1 failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stage 1 failed: {str(e)}")
