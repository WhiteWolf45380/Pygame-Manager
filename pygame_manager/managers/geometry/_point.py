from ._vector import VectorObject


# ======================================== OBJET ========================================
class PointObject:
    """
    Object géométrique : Point
    """
    __slots__ = ["_pos"]
    def __init__(self, *coos):
        if len(coos) == 0:
            self._raise_error('__init__', 'Point must have at least 1 coordinate')
        self._pos = list(coos)
    
    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __repr__(self) -> str:
        """Représentation du point"""
        return f"Point({', '.join(map(str, self._pos))})"
    
    def __iter__(self) -> iter:
        """Itération sur le point"""
        return iter(self._pos)
    
    def __hash__(self):
       """Renvoie le point hashable"""
       return hash(self.to_tuple())

    # ======================================== GETTERS ========================================
    def __getitem__(self, i: int) -> float:
        """Renvoie la coordonnée de rang i du point"""
        if i >= len(self._pos):
            return 0.0
        return self._pos[i]

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
    def __setitem__(self, i: int, x: int|float):
        """Fixe la coordonnée de rang i du point"""
        if not isinstance(x, (int, float)):
            self._raise_error('__setitem__', 'Coordinate must be an integer or float')
        self.reshape(-i)
        self._pos[i] = x

    @x.setter
    def x(self, x: int|float) :
        """Fixe la coordonnée x du point"""
        self[0] = x

    @y.setter
    def y(self, y: int|float):
        """Fixe la coordonnée y du point"""
        self[1] = y

    @z.setter
    def z(self, z: int|float):
        """Fixe la coordonnée z du point"""
        self[2] = z

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: VectorObject) -> object:
        """Renvoie l'image du point par le vecteur donné"""
        return self.translate(vector)

    def __sub__(self, other: object) -> VectorObject:
        """Renvoie le vecteur self -> other"""
        return other.to(self)

    def __pos__(self) -> object:
        """Copie"""
        return PointObject(*self._pos)

    def __neg__(self) -> object:
        """Opposé"""
        return PointObject(*(-c for c in self._pos))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, other: object) -> bool:
        """Vérifie la correspondance de deux points"""
        if not isinstance(other, PointObject):
            return False
        return self.to_tuple() == other.to_tuple()
    
    def __ne__(self, other: object) -> bool:
        """Vérifie la non correspondance de deux vecteurs"""
        if not isinstance(other, PointObject):
            return True
        return self.to_tuple() != other.to_tuple()
    
    def __contains__(self, x: int|float) -> bool:
        """Vérifie que le point contienne une coordonnée spécifique"""
        if not isinstance(x, (int, float)):
            self._raise_error('__contains__', 'Value must be an integer or float')
        return x in self.to_tuple()
    
    # ======================================== PREDICATS ========================================
    def is_origin(self) -> bool:
        """
        Vérifie que le point soit l'origine du repère
        """
        return all(c == 0 for c in self._pos)
    
    def __bool__(self) -> bool:
        """
        Vérifie que le vecteur ne soit pas l'origine du repère
        """
        return not self.is_origin()
    
    def is_aligned(self, *points):
        """
        Vérifie que les points soient alignés
        """
        if not all(isinstance(p, PointObject) for p in points):
            self._raise_error('aligned', 'Points must be PointObjects')
        if len(points) < 2:
            return True
        all_points = self.equalized(*points)
        vector0 = all_points[1] - all_points[0]
        if vector0.is_null():
            return all((p - all_points[0]).is_null() for p in all_points[2:])
        return all(vector0.is_collinear(p - all_points[0]) for p in all_points[2:])
    
    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> object:
        """Renvoie une copie du point"""
        return PointObject(*self._pos)
    
    def to_tuple(self) -> tuple:
        """Renvoie les coordonnées du point en tuple"""
        return tuple(self._pos)
    
    def to_list(self) -> list:
        """Renvoie les coordonnées du point en liste"""
        return list(self._pos)
    
    def to_vector(self) -> VectorObject:
        """Renvoie le vecteur 0 -> self"""
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
            self._raise_error('reshape', 'Dimension must be a positive integer')
        if dim == 0:            # réduction automatique
            last_nonzero = next((i for i in reversed(range(len(self._pos))) if self._pos[i] != 0), None)
            self._pos = self._pos[:last_nonzero + 1] if last_nonzero is not None else [0.0]
        elif dim < 0:           # au moins dim
            if self.dim < abs(dim): self.reshape(abs(dim))
        elif dim <= self.dim:   # réduction strictement à dim
            self._pos = self._pos[:dim]
        else:                   # augmentation strictement à dim
            self._pos.extend([0] * (dim - len(self._pos)))

    def equalized(self, *points: tuple[object] | list[object]) -> tuple[object]:
        """
        Egalise les dimensions du point et de plusieurs autres points

        Args:
            points (tuple[PointObject]) : ensemble des points à mettre sur la même dimension
        """
        if not all(isinstance(p, PointObject) for p in points):
            self._raise_error('equalized', 'Points must be PointObjects')
        points = (self, *points)
        dim = max(points, key=lambda p: p.dim).dim
        equalized_points = []
        for point in points:
            p = point.copy()
            p.reshape(dim)
            equalized_points.append(p)
        return tuple(equalized_points)
    
    def equalized_with_vectors(self, *vectors: tuple[VectorObject] | list[VectorObject]) -> tuple[VectorObject]:
        """
        Egalise les dimensions du point avec plusieurs vecteurs

        Args:
            vectors (Iterable[VectorObject]) : ensemble des vecteurs à mettre sur la même dimension
        """
        if not all(isinstance(v, VectorObject) for v in vectors):
            self._raise_error('equalized_with_vectors', 'Vectors must be VectorObjects')
        if self not in vectors:
            vectors = (self, *vectors)
        dim = max(vectors, key=lambda v: v.dim).dim
        equalized_vectors = []
        for vector in vectors:
            v = vector.copy()
            v.reshape(dim)
            equalized_vectors.append(v)
        return tuple(equalized_vectors)
    
    def distance(self, other: object) -> float:
        """
        Distance euclidienne entre deux points
        
        Args:
            other (PointObject) : second point
        """
        if not isinstance(other, PointObject):
            return self._raise_error('distance', 'Other must be a PointObject')
        return (self - other).norm
    
    def to(self, other: object) -> VectorObject:
        """
        Renvoie le vecteur self -> point

        Args:
            other (PointObject) : le point d'arrivé
        """
        if not isinstance(other, PointObject):
            self._raise_error('to', 'Other must be a PointObject')
        A, B = self.equalized(other)
        return VectorObject(*(b - a for a, b in zip(A, B)))
    
    def translate(self, vector: VectorObject) -> object:
        """
        Renvoie l'image du point par un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        if not isinstance(vector, VectorObject):
            self._raise_error('translate', 'Vector must be a VectorObject')
        A, u = self.equalized_with_vectors(vector)
        return PointObject(*tuple(A[i] + u[i] for i in range(A.dim)))
    
    def midpoint(self, other: object) -> object:
        """
        Renvoie le point central entre self et other

        Args:
            other (PointObject) : second point
        """
        if not isinstance(other, PointObject):
            self._raise_error('midpoint', 'Other must be a PointObject')
        A, B = self.equalized(other)
        return PointObject(*((A[i] + B[i]) / 2 for i in range(A.dim)))
    
    def barycenter(self, *points: tuple[object] | list[object], weights: list[float] | tuple[float] | None = None) -> object:
        """
        Calcule le barycentre du point à plusieurs points
        
        Args:
            points : points à inclure dans le barycentre
            weights: poids associés à chaque point (défaut: poids égaux)
        """
        if not points:
            return self.copy()       
        if not all(isinstance(p, PointObject) for p in points):
            self._raise_error('barycenter', 'Points must be PointObjects')
        
        if self not in points:
            points = (self, *points)
        n = len(points)
        
        if weights is None:     # poids égaux par défaut
            weights = [1.0] * n
        else:                   # pondération par des poids spécifiques
            weights = list(weights)
            if len(weights) != n:
                self._raise_error('barycenter', f'Need {n} weights, got {len(weights)}. Perhaps you forgot self weight as first weight')
            if any(not isinstance(w, (int, float)) for w in weights):
                self._raise_error('barycenter', 'Weights must be numbers')
        
        total_weight = sum(weights)
        if total_weight == 0:
            self._raise_error('barycenter', 'Total weight cannot be zero')
        
        equalized_points = self.equalized(*points)
        dim = equalized_points[0].dim
        barycenter_coords = []
        
        for i in range(dim):
            coord = sum(weights[j] * equalized_points[j][i] for j in range(n)) / total_weight
            barycenter_coords.append(coord)
        
        return PointObject(*barycenter_coords)