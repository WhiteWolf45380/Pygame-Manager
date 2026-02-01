# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *
from ._point import PointObject, _to_point
from ._vector import VectorObject, _to_vector

# ======================================== OBJET ========================================
class SegmentObject:
    """
    Object géométrique nD : Segment
    """
    __slots__ = ["_start", "_end", "_color", "_width", "_dashed", "_dash", "_gap"]
    def __init__(self, start: PointObject, end: PointObject):
        # point de départ
        self._start = _to_point(start, copy=True)

        # point d'arrivée
        self._end = _to_point(end, copy=True)

        # paramètres d'affichage
        self._color = (0, 0, 0)
        self._width = 1
        self._dashed = False
        self._dash = 10
        self._gap = 6
    
    def __repr__(self) -> str:
        """Représentation du segment"""
        return f"Segment(P1{self._start.to_tuple()}, P2{self._end.to_tuple()})"
    
    def __hash__(self) -> int:
        """Renvoie du segment hashé"""
        return hash(frozenset([self._start.to_tuple(), self._end.to_tuple()]))
    
    # ======================================== GETTERS ========================================
    @property
    def dim(self) -> int:
        """Renvoie la dimension du segment"""
        return self._start.dim

    def __len__(self) -> int:
        """Renvoie la dimension du segment"""
        return self._start.dim
    
    def __getitem__(self, i: int) -> PointObject:
        """Renvoie l'une des deux extremités du segment"""
        if isinstance(i, slice): return NotImplemented
        if isinstance(i, int) and i in (0, 1):
            return self._start if i == 0 else self._end
        _raise_error(self, '__getitem__', 'Invalid index')

    def get_start(self) -> PointObject:
        """Renvoie la première extremité du segment"""
        return self._start.copy()
    
    @property
    def P1(self) -> PointObject:
        """Renvoie la première extremité du segment"""
        return self._start.copy()

    def get_end(self) -> PointObject:
        """Renvoie la seconde extremité du segment"""
        return self._end.copy()
    
    @property
    def P2(self) -> PointObject:
        """Renvoie la seconde extremité du segment"""
        return self._end.copy()
    
    @property
    def midpoint(self) -> PointObject:
        """Renvoie le point au milieu du segment"""
        return self._start + 0.5 * (self._end - self._start)
    
    def get_vector(self) -> VectorObject:
        """Renvoie un vecteur directeur normalisé du segment"""
        return (self._end - self._start).normalized
    
    @property
    def length(self) -> float:
        """Renvoie la longueur du segment"""
        return (self._end - self._start).norm
    
    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur d'affichage"""
        return self._color
    
    @property
    def width(self) -> int:
        """Renvoie la largeur d'affichage"""
        return self._width
    
    @property
    def dashed(self) -> bool:
        """Vérifie si l'affichage du segment est segmenté"""
        return self._dashed
    
    @property
    def dash(self) -> int:
        """Renvoie la longueur des segments"""
        return self._dash
    
    @property
    def gap(self) -> int:
        """Renvoie la longueur des espaces inter-segments"""
        return self._gap

    # ======================================== SETTERS ========================================
    def set_start(self, point: PointObject):
        """Fixe la première extremité du segment"""
        self._start = _to_point(point, copy=True)
        self._start(self._end)

    @P1.setter
    def P1(self, point: PointObject):
        """Fixe la première extremité du segment"""
        self._start = _to_point(point, copy=True)
        self._start(self._end)
    
    def set_end(self, point: PointObject):
        """Fixe la seconde extremité du segment"""
        self._end = _to_point(point, copy=True)
        self._end(self._start)
    
    @P2.setter
    def P2(self, point: PointObject):
        """Fixe la seconde extremité du segment"""
        self._end = _to_point(point, copy=True)
        self._end(self._start)

    @color.setter
    def color(self, color: pygame.Color):
        """Fixe la couleur d'affichage"""
        self._color = _to_color(color)

    @width.setter
    def width(self, width: int):
        """Fixe la largeur d'affichage"""
        if not isinstance(width, int) or width <= 0:
            _raise_error(self, 'set_width', 'Invalid width argument')
        self._width = width

    @dashed.setter
    def dashed(self, value: bool):
        """Active ou non l'affichage segmenté"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_dashed', 'Invalid value argument')
        self._dashed = value

    @dash.setter
    def dash(self, length: int):
        """Fixe la longueur des segments"""
        if not isinstance(length, int) or length <= 0:
            _raise_error(self, 'set_dash', 'Invalid length argument')
        self._dash = length
    
    # ======================================== COMPARATEURS ========================================
    def __eq__(self, segment: SegmentObject) -> bool:
        """Vérifie la correspondance de deux segments"""
        if not isinstance(segment, SegmentObject): return False
        return (self._start == segment._start and self._end == segment._end) or (self._start == segment._end and self._end == segment._start)
    
    def __ne__(self, segment: SegmentObject) -> bool:
        """Vérifie la non correspondance de deux segments"""
        return not self == segment
    
    def __contains__(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans le segment"""
        return self._contains(_to_point(point))
    
    # ======================================== PREDICATS ========================================
    def contains(self, point: PointObject) -> bool:
        """
        Vérifie qu'un point soit compris dans le segment

        Args:
            point (PointObject) : point à vérifier
        """        
        point = _to_point(point)
        return self._contains(point)
    
    def _contains(self, point: PointObject) -> bool:
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
    
    def is_orthogonal(self, segment: SegmentObject) -> bool:
        """
        Vérifie que le segment est orthogonal à un autre segment

        Args:
            segment (SegmentObject) : segment à vérifier
        """
        if not isinstance(segment, SegmentObject): 
            _raise_error(self, 'is_orthogonal', 'Invalid segment argument')
        return self._is_orthogonal(segment)
    
    def _is_orthogonal(self, segment: SegmentObject) -> bool:
        """Implémentation interne de is_orthogonal"""
        return self.get_vector()._is_orthogonal(segment.get_vector())
    
    def is_parallel(self, segment: SegmentObject) -> bool:
        """
        Vérifie si le segment est parallèle à un autre segment
        
        Args:
            segment (SegmentObject) : segment à vérifier
        """
        if not isinstance(segment, SegmentObject): 
            _raise_error(self, 'is_parallel', 'Invalid segment argument')
        return self._is_parallel(segment)
    
    def _is_parallel(self, segment: SegmentObject) -> bool:
        """Implémentation interne de is_parallel"""
        return self.get_vector()._is_collinear(segment.get_vector())
    
    def is_secant(self, segment: SegmentObject) -> bool:
        """
        Vérifie si le segment est sécant avec un autre segment
        
        Args:
            segment (SegmentObject) : segment à vérifier
        """
        if not isinstance(segment, SegmentObject): 
            _raise_error(self, 'is_secant', 'Invalid segment argument')
        return self._is_secant(segment)
    
    def _is_secant(self, segment: SegmentObject) -> bool:
        """Implémentation interne de is_secant"""
        return not self._is_parallel(segment) and self._intersection(segment) is not None

    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: PointObject) -> bool:
        """
        Vérifie qu'un point touche le segment
        
        Args:
            point (PointObject) : segment à vérifier
        """
        point = _to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: PointObject) -> bool:
        """Implémentation interne de collidepoint"""
        return self._contains(point)
    
    def collidesegment(self, segment: SegmentObject) -> bool:
        """
        Vérifie que deux segments se touchent

        Args:
            segment (SegmentObject) : segment à vérifier
        """
        if not isinstance(segment, SegmentObject): 
            _raise_error(self, 'is_orthogonal', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: SegmentObject) -> bool:
        """Implémentation interne de collidesegment"""
        return self.intersection(segment) is not None
    
    def collideline(self, line: LineObject) -> bool:
        """Vérifie qu'une ligne touche le segment"""
        from ._line import LineObject
        if not isinstance(line, LineObject):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line: LineObject) -> bool:
        """Implémentation interne de collideline"""
        return line._collidesegment(self)
    
    def collidecircle(self, circle: CircleObject) -> bool:
        """Vérifie qu'un cercle touche le segment"""
        from ._circle import CircleObject
        if not isinstance(circle, CircleObject):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)
    
    def _collidecircle(self, circle: CircleObject) -> bool:
        """Implémentation interne de collidecircle"""
        return circle._collidesegment(self)
    
    def colliderect(self, rect: RectObject) -> bool:
        """Vérifie qu'un rectangle touche le segment"""
        from ._rect import RectObject
        if not isinstance(rect, RectObject):
            _raise_error(self, 'colliderect', 'Invalid rect argument')
        return self._colliderect(rect)
    
    def _colliderect(self, rect: RectObject) -> bool:
        """Implémentation interne de colliderect"""
        return rect._collidesegment(self)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> SegmentObject:
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
        if self not in objs: objs = (self, *objs)
        dim = max(objs, key=lambda o: o.dim).dim
        for obj in objs:
            obj.reshape(dim)
    
    def project(self, point: PointObject) -> PointObject:
        """
        Renvoie le projeté d'un point sur le segment

        Args:
            point (PointObject) : point à projeter
        """
        point = _to_point(point)
        return self._project(point)
    
    def _project(self, point: PointObject) -> PointObject:
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

    def distance(self, point: PointObject) -> float:
        """
        Renvoie la distance entre un point et le segment

        Args:
            point (PointObject) : point distant
        """
        point = _to_point(point)
        return self._distance(point)
    
    def _distance(self, point: PointObject) -> float:
        """Implémentation interne de distance"""
        return point._distance(self._project(point))

    def intersection(self, segment: SegmentObject) -> PointObject | None:
        """
        Renvoie le point d'intersection du segment et d'un autre segment

        Args:
            segment (SegmentObject) : second segment
        """
        if not isinstance(segment, SegmentObject):
            _raise_error(self, "intersection", "Invalid segment argument")
        return self._intersection(segment)
    
    def _intersection(self, segment: SegmentObject) -> PointObject | None:
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
                
    def angle_with(self, segment: SegmentObject) -> float:
        """
        Renvoie l'angle entre deux segments (en radians)

        Args:
            segment (SegmentObject) : second segment
        """
        if not isinstance(segment, SegmentObject):
            _raise_error(self, "angle_with", "Invalid segment argument")
        return self._angle_with(segment)
    
    def _angle_with(self, segment: SegmentObject) -> float:
        """Implémentation interne de angle_with"""
        return self.get_vector()._angle_with(segment.get_vector())

    def translate(self, vector: VectorObject) -> SegmentObject:
        """
        Translate le segment selon un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        vector = _to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: VectorObject) -> SegmentObject:
        """Implémentation interne de translate"""
        self._start = self._start + vector
        self._end = self._end + vector

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, color: pygame.Color=None, width: int=None, dashed: bool=None, dash: int=None, gap: int=None):
        """Dessine le segment"""
        if not isinstance(surface, pygame.Surface): 
            _raise_error(self, 'draw', 'Invalid surface argument')
        
        color = self._color if color is None else _to_color(color)
        width = self._width if width is None else width
        dashed = self._dashed if dashed is None else dashed
        dash = self._dash if dash is None else dash
        gap = self._gap if gap is None else gap

        start_pos = tuple(map(int, self.P1[:2]))
        end_pos = tuple(map(int, self.P2[:2]))

        if dashed:
            self._draw_dashed(surface, color, start_pos, end_pos, width, dash, gap)
        elif width == 1:
            pygame.draw.aaline(surface, color, start_pos, end_pos)
        else:
            pygame.draw.line(surface, color, start_pos, end_pos, width)

    def _draw_dashed(self, surface: pygame.Surface, color: tuple[int], start: tuple[float, float], end: tuple[float, float], width: int, dash: int, gap: int):
        """Dessine un segment en pointillés"""
        x1, y1 = start
        x2, y2 = end

        dx = x2 - x1
        dy = y2 - y1
        length = math.hypot(dx, dy)

        if length == 0:
            return

        ux = dx / length
        uy = dy / length

        pos = 0
        draw = True

        while pos < length:
            seg_len = dash if draw else gap
            seg_len = min(seg_len, length - pos)

            if draw:
                sx = x1 + ux * pos
                sy = y1 + uy * pos
                ex = x1 + ux * (pos + seg_len)
                ey = y1 + uy * (pos + seg_len)

                if width == 1:
                    pygame.draw.aaline(surface, color, (sx, sy), (ex, ey))
                else:
                    pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)

            pos += seg_len
            draw = not draw