"""
Demo API Endpoints for Pilot DWG Processing

Provides FastAPI endpoints for:
- Analyzing Pilot DWG and dividing into zones
- Generating layout for specific zone
- Downloading color-coded DXF output
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import tempfile
import shutil
from pathlib import Path
import json
import time

from demo.pilot_zone_processor import process_pilot_zone
from demo.fast_layout_generator import FastLayoutGenerator
from demo.demo_dxf_generator import DemoDXFGenerator
from demo.full_site_analyzer import FullSiteAnalyzer
from demo.scenario_generator import ScenarioGenerator

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory storage for demo (replace with database in production)
demo_jobs = {}
demo_files = {}


class ZoneInfo(BaseModel):
    """Zone information"""
    id: int
    name: str
    area_ha: float
    area_m2: float
    bounds: List[float]
    centroid: List[float]


class ZoneAnalysisResponse(BaseModel):
    """Response from zone analysis"""
    total_area_ha: float
    zones: List[ZoneInfo]
    has_topography: bool
    elevation_range: Optional[List[float]] = None


class ZoneLayoutRequest(BaseModel):
    """Request to generate zone layout"""
    zone_id: int
    industry_focus: Optional[str] = "light_manufacturing"
    extract_terrain: bool = True


class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: str  # "processing", "completed", "failed"
    progress: int  # 0-100
    message: Optional[str] = None
    result: Optional[Dict] = None
    error: Optional[str] = None


@router.post("/analyze-pilot", response_model=ZoneAnalysisResponse)
async def analyze_pilot_dwg(
    file: UploadFile = File(...)
):
    """
    Analyze Pilot DWG/DXF and divide into zones
    
    Returns zone information for all 4 quadrants
    """
    logger.info(f"Analyzing Pilot DWG: {file.filename}")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    try:
        # Import here to avoid circular imports
        from demo.pilot_zone_processor import PilotZoneProcessor
        
        processor = PilotZoneProcessor()
        
        # Extract boundary
        boundary = processor.extract_pilot_boundary(tmp_path)
        
        # Try to extract topography (but don't fail if it doesn't exist)
        has_topography = False
        elevation_range = None
        
        try:
            topo_data = processor.extract_topography_data(tmp_path)
            if topo_data and topo_data.get('point_count', 0) > 0:
                has_topography = True
                elevation_range = list(topo_data['elevation_range'])
        except Exception as e:
            logger.warning(f"Could not extract topography: {e}")
        
        # Divide into zones
        zones = processor.divide_into_zones(boundary)
        
        # Store file path for later use
        file_id = Path(tmp_path).stem
        demo_files[file_id] = {
            'path': tmp_path,
            'filename': file.filename,
            'processor': processor
        }
        
        # Convert zones to response format
        zone_infos = [
            ZoneInfo(
                id=z['id'],
                name=z['name'],
                area_ha=z['area_ha'],
                area_m2=z['area_m2'],
                bounds=list(z['bounds']),
                centroid=list(z['centroid'])
            )
            for z in zones
        ]
        
        total_area_ha = boundary.area / 10000
        
        return ZoneAnalysisResponse(
            total_area_ha=total_area_ha,
            zones=zone_infos,
            has_topography=has_topography,
            elevation_range=elevation_range
        )
        
    except Exception as e:
        logger.error(f"Failed to analyze Pilot DWG: {e}")
        # Clean up temp file
        Path(tmp_path).unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-zone-layout")
async def generate_zone_layout(
    request: ZoneLayoutRequest,
    background_tasks: BackgroundTasks,
    file_id: Optional[str] = None
):
    """
    Generate layout for specific zone
    
    Returns job ID for tracking progress
    """
    logger.info(f"Generating layout for Zone {request.zone_id}")
    
    # For demo, we'll process synchronously but simulate async
    # In production, use Celery or similar
    
    job_id = f"demo_{int(time.time())}_{request.zone_id}"
    
    demo_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'zone_id': request.zone_id,
        'started_at': time.time()
    }
    
    # Add background task
    background_tasks.add_task(
        process_zone_layout,
        job_id=job_id,
        zone_id=request.zone_id,
        extract_terrain=request.extract_terrain,
        file_id=file_id
    )
    
    return {
        'job_id': job_id,
        'status': 'processing',
        'message': f'Processing Zone {request.zone_id}...'
    }


@router.get("/job-status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get status of layout generation job
    """
    if job_id not in demo_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = demo_jobs[job_id]
    
    return JobStatusResponse(
        job_id=job_id,
        status=job['status'],
        progress=job.get('progress', 0),
        message=job.get('message'),
        result=job.get('result'),
        error=job.get('error')
    )


@router.get("/download/{filename}")
async def download_dxf(filename: str):
    """
    Download generated DXF file
    """
    from fastapi.responses import FileResponse
    
    # In production, use proper file storage
    file_path = Path("exports") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/dxf"
    )


# Background worker function
def process_zone_layout(
    job_id: str,
    zone_id: int,
    extract_terrain: bool,
    file_id: Optional[str] = None
):
    """
    Background worker to process zone layout
    """
    try:
        logger.info(f"[Job {job_id}] Starting zone layout generation")
        
        demo_jobs[job_id]['progress'] = 10
        demo_jobs[job_id]['message'] = "Extracting zone data..."
        
        # Get file path (for demo, use sample file if not provided)
        if file_id and file_id in demo_files:
            file_path = demo_files[file_id]['path']
        else:
            # Use sample Pilot file
            file_path = "sample-data/Pilot_Existing Topo _ Boundary.dxf"
        
        # Process zone
        demo_jobs[job_id]['progress'] = 20
        demo_jobs[job_id]['message'] = "Processing topography..."
        
        zone_data = process_pilot_zone(
            file_path=file_path,
            zone_id=zone_id,
            extract_terrain=extract_terrain
        )
        
        # Generate layout
        demo_jobs[job_id]['progress'] = 40
        demo_jobs[job_id]['message'] = "Generating layout..."
        
        generator = FastLayoutGenerator(terrain_strategy='balanced_cut_fill')
        
        layout = generator.generate_layout(
            zone=zone_data['zone'],
            parameters=zone_data['parameters'],
            terrain_data=zone_data['zone'].get('terrain_data')
        )
        
        # Export to DXF
        demo_jobs[job_id]['progress'] = 80
        demo_jobs[job_id]['message'] = "Exporting DXF..."
        
        dxf_gen = DemoDXFGenerator(output_dir="exports")
        
        # Prepare layout for DXF export
        export_layout = {
            'name': f"Pilot Zone {zone_id}",
            'variant_id': f"zone{zone_id}_demo",
            'site_boundary': zone_data['zone']['geometry'],
            'buildings': layout['plots'],
            'roads': layout['roads'],
            'green_areas': layout['green_areas'],
            'fire_stations': layout['fire_stations'],
            'terrain_data': zone_data['zone'].get('terrain_data')
        }
        
        dxf_path = dxf_gen.generate(
            export_layout,
            filename=f"pilot_zone{zone_id}_demo.dxf"
        )
        
        # Complete
        demo_jobs[job_id]['progress'] = 100
        demo_jobs[job_id]['status'] = 'completed'
        demo_jobs[job_id]['message'] = "Layout generation complete!"
        demo_jobs[job_id]['result'] = {
            'dxf_file': Path(dxf_path).name,
            'download_url': f"/api/demo/download/{Path(dxf_path).name}",
            'statistics': layout['statistics'],
            'grading_cost': layout['grading_cost'],
            'plot_count': len(layout['plots']),
            'processing_time': time.time() - demo_jobs[job_id]['started_at']
        }
        
        logger.info(f"[Job {job_id}] Completed successfully")
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {e}")
        demo_jobs[job_id]['status'] = 'failed'
        demo_jobs[job_id]['error'] = str(e)
        demo_jobs[job_id]['progress'] = 0


# ============================================================================
# FULL-SITE ANALYSIS ENDPOINTS
# ============================================================================

class FullSiteAnalysisRequest(BaseModel):
    """Request for full-site analysis"""
    target_plot_count: int = 200


class ScenarioInfo(BaseModel):
    """Scenario information"""
    scenario_id: str
    name: str
    description: str
    strategy: str
    plot_count: int
    development_area_ha: float
    estimated_cost_usd: float
    generation_time_s: float


class FullSiteAnalysisResponse(BaseModel):
    """Response from full-site analysis"""
    job_id: str
    status: str
    message: str


@router.post("/analyze-full-site", response_model=FullSiteAnalysisResponse)
async def analyze_full_site(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    target_plot_count: int = 200
):
    """
    Analyze entire Pilot site and generate development scenarios.
    
    This endpoint:
    1. Extracts site boundary
    2. Analyzes terrain and identifies buildable zones
    3. Generates 3 development scenarios (Cost, Capacity, Balanced)
    4. Returns job ID for tracking progress
    
    Args:
        file: DWG/DXF file upload
        target_plot_count: Target number of plots (default: 200)
    
    Returns:
        Job ID and initial status
    """
    try:
        # Save uploaded file to uploads directory
        import uuid
        import os
        
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        file_id = str(uuid.uuid4())
        tmp_path = upload_dir / f"{file_id}.dxf"
        
        with open(tmp_path, 'wb') as tmp:
            shutil.copyfileobj(file.file, tmp)
        
        # Create job
        job_id = str(uuid.uuid4())
        
        demo_jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Starting full-site analysis...',
            'started_at': time.time(),
            'type': 'full_site_analysis'
        }
        
        # Add background task
        if background_tasks:
            background_tasks.add_task(
                process_full_site_analysis,
                job_id=job_id,
                file_path=tmp_path,
                target_plot_count=target_plot_count
            )
        
        return {
            'job_id': job_id,
            'status': 'processing',
            'message': 'Full-site analysis started'
        }
        
    except Exception as e:
        logger.error(f"Failed to start full-site analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scenarios/{job_id}")
async def get_scenarios(job_id: str):
    """
    Get scenarios for a completed full-site analysis job.
    
    Args:
        job_id: Job ID from analyze_full_site
    
    Returns:
        Scenario comparison data
    """
    if job_id not in demo_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = demo_jobs[job_id]
    
    if job['status'] != 'completed':
        return {
            'job_id': job_id,
            'status': job['status'],
            'progress': job.get('progress', 0),
            'message': job.get('message', ''),
            'scenarios': None
        }
    
    # Return scenarios
    return {
        'job_id': job_id,
        'status': 'completed',
        'progress': 100,
        'message': 'Analysis complete',
        'site_analysis': job['result']['site_analysis'],
        'scenarios': job['result']['scenarios']
    }


@router.post("/select-scenario")
async def select_scenario(
    job_id: str,
    scenario_id: str,
    background_tasks: BackgroundTasks = None
):
    """
    Select a scenario and export to DXF.
    
    Args:
        job_id: Job ID from analyze_full_site
        scenario_id: Scenario ID (A, B, or C)
    
    Returns:
        Export job information
    """
    if job_id not in demo_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = demo_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Analysis not complete")
    
    # Find selected scenario from original scenarios (with geometry)
    original_scenarios = job.get('_original_scenarios', [])
    selected = next((s for s in original_scenarios if s['scenario_id'] == scenario_id), None)
    
    if not selected:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create export job
    import uuid
    export_job_id = str(uuid.uuid4())
    
    demo_jobs[export_job_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'Exporting scenario to DXF...',
        'started_at': time.time(),
        'type': 'scenario_export'
    }
    
    # Add background task
    if background_tasks:
        background_tasks.add_task(
            export_scenario_dxf,
            export_job_id=export_job_id,
            scenario=selected,
            site_boundary=job['result']['site_analysis']['terrain_data']['elevation_grid']
        )
    
    return {
        'export_job_id': export_job_id,
        'status': 'processing',
        'message': 'DXF export started',
        'scenario': {
            'id': selected['scenario_id'],
            'name': selected['name'],
            'plot_count': selected['metrics']['plot_count']
        }
    }


def process_full_site_analysis(
    job_id: str,
    file_path: str,
    target_plot_count: int
):
    """
    Background worker for full-site analysis.
    """
    try:
        logger.info(f"[Job {job_id}] Starting full-site analysis")
        
        # Extract boundary
        demo_jobs[job_id]['progress'] = 10
        demo_jobs[job_id]['message'] = "Extracting site boundary..."
        
        from demo.pilot_zone_processor import PilotZoneProcessor
        processor = PilotZoneProcessor()
        site_boundary = processor.extract_pilot_boundary(file_path)
        
        # Analyze full site
        demo_jobs[job_id]['progress'] = 20
        demo_jobs[job_id]['message'] = "Analyzing terrain and identifying buildable zones..."
        
        analyzer = FullSiteAnalyzer(grid_resolution=20.0)
        site_analysis = analyzer.analyze_entire_site(file_path, site_boundary)
        
        # Generate scenarios
        demo_jobs[job_id]['progress'] = 50
        demo_jobs[job_id]['message'] = "Generating development scenarios..."
        
        scenario_gen = ScenarioGenerator()
        scenarios = scenario_gen.generate_scenarios(
            site_analysis,
            target_plot_count=target_plot_count
        )
        
        # Convert scenarios to serializable format
        serializable_scenarios = []
        for scenario in scenarios:
            # Remove non-serializable objects
            scenario_copy = scenario.copy()
            
            # Remove geometry objects from zones
            if 'selected_zones' in scenario_copy:
                for zone in scenario_copy['selected_zones']:
                    if 'geometry' in zone:
                        zone['geometry'] = None
                    if 'centroid' in zone:
                        zone['centroid'] = None
            
            # Remove layout geometry
            if 'layout' in scenario_copy:
                layout = scenario_copy['layout']
                for plot in layout.get('plots', []):
                    if 'geometry' in plot:
                        plot['geometry'] = None
                for road in layout.get('roads', []):
                    if 'geometry' in road:
                        road['geometry'] = None
                for green in layout.get('green_areas', []):
                    if 'geometry' in green:
                        green['geometry'] = None
            
            serializable_scenarios.append(scenario_copy)
        
        # Complete
        demo_jobs[job_id]['progress'] = 100
        demo_jobs[job_id]['status'] = 'completed'
        demo_jobs[job_id]['message'] = "Full-site analysis complete!"
        demo_jobs[job_id]['result'] = {
            'site_analysis': {
                'site_area_ha': site_analysis['site_area_ha'],
                'buildable_zones': len(site_analysis['buildable_zones']),
                'optimal_zones': len(site_analysis['optimal_zones']),
                'statistics': site_analysis['statistics'],
                'processing_time_s': site_analysis['processing_time_s']
            },
            'scenarios': serializable_scenarios
        }
        # Store original scenarios separately for DXF export (not serialized)
        demo_jobs[job_id]['_original_scenarios'] = scenarios
        
        logger.info(f"[Job {job_id}] Completed successfully")
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {e}")
        import traceback
        traceback.print_exc()
        demo_jobs[job_id]['status'] = 'failed'
        demo_jobs[job_id]['error'] = str(e)
        demo_jobs[job_id]['progress'] = 0


def export_scenario_dxf(
    export_job_id: str,
    scenario: Dict,
    site_boundary: Dict
):
    """
    Background worker to export scenario to DXF.
    """
    try:
        logger.info(f"[Export {export_job_id}] Starting DXF export")
        
        demo_jobs[export_job_id]['progress'] = 20
        demo_jobs[export_job_id]['message'] = "Preparing layout data..."
        
        # Get layout from scenario
        layout = scenario['layout']
        
        # Export to DXF
        demo_jobs[export_job_id]['progress'] = 50
        demo_jobs[export_job_id]['message'] = "Generating DXF file..."
        
        dxf_gen = DemoDXFGenerator(output_dir="exports")
        
        # Prepare export layout
        export_layout = {
            'name': f"Pilot Full Site - Scenario {scenario['scenario_id']}",
            'variant_id': f"fullsite_scenario_{scenario['scenario_id']}",
            'site_boundary': None,  # Will be reconstructed from terrain data
            'buildings': layout['plots'],
            'roads': layout['roads'],
            'green_areas': layout.get('green_areas', []),
            'fire_stations': layout.get('fire_stations', []),
            'terrain_data': None
        }
        
        filename = f"pilot_fullsite_scenario_{scenario['scenario_id']}.dxf"
        dxf_path = dxf_gen.generate(export_layout, filename=filename)
        
        # Complete
        demo_jobs[export_job_id]['progress'] = 100
        demo_jobs[export_job_id]['status'] = 'completed'
        demo_jobs[export_job_id]['message'] = "DXF export complete!"
        demo_jobs[export_job_id]['result'] = {
            'dxf_file': Path(dxf_path).name,
            'download_url': f"/api/demo/download/{Path(dxf_path).name}",
            'scenario_id': scenario['scenario_id'],
            'scenario_name': scenario['name'],
            'plot_count': scenario['metrics']['plot_count']
        }
        
        logger.info(f"[Export {export_job_id}] Completed successfully")
        
    except Exception as e:
        logger.error(f"[Export {export_job_id}] Failed: {e}")
        import traceback
        traceback.print_exc()
        demo_jobs[export_job_id]['status'] = 'failed'
        demo_jobs[export_job_id]['error'] = str(e)
        demo_jobs[export_job_id]['progress'] = 0


def get_router():
    """Get demo router"""
    return router
