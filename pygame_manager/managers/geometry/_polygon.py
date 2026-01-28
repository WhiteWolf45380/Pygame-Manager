from ._point import PointObject


# ======================================== OBJET ========================================
class PolygonObject:
    """
    Object géométrique : Polygone
    """
    __slots__ = ["_vertexs"]
    def __init__(self, *points: tuple[PointObject]):
        self._vertexs = list(points)