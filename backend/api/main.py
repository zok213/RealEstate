"""
FastAPI Backend for Industrial Park AI Designer.
Provides REST API and WebSocket endpoints for design generation.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import json
import os
import math
import random
import tempfile
import subprocess
from datetime import datetime
from uuid import uuid4

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    settings,
    IEAT_REGULATIONS,
    INDUSTRIAL_PARK_REGULATIONS,
    DEFAULT_REGULATIONS
)
from ai.llm_orchestrator import IndustrialParkLLMOrchestrator
from ai.dxf_analyzer import DXFAnalyzer
from optimization.csp_solver import IndustrialParkCSP, generate_buildings_from_params
from optimization.ga_optimizer import IndustrialParkGA
from design.compliance_checker import ComplianceChecker
from design.enhanced_layout_generator import EnhancedLayoutGenerator
from cad.dxf_generator import DXFGenerator

# Import optimized subdivision endpoint
from api.optimized_subdivision_endpoint import get_router as get_optimized_router

# Import financial endpoints
try:
    from api.financial_endpoints import get_router as get_financial_router
    FINANCIAL_ENDPOINTS_AVAILABLE = True
except Exception as e:
    print(f"⚠️ Could not load financial endpoints: {e}")
    FINANCIAL_ENDPOINTS_AVAILABLE = False

# Import DXF endpoints
try:
    from api.dxf_endpoints import router as dxf_router
    DXF_ENDPOINTS_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Could not load DXF endpoints: {e}")
    DXF_ENDPOINTS_AVAILABLE = False

# Import demo endpoints
try:
    from api.demo_endpoints import get_router as get_demo_router
    DEMO_ENDPOINTS_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Could not load demo endpoints: {e}")
    DEMO_ENDPOINTS_AVAILABLE = False

# Import MVP Auto-Design endpoint
try:
    from api.auto_design_endpoint import get_router as get_auto_design_router
    AUTO_DESIGN_AVAILABLE = True
except Exception as e:
    print(f"[WARN] Could not load auto-design endpoint: {e}")
    AUTO_DESIGN_AVAILABLE = False


# ==================== APP SETUP ====================

app = FastAPI(
    title="Industrial Park AI Designer API",
    description="AI-powered industrial park design with LLM, CSP, and GA optimization",
    version="1.0.0"
)

# CORS configuration
origins = settings.cors_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include optimized subdivision router
try:
    optimized_router = get_optimized_router()
    app.include_router(optimized_router, tags=["Optimized Subdivision"])
    print("[OK] Optimized subdivision algorithms loaded successfully")
except Exception as e:
    print(f"[WARN] Could not load optimized algorithms: {e}")

# Include financial analysis router
if FINANCIAL_ENDPOINTS_AVAILABLE:
    try:
        financial_router = get_financial_router()
        app.include_router(financial_router, tags=["Financial Analysis"])
        print("[OK] Financial analysis endpoints loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not include financial router: {e}")

# Include DXF endpoints router
if DXF_ENDPOINTS_AVAILABLE:
    try:
        app.include_router(dxf_router, tags=["DXF Georeferencing"])
        print("[OK] DXF georeferencing endpoints loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not include DXF router: {e}")

# Include demo endpoints router
if DEMO_ENDPOINTS_AVAILABLE:
    try:
        demo_router = get_demo_router()
        app.include_router(demo_router, prefix="/api/demo", tags=["Demo - Pilot Processing"])
        print("[OK] Demo endpoints loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not include demo router: {e}")

# Include MVP Auto-Design router
if AUTO_DESIGN_AVAILABLE:
    try:
        auto_design_router = get_auto_design_router()
        app.include_router(auto_design_router, tags=["MVP Auto-Design"])
        print("[OK] MVP Auto-Design endpoint loaded successfully")
    except Exception as e:
        print(f"[WARN] Could not include auto-design router: {e}")

# In-memory storage (replace with database in production)
projects: Dict[str, Dict] = {}
design_jobs: Dict[str, Dict] = {}
chat_sessions: Dict[str, IndustrialParkLLMOrchestrator] = {}


# ==================== DATA MODELS ====================

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    site_area_ha: float = Field(..., gt=0, description="Site area in hectares")
    description: Optional[str] = None


class ChatMessage(BaseModel):
    project_id: str
    message: str


class DesignGenerationRequest(BaseModel):
    project_id: str
    parameters: Optional[Dict] = None
    use_chat_params: bool = True


class ExportRequest(BaseModel):
    project_id: str
    variant_id: str
    format: str = Field("dxf", pattern="^(dxf|json|pdf)$")


# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    """API health check and info."""
    return {
        "name": "Industrial Park AI Designer API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "projects": "/api/projects",
            "chat": "/api/chat/{project_id}",
            "designs": "/api/designs"
        }
    }


@app.post("/api/projects/new")
async def create_new_project(request: ProjectCreate):
    """Create new design project."""
    project_id = str(uuid4())
    
    # Calculate site dimensions (assume rectangular)
    total_area_m2 = request.site_area_ha * 10000
    width = math.sqrt(total_area_m2 * 1.5)  # 1.5:1 aspect ratio
    height = total_area_m2 / width
    
    project = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "site": {
            "area_ha": request.site_area_ha,
            "total_area_m2": total_area_m2,
            "width": width,
            "height": height
        },
        "created_at": datetime.now().isoformat(),
        "variants": [],
        "chat_history": []
    }
    
    projects[project_id] = project
    
    # Initialize chat session
    chat_sessions[project_id] = IndustrialParkLLMOrchestrator()
    
    return {"project_id": project_id, "project": project}


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get project details."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return projects[project_id]


@app.get("/api/projects")
async def list_projects():
    """List all projects."""
    return {"projects": list(projects.values())}


@app.post("/api/upload-dxf")
async def upload_and_analyze_dxf(
    file: UploadFile = File(...),
    project_id: Optional[str] = None
):
    """
    Upload DXF file và tự động phân tích để đưa ra gợi ý thiết kế.
    
    Nếu có project_id, sẽ inject DXF context vào chat session.
    
    Returns:
        - Thông tin khu đất (diện tích, kích thước)
        - Gợi ý phân bổ công năng theo IEAT
        - Câu hỏi hỗ trợ để thu thập thêm yêu cầu
        - Prompt mẫu để user có thể sử dụng ngay
        - AI greeting message với context từ DXF
    """
    # Validate file type
    if not (file.filename.lower().endswith('.dxf') or file.filename.lower().endswith('.dwg')):
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ file DXF/DWG. Vui lòng upload file .dxf hoặc .dwg"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix='.dxf'
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Analyze DXF
        analyzer = DXFAnalyzer(tmp_path)
        analysis = analyzer.analyze()
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if not analysis.get("success"):
            raise HTTPException(
                status_code=400,
                detail=analysis.get("error", "Không thể phân tích file DXF")
            )
        
        # Nếu có project_id, inject DXF context vào chat
        ai_greeting = None
        if project_id:
            # Get or create chat session
            if project_id not in chat_sessions:
                chat_sessions[project_id] = IndustrialParkLLMOrchestrator()
            
            orchestrator = chat_sessions[project_id]
            ai_greeting = orchestrator.inject_dxf_context(analysis)
            
            # Update project with DXF info
            if project_id in projects:
                projects[project_id]["site"]["area_ha"] = (
                    analysis["site_info"]["area_ha"]
                )
                projects[project_id]["site"]["boundary"] = (
                    analysis.get("boundary_points", [])
                )
        
        # Format response với gợi ý thông minh
        return {
            "success": True,
            "filename": file.filename,
            "site_info": analysis["site_info"],
            "suggestions": analysis["suggestions"],
            "questions": analysis["questions"],
            "sample_prompts": analysis["sample_prompts"],
            "ai_greeting": ai_greeting,
            "next_steps": [
                "1. Trả lời các câu hỏi để AI hiểu rõ hơn yêu cầu",
                "2. Hoặc copy một prompt mẫu và chỉnh sửa",
                "3. Gửi prompt để AI tạo thiết kế tự động"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý file: {str(e)}"
        )


@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    """
    Send chat message and get AI response.
    Use this for HTTP-based chat (alternative to WebSocket).
    """
    project_id = request.project_id
    
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get or create chat session
    if project_id not in chat_sessions:
        chat_sessions[project_id] = IndustrialParkLLMOrchestrator()
    
    orchestrator = chat_sessions[project_id]
    
    try:
        # Get LLM response
        response = orchestrator.chat(request.message)
        
        # Store in project history
        projects[project_id]["chat_history"].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        projects[project_id]["chat_history"].append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response.content,
            "extracted_params": response.extracted_params,
            "ready_for_design": response.ready_for_generation,
            "model_used": response.model_used
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/api/chat/{project_id}")
async def websocket_chat(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time chat.
    User types requirements → AI responds → Parameters extracted → Ready for design
    """
    await websocket.accept()
    
    if project_id not in projects:
        await websocket.send_json({"error": "Project not found"})
        await websocket.close()
        return
    
    # Get or create chat session
    if project_id not in chat_sessions:
        chat_sessions[project_id] = IndustrialParkLLMOrchestrator()
    
    orchestrator = chat_sessions[project_id]
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get('text', message_data.get('message', ''))
            
            # Get LLM response
            response = orchestrator.chat(user_message)
            
            # Send response
            await websocket.send_json({
                "response": response.content,
                "extracted_params": response.extracted_params,
                "ready_for_design": response.ready_for_generation,
                "model_used": response.model_used
            })
            
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for project {project_id}")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
    finally:
        await websocket.close()


@app.post("/api/designs/generate")
async def generate_designs(
    request: DesignGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger design variant generation.
    Runs CSP + GA in background, returns job ID for tracking.
    """
    project_id = request.project_id
    
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[project_id]
    
    # Get parameters
    if request.use_chat_params and project_id in chat_sessions:
        orchestrator = chat_sessions[project_id]
        params = orchestrator.get_design_params_for_optimizer()
    else:
        params = request.parameters or {}
    
    # Merge with project site info
    params["total_area_ha"] = project["site"]["area_ha"]
    params["total_area_m2"] = project["site"]["total_area_m2"]
    params["width"] = project["site"]["width"]
    params["height"] = project["site"]["height"]
    
    # Create job
    job_id = str(uuid4())
    design_jobs[job_id] = {
        "id": job_id,
        "project_id": project_id,
        "status": "queued",
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "variants": []
    }
    
    # Run in background
    background_tasks.add_task(
        design_generation_worker,
        job_id,
        project_id,
        params
    )
    
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/designs/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get design generation job status."""
    if job_id not in design_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return design_jobs[job_id]


@app.get("/api/designs/{project_id}/variants")
async def get_design_variants(project_id: str):
    """Retrieve generated variants for a project."""
    if project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return {"variants": projects[project_id].get("variants", [])}


@app.post("/api/export")
async def export_design(request: ExportRequest):
    """Export design in specified format."""
    if request.project_id not in projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = projects[request.project_id]
    variants = project.get("variants", [])
    
    # Find variant
    variant = None
    for v in variants:
        if v.get("id") == request.variant_id:
            variant = v
            break
    
    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    
    if request.format == "dxf":
        # Generate DXF
        generator = DXFGenerator("exports")
        layout = variant.get("layout", {})
        layout["name"] = project.get("name", "Industrial Park")
        layout["variant_id"] = request.variant_id
        
        filepath = generator.generate(layout)
        
        return {
            "format": "dxf",
            "filename": os.path.basename(filepath),
            "download_url": f"/api/files/{os.path.basename(filepath)}"
        }
    
    elif request.format == "json":
        return variant
    
    else:
        raise HTTPException(status_code=400, detail=f"Format {request.format} not supported yet")


@app.get("/api/files/{filename}")
async def download_file(filename: str):
    """Download generated file."""
    filepath = os.path.join("exports", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        filepath,
        media_type="application/octet-stream",
        filename=filename
    )


@app.post("/api/convert/dwg-to-dxf")
async def convert_dwg_to_dxf(file: UploadFile = File(...)):
    """
    Convert DWG file to DXF format using ezdxf.
    Falls back to instructions if conversion fails.
    """
    try:
        # Try using ezdxf
        import ezdxf
        
        # Save uploaded file to temp
        tmp_dwg = tempfile.NamedTemporaryFile(
            delete=False, suffix='.dwg'
        )
        content = await file.read()
        tmp_dwg.write(content)
        tmp_dwg.close()
        tmp_dwg_path = tmp_dwg.name
        
        try:
            # Try to read DWG directly with ezdxf
            doc = ezdxf.readfile(tmp_dwg_path)
            
            # Convert to DXF in memory
            dxf_content = doc.write_to_string()
            
            # Cleanup
            os.unlink(tmp_dwg_path)
            
            # Return DXF content
            dxf_filename = file.filename.replace('.dwg', '.dxf')
            return PlainTextResponse(
                content=dxf_content,
                headers={
                    "Content-Disposition": (
                        f"attachment; filename={dxf_filename}"
                    ),
                    "Content-Type": "application/dxf"
                }
            )
        except Exception as e:
            # Cleanup temp file
            if os.path.exists(tmp_dwg_path):
                os.unlink(tmp_dwg_path)
            raise e
            
    except Exception as e:
        # Fallback to manual instructions
        error_msg = str(e)[:100]
        return JSONResponse(
            status_code=501,
            content={
                "error": "DWG conversion not fully supported",
                "reason": (
                    f"ezdxf không hỗ trợ phiên bản DWG này: "
                    f"{error_msg}"
                ),
                "message": (
                    "Vui lòng export file DWG sang DXF "
                    "trước khi upload."
                ),
                "instructions": [
                    "1. Mở file DWG trong AutoCAD/LibreCAD",
                    "2. Chọn File > Save As",
                    "3. Chọn format 'AutoCAD 2018 DXF'",
                    "4. Upload file DXF đã convert"
                ],
                "auto_conversion": (
                    "Hệ thống đã thử auto-convert nhưng "
                    "không thành công với file này."
                ),
                "alternative": (
                    "💡 Dùng online: "
                    "https://convertio.co/vn/dwg-dxf/ (miễn phí)"
                )
            }
        )


# ==================== BACKGROUND WORKERS ====================

async def design_generation_worker(job_id: str, project_id: str, params: Dict):
    """Background worker for design generation with progress updates."""
    import time
    start_time = time.time()
    timings = {}  # Track timing for each step
    
    try:
        design_jobs[job_id]["status"] = "running"
        design_jobs[job_id]["progress"] = 5
        design_jobs[job_id]["current_step"] = "Đang phân tích yêu cầu..."
        
        await asyncio.sleep(0.5)  # Allow UI to update
        
        # 1. Parse parameters and generate buildings
        step_start = time.time()
        design_jobs[job_id]["progress"] = 10
        design_jobs[job_id]["current_step"] = "Tạo danh sách nhà máy và tòa nhà..."
        
        site_params = {
            "total_area_m2": params.get("total_area_m2", 500000),
            "width": params.get("width", 1000),
            "height": params.get("height", 500),
            "terrain_strategy": params.get("terrain_strategy", "balanced_cut_fill"),
            "has_topography": params.get("has_topography", False),
            "terrain": params.get("terrain", {})
        }
        
        buildings = generate_buildings_from_params(params)
        timings["building_generation"] = time.time() - step_start
        design_jobs[job_id]["progress"] = 15
        design_jobs[job_id]["current_step"] = f"✓ Đã tạo {len(buildings)} tòa nhà ({timings['building_generation']:.1f}s)"
        print(f"[Design] Generated {len(buildings)} buildings in {timings['building_generation']:.2f}s")
        
        await asyncio.sleep(0.5)
        
        # 2. Run CSP to get feasible solutions
        step_start = time.time()
        design_jobs[job_id]["progress"] = 20
        design_jobs[job_id]["current_step"] = "Đang giải bài toán ràng buộc CSP..."
        
        csp_solver = IndustrialParkCSP(site_params)
        csp_solver.set_buildings(buildings)
        csp_solver.add_building_variables()
        csp_solver.add_no_overlap_constraint()
        csp_solver.add_boundary_constraint()
        
        design_jobs[job_id]["progress"] = 30
        design_jobs[job_id]["current_step"] = "Tìm kiếm layout khả thi..."
        
        feasible_layouts = csp_solver.solve(max_solutions=3)
        timings["csp_solver"] = time.time() - step_start
        design_jobs[job_id]["progress"] = 40
        design_jobs[job_id]["current_step"] = f"✓ Tìm được {len(feasible_layouts)} layout khả thi ({timings['csp_solver']:.1f}s)"
        print(f"[Design] CSP solved in {timings['csp_solver']:.2f}s, found {len(feasible_layouts)} layouts")
        
        await asyncio.sleep(0.5)
        
        # 3. Run GA for optimization (reduced for speed)
        step_start = time.time()
        design_jobs[job_id]["progress"] = 45
        design_jobs[job_id]["current_step"] = "Khởi tạo thuật toán di truyền GA..."
        
        ga_optimizer = IndustrialParkGA(site_params, feasible_layouts=feasible_layouts)
        ga_optimizer.set_buildings(buildings)
        
        design_jobs[job_id]["progress"] = 50
        design_jobs[job_id]["current_step"] = "Đang tối ưu hóa với GA (10 thế hệ)..."
        print("[Design] Starting GA optimization...")
        
        # Reduced to 10/10 for faster generation (~10 seconds)
        optimized_variants = ga_optimizer.optimize(population_size=10, generations=10)
        timings["ga_optimizer"] = time.time() - step_start
        design_jobs[job_id]["progress"] = 70
        design_jobs[job_id]["current_step"] = f"✓ Tối ưu xong! Có {len(optimized_variants)} phương án ({timings['ga_optimizer']:.1f}s)"
        print(f"[Design] GA optimization complete in {timings['ga_optimizer']:.2f}s, {len(optimized_variants)} variants")
        
        await asyncio.sleep(0.5)
        
        # 4. Check compliance for each variant
        step_start = time.time()
        design_jobs[job_id]["progress"] = 75
        design_jobs[job_id]["current_step"] = (
            "Kiểm tra tuân thủ IEAT Thailand..."
        )
        
        compliance_checker = ComplianceChecker()
        
        results = []
        for i, (layout, fitness_scores) in enumerate(optimized_variants[:5]):
            design_jobs[job_id]["progress"] = 75 + (i * 3)
            design_jobs[job_id]["current_step"] = f"Phân tích phương án {i+1}/5..."
            
            layout["site"] = site_params
            layout["worker_capacity"] = params.get("worker_capacity", 3000)
            
            compliance_report = compliance_checker.check_layout(layout)
            
            variant = {
                "id": str(uuid4()),
                "name": f"Variant {i+1}",
                "layout": layout,
                "fitness_scores": {
                    "road_efficiency": round(fitness_scores[0], 2),
                    "worker_flow": round(fitness_scores[1], 2),
                    "green_ratio": round(fitness_scores[2], 2),
                    "total": round(sum(fitness_scores), 2)
                },
                "compliance": compliance_report,
                "generated_at": datetime.now().isoformat()
            }
            results.append(variant)
        
        timings["compliance_check"] = time.time() - step_start
        design_jobs[job_id]["progress"] = 90
        design_jobs[job_id]["current_step"] = "Lưu kết quả..."
        
        # 5. Save to project
        projects[project_id]["variants"] = results
        
        # 6. Calculate total time and update job status
        total_time = time.time() - start_time
        timings["total"] = total_time
        
        design_jobs[job_id]["status"] = "completed"
        design_jobs[job_id]["progress"] = 100
        design_jobs[job_id]["current_step"] = f"✓ Hoàn thành trong {total_time:.1f}s!"
        design_jobs[job_id]["variants"] = results
        design_jobs[job_id]["timings"] = timings
        design_jobs[job_id]["completed_at"] = datetime.now().isoformat()
        
        print(f"[Design] Job {job_id} completed in {total_time:.2f}s")
        print(f"[Design] Timings: Buildings={timings.get('building_generation',0):.2f}s, CSP={timings.get('csp_solver',0):.2f}s, GA={timings.get('ga_optimizer',0):.2f}s, Compliance={timings.get('compliance_check',0):.2f}s")
        print(f"[Design] Generated {len(results)} variants successfully")
        
    except Exception as e:
        design_jobs[job_id]["status"] = "failed"
        design_jobs[job_id]["error"] = str(e)
        design_jobs[job_id]["current_step"] = f"❌ Lỗi: {str(e)}"
        print(f"Design generation error: {e}")
        import traceback
        traceback.print_exc()


# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
