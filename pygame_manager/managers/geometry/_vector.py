# ======================================== IMPORTS ========================================
from __future__ import annotations
from _core.imports import Iterable, Iterator, Self, Tuple, numbers, np, math
from _core.utils import *

# ======================================== TRANSFORMATION INTERMEDIAIRE ========================================
def _to_vector(vector: VectorObject | Iterable[numbers.Real], fallback: object=None, raised: bool=True, method: str='_to_vector', message: str='Invalid vector argument') -> VectorObject | object | None:
    """tente de convertir si besoin l'objet en Point"""
    if isinstance(vector, VectorObject):
        return vector
    if isinstance(vector, Sequence) and all(isinstance(c, numbers.Real) for c in vector):
        return VectorObject(*vector)
    return fallback if fallback is not None else _raise_error(method, message) if raised else None

# ======================================== OBJET ========================================
class VectorObject:
    """
    Gestionnaire vectoriel

    Fonctionnalités:
        stocker des coordonnées vectorielles toute dimension
        effectuer des opérations vectorielles simplement
    """
    __slots__ = ["_v"]
    PRECISION = 9
    def __init__(self, *components: numbers.Real):
        if len(components) == 0: _raise_error(self, '__init__', 'Vector must have at least 1 component')
        while any(not isinstance(c, numbers.Real) for c in components):
            if len(components) == 1 and isinstance(components[0], Sequence): components = components[0]
            else: _raise_error(self, '__init__', 'Invalid components arguments')
        self._v = np.round(np.array(components, dtype=np.float32), self.PRECISION)

    # ======================================== METHODES FONCTIONNELLES ========================================    
    def __repr__(self) -> str:
        """Représentation du vecteur"""
        return f"Vector({', '.join(map(str, self._v))})"
    
    def __iter__(self) -> Iterator[float]:
        """Itération sur le vecteur"""
        return iter(self.to_tuple())
    
    def __hash__(self) -> int:
       """Renvoie le vecteur hashé"""
       return hash(self.to_tuple())
    
    @staticmethod
    def _compute_rank(matrix: list[list[float]], epsilon: float = 1e-10) -> int:
        """Calcule le rang d'une matrice par élimination de Gauss"""
        if not matrix or not matrix[0]:
            return 0
        
        m = [row[:] for row in matrix]
        rows = len(m)
        cols = len(m[0])
        
        rank = 0
        for col in range(cols):
            pivot_row = None
            for row in range(rank, rows):
                if abs(m[row][col]) > epsilon:
                    pivot_row = row
                    break
            
            if pivot_row is None: # colonne nulle
                continue
            
            m[rank], m[pivot_row] = m[pivot_row], m[rank]     
            for row in range(rank + 1, rows):
                if abs(m[row][col]) > epsilon:
                    factor = m[row][col] / m[rank][col]
                    for c in range(cols):
                        m[row][c] -= factor * m[rank][c]
            rank += 1
        return rank
    
    # ======================================== GETTERS ========================================
    def __getitem__(self, i: int) -> float:
        """Renvoie la composante de rang i du vecteur"""
        if i >= len(self._v): return 0.0
        return float(self._v[i])

    @property
    def x(self) -> float:
        """Renvoie la composante x du vecteur"""
        return self[0]
    
    @property
    def y(self) -> float:
        """Renvoie la composante y du vecteur"""
        return self[1]
    
    @property
    def z(self) -> float:
        """Renvoie la composante z du vecteur"""
        return self[2]
    
    @property
    def array(self) -> np.ndarray:
        """Renvoie le vecteur sous forme d'array numpy"""
        return self._v
    
    @property
    def dim(self) -> int:
        """Renvoie la dimension du vecteur"""
        return self._v.shape[0]
    
    def __len__(self) -> int:
        """Renvoie la dimension du vecteur"""
        return self._v.shape[0]
    
    @property
    def norm(self) -> float:
        """Renvoie la norme du vecteur"""
        return math.sqrt(sum(c**2 for c in self._v))
    
    def __abs__(self) -> float:
        """Renvoie la norme du vecteur"""
        return self.norm
    
    @property
    def normalized(self) -> VectorObject:
        """Renvoie le vecteur normalisé"""
        if self.is_null(): _raise_error(self, 'normalized', 'Cannot normalize null vector')
        return VectorObject(*(self / self.norm))
    
    # ======================================== SETTERS ========================================
    def __setitem__(self, i: int, r: numbers.Real):
        """Fixe la composante de rang i du vecteur"""
        if not isinstance(r, numbers.Real): _raise_error(self, '__setitem__', 'Invalid r argument')
        self.reshape(-i)
        self._v[i] = np.round(np.float32(r), self.PRECISION)

    @x.setter
    def x(self, x: numbers.Real) :
        """Fixe la composante x du vecteur"""
        self[0] = x

    @y.setter
    def y(self, y: numbers.Real):
        """Fixe la composante y du vecteur"""
        self[1] = y

    @z.setter
    def z(self, z: numbers.Real):
        """Fixe la composante z du vecteur"""
        self[2] = z

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: VectorObject) -> VectorObject:
        """addition vectorielle"""
        vector = _to_vector(vector, method='__add__')
        u, v = self.equalized(vector)
        return VectorObject(*(u.array + v.array))

    def __sub__(self, vector: VectorObject) -> VectorObject:
        """Soustraction vectorielle"""
        vector = _to_vector(vector, method='__sub__')
        u, v = self.equalized(vector)
        return VectorObject(*(u.array - v.array))
    
    def __mul__(self, scalar: numbers.Real) -> VectorObject:
        """Multiplication par un scalaire"""
        if not isinstance(scalar, numbers.Real): _raise_error(self, '__mul__', 'Invalid scalar argument')
        return VectorObject(*(self.array * float(scalar)))
    
    def __rmul__(self, scalar: numbers.Real) -> VectorObject:
        """Multiplication par un scalaire (inversé)"""
        if not isinstance(scalar, numbers.Real): _raise_error(self, '__rmul__', 'Invalid scalar argument')
        return VectorObject(*(self.array * float(scalar)))
    
    def __truediv__(self, scalar: numbers.Real) -> VectorObject:
        """Division par un scalaire"""
        if not isinstance(scalar, numbers.Real): _raise_error(self, '__truediv__', 'Invalid scalar argument')
        return VectorObject(*(self.array / float(scalar)))
    
    def __matmul__(self, vector: VectorObject) -> float:
        """Produit scalaire"""
        vector = _to_vector(vector, method='__dot__')
        return self.dot(vector)
    
    def __xor__(self, vector: VectorObject) -> VectorObject:
        """Produit vectoriel"""
        vector = _to_vector(vector, method='__cross__')
        return self.cross(vector)
    
    def __pos__(self) -> VectorObject:
        """Copie"""
        return VectorObject(*self.array)

    def __neg__(self) -> VectorObject:
        """Opposé"""
        return VectorObject(*(-self.array))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, vector: VectorObject) -> bool:
        """Vérifie la correspondance de deux vecteurs"""
        vector = _to_vector(vector, raised=False)
        if vector is None:
            return False
        u, v = self.equalized(vector)
        return all(u[i] == v[i] for i in range(u.dim))
    
    def __ne__(self, vector: object) -> bool:
        """Vérifie la non correspondance de deux vecteurs"""
        if not isinstance(vector, VectorObject):
            return True
        return not self == vector
    
    def __contains__(self, r: numbers.Real) -> bool:
        """Vérifie que le vecteur contienne une composante spécifique"""
        if not isinstance(r, numbers.Real):
            return False
        return float(r) in self.to_tuple()
    
    # ======================================== PREDICATS ========================================
    def is_null(self) -> bool:
        """
        Vérifie que le vecteur soit nul
        """
        return np.all(self._v == 0)
    
    def __bool__(self) -> bool:
        """
        Vérifie que le vecteur ne soit pas nul
        """
        return not self.is_null()
    
    def is_orthogonal(self, vector: VectorObject) -> bool:
        """
        Vérifie l'orthogonalité avec un autre vecteur

        Args:
            vector (VectorObject) : second vecteur
        """
        _to_vector(vector, method='is_orthogonal')
        if self.is_null() or vector.is_null():
            return True
        return np.isclose(self.dot(vector), 0)

    def is_collinear(self, vector: VectorObject) -> bool:
        """
        Vérifie la colinéarité avec un autre vecteur
        
        Args:
            vector (VectorObject) : second vecteur
        """
        vector = _to_vector(vector, method='is_collinear')
        if self.is_null() or vector.is_null():
            return True
        return abs(self.dot(vector)) == self.norm * vector.norm
    
    def is_coplanar(self, *vectors: VectorObject) -> bool:
        """
        Vérifie si les vecteurs sont coplanaires (dans un même plan)
        
        Args:
            vectors (tuple[VectorObject]): vecteurs à tester avec Self
        """
        vectors = list(map(_to_vector, vectors))
        
        equalized = self.equalized(*vectors)
        dim = equalized[0].dim
        
        # toujours coplanaire en 1D / 2D
        if dim <= 2 or len(equalized) < 3:
            return True
        
        # produit mixte pour 3D
        if dim == 3 and len(equalized) == 3:
            v1, v2, v3 = equalized
            return abs(v1.dot(v2.cross(v3))) < 1e-10
        
        # méthode générale : élimination de Gauss
        matrix = [[v[i] for v in equalized] for i in range(dim)]
        return self._compute_rank(matrix) <= 2

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> VectorObject:
        """Renvoie une copie du vecteur"""
        return VectorObject(*self.array)
    
    def to_tuple(self) -> tuple[float]:
        """Renvoie les composantes du vecteur en tuple"""
        return tuple(map(float, self.array))
    
    def to_list(self) -> list[float]:
        """Renvoie les composantes du vecteur en liste"""
        return list(map(float, self.array))
    
    def normalize(self):
        """Normalise le vecteur"""
        self._v = self.normalized.array
    
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
            _raise_error(self, 'reshape', 'Invalid dim argument')
        if dim == 0:            # réduction automatique
            self._v = self._v[: np.max(np.nonzero(self._v)[0]) + 1] if np.any(self._v != 0) else np.array([0.0])
        elif dim < 0:           # au moins dim
            if self.dim < abs(dim): self.reshape(abs(dim))
        elif dim <= self.dim:   # réduction strictement à dim
            self._v = np.array(self._v[:dim])
        else:                   # augmentation strictement à dim
            self._v = np.concatenate([self._v, np.zeros(dim - len(self))])

    def equalized(self, *vectors: VectorObject) -> Tuple[Self, *tuple[VectorObject]]:
        """
        Egalise les dimensions de plusieurs vecteurs

        Args:
            vectors (tuple[VectorObject]) : ensemble de vecteurs à mettre sur la même dimension
        """
        vectors = list(map(_to_vector, vectors))
        if self not in vectors:
            vectors = (self, *vectors)
        dim = max(vectors, key=lambda v: v.dim).dim
        equalized_vectors = []
        for vector in vectors:
            v = vector.copy()
            v.reshape(dim)
            equalized_vectors.append(v)
        return tuple(equalized_vectors)

    def dot(self, vector: VectorObject) -> float:
        """
        Renvoie le produit scalaire des deux vecteurs

        Args:
            vector (VectorObject) : second vecteur
        """
        vector = _to_vector(vector, method='dot')
        u, v = self.equalized(vector)
        return float(np.dot(u.array, v.array))
    
    def cross(self, vector: VectorObject) -> VectorObject:
        """
        Renvoie le produit vectoriel de deux vecteurs

        Args:
            vector (VectorObject) : second vecteur
        """
        vector = _to_vector(vector, method='cross')
        u, v = self.equalized(vector)
        return VectorObject(*np.cross(u.array, v.array))
    
    def angle_with(self, vector: VectorObject, degrees: bool=False) -> float:
        """
        Renvoie l'angle entre deux vecteurs

        Args:
            vector (VectorObject) : second vecteur
            degrees (bool, optional) : conversion en degrée
        """
        vector = _to_vector(vector, method='angle_with')
        if self.is_null() or vector.is_null(): _raise_error(self, 'angle_with', 'Cannot define an angle with null vector')
        angle = float(np.arccos(self.dot(vector) / (self.norm * vector.norm)))
        if degrees:
            return math.degrees(angle)
        return angle

    def projection(self, vector: VectorObject) -> VectorObject:
        """
        Renvoie le projeté vectoriel du vecteur donné sur Self

        Args:
            vecteur (VectorObject) : vecteur à projeter
        """
        vector = _to_vector(vector, method='projection')
        return (vector.dot(self) / self.dot(self)) * self
    
    def distance(self, vector: VectorObject) -> float:
        """
        Distance euclidienne entre deux vecteurs
        
        Args:
            vector (VectorObject) : second vecteur
        """
        vector = _to_vector(vector, method='distance')
        return (self - vector).norm