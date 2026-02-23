"""
Multi-Model LLM Orchestrator for Industrial Park Design AI.
Supports: DeepSeek-V3.2, Qwen2.5 (Groq), Ollama (local fallback).
"""

from openai import OpenAI, AsyncOpenAI
from typing import Dict, List, Tuple, Optional, Any
import json
import re
import os
from dataclasses import dataclass
from enum import Enum

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings, INDUSTRIAL_PARK_REGULATIONS, LLM_MODELS, LLM_ROTATION_ORDER


class LLMProvider(Enum):
    MEGALLM = "megallm"  # Primary - Llama 3.3 70B
    GEMINI = "gemini"    # Google Gemini 2.0 Flash
    DEEPSEEK = "deepseek"  # Disabled - no credits
    GROQ_QWEN = "qwen"   # Groq - Qwen 2.5 72B
    MISTRAL = "mistral"  # Mistral Large
    CEREBRAS = "cerebras" # Cerebras Llama 3.1 70B
    OLLAMA = "ollama"    # Local fallback


@dataclass
class LLMResponse:
    """Structured LLM response."""
    content: str
    extracted_params: Dict
    ready_for_generation: bool
    model_used: str
    tokens_used: int = 0


class FreeLLMClient:
    """
    Multi-model LLM client with intelligent routing.
    - MegaLLM (Llama 3.3 70B): Primary for reasoning + Vietnamese
    - Qwen 2.5 72B (Groq): Vietnamese fallback
    - Ollama: Local fallback
    """
    
    def __init__(self):
        self.clients: Dict[str, OpenAI] = {}
        self.gemini_client = None
        self._init_clients()
        
    def _init_clients(self):
        """Initialize API clients for each provider."""
        # Google Gemini Client (Primary - via google.generativeai)
        if settings.google_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.google_api_key)
                self.gemini_client = genai.GenerativeModel('gemini-2.0-flash-exp')
                print(f"✓ Google Gemini client initialized")
            except Exception as e:
                print(f"⚠ Gemini initialization failed: {e}")
        
        # MegaLLM Client (Llama 3.3 70B - Fallback)
        if settings.megallm_api_key:
            self.clients["megallm"] = OpenAI(
                api_key=settings.megallm_api_key,
                base_url=settings.megallm_base_url,
                timeout=30.0  # 30 second timeout
            )
            print(f"✓ MegaLLM client initialized (model: {settings.megallm_model})")
        
        # DeepSeek Client (disabled - no credits)
        if settings.deepseek_api_key:
            self.clients["deepseek"] = OpenAI(
                api_key=settings.deepseek_api_key,
                base_url=settings.deepseek_base_url,
                timeout=15.0
            )
        
        # Groq Client (for Qwen)
        if settings.groq_api_key:
            self.clients["groq"] = OpenAI(
                api_key=settings.groq_api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            print(f"✓ Groq client initialized")
        
        # Mistral Client
        if settings.mistral_api_key:
            self.clients["mistral"] = OpenAI(
                api_key=settings.mistral_api_key,
                base_url="https://api.mistral.ai/v1"
            )
            print(f"✓ Mistral client initialized")
        
        # Cerebras Client
        if settings.cerebras_api_key:
            self.clients["cerebras"] = OpenAI(
                api_key=settings.cerebras_api_key,
                base_url="https://api.cerebras.ai/v1"
            )
            print(f"✓ Cerebras client initialized")
        
        # Ollama Client (local)
        self.clients["ollama"] = OpenAI(
            api_key="ollama",
            base_url=settings.ollama_base_url + "/v1"
        )
    
    def chat(
        self,
        messages: List[Dict],
        provider: LLMProvider = LLMProvider.MEGALLM,
        **kwargs
    ) -> str:
        """
        Send chat request to selected provider.
        
        Args:
            messages: Chat messages in OpenAI format
            provider: Which LLM provider to use
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            LLM response text
        """
        import time
        print(f"[LLM] Starting chat request...")
        
        # Skip Gemini if quota exceeded (detected from previous failures)
        # Uncomment below if Gemini quota is restored:
        # if self.gemini_client:
        #     try:
        #         return self._call_gemini(messages, **kwargs)
        #     except Exception as e:
        #         print(f"[LLM] Gemini failed: {e}, trying fallback...")
        
        try:
            if provider == LLMProvider.MEGALLM:
                return self._call_megallm(messages, **kwargs)
            elif provider == LLMProvider.GEMINI:
                return self._call_gemini(messages, **kwargs)
            elif provider == LLMProvider.DEEPSEEK:
                return self._call_deepseek(messages, **kwargs)
            elif provider == LLMProvider.GROQ_QWEN:
                return self._call_groq_qwen(messages, **kwargs)
            elif provider == LLMProvider.MISTRAL:
                return self._call_mistral(messages, **kwargs)
            elif provider == LLMProvider.CEREBRAS:
                return self._call_cerebras(messages, **kwargs)
            elif provider == LLMProvider.OLLAMA:
                return self._call_ollama(messages, **kwargs)
        except Exception as e:
            print(f"[LLM] Provider {provider} failed: {e}, rotating...")
            return self._fallback_chain(messages, provider, **kwargs)
    
    def _call_gemini(self, messages: List[Dict], **kwargs) -> str:
        """Call Google Gemini API with timeout."""
        import time
        if not self.gemini_client:
            raise ValueError("Gemini client not initialized")
        
        print(f"[Gemini] Starting API call...")
        start_time = time.time()
        
        # Convert OpenAI format to Gemini format (simplified)
        # Skip system prompt if too long - just use user message
        user_messages = [msg for msg in messages if msg.get("role") == "user"]
        if user_messages:
            last_user_msg = user_messages[-1].get("content", "")
            # Simple prompt for faster response
            full_prompt = f"""You are an industrial park design AI. Respond in Vietnamese.

User request: {last_user_msg}

Extract these parameters in JSON format:
{{
  "parameters": {{
    "totalArea_ha": <number>,
    "industryFocus": [{{"type": "logistics/warehouse", "count": <number>, "percentage": <number>}}],
    "workerCapacity": <number>,
    "constraints": {{"greenAreaMin_percent": 20, "roadAreaMin_percent": 15}}
  }},
  "readyForGeneration": true
}}

Response (in Vietnamese + JSON):"""
        else:
            full_prompt = "Hello! How can I help you design an industrial park?"
        
        try:
            response = self.gemini_client.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": 512,  # Reduced for speed
                    "temperature": 0.5
                },
                request_options={"timeout": 10}  # 10 second timeout
            )
            elapsed = time.time() - start_time
            print(f"[Gemini] Response received in {elapsed:.2f}s")
            return response.text
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"[Gemini] Failed after {elapsed:.2f}s: {e}")
            raise
    
    def _call_megallm(self, messages: List[Dict], **kwargs) -> str:
        """Call MegaLLM API (Llama 3.3 70B)."""
        if "megallm" not in self.clients:
            raise ValueError("MegaLLM API key not configured")
            
        config = LLM_MODELS["megallm"]
        response = self.clients["megallm"].chat.completions.create(
            model=settings.megallm_model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"])
        )
        return response.choices[0].message.content
    
    def _call_deepseek(self, messages: List[Dict], **kwargs) -> str:
        """Call DeepSeek API."""
        if "deepseek" not in self.clients:
            raise ValueError("DeepSeek API key not configured")
            
        config = LLM_MODELS["deepseek"]
        response = self.clients["deepseek"].chat.completions.create(
            model=config["name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"]),
            top_p=kwargs.get("top_p", config.get("top_p", 0.95))
        )
        return response.choices[0].message.content
    
    def _call_groq_qwen(self, messages: List[Dict], **kwargs) -> str:
        """Call Qwen via Groq API."""
        if "groq" not in self.clients:
            raise ValueError("Groq API key not configured")
            
        config = LLM_MODELS["qwen"]
        response = self.clients["groq"].chat.completions.create(
            model=config["name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"])
        )
        return response.choices[0].message.content
    
    def _call_mistral(self, messages: List[Dict], **kwargs) -> str:
        """Call Mistral API."""
        if "mistral" not in self.clients:
            raise ValueError("Mistral API key not configured")
            
        config = LLM_MODELS["mistral"]
        response = self.clients["mistral"].chat.completions.create(
            model=config["name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"])
        )
        return response.choices[0].message.content
    
    def _call_cerebras(self, messages: List[Dict], **kwargs) -> str:
        """Call Cerebras API."""
        if "cerebras" not in self.clients:
            raise ValueError("Cerebras API key not configured")
            
        config = LLM_MODELS["cerebras"]
        response = self.clients["cerebras"].chat.completions.create(
            model=config["name"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", config["max_tokens"]),
            temperature=kwargs.get("temperature", config["temperature"])
        )
        return response.choices[0].message.content
    
    def _call_ollama(self, messages: List[Dict], model: str = "deepseek-v3", **kwargs) -> str:
        """Call Ollama local API."""
        response = self.clients["ollama"].chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 4096),
            temperature=kwargs.get("temperature", 1.0)
        )
        return response.choices[0].message.content
    
    def _fallback_chain(
        self,
        messages: List[Dict],
        failed_provider: LLMProvider,
        **kwargs
    ) -> str:
        """Try fallback providers in rotation order."""
        provider_methods = {
            "megallm": self._call_megallm,
            "gemini": self._call_gemini,
            "qwen": self._call_groq_qwen,
            "mistral": self._call_mistral,
            "cerebras": self._call_cerebras,
            "ollama_qwen": self._call_ollama,
        }
        
        # Try providers in rotation order
        for provider_name in LLM_ROTATION_ORDER:
            if provider_name == failed_provider.value:
                continue
            
            method = provider_methods.get(provider_name)
            if not method:
                continue
                
            try:
                print(f"Trying fallback provider: {provider_name}")
                return method(messages, **kwargs)
            except Exception as e:
                print(f"Fallback {provider_name} failed: {e}")
                continue
        
        raise RuntimeError("All LLM providers failed")


class IndustrialParkLLMOrchestrator:
    """
    LLM orchestrator for industrial park design.
    Manages multi-turn conversation, parameter extraction, and constraint reasoning.
    Supports incremental refinement through small adjustments.
    """
    
    def __init__(self):
        self.llm_client = FreeLLMClient()
        self.conversation_history: List[Dict] = []
        self.extracted_params: Dict = {}
        self.design_iterations: List[Dict] = []  # Track design changes
        self.current_validation: Dict = {}  # Current IEAT validation status
        self.system_prompt = self._build_system_prompt_ieat()
    
    def _build_system_prompt_ieat(self) -> str:
        """Build comprehensive system prompt with IEAT Thailand standards."""
        ieat = INDUSTRIAL_PARK_REGULATIONS.get("ieat_thailand", {})
        
        return f"""You are an expert Industrial Park Design Assistant with expertise in:
- IEAT Thailand standards for masterplan development
- Industrial estate layout optimization
- Infrastructure planning and utility systems
- Multi-turn conversation and incremental design refinement

ROLE: Guide users through industrial park design step-by-step.
Support both complete specifications AND incremental adjustments.

========== IEAT THAILAND STANDARDS ==========

1. LAND USE RATIOS:
   - Salable Area: ≥ {ieat['land_use']['salable_area_min_percent']}%
   - Green Area: ≥ {ieat['land_use']['green_min_percent']}%
   - Utility Area: ~{ieat['land_use']['utility_area_percent']}%
   - Green Buffer: {ieat['land_use']['green_buffer_width_m']}m strip

2. LARGE PROJECT RULES (Area > 1000 rai):
   - U+G Combined: ≥ {ieat['green_requirements']['large_project_min_rai']} rai
   
3. PLOT DESIGN:
   - Shape: {ieat['plot_dimensions']['shape'].title()}
   - W:D Ratio: 1:1.5 to 1:2
   - Min Frontage: {ieat['plot_dimensions']['min_frontage_width_m']}m
   - Preferred: > {ieat['plot_dimensions']['preferred_frontage_m']}m

4. ROAD STANDARDS:
   - Traffic Lane: {ieat['road_standards']['traffic_lane_width_m']}m
   - Min ROW: {ieat['road_standards']['min_right_of_way_m']}m
   - Layout: Double-loaded secondary roads

5. INFRASTRUCTURE:
   - Retention Pond: 1 rai per {ieat['infrastructure']['retention_pond']['ratio_rai']} rai gross
   - Water Treatment: {ieat['infrastructure']['water_treatment']['capacity_cmd_per_rai']} cmd/rai
   - Wastewater: {ieat['infrastructure']['wastewater_treatment']['capacity_cmd_per_rai']} cmd/rai
   - Substation: {ieat['infrastructure']['substation']['area_rai']} rai at center

========== CONVERSATION MODES ==========

MODE 1: Initial Planning (Full Specification)
- Ask about: area, target customers, industry focus
- Extract: totalArea_ha, salableArea_percent, greenArea_percent
- Validate against IEAT standards
- When complete, set readyForGeneration: true

MODE 2: Incremental Refinement (Small Adjustments)
Examples:
- "Tăng green area lên 12%" → greenArea_percent: 12
- "Thêm 2 nhà máy nữa" → Update industryFocus count
- "Giảm frontage xuống 95m" → frontage_width_m: 95
- "Thay đổi plot ratio thành 1:1.8" → Update aspect ratio

For each adjustment:
1. Understand the specific change requested
2. Update ONLY the affected parameter
3. Validate new value against IEAT standards
4. Warn if non-compliant
5. Suggest alternatives if needed

MODE 3: Design Review & Optimization
- Review current parameters
- Suggest improvements
- Optimize for cost, logistics, or customer requirements

========== RESPONSE GUIDELINES ==========

1. Always respond in Vietnamese when user uses Vietnamese
2. Be conversational and helpful
3. Explain IEAT constraints when relevant
4. For incremental changes, acknowledge previous design
5. Validate every change against IEAT standards
6. Use encouraging language for compliant designs
7. Provide clear warnings for non-compliance

OUTPUT FORMAT (when parameters ready):
```json
{{
  "parameters": {{
    "totalArea_ha": <number>,
    "totalArea_rai": <number>,
    "salableArea_percent": <number 75-80>,
    "utilityArea_percent": <number 12-15>,
    "greenArea_percent": <number 10-15>,
    "industryFocus": [
      {{"type": "industrial", "percentage": 60, "count": 5}},
      {{"type": "warehouse", "percentage": 30, "count": 3}}
    ],
    "plotDimensions": {{
      "shape": "rectangular",
      "widthToDepthRatio": 1.5,
      "frontageWidth_m": 100,
      "minFrontage_m": 90
    }},
    "infrastructure": {{
      "retentionPond_rai": <calculated>,
      "substation_rai": 10,
      "waterTreatment_cmd": <calculated>,
      "wastewater_cmd": <calculated>
    }},
    "constraints": {{
      "greenBufferWidth_m": 10,
      "minROW_m": 25,
      "doubleLoadedRoads": true
    }}
  }},
  "ieatCompliance": {{
    "salableArea": "✅ PASS",
    "greenArea": "✅ PASS",
    "plotDesign": "✅ PASS",
    "infrastructure": "✅ PASS"
  }},
  "readyForGeneration": true
}}
```

INCREMENTAL UPDATE FORMAT:
```json
{{
  "understood": "User wants to increase green area to 12%",
  "changes": [
    {{"param": "parameters.greenArea_percent", "from": 10, "to": 12}}
  ],
  "impact": "Green area increased. Still compliant with IEAT (≥10%). Salable area reduced to 75.6%.",
  "validation": {{
    "compliant": true,
    "warnings": ["Salable area at minimum threshold"]
  }}
}}
```

Be helpful, precise, and always validate against IEAT standards!"""
    
    def inject_dxf_context(self, dxf_analysis: Dict) -> str:
        """
        Inject DXF analysis vào conversation context để AI có thông tin khu đất.
        
        Args:
            dxf_analysis: Result từ DXFAnalyzer.analyze()
            
        Returns:
            AI response với gợi ý và câu hỏi
        """
        if not dxf_analysis.get("success"):
            return "⚠️ Không thể đọc file DXF. Vui lòng kiểm tra file."
        
        site = dxf_analysis["site_info"]
        sugg = dxf_analysis["suggestions"]
        
        # Tạo context message để AI hiểu
        context_msg = f"""📁 FILE DXF ĐÃ UPLOAD

🏗️ THÔNG TIN KHU ĐẤT:
- Diện tích: {site['area_ha']} ha ({site['area_m2']:,.0f} m²)
- Kích thước: {site['dimensions']['width_m']}m × {site['dimensions']['height_m']}m
- Chu vi: {site['dimensions']['perimeter_m']}m
- Quy mô: {sugg['project_scale']}

💡 GỢI Ý IEAT THAILAND:
- Salable area: ~{sugg['land_use_breakdown']['salable_area_ha']} ha (77%)
- Green area: ~{sugg['land_use_breakdown']['green_area_ha']} ha (12%)
- Utility area: ~{sugg['land_use_breakdown']['utility_area_ha']} ha (11%)
- Estimated plots: ~{sugg['estimated_plots']} buildings
- Plot size: {sugg['building_recommendations']['plot_size_range']}
- Building height: {sugg['building_recommendations']['building_height']}

System initialized with site context from DXF file."""
        
        # Inject vào conversation history
        self.conversation_history.append({
            "role": "system",
            "content": context_msg
        })
        
        # Tạo initial parameters từ DXF
        self.extracted_params = {
            "parameters": {
                "totalArea_ha": site['area_ha'],
                "totalArea_m2": site['area_m2'],
                "dimensions": {
                    "width_m": site['dimensions']['width_m'],
                    "height_m": site['dimensions']['height_m']
                },
                "terrain": site.get('terrain', {}),
                "has_topography": site.get('terrain', {}).get('has_topography', False),
                "source": "dxf_upload"
            }
        }
        
        # Tạo AI greeting với gợi ý
        greeting = f"""✅ Đã phân tích file DXF thành công!

📍 **Khu đất của bạn:**
- Diện tích: **{site['area_ha']} ha** ({site['area_m2']:,.0f} m²)
- Kích thước: {site['dimensions']['width_m']}m × {site['dimensions']['height_m']}m
- Quy mô dự án: **{sugg['project_scale'].replace('_', ' ').title()}**

💡 **Theo IEAT Thailand standards, dự án này có thể:**
- Xây dựng **~{sugg['estimated_plots']} buildings** (mỗi plot 5,000-30,000 m²)
- Phân bổ: 77% salable (~{sugg['land_use_breakdown']['salable_area_ha']} ha), 12% green, 11% utility
- Đường chính: {sugg.get('infrastructure', {}).get('main_road_width', '25-30m')}, secondary: {sugg.get('infrastructure', {}).get('secondary_road', '15-20m')}
- Plot size: {sugg.get('building_recommendations', {}).get('plot_size_range', '5,000-30,000 m²')}
- Building height: {sugg.get('building_recommendations', {}).get('building_height', '8-15m')}

❓ **Để tôi hỗ trợ tốt hơn, bạn có thể cho biết:**

"""
        
        # Thêm questions
        for i, q in enumerate(dxf_analysis["questions"][:3], 1):
            greeting += f"\n{i}. {q['question']}"
            if q.get("options"):
                greeting += f"\n   Options: {', '.join(q['options'][:3])}"
                if len(q['options']) > 3:
                    greeting += f", ..."
        
        greeting += f"""

📝 **Hoặc dùng prompt mẫu:**
"{dxf_analysis['sample_prompts'][0]}"

💬 Bạn có thể bắt đầu bằng cách:
- Trả lời các câu hỏi trên
- Chỉnh sửa và gửi prompt mẫu
- Hoặc mô tả yêu cầu của bạn bằng ngôn ngữ tự nhiên"""
        
        return greeting
    
    def chat(
        self, 
        user_message: str, 
        prefer_vietnamese: bool = True
    ) -> LLMResponse:
        """
        Multi-turn conversation with parameter tracking.
        
        Args:
            user_message: User input text
            prefer_vietnamese: Use Qwen for better Vietnamese support
            
        Returns:
            LLMResponse with content and extracted parameters
        """
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages with system prompt
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history
        
        # Choose provider: MegaLLM (Llama 3.3 70B) by default, Groq for fallback
        if settings.groq_api_key and prefer_vietnamese:
            provider = LLMProvider.GROQ_QWEN
        elif settings.megallm_api_key:
            provider = LLMProvider.MEGALLM
        else:
            provider = LLMProvider.OLLAMA
        
        try:
            response_text = self.llm_client.chat(messages, provider)
        except Exception as e:
            print(f"Primary provider failed: {e}")
            # Use smart offline mode instead of crashing
            response_text = self._generate_offline_response(user_message)
        
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Extract structured parameters if present
        extracted = self._extract_structured_params(response_text)
        if extracted:
            self.extracted_params.update(extracted)
        
        return LLMResponse(
            content=response_text,
            extracted_params=self.extracted_params,
            ready_for_generation=self.is_ready_for_optimization(),
            model_used=provider.value
        )
    
    def _extract_structured_params(self, text: str) -> Dict:
        """Extract JSON parameters from LLM response."""
        try:
            # Find JSON block in response
            json_pattern = r'```json\s*([\s\S]*?)\s*```'
            match = re.search(json_pattern, text)
            if match:
                json_str = match.group(1)
                parsed = json.loads(json_str)
                return parsed
            
            # Try finding raw JSON object
            json_match = re.search(r'\{[\s\S]*?"parameters"[\s\S]*?\}', text)
            if json_match:
                parsed = json.loads(json_match.group())
                return parsed
                
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"Parameter extraction error: {e}")
        
        # Extract terrain strategy from text patterns
        text_lower = text.lower()
        extracted = {}
        
        if 'minimal' in text_lower and (
            'cut' in text_lower or 
            'fill' in text_lower or 
            'giữ nguyên' in text_lower
        ):
            extracted['terrain_strategy'] = 'minimal_cut'
        elif 'balanced' in text_lower and (
            'cut' in text_lower or 
            'fill' in text_lower or 
            'cân bằng' in text_lower
        ):
            extracted['terrain_strategy'] = 'balanced_cut_fill'
        elif 'major' in text_lower and (
            'grading' in text_lower or 
            'san phẳng' in text_lower or 
            'san nền' in text_lower
        ):
            extracted['terrain_strategy'] = 'major_grading'
        
        return extracted
    
    def get_extracted_params(self) -> Dict:
        """Get current extracted parameters."""
        return self.extracted_params
    
    def is_ready_for_optimization(self) -> bool:
        """Check if parameters are complete for design generation."""
        params = self.extracted_params.get("parameters", self.extracted_params)
        required = ['totalArea_ha', 'industryFocus']
        has_required = all(key in params for key in required)
        return has_required or self.extracted_params.get("readyForGeneration", False)
    
    def reset_conversation(self):
        """Reset conversation for new project."""
        self.conversation_history = []
        self.extracted_params = {}
    
    def get_design_params_for_optimizer(self) -> Dict:
        """Get parameters formatted for the optimization engine."""
        params = self.extracted_params.get("parameters", self.extracted_params)
        
        return {
            "total_area_ha": params.get("totalArea_ha", 50),
            "total_area_m2": params.get("totalArea_ha", 50) * 10000,
            "industry_focus": params.get("industryFocus", []),
            "worker_capacity": params.get("workerCapacity", 3000),
            "constraints": params.get("constraints", {}),
            "special_requirements": params.get("specialRequirements", []),
            "terrain_strategy": params.get("terrain_strategy", "balanced_cut_fill"),
            "has_topography": params.get("has_topography", False),
            "terrain": params.get("terrain", {})
        }
    
    def update_parameter(
        self, 
        param_path: str, 
        value: any,
        user_request: str = ""
    ) -> Dict:
        """
        Update a specific parameter incrementally.
        
        Args:
            param_path: Dot-notation path (e.g., "parameters.totalArea_ha")
            value: New value
            user_request: Original user request for context
            
        Returns:
            Validation result with updated params
        """
        # Get old value before update
        old_value = self._get_nested_param(param_path)
        
        # Update parameter
        self._set_nested_param(param_path, value)
        
        # Store iteration
        from datetime import datetime
        iteration = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "param_path": param_path,
            "old_value": old_value,
            "new_value": value
        }
        self.design_iterations.append(iteration)
        
        # Validate against IEAT standards
        validation = self._validate_ieat_compliance()
        self.current_validation = validation
        
        return {
            "status": "success",
            "message": f"Updated {param_path} from {old_value} to {value}",
            "param_path": param_path,
            "old_value": old_value,
            "new_value": value,
            "validation": validation
        }
    
    def _get_nested_param(self, path: str) -> any:
        """Get nested parameter by dot notation."""
        keys = path.split(".")
        value = self.extracted_params
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        return value
    
    def _set_nested_param(self, path: str, value: any):
        """Set nested parameter by dot notation."""
        keys = path.split(".")
        target = self.extracted_params
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        target[keys[-1]] = value
    
    def _validate_ieat_compliance(self) -> Dict:
        """
        Validate current parameters against IEAT standards.
        
        Returns:
            Dict with compliance status, rules, warnings and recommendations
        """
        params = self.extracted_params.get("parameters", {})
        total_area_rai = params.get("totalArea_ha", 0) * 6.25  # ha to rai
        
        ieat = INDUSTRIAL_PARK_REGULATIONS.get("ieat_thailand", {})
        land_use = ieat.get("land_use", {})
        
        validation = {
            "compliant": True,
            "rules": {},
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Check salable area
        salable_pct = params.get("salableArea_percent", 75)
        min_salable = land_use.get("salable_area_min_percent", 75)
        salable_ok = salable_pct >= min_salable
        
        validation["rules"]["salable_area"] = {
            "compliant": salable_ok,
            "status": f"Salable {salable_pct}% (min {min_salable}%)"
        }
        
        if not salable_ok:
            validation["errors"].append(
                f"Salable area {salable_pct}% < minimum {min_salable}% (IEAT)"
            )
            validation["compliant"] = False
        
        # Check green area
        green_pct = params.get("greenArea_percent", 10)
        min_green = land_use.get("green_min_percent", 10)
        green_ok = green_pct >= min_green
        
        validation["rules"]["green_area"] = {
            "compliant": green_ok,
            "status": f"Green {green_pct}% (min {min_green}%)"
        }
        
        if not green_ok:
            validation["errors"].append(
                f"Green area {green_pct}% < minimum {min_green}% (IEAT)"
            )
            validation["compliant"] = False
        
        # Check U+G for large projects
        green_req = ieat.get("green_requirements", {})
        threshold = green_req.get("threshold_rai", 1000)
        
        if total_area_rai > threshold:
            utility_pct = params.get("utilityArea_percent", 12)
            ug_rai = total_area_rai * (utility_pct + green_pct) / 100
            min_ug = green_req.get("large_project_min_rai", 250)
            ug_ok = ug_rai >= min_ug
            
            validation["rules"]["ug_combined"] = {
                "compliant": ug_ok,
                "status": f"U+G {ug_rai:.1f} rai (min {min_ug} rai)"
            }
            
            if not ug_ok:
                validation["warnings"].append(
                    f"U+G = {ug_rai:.1f} rai < {min_ug} rai (large project)"
                )
        
        # Check plot dimensions
        plot_dims = params.get("plotDimensions", {})
        min_frontage = ieat.get("plot_dimensions", {}).get(
            "min_frontage_width_m", 90
        )
        frontage = plot_dims.get("frontageWidth_m", 100)
        frontage_ok = frontage >= min_frontage
        
        validation["rules"]["plot_frontage"] = {
            "compliant": frontage_ok,
            "status": f"Frontage {frontage}m (min {min_frontage}m)"
        }
        
        if not frontage_ok:
            validation["warnings"].append(
                f"Frontage width < {min_frontage}m (IEAT standard)"
            )
        
        # Add recommendations
        if validation["compliant"]:
            validation["recommendations"].append(
                "✅ Design meets IEAT Thailand standards"
            )
            if not validation["warnings"]:
                validation["recommendations"].append(
                    "💡 Consider optimizing plot layout for logistics"
                )
        
        return validation
    
    def suggest_adjustment(
        self, 
        user_query: str,
        context: str = ""
    ) -> Dict:
        """
        Suggest parameter adjustments based on user query.
        Uses AI to understand intent and propose changes.
        
        Args:
            user_query: Natural language request
                (e.g., "increase green area", "add 2 more factories")
            context: Additional context
            
        Returns:
            Suggested changes with validation
        """
        # Build prompt for adjustment suggestion
        adjustment_prompt = f"""
User query: "{user_query}"
Current parameters: {json.dumps(self.extracted_params, indent=2)}

Analyze the user's request and suggest specific parameter changes.
Respond in Vietnamese with:
1. What you understood from the request
2. Specific parameters to change (with values)
3. IEAT compliance impact

Format:
```json
{{
  "understood": "...",
  "changes": [
    {{"param": "parameters.greenArea_percent", "from": 10, "to": 12}},
    ...
  ],
  "impact": "...",
  "compliant": true
}}
```
"""
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": adjustment_prompt}
        ]
        
        try:
            response = self.llm_client.chat(
                messages, 
                LLMProvider.MEGALLM,
                max_tokens=1024
            )
            
            # Extract suggestion
            suggestion = self._extract_structured_params(response)
            if suggestion:
                return suggestion
            
            # If no structured data, wrap raw response
            return {
                "action": "understand_request",
                "target": "parameters",
                "understood": user_query,
                "changes": [],
                "response": response
            }
                
        except Exception as e:
            print(f"Adjustment suggestion failed: {e}")
        
        # Fallback to pattern matching
        return self._suggest_adjustment_offline(user_query)
    
    def _suggest_adjustment_offline(self, query: str) -> Dict:
        """Offline adjustment suggestion using regex."""
        query_lower = query.lower()
        
        suggestion = {
            "action": "adjust_parameter",
            "target": "",
            "understood": query,
            "changes": [],
            "impact": "",
            "compliant": True
        }
        
        # Patterns for common adjustments
        if "tăng" in query_lower or "thêm" in query_lower:
            # Extract what to increase
            if "cây xanh" in query_lower or "green" in query_lower:
                match = re.search(r'(\d+)', query)
                if match:
                    new_val = int(match.group(1))
                    suggestion["target"] = "green_area"
                    suggestion["changes"].append({
                        "param": "parameters.greenArea_percent",
                        "from": self._get_nested_param(
                            "parameters.greenArea_percent"
                        ),
                        "to": new_val
                    })
                    suggestion["understood"] = \
                        f"Tăng diện tích cây xanh lên {new_val}%"
        
        elif "giảm" in query_lower:
            # Similar logic for decrease
            suggestion["action"] = "reduce"
        
        elif "nhà máy" in query_lower or "factory" in query_lower:
            # Adjust factory count
            match = re.search(r'(\d+)', query)
            if match:
                new_count = int(match.group(1))
                suggestion["target"] = "factory_count"
                suggestion["changes"].append({
                    "param": "parameters.industryFocus.0.count",
                    "from": None,
                    "to": new_count
                })
        
        return suggestion
    
    def apply_suggestions(self, suggestions: Dict) -> Dict:
        """Apply suggested parameter changes."""
        results = []
        failed = []
        
        changes = suggestions if isinstance(suggestions, list) else suggestions.get("changes", [])
        
        for change in changes:
            if isinstance(change, dict) and "param" in change:
                param_path = change["param"]
                new_value = change["to"]
                
                try:
                    result = self.update_parameter(
                        param_path,
                        new_value,
                        user_request=suggestions.get("understood", "")
                    )
                    results.append(result)
                except Exception as e:
                    failed.append({
                        "param": param_path,
                        "error": str(e)
                    })
        
        return {
            "status": "success" if len(failed) == 0 else "partial",
            "applied_count": len(results),
            "failed": failed,
            "results": results,
            "updated_params": self.extracted_params,
            "validation": self.current_validation
        }
    
    def _generate_offline_response(self, user_message: str) -> str:
        """
        Generate intelligent response in offline mode (when API unavailable).
        Uses regex to extract parameters from user message.
        """
        import re
        
        text = user_message.lower()
        
        # Quick responses for common greetings
        greetings = ['chào', 'hello', 'hi', 'xin chào', 'hey']
        if any(g in text for g in greetings) and len(text) < 20:
            return """Xin chào! 👋 Tôi là AI trợ lý thiết kế khu công nghiệp.

Tôi có thể giúp bạn:
- Thiết kế layout khu công nghiệp
- Tối ưu hóa diện tích theo IEAT Thailand standards
- Đề xuất số lượng và loại nhà máy

Hãy cho tôi biết về dự án của bạn! Ví dụ:
"Tôi có 191 hecta đất ở Thailand, muốn làm khu công nghiệp"
"""
        
        # Extract area in hectares
        area_match = re.search(r'(\d+)\s*(ha|hecta|héc ta)', text)
        if not area_match:
            area_match = re.search(r'(\d+)\s*m2|m²', text)
        
        # Extract number of buildings/factories
        building_match = re.search(r'(\d+)\s*(nhà máy|nhà xưởng|tòa nhà|building|factory|xưởng)', text)
        
        # Extract worker count
        worker_match = re.search(r'(\d+)\s*(công nhân|worker|nhân viên|người)', text)
        
        # Detect industry type
        industry_types = []
        if any(k in text for k in ['ô tô', 'automotive', 'xe', 'motor']):
            industry_types.append({'type': 'medium_manufacturing', 'count': 5, 'percentage': 50})
        if any(k in text for k in ['logistics', 'kho', 'warehouse', 'vận chuyển']):
            industry_types.append({'type': 'logistics', 'count': 3, 'percentage': 30})
            industry_types.append({'type': 'warehouse', 'count': 3, 'percentage': 20})
        if any(k in text for k in ['dệt may', 'textile', 'may mặc']):
            industry_types.append({'type': 'light_manufacturing', 'count': 8, 'percentage': 60})
        if any(k in text for k in ['điện tử', 'electronic', 'semiconductor']):
            industry_types.append({'type': 'light_manufacturing', 'count': 6, 'percentage': 50})
        
        # Default industry if none detected
        if not industry_types:
            industry_types = [
                {'type': 'light_manufacturing', 'count': 5, 'percentage': 40},
                {'type': 'warehouse', 'count': 3, 'percentage': 30}
            ]
        
        # If we have enough info, return design ready response
        if area_match or building_match:
            area_ha = int(area_match.group(1)) if area_match else 50
            if 'm2' in text or 'm²' in text and area_match:
                area_ha = area_ha / 10000  # Convert m² to ha
            
            buildings = int(building_match.group(1)) if building_match else 8
            workers = int(worker_match.group(1)) if worker_match else 3000
            
            # Update industry counts based on building number
            for ind in industry_types:
                ind['count'] = max(1, buildings // len(industry_types))
            
            # Store extracted params
            self.extracted_params = {
                "status": "complete",
                "parameters": {
                    "projectName": "Industrial Park Design",
                    "totalArea_ha": area_ha,
                    "industryFocus": industry_types,
                    "workerCapacity": workers,
                    "constraints": {
                        "greenAreaMin_percent": 20,
                        "roadAreaMin_percent": 15,
                        "minBuildingSpacing_m": 12
                    }
                },
                "readyForGeneration": True
            }
            
            return f"""Tôi đã hiểu yêu cầu của bạn! Dưới đây là tóm tắt:

📐 **Diện tích**: {area_ha} hecta ({area_ha * 10000:,.0f} m²)
🏭 **Số nhà máy**: {buildings} tòa
👷 **Công nhân**: {workers:,} người
🔧 **Ngành nghề**: {', '.join([i['type'].replace('_', ' ').title() for i in industry_types])}

Các ràng buộc theo TCVN 7144:2014:
- Cây xanh: ≥ 20%
- Đường giao thông: ≥ 15%
- Khoảng cách tòa nhà: ≥ 12m

✅ **Sẵn sàng tạo thiết kế!** Hệ thống sẽ sử dụng thuật toán CSP + GA để tối ưu layout.

```json
{json.dumps(self.extracted_params, indent=2, ensure_ascii=False)}
```"""
        
        # Default greeting if not enough info
        return """Xin chào! Tôi là AI trợ lý thiết kế khu công nghiệp.

🔧 **Chế độ Offline** - Hệ thống AI đang hoạt động cục bộ.

Vui lòng cho tôi biết:
1. **Diện tích** khu công nghiệp (hecta hoặc m²)
2. **Số lượng nhà máy** cần thiết kế
3. **Ngành nghề** chính (ô tô, logistics, dệt may, điện tử...)
4. **Số công nhân** dự kiến

Ví dụ: "Thiết kế khu công nghiệp 50 ha cho 8 nhà máy ô tô, 3000 công nhân"

Tôi sẽ tự động tạo layout tối ưu theo tiêu chuẩn TCVN 7144:2014."""


# Quick test
if __name__ == "__main__":
    orchestrator = IndustrialParkLLMOrchestrator()
    
    # Test conversation
    response = orchestrator.chat("Tôi cần thiết kế khu công nghiệp 50 hecta")
    print(f"Response: {response.content[:500]}...")
    print(f"Extracted params: {response.extracted_params}")
    print(f"Ready for generation: {response.ready_for_generation}")
