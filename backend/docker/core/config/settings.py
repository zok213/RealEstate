"""
Algorithm configuration settings and constants.

Contains all configurable parameters for the land redistribution algorithm,
organized into dataclasses for type safety and clarity.
"""

from dataclasses import dataclass, field
from typing import Tuple


@dataclass(frozen=True)
class RoadSettings:
    """Road and transportation infrastructure settings (QCVN 01:2021/BXD)."""
    
    # 4-Tier Road System (hierarchical grid)
    perimeter_width: float = 20.0   # Tier 1: Perimeter road (vành đai)
    main_width: float = 14.0        # Tier 2: Main roads (trục chính, 2-4 làn)
    secondary_width: float = 8.0    # Tier 3: Secondary roads (phân khu)
    internal_width: float = 6.0     # Tier 4: Internal roads (nhánh)
    
    # Sidewalk requirements (QCVN 01:2021/BXD)
    sidewalk_width: float = 3.0     # Sidewalk minimum ≥ 3m (includes utility trench)
    turning_radius: float = 125.0   # Corner radius ≥ 125m for trucks/containers
    max_slope: float = 0.06         # Maximum road slope ≤ 6%
    
    # Environmental buffer zones (TCVN 4449:1987)
    buffer_class_1: float = 1000.0  # Độc hại cấp I: ≥ 1000m to residential
    buffer_class_2: float = 300.0   # Độc hại cấp II: ≥ 300m
    buffer_class_3: float = 100.0   # Độc hại cấp III: ≥ 100m
    min_green_in_buffer: float = 0.50  # 50% of buffer must be green space
    
    # Green separation buffers (đai cây xanh cách ly)
    zone_separation_buffer: float = 20.0  # 20m green buffer between zones
    perimeter_green_buffer: float = 30.0  # 30m green buffer around perimeter


@dataclass(frozen=True)
class ZoneSubdivisionConfig:
    """Subdivision configuration for a specific zone type."""
    min_lot_width: float
    max_lot_width: float
    target_lot_width: float
    min_lot_area: float


@dataclass(frozen=True)
class SubdivisionSettings:
    """Block and lot subdivision settings."""
    
    # Land allocation
    service_area_ratio: float = 0.10    # 10% for infrastructure
    min_block_area: float = 2000.0      # Minimum block area (balance between roads and usable blocks)
    
    # Default lot dimensions (for backward compatibility)
    min_lot_width: float = 40.0         # Minimum lot frontage (m) - ~1600m² lots
    max_lot_width: float = 200.0        # Maximum lot frontage (m) - Allow up to 40,000m² lots
    target_lot_width: float = 80.0      # Target lot width (m) - ~6400m² average
    min_lot_area: float = 1000.0        # Minimum lot area (m²)
    
    # Zone-specific configurations
    factory_config: ZoneSubdivisionConfig = field(default_factory=lambda: ZoneSubdivisionConfig(
        min_lot_width=100.0,    # Large factories: 100-200m width
        max_lot_width=200.0,
        target_lot_width=150.0,
        min_lot_area=10000.0    # 10,000m² minimum for factories
    ))
    
    warehouse_config: ZoneSubdivisionConfig = field(default_factory=lambda: ZoneSubdivisionConfig(
        min_lot_width=40.0,     # Medium warehouses: 40-80m width
        max_lot_width=80.0,
        target_lot_width=60.0,
        min_lot_area=2500.0     # 2,500m² minimum for warehouses
    ))
    
    residential_config: ZoneSubdivisionConfig = field(default_factory=lambda: ZoneSubdivisionConfig(
        min_lot_width=15.0,     # Small residential: 15-30m width
        max_lot_width=30.0,
        target_lot_width=20.0,
        min_lot_area=300.0      # 300m² minimum for residential
    ))
    
    # Legal/Construction (TCVN 4514:2012)
    setback_distance: float = 6.0       # Building setback from road (m)
    fire_safety_gap: float = 4.0        # Fire safety gap between buildings (m)
    
    # Building density & green space (QCVN 01:2021/BXD)
    max_building_coverage: float = 0.70  # Maximum 70% building coverage in lot
    min_green_in_lot: float = 0.20       # Minimum 20% green space in lot
    
    # Parking requirements (QCVN 01:2021/BXD)
    parking_car_area: float = 25.0       # 25 m²/car space
    parking_motorcycle_area: float = 3.0  # 3 m²/motorcycle space
    parking_bicycle_area: float = 0.9    # 0.9 m²/bicycle space
    
    # Solver
    solver_time_limit: float = 0.5      # OR-Tools time limit per block (seconds)


@dataclass(frozen=True)
class InfrastructureSettings:
    """Infrastructure planning settings."""
    
    # Electrical
    transformer_radius: float = 300.0   # Effective service radius (m)
    lots_per_transformer: int = 15      # Approximate lots per transformer
    
    # Network
    loop_redundancy_ratio: float = 0.15 # 15% extra edges for loop network safety
    max_connection_distance: float = 500.0  # Max distance for lot connections (m)
    
    # Drainage
    drainage_arrow_length: float = 30.0 # Arrow length for visualization (m)


@dataclass(frozen=True)
class OptimizationSettings:
    """NSGA-II genetic algorithm settings."""
    
    # Population
    population_size: int = 30
    generations: int = 15
    
    # Crossover/Mutation
    crossover_probability: float = 0.7
    mutation_probability: float = 0.3
    eta: float = 20.0  # Distribution index for SBX crossover
    
    # Gene bounds
    # Gene bounds - Very large for industrial estate blocks (100-250m spacing)
    spacing_bounds: Tuple[float, float] = (100.0, 250.0)
    angle_bounds: Tuple[float, float] = (0.0, 90.0)
    
    # Block quality thresholds
    good_block_ratio: float = 0.65      # Ratio for residential/commercial
    fragmented_block_ratio: float = 0.1 # Below this = too small


@dataclass(frozen=True)
class AestheticSettings:
    """Shape quality thresholds for aesthetic optimization (from Beauti_mode)."""
    
    # Rectangularity: area / OBB area (1.0 = perfect rectangle)
    # Relaxed to 0.65 to accept trapezoids from Voronoi slicing
    min_rectangularity: float = 0.65
    
    # Aspect ratio: length / width (lower = more square)
    max_aspect_ratio: float = 4.0
    
    # Minimum lot area to avoid tiny fragments (m²)
    # Accept smaller industrial lots (1000-2000m²) for better land coverage
    min_lot_area: float = 1000.0
    
    # OR-Tools deviation penalty weight (higher = more uniform lots)
    deviation_penalty_weight: float = 50.0
    
    # Enable leftover management (convert poor lots to green space)
    # DISABLED: Row-based subdivision creates clean lots, no need to filter
    enable_leftover_management: bool = False


@dataclass(frozen=True)
class LandUseValidation:
    """Land use validation thresholds (QCVN 01:2021/BXD)."""
    
    # Minimum land allocation percentages
    min_road_ratio: float = 0.15         # Roads ≥ 15% (15-20%)
    min_green_ratio: float = 0.07        # Green/water ≥ 7% (7-15%)
    min_infrastructure_ratio: float = 0.01  # Technical infrastructure ≥ 1% (1-3%)
    min_admin_ratio: float = 0.02        # Admin/service ≥ 2% (2-4%)
    
    # Target land allocation (chuẩn theo yêu cầu)
    target_road_ratio: float = 0.175     # 17.5% roads (middle of 15-20%)
    target_green_ratio: float = 0.11     # 11% green/water (middle of 7-15%)
    target_infra_ratio: float = 0.02     # 2% infrastructure (middle of 1-3%)
    target_admin_ratio: float = 0.03     # 3% admin/service (middle of 2-4%)
    target_lot_ratio: float = 0.60       # 60% lots (middle of 50-70%)
    
    # Green buffer requirements
    green_buffer_width: float = 20.0     # 20m buffer between functional zones
    perimeter_buffer_width: float = 30.0 # 30m green buffer around perimeter


@dataclass
class AlgorithmSettings:
    """Complete algorithm configuration."""
    
    road: RoadSettings = field(default_factory=RoadSettings)
    subdivision: SubdivisionSettings = field(default_factory=SubdivisionSettings)
    infrastructure: InfrastructureSettings = field(default_factory=InfrastructureSettings)
    optimization: OptimizationSettings = field(default_factory=OptimizationSettings)
    aesthetic: AestheticSettings = field(default_factory=AestheticSettings)
    validation: LandUseValidation = field(default_factory=LandUseValidation)
    
    # Random seed for reproducibility
    random_seed: int = 42
    
    @classmethod
    def from_dict(cls, config: dict) -> 'AlgorithmSettings':
        """Create settings from API config dictionary."""
        settings = cls()
        
        # Map API config to internal settings
        if 'min_lot_width' in config:
            settings = cls(
                subdivision=SubdivisionSettings(
                    min_lot_width=config.get('min_lot_width', 20.0),
                    max_lot_width=config.get('max_lot_width', 80.0),
                    target_lot_width=config.get('target_lot_width', 40.0),
                    solver_time_limit=config.get('ortools_time_limit', 0.5),
                ),
                optimization=OptimizationSettings(
                    population_size=config.get('population_size', 30),
                    generations=config.get('generations', 15),
                    spacing_bounds=(
                        config.get('spacing_min', 50.0),
                        config.get('spacing_max', 150.0)
                    ),
                    angle_bounds=(
                        config.get('angle_min', 0.0),
                        config.get('angle_max', 90.0)
                    ),
                ),
                road=RoadSettings(
                    main_width=DEFAULT_SETTINGS.road.main_width,
                    internal_width=config.get('road_width', DEFAULT_SETTINGS.road.internal_width),
                    sidewalk_width=DEFAULT_SETTINGS.road.sidewalk_width,
                    turning_radius=DEFAULT_SETTINGS.road.turning_radius
                )
            )
        
        return settings


# Default settings instance
DEFAULT_SETTINGS = AlgorithmSettings()


# Convenience accessors for backward compatibility
ROAD_MAIN_WIDTH = DEFAULT_SETTINGS.road.main_width
ROAD_INTERNAL_WIDTH = DEFAULT_SETTINGS.road.internal_width
SIDEWALK_WIDTH = DEFAULT_SETTINGS.road.sidewalk_width
TURNING_RADIUS = DEFAULT_SETTINGS.road.turning_radius
SERVICE_AREA_RATIO = DEFAULT_SETTINGS.subdivision.service_area_ratio
MIN_BLOCK_AREA = DEFAULT_SETTINGS.subdivision.min_block_area
MIN_LOT_WIDTH = DEFAULT_SETTINGS.subdivision.min_lot_width
MAX_LOT_WIDTH = DEFAULT_SETTINGS.subdivision.max_lot_width
TARGET_LOT_WIDTH = DEFAULT_SETTINGS.subdivision.target_lot_width
SETBACK_DISTANCE = DEFAULT_SETTINGS.subdivision.setback_distance
FIRE_SAFETY_GAP = DEFAULT_SETTINGS.subdivision.fire_safety_gap
SOLVER_TIME_LIMIT = DEFAULT_SETTINGS.subdivision.solver_time_limit
TRANSFORMER_RADIUS = DEFAULT_SETTINGS.infrastructure.transformer_radius

# Aesthetic thresholds (from Beauti_mode)
MIN_RECTANGULARITY = DEFAULT_SETTINGS.aesthetic.min_rectangularity
MAX_ASPECT_RATIO = DEFAULT_SETTINGS.aesthetic.max_aspect_ratio
MIN_LOT_AREA = DEFAULT_SETTINGS.aesthetic.min_lot_area
DEVIATION_PENALTY_WEIGHT = DEFAULT_SETTINGS.aesthetic.deviation_penalty_weight
ENABLE_LEFTOVER_MANAGEMENT = DEFAULT_SETTINGS.aesthetic.enable_leftover_management
