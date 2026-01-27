import numpy as np
import math


# ======================================== GESTIONNAIRE ========================================
class VectorObject:
    """
    Gestionnaire vectoriel

    Fonctionnalités:
        stocker des coordonnées vectorielles toute dimension
        effectuer des opérations vectorielles simplement
    """
    __slots__ = ["_v"]
    def __init__(self, *components):
        if len(components) == 0:
            self._raise_error('__init__', 'Vector must have at least 1 component')
        self._v = np.array(components, dtype=np.float32)

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __repr__(self) -> str:
        """Représentation du vecteur"""
        return f"Vector({', '.join(map(str, self._v))})"
    
    def __len__(self) -> int:
        """Renvoie la dimension du vecteur"""
        return self._v.shape[0]
    
    def __iter__(self) -> iter:
        """Itération sur le vecteur"""
        return iter(self._v)
    
    def __hash__(self):
       """Renvoie le vecteur hashable"""
       return hash(self.to_tuple())
    
    # ======================================== GETTERS ========================================
    @property
    def array(self) -> np.array:
        """Renvoie le vecteur sous forme d'array numpy"""
        return self._v

    @property
    def x(self) -> float:
        """Renvoie la composante x du vecteur"""
        return self._v[0]
    
    @property
    def y(self) -> float:
        """Renvoie la composante y du vecteur"""
        return self._v[1]
    
    @property
    def z(self) -> float:
        """Renvoie la composante z du vecteur"""
        return self._v[2]
    
    def __getitem__(self, i) -> float:
        """Renvoie la composante de rang i du vecteur"""
        if i >= len(self._v):
            return 0.0
        return self._v[i]
    
    @property
    def dim(self) -> int:
        """Renvoie la dimension du vecteur"""
        return self._v.shape[0]
    
    @property
    def norm(self) -> float:
        """Renvoie la norme du vecteur"""
        return math.sqrt(sum(x**2 for x in self._v))
    
    def __abs__(self):
        """Renvoie la norme du vecteur"""
        return self.norm
    
    @property
    def normalized(self) -> object:
        """Renvoie le vecteur normalisé"""
        if self.is_null():
           self._raise_error('normalized', 'Cannot normalize null vector')
        return VectorObject(*(self / self.norm))
    
    # ======================================== SETTERS ========================================
    @x.setter
    def x(self, x) :
        """Fixe la composante x du vecteur"""
        if not isinstance(x, (int, float, np.float32)):
            self._raise_error('set_x', 'Component must be an integer or float')
        self._v[0] = x

    @y.setter
    def y(self, y):
        """Fixe la composante y du vecteur"""
        if not isinstance(y, (int, float, np.float32)):
            self._raise_error('set_y', 'Component must be an integer or float')
        self._v[1] = y

    @z.setter
    def z(self, z: int|float):
        """Fixe la composante z du vecteur"""
        if not isinstance(z, (int, float, np.float32)):
            self._raise_error('set_z', 'Component must be an integer or float')
        self._v[2] = z

    def __setitem__(self, i, x):
        """Fixe la composante de rang i du vecteur"""
        if not isinstance(x, (int, float, np.float32)):
            self._raise_error('__setitem__', 'Component must be an integer or float')
        self._v[i] = x

    # ======================================== OPERATIONS ========================================
    def __add__(self, other: object) -> object:
        """addition vectorielle"""
        if not isinstance(other, VectorObject):
            self._raise_error('__add__', 'Invalid addition')
        u, v = self.equalized(self, other)
        return VectorObject(*(u.array + v.array))

    def __sub__(self, other: object) -> object:
        """Soustraction vectorielle"""
        if not isinstance(other, VectorObject):
            self._raise_error('__add__', 'Invalid substraction')
        u, v = self.equalized(self, other)
        return VectorObject(*(u.array - v.array))
    
    def __mul__(self, other: int|float) -> object:
        """Multiplication par un scalaire"""
        if not isinstance(other, (int, float, np.float32)):
            self._raise_error('__mul__', 'Invalid multiplication')
        return VectorObject(*(self.array * other))
    
    def __rmul__(self, other: int|float) -> object:
        """Multiplication par un scalaire (inversé)"""
        if not isinstance(other, (int, float, np.float32)):
            self._raise_error('__rmul__', 'Invalid multiplication')
        return VectorObject(*(self.array * other))
    
    def __truediv__(self, other: int|float) -> object:
        """Division par un scalaire"""
        if not isinstance(other, (int, float, np.float32)):
            self._raise_error('__truediv__', 'Invalid division')
        return VectorObject(*(self.array / other))
    
    def __matmul__(self, other: object) -> float:
        """Produit scalaire"""
        if not isinstance(other, VectorObject):
            self._raise_error('__matmul__', 'Invalid dot')
        return self.dot(other)
    
    def __xor__(self, other: object) -> object:
        """Produit vectoriel"""
        if not isinstance(other, VectorObject):
            self._raise_error('__xor__', 'Invalid cross product')
        return self.cross(other)
    
    def __pos__(self) -> object:
        """Copie"""
        return VectorObject(*self.array)

    def __neg__(self) -> object:
        """Opposé"""
        return VectorObject(*(-self.array))
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, other: object) -> bool:
        """Vérifie la correspondance de deux vecteurs"""
        if not isinstance(other, VectorObject):
            return False
        return self.to_tuple() == other.to_tuple()
    
    def __ne__(self, other: object) -> bool:
        """Vérifie la non correspondance de deux vecteurs"""
        if not isinstance(other, VectorObject):
            return True
        return self.to_tuple() != other.to_tuple()
    
    def __contains__(self, x: int|float) -> bool:
        """Vérifie que le vecteur contient une composante spécifique"""
        if not isinstance(x, (int, float, np.float32)):
            self._raise_error('__contains__', 'Value must be an integer or float')
        return x in tuple(self._v)
    
    # ======================================== PREDICATS ========================================
    def is_null(self):
        """
        Vérifie que le vecteur soit nul
        """
        return np.all(self._v == 0)
    
    def __bool__(self):
        """
        Vérifie que le vecteur ne soit pas nul
        """
        return not self.is_null
    
    def is_orthogonal(self, other: object) -> bool:
        """
        Vérifie l'orthogonalité avecun autre vecteur

        Args:
            other (VectorObject) : second vecteur
        """
        if self.is_null() or other.is_null():
           return True
        return np.isclose(self.dot(other), 0)

    def is_collinear(self, other: object) -> bool:
        """
        Vérifie la colinéarité avec un autre vecteur
        
        Args:
            other (VectorObject) : second vecteur
        """
        if self.is_null() or other.is_null():
           return True
        return np.isclose(abs(self.dot(other)), self.norm * other.norm)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self):
        """Renvoie une copie du vecteur"""
        return VectorObject(*self.array)
    
    def to_tuple(self):
        """Renvoie les composantes du vecteurs en tuple"""
        return tuple(self.array)
    
    def to_list(self):
        """Renvoie les composantes du vecteurs en liste"""
        return list(self.array)
    
    def normalize(self):
        """Normalise le vecteur"""
        self._v = self.normalized
    
    def reshape(self, dim: int=-1):
        """
        Fixe la dimension

        Args:
            dim (int) : dimension souhaitée
        """
        if not isinstance(dim, int) or (dim <= 0 and dim != -1):
            self._raise_error('reshape', 'Dimension must be a positive integer')
        if dim == -1:
            self._v = self._v[: np.max(np.nonzero(self._v)[0]) + 1] if np.any(self._v != 0) else np.array([0])
        elif dim <= self.dim:
            self._v = np.array(self._v[:dim])
        else:
            self._v = np.concatenate([self._v, np.zeros(dim - len(self))])

    def equalized(self, *vectors: tuple[object]) -> tuple:
        """
        Egalise les dimensions des deux vecteurs

        Args:
            vectors (tuple[VectorObject]) : ensemble des vecteurs à mettre sur la même dimension
        """
        dim = max(vectors, key=lambda v: v.dim).dim
        equalized_vectors = []
        for vector in vectors:
            v = vector.copy()
            v.reshape(dim)
            equalized_vectors.append(v)
        return tuple(equalized_vectors)

    def dot(self, other: object) -> float:
        """
        Renvoie le produit scalaire des deux vecteurs

        Args:
            other (VectorObject) : second vecteur
        """
        if not isinstance(other, VectorObject):
            self._raise_error('dot', 'Invalid dot')
        u, v = self.equalized(self, other)
        return np.dot(u.array, v.array)
    
    def cross(self, other: object) -> object:
        """
        Renvoie le produit vectoriel de deux vecteurs

        Args:
            other (VectorObject) : second vecteur
        """
        if not isinstance(other, VectorObject):
            self._raise_error('cross', 'Invalid dot')
        u, v = self.equalized(self, other)
        return VectorObject(*np.cross(u.array, v.array))
    
    def angle_with(self, other: object, degrees: bool=False) -> float:
        """
        Renvoie l'angle entre deux vecteurs

        Args:
            other (VectorObject) : second vecteur
            degrees (bool, optional) : conversion en degrée
        """
        if not isinstance(other, VectorObject):
            self._raise_error('angle_with', 'Invalid dot')
        if self.is_null() or other.is_null():
           self._raise_error('angle_with', 'Cannot define an angle with null vector')
        angle = np.arccos(self.dot(other) / (self.norm * other.norm))
        if degrees:
            return math.degrees(angle)
        return angle

    def project(self, other: object) -> object:
        """
        Renvoie le projeté du vecteur donné

        Args:
            other (VectorObject) : vecteur à projeter
        """
        if not isinstance(other, VectorObject):
            return self._raise_error('angle_with', 'Invalid dot')
        return (self.dot(other) / other.dot(other)) * other
    
    def distance(self, other: object) -> float:
        """D
        istance euclidienne entre deux vecteurs
        
        Args:
            other (VectorObject) : vecteur à projeter
        """
        if not isinstance(other, VectorObject):
            return self._raise_error('distance', 'Invalid distance')
        return (self - other).norm