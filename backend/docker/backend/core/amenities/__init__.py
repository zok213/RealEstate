"""
Amenities module for industrial zone layout.

Contains generators for:
- Water features (lakes, ponds)
- Central parks with roundabouts
- Row house patterns for residential zones
"""

from .water_generator import create_lakes, create_water_feature
from .central_park import create_central_park, create_roundabout

__all__ = [
    'create_lakes',
    'create_water_feature', 
    'create_central_park',
    'create_roundabout'
]
