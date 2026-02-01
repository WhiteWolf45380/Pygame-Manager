# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

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
    def __add__(self, vector: geometry.Vector) -> geometry.Point:
        """Renvoie l'image du point par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        return self._translate(vector)
    
    def __radd__(self, vector: geometry.Vector) -> geometry.Point:
        """Renvoie l'image du point par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        return self._translate(vector)

    def __sub__(self, vector: geometry.Vector) -> geometry.Point:
        """Renvoie l'image du point par l'opposé du vecteur"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        return self.translate(-vector)
    
    def __rsub__(self, point: geometry.Point) -> geometry.Vector:
        """Renvoie le vecteur point -> Self"""
        point = geometry._to_point(point, raised=False)
        if point is None: return NotImplemented
        return self._vector_to(point)

    def __pos__(self) -> geometry.Point:
        """Copie"""
        return geometry.Point(*self._pos)

    def __neg__(self) -> geometry.Point:
        """Opposé"""
        return geometry.Point(*(-c for c in self._pos))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, point: geometry.Point) -> bool:
        """Vérifie la correspondance de deux points"""
        point = geometry._to_point(point, raised=False)
        if point is None: return False
        self._equalize(point)
        return all(self[i] == point[i] for i in range(self.dim))
    
    def __ne__(self, point: geometry.Point) -> bool:
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
    
    def is_aligned(self, *points: geometry.Point) -> bool:
        """
        Vérifie que les points soient alignés

        Args:
            points (tuple[geometry.Point]) : points dont on veut vérifier l'alignement
        """
        points = list(map(geometry._to_point, points))
        return self._is_aligned(*points)
    
    def _is_aligned(self, *points: geometry.Point) -> bool:
        """Implémentation interne de is_aligned"""
        self._equalize(*points)
        points = (self, *points)
        if len(points) < 2: return True
        vector0 = points[1] - points[0]
        if not vector0:
            return all((p - points[0]).is_null() for p in points[2:])
        return all(vector0._is_collinear(p - points[0]) for p in points[2:])
    
    def is_close(self, point: geometry.Point, epsilon: float=1e-10) -> bool:
        """
        Vérifie que les points sont à epsilon près similaires

        Args:
            point (geometry.Point) : second point
            epsilon (float) : seuil de tolérance d'écart
        """
        if not isinstance(epsilon, Real): _raise_error(self, 'is_close', 'Invalid epsilon argument')
        point = geometry._to_point(point)
        return self._is_close(point, epsilon=epsilon)
    
    def _is_close(self, point: geometry.Point, epsilon: float=1e-10) -> bool:
        """Implémentation interne de is_close"""
        self._equalize(point)
        return all(abs(point[k] - self[k]) < epsilon for k in range(self.dim))
    
    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> geometry.Point:
        """Renvoie une copie du point"""
        return geometry.Point(*self._pos)
    
    def to_tuple(self) -> tuple[float]:
        """Renvoie les coordonnées du point en tuple"""
        return tuple(self._pos)
    
    def to_list(self) -> list[float]:
        """Renvoie les coordonnées du point en liste"""
        return list(self._pos)
    
    def to_vector(self) -> geometry.Vector:
        """Renvoie le vecteur O -> Self"""
        return geometry.Vector(*self)
    
    def reshape(self, dim: int=0):
        """
        Fixe la dimension

        Args:
            dim (int) : dimension souhaitée
                < 0 : au moins |dim| éléments
                = 0 : reshape automatique (suppression des zéros de fin)
                > 0 : strictement dim éléments
        """
        if not isinstance(dim, int): _raise_error(self, 'reshape', 'Invalid dimension argument')
        if dim == 0:
            last_nonzero = next((i for i in reversed(range(len(self._pos))) if self._pos[i] != 0), None)
            self._pos = self._pos[:last_nonzero + 1] if last_nonzero is not None else [0.0]
        elif dim < 0:
            if self.dim < abs(dim): self.reshape(abs(dim))
        elif dim <= self.dim:
            self._pos = self._pos[:dim]
        else:
            self._pos.extend([0.0] * (dim - len(self._pos)))

    def equalize(self, *objs: Reshapable):
        """
        Egalise les dimensions du point et de plusieurs autres objets géométriques

        Args:
            objs (tuple[Reshapable]) : ensemble des objets à mettre sur la même dimension
        """
        if any(not isinstance(obj, Reshapable) for obj in objs): _raise_error(self, 'equalize', 'Invalid objs arguments')
        self._equalize(*objs)
    
    def _equalize(self, *objs: Reshapable):
        """Implémentation interne de equalize"""
        if self not in objs: objs = (self, *objs)
        dim = max(objs, key=lambda o: o.dim).dim
        for obj in objs:
            obj.reshape(dim)
    
    def distance(self, point: geometry.Point) -> float:
        """
        Distance euclidienne entre deux points
        
        Args:
            point (geometry.Point) : second point
        """
        point = geometry._to_point(point, method='distance')
        return self._distance(point)
    
    def _distance(self, point: geometry.Point) -> float:
        """Implémentation interne de distance"""
        return (self - point).norm
    
    def vector_to(self, point: geometry.Point) -> geometry.Vector:
        """
        Renvoie le vecteur Self -> point

        Args:
            point (geometry.Point) : le point d'arrivée
        """
        point = geometry._to_point(point, method='vector_to')
        return self._vector_to(point)
    
    def _vector_to(self, point: geometry.Point) -> geometry.Vector:
        """Implémentation interne de vector_to"""
        self._equalize(point)
        return geometry.Vector(*(b - a for a, b in zip(self, point)))
    
    def translate(self, vector: geometry.Vector) -> geometry.Point:
        """
        Renvoie l'image du point par un vecteur

        Args:
            vector (geometry.Vector) : vecteur de translation
        """
        vector = geometry._to_vector(vector)
        return self._translate(vector)
    
    def _translate(self, vector: geometry.Vector) -> geometry.Point:
        """Implémentation interne de translate"""
        return geometry.Point(*tuple(self[i] + vector[i] for i in range(self.dim)))
    
    def midpoint(self, point: geometry.Point) -> geometry.Point:
        """
        Renvoie le point central entre Self et point

        Args:
            point (geometry.Point) : second point
        """
        point = geometry._to_point(point, method='midpoint')
        return self._midpoint(point)
    
    def _midpoint(self, point: geometry.Point) -> geometry.Point:
        """Implémentation interne de midpoint"""
        self._equalize(point)
        return geometry.Point(*((self[i] + point[i]) / 2 for i in range(self.dim)))
    
    def barycenter(self, *points: geometry.Point, weights: Iterable[float]=None) -> geometry.Point:
        """
        Calcule le barycentre du point à plusieurs points
        
        Args:
            points (tuple[geometry.Point]) : points à inclure dans le barycentre
            weights (Iterable[float]) : poids associés à chaque point (défaut: poids égaux)
        """
        if not points:
            return self.copy()       
        points = list(map(geometry._to_point, points))
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
        
        return self._barycenter(*points, weights)
    
    def _barycenter(self, *points: geometry.Point, weights: Iterable[float]=None) -> geometry.Point:
        """Implémentation interne de barycenter"""
        n = len(points)
        
        total_weight = sum(weights)
        if total_weight == 0:
            _raise_error(self, 'barycenter', 'Total weight cannot be zero')
        
        self.equalize(*points)
        dim = points[0].dim
        barycenter_coords = []
        
        for i in range(dim):
            coord = sum(weights[j] * points[j][i] for j in range(n)) / total_weight
            barycenter_coords.append(coord)
        
        return geometry.Point(*barycenter_coords)