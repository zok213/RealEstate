"""
Configuration module for Industrial Park AI Designer Backend.
Contains IEAT Thailand regulations (primary) and TCVN 7144 Vietnam (legacy).
"""

import os
from pydantic_settings import BaseSettings
from typing import Dict, List, Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # MegaLLM API (via OpenAI-compatible API)
    megallm_api_key: str = os.getenv("MEGALLM_API_KEY", "")
    megallm_base_url: str = "https://ai.megallm.io/v1"
    megallm_model: str = "gpt-3.5-turbo"  # Free tier model (or try: gpt-4o-mini, claude-3-haiku)
    
    # Google Gemini API
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # Legacy DeepSeek (disabled - no credits)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    
    huggingface_token: str = os.getenv("HUGGINGFACE_TOKEN", "")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    mistral_api_key: str = os.getenv("MISTRAL_API_KEY", "")
    cerebras_api_key: str = os.getenv("CEREBRAS_API_KEY", "")
    ollama_base_url: str = "http://localhost:11434"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/industrial_park"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # App
    app_env: str = "development"
    debug: bool = True
    cors_origins: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# IEAT (Thailand) + TCVN 7144 (Vietnam) Combined Regulations
INDUSTRIAL_PARK_REGULATIONS: Dict = {
    # IEAT Thailand Standards for Masterplan Design
    "ieat_thailand": {
        "land_use": {
            "salable_area_min_percent": 75,  # Sell area >= 75%
            "green_min_percent": 10,          # Green >= 10%
            "utility_area_percent": 12.36,    # U+G requirement
            "green_buffer_width_m": 10        # Min 10m strip
        },
        "green_requirements": {
            # U+G >= 250 rai when TA > 1000 rai (62.5 ha)
            # U+G >= 25% when TA <= 1000 rai
            "large_project_min_rai": 250,     # For TA > 1000 rai
            "small_project_min_percent": 25,  # For TA <= 1000 rai
            "threshold_rai": 1000
        },
        "plot_dimensions": {
            "shape": "rectangular",
            "width_to_depth_ratio": (0.5, 0.67),  # 1:1.5 to 1:2
            "min_frontage_width_m": 90,
            "preferred_frontage_m": 100,
            "aspect_ratio_optimal": 1.5
        },
        "road_standards": {
            "traffic_lane_width_m": 3.5,
            "min_right_of_way_m": 25,
            "main_road_row_m": (25, 30),
            "double_loaded_roads": True  # Secondary roads
        },
        "infrastructure": {
            "retention_pond": {
                "ratio_rai": 20,  # 20 rai gross per 1 rai pond
                "elevation": "higher_than_downstream"
            },
            "water_treatment": {
                "capacity_cmd_per_rai": 2000,
                "demand_commercial_cmd_per_rai": 3,
                "demand_industrial_cmd_per_rai": 4,
                "demand_powerplant_cmd_per_rai": 50
            },
            "wastewater_treatment": {
                "capacity_cmd_per_rai": 500,
                "ratio_general": 0.8,      # 80% of water demand
                "ratio_powerplant": 0.5    # 50% of water demand
            },
            "substation": {
                "area_rai": 10,
                "placement": "center"
            }
        },
        "grading": {
            "elevation_above_frontage": True,
            "max_cut_depth_m": 5,
            "cut_fill_ratio": 1.05  # Volume cut = 1.05 x Volume fill
        }
    },
    
    # TCVN 7144:2014 Vietnam Standards (Legacy support)
    "tcvn_7144_vietnam": {
        "area_distribution": {
            "development_min_percent": 60,
            "green_min_percent": 20,
            "road_min_percent": 15,
            "infrastructure_min_percent": 3
        },
        "building_types": {
            "light_manufacturing": {
                "size_range_m2": (2000, 10000),
                "max_height_m": 15,
                "min_spacing_m": 12,
                "parking_ratio": 1/250
            },
            "medium_manufacturing": {
                "size_range_m2": (5000, 30000),
                "max_height_m": 20,
                "min_spacing_m": 15,
                "parking_ratio": 1/200
            },
            "heavy_manufacturing": {
                "size_range_m2": (10000, 50000),
                "max_height_m": 25,
                "min_spacing_m": 25,
                "parking_ratio": 1/250
            },
            "warehouse": {
                "size_range_m2": (2000, 20000),
                "max_height_m": 12,
                "min_spacing_m": 12,
                "loading_docks_min": 2
            }
        },
        "fire_safety": {
            "min_building_spacing_m": 12,
            "max_building_spacing_m": 25,
            "emergency_exits_per_building": 2,
            "fire_truck_access_width_m": 6
        },
        "road_network": {
            "primary_road_width_m": (20, 30),
            "secondary_road_width_m": (12, 15),
            "service_road_width_m": (8, 10)
        }
    }
}


# LLM Model Configuration
LLM_MODELS = {
    "megallm": {
        "name": "llama3.3-70b-instruct",
        "base_url": "https://ai.megallm.io/v1",
        "max_tokens": 4096,
        "temperature": 0.7,
        "capabilities": ["reasoning", "vietnamese", "tool_use"]
    },
    "gemini": {
        "name": "gemini-2.0-flash-exp",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "max_tokens": 8192,
        "temperature": 0.7,
        "capabilities": ["reasoning", "vietnamese", "multimodal"]
    },
    "deepseek": {
        "name": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "max_tokens": 4096,
        "temperature": 1.0,
        "top_p": 0.95,
        "capabilities": ["reasoning", "tool_use", "code"]
    },
    "qwen": {
        "name": "qwen2.5-72b-instruct",
        "base_url": "https://api.groq.com/openai/v1",
        "max_tokens": 4096,
        "temperature": 0.7,
        "capabilities": ["vietnamese", "reasoning"],
        "priority": 2
    },
    "mistral": {
        "name": "mistral-large-latest",
        "base_url": "https://api.mistral.ai/v1",
        "max_tokens": 4096,
        "temperature": 0.7,
        "capabilities": ["reasoning", "tool_use", "multilingual"],
        "priority": 3
    },
    "cerebras": {
        "name": "llama3.1-70b",
        "base_url": "https://api.cerebras.ai/v1",
        "max_tokens": 8192,
        "temperature": 0.7,
        "capabilities": ["reasoning", "fast_inference"],
        "priority": 4
    },
    "ollama_qwen": {
        "name": "qwen2.5:72b",
        "base_url": "http://localhost:11434/v1",
        "max_tokens": 4096,
        "temperature": 0.7,
        "capabilities": ["vietnamese", "local"],
        "priority": 99
    }
}

# Backup rotation order (priority-based)
LLM_ROTATION_ORDER = ["megallm", "gemini", "qwen", "mistral", "cerebras", "ollama_qwen"]


# Get settings instance
settings = Settings()

# Default to IEAT Thailand standards
IEAT_REGULATIONS = INDUSTRIAL_PARK_REGULATIONS["ieat_thailand"]

# Aliases for backwards compatibility
TCVN_7144_REGULATIONS = INDUSTRIAL_PARK_REGULATIONS["tcvn_7144_vietnam"]
DEFAULT_REGULATIONS = IEAT_REGULATIONS
