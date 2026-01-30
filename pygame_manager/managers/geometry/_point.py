# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# Import lazy pour éviter les dépendances circulaires
def _lazy_import_vector():
    from ._vector import VectorObject, _to_vector
    return VectorObject, _to_vector

# ======================================== TRANSFORMATION INTERMEDIAIRE ========================================
def _to_point(point: PointObject | Iterable[Real], fallback: object=None, raised: bool=True, method: str='_to_point', message: str='Invalid point argument'):
    """tente de convertir si besoin l'objet en Point"""
    if isinstance(point, PointObject):
        return point.copy()
    if isinstance(point, Sequence) and all(isinstance(c, Real) for c in point):
        return PointObject(*point)
    return fallback if fallback is not None else _raise_error(PointObject, method, message) if raised else None

# ======================================== OBJET ========================================
class PointObject:
    """
    Object géométrique nD : Point
    """
    __slots__ = ["_pos"]
    PRECISION = 9
    def __init__(self, *coos: Real):
        if len(coos) == 0:
            _raise_error(self, '__init__', 'Point must have at least 1 coordinate')
        while any(not isinstance(c, Real) for c in coos):
            if len(coos) == 1 and isinstance(coos[0], Sequence): coos = coos[0]
            else: _raise_error(self, '__init__', 'Invalid coos arguments')
        self._pos = [round(c, self.PRECISION) for c in list(map(float, coos))]
    
    def __repr__(self) -> str:
        """Représentation du point"""
        return f"Point({', '.join(map(str, self._pos))})"
    
    def __iter__(self) -> Iterator[float]:
        """Itération sur le point"""
        return iter(self.to_tuple())
    
    def __hash__(self) -> int:
       """Renvoie le point hashé"""
       return hash(self.to_tuple())

    # ======================================== GETTERS ========================================
    def __getitem__(self, i: int | slice) -> float | tuple[float]:
        """Renvoie la coordonnée de rang i du point"""
        if isinstance(i, slice):
            return tuple(self._pos[j] for j in range(*i.indices(len(self._pos))))
        return self._pos[i] if i < len(self._pos) else 0.0

    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du point"""
        return self[0]
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du point"""
        return self[1]
    
    @property
    def z(self) -> float:
        """Renvoie la coordonnée z du point"""
        return self[2]
    
    @property
    def dim(self) -> int:
        """Renvoie la dimension du point"""
        return len(self._pos)
    
    def __len__(self) -> int:
        """Renvoie la dimension du point"""
        return len(self._pos)
    
    # ======================================== SETTERS ========================================
    def __setitem__(self, i: int, x: Real):
        """Fixe la coordonnée de rang i du point"""
        if not isinstance(i, int): _raise_error(self, '__setitem__', 'Invalid index argument')
        if not isinstance(x, Real): _raise_error(self, '__setitem__', 'Invalid coordinate argument')
        self.reshape(-i-1)
        self._pos[i] = round(float(x), self.PRECISION)

    @x.setter
    def x(self, x: Real) :
        """Fixe la coordonnée x du point"""
        self[0] = x

    @y.setter
    def y(self, y: Real):
        """Fixe la coordonnée y du point"""
        self[1] = y

    @z.setter
    def z(self, z: Real):
        """Fixe la coordonnée z du point"""
        self[2] = z

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector) -> PointObject:
        """Renvoie l'image du point par le vecteur donné"""
        VectorObject, _to_vector = _lazy_import_vector()
        vector = _to_vector(vector, fallback=NotImplemented)
        if vector is NotImplemented: return NotImplemented
        return self.translate(vector)
    
    def __radd__(self, vector) -> PointObject:
        """Renvoie l'image du point par le vecteur donné"""
        VectorObject, _to_vector = _lazy_import_vector()
        vector = _to_vector(vector, fallback=NotImplemented)
        if vector is NotImplemented: return NotImplemented
        return self.translate(vector)

    def __sub__(self, vector) -> PointObject:
        """Renvoie l'image du point par l'opposé du vecteur"""
        VectorObject, _to_vector = _lazy_import_vector()
        vector = _to_vector(vector, fallback=NotImplemented)
        if vector is NotImplemented: return NotImplemented
        return self.translate(-vector)
    
    def __rsub__(self, point: PointObject):
        """Renvoie le vecteur point -> Self"""
        point = _to_point(point, fallback=NotImplemented)
        if point is NotImplemented: return NotImplemented
        return self.vector_to(point)

    def __pos__(self) -> PointObject:
        """Copie"""
        return PointObject(*self._pos)

    def __neg__(self) -> PointObject:
        """Opposé"""
        return PointObject(*(-c for c in self._pos))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, point: PointObject) -> bool:
        """Vérifie la correspondance de deux points"""
        point = _to_point(point, raised=False, method='__eq__')
        if point is None: return False
        A, B = self.equalized(point)
        return all(A[i] == B[i] for i in range(A.dim))
    
    def __ne__(self, point: PointObject) -> bool:
        """Vérifie la non correspondance de deux points"""
        return not self == point
    
    def __contains__(self, n: Real) -> bool:
        """Vérifie que le point contienne une coordonnée spécifique"""
        if not isinstance(n, Real):
            return False
        return round(float(n), self.PRECISION) in self.to_tuple()
    
    # ======================================== PREDICATS ========================================
    def is_origin(self) -> bool:
        """Vérifie que le point soit l'origine du repère"""
        return all(c == 0 for c in self._pos)
    
    def __bool__(self) -> bool:
        """Vérifie que le point soit valide"""
        return True
    
    def is_aligned(self, *points: PointObject) -> bool:
        """Vérifie que les points soient alignés"""
        points = list(map(_to_point, points))
        if len(points) < 2: return True
        all_points = self.equalized(*points)
        vector0 = all_points[1] - all_points[0]
        if not vector0:
            return all((p - all_points[0]).is_null() for p in all_points[2:])
        return all(vector0.is_collinear(p - all_points[0]) for p in all_points[2:])
    
    def is_close(self, point: PointObject, epsilon: float=1e-10) -> bool:
        """
        Vérifie que les points sont à epsilon près similaires

        Args:
            point (PointObject) : second point
            epsilon (float) : seuil de tolérance d'écart
        """
        p1, p2 = self.equalized(point)
        return all(abs(p2[k] - p1[k]) < epsilon for k in range(p1.dim))
    
    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> PointObject:
        """Renvoie une copie du point"""
        return PointObject(*self._pos)
    
    def to_tuple(self) -> tuple[float]:
        """Renvoie les coordonnées du point en tuple"""
        return tuple(self._pos)
    
    def to_list(self) -> list[float]:
        """Renvoie les coordonnées du point en liste"""
        return list(self._pos)
    
    def to_vector(self):
        """Renvoie le vecteur 0 -> self"""
        VectorObject, _ = _lazy_import_vector()
        return VectorObject(*self)
    
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
            _raise_error(self, 'reshape', 'Invalid dimension argument')
        if dim == 0:
            last_nonzero = next((i for i in reversed(range(len(self._pos))) if self._pos[i] != 0), None)
            self._pos = self._pos[:last_nonzero + 1] if last_nonzero is not None else [0.0]
        elif dim < 0:
            if self.dim < abs(dim): self.reshape(abs(dim))
        elif dim <= self.dim:
            self._pos = self._pos[:dim]
        else:
            self._pos.extend([0.0] * (dim - len(self._pos)))

    def equalized(self, *points: PointObject) -> Tuple[Self, *tuple[PointObject]]:
        """
        Egalise les dimensions du point et de plusieurs autres points

        Args:
            points (tuple[PointObject]) : ensemble des points à mettre sur la même dimension
        """
        points = list(map(_to_point, points))
        if self not in points: points = (self, *points)
        dim = max(points, key=lambda p: p.dim).dim
        equalized_points = []
        for point in points:
            p = point.copy()
            p.reshape(dim)
            equalized_points.append(p)
        return tuple(equalized_points)
    
    def equalized_with_vectors(self, *vectors) -> Tuple[Self, *tuple]:
        """
        Egalise les dimensions du point avec plusieurs vecteurs

        Args:
            vectors (tuple[VectorObject]) : ensemble des vecteurs à mettre sur la même dimension
        """
        VectorObject, _to_vector = _lazy_import_vector()
        vectors = list(map(_to_vector, vectors))
        objects = [self] + vectors
        dim = max(objects, key=lambda v: v.dim).dim
        equalized_objects = []
        for obj in objects:
            o = obj.copy()
            o.reshape(dim)
            equalized_objects.append(o)
        return tuple(equalized_objects)
    
    def distance(self, point: PointObject) -> float:
        """
        Distance euclidienne entre deux points
        
        Args:
            point (PointObject) : second point
        """
        point = _to_point(point, method='distance')
        return (self - point).norm
    
    def vector_to(self, point: PointObject):
        """
        Renvoie le vecteur Self -> point

        Args:
            point (PointObject) : le point d'arrivée
        """
        VectorObject, _ = _lazy_import_vector()
        point = _to_point(point, method='vector_to')
        A, B = self.equalized(point)
        return VectorObject(*(b - a for a, b in zip(A, B)))
    
    def translate(self, vector):
        """
        Renvoie l'image du point par un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        VectorObject, _to_vector = _lazy_import_vector()
        vector = _to_vector(vector)
        A, u = self.equalized_with_vectors(vector)
        return PointObject(*tuple(A[i] + u[i] for i in range(A.dim)))
    
    def midpoint(self, point: PointObject) -> PointObject:
        """
        Renvoie le point central entre Self et point

        Args:
            point (PointObject) : second point
        """
        point = _to_point(point, method='midpoint')
        A, B = self.equalized(point)
        return PointObject(*((A[i] + B[i]) / 2 for i in range(A.dim)))
    
    def barycenter(self, *points: PointObject, weights: Iterable[float]=None) -> PointObject:
        """
        Calcule le barycentre du point à plusieurs points
        
        Args:
            points (tuple[PointObject]) : points à inclure dans le barycentre
            weights (Iterable[float]) : poids associés à chaque point (défaut: poids égaux)
        """
        if not points:
            return self.copy()       
        points = list(map(_to_point, points))
        if weights is not None and not isinstance(weights, Sequence):
            _raise_error(self, 'barycenter', 'Invalid weights argument')
        
        if self not in points:
            points = (self, *points)
        n = len(points)
        
        if weights is None:
            weights = [1.0] * n
        else:
            weights = list(weights)
            if len(weights) != n:
                _raise_error(self, 'barycenter', f'Need {n} weights, got {len(weights)}. Perhaps you forgot self weight as first weight')
            if any(not isinstance(w, Real) for w in weights):
                _raise_error(self, 'barycenter', 'Weights must be numbers')
        
        total_weight = sum(weights)
        if total_weight == 0:
            _raise_error(self, 'barycenter', 'Total weight cannot be zero')
        
        equalized_points = self.equalized(*points)
        dim = equalized_points[0].dim
        barycenter_coords = []
        
        for i in range(dim):
            coord = sum(weights[j] * equalized_points[j][i] for j in range(n)) / total_weight
            barycenter_coords.append(coord)
        
        return PointObject(*barycenter_coords)