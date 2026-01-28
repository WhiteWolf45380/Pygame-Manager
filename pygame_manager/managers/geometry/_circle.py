from ._point import PointObject


# ======================================== OBJET ========================================
class CircleObject:
    """
    Object géométrique : Cercle
    """
    def __init__(self, center: PointObject, radius: int|float):
       self._center = center
       self._radius = radius