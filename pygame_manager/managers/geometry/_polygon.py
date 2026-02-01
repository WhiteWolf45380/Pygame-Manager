# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class PolygonObject:
    """
    Object géométrique 2D : Polygone
    """
    __slots__ = ["_vertices", "_filling", "_color", "_border", "_border_color", "_border_width", "_border_around"]
    PRECISION = 9

    def __init__(self, *points: geometry.Point):
        # sommets
        if len(points) < 3:
            _raise_error(self, '__init__', 'Polygon must have at least 3 vertices')
        self._vertices = [geometry._to_point(p, copy=True) for p in points]
        for v in self._vertices:
            v.reshape(2)

        # remplissage
        self._filling = True
        self._color = (255, 255, 255)

        # bordure
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False

    def __repr__(self) -> str:
        """Représentation du polygone"""
        return f"Polygon({', '.join(repr(v) for v in self._vertices)})"

    def __iter__(self) -> Iterator[geometry.Point]:
        """Itération sur les sommets"""
        for vertex in self._vertices:
            yield vertex.copy()

    def __hash__(self) -> int:
        """Renvoie le polygone hashé"""
        return hash(tuple(v.to_tuple() for v in self._vertices))

    # ======================================== GETTERS ========================================
    def __getitem__(self, i: int | slice) -> geometry.Point | list[geometry.Point]:
        """Renvoie le sommet de rang i"""
        if isinstance(i, slice):
            return [v.copy() for v in self._vertices[i]]
        return self._vertices[i].copy()

    @property
    def vertices(self) -> list[geometry.Point]:
        """Renvoie la liste des sommets"""
        return [v.copy() for v in self._vertices]

    @property
    def n(self) -> int:
        """Renvoie le nombre de sommets"""
        return len(self._vertices)

    def __len__(self) -> int:
        """Renvoie le nombre de sommets"""
        return len(self._vertices)

    @property
    def edges(self) -> list[geometry.Segment]:
        """Renvoie la liste des arêtes"""
        n = self.n
        return [geometry.Segment(self._vertices[i], self._vertices[(i + 1) % n]) for i in range(n)]

    @property
    def center(self) -> geometry.Point:
        """Renvoie le centre de masse du polygone (centroïde)"""
        return self._center()

    @property
    def perimeter(self) -> float:
        """Renvoie le périmètre"""
        return sum(
            self._vertices[i]._distance(self._vertices[(i + 1) % self.n])
            for i in range(self.n)
        )

    @property
    def area(self) -> float:
        """Renvoie l'aire (formule de Shoelace, valeur absolue)"""
        return abs(self._signed_area())

    @property
    def is_convex(self) -> bool:
        """Vérifie la convexité du polygone"""
        return self._is_convex()

    # paramètres d'affichage
    @property
    def filling(self) -> bool:
        """Vérifie le remplissage"""
        return self._filling

    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur"""
        return self._color

    @property
    def border(self) -> bool:
        """Vérifie la bordure"""
        return self._border

    @property
    def border_color(self) -> pygame.Color:
        """Renvoie la couleur de la bordure"""
        return self._border_color

    @property
    def border_width(self) -> int:
        """Renvoie l'épaisseur de la bordure"""
        return self._border_width

    @property
    def border_around(self) -> bool:
        """Vérifie que la bordure soit autour du polygone"""
        return self._border_around

    # ======================================== SETTERS ========================================
    def __setitem__(self, i: int, point: geometry.Point):
        """Fixe le sommet de rang i"""
        if not isinstance(i, int):
            _raise_error(self, '__setitem__', 'Invalid index argument')
        point = geometry._to_point(point, copy=True)
        point.reshape(2)
        self._vertices[i] = point

    @filling.setter
    def filling(self, value: bool):
        """Active ou non le remplissage"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_filling', 'Invalid value argument')
        self._filling = value

    @color.setter
    def color(self, color: pygame.Color):
        """Fixe la couleur"""
        self._color = _to_color(color)

    @border.setter
    def border(self, value: bool):
        """Active ou non la bordure"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_border', 'Invalid value argument')
        self._border = value

    @border_color.setter
    def border_color(self, color: pygame.Color):
        """Fixe la couleur de la bordure"""
        self._border_color = _to_color(color)

    @border_width.setter
    def border_width(self, width: int):
        """Fixe l'épaisseur de la bordure"""
        if not isinstance(width, int) or width <= 0:
            _raise_error(self, 'set_border_width', 'Invalid width argument')
        self._border_width = width

    @border_around.setter
    def border_around(self, value: bool):
        """Active ou non la bordure extérieure"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_border_around', 'Invalid value argument')
        self._border_around = value

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: geometry.Vector) -> geometry.Polygon:
        """Renvoie l'image du polygone par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(vector)
        return result

    def __radd__(self, vector: geometry.Vector) -> geometry.Polygon:
        """Renvoie l'image du polygone par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(vector)
        return result

    def __sub__(self, vector: geometry.Vector) -> geometry.Polygon:
        """Renvoie l'image du polygone par l'opposé du vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(-vector)
        return result

    # ======================================== PREDICATS & COLLISIONS ========================================
    def collidepoint(self, point: geometry.Point) -> bool:
        """
        Vérifie que le point se trouve dans le polygone (ray casting)

        Args:
            point (geometry.Point) : point à vérifier
        """
        point = geometry._to_point(point)
        return self._collidepoint(point)

    def _collidepoint(self, point: geometry.Point) -> bool:
        """Implémentation interne de collidepoint (ray casting)"""
        px, py = point.x, point.y
        n = self.n
        inside = False

        j = n - 1
        for i in range(n):
            xi, yi = self._vertices[i].x, self._vertices[i].y
            xj, yj = self._vertices[j].x, self._vertices[j].y

            # vérifie si le point est exactement sur une arête horizontale
            if yi == yj == py and min(xi, xj) <= px <= max(xi, xj):
                return True

            if (yi > py) != (yj > py):
                x_intersect = (xj - xi) * (py - yi) / (yj - yi) + xi
                if px == x_intersect:
                    return True  # exactement sur une arête
                if px < x_intersect:
                    inside = not inside

            j = i

        return inside

    def collideline(self, line: geometry.Line) -> bool:
        """
        Vérifie que la ligne croise le polygone

        Args:
            line (geometry.Line) : ligne à vérifier
        """
        if not isinstance(line, geometry.Line):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)

    def _collideline(self, line: geometry.Line) -> bool:
        """Implémentation interne de collideline"""
        intersections = self._line_intersection(line)
        return intersections is not None and len(intersections) > 0

    def collidesegment(self, segment: geometry.Segment) -> bool:
        """
        Vérifie que le segment croise le polygone

        Args:
            segment (geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, geometry.Segment):
            _raise_error(self, 'collidesegment', 'Invalid segment argument')
        return self._collidesegment(segment)

    def _collidesegment(self, segment: geometry.Segment) -> bool:
        """Implémentation interne de collidesegment"""
        if self._collidepoint(segment._start) or self._collidepoint(segment._end):
            return True

        sx1, sy1 = segment._start.x, segment._start.y
        sx2, sy2 = segment._end.x, segment._end.y
        n = self.n
        for i in range(n):
            j = (i + 1) % n
            if geometry.segment_segment_collide(sx1, sy1, sx2, sy2, self._vertices[i].x, self._vertices[i].y, self._vertices[j].x, self._vertices[j].y):
                return True
        return False

    def colliderect(self, rect: geometry.Rect) -> bool:
        """
        Vérifie la collision avec un rectangle

        Args:
            rect (geometry.Rect) : rectangle à vérifier
        """
        rect = geometry._to_rect(rect)
        return self._colliderect(rect)

    def _colliderect(self, rect: geometry.Rect) -> bool:
        """Implémentation interne de colliderect"""
        # un sommet du polygone dans le rect
        for v in self._vertices:
            if rect._collidepoint(v):
                return True

        # un sommet du rect dans le polygone
        for corner in [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft]:
            if self._collidepoint(corner):
                return True

        # une arête du polygone croise une arête du rect
        rect_edges = [
            (rect.left, rect.top, rect.right, rect.top),
            (rect.right, rect.top, rect.right, rect.bottom),
            (rect.right, rect.bottom, rect.left, rect.bottom),
            (rect.left, rect.bottom, rect.left, rect.top),
        ]
        n = self.n
        for i in range(n):
            j = (i + 1) % n
            px1, py1 = self._vertices[i].x, self._vertices[i].y
            px2, py2 = self._vertices[j].x, self._vertices[j].y
            for rx1, ry1, rx2, ry2 in rect_edges:
                if geometry.segment_segment_collide(px1, py1, px2, py2, rx1, ry1, rx2, ry2):
                    return True

        return False

    def collidecircle(self, circle: geometry.Circle) -> bool:
        """
        Vérifie la collision avec un cercle

        Args:
            circle (geometry.Circle) : cercle à vérifier
        """
        if not isinstance(circle, geometry.Circle):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)

    def _collidecircle(self, circle: geometry.Circle) -> bool:
        """Implémentation interne de collidecircle"""
        # le centre du cercle est dans le polygone
        if self._collidepoint(circle._center):
            return True

        cx, cy = circle._center.x, circle._center.y
        r = circle._radius

        n = self.n
        for i in range(n):
            j = (i + 1) % n
            # un sommet du polygone est dans le cercle
            if circle._collidepoint(self._vertices[i]):
                return True
            # une arête du polygone est à moins de rayon du centre
            if geometry.segment_point_distance(self._vertices[i].x, self._vertices[i].y, self._vertices[j].x, self._vertices[j].y, cx, cy) <= r:
                return True

        return False

    def collidepolygon(self, polygon: geometry.Polygon) -> bool:
        """
        Vérifie la collision avec un autre polygone

        Args:
            polygon (geometry.Polygon) : polygone à vérifier
        """
        if not isinstance(polygon, geometry.Polygon):
            _raise_error(self, 'collidepolygon', 'Invalid polygon argument')
        return self._collidepolygon(polygon)

    def _collidepolygon(self, polygon: geometry.Polygon) -> bool:
        """Implémentation interne de collidepolygon"""
        # un sommet de l'un est dans l'autre
        for v in self._vertices:
            if polygon._collidepoint(v):
                return True
        for v in polygon._vertices:
            if self._collidepoint(v):
                return True

        # une arête de l'un croise une arête de l'autre
        n1 = self.n
        n2 = polygon.n
        for i in range(n1):
            i2 = (i + 1) % n1
            ax1, ay1 = self._vertices[i].x, self._vertices[i].y
            ax2, ay2 = self._vertices[i2].x, self._vertices[i2].y
            for j in range(n2):
                j2 = (j + 1) % n2
                if geometry.segment_segment_collide(ax1, ay1, ax2, ay2, polygon._vertices[j].x, polygon._vertices[j].y, polygon._vertices[j2].x, polygon._vertices[j2].y):
                    return True

        return False

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> geometry.Polygon:
        """Renvoie une copie du polygone"""
        return _deepcopy(self)

    def to_tuple(self) -> tuple[tuple[float, float]]:
        """Renvoie les sommets en tuple de tuples"""
        return tuple(v.to_tuple() for v in self._vertices)

    def to_list(self) -> list[list[float]]:
        """Renvoie les sommets en liste de listes"""
        return [v.to_list() for v in self._vertices]

    def scale(self, ratio: Real, center: geometry.Point = None):
        """
        Redimensionne le polygone depuis un centre

        Args:
            ratio (Real) : ratio de redimensionnement
            center (geometry.Point, optional) : centre de redimensionnement (défaut: centroïde)
        """
        if not isinstance(ratio, Real) or ratio <= 0:
            _raise_error(self, 'scale', 'Invalid ratio argument')
        if center is None:
            center = self._center()
        else:
            center = geometry._to_point(center)
        self._scale(ratio, center)

    def _scale(self, ratio: Real, center: geometry.Point):
        """Implémentation interne de scale"""
        for i in range(self.n):
            v = self._vertices[i]
            self._vertices[i] = geometry.Point(
                center.x + (v.x - center.x) * ratio,
                center.y + (v.y - center.y) * ratio,
            )

    def translate(self, vector: geometry.Vector):
        """
        Translate le polygone selon un vecteur

        Args:
            vector (geometry.Vector) : vecteur de translation
        """
        vector = geometry._to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: geometry.Vector):
        """Implémentation interne de translate"""
        for i in range(self.n):
            self._vertices[i] = self._vertices[i] + vector

    def rotate(self, angle: Real, center: geometry.Point = None, degrees: bool = False):
        """
        Tourne le polygone autour d'un centre

        Args:
            angle (Real) : angle de rotation
            center (geometry.Point, optional) : centre de rotation (défaut: centroïde)
            degrees (bool) : si True, angle en degrés
        """
        if not isinstance(angle, Real):
            _raise_error(self, 'rotate', 'Invalid angle argument')
        if center is None:
            center = self._center()
        else:
            center = geometry._to_point(center)
        self._rotate(angle, center, degrees=degrees)

    def _rotate(self, angle: Real, center: geometry.Point, degrees: bool = False):
        """Implémentation interne de rotate"""
        if degrees:
            angle = math.radians(angle)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        cx, cy = center.x, center.y

        for i in range(self.n):
            dx = self._vertices[i].x - cx
            dy = self._vertices[i].y - cy
            self._vertices[i] = geometry.Point(
                cx + dx * cos_a - dy * sin_a,
                cy + dx * sin_a + dy * cos_a,
            )

    def line_intersection(self, line: geometry.Line) -> tuple[geometry.Point] | None:
        """
        Renvoie les points d'intersection entre la ligne et le polygone

        Args:
            line (geometry.Line) : ligne à tester
        """
        if not isinstance(line, geometry.Line):
            _raise_error(self, 'line_intersection', 'Invalid line argument')
        return self._line_intersection(line)

    def _line_intersection(self, line: geometry.Line) -> tuple[geometry.Point] | None:
        """Implémentation interne de line_intersection"""
        ox, oy = line.get_origin().x, line.get_origin().y
        vx, vy = line.get_vector().x, line.get_vector().y

        points = []
        n = self.n
        for i in range(n):
            j = (i + 1) % n
            result = geometry.line_segment_intersection(ox, oy, vx, vy, self._vertices[i].x, self._vertices[i].y, self._vertices[j].x, self._vertices[j].y)
            if result is not None:
                points.append(geometry.Point(*result))

        # suppression des doublons
        unique_points = []
        seen = set()
        for p in points:
            key = (round(p.x, 6), round(p.y, 6))
            if key not in seen:
                unique_points.append(p)
                seen.add(key)

        if not unique_points:
            return None

        # tri par paramètre t sur la droite
        def t_of(p):
            return ((p.x - ox) / vx) if vx != 0 else ((p.y - oy) / vy)

        unique_points.sort(key=t_of)
        return tuple(unique_points)

    # ======================================== INTERNALS ========================================
    def _signed_area(self) -> float:
        """Aire signée par la formule de Shoelace (positif = sens anti-horaire)"""
        n = self.n
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += self._vertices[i].x * self._vertices[j].y
            area -= self._vertices[j].x * self._vertices[i].y
        return area / 2.0

    def _center(self) -> geometry.Point:
        """Centroïde du polygone"""
        n = self.n
        a = self._signed_area()

        if abs(a) < 1e-10:
            # polygone dégénéré : retourne la moyenne des sommets
            cx = sum(v.x for v in self._vertices) / n
            cy = sum(v.y for v in self._vertices) / n
            return geometry.Point(cx, cy)

        cx, cy = 0.0, 0.0
        for i in range(n):
            j = (i + 1) % n
            cross = self._vertices[i].x * self._vertices[j].y - self._vertices[j].x * self._vertices[i].y
            cx += (self._vertices[i].x + self._vertices[j].x) * cross
            cy += (self._vertices[i].y + self._vertices[j].y) * cross

        cx /= (6.0 * a)
        cy /= (6.0 * a)
        return geometry.Point(cx, cy)

    def _is_convex(self) -> bool:
        """Vérifie la convexité via le signe du produit vectoriel consécutif"""
        n = self.n
        sign = None
        for i in range(n):
            x1, y1 = self._vertices[i].x, self._vertices[i].y
            x2, y2 = self._vertices[(i + 1) % n].x, self._vertices[(i + 1) % n].y
            x3, y3 = self._vertices[(i + 2) % n].x, self._vertices[(i + 2) % n].y

            cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
            if abs(cross) < 1e-10:
                continue  # points alignés, on skip

            if sign is None:
                sign = cross > 0
            elif (cross > 0) != sign:
                return False

        return True

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, filling: bool = None, color: pygame.Color = None,
             border: bool = None, border_width: int = None, border_color: pygame.Color = None):
        """
        Dessine le polygone sur une surface donnée

        Args:
            surface (pygame.Surface) : surface de dessin
            filling (bool, optional) : remplissage
            color (pygame.Color, optional) : couleur de remplissage
            border (bool, optional) : bordure
            border_width (int, optional) : épaisseur de la bordure
            border_color (pygame.Color, optional) : couleur de la bordure
        """
        if not isinstance(surface, pygame.Surface):
            _raise_error(self, 'draw', 'Invalid surface argument')

        # paramètres d'affichage
        filling = self._filling if filling is None else filling
        color = self._color if color is None else _to_color(color)
        border = self._border if border is None else border
        border_width = self._border_width if border_width is None else border_width
        border_color = self._border_color if border_color is None else _to_color(border_color)
        border_around = self._border_around

        points = [(int(v.x), int(v.y)) for v in self._vertices]

        # remplissage
        if filling:
            pygame.draw.polygon(surface, color, points)

        # bordure
        if border:
            if border_around:
                # bordure en dehors : on dessine d'abord une version élargie en noir
                # puis le remplissage par-dessus (approximation via décalage des sommets)
                pygame.draw.polygon(surface, border_color, points, border_width * 2)
                if filling:
                    pygame.draw.polygon(surface, color, points)
                else:
                    pygame.draw.polygon(surface, border_color, points, border_width)
            else:
                pygame.draw.polygon(surface, border_color, points, border_width)