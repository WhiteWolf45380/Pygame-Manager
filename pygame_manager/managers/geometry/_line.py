from ._point import PointObject
from ._vector import VectorObject


# ======================================== OBJET ========================================
class LineObject:
    """
    Object géométrique : Droite
    """
    def __init__(self, point: PointObject, vector: VectorObject):
        self._point = point
        self._vector = vector