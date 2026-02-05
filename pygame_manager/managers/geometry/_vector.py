# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class VectorObject:
    """
    Objet géométrique nD : Vecteur
    """
    __slots__ = ["_v"]
    PRECISION = 9
    def __init__(self, *components: Real):
        if len(components) == 0: _raise_error(self, '__init__', 'Vector must have at least 1 component')
        while any(not isinstance(c, Real) for c in components):
            if len(components) == 1 and isinstance(components[0], Sequence): components = components[0]
            else: _raise_error(self, '__init__', 'Invalid components arguments')
        self._v = np.round(np.array(components, dtype=np.float32), self.PRECISION)

    def __repr__(self) -> str:
        """Représentation du vecteur"""
        return f"Vector({', '.join(map(str, self._v))})"
    
    def __iter__(self) -> Iterator[float]:
        """Itération sur le vecteur"""
        return iter(self.to_tuple())
    
    def __hash__(self) -> int:
       """Renvoie le vecteur hashé"""
       self.reshape(0)
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
            
            if pivot_row is None:
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
    def __getitem__(self, i: int| slice) -> float | tuple[float]:
        """Renvoie la composante de rang i du vecteur"""
        if isinstance(i, slice):
            return tuple(float(self._v[j]) for j in range(*i.indices(len(self._v))))
        return float(self._v[i]) if i < len(self._v) else 0.0

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
        return self._v.copy()
    
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
        return float(np.linalg.norm(self._v))
    
    def __abs__(self) -> float:
        """Renvoie la norme du vecteur"""
        return self.norm
    
    @property
    def normalized(self) -> context.geometry.Vector:
        """Renvoie le vecteur normalisé"""
        if self.is_null(): _raise_error(self, 'normalized', 'Cannot normalize null vector')
        return context.geometry.Vector(*(self / self.norm))
    
    # ======================================== SETTERS ========================================
    def __setitem__(self, i: int, r: Real):
        """Fixe la composante de rang i du vecteur"""
        if not isinstance(r, Real): _raise_error(self, '__setitem__', 'Invalid r argument')
        self.reshape(-i-1)
        self._v[i] = np.round(np.float32(r), self.PRECISION)

    @x.setter
    def x(self, x: Real) :
        """Fixe la composante x du vecteur"""
        self[0] = x

    @y.setter
    def y(self, y: Real):
        """Fixe la composante y du vecteur"""
        self[1] = y

    @z.setter
    def z(self, z: Real):
        """Fixe la composante z du vecteur"""
        self[2] = z
    
    @norm.setter
    def norm(self, norm: Real):
        """Fixe la norme du vecteur"""
        self._v = (np.float32(norm) * self.normalized).array

    def set_norm(self, norm: Real):
        """Fixe la norme du vecteur"""
        self._v = (np.float32(norm) * self.normalized).array

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """addition vectorielle"""
        vector = context.geometry._to_vector(vector, method='__add__', raised=False)
        if vector is None: return NotImplemented
        self._equalize(vector)
        return context.geometry.Vector(*(self.array + vector.array))

    def __sub__(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """Soustraction vectorielle"""
        vector = context.geometry._to_vector(vector, method='__sub__', raised=False)
        if vector is None: return NotImplemented
        self._equalize(vector)
        return context.geometry.Vector(*(self.array - vector.array))
    
    def __mul__(self, scalar: Real) -> context.geometry.Vector:
        """Multiplication par un scalaire"""
        if not isinstance(scalar, Real): return NotImplemented
        return context.geometry.Vector(*(self.array * float(scalar)))
    
    def __rmul__(self, scalar: Real) -> context.geometry.Vector:
        """Multiplication par un scalaire (inversé)"""
        if not isinstance(scalar, Real): return NotImplemented
        return context.geometry.Vector(*(self.array * float(scalar)))
    
    def __truediv__(self, scalar: Real) -> context.geometry.Vector:
        """Division par un scalaire"""
        if not isinstance(scalar, Real): return NotImplemented
        if scalar == 0: _raise_error(self, '__truediv__', 'Cannot divide by zero')
        return context.geometry.Vector(*(self.array / float(scalar)))
    
    def __rtruediv__(self, vector: context.geometry.Vector) -> float:
        """Rapport scalaire entre deux vecteurs colinéaires"""
        vector = context.geometry._to_vector(vector, method='__rtruediv__', raised=False)
        if vector is None: return NotImplemented
        self._equalize(vector)
        if not self.is_collinear(vector): return NotImplemented
        for i in range(self.dim):
            if self[i] != 0: return vector[i] / self[i]
        return 0.0
    
    def __matmul__(self, vector: context.geometry.Vector) -> float:
        """Produit scalaire"""
        vector = context.geometry._to_vector(vector, method='__dot__', raised=False)
        if vector is None: return NotImplemented
        return self._dot(vector)
    
    def __xor__(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """Produit vectoriel"""
        vector = context.geometry._to_vector(vector, method='__cross__', raised=False)
        if vector is None: return NotImplemented
        return self._cross(vector)
    
    def __pos__(self) -> context.geometry.Vector:
        """Copie"""
        return context.geometry.Vector(*self.array)

    def __neg__(self) -> context.geometry.Vector:
        """Opposé"""
        return context.geometry.Vector(*(-self.array))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, vector: context.geometry.Vector) -> bool:
        """Vérifie la correspondance de deux vecteurs"""
        vector = context.geometry._to_vector(vector, raised=False)
        if vector is None:return False
        self._equalize(vector)
        return all(self[i] == vector[i] for i in range(self.dim))
    
    def __ne__(self, vector: context.geometry.Vector) -> bool:
        """Vérifie la non correspondance de deux vecteurs"""
        return not self == vector
    
    def __contains__(self, r: Real) -> bool:
        """Vérifie que le vecteur contienne une composante spécifique"""
        if not isinstance(r, Real):
            return False
        return float(r) in self.to_tuple()
    
    # ======================================== PREDICATS ========================================
    def is_null(self) -> bool:
        """Vérifie que le vecteur soit nul"""
        return np.all(self._v == 0)
    
    def __bool__(self) -> bool:
        """Vérifie que le vecteur ne soit pas nul"""
        return not self.is_null()
    
    def is_orthogonal(self, vector: context.geometry.Vector) -> bool:
        """
        Vérifie l'orthogonalité avec un autre vecteur

        Args:
            vector (context.geometry.Vector) : second vecteur
        """
        context.geometry._to_vector(vector, method='is_orthogonal')
        return self._is_orthogonal(vector)
    
    def _is_orthogonal(self, vector: context.geometry.Vector) -> bool:
        """Implémentation interne de is_orthogonal"""
        if self.is_null() or vector.is_null():
            return True
        return np.isclose(self._dot(vector), 0)

    def is_collinear(self, vector: context.geometry.Vector) -> bool:
        """
        Vérifie la colinéarité avec un autre vecteur
        
        Args:
            vector (context.geometry.Vector) : second vecteur
        """
        vector = context.geometry._to_vector(vector, method='is_collinear')
        return self._is_collinear(vector)
    
    def _is_collinear(self, vector: context.geometry.Vector) -> bool:
        """Implémentation interne de is_collinear"""
        if self.is_null() or vector.is_null():
            return True
        return abs(self._dot(vector)) == self.norm * vector.norm
    
    def is_coplanar(self, *vectors: context.geometry.Vector) -> bool:
        """
        Vérifie si les vecteurs sont coplanaires (dans un même plan)
        
        Args:
            vectors (tuple[context.geometry.Vector]): vecteurs à tester avec Self
        """
        vectors = list(map(context.geometry._to_vector, vectors))
        return self._is_coplanar(*vectors)
    
    def _is_coplanar(self, *vectors: context.geometry.Vector) -> bool:
        """Implémentation interne de is_coplanar"""
        self._equalize(*vectors)
        vectors = (self, *vectors)
        dim = vectors[0].dim
        
        # toujours coplanaire en 1D / 2D
        if dim <= 2 or len(vectors) < 3:
            return True
        
        # produit mixte pour 3D
        if dim == 3 and len(vectors) == 3:
            v1, v2, v3 = vectors
            return abs(v1._dot(v2._cross(v3))) < 1e-10
        
        # méthode générale : élimination de Gauss
        matrix = [[v[i] for v in vectors] for i in range(dim)]
        return self._compute_rank(matrix) <= 2

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> context.geometry.Vector:
        """Renvoie une copie du vecteur"""
        return context.geometry.Vector(*self.array)
    
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
        if not isinstance(dim, int): _raise_error(self, 'reshape', 'Invalid dim argument')
        if dim == 0:
            self._v = self._v[: np.max(np.nonzero(self._v)[0]) + 1] if np.any(self._v != 0) else np.array([0.0], dtype=np.float32)
        elif dim < 0:
            if self.dim < abs(dim): self.reshape(abs(dim))
        elif dim <= self.dim:
            self._v = np.array(self._v[:dim], dtype=np.float32)
        else:
            self._v = np.concatenate([self._v, np.zeros(dim - len(self), dtype=np.float32)])

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
        if not any(obj.dim != objs[0].dim for obj in objs): return objs
        objs = {self, *objs}
        dim = max(objs, key=lambda o: o.dim).dim
        for obj in objs:
            obj.reshape(dim)

    def dot(self, vector: context.geometry.Vector) -> float:
        """
        Renvoie le produit scalaire des deux vecteurs

        Args:
            vector (context.geometry.Vector) : second vecteur
        """
        vector = context.geometry._to_vector(vector, method='dot')
        return self._dot(vector)
    
    def _dot(self, vector: context.geometry.Vector) -> float:
        """Implémentation interne de dot"""
        self._equalize(vector)
        return float(np.dot(self.array, vector.array))
    
    def cross(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """
        Renvoie le produit vectoriel de deux vecteurs

        Args:
            vector (context.geometry.Vector) : second vecteur
        """
        vector = context.geometry._to_vector(vector, method='cross')
        return self._cross(vector)
    
    def _cross(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """Implémentation interne de cross"""
        self._equalize(vector)
        return context.geometry.Vector(*np.cross(self.array, vector.array))
    
    def angle_with(self, vector: context.geometry.Vector, degrees: bool=False) -> float:
        """
        Renvoie l'angle entre deux vecteurs

        Args:
            vector (context.geometry.Vector) : second vecteur
            degrees (bool, optional) : conversion en degrée
        """
        vector = context.geometry._to_vector(vector, method='angle_with')
        if self.is_null() or vector.is_null(): _raise_error(self, 'angle_with', 'Cannot define an angle with null vector')
        return self._angle_with(vector, degrees=degrees)
    
    def _angle_with(self, vector: context.geometry.Vector, degrees: bool=False) -> float:
        """Implémentation interne de angle_with"""
        cos_angle = self._dot(vector) / (self.norm * vector.norm)
        cos_angle = max(-1.0, min(1.0, cos_angle))  # Clamp pour éviter les erreurs d'arrondi
        angle = float(np.arccos(cos_angle))
        if degrees:
            return math.degrees(angle)
        return angle

    def projection(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """
        Renvoie le projeté vectoriel du vecteur donné sur Self

        Args:
            vecteur (context.geometry.Vector) : vecteur à projeter
        """
        vector = context.geometry._to_vector(vector, method='projection')
        return self._projection(vector)
    
    def _projection(self, vector: context.geometry.Vector) -> context.geometry.Vector:
        """Implémentation interne de projection"""
        return (vector._dot(self) / self._dot(self)) * self
    
    def distance(self, vector: context.geometry.Vector) -> float:
        """
        Distance euclidienne entre deux vecteurs
        
        Args:
            vector (context.geometry.Vector) : second vecteur
        """
        vector = context.geometry._to_vector(vector, method='distance')
        return self._distance(vector)
    
    def _distance(self, vector: context.geometry.Vector) -> float:
        """Implémentation interne de distance"""
        return (self - vector).norm