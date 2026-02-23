"""
DXF Analyzer - Tự động đọc và phân tích file DXF để đưa ra gợi ý thiết kế.
"""
import ezdxf
from typing import Dict, List, Tuple, Optional
import math
from pathlib import Path


class DXFAnalyzer:
    """Tự động phân tích file DXF và tạo gợi ý thiết kế thông minh."""
    
    def __init__(self, dxf_path: str):
        self.dxf_path = dxf_path
        self.doc = None
        self.site_info = {}
        
    def analyze(self) -> Dict:
        """
        Phân tích file DXF và trả về thông tin chi tiết.
        
        Returns:
            {
                "area_ha": 50.5,
                "area_m2": 505000,
                "dimensions": {"width": 700, "height": 720},
                "boundary_points": [...],
                "suggested_buildings": {...},
                "questions": [...],
                "prompts": [...]
            }
        """
        try:
            # Try to read as DXF or DWG
            try:
                self.doc = ezdxf.readfile(self.dxf_path)
            except ezdxf.DXFStructureError as e:
                # If DWG, ezdxf can still read some versions
                if 'not a DXF file' in str(e):
                    # Try reading as DWG (ezdxf supports DWG R13-R2018)
                    try:
                        self.doc = ezdxf.readfile(self.dxf_path)
                    except Exception as dwg_error:
                        return {
                            "success": False,
                            "error": (
                                f"Không thể đọc file DWG: {str(dwg_error)}. "
                                "ezdxf chỉ hỗ trợ DWG R13-R2018. "
                                "Vui lòng export sang DXF (AutoCAD 2018 format)."
                            ),
                            "suggestions": [
                                "1. Mở file DWG trong AutoCAD/LibreCAD",
                                "2. Chọn File > Save As",
                                "3. Chọn format 'AutoCAD 2018 DXF'",
                                "4. Upload file DXF đã convert"
                            ]
                        }
                else:
                    raise
            
            msp = self.doc.modelspace()
            
            # 1. Tìm boundary (đường biên khu đất)
            boundary = self._find_boundary(msp)
            
            if not boundary:
                return {
                    "error": "Không tìm thấy boundary trong file DXF",
                    "suggestions": [
                        "Đảm bảo file DXF có LWPOLYLINE hoặc POLYLINE",
                        "Kiểm tra layer 'BOUNDARY' hoặc 'SITE'"
                    ]
                }
            
            # 2. Tính diện tích
            area_m2 = self._calculate_area(boundary)
            area_ha = area_m2 / 10000
            
            # 3. Tính kích thước
            dimensions = self._get_dimensions(boundary)
            
            # 4. Phân tích địa hình (nếu có)
            terrain_info = self._analyze_terrain(msp)
            
            # 5. Tạo gợi ý thiết kế dựa trên diện tích
            suggestions = self._generate_suggestions(area_ha, dimensions)
            
            # 6. Tạo câu hỏi hỗ trợ
            questions = self._generate_questions(area_ha, terrain_info)
            
            # 7. Tạo prompt mẫu
            sample_prompts = self._generate_sample_prompts(area_ha, dimensions)
            
            return {
                "success": True,
                "site_info": {
                    "area_ha": round(area_ha, 2),
                    "area_m2": round(area_m2, 0),
                    "area_rai": round(area_ha * 6.25, 2),  # Thailand unit
                    "dimensions": {
                        "width_m": round(dimensions["width"], 0),
                        "height_m": round(dimensions["height"], 0),
                        "perimeter_m": round(dimensions["perimeter"], 0)
                    },
                    "boundary_points_count": len(boundary),
                    "terrain": terrain_info
                },
                "suggestions": suggestions,
                "questions": questions,
                "sample_prompts": sample_prompts,
                "boundary_points": boundary[:10]  # First 10 points for preview
            }
            
        except Exception as e:
            return {
                "error": f"Lỗi phân tích DXF: {str(e)}",
                "suggestions": [
                    "Kiểm tra định dạng file DXF (AutoCAD R12-R2018)",
                    "Đảm bảo file không bị corrupt"
                ]
            }
    
    def _find_boundary(self, msp) -> Optional[List[Tuple[float, float]]]:
        """Tìm đường biên lớn nhất trong file DXF."""
        polylines = []
        
        for entity in msp:
            if entity.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
                points = list(entity.get_points())
                if len(points) > 2:
                    area = self._calculate_area(points)
                    polylines.append((area, points))
        
        if not polylines:
            return None
        
        # Lấy polyline có diện tích lớn nhất (boundary chính)
        polylines.sort(key=lambda x: x[0], reverse=True)
        return polylines[0][1]
    
    def _calculate_area(self, points: List[Tuple[float, float]]) -> float:
        """Tính diện tích bằng công thức Shoelace."""
        n = len(points)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += points[i][0] * points[j][1]
            area -= points[j][0] * points[i][1]
        return abs(area) / 2.0
    
    def _get_dimensions(self, points: List[Tuple[float, float]]) -> Dict:
        """Tính kích thước khu đất."""
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        
        # Tính chu vi
        perimeter = 0
        for i in range(len(points)):
            j = (i + 1) % len(points)
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]
            perimeter += math.sqrt(dx*dx + dy*dy)
        
        return {
            "width": width,
            "height": height,
            "perimeter": perimeter,
            "aspect_ratio": width / height if height > 0 else 1
        }
    
    def _analyze_terrain(self, msp) -> Dict:
        """Phân tích địa hình từ contour lines."""
        contours = []
        for entity in msp:
            if entity.dxftype() in ['LINE', 'ARC']:
                layer = entity.dxf.layer.upper()
                if 'CONTOUR' in layer or 'TOPO' in layer:
                    contours.append(entity)
        
        return {
            "has_topography": len(contours) > 0,
            "contour_count": len(contours)
        }
    
    def _generate_suggestions(self, area_ha: float, dimensions: Dict) -> Dict:
        """Tạo gợi ý thiết kế dựa trên IEAT standards."""
        
        # IEAT land use ratios
        salable_area = area_ha * 0.77  # 77% salable (IEAT min 75%)
        green_area = area_ha * 0.12    # 12% green (IEAT min 10%)
        utility_area = area_ha * 0.11  # 11% utility (roads, infrastructure)
        
        # Estimated building capacity
        avg_plot_size_ha = 0.5  # 5,000 m² per plot
        estimated_plots = int(salable_area / avg_plot_size_ha)
        
        # Building suggestions based on area
        if area_ha < 10:
            focus = "small_industrial"
            building_types = "Light manufacturing (5-8 buildings)"
        elif area_ha < 50:
            focus = "mixed_industrial"
            building_types = "Mixed: 60/%/ industrial, 30/%/ warehouse, 10/%/ logistics"
        elif area_ha < 200:
            focus = "large_industrial_park"
            building_types = "Large scale: Multiple zones with specialized areas"
        else:
            focus = "mega_industrial_estate"
            building_types = "Mega project: Multiple phases, mixed-use development"
        
        return {
            "project_scale": focus,
            "estimated_plots": estimated_plots,
            "land_use_breakdown": {
                "salable_area_ha": round(salable_area, 2),
                "green_area_ha": round(green_area, 2),
                "utility_area_ha": round(utility_area, 2),
                "notes": "Theo IEAT Thailand standards"
            },
            "building_recommendations": {
                "description": building_types,
                "plot_size_range": "5,000-30,000 m² per building",
                "building_height": "8-15m (1-2 floors)",
                "spacing": "Min 12m between buildings (IEAT fire safety)"
            },
            "infrastructure": {
                "main_road_width": "25-30m (IEAT standard)",
                "secondary_road": "15-20m",
                "green_buffer": "10m minimum strip",
                "retention_pond": f"{round(area_ha * 6.25 / 20, 1)} rai required"
            }
        }
    
    def _generate_questions(self, area_ha: float, terrain: Dict) -> List[Dict]:
        """Tạo câu hỏi hỗ trợ để thu thập thêm thông tin."""
        questions = []
        
        # Q1: Industry type
        questions.append({
            "question": "🏭 Loại hình công nghiệp chủ yếu?",
            "options": [
                "Electronics & Technology",
                "Automotive & Parts",
                "Food & Beverage",
                "Logistics & Warehousing",
                "Textile & Garment",
                "Chemicals & Pharma",
                "Mixed-use (đa ngành)"
            ],
            "why": "Để xác định yêu cầu về spacing, utilities và compliance"
        })
        
        # Q2: Target FAR
        questions.append({
            "question": "📊 Hệ số sử dụng đất mong muốn (FAR)?",
            "options": [
                "Thấp (0.3-0.4) - Ưu tiên không gian xanh",
                "Trung bình (0.4-0.6) - Cân bằng",
                "Cao (0.6-0.8) - Tối ưu hiệu quả sử dụng đất"
            ],
            "default": "0.4 (IEAT standard)",
            "why": "Ảnh hưởng đến số lượng và quy mô building"
        })
        
        # Q3: Timeline
        questions.append({
            "question": "⏰ Timeline dự án?",
            "options": [
                "Urgent (< 1 tuần) - Concept design only",
                "Normal (2-4 tuần) - Detailed masterplan",
                "Flexible (> 1 tháng) - Full phasing plan"
            ],
            "why": "Xác định mức độ chi tiết thiết kế"
        })
        
        # Q4: Special requirements
        questions.append({
            "question": "✨ Yêu cầu đặc biệt?",
            "options": [
                "Green building / LEED certified",
                "Smart factory / IoT integration",
                "High security zones",
                "Public amenities (cafeteria, clinic)",
                "Không có yêu cầu đặc biệt"
            ],
            "multi_select": True,
            "why": "Để tích hợp features đặc biệt vào thiết kế"
        })
        
        # Q5: Terrain handling (if topography exists)
        if terrain.get("has_topography"):
            questions.append({
                "question": "🏔️ Xử lý địa hình?",
                "options": [
                    "Minimal cut/fill - giữ nguyên địa hình",
                    "Balanced cut/fill - san nền cân bằng",
                    "Major grading - san phẳng hoàn toàn"
                ],
                "default": "Balanced cut/fill",
                "why": "File DXF có thông tin địa hình (contour lines)"
            })
        
        return questions
    
    def _generate_sample_prompts(self, area_ha: float, dimensions: Dict) -> List[str]:
        """Tạo prompt mẫu để user có thể copy và chỉnh sửa."""
        
        prompts = []
        
        # Prompt 1: Simple
        prompts.append(
            f"Thiết kế khu công nghiệp {area_ha:.1f} ha, "
            f"ưu tiên logistics, tuân thủ IEAT Thailand"
        )
        
        # Prompt 2: Detailed
        prompts.append(
            f"Tạo masterplan cho khu đất {area_ha:.1f} ha ({dimensions['width']:.0f}m × {dimensions['height']:.0f}m), "
            f"gồm 8-12 building, mỗi building 3000-5000m², "
            f"ưu tiên: logistics & manufacturing, green buffer 15%, "
            f"đường chính 25m, tuân thủ IEAT"
        )
        
        # Prompt 3: Advanced
        prompts.append(
            f"Industrial park {area_ha:.1f} ha theo IEAT Thailand:\n"
            f"- Salable: 77% (~{area_ha*0.77:.1f} ha)\n"
            f"- Green: 12% (~{area_ha*0.12:.1f} ha)\n"
            f"- Buildings: 10-15 plots, 5,000-8,000 m² each\n"
            f"- Industry: Mixed (electronics, automotive, logistics)\n"
            f"- Road: Main 25m, secondary 15m\n"
            f"- Special: Smart factory ready, LEED zones"
        )
        
        return prompts


def analyze_dxf_file(file_path: str) -> Dict:
    """Helper function để phân tích DXF file."""
    analyzer = DXFAnalyzer(file_path)
    return analyzer.analyze()


# Test function
if __name__ == "__main__":
    # Test với pilot project file
    test_file = "../../sample-data/Pilot_Existing Topo _ Boundary.dxf"
    
    if Path(test_file).exists():
        print("🔍 Analyzing DXF file...")
        result = analyze_dxf_file(test_file)
        
        if result.get("success"):
            print("\n✅ Phân tích thành công!")
            print(f"\n📏 Thông tin khu đất:")
            print(f"   Diện tích: {result['site_info']['area_ha']} ha")
            print(f"   Kích thước: {result['site_info']['dimensions']['width_m']}m × {result['site_info']['dimensions']['height_m']}m")
            
            print(f"\n💡 Gợi ý thiết kế:")
            print(f"   Quy mô: {result['suggestions']['project_scale']}")
            print(f"   Số plots: ~{result['suggestions']['estimated_plots']}")
            
            print(f"\n❓ Câu hỏi hỗ trợ ({len(result['questions'])}):")
            for i, q in enumerate(result['questions'], 1):
                print(f"   {i}. {q['question']}")
            
            print(f"\n📝 Prompt mẫu:")
            for i, p in enumerate(result['sample_prompts'], 1):
                print(f"\n   {i}. \"{p}\"")
        else:
            print(f"\n❌ Lỗi: {result.get('error')}")
    else:
        print(f"❌ File not found: {test_file}")
