# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class CircleObject:
    """
    Object géométrique 2D : Cercle
    """
    __slots__ = ["_center", "_radius"]
    PRECISION = 9
    def __init__(self, center: context.geometry.Point, radius: Real):
        """
        Args:
            center (context.geometry.Point) : point central du cercle
            radius (Real) : rayon du cercle
        """
        # centre
        self._center = context.geometry._to_point(center, copy=True)
        self._center.reshape(2)

        # rayon
        if not isinstance(radius, Real) or radius <= 0:  _raise_error(self, '__init__', 'Invalid radius argument')
        self._radius = float(radius)
    
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
    def center(self) -> context.geometry.Point:
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
    
    # ======================================== SETTERS ========================================
    @center.setter
    def center(self, point: context.geometry.Point):
        """Fixe le point central"""
        self._center = context.geometry._to_point(point, copy=True)
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

    # ======================================== PREDICATS ========================================
    def collidepoint(self, point: context.geometry.Point) -> bool:
        """
        Vérifie qu'un point soit dans le cercle

        Args:
            point (context.geometry.Point) : point à vérifier
        """
        point = context.geometry._to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: context.geometry.Point) -> bool:
        """Implémentation interne de collidepoint"""
        dist_sq = (point.x - self.centerx)**2 + (point.y - self.centery)**2
        return dist_sq <= self._radius**2

    def collideline(self, line: context.geometry.Line) -> bool:
        """
        Vérifie que la droite croise le cercle

        Args:
            line (context.geometry.Line) : droite à vérifier
        """
        if not isinstance(line, context.geometry.Line):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line: context.geometry.Line) -> bool:
        """Implémentation interne de collideline"""
        dist = line._distance(self._center)
        return dist <= self._radius

    def collidesegment(self, segment: context.geometry.Segment) -> bool:
        """
        Vérifie que le segment croise le cercle

        Args:
            segment (context.geometry.Segment) : segment à vérifier
        """
        if not isinstance(segment, context.geometry.Segment):
            _raise_error(self, 'collidesegment', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: context.geometry.Segment) -> bool:
        """Implémentation interne de collidesegment"""
        dist = segment._distance(self._center)
        return dist <= self._radius

    def colliderect(self, rect: context.geometry.Rect) -> bool:
        """
        Vérifie la collision avec un rectangle

        Args:
            rect (context.geometry.Rect) : rectangle à vérifier
        """
        rect = context.geometry._to_rect(rect)
        return self._colliderect(rect)
    
    def _colliderect(self, rect: context.geometry.Rect) -> bool:
        """Implémentation interne de colliderect"""
        return rect._collidecircle(self)

    def collidecircle(self, circle: context.geometry.Circle) -> bool:
        """
        Vérifie la collision avec un autre cercle

        Args:
            circle (context.geometry.Circle) : cercle à vérifier
        """
        if not isinstance(circle, context.geometry.Circle):
            _raise_error(self, 'collidecircle', 'Invalid circle argument')
        return self._collidecircle(circle)
    
    def _collidecircle(self, circle: context.geometry.Circle) -> bool:
        """Implémentation interne de collidecircle"""
        dist_sq = (self.centerx - circle.centerx)**2 + (self.centery - circle.centery)**2
        dist = math.sqrt(dist_sq)
        return dist <= self._radius + circle.radius

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> context.geometry.Circle:
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
    
    def translate(self, vector: context.geometry.Vector):
        """
        Translate le cercle selon un vecteur

        Args:
            vector (context.geometry.Vector) : vecteur de translation
        """
        vector = context.geometry._to_vector(vector)
        self._translate(vector)

    def _translate(self, vector: context.geometry.Vector):
        """Implémentation interne de translate"""
        self.centerx += vector.x
        self.centery += vector.y
    
    def point_from_angle(self, angle: Real, degrees: bool = False) -> context.geometry.Point:
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
    
    def _point_from_angle(self, angle: Real, degrees: bool = False) -> context.geometry.Point:
        """Implémentation interne de point_from_angle"""
        if degrees:
            angle = math.radians(angle)

        x = self.centerx + self._radius * math.cos(angle)
        y = self.centery + self._radius * math.sin(angle)
        
        return context.geometry.Point(x, y)

    def line_intersection(self, line: context.geometry.Line) -> tuple[context.geometry.Point] | None:
        """
        Renvoie les points d'intersection entre le cercle et une droite
        
        Args:
            line (context.geometry.Line): droite
            
        Returns:
            tuple[context.geometry.Point] | None: 0, 1 ou 2 points d'intersection
        """
        if not isinstance(line, context.geometry.Line):
            _raise_error(self, 'line_intersection', 'Invalid line argument')
        return self._line_intersection(line)
    
    def _line_intersection(self, line: context.geometry.Line) -> tuple[context.geometry.Point] | None:
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

    def segment_intersection(self, segment: context.geometry.Segment) -> tuple[context.geometry.Point] | None:
        """
        Renvoie les points d'intersection entre le cercle et un segment
        
        Args:
            segment (context.geometry.Segment): segment
            
        Returns:
            tuple[context.geometry.Point] | None: 0, 1 ou 2 points d'intersection
        """
        if not isinstance(segment, context.geometry.Segment):
            _raise_error(self, 'segment_intersection', 'Invalid segment argument')
        return self._segment_intersection(segment)
    
    def _segment_intersection(self, segment: context.geometry.Segment) -> tuple[context.geometry.Point] | None:
        """Implémentation interne de segment_intersection"""
        line = context.geometry.Line(segment._start, segment.get_vector())
        intersections = self.line_intersection(line)
        
        if intersections is None:
            return None
        
        valid_points = []
        for point in intersections:
            if point in segment:
                valid_points.append(point)
        
        return tuple(valid_points) if valid_points else None

    def rect_intersection(self, rect: context.geometry.Rect) -> tuple[context.geometry.Point] | None:
        """
        Renvoie les points d'intersection entre le cercle et un rectangle
        
        Args:
            rect (context.geometry.Rect): rectangle
            
        Returns:
            tuple[context.geometry.Point] | None: liste des points d'intersection
        """
        rect = context.geometry._to_rect(rect)
        return self._rect_intersection(rect)
        
    def _rect_intersection(self, rect: context.geometry.Rect) -> tuple[context.geometry.Point] | None:
        """Implémentation interne de rect_intersection"""
        if not self._colliderect(rect):
            return None
        
        points = []
        r = rect.border_radius if rect.border_radius > 0 else 0
        
        if r <= 0:
            segments = [
                context.geometry.Segment(context.geometry.Point(rect.left, rect.top), context.geometry.Point(rect.right, rect.top)),
                context.geometry.Segment(context.geometry.Point(rect.right, rect.top), context.geometry.Point(rect.right, rect.bottom)),
                context.geometry.Segment(context.geometry.Point(rect.right, rect.bottom), context.geometry.Point(rect.left, rect.bottom)),
                context.geometry.Segment(context.geometry.Point(rect.left, rect.bottom), context.geometry.Point(rect.left, rect.top)),
            ]
            
            for segment in segments:
                intersections = self._segment_intersection(segment)
                if intersections:
                    points.extend(intersections)
        else:
            top_segment = context.geometry.Segment(
                context.geometry.Point(rect.left + r, rect.top),
                context.geometry.Point(rect.right - r, rect.top)
            )
            bottom_segment = context.geometry.Segment(
                context.geometry.Point(rect.left + r, rect.bottom),
                context.geometry.Point(rect.right - r, rect.bottom)
            )
            left_segment = context.geometry.Segment(
                context.geometry.Point(rect.left, rect.top + r),
                context.geometry.Point(rect.left, rect.bottom - r)
            )
            right_segment = context.geometry.Segment(
                context.geometry.Point(rect.right, rect.top + r),
                context.geometry.Point(rect.right, rect.bottom - r)
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
                corner_points = self._circle_intersection(CircleObject(context.geometry.Point(cx, cy), r))
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

    def circle_intersection(self, circle: context.geometry.Circle) -> tuple[context.geometry.Point] | None:
        """
        Calcule l'intersection avec un autre cercle
        
        Args:
            circle (context.geometry.Circle | tuple): autre cercle
            
        Returns:
            tuple[context.geometry.Point] | None: 0, 1 ou 2 points d'intersection
        """        
        if not isinstance(circle, context.geometry.Circle):
            _raise_error(self, 'circle_intersection', 'Invalid circle argument')
        return self._circle_intersection(circle)
    
    def _circle_intersection(self, circle: context.geometry.Circle) -> tuple[context.geometry.Point] | None:
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
            return (context.geometry.Point(px, py),)
        
        a = (r1**2 - r2**2 + d**2) / (2 * d)
        h = math.sqrt(r1**2 - a**2)
        
        px2 = x1 + a * dx / d
        py2 = y1 + a * dy / d
        
        p1x = px2 + h * dy / d
        p1y = py2 - h * dx / d
        
        p2x = px2 - h * dy / d
        p2y = py2 + h * dx / d
        
        return (context.geometry.Point(p1x, p1y), context.geometry.Point(p2x, p2y))

    def rect_collision_normal(self, rect: context.geometry.Rect, collision_point: context.geometry.Point=None) -> context.geometry.Vector:
        """
        Renvoie le vecteur normal au point de collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): rectangle avec lequel il y a collision
            collision_point (context.geometry.Point, optional): point de collision spécifique
            
        Returns:
            context.geometry.Vector: vecteur normal normalisé pointant vers l'extérieur du rectangle
        """
        rect = context.geometry._to_rect(rect)
        return self._rect_collision_normal(rect, collision_point=collision_point)
    
    def _rect_collision_normal(self, rect: context.geometry.Rect, collision_point: context.geometry.Point=None) -> context.geometry.Vector:
        """Implémentation interne de rect_collision_normal"""        
        if collision_point is None:
            collision_point = rect._closest_point(self._center)
        else:
            collision_point = context.geometry._to_point(collision_point)
        
        r = rect.border_radius if rect.border_radius > 0 else 0
        px, py = collision_point.x, collision_point.y
        
        if r <= 0:
            epsilon = 1e-6
            
            if abs(py - rect.top) < epsilon:
                return context.geometry.Vector(0, -1)
            elif abs(py - rect.bottom) < epsilon:
                return context.geometry.Vector(0, 1)
            elif abs(px - rect.left) < epsilon:
                return context.geometry.Vector(-1, 0)
            elif abs(px - rect.right) < epsilon:
                return context.geometry.Vector(1, 0)
            else:
                normal = self._center - collision_point
                if normal.is_null():
                    return context.geometry.Vector(0, -1)
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
                normal = context.geometry.Vector(px - cx, py - cy)
                if normal.is_null():
                    normal = self._center - collision_point
                if not normal.is_null():
                    return normal.normalized
        
        epsilon = 1e-6
        
        if rect.left + r <= px <= rect.right - r:
            if abs(py - rect.top) < epsilon:
                return context.geometry.Vector(0, -1)
            elif abs(py - rect.bottom) < epsilon:
                return context.geometry.Vector(0, 1)
        
        if rect.top + r <= py <= rect.bottom - r:
            if abs(px - rect.left) < epsilon:
                return context.geometry.Vector(-1, 0)
            elif abs(px - rect.right) < epsilon:
                return context.geometry.Vector(1, 0)
        
        normal = self._center - collision_point
        if normal.is_null():
            return context.geometry.Vector(0, -1)
        return normal.normalized