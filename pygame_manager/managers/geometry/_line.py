# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *
from ._point import PointObject, _to_point
from ._vector import VectorObject, _to_vector

# ======================================== OBJET ========================================
class LineObject:
    """
    Object géométrique nD : Droite
    """
    __slots__ = ["_origin", "_vector", "_color", "_width", "_dashed", "_dash", "_gap"]
    def __init__(self, point: PointObject, vector: VectorObject):        
        # représentation paramétrique
        self._origin = _to_point(point, copy=True)
        self._vector = _to_vector(vector, copy=True)
        if vector.is_null():
            _raise_error(self, "__init__", "direction vector cannot be null vector")
        self._origin.equalize(self._vector)

        # paramètres d'affichage
        self._color = (0, 0, 0)
        self._width = 1
        self._dashed = False
        self._dash = 10
        self._gap = 6
    
    def __repr__(self) -> str:
        """Représentation de la droite"""
        return f"Line({self._origin.__repr__()}, {self._vector.__repr__()})"
    
    def __hash__(self) -> int:
        """Renvoie la droite hashée"""
        return hash((self.unique_point.to_tuple(), self.unique_vector.to_tuple()))
    
    # ======================================== GETTERS ========================================
    @property
    def dim(self) -> int:
        """Renvoie la dimension de la droite"""
        return self._origin.dim

    def __len__(self) -> int:
        """Renvoie la dimension de la droite"""
        return self._origin.dim
    
    def __getitem__(self, t: Real) -> PointObject:
        """Renvoie le point de la droite de paramètre t, P : O + t * v"""
        if isinstance(t, slice):
            n = t.stop if t.stop is not None else 1
            start = t.start if t.start is not None else 0.0
            step = t.step if t.step is not None else (1.0 if n == 1 else (1.0 - start)/(n-1))
            return tuple(self.point(start + i*step) for i in range(n))
        return self.point(t)

    def get_origin(self) -> PointObject:
        """Renvoie l'origine de la droite"""
        return self._origin.copy()
    
    def get_vector(self) -> VectorObject:
        """Renvoie un vecteur directeur de la droite"""
        return self._vector.copy()
    
    @property
    def unique_point(self) -> PointObject:
        """Renvoie le point unique d'une droite"""
        return self._project(PointObject(0))
    
    @property
    def unique_vector(self) -> VectorObject:
        """Renvoie le vecteur directeur unique d'une droite"""
        sign = 1
        for component in self._vector:
            if component != 0:
                sign = 1 if component > 0 else -1
                break
        return (sign * self._vector.normalized)
    
    def get_cartesian_equation(self) -> dict[float]:
        """Renvoie l'équation cartésienne en 2D : ax + by + c = 0"""
        line = self.copy()
        line.reshape(2)
        u, v = line._vector.x, line._vector.y
        x0, y0 = line._origin.x, line._origin.y
        a, b = -v, u
        c = -(a * x0 + b * y0)
        return {"a": a, "b": b, "c": c}
    
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
        """Vérifie si l'affichage de la droite est segmenté"""
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
    def set_origin(self, point: PointObject):
        """Modifie l'origine de la droite"""
        self._origin = _to_point(point, copy=True)
        self._origin.equalize(self._vector)
    
    def set_vector(self, vector: VectorObject):
        """Modifie le vecteur directeur de la droite"""
        self._vector = _to_vector(vector, copy=True)
        if self._vector.is_null(): 
            _raise_error(self, "set_vector", "direction vector cannot be null vector")
        self._vector.equalize(self._origin)

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
    def __eq__(self, line: LineObject) -> bool:
        """Vérifie la correspondance de deux droites"""
        if not isinstance(line, LineObject): return False
        return (self._origin in line and self._vector.is_collinear(line._vector))
    
    def __ne__(self, line: LineObject) -> bool:
        """Vérifie la non correspondance de deux droites"""
        return not self == line
    
    def __contains__(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans la droite"""
        return self._contains(_to_point(point))
    
    # ======================================== PREDICATS ========================================
    def contains(self, point: PointObject) -> bool:
        """
        Vérifie qu'un point soit compris dans la droite

        Args:
            point (PointObject) ; point à vérifier
        """
        point = _to_point(point)
        return self._contains(point)
    
    def _contains(self, point: PointObject) -> bool:
        """Implémentation interne de contains"""
        self._origin.equalize(point)
        return self._vector._is_collinear(point - self)
    
    def is_orthogonal(self, line: LineObject) -> bool:
        """
        Vérifie si deux droites sont orthogonales

        Args:
            line (LineObject) : Droite à vérifier
        """
        if not isinstance(line, LineObject): 
            _raise_error(self, 'is_orthogonal', 'Invalid line argument')
        return self._is_orthogonal(line)
    
    def _is_orthogonal(self, line: LineObject) -> bool:
        """Implémentation interne de is_orthogonal"""
        return self._vector._is_orthogonal(line._vector)
    
    def is_parallel(self, line: LineObject) -> bool:
        """Vérifie si deux droites sont parallèles"""
        if not isinstance(line, LineObject): 
            _raise_error(self, 'is_parallel', 'Invalid line argument')
        return self._is_parallel(line)
    
    def _is_parallel(self, line: LineObject) -> bool:
        """Implémentation interne de is_parallel"""
        return self._vector._is_collinear(line._vector)
    
    def is_secant(self, line: LineObject) -> bool:
        """Vérifie si deux droites sont sécantes"""
        if not isinstance(line, LineObject): 
            _raise_error(self, 'is_secant', 'Invalid line argument')
        return self._is_secant(line)
    
    def _is_secant(self, line: LineObject) -> bool:
        """Implémentation interne de is_secant"""
        return not self._is_parallel(line) and self._intersection(line) is not None

    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: PointObject) -> bool:
        """Vérifie qu'un point touche la droite"""
        point = _to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: PointObject) -> bool:
        """Implémentation interne de collidepoint"""
        return self._contains(point)
    
    def collideline(self, line: LineObject) -> bool:
        """Vérifie que deux droites se touchent"""
        if not isinstance(line, LineObject):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line: LineObject) -> bool:
        """Implémentation interne de collideline"""
        return self._intersection(line) is not None or self == line
    
    def collidesegment(self, segment: SegmentObject) -> bool:
        """Vérifie qu'un segment touche la droite"""
        from ._segment import SegmentObject
        if not isinstance(segment, SegmentObject):
            _raise_error(self, 'collidesegment', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: SegmentObject) -> bool:
        """Implémentation interne de collidesegment"""        
        if self.contains(segment.P1) or self.contains(segment.P2):
            return True
        
        P1 = segment._start
        P2 = segment._end
        u = P2 - P1
        
        temp_line = LineObject(P1, u)
        intersection = self._intersection(temp_line)
        
        if intersection is None:
            return False
        
        return intersection in segment
    
    def collidecircle(self, circle: CircleObject) -> bool:
        """Vérifie qu'un cercle touche la droite"""
        from ._circle import CircleObject
        if not isinstance(circle, CircleObject):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)
    
    def _collidecircle(self, circle: CircleObject) -> bool:
        """Implémentation interne de collidecircle"""
        return circle._collideline(self)
    
    def colliderect(self, rect: RectObject) -> bool:
        """Vérifie qu'un rectangle touche la droite"""
        from ._rect import RectObject
        if not isinstance(rect, RectObject):
            _raise_error(self, 'colliderect', 'Invalid rect argument')
        return self._colliderect(rect)
    
    def _colliderect(self, rect: RectObject) -> bool:
        """Vérifie qu'un rectangle touche la droite"""
        return rect._collideline(self)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> LineObject:
        """Renvoie une copie de la droite"""
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
        self._origin.reshape(dim)
        self._vector.reshape(dim)

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
    
    def point(self, t: float) -> PointObject:
        """
        Renvoie le point de paramètre t, P : O + t * v

        Args:
            t (float) : paramètre d'avancement sur la droite
        """
        if not isinstance(t, Real): 
            _raise_error(self, "point", "Invalid t argument")
        return self._point(t)
    
    def _point(self, t: float) -> PointObject:
        """Implémentation interne de point"""
        return self._origin + self._vector * float(t)
    
    def project(self, point: PointObject) -> PointObject:
        """
        Renvoie le projeté d'un point sur la droite

        Args:
            point (PointObject) : point à projeter
        """
        point = _to_point(point)
        return self._project(point)
    
    def _project(self, point: PointObject) -> PointObject:
        """Implémentation interne de project"""
        self._equalize(point)
        A, v = self._origin, self._vector
        AP = point - A
        return A + (AP._dot(v) / v._dot(v)) * v

    def distance(self, point: PointObject) -> float:
        """
        Renvoie la distance entre un point et une droite

        Args:
            point (PointObject) : point distant
        """
        point = _to_point(point)
        return self._distance(point)
    
    def _distance(self, point: PointObject) -> float:
        """Implémentation interne de distance"""
        return point._distance(self._project(point))

    def intersection(self, line: LineObject):
        """
        Renvoie le point d'intersection de deux droites

        Args:
            line (LineObject) : seconde droite
        """
        if not isinstance(line, LineObject): 
            _raise_error(self, "intersection", "Invalid line argument")
        return self._intersection(line)
    
    def _intersection(self, line: LineObject):
        """Implémentation interne de intersection"""
        if self.is_parallel(line):
            return None
        
        d1, d2 = self.equalized(line)
        P1, u1 = d1._origin, d1._vector
        P2, u2 = d2._origin, d2._vector

        v = P2 - P1
        if not v.is_coplanar(u1, u2):
            return None

        for i in range(d1.dim):
            for j in range(i + 1, d1.dim):             
                det = u1[i] * (-u2[j]) - u1[j] * (-u2[i])
                
                if abs(det) > 1e-10:
                    t = (v[i] * (-u2[j]) - v[j] * (-u2[i])) / det
                    return P1 + u1 * t
        return None
                
    def angle_with(self, line: LineObject) -> float:
        """
        Renvoie l'angle entre deux droites (en radians)

        Args:
            line (LineObject) : seconde droite
        """
        if not isinstance(line, LineObject):
            _raise_error(self, "angle_with", "Invalid line argument")
        return self._angle_with(line)
    
    def _angle_with(self, line: LineObject) -> float:
        """Implémentation interne de angle_with"""
        return self._vector._angle_with(line._vector)

    def symmetric(self, point: PointObject) -> PointObject:
        """
        Renvoie le symétrique d'un point par rapport à la droite

        Args:
            point (PointObject) : point dont on cherche le symétrique
        """
        point = _to_point(point)
        return self._symmetric(point)
    
    def _symmetric(self, point: PointObject) -> PointObject:
        """Implémentation interne de symmetric"""
        H = self._project(point)
        return H + (H - point)

    def translate(self, vector: VectorObject) -> LineObject:
        """
        Translate la droite selon un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        vector = _to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: VectorObject) -> LineObject:
        """Implémentation interne de translate"""
        self._origin += vector

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, x_min: float=None, x_max: float=None, y_min: float=None, y_max: float=None, color: pygame.Color=None, width: int=None, dashed: bool=None, dash: int=None, gap: int=None):
        """Dessine la droite"""
        if not isinstance(surface, pygame.Surface): 
            _raise_error(self, 'draw', 'Invalid surface argument')

        # paramètres d'affichage
        x_min = 0 if x_min is None else x_min
        x_max = surface.get_width() if x_max is None else x_max
        y_min = 0 if y_min is None else y_min
        y_max = surface.get_height() if y_max is None else y_max
        color = self._color if color is None else _to_color(color)
        width = self._width if width is None else width
        dashed = self._dashed if dashed is None else dashed
        dash = self._dash if dash is None else dash
        gap = self._gap if gap is None else gap

        # Lignes des bordures
        borders = {
            "left": LineObject((x_min, y_min), (0, 1)),
            "top": LineObject((x_min, y_min), (1, 0)),
            "right": LineObject((x_max, y_max), (0, 1)),
            "bottom": LineObject((x_min, y_max), (1, 0))
        }

        points = []
        for border in borders.values():
            p = self.intersection(border)
            if p is None:
                continue
            x, y = p.x, p.y
            if x_min <= x <= x_max and y_min <= y <= y_max:
                points.append((x, y))

        points = list(dict.fromkeys(points))
        if len(points) < 2:
            return

        start_pos, end_pos = points[0], points[1]

        if dashed:
            self._draw_dashed(surface, color, start_pos, end_pos, width, dash, gap)
        elif width == 1:
            pygame.draw.aaline(surface, color, start_pos, end_pos)
        else:
            pygame.draw.line(surface, color, start_pos, end_pos, width)

    def _draw_dashed(self, surface: pygame.Surface, color: tuple[int], start: tuple[float, float], end: tuple[float, float], width: int, dash: int, gap: int):
        """Dessine une droite en pointillés"""
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