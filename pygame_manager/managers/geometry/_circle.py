# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *
from ._point import PointObject, _to_point
from ._vector import VectorObject, _to_vector

# ======================================== OBJET ========================================
class CircleObject:
    """
    Object géométrique 2D : Cercle
    """
    __slots__ = ["_center", "_radius", "_filling", "_color", "_border", "_border_color", "_border_width", "_border_around"]
    PRECISION = 9
    def __init__(self, center: PointObject, radius: Real):
        """
        Args:
            center (PointObject) : point central du cercle
            radius (Real) : rayon du cercle
        """
        # centre
        self._center = _to_point(center, copy=True)
        self._center.reshape(2)

        # rayon
        if not isinstance(radius, Real) or radius <= 0:  _raise_error(self, '__init__', 'Invalid radius argument')
        self._radius = float(radius)

        # remplissage
        self._filling = True
        self._color = (255, 255, 255)
       
        # bordure
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False
    
    def __repr__(self) -> str:
        """Représentation du cercle"""
        return f"Circle(O={self._center}, r={self._radius})"
    
    def __iter__(self) -> Iterator:
        """Itération sur les points du cercle"""
        for i in range(360):
            yield self.point_from_angle(i, degrees=True)
    
    def __hash__(self) -> int:
        """Renvoie le cercle hashé"""
        return hash((self.center.to_tuple(), self._radius))
    
    # ======================================== GETTERS ========================================
    @property
    def center(self) -> PointObject:
        """Renvoie le point central"""
        return self._center.copy()
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du point central"""
        return self._center.x
    
    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du point central"""
        return self._center.y

    @property
    def radius(self) -> float:
        """Renvoie le rayon"""
        return self._radius
    
    @property
    def diameter(self) -> float:
        """Renvoie le diamètre"""
        return 2 * self._radius
    
    @property
    def perimeter(self) -> float:
        """Renvoie le périmètre"""
        return 2 * math.pi * self._radius
    
    @property
    def area(self) -> float:
        """Renvoie l'aire"""
        return math.pi * self._radius**2

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
        """Vérifie que la bordure soit autour du cercle"""
        return self._border_around
    
    # ======================================== SETTERS ========================================
    @center.setter
    def center(self, point: PointObject):
        """Fixe le point central"""
        self._center = _to_point(point, copy=True)
        self._center.reshape(2)

    @centerx.setter
    def centerx(self, coordinate: Real):
        """Fixe la coordonnée x du point central"""
        self._center.x = coordinate

    @centery.setter
    def centery(self, coordinate: Real):
        """Fixe la coordonnée y du point central"""
        self._center.y = coordinate

    @radius.setter
    def radius(self, radius: Real):
        """Fixe le rayon"""
        if not isinstance(radius, Real) or radius <= 0:
            _raise_error(self, 'set_radius', 'Invalid Radius Argument')
        self._radius = round(float(radius), self.PRECISION)
    
    @diameter.setter
    def diameter(self, diameter: Real):
        """Fixe le diamètre"""
        if not isinstance(diameter, Real) or diameter <= 0:
            _raise_error(self, 'set_diameter', 'Invalid diameter argument')
        self._radius = round(float(diameter) / 2, self.PRECISION)
    
    @perimeter.setter
    def perimeter(self, perimeter: Real):
        """Fixe le périmètre"""
        if not isinstance(perimeter, Real) or perimeter <= 0:
            _raise_error(self, 'set_perimeter', 'Invalid perimeter argument')
        self._radius = round(float(perimeter) / (2 * math.pi), self.PRECISION)

    @area.setter
    def area(self, area: Real):
        """Fixe l'aire"""
        if not isinstance(area, Real) or area <= 0:
            _raise_error(self, 'set_area', 'Invalid area argument')
        self._radius = round(math.sqrt(float(area) / math.pi), self.PRECISION)

    @filling.setter
    def filling(self, value: bool):
        """Active ou non le remplissage"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_filling', 'Invalid value argument')
        self._filling = value
    
    @color.setter
    def color(self, color: pygame.Color):
        """Fixe la couleur de remplissage"""
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

    # ======================================== PREDICATS ========================================
    def collidepoint(self, point: PointObject) -> bool:
        """
        Vérifie qu'un point soit dans le cercle

        Args:
            point (PointObject) : point à vérifier
        """
        point = _to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: PointObject) -> bool:
        """Implémentation interne de collidepoint"""
        dist_sq = (point.x - self.centerx)**2 + (point.y - self.centery)**2
        return dist_sq <= self._radius**2

    def collideline(self, line: LineObject) -> bool:
        """
        Vérifie que la droite croise le cercle

        Args:
            line (LineObject) : droite à vérifier
        """
        from ._line import LineObject
        if not isinstance(line, LineObject):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line: LineObject) -> bool:
        """Implémentation interne de collideline"""
        dist = line._distance(self._center)
        return dist <= self._radius

    def collidesegment(self, segment: SegmentObject) -> bool:
        """
        Vérifie que le segment croise le cercle

        Args:
            segment (SegmentObject) : segment à vérifier
        """
        from ._segment import SegmentObject
        if not isinstance(segment, SegmentObject):
            _raise_error(self, 'collidesegment', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: SegmentObject) -> bool:
        """Implémentation interne de collidesegment"""
        dist = segment._distance(self._center)
        return dist <= self._radius

    def colliderect(self, rect: RectObject) -> bool:
        """
        Vérifie la collision avec un rectangle

        Args:
            rect (RectObject) : rectangle à vérifier
        """
        from ._rect import _to_rect
        rect = _to_rect(rect)
        return self._colliderect(rect)
    
    def _colliderect(self, rect: RectObject) -> bool:
        """Implémentation interne de colliderect"""
        return rect._collidecircle(self)

    def collidecircle(self, circle: CircleObject) -> bool:
        """
        Vérifie la collision avec un autre cercle

        Args:
            circle (CircleObject) : cercle à vérifier
        """
        from ._circle import CircleObject
        if not isinstance(circle, CircleObject):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)
    
    def _collidecircle(self, circle: CircleObject) -> bool:
        """Implémentation interne de collidecircle"""
        dist_sq = (self.centerx - circle.centerx)**2 + (self.centery - circle.centery)**2
        dist = math.sqrt(dist_sq)
        return dist <= self._radius + circle.radius

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> CircleObject:
        """Renvoie une copie du cercle"""
        return _deepcopy(self)
    
    def to_tuple(self) -> tuple[float]:
        """Renvoie les propriétés dans un tuple"""
        return (self.center.to_tuple(), self.radius)
    
    def to_list(self) -> tuple[float]:
        """Renvoie les propriétés dans une liste"""
        return [self.center.to_list(), self.radius]
    
    def scale(self, ratio: Real):
        """
        Redimensionne le cercle

        Args:
            ratio (Real) : ratio de redimensionnement
        """
        if not isinstance(ratio, Real) or ratio <= 0:
            _raise_error(self, 'scale', 'Invalid ratio argument')
        self._scale(ratio)

    def _scale(self, ratio: Real):
        """Implémentation interne de scale"""
        self.radius = round(self.radius * float(ratio), self.PRECISION)
    
    def translate(self, vector: VectorObject):
        """
        Translate le cercle selon un vecteur

        Args:
            vector (VectorObject) : vecteur de translation
        """
        vector = _to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: VectorObject):
        """Implémentation interne de translate"""
        self.centerx += vector.x
        self.centery += vector.y
    
    def point_from_angle(self, angle: Real, degrees: bool = False) -> PointObject:
        """
        Renvoie le point sur le cercle à un angle donné
        
        Args:
            angle (Real): angle
            degrees (bool): si True, angle en degrés, sinon en radians
        """
        if not isinstance(angle, Real):
            _raise_error(self, 'point_from_angle', 'Invalid angle argument')
        if not isinstance(degrees, bool):
            _raise_error(self, 'point_from_angle', 'Invalid degrees argument')
        return self._point_from_angle(angle, degrees=degrees)
    
    def _point_from_angle(self, angle: Real, degrees: bool = False) -> PointObject:
        """Implémentation interne de point_from_angle"""
        if degrees:
            angle = math.radians(angle)

        x = self.centerx + self._radius * math.cos(angle)
        y = self.centery + self._radius * math.sin(angle)
        
        return PointObject(x, y)

    def line_intersection(self, line: LineObject) -> tuple[PointObject] | None:
        """
        Renvoie les points d'intersection entre le cercle et une droite
        
        Args:
            line (LineObject): droite
            
        Returns:
            tuple[PointObject] | None: 0, 1 ou 2 points d'intersection
        """
        from ._line import LineObject        
        if not isinstance(line, LineObject):
            _raise_error(self, 'line_intersection', 'Invalid line argument')
        return self._line_intersection(line)
    
    def _line_intersection(self, line: LineObject) -> tuple[PointObject] | None:
        """Implémentation interne de line_intersection"""
        line = line.copy()
        line.reshape(2)
        
        O = line.get_origin()
        v = line.get_vector()
        C = self._center
        r = self._radius
        
        OC = C - O
        v_dot_v = v.dot(v)
        if v_dot_v == 0:
            return None
        
        t_proj = OC.dot(v) / v_dot_v
        H = O + t_proj * v
        HC = C - H
        d = HC.norm
        
        if d > r:
            return None
        
        if abs(d - r) < 1e-10:
            return (H,)
        
        delta = math.sqrt(r**2 - d**2)
        v_normalized = v.normalized
        P1 = H + delta * v_normalized
        P2 = H - delta * v_normalized
        
        return (P1, P2)

    def segment_intersection(self, segment: SegmentObject) -> tuple[PointObject] | None:
        """
        Renvoie les points d'intersection entre le cercle et un segment
        
        Args:
            segment (SegmentObject): segment
            
        Returns:
            tuple[PointObject] | None: 0, 1 ou 2 points d'intersection
        """
        from ._segment import SegmentObject       
        if not isinstance(segment, SegmentObject):
            _raise_error(self, 'segment_intersection', 'Invalid segment argument')
        return self._segment_intersection(segment)
    
    def _segment_intersection(self, segment: SegmentObject) -> tuple[PointObject] | None:
        """Implémentation interne de segment_intersection"""
        from ._line import LineObject        
        line = LineObject(segment.P1, segment.get_vector())
        intersections = self.line_intersection(line)
        
        if intersections is None:
            return None
        
        valid_points = []
        for point in intersections:
            if point in segment:
                valid_points.append(point)
        
        return tuple(valid_points) if valid_points else None

    def rect_intersection(self, rect: RectObject) -> tuple[PointObject] | None:
        """
        Renvoie les points d'intersection entre le cercle et un rectangle
        
        Args:
            rect (RectObject): rectangle
            
        Returns:
            tuple[PointObject] | None: liste des points d'intersection
        """
        from ._rect import _to_rect        
        rect = _to_rect(rect)
        return self._rect_intersection(rect)
        
    def _rect_intersection(self, rect: RectObject) -> tuple[PointObject] | None:
        """Implémentation interne de rect_intersection"""
        from ._segment import SegmentObject
        if not self._colliderect(rect):
            return None
        
        points = []
        r = rect.border_radius if rect.border_radius > 0 else 0
        
        if r <= 0:
            segments = [
                SegmentObject(PointObject(rect.left, rect.top), PointObject(rect.right, rect.top)),
                SegmentObject(PointObject(rect.right, rect.top), PointObject(rect.right, rect.bottom)),
                SegmentObject(PointObject(rect.right, rect.bottom), PointObject(rect.left, rect.bottom)),
                SegmentObject(PointObject(rect.left, rect.bottom), PointObject(rect.left, rect.top)),
            ]
            
            for segment in segments:
                intersections = self._segment_intersection(segment)
                if intersections:
                    points.extend(intersections)
        else:
            top_segment = SegmentObject(
                PointObject(rect.left + r, rect.top),
                PointObject(rect.right - r, rect.top)
            )
            bottom_segment = SegmentObject(
                PointObject(rect.left + r, rect.bottom),
                PointObject(rect.right - r, rect.bottom)
            )
            left_segment = SegmentObject(
                PointObject(rect.left, rect.top + r),
                PointObject(rect.left, rect.bottom - r)
            )
            right_segment = SegmentObject(
                PointObject(rect.right, rect.top + r),
                PointObject(rect.right, rect.bottom - r)
            )
            
            for segment in [top_segment, bottom_segment, left_segment, right_segment]:
                intersections = self._segment_intersection(segment)
                if intersections:
                    points.extend(intersections)
            
            corners = [
                (rect.left + r, rect.top + r),
                (rect.right - r, rect.top + r),
                (rect.left + r, rect.bottom - r),
                (rect.right - r, rect.bottom - r),
            ]
            
            for cx, cy in corners:
                corner_points = self._circle_intersection((PointObject(cx, cy), r))
                if corner_points:
                    points.extend(corner_points)
        
        unique_points = []
        seen = set()
        for p in points:
            key = (round(p.x, 6), round(p.y, 6))
            if key not in seen:
                unique_points.append(p)
                seen.add(key)
        
        return tuple(unique_points) if unique_points else None

    def circle_intersection(self, circle: CircleObject) -> tuple[PointObject] | None:
        """
        Calcule l'intersection avec un autre cercle
        
        Args:
            circle (CircleObject | tuple): autre cercle
            
        Returns:
            tuple[PointObject] | None: 0, 1 ou 2 points d'intersection
        """        
        if not isinstance(circle, CircleObject):
            _raise_error(self, 'circle_intersection', 'Invalid circle argument')
        return self._circle_intersection(circle)
    
    def _circle_intersection(self, circle: CircleObject) -> tuple[PointObject] | None:
        """Implémentation interne de circle_intersection"""        
        x1, y1 = self.centerx, self.centery
        r1 = self._radius

        x2, y2 = circle.centerx, circle.centery
        r2 = circle._radius
        
        dx = x2 - x1
        dy = y2 - y1
        d = math.sqrt(dx**2 + dy**2)
        
        if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
            return None
        
        if abs(d - (r1 + r2)) < 1e-10 or abs(d - abs(r1 - r2)) < 1e-10:
            ratio = r1 / d
            px = x1 + ratio * dx
            py = y1 + ratio * dy
            return (PointObject(px, py),)
        
        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = math.sqrt(r1**2 - a**2)
        
        px2 = x1 + a * dx / d
        py2 = y1 + a * dy / d
        
        p1x = px2 + h * dy / d
        p1y = py2 - h * dx / d
        
        p2x = px2 - h * dy / d
        p2y = py2 + h * dx / d
        
        return (PointObject(p1x, p1y), PointObject(p2x, p2y))

    def rect_collision_normal(self, rect: RectObject, collision_point: PointObject=None) -> VectorObject:
        """
        Renvoie le vecteur normal au point de collision avec un rectangle
        
        Args:
            rect (RectObject): rectangle avec lequel il y a collision
            collision_point (PointObject, optional): point de collision spécifique
            
        Returns:
            VectorObject: vecteur normal normalisé pointant vers l'extérieur du rectangle
        """
        from ._rect import _to_rect        
        rect = _to_rect(rect)
        return self._rect_collision_normal(rect, collision_point=collision_point)
    
    def _rect_collision_normal(self, rect: RectObject, collision_point: PointObject=None) -> VectorObject:
        """Implémentation interne de rect_collision_normal"""        
        if collision_point is None:
            collision_point = rect._closest_point(self._center)
        else:
            collision_point = _to_point(collision_point)
        
        r = rect.border_radius if rect.border_radius > 0 else 0
        px, py = collision_point.x, collision_point.y
        
        if r <= 0:
            epsilon = 1e-6
            
            if abs(py - rect.top) < epsilon:
                return VectorObject(0, -1)
            elif abs(py - rect.bottom) < epsilon:
                return VectorObject(0, 1)
            elif abs(px - rect.left) < epsilon:
                return VectorObject(-1, 0)
            elif abs(px - rect.right) < epsilon:
                return VectorObject(1, 0)
            else:
                normal = collision_point - self._center
                if normal.is_null():
                    return VectorObject(0, -1)
                return normal.normalized
        
        corners = [
            (rect.left + r, rect.top + r),
            (rect.right - r, rect.top + r),
            (rect.left + r, rect.bottom - r),
            (rect.right - r, rect.bottom - r),
        ]
        
        for cx, cy in corners:
            dist_to_corner = math.sqrt((px - cx)**2 + (py - cy)**2)
            
            if dist_to_corner < r + 1e-6:
                normal = VectorObject(px - cx, py - cy)
                if normal.is_null():
                    normal = collision_point - self._center
                if not normal.is_null():
                    return normal.normalized
        
        epsilon = 1e-6
        
        if rect.left + r <= px <= rect.right - r:
            if abs(py - rect.top) < epsilon:
                return VectorObject(0, -1)
            elif abs(py - rect.bottom) < epsilon:
                return VectorObject(0, 1)
        
        if rect.top + r <= py <= rect.bottom - r:
            if abs(px - rect.left) < epsilon:
                return VectorObject(-1, 0)
            elif abs(px - rect.right) < epsilon:
                return VectorObject(1, 0)
        
        normal = collision_point - self._center
        if normal.is_null():
            return VectorObject(0, -1)
        return normal.normalized

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, filling: bool = None, color: pygame.Color = None, border: bool = None, border_color: pygame.Color = None, border_width: int = None):
        """
        Dessine le cercle sur une surface donnée

        Args:
            surface (pygame.Surface): surface de dessin
            filling (bool, optional): remplissage
            color (pygame.Color, optional): couleur de remplissage
            border (bool, optional): bordure
            border_color (pygame.Color, optional): couleur de la bordure
            border_width (int, optional): épaisseur de la bordure
        """
        if not isinstance(surface, pygame.Surface):
            _raise_error(self, 'draw', 'Invalid surface argument')
        
        # paramètres d'affichage
        filling = self._filling if filling is None else filling
        color = self._color if color is None else _to_color(color)
        border = self._border if border is None else border
        border_color = self._border_color if border_color is None else _to_color(border_color)
        border_width = self._border_width if border_width is None else border_width
        border_around = self._border_around
        
        center_pos = (int(self.centerx), int(self.centery))
        radius = int(self._radius)
        
        # remplissage
        if filling:
            pygame.draw.circle(surface, color, center_pos, radius)
        
        # bordure
        if border:
            if border_around:
                # bordure externe
                pygame.draw.circle(surface, border_color, center_pos, radius + border_width, border_width)
            else:
                # bordure interne
                pygame.draw.circle(surface, border_color, center_pos, radius, border_width)