from __future__ import annotations
from _core import *

# ======================================== OBJET ========================================
class LineObject:
    """
    Object géométrique nD : Droite
    """
    __slots__ = ["_origin", "_vector", "_color", "_width", "_dashed"]
    def __init__(self, point: PointObject, vector: VectorObject):
        # représentation paramétrique
        point = _to_point(point)
        vector = _to_vector(vector)
        if vector.is_null():
            _raise_error(self, "__init__", "direction vector cannot be null vector")
        self._origin, self._vector = point.equalized_with_vectors(vector)

        # paramètres d'affichage
        self._color = (0, 0, 0)
        self._width = 1
        self._dashed = False
        self._dash = 10
        self._gap = 6
    
    def __repr__(self) -> str:
        """Représentation de la droite"""
        return f"Line({self._origin.__repr__}, {self._vector.__repr__})"
    
    def __hash__(self) -> int:
        """Renvoie la droite hashée"""
        return hash((self.unique_point.to_tuple(), self.unique_vector.to_tuple()))
    
    # ======================================== GETTERS ========================================
    @property
    def dim(self) -> int:
        """Renvoie la dimension du point"""
        return self._origin.dim

    def __len__(self) -> int:
        """Renvoie la dimension de la droite"""
        return self._origin.dim
    
    def __getitem__(self, t) -> PointObject:
        """Renvoie le point de la droite de paramètre t, P : O + t * v"""
        return self.point(t)

    def get_origin(self) -> PointObject:
        """Renvoie l'origine de la droite"""
        return self._origin
    
    def get_vector(self) -> VectorObject:
        """Renvoie un vecteur directeur de la droite"""
        return self._vector
    
    @property
    def unique_point(self) -> PointObject:
        """Renvoie le point unique d'une droite"""
        return self.project(PointObject(0))
    
    @property
    def unique_vector(self) -> VectorObject:
        """Renvoie le vecteur directeur unique d'une droite"""
        sign = 1
        for component in self._vector:
            if component != 0:
                sign = 1 if component > 0 else -1
                break
        return (sign * self._vector.normalized)
    
    def get_cartesian_equation(self) -> dict:
        """Renvoie l'équation cartésienne en 2D : ax + by + c = 0"""
        line = self.copy().reshape(2)
        u, v = line._vector.x, line._vector.y
        x0, y0 = line._origin.x, line._origin.y
        a, b = -v, u # vecteur normal (-v, u)
        c = -(a * x0 + b * y0)
        return {"a": a, "b": b, "c": c}
    
    @property
    def color(self) -> tuple[int, int ,int]:
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
        point = _to_point(point)
        self._origin, self._vector = point.equalized_with_vectors(self._vector)
    
    def set_vector(self, vector: VectorObject):
        """Modifie le vecteur directeur de la droite"""
        vector = _to_vector(vector)
        if vector.is_null(): _raise_error(self, "set_vector", "direction vector cannot be null vector")
        self._origin, self._vector = self._origin.equalized_with_vectors(vector)

    @color.setter
    def color(self, color: tuple[int, int, int]):
        """Fixe la couleur d'affichage"""
        if not isinstance(color, tuple) or len(color) != 3 or any(not isinstance(c, int) or c < 0 for c in color):
            _raise_error(self, 'set_color', 'Invalid color argument')
        self._color = color

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
        return (self._origin in line and self._vector.is_collinear(line.get_vector()))
    
    def __ne__(self, line: LineObject) -> bool:
        """Vérifie la non correspondance de deux droites"""
        return not self == line
    
    def __contains__(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans la droite'"""
        return self.contains(point)
    
    # ======================================== PREDICATS ========================================
    def contains(self, point: PointObject) -> bool:
        """Vérifie qu'un point soit compris dans la droite"""
        point = _to_point(point)
        A, B = self._origin.equalized(point)
        return self._vector.is_collinear(B - A)
    
    def is_orthogonal(self, line: LineObject) -> bool:
        """Vérifie si deux droites sont orthogonales"""
        if not isinstance(line, LineObject): _raise_error(self, 'is_orthogonal', 'Invalid line argument')
        return self._vector.is_orthogonal(line.get_vector())
    
    def is_parallel(self, line: LineObject) -> bool:
        """Vérifie si deux droites sont parallèles"""
        if not isinstance(line, LineObject): _raise_error(self, 'is_orthogonal', 'Invalid line argument')
        return self._vector.is_collinear(line.get_vector())
    
    def is_secant(self, line: LineObject) -> bool:
        """Vérifie si deux droites sont sécantes"""
        if not isinstance(line, LineObject): _raise_error(self, 'is_orthogonal', 'Invalid line argument')
        return not self.is_parallel(line) and self.intersection(line) is not None

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> LineObject:
        """
        Renvoie une copie de la droite
        """
        return deepcopy(self)
    
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
        self._origin.reshape(dim)
        self._vector.reshape(dim)

    def equalized(self, *lines: tuple[LineObject]) -> Tuple[Self, tuple[LineObject]]:
        """
        Egalise les dimensions de la droite et plusieurs autres droites

        Args:
            lines (tuple[LineObject]) : ensemble des droites à mettre sur la même dimension
        """
        if any(not isinstance(d, LineObject) for d in lines): _raise_error(self, 'equalized', 'Invalid lines arguments')
        if self not in lines: lines = (self, *lines)
        dim = max(lines, key=lambda l: l.dim).dim
        equalized_lines = []
        for line in lines:
            l = line.copy()
            l.reshape(dim)
            equalized_lines.append(l)
        return tuple(equalized_lines)

    def equalized_with_objects(self, *objects: tuple[PointObject | VectorObject]) -> Tuple[Self, tuple[PointObject | VectorObject]]:
        """
        Egalise les dimensions de la droite et de plusieurs autres points ou vecteurs

        Args:
            objects (tuple[PointObject|VectorObject]) : ensemble des objets géométriques à mettre sur la même dimension
        """
        if any(not isinstance(o, (PointObject, VectorObject)) for o in objects): _raise_error(self, 'equalized_with_objects', 'Invalid objects arguments')
        objects = (self, *objects)
        dim = max(objects, key=lambda o: o.dim).dim
        equalized_objects = []
        for obj in objects:
            o = obj.copy()
            o.reshape(dim)
            equalized_objects.append(o)
        return tuple(equalized_objects)
    
    def point(self, t: float) -> PointObject:
        """
        Renvoie le point de paramètre t, P : O + t * v

        Args:
            t (float) : paramètre d'avancement sur la droite
        """
        if not isinstance(t, numbers.Real): _raise_error(self, "point", "Invalid t argument")
        return self._origin + self._vector * float(t)
    
    def project(self, point: PointObject) -> PointObject:
        """
        Renvoie le projeté d'un point sur la droite

        Args:
            point (PointObject) : point à projeter
        """
        point = _to_point(point)
        d, P = self.equalized_with_objects(point)
        A, v = d.get_origin(), d.get_vector()
        AP = P - A
        return A + (AP.dot(v) / v.dot(v)) * v

    def distance(self, point: PointObject) -> float:
        """
        Renvoie la distance entre un point et une droite

        Args:
            point (PointObject) : point distant
        """
        point = _to_point(point)
        return point.distance(self.project(point))

    def intersection(self, line: LineObject) -> PointObject:
        """
        Renvoie le point d'intersection de deux droites

        Args:
            line (LineObject) : seconde droite
        """
        if not isinstance(line, LineObject): _raise_error(self, "intersection", "line argument must be LineObject")
        
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
                
    def angle_with(self, line: LineObject) -> float:
        """
        Renvoie l'angle entre deux droites (en radians)

        Args:
            line (LineObject) : seconde droite
        """
        if not isinstance(line, LineObject):
            _raise_error(self, "angle_with", "line argument must be LineObject")
        return self._vector.angle_with(line.get_vector())

    def symmetry(self, point: PointObject) -> PointObject:
        """
        Renvoie le symétrique d'un point par rapport à la droite

        Args:
            point (PointObject) : point dont on cherche le symétrique
        """
        point = _to_point(point)
        H = self.project(point)
        return H + (H - point)

    def translate(self, vector: VectorObject):
        """
        Translate la droite selon un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        vector = _to_vector(vector)
        self._origin = self._origin + vector

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, x_min: numbers.Real=None, x_max: numbers.Real=None, y_min: numbers.Real=None, y_max: numbers.Real=None, color: tuple[int, int, int]=None, width: int=None, dashed: bool=None, dash: int=None, gap: int=None):
        """Dessine la ligne"""
        if not isinstance(surface, pygame.Surface): _raise_error(self, 'draw', 'Invalid surface argument')
        if x_min is not None and not isinstance(x_min, numbers.Real): _raise_error(self, 'draw', 'Invalid x_min argument')
        if x_max is not None and not isinstance(x_max, numbers.Real): _raise_error(self, 'draw', 'Invalid x_max argument')
        if y_min is not None and not isinstance(y_min, numbers.Real): _raise_error(self, 'draw', 'Invalid y_min argument')
        if y_max is not None and not isinstance(y_max, numbers.Real): _raise_error(self, 'draw', 'Invalid y_max argument')
        if color is not None and (not isinstance(color, tuple) or any(not isinstance(c, int) for c in color)): _raise_error(self, 'draw', 'Invalid color argument')
        if width is not None and not isinstance(width, int): _raise_error(self, 'draw', 'Invalid width argument')
        if dashed is not None and not isinstance(dashed, bool): _raise_error(self, 'draw', 'Invalid dashed argument')
        if dash is not None and not isinstance(dash, int): _raise_error(self, 'draw', 'Invalid dash argument')
        if gap is not None and not isinstance(gap, int): _raise_error(self, 'draw', 'Invalid gap argument')

        # paramètres d'affichage
        x_min = 0 if x_min is None else x_min
        x_max = surface.get_width() if x_max is None else x_max
        y_min = 0 if y_min is None else y_min
        y_max = surface.get_height() if y_max is None else y_max
        color = self._color if color is None else color
        width = self._width if width is None else width
        dashed = self._dashed if dashed is None else dashed
        dash = self._dash if dash is None else dash
        gap = self._gap if gap is None else gap

        borders = {
            "left": self.intersection(LineObject((x_min, y_min), (0, 1))),
            "top": self.intersection(LineObject((x_min, y_min), (1, 0))),
            "right": self.intersection(LineObject((x_max, y_max), (0, 1))),
            "bottom": self.intersection(LineObject((x_max, y_max), (1, 0)))
        }

        points = []
        for border in borders:
            p = self.intersection(border)
            if p is None:
                continue
            x, y = p.to_tuple()
            if x_min <= x <= x_max and y_min <= y <= y_max:
                points.append((x, y))

        points = list(dict.fromkeys(points))
        if len(points) < 2:
            return

        start_pos, end_pos = points[0], points[1]
        

        if dashed:
            self._draw_dashed_line(surface, color, start_pos, end_pos, width, dash, gap)
        elif width == 1:
            pygame.draw.aaline(surface, color, start_pos, end_pos)
        else:
            pygame.draw.line(surface, color, start_pos, end_pos, width)


    def _draw_dashed_line(self, surface: pygame.Surface, color: tuple[int, int, int], start: tuple[float, float], end: tuple[float, float], width: int, dash: int, gap: int):
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