from ._point import PointObject
from ._vector import VectorObject


# ======================================== OBJET ========================================
class LineObject:
    """
    Object géométrique : Droite
    """
    __slots__ = ["_point", "_vector"]
    def __init__(self, point: PointObject, vector: VectorObject):
        if not isinstance(point, PointObject):
            self._raise_error("__init__", "point argument must be PointObject")
        if not isinstance(vector, VectorObject):
            self._raise_error("__init__", "vector argument must be VectorObject")
        if vector.is_null():
            self._raise_error("__init__", "direction vector cannot be null vector")
        self._origin, self._vector = point.equalized_with_vectors(vector)
    
    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __repr__(self) -> str:
        """Représentation de la droite"""
        return f"Line({self._origin.__repr__}, {self._vector.__repr__})"
    
    # ======================================== GETTERS ========================================
    @property
    def dim(self) -> int:
        """Renvoie la dimension du point"""
        return self._origin.dim

    def __len__(self) -> int:
        """Renvoie la dimension de la droite"""
        return self._origin.dim

    def get_origin(self) -> PointObject:
        """Renvoie l'origine de la droite"""
        return self._origin
    
    def get_vector(self) -> VectorObject:
        """Renvoie un vecteur directeur de la droite"""
        return self._vector

    # ======================================== SETTERS ========================================
    def set_origin(self, point: PointObject):
        """Modifie l'origine de la droite"""
        if not isinstance(point, PointObject):
            self._raise_error("set_origin", "point argument must be PointObject")
        self._origin, self._vector = point.equalized_with_vectors(self._vector)
    
    def set_vector(self, vector: VectorObject):
        """Modifie le vecteur directeur de la droite"""
        if not isinstance(vector, VectorObject):
            self._raise_error("set_vector", "vector argument must be VectorObject")
        if vector.is_null():
            self._raise_error("set_vector", "direction vector cannot be null vector")
        self._origin, self._vector = self._origin.equalized_with_vectors(self._vector)
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, line: object) -> bool:
        """Vérifie la correspondance de deux droites"""
        if not isinstance(line, LineObject):
            return False
        return (self._origin in line and self._vector.is_collinear(line.get_vector()))
    
    def __ne__(self, line: object) -> bool:
        """Vérifie la non correspondance de deux droites"""
        if not isinstance(line, LineObject):
            return True
        return not self.__eq__(line)
    
    def __contains__(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans la droite'"""
        return self.contains(point)
    
    # ======================================== PREDICATS ========================================
    def contains(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans la droite"""
        if not isinstance(point, PointObject):
            self._raise_error("contains", "point argument must be PointObject")
        A, B = self.equalized(self._origin, point)
        return self._vector.is_collinear(B - A)
    
    def is_orthogonal(self, line: object) -> bool:
        """Vérifie que la droite soit orthogonale à une autre"""
        return self._vector.is_orthogonal(line.get_vector())
    
    def is_parallel(self, line: object) -> bool:
        """Vérifie que la droite soit parallèle à une autre"""
        return self._vector.is_collinear(line.get_vector())

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self):
        """Renvoie une copie de la droite"""
        return LineObject(self._origin, self._vector)
    
    def reshape(self, dim: int=0):
        """
        Fixe la dimension

        Args:
            dim (int) : dimension souhaitée
                < 0 : au moins |dim| éléments
                = 0 : reshape automatique (suppression des zéros de fin)
                > 0 : strictement dim éléments
        """
        if not isinstance(dim, int):
            self._raise_error('reshape', 'Dimension must be a positive integer')
        self._origin.reshape(dim)
        self._vector.reshape(dim)

    def equalized(self, *objects: tuple[PointObject | VectorObject]) -> tuple[PointObject | VectorObject]:
        """
        Egalise les dimensions de la droite et de plusieurs autres points ou vecteurs

        Args:
            objects (tuple[PointObject|VectorObject]) : ensemble des objets géométriques à mettre sur la même dimension
        """
        if not all(isinstance(o, (PointObject, VectorObject)) for o in objects):
            self._raise_error('equalized', 'objects argument must be Point or Vector Objects')
        objects = (self, *objects)
        dim = max(objects, key=lambda p: p.dim).dim
        equalized_objects = []
        for obj in objects:
            o = obj.copy()
            o.reshape(dim)
            equalized_objects.append(o)
        return tuple(equalized_objects)
    
    def project(self, point: PointObject) -> PointObject:
        """Renvoie le projeté d'un point sur la droite"""
        if not isinstance(point, PointObject):
            self._raise_error("project", "point argument must be PointObject")
        d, P = self.equalized(point)
        A, v = d.get_origin(), d.get_vector()
        AP = P - A
        return A + (AP.dot(v) / v.dot(v)) * v

    def distance(self, point: PointObject) -> float:
        """Renvoie la distance entre un point et une droite"""
        if not isinstance(point, PointObject):
            self._raise_error("distance", "point argument must be PointObject")
        return point.distance(self.project(point))

    def intersect(self, line: object) -> PointObject:
        """Renvoie le point d'intersection de deux droites"""
        if not isinstance(line, LineObject):
            self._raise_error("intersect", "line argument must be LineObject")
        
        if self.is_parallel(line):
            if self == line:
                self._raise_error("intersect", "lines are coincident (infinite intersections)")
            return None
        
        d1, d2 = self.equalized(line)
        A1, u1 = d1.get_origin(), d1.get_vector()
        A2, u2 = d2.get_origin(), d2.get_vector()
        
        # Système : A1 + t*u1 = A2 + s*u2
        # En 2D : résolution simple
        if d1.dim == 2:
            # u1.x * t - u2.x * s = A2.x - A1.x
            # u1.y * t - u2.y * s = A2.y - A1.y
            det = u1[0] * (-u2[1]) - u1[1] * (-u2[0])
            if abs(det) < 1e-10:
                self._raise_error("intersect", "lines do not intersect in 2D")
            
            dx = A2[0] - A1[0]
            dy = A2[1] - A1[1]
            t = (dx * (-u2[1]) - dy * (-u2[0])) / det
            return A1 + u1 * t
        
        # En dimension > 2 : pas toujours d'intersection (droites non coplanaires)
        # Il faudrait vérifier la coplanarité et résoudre le système
        self._raise_error("intersect", "intersection in dimension > 2 not yet implemented")