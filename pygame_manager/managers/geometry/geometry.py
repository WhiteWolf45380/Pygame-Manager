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
    
    # ======================================== GENERATIONS PARTICULIERES ========================================
    def line_from_two_points(self, P1: PointObject, P2: PointObject) -> LineObject:
        """Crée une droite à partir de deux points"""
        if not isinstance(P1, PointObject) or not isinstance(P2, PointObject):
            self._raise_error("line_from_two_points", "Both arguments must be PointObject")
        if P1 == P2:
            self._raise_error("line_from_two_points", "Points must be different")
        return LineObject(P1, P2 - P1)

    def line_from_cartesian(self, a: float, b: float, c: float) -> LineObject:
        """
        Crée une droite à partir de l'équation cartésienne ax + by + c = 0
        Fonctionne uniquement en 2D
        """
        if a == 0 and b == 0:
           self._raise_error("line_from_cartesian", "a and b cannot both be null")
        if b != 0:
            point = PointObject(0, -c/b)
        else:
            point = PointObject(-c/a, 0)        
        vector = VectorObject(-b, a)   
        return LineObject(point, vector)


# ======================================== INSTANCE ========================================
geometry_manager = GeometryManager()