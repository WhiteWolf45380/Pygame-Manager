from ._vector import VectorObject
from ._point import PointObject
from ._line import LineObject
from ._rect import RectObject
from ._circle import CircleObject
from ._polygon import PolygonObject


# ======================================== GESTIONNAIRE ========================================
class GeometryManager:
    """
    Gesionnaire de la géométrie

    Fonctionnalités:
        manipulation vectorielle
    """
    def __init__(self):
        self.Vector = VectorObject
        self.Point = PointObject
        self.Line = LineObject
        self.Rect = RectObject
        self.Circle = CircleObject
        self.Polygon = PolygonObject

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")


# ======================================== INSTANCE ========================================
geometry_manager = GeometryManager()