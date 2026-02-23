"""
MVP Auto-Design Endpoint

Automatically generates industrial park layout from DXF boundary file.
No LLM, no user input - pure regulation-based design.

Workflow:
1. Upload DWG/DXF file
2. Analyze site boundary and area
3. Apply IEAT default regulations based on site size
4. Generate buildings from regulations
5. CSP solve for feasible placement
6. GA optimize for best layout
7. Check compliance
8. Generate output DXF

NOTE: Uses lazy imports for fast startup - heavy modules loaded on first request.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Optional, TYPE_CHECKING
import tempfile
import os
import math
import logging
from datetime import datetime

# Path setup for imports
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# LAZY IMPORTS - These are imported inside functions to speed up startup
# from ai.dxf_analyzer import DXFAnalyzer
# from optimization.csp_solver import IndustrialParkCSP, generate_buildings_from_params
# from optimization.ga_optimizer import IndustrialParkGA
# from design.compliance_checker import ComplianceChecker
# from cad.dxf_generator import DXFGenerator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["MVP Auto-Design"])


def generate_default_params(area_ha: float) -> Dict:
    """
    Generate default design parameters based on site area.
    Follows IEAT Thailand regulations with sensible defaults.
    
    Args:
        area_ha: Site area in hectares
        
    Returns:
        Design parameters dict
    """
    # Industry mix based on site size
    if area_ha < 20:
        # Small site: Focus on light manufacturing
        industry_focus = [
            {"type": "light_manufacturing", "percentage": 70, "count": max(3, int(area_ha * 0.5))},
            {"type": "warehouse", "percentage": 20, "count": max(1, int(area_ha * 0.15))},
            {"type": "support_offices", "percentage": 10, "count": 1}
        ]
        green_ratio = 0.15
        road_width = 20
    elif area_ha < 50:
        # Medium site: Balanced mix
        industry_focus = [
            {"type": "light_manufacturing", "percentage": 50, "count": max(5, int(area_ha * 0.3))},
            {"type": "medium_manufacturing", "percentage": 20, "count": max(2, int(area_ha * 0.1))},
            {"type": "warehouse", "percentage": 20, "count": max(2, int(area_ha * 0.15))},
            {"type": "support_offices", "percentage": 10, "count": 2}
        ]
        green_ratio = 0.18
        road_width = 25
    else:
        # Large site: Diverse mix
        industry_focus = [
            {"type": "light_manufacturing", "percentage": 40, "count": max(8, int(area_ha * 0.2))},
            {"type": "medium_manufacturing", "percentage": 25, "count": max(4, int(area_ha * 0.08))},
            {"type": "heavy_manufacturing", "percentage": 10, "count": max(2, int(area_ha * 0.03))},
            {"type": "warehouse", "percentage": 15, "count": max(3, int(area_ha * 0.08))},
            {"type": "logistics", "percentage": 5, "count": max(1, int(area_ha * 0.02))},
            {"type": "support_offices", "percentage": 5, "count": 3}
        ]
        green_ratio = 0.20
        road_width = 30
    
    return {
        "total_area_ha": area_ha,
        "total_area_m2": area_ha * 10000,
        "industry_focus": industry_focus,
        "green_ratio": green_ratio,
        "road_width": road_width,
        "min_plot_size_m2": 1600,
        "plot_ratio": 1.5,  # width:depth
        "fire_safety_distance_m": 15,
        "boundary_buffer_m": 20,
        "retention_pond_ratio": 20,  # 1 rai pond per 20 rai gross
        "worker_capacity": int(area_ha * 50),  # ~50 workers per ha
        "regulations": "IEAT_Thailand"
    }


def generate_site_params(dxf_analysis: Dict) -> Dict:
    """
    Generate site parameters from DXF analysis result.
    
    Args:
        dxf_analysis: Result from DXFAnalyzer.analyze()
        
    Returns:
        Site parameters for CSP/GA
    """
    site_info = dxf_analysis.get("site_info", {})
    dimensions = dxf_analysis.get("dimensions", {})
    
    return {
        "width": dimensions.get("width", 500),
        "height": dimensions.get("height", 400),
        "total_area_m2": site_info.get("area_m2", 200000),
        "boundary_points": dxf_analysis.get("boundary_points", [])
    }


def generate_layout_summary(layout: Dict, compliance: Dict) -> Dict:
    """
    Generate summary statistics for the layout.
    
    Args:
        layout: Generated layout
        compliance: Compliance check result
        
    Returns:
        Summary dict
    """
    buildings = layout.get("buildings", [])
    site = layout.get("site", {})
    
    # Count by type
    building_counts = {}
    total_building_area = 0
    for b in buildings:
        btype = b.get("type", "other")
        building_counts[btype] = building_counts.get(btype, 0) + 1
        total_building_area += b.get("width", 0) * b.get("height", 0)
    
    total_area = site.get("total_area_m2", 1)
    
    return {
        "total_buildings": len(buildings),
        "building_counts_by_type": building_counts,
        "total_building_area_m2": round(total_building_area, 2),
        "building_area_percent": round(100 * total_building_area / total_area, 1),
        "estimated_green_area_percent": round(100 * (1 - total_building_area / total_area - 0.15), 1),
        "estimated_road_area_percent": 15,
        "compliance_status": compliance.get("status", "UNKNOWN"),
        "compliance_percent": compliance.get("overall_compliance_percent", 0)
    }


@router.post("/auto-design")
async def auto_design_from_dxf(
    file: UploadFile = File(...),
    output_format: str = "json"
):
    """
    MVP: Auto-generate industrial park layout from DXF/DWG boundary.
    
    No LLM, no user input - pure regulation-based design.
    
    Args:
        file: DXF or DWG file containing site boundary
        output_format: "json" or "dxf" (default: json)
        
    Returns:
        - site_info: Analyzed site information
        - design_params: Parameters used for design
        - layout: Generated layout with buildings, roads
        - layout_summary: Statistics
        - compliance: IEAT compliance report
        - dxf_download_url: (if output_format="dxf") URL to download DXF
    """
    logger.info(f"[MVP Auto-Design] Processing file: {file.filename}")
    
    # Validate file type
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.dxf') or filename_lower.endswith('.dwg')):
        raise HTTPException(
            status_code=400,
            detail="Chỉ hỗ trợ file DXF hoặc DWG. Vui lòng upload đúng định dạng."
        )
    
    try:
        # ==================== STEP 1: Save uploaded file ====================
        suffix = '.dxf' if filename_lower.endswith('.dxf') else '.dwg'
        
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"[MVP Auto-Design] Saved temp file: {tmp_path}")
        
        # ==================== STEP 2: Handle DWG conversion ====================
        if suffix == '.dwg':
            # Try to convert DWG to DXF using ezdxf
            try:
                import ezdxf
                doc = ezdxf.readfile(tmp_path)
                
                # Save as DXF
                dxf_path = tmp_path.replace('.dwg', '.dxf')
                doc.saveas(dxf_path)
                
                # Update path
                os.unlink(tmp_path)
                tmp_path = dxf_path
                logger.info(f"[MVP Auto-Design] Converted DWG to DXF: {dxf_path}")
                
            except Exception as e:
                os.unlink(tmp_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"Không thể đọc file DWG. Vui lòng convert sang DXF trước. Lỗi: {str(e)[:100]}"
                )
        
        # ==================== LAZY IMPORTS (for fast startup) ====================
        from ai.dxf_analyzer import DXFAnalyzer
        from optimization.csp_solver import IndustrialParkCSP, generate_buildings_from_params
        from optimization.ga_optimizer import IndustrialParkGA
        from design.compliance_checker import ComplianceChecker
        from cad.dxf_generator import DXFGenerator
        
        # ==================== STEP 3: Analyze DXF ====================
        logger.info("[MVP Auto-Design] Step 3: Analyzing DXF...")
        
        analyzer = DXFAnalyzer(tmp_path)
        dxf_analysis = analyzer.analyze()
        
        if not dxf_analysis.get("success", False):
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=400,
                detail=f"Không thể phân tích file DXF: {dxf_analysis.get('error', 'Unknown error')}"
            )
        
        site_info = dxf_analysis.get("site_info", {})
        area_ha = site_info.get("area_ha", 10)
        
        logger.info(f"[MVP Auto-Design] Site area: {area_ha:.2f} ha")
        
        # ==================== STEP 4: Generate default params ====================
        logger.info("[MVP Auto-Design] Step 4: Generating default parameters...")
        
        default_params = generate_default_params(area_ha)
        site_params = generate_site_params(dxf_analysis)
        
        # Merge site dimensions into default params
        default_params["width"] = site_params["width"]
        default_params["height"] = site_params["height"]
        
        logger.info(f"[MVP Auto-Design] Industry focus: {len(default_params['industry_focus'])} types")
        
        # ==================== STEP 5: Generate buildings ====================
        logger.info("[MVP Auto-Design] Step 5: Generating buildings...")
        
        buildings = generate_buildings_from_params(default_params)
        logger.info(f"[MVP Auto-Design] Generated {len(buildings)} buildings")
        
        # ==================== STEP 6: CSP Solve ====================
        logger.info("[MVP Auto-Design] Step 6: Running CSP solver...")
        
        csp = IndustrialParkCSP(site_params)
        csp.set_buildings(buildings)
        csp.add_building_variables()
        csp.add_no_overlap_constraint()
        csp.add_boundary_constraint()
        
        feasible_layouts = csp.solve(max_solutions=3)
        logger.info(f"[MVP Auto-Design] CSP found {len(feasible_layouts)} feasible layouts")
        
        if not feasible_layouts:
            os.unlink(tmp_path)
            raise HTTPException(
                status_code=500,
                detail="Không tìm được layout khả thi. Có thể diện tích quá nhỏ cho số lượng building."
            )
        
        # ==================== STEP 7: GA Optimize ====================
        logger.info("[MVP Auto-Design] Step 7: Running GA optimizer...")
        
        ga = IndustrialParkGA(site_params, feasible_layouts=feasible_layouts)
        ga.set_buildings(buildings)
        
        # Run with reduced iterations for speed
        optimized_variants = ga.optimize(population_size=10, generations=10)
        
        if not optimized_variants:
            # Use first feasible as fallback
            best_layout = feasible_layouts[0]
            fitness_scores = (5.0, 5.0, 5.0)
        else:
            best_layout, fitness_scores = optimized_variants[0]
        
        logger.info(f"[MVP Auto-Design] GA complete. Best scores: {fitness_scores}")
        
        # Add site info to layout
        best_layout["site"] = site_params
        best_layout["worker_capacity"] = default_params.get("worker_capacity", 1000)
        
        # ==================== STEP 8: Compliance check ====================
        logger.info("[MVP Auto-Design] Step 8: Checking IEAT compliance...")
        
        checker = ComplianceChecker(standard="ieat_thailand")
        compliance_report = checker.check_layout(best_layout)
        
        logger.info(f"[MVP Auto-Design] Compliance: {compliance_report.get('status', 'UNKNOWN')}")
        
        # ==================== STEP 9: Generate output ====================
        result = {
            "success": True,
            "filename": file.filename,
            "generated_at": datetime.now().isoformat(),
            "site_info": site_info,
            "design_params": {
                "total_area_ha": area_ha,
                "industry_focus": default_params["industry_focus"],
                "green_ratio_target": default_params["green_ratio"],
                "road_width_m": default_params["road_width"],
                "regulations_used": "IEAT Thailand"
            },
            "layout": {
                "buildings": best_layout.get("buildings", []),
                "site_dimensions": {
                    "width_m": site_params["width"],
                    "height_m": site_params["height"]
                },
                "fitness_scores": {
                    "road_efficiency": round(fitness_scores[0], 2),
                    "worker_flow": round(fitness_scores[1], 2),
                    "green_ratio": round(fitness_scores[2], 2),
                    "total": round(sum(fitness_scores), 2)
                }
            },
            "layout_summary": generate_layout_summary(best_layout, compliance_report),
            "compliance": compliance_report
        }
        
        # ==================== STEP 10: Generate DXF if requested ====================
        if output_format.lower() == "dxf":
            logger.info("[MVP Auto-Design] Step 10: Generating output DXF...")
            
            generator = DXFGenerator("exports")
            
            # Prepare layout for DXF generation
            dxf_layout = best_layout.copy()
            dxf_layout["name"] = f"AutoDesign_{file.filename.replace('.dxf', '').replace('.dwg', '')}"
            dxf_layout["variant_id"] = "mvp_v1"
            
            dxf_filepath = generator.generate(dxf_layout)
            dxf_filename = os.path.basename(dxf_filepath)
            
            result["dxf_download_url"] = f"/api/files/{dxf_filename}"
            result["dxf_filename"] = dxf_filename
            
            logger.info(f"[MVP Auto-Design] DXF generated: {dxf_filename}")
        
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        logger.info("[MVP Auto-Design] Complete!")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[MVP Auto-Design] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Cleanup
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý: {str(e)}"
        )


@router.get("/auto-design/defaults")
async def get_default_params(area_ha: float = 30.0):
    """
    Get default design parameters for a given site area.
    Useful for understanding what parameters will be used.
    
    Args:
        area_ha: Site area in hectares
        
    Returns:
        Default parameters that would be applied
    """
    return {
        "area_ha": area_ha,
        "default_params": generate_default_params(area_ha),
        "regulations": "IEAT Thailand",
        "notes": [
            "Các tham số được tạo tự động dựa trên diện tích khu đất",
            "Industry mix thay đổi theo quy mô: nhỏ (<20ha), vừa (20-50ha), lớn (>50ha)",
            "Tuân thủ quy chuẩn IEAT Thailand về tỷ lệ đất, green space, road width"
        ]
    }


# Export router for inclusion in main app
def get_router():
    return router
