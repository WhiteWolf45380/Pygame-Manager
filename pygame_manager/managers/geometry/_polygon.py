# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class PolygonObject:
    """
    Object géométrique 2D : Polygone
    """
    __slots__ = ["_vertexs"]
    def __init__(self, *points: tuple):
        self._vertexs = list(points)