from ._point import PointObject
from ._vector import VectorObject


# ======================================== OBJET ========================================
class LineObject:
    """
    Object géométrique : Droite
    """
    __slots__ = ["_origin", "_vector"]
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
    
    def get_cartesian_equation(self) -> dict:
        """Renvoie l'équation cartésienne en 2D : ax + by + c = 0"""
        line = self.copy().reshape(2)
        u, v = line._vector.x, line._vector.y
        x0, y0 = line._origin.x, line._origin.y
        # vecteur normal (-v, u)
        a, b = -v, u
        c = -(a * x0 + b * y0)
        return {"a": a, "b": b, "c": c}

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
        self._origin, self._vector = self._origin.equalized_with_vectors(vector)
    
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
        A, B = self._origin.equalized(point)
        return self._vector.is_collinear(B - A)
    
    def is_orthogonal(self, line: object) -> bool:
        """Vérifie si deux droites sont orthogonales"""
        return self._vector.is_orthogonal(line.get_vector())
    
    def is_parallel(self, line: object) -> bool:
        """Vérifie si deux droites sont parallèles"""
        return self._vector.is_collinear(line.get_vector())
    
    def is_secant(self, line: object) -> bool:
        """Vérifie si deux droites sont sécantes"""
        if not isinstance(line, LineObject):
            return False
        return not self.is_parallel(line) and self.intersect(line) is not None

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

    def equalized(self, *lines: tuple[object]) -> tuple[object]:
        """
        Egalise les dimensions de la droite et plusieurs autres droites

        Args:
            lines (tuple[LineObject]) : ensemble des droites à mettre sur la même dimension
        """
        if not all(isinstance(d, LineObject) for d in lines):
            self._raise_error('equalized', 'lines arguments must be LineObject')
        if self not in lines:
            lines = (self, *lines)
        dim = max(lines, key=lambda l: l.dim).dim
        equalized_lines = []
        for line in lines:
            l = line.copy()
            l.reshape(dim)
            equalized_lines.append(l)
        return tuple(equalized_lines)

    def equalized_with_objects(self, *objects: tuple[PointObject | VectorObject]) -> tuple[PointObject | VectorObject]:
        """
        Egalise les dimensions de la droite et de plusieurs autres points ou vecteurs

        Args:
            objects (tuple[PointObject|VectorObject]) : ensemble des objets géométriques à mettre sur la même dimension
        """
        if not all(isinstance(o, (PointObject, VectorObject)) for o in objects):
            self._raise_error('equalized_with_objects', 'objects arguments must be PointObject or VectorObject')
        objects = (self, *objects)
        dim = max(objects, key=lambda o: o.dim).dim
        equalized_objects = []
        for obj in objects:
            o = obj.copy()
            o.reshape(dim)
            equalized_objects.append(o)
        return tuple(equalized_objects)
    
    def point(self, t: float) -> PointObject:
        """Renvoie le point de paramètre t : A + t*u"""
        if not isinstance(t, (int, float)):
            self._raise_error("point", "t must be a number")
        return self._origin + self._vector * t
    
    def project(self, point: PointObject) -> PointObject:
        """Renvoie le projeté d'un point sur la droite"""
        if not isinstance(point, PointObject):
            self._raise_error("project", "point argument must be PointObject")
        d, P = self.equalized_with_objects(point)
        A, v = d.get_origin(), d.get_vector()
        AP = P - A
        return A + (AP.dot(v) / v.dot(v)) * v

    def distance(self, point: PointObject) -> float:
        """Renvoie la distance entre un point et une droite"""
        if not isinstance(point, PointObject):
            self._raise_error("distance", "point argument must be PointObject")
        return point.distance(self.project(point))

    def intersection(self, line: object) -> PointObject:
        """Renvoie le point d'intersection de deux droites"""
        if not isinstance(line, LineObject):
            self._raise_error("intersect", "line argument must be LineObject")
        
        # si parallèles, pas d'intersection unique
        if self.is_parallel(line):
            return
        
        d1, d2 = self.equalized(line)
        P1, u1 = d1.get_origin(), d1.get_vector()
        P2, u2 = d2.get_origin(), d2.get_vector()

        v = P2 - P1
        if not v.is_coplanar(u1, u2):   # droites non coplanaires
            return None

        for i in range(d1.dim):
            for j in range(i + 1, d1.dim):             
                det = u1[i] * (-u2[j]) - u1[j] * (-u2[i])
                
                if abs(det) > 1e-10:  # système non dégénéré
                    t = (v[i] * (-u2[j]) - v[j] * (-u2[i])) / det
                    return P1 + u1 * t
                
    def angle_with(self, line: object) -> float:
        """Renvoie l'angle entre deux droites (en radians)"""
        if not isinstance(line, LineObject):
            self._raise_error("angle_with", "line argument must be LineObject")
        return self._vector.angle_with(line.get_vector())

    def symmetry(self, point: PointObject) -> PointObject:
        """Renvoie le symétrique d'un point par rapport à la droite"""
        if not isinstance(point, PointObject):
            self._raise_error("symmetry", "point argument must be PointObject")
        H = self.project(point)
        return H + (H - point)

    def translate(self, vector: VectorObject):
        """Translate la droite selon un vecteur"""
        if not isinstance(vector, VectorObject):
            self._raise_error("translate", "vector argument must be VectorObject")
        self._origin = self._origin + vector