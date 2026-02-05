# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class SegmentObject:
    """
    Object géométrique nD : Segment
    """
    __slots__ = ["_start", "_end"]
    def __init__(self, start: context.geometry.Point, end: context.geometry.Point):
        # point de départ
        self._start = context.geometry._to_point(start, copy=True)

        # point d'arrivée
        self._end = context.geometry._to_point(end, copy=True)

    def __repr__(self) -> str:
        """Représentation du segment"""
        return f"Segment(P1{self._start.to_tuple()}, P2{self._end.to_tuple()})"
    
    def __hash__(self) -> int:
        """Renvoie du segment hashé"""
        return hash(frozenset([hash(self._start), hash(self._end)]))
    
    # ======================================== GETTERS ========================================
    @property
    def dim(self) -> int:
        """Renvoie la dimension du segment"""
        return self._start.dim

    def __len__(self) -> int:
        """Renvoie la dimension du segment"""
        return self._start.dim
    
    def __getitem__(self, i: int) -> context.geometry.Point:
        """Renvoie l'une des deux extremités du segment"""
        if isinstance(i, slice): return NotImplemented
        if isinstance(i, int) and i in (0, 1):
            return self._start if i == 0 else self._end
        _raise_error(self, '__getitem__', 'Invalid index')

    def get_start(self) -> context.geometry.Point:
        """Renvoie la première extremité du segment"""
        return self._start.copy()
    
    @property
    def P1(self) -> context.geometry.Point:
        """Renvoie la première extremité du segment"""
        return self._start.copy()

    def get_end(self) -> context.geometry.Point:
        """Renvoie la seconde extremité du segment"""
        return self._end.copy()
    
    @property
    def P2(self) -> context.geometry.Point:
        """Renvoie la seconde extremité du segment"""
        return self._end.copy()
    
    @property
    def midpoint(self) -> context.geometry.Point:
        """Renvoie le point au milieu du segment"""
        return self._start + 0.5 * (self._end - self._start)
    
    def get_vector(self) -> context.geometry.Vector:
        """Renvoie un vecteur directeur normalisé du segment"""
        return (self._end - self._start).normalized
    
    @property
    def length(self) -> float:
        """Renvoie la longueur du segment"""
        return (self._end - self._start).norm

    # ======================================== SETTERS ========================================
    def set_start(self, point: context.geometry.Point):
        """Fixe la première extremité du segment"""
        self._start = context.geometry._to_point(point, copy=True)
        self._start._equalize(self._end)

    @P1.setter
    def P1(self, point: context.geometry.Point):
        """Fixe la première extremité du segment"""
        self._start = context.geometry._to_point(point, copy=True)
        self._start._equalize(self._end)
    
    def set_end(self, point: context.geometry.Point):
        """Fixe la seconde extremité du segment"""
        self._end = context.geometry._to_point(point, copy=True)
        self._end._equalize(self._start)
    
    @P2.setter
    def P2(self, point: context.geometry.Point):
        """Fixe la seconde extremité du segment"""
        self._end = context.geometry._to_point(point, copy=True)
        self._end._equalize(self._start)
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, segment: context.geometry.Segment) -> bool:
        """Vérifie la correspondance de deux segments"""
        if not isinstance(segment, context.geometry.Segment): return False
        return (self._start == segment._start and self._end == segment._end) or (self._start == segment._end and self._end == segment._start)
    
    def __ne__(self, segment: context.geometry.Segment) -> bool:
        """Vérifie la non correspondance de deux segments"""
        return not self == segment
    
    def __contains__(self, point: context.geometry.Point) -> bool:
        """Vérifie qu'un point soit compris dans le segment"""
        return self._contains(context.geometry._to_point(point))
    
    # ======================================== PREDICATS ========================================
    def contains(self, point: context.geometry.Point) -> bool:
        """
        Vérifie qu'un point soit compris dans le segment

        Args:
            point (context.geometry.Point) : point à vérifier
        """        
        point = context.geometry._to_point(point)
        return self._contains(point)
    
    def _contains(self, point: context.geometry.Point) -> bool:
        """Implémentation interne de contains"""        
        self._start._equalize(point)
        u, v = self.get_vector(), point - self._start
        
        if not u._is_collinear(v):
            return False
        
        for i in range(u.dim):
            if u[i] != 0:
                t = v[i] / u[i]
                return 0 <= t <= self.length
        return True
    
    def is_orthogonal(self, segment: context.geometry.Segment) -> bool:
        """
        Vérifie que le segment est orthogonal à un autre segment

        Args:
            segment (context.geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, context.geometry.Segment): 
            _raise_error(self, 'is_orthogonal', 'Invalid segment argument')
        return self._is_orthogonal(segment)
    
    def _is_orthogonal(self, segment: context.geometry.Segment) -> bool:
        """Implémentation interne de is_orthogonal"""
        return self.get_vector()._is_orthogonal(segment.get_vector())
    
    def is_parallel(self, segment: context.geometry.Segment) -> bool:
        """
        Vérifie si le segment est parallèle à un autre segment
        
        Args:
            segment (context.geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, context.geometry.Segment): 
            _raise_error(self, 'is_parallel', 'Invalid segment argument')
        return self._is_parallel(segment)
    
    def _is_parallel(self, segment: context.geometry.Segment) -> bool:
        """Implémentation interne de is_parallel"""
        return self.get_vector()._is_collinear(segment.get_vector())
    
    def is_secant(self, segment: context.geometry.Segment) -> bool:
        """
        Vérifie si le segment est sécant avec un autre segment
        
        Args:
            segment (context.geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, context.geometry.Segment): 
            _raise_error(self, 'is_secant', 'Invalid segment argument')
        return self._is_secant(segment)
    
    def _is_secant(self, segment: context.geometry.Segment) -> bool:
        """Implémentation interne de is_secant"""
        return not self._is_parallel(segment) and self._intersection(segment) is not None

    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: context.geometry.Point) -> bool:
        """
        Vérifie qu'un point touche le segment
        
        Args:
            point (context.geometry.Point) : segment à vérifier
        """
        point = context.geometry._to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: context.geometry.Point) -> bool:
        """Implémentation interne de collidepoint"""
        return self._contains(point)
    
    def collidesegment(self, segment: context.geometry.Segment) -> bool:
        """
        Vérifie que deux segments se touchent

        Args:
            segment (context.geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, context.geometry.Segment): 
            _raise_error(self, 'is_orthogonal', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: context.geometry.Segment) -> bool:
        """Implémentation interne de collidesegment"""
        return self.intersection(segment) is not None
    
    def collideline(self, line: context.geometry.Line) -> bool:
        """Vérifie qu'une ligne touche le segment"""
        if not isinstance(line, context.geometry.Line):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line: context.geometry.Line) -> bool:
        """Implémentation interne de collideline"""
        return line._collidesegment(self)
    
    def collidecircle(self, circle: context.geometry.Circle) -> bool:
        """Vérifie qu'un cercle touche le segment"""
        if not isinstance(circle, context.geometry.Circle):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)
    
    def _collidecircle(self, circle: context.geometry.Circle) -> bool:
        """Implémentation interne de collidecircle"""
        return circle._collidesegment(self)
    
    def colliderect(self, rect: context.geometry.Rect) -> bool:
        """Vérifie qu'un rectangle touche le segment"""
        if not isinstance(rect, context.geometry.Rect):
            _raise_error(self, 'colliderect', 'Invalid rect argument')
        return self._colliderect(rect)
    
    def _colliderect(self, rect: context.geometry.Rect) -> bool:
        """Implémentation interne de colliderect"""
        return rect._collidesegment(self)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> context.geometry.Segment:
        """Renvoie une copie du segment"""
        return _deepcopy(self)
    
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
        self._start.reshape(dim)
        self._end.reshape(dim)

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
    
    def project(self, point: context.geometry.Point) -> context.geometry.Point:
        """
        Renvoie le projeté d'un point sur le segment

        Args:
            point (context.geometry.Point) : point à projeter
        """
        point = context.geometry._to_point(point)
        return self._project(point)
    
    def _project(self, point: context.geometry.Point) -> context.geometry.Point:
        """Implémentation interne de project"""
        self.equalize(point)
        
        A = self._start
        B = self._end
        AB = B - A
        AP = point - A
        
        if AB.is_null():
            return A.copy()
        
        t = AP.dot(AB) / AB.dot(AB)
        t = max(0, min(1, t))
        
        return A + t * AB

    def distance(self, point: context.geometry.Point) -> float:
        """
        Renvoie la distance entre un point et le segment

        Args:
            point (context.geometry.Point) : point distant
        """
        point = context.geometry._to_point(point)
        return self._distance(point)
    
    def _distance(self, point: context.geometry.Point) -> float:
        """Implémentation interne de distance"""
        return point._distance(self._project(point))

    def intersection(self, segment: context.geometry.Segment) -> context.geometry.Point | None:
        """
        Renvoie le point d'intersection du segment et d'un autre segment

        Args:
            segment (context.geometry.Segment) : second segment
        """
        if not isinstance(segment, context.geometry.Segment):
            _raise_error(self, "intersection", "Invalid segment argument")
        return self._intersection(segment)
    
    def _intersection(self, segment: context.geometry.Segment) -> context.geometry.Point | None:
        """Implémentation interne de intersection"""            
        # si parallèles, pas d'intersection unique
        if self.is_parallel(segment):
            return None
        
        self.equalize(segment)
        P1, u1 = self._start, self._end - self._start
        P2, u2 = segment._start, segment._end - segment._start

        v = P2 - P1
        if not v.is_coplanar(u1, u2):
            return None

        for i in range(self.dim):
            for j in range(i + 1, self.dim):             
                det = u1[i] * (-u2[j]) - u1[j] * (-u2[i])
                
                if abs(det) > 1e-10:
                    t = (v[i] * (-u2[j]) - v[j] * (-u2[i])) / det
                    s = (v[i] * u1[j] - v[j] * u1[i]) / det

                    if 0 <= t <= 1 and 0 <= s <= 1:
                        return P1 + t * u1
                    else:
                        return None
        return None
                
    def angle_with(self, segment: context.geometry.Segment) -> float:
        """
        Renvoie l'angle entre deux segments (en radians)

        Args:
            segment (context.geometry.Segment) : second segment
        """
        if not isinstance(segment, context.geometry.Segment):
            _raise_error(self, "angle_with", "Invalid segment argument")
        return self._angle_with(segment)
    
    def _angle_with(self, segment: context.geometry.Segment) -> float:
        """Implémentation interne de angle_with"""
        return self.get_vector()._angle_with(segment.get_vector())

    def translate(self, vector: context.geometry.Vector) -> context.geometry.Segment:
        """
        Translate le segment selon un vecteur

        Args:
            vector (context.geometry.Vector) : vecteur de translation
        """
        vector = context.geometry._to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: context.geometry.Vector) -> context.geometry.Segment:
        """Implémentation interne de translate"""
        self._start = self._start + vector
        self._end = self._end + vector