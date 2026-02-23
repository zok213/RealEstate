"""
Full-site processing endpoints - append to demo_endpoints.py
"""

# ============================================================================
# FULL-SITE PROCESSING ENDPOINTS
# ============================================================================

@router.post("/analyze-full-site")
async def analyze_full_site(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    target_plot_count: int = 200
):
    """
    Analyze entire Pilot site and generate development scenarios.
    
    This processes the full 191.42 ha site instead of dividing into zones.
    Returns 3 scenarios: Cost-Optimized, Maximum Capacity, and Balanced.
    """
    logger.info(f"Starting full-site analysis: {file.filename}")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    # Create job
    job_id = f"fullsite_{int(time.time())}"
    
    demo_jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'started_at': time.time(),
        'file_path': tmp_path,
        'target_plot_count': target_plot_count
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
        'message': 'Analyzing full site and generating scenarios...'
    }


@router.get("/scenarios/{job_id}")
async def get_scenarios(job_id: str):
    """
    Get generated scenarios for a full-site analysis job.
    
    Returns all 3 scenarios with metrics and comparison data.
    """
    if job_id not in demo_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = demo_jobs[job_id]
    
    if job['status'] != 'completed':
        return {
            'job_id': job_id,
            'status': job['status'],
            'progress': job.get('progress', 0),
            'message': job.get('message', 'Processing...')
        }
    
    # Return scenarios
    scenarios = job.get('scenarios', [])
    
    # Convert to response format
    scenario_infos = []
    for s in scenarios:
        scenario_infos.append({
            'scenario_id': s['scenario_id'],
            'name': s['name'],
            'description': s['description'],
            'plot_count': s['metrics']['plot_count'],
            'development_area_ha': s['metrics']['development_area_ha'],
            'estimated_cost_usd': s['grading_cost']['estimated_cost_usd'],
            'metrics': s['metrics'],
            'generation_time_s': s['generation_time_s']
        })
    
    return {
        'job_id': job_id,
        'status': 'completed',
        'scenarios': scenario_infos,
        'site_analysis': job.get('site_analysis', {}),
        'processing_time': job.get('processing_time', 0)
    }


@router.post("/select-scenario")
async def select_scenario(
    job_id: str,
    scenario_id: str,
    background_tasks: BackgroundTasks
):
    """
    Select a scenario and generate final DXF export.
    
    Args:
        job_id: Full-site analysis job ID
        scenario_id: Scenario ID (A, B, or C)
    
    Returns:
        Job ID for DXF generation
    """
    if job_id not in demo_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = demo_jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Analysis not completed yet")
    
    scenarios = job.get('scenarios', [])
    selected_scenario = None
    
    for s in scenarios:
        if s['scenario_id'] == scenario_id:
            selected_scenario = s
            break
    
    if not selected_scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    # Create DXF export job
    export_job_id = f"export_{job_id}_{scenario_id}"
    
    demo_jobs[export_job_id] = {
        'status': 'processing',
        'progress': 0,
        'started_at': time.time(),
        'scenario': selected_scenario
    }
    
    # Add background task
    background_tasks.add_task(
        export_scenario_dxf,
        job_id=export_job_id,
        scenario=selected_scenario
    )
    
    return {
        'job_id': export_job_id,
        'status': 'processing',
        'message': f'Exporting Scenario {scenario_id} to DXF...'
    }


# Background worker functions for full-site processing

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
        
        logger.info(f"Site boundary: {site_boundary.area / 10000:.2f} ha")
        
        # Analyze full site
        demo_jobs[job_id]['progress'] = 20
        demo_jobs[job_id]['message'] = "Analyzing terrain and identifying buildable zones..."
        
        analyzer = FullSiteAnalyzer(grid_resolution=20.0)
        site_analysis = analyzer.analyze_entire_site(file_path, site_boundary)
        
        logger.info(f"Found {len(site_analysis['buildable_zones'])} buildable zones")
        logger.info(f"Buildable area: {site_analysis['statistics']['total_buildable_area_ha']:.1f} ha")
        
        # Generate scenarios
        demo_jobs[job_id]['progress'] = 50
        demo_jobs[job_id]['message'] = "Generating development scenarios..."
        
        scenario_gen = ScenarioGenerator()
        scenarios = scenario_gen.generate_scenarios(
            site_analysis,
            target_plot_count=target_plot_count
        )
        
        logger.info(f"Generated {len(scenarios)} scenarios")
        
        # Complete
        demo_jobs[job_id]['progress'] = 100
        demo_jobs[job_id]['status'] = 'completed'
        demo_jobs[job_id]['message'] = "Analysis complete!"
        demo_jobs[job_id]['scenarios'] = scenarios
        demo_jobs[job_id]['site_analysis'] = {
            'site_area_ha': site_analysis['site_area_ha'],
            'buildable_area_ha': site_analysis['statistics']['total_buildable_area_ha'],
            'buildable_percentage': site_analysis['statistics']['buildable_percentage'],
            'num_zones': site_analysis['statistics']['num_zones']
        }
        demo_jobs[job_id]['processing_time'] = time.time() - demo_jobs[job_id]['started_at']
        
        logger.info(f"[Job {job_id}] Completed in {demo_jobs[job_id]['processing_time']:.1f}s")
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Failed: {e}", exc_info=True)
        demo_jobs[job_id]['status'] = 'failed'
        demo_jobs[job_id]['error'] = str(e)
        demo_jobs[job_id]['progress'] = 0


def export_scenario_dxf(job_id: str, scenario: Dict):
    """
    Background worker to export scenario to DXF.
    """
    try:
        logger.info(f"[Job {job_id}] Exporting scenario {scenario['scenario_id']} to DXF")
        
        demo_jobs[job_id]['progress'] = 20
        demo_jobs[job_id]['message'] = "Preparing layout data..."
        
        layout = scenario['layout']
        zones = scenario['selected_zones']
        
        # Combine zone geometries
        from shapely.ops import unary_union
        zone_polygons = [z['geometry'] for z in zones]
        combined_boundary = unary_union(zone_polygons)
        
        # Prepare export layout
        demo_jobs[job_id]['progress'] = 50
        demo_jobs[job_id]['message'] = "Generating DXF..."
        
        export_layout = {
            'name': f"Pilot Full Site - Scenario {scenario['scenario_id']}",
            'variant_id': f"fullsite_scenario_{scenario['scenario_id'].lower()}",
            'site_boundary': combined_boundary,
            'buildings': layout['plots'],
            'roads': layout['roads'],
            'green_areas': layout['green_areas'],
            'fire_stations': layout['fire_stations']
        }
        
        # Generate DXF
        dxf_gen = DemoDXFGenerator(output_dir="exports")
        dxf_path = dxf_gen.generate(
            export_layout,
            filename=f"pilot_scenario_{scenario['scenario_id']}.dxf"
        )
        
        # Complete
        demo_jobs[job_id]['progress'] = 100
        demo_jobs[job_id]['status'] = 'completed'
        demo_jobs[job_id]['message'] = "DXF export complete!"
        demo_jobs[job_id]['result'] = {
            'dxf_file': Path(dxf_path).name,
            'download_url': f"/api/demo/download/{Path(dxf_path).name}",
            'scenario_id': scenario['scenario_id'],
            'plot_count': scenario['metrics']['plot_count'],
            'file_size_kb': Path(dxf_path).stat().st_size / 1024
        }
        
        logger.info(f"[Job {job_id}] DXF exported successfully")
        
    except Exception as e:
        logger.error(f"[Job {job_id}] Export failed: {e}", exc_info=True)
        demo_jobs[job_id]['status'] = 'failed'
        demo_jobs[job_id]['error'] = str(e)
        demo_jobs[job_id]['progress'] = 0
