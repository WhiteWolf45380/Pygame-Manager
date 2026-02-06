"""Module contenant tous les types du framework pour le typage"""
# ========================================== ENTITIES ==========================================
from .managers.entities import (
    Entity,
    SegmentEntity,
    LineEntity,
    CircleEntity,
    RectEntity,
    PolygonEntity
)

# ========================================== GEOMETRY ==========================================
from .managers.geometry import (
    VectorObject,
    PointObject,
    SegmentObject,
    LineObject,
    CircleObject,
    RectObject,
    PolygonObject
)

# ========================================== PANELS ==========================================
from .managers.panels import Panel

# ========================================== STATES ==========================================
from .managers.states import State

# ========================================== UI ==========================================
from .managers.ui import (
    TextObject, 
    ImageObject, 
    SectionObject, 
    OverlayObject,
    RectButtonObject,
    CircleButtonObject,
    RectSelectorObject,
    CircleSelectorObject,
    TextCaseObject,
)

# ========================================== EXPOSITION ==========================================
__all__ = [
    # Entities
    "Entity",
    "SegmentEntity",
    "LineEntity",
    "CircleEntity",
    "RectEntity",
    "PolygonEntity",

    # Geometry
    "VectorObject",
    "PointObject",
    "SegmentObject",
    "LineObject",
    "CircleObject",
    "RectObject",
    "PolygonObject",

    # Panels
    "Panel",

    # States
    "State",
    
    # UI
    "TextObject", 
    "ImageObject", 
    "SectionObject", 
    "OverlayObject",
    "RectButtonObject",
    "CircleButtonObject",
    "RectSelectorObject",
    "CircleSelectorObject",
    "TextCaseObject",
]