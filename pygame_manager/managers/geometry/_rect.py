# ======================================== IMPORTS ========================================
from __future__ import annotations
from ._core import *

# ======================================== OBJET ========================================
class RectObject:
    """
    Object géométrique 2D : Rectangle
    """
    __slots__ = ["_O", "_w", "_h", "_filling", "_color", "_border", "_border_color", "_border_width", "_border_around", "_border_radius",
                "_border_topleft_radius", "_border_topright_radius", "_border_bottomleft_radius", "_border_bottomright_radius"]
    
    def __init__(self, point: geometry.Point, width: Real, height: Real):
        # point haut gauche
        self._O = geometry._to_point(point)       
        self._O.reshape(2)

        # largeur
        if not isinstance(width, Real) or width <= 0:
            _raise_error(self, '__init__', 'Invalid width argument')
        self._w = geometry.Vector(width, 0)

        # hauteur
        if not isinstance(height, Real) or height <= 0:
            _raise_error(self, '__init__', 'Invalid height argument')
        self._h = geometry.Vector(0, height)

        # remplissage
        self._filling = True
        self._color = (255, 255, 255)

        # bordure
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False

        # forme
        self._border_radius = -1
        self._border_topleft_radius = -1
        self._border_topright_radius = -1
        self._border_bottomleft_radius = -1
        self._border_bottomright_radius = -1

    def __repr__(self) -> str:
        """Représentation du rect"""
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
    
    def __iter__(self) -> Iterator[geometry.Point]:
        """Itération sur les sommets"""
        for vertex in [
            geometry.Point(*self.topleft), 
            geometry.Point(*self.topright), 
            geometry.Point(*self.bottomright), 
            geometry.Point(*self.bottomleft)
        ]: 
            yield vertex 

    def __hash__(self) -> int:
        """Renvoie le rect hashé"""
        return hash(self.to_tuple())
    
    # ======================================== GETTERS ========================================
    @property
    def rect(self) -> pygame.Rect:
        """Renvoie l'objet pygame.Rect"""
        return pygame.Rect(*map(int, [self.x, self.y, self.width, self.height]))
    
    # position
    def get_pos(self) -> geometry.Point:
        """Renvoie le point positionnel"""
        return self._O.copy()
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x"""
        return self._O.x
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y"""
        return self._O.y
    
    @property
    def topleft(self) -> geometry.Point:
        """Renvoie le point haut gauche"""
        return self._O.copy()
    
    @property
    def top(self) -> float:
        """Renvoie la coordonnée du haut"""
        return self.y
    
    @property
    def topright(self) -> geometry.Point:
        """Renvoie le point haut droit"""
        return self._O + self._w
    
    @property
    def right(self) -> float:
        """Renvoie la coordonnée de la droite"""
        return self.x + self.width
    
    @property
    def bottomright(self) -> geometry.Point:
        """Renvoie le du point bas droit"""
        return self._O + self._w + self._h
    
    @property
    def bottom(self) -> float:
        """Renvoie la coordonnée du bas"""
        return self.y + self.height
    
    @property
    def bottomleft(self) -> geometry.Point:
        """Renvoie le du point bas gauche"""
        return self._O + self._h
    
    @property
    def left(self) -> float:
        """Renvoie la coordonnée de la gauche"""
        return self.x
    
    @property
    def center(self) -> geometry.Point:
        """Renvoie le point central"""
        return self._O + 0.5 * (self._w + self._h)
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self.x + self.width / 2

    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self.y + self.height / 2

    # taille
    def get_size(self) -> tuple[float, float]:
        """Renvoie les dimensions du rect"""
        return (self.width, self.height)
    
    @property
    def width(self) -> float:
        """Renvoie la largeur"""
        return self._w.norm
    
    @property
    def height(self) -> float:
        """Renvoie la hauteur"""
        return self._h.norm
    
    @property
    def diagonal(self) -> float:
        """Renvoie la longueur de la diagonale"""
        return math.sqrt(self.width**2 + self.height**2)
    
    @property
    def perimeter(self) -> float:
        """Renvoie le périmètre"""
        return 2 * (self.width + self.height)
    
    @property
    def area(self) -> float:
        """Renvoie l'aire"""
        return self.width * self.height
    
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
        """Vérifie que la bordure soit autour du rect"""
        return self._border_around
    
    @property
    def border_radius_max(self) -> int:
        """Renvoie le rayon maximum d'arrondissement des coins"""
        return int(min(self.width // 2, self.height // 2))
    
    @property
    def border_radius(self) -> int:
        """Renvoie l'arrondi des coins"""
        return self._border_radius
    
    @property
    def border_topleft_radius(self) -> int:
        """Renvoie l'arrondi du coin haut gauche"""
        return self._border_topleft_radius
    
    @property
    def border_topright_radius(self) -> int:
        """Renvoie l'arrondi du coin haut droit"""
        return self._border_topright_radius
    
    @property
    def border_bottomleft_radius(self) -> int:
        """Renvoie l'arrondi du coin bas gauche"""
        return self._border_bottomleft_radius
    
    @property
    def border_bottomright_radius(self) -> int:
        """Renvoie l'arrondi du coin bas droit"""
        return self._border_bottomright_radius

    # ======================================== SETTERS ========================================
    # position
    @x.setter
    def x(self, coordinate: Real):
        """Fixe la coordonnée x"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_x', 'Invalid coordinate argument')
        self._O.x = coordinate
    
    @y.setter
    def y(self, coordinate: Real):
        """Fixe la coordonnée y"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_y', 'Invalid coordinate argument')
        self._O.y = coordinate

    @topleft.setter
    def topleft(self, point: geometry.Point):
        """Fixe les coordonnées du coin haut gauche"""
        self._O = geometry._to_point(point)

    @top.setter
    def top(self, coordinate: Real):
        """Fixe la coordonnée du haut"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_top', 'Invalid coordinate argument')
        self._O.y = coordinate

    @topright.setter
    def topright(self, point: geometry.Point):
        """Fixe les coordonnées du coin haut droit"""
        self._O = geometry._to_point(point) - self._w
    
    @right.setter
    def right(self, coordinate: Real):
        """Fixe la coordonnée de la droite"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_right', 'Invalid coordinate argument')
        self._O.x = coordinate - self.width

    @bottomright.setter
    def bottomright(self, point: geometry.Point):
        """Fixe les coordonnées du coin bas droit"""
        self._O = geometry._to_point(point) - (self._w + self._h)
    
    @bottom.setter
    def bottom(self, coordinate: Real):
        """Fixe la coordonnée du bas"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_bottom', 'Invalid coordinate argument')
        self._O.y = coordinate - self.height
    
    @bottomleft.setter
    def bottomleft(self, point: geometry.Point):
        """Fixe les coordonnées du coin bas gauche"""
        self._O = geometry._to_point(point) - self._h

    @left.setter
    def left(self, coordinate: Real):
        """Fixe la coordonnée de la gauche"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_left', 'Invalid coordinate argument')
        self._O.x = coordinate
    
    @center.setter
    def center(self, point: geometry.Point):
        """Fixe les coordonnées du centre"""
        self._O = geometry._to_point(point) - 0.5 * (self._w + self._h)

    @centerx.setter
    def centerx(self, coordinate: Real):
        """Fixe la coordonnée x du centre"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_centerx', 'Invalid coordinate argument')
        self._O.x = coordinate - self.width / 2
    
    @centery.setter
    def centery(self, coordinate: Real):
        """Fixe la coordonnée y du centre"""
        if not isinstance(coordinate, Real):
            _raise_error(self, 'set_centery', 'Invalid coordinate argument')
        self._O.y = coordinate - self.height / 2
    
    @width.setter
    def width(self, width: Real):
        """Fixe la largeur"""
        if not isinstance(width, Real) or width <= 0:
            _raise_error(self, 'set_width', 'Invalid width argument')
        self._w.set_norm(width)

    @height.setter
    def height(self, height: Real):
        """Fixe la hauteur"""
        if not isinstance(height, Real) or height <= 0:
            _raise_error(self, 'set_height', 'Invalid height argument')
        self._h.set_norm(height)

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
        """Active ou non la bordure à l'extérieur du rect"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_border_around', 'Invalid value argument')
        self._border_around = value

    @border_radius.setter
    def border_radius(self, radius: int):
        """Fixe l'arrondi des coins"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_radius', 'Invalid radius argument')
        self._border_radius = min(radius, self.border_radius_max)

    @border_topleft_radius.setter
    def border_topleft_radius(self, radius: int):
        """Fixe l'arrondi du coin haut gauche"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_topleft_radius', 'Invalid radius argument')
        self._border_topleft_radius = min(radius, self.border_radius_max)
    
    @border_topright_radius.setter
    def border_topright_radius(self, radius: int):
        """Fixe l'arrondi du coin haut droit"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_topright_radius', 'Invalid radius argument')
        self._border_topright_radius = min(radius, self.border_radius_max)

    @border_bottomleft_radius.setter
    def border_bottomleft_radius(self, radius: int):
        """Fixe l'arrondi du coin bas gauche"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_bottomleft_radius', 'Invalid radius argument')
        self._border_bottomleft_radius = min(radius, self.border_radius_max)

    @border_bottomright_radius.setter
    def border_bottomright_radius(self, radius: int):
        """Fixe l'arrondi du coin bas droit"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_bottomright_radius', 'Invalid radius argument')
        self._border_bottomright_radius = min(radius, self.border_radius_max)

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: geometry.Vector) -> geometry.Rect:
        """Renvoie l'image du rect par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(vector)
        return result
    
    def __radd__(self, vector: geometry.Vector) -> geometry.Rect:
        """Renvoie l'image du rect par le vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(vector)
        return result
    
    def __sub__(self, vector: geometry.Vector) -> geometry.Rect:
        """Renvoie l'image du rect par l'opposé du vecteur donné"""
        vector = geometry._to_vector(vector, raised=False)
        if vector is None: return NotImplemented
        result = self.copy()
        result._translate(-vector)
        return result
    
    # ======================================== PREDICATS & COLLISIONS ========================================
    def collidepoint(self, point: geometry.Point) -> bool:
        """
        Vérifie que le point se trouve dans le rect

        Args:
            point (geometry.Point) : point à vérifier
        """
        point = geometry._to_point(point)
        return self._collidepoint(point)
    
    def _collidepoint(self, point: geometry.Point) -> bool:
        """Implémentation interne de collidepoint"""
        px, py = point.x, point.y
        if self._border_radius <= 0:
            return self.left <= px <= self.right and self.top <= py <= self.bottom
        
        r = self._border_radius
        
        if self.left + r <= px <= self.right - r:
            return self.top <= py <= self.bottom
        if self.top + r <= py <= self.bottom - r:
            return self.left <= px <= self.right
        
        corners = [
            (self.left + r, self.top + r),
            (self.right - r, self.top + r),
            (self.left + r, self.bottom - r),
            (self.right - r, self.bottom - r),
        ]
        
        for cx, cy in corners:
            dx = px - cx
            dy = py - cy
            dist_sq = dx**2 + dy**2
            
            in_quadrant = False
            if cx < self.centerx:
                if cy < self.centery:
                    in_quadrant = (px <= cx and py <= cy)
                else:
                    in_quadrant = (px <= cx and py >= cy)
            else:
                if cy < self.centery:
                    in_quadrant = (px >= cx and py <= cy)
                else:
                    in_quadrant = (px >= cx and py >= cy)
            
            if in_quadrant and dist_sq <= r**2:
                return True
        
        return False

    def collideline(self, line: geometry.Line) -> bool:
        """Vérifie que la ligne croise le rect"""
        if not isinstance(line, geometry.Line):
            _raise_error(self, 'collideline', 'Invalid line argument')
        return self._collideline(line)
    
    def _collideline(self, line) -> bool:
        """Implémentation interne de collideline"""        
        intersections = self._line_intersection(line)
        return intersections is not None and len(intersections) > 0

    def collidesegment(self, segment: geometry.Segment) -> bool:
        """Vérifie qu'un segment croise le rect"""
        if not isinstance(segment, geometry.Segment):
            _raise_error(self, 'collidesegment', 'Invalid segment argument')
        return self._collidesegment(segment)
    
    def _collidesegment(self, segment: geometry.Segment) -> bool:
        """Implémentation interne de collidesegment"""        
        if self._collidepoint(segment._start) or self._collidepoint(segment._end):
            return True
        
        line = geometry.Line(segment._start, segment.get_vector())
        intersections = self._line_intersection(line)
        
        if intersections is None: return False
        for inter in intersections:
            if inter in segment:
                return True
        return False

    def colliderect(self, rect: geometry.Rect) -> bool:
        """
        Vérifie la superposition de deux rects

        Args:
            rect (geometry.Rect) : rect à vérifier
        """
        rect = geometry._to_rect(rect)
        return self._colliderect(rect)
    
    def _colliderect(self, rect: geometry.Rect) -> bool:
        """Implémentation interne de colliderect"""       
        if self.right < rect.left or rect.right < self.left:
            return False
        if self.bottom < rect.top or rect.bottom < self.top:
            return False
        
        if self._border_radius == 0 and rect._border_radius == 0:
            return True
        
        r1 = self._border_radius
        r2 = rect._border_radius

        corners1 = [
            (self.left + r1, self.top + r1),
            (self.right - r1, self.top + r1),
            (self.left + r1, self.bottom - r1),
            (self.right - r1, self.bottom - r1),
        ] if r1 > 0 else []
        
        corners2 = [
            (rect.left + r2, rect.top + r2),
            (rect.right - r2, rect.top + r2),
            (rect.left + r2, rect.bottom - r2),
            (rect.right - r2, rect.bottom - r2),
        ] if r2 > 0 else []
        
        central1_left = self.left + r1
        central1_right = self.right - r1
        central1_top = self.top + r1
        central1_bottom = self.bottom - r1
        
        h1_collides = not (central1_right < rect.left or central1_left > rect.right or self.top > rect.bottom or self.bottom < rect.top)
        v1_collides = not (self.left > rect.right or self.right < rect.left or central1_bottom < rect.top or central1_top > rect.bottom)
        
        if h1_collides or v1_collides:
            return True
        
        if r1 > 0 and r2 > 0:
            for cx1, cy1 in corners1:
                for cx2, cy2 in corners2:
                    dist_sq = (cx1 - cx2)**2 + (cy1 - cy2)**2
                    if dist_sq <= (r1 + r2)**2:
                        return True
        
        if r1 > 0:
            for cx, cy in corners1:
                closest_x = max(rect.left, min(cx, rect.right))
                closest_y = max(rect.top, min(cy, rect.bottom))
                
                dist_sq = (cx - closest_x)**2 + (cy - closest_y)**2
                if dist_sq <= r1**2:
                    return True
        
        if r2 > 0:
            for cx, cy in corners2:
                closest_x = max(self.left, min(cx, self.right))
                closest_y = max(self.top, min(cy, self.bottom))
                
                dist_sq = (cx - closest_x)**2 + (cy - closest_y)**2
                if dist_sq <= r2**2:
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
        center = circle._center
        radius = circle._radius

        closest = self._closest_point(center)
        
        if self._border_radius <= 0:
            dist_sq = (center.x - closest.x)**2 + (center.y - closest.y)**2
            return dist_sq <= radius**2
        
        r = self._border_radius
        cx, cy = center.x, center.y
        
        if self.left + r <= cx <= self.right - r:
            dist = abs(cy - closest.y)
            return dist <= radius
        if self.top + r <= cy <= self.bottom - r:
            dist = abs(cx - closest.x)
            return dist <= radius
        
        corners = [
            (self.left + r, self.top + r),
            (self.right - r, self.top + r),
            (self.left + r, self.bottom - r),
            (self.right - r, self.bottom - r),
        ]
        
        for corner_x, corner_y in corners:
            in_quadrant = False
            if corner_x < self.centerx:
                if corner_y < self.centery:
                    in_quadrant = (cx < self.left + r and cy < self.top + r)
                else:
                    in_quadrant = (cx < self.left + r and cy > self.bottom - r)
            else:
                if corner_y < self.centery:
                    in_quadrant = (cx > self.right - r and cy < self.top + r)
                else:
                    in_quadrant = (cx > self.right - r and cy > self.bottom - r)
            
            if in_quadrant:
                dist_sq = (cx - corner_x)**2 + (cy - corner_y)**2
                dist = math.sqrt(dist_sq)
                return dist <= radius + r
        
        dist_sq = (cx - closest.x)**2 + (cy - closest.y)**2
        return dist_sq <= radius**2

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> geometry.Rect:
        """Renvoie une copie du rect"""
        return _deepcopy(self)

    def to_tuple(self) -> tuple[float, float, float, float]:
        """Renvoie les propriétés dans un tuple"""
        return (self.x, self.y, self.width, self.height)

    def to_list(self) -> list[float]:
        """Renvoie les propriétés dans une liste"""
        return [self.x, self.y, self.width, self.height]
    
    def scale(self, ratio: Real):
        """
        Redimensionne le rectangle

        Args:
            ratio (Real) : ratio de redimensionnement
        """
        if not isinstance(ratio, Real) or ratio <= 0:
            _raise_error(self, 'scale', 'Invalid ratio argument')
        self.width = self.width * ratio
        self.height = self.height * ratio
    
    def translate(self, vector: geometry.Vector):
        """
        Translate le rect selon un vecteur

        Args:
            vector (geometry.Vector) : vecteur de translation
        """
        vector = geometry._to_vector(vector)
        self.x += vector.x
        self.y += vector.y
    
    def closest_point(self, point: geometry.Point):
        """Renvoie le point du rect le plus proche d'un point donné"""
        point = geometry._to_point(point)
        px, py = point.x, point.y
        
        # Sans arrondi, simple clamping
        if self._border_radius <= 0:
            x = max(self.left, min(px, self.right))
            y = max(self.top, min(py, self.bottom))
            return geometry.Point(x, y)
        
        r = self._border_radius
        
        # Zone centrale horizontale
        if self.left + r <= px <= self.right - r:
            y = max(self.top, min(py, self.bottom))
            return geometry.Point(px, y)
        
        # Zone centrale verticale
        if self.top + r <= py <= self.bottom - r:
            x = max(self.left, min(px, self.right))
            return geometry.Point(x, py)
        
        # Dans une zone de coin arrondi
        corners = [
            (self.left + r, self.top + r, -1, -1),
            (self.right - r, self.top + r, 1, -1),
            (self.left + r, self.bottom - r, -1, 1),
            (self.right - r, self.bottom - r, 1, 1),
        ]
        
        for cx, cy, sign_x, sign_y in corners:
            in_quadrant = (sign_x * (px - cx) >= 0 and sign_y * (py - cy) >= 0)
            
            if in_quadrant:
                dx = px - cx
                dy = py - cy
                dist = math.sqrt(dx**2 + dy**2)
                
                if dist == 0:
                    return geometry.Point(cx + sign_x * r, cy)
                
                if dist <= r:
                    return geometry.Point(px, py)
                else:
                    ratio = r / dist
                    return geometry.Point(cx + dx * ratio, cy + dy * ratio)
        
        # Fallback
        x = max(self.left, min(px, self.right))
        y = max(self.top, min(py, self.bottom))
        return geometry.Point(x, y)
    
    def line_intersection(self, line):
        """Renvoie l'ensemble des points d'intersection entre la droite et le rect"""
        if not isinstance(line, geometry.Line): 
            _raise_error(self, 'line_intersection', 'Invalid line argument')
        
        # Propriétés du rect
        top, right, bottom, left = self.top, self.right, self.bottom, self.left
        r = self._border_radius if self._border_radius > 0 else 0

        # Droite
        x0, y0 = line.get_origin().x, line.get_origin().y
        dx, dy = line.get_vector().x, line.get_vector().y

        # Intersections
        points = []

        # Côtés du rect
        if dy != 0:  # haut
            t = (top - y0) / dy
            x = x0 + t * dx
            if left + r <= x <= right - r:
                points.append(geometry.Point(x, top))

        if dx != 0:  # droit
            t = (right - x0) / dx
            y = y0 + t * dy
            if top + r <= y <= bottom - r:
                points.append(geometry.Point(right, y))

        if dy != 0:  # bas
            t = (bottom - y0) / dy
            x = x0 + t * dx
            if left + r <= x <= right - r:
                points.append(geometry.Point(x, bottom))

        if dx != 0:  # gauche
            t = (left - x0) / dx
            y = y0 + t * dy
            if top + r <= y <= bottom - r:
                points.append(geometry.Point(left, y))

        # Coins arrondis
        if r > 0:
            corners = [
                (left + r, top + r),
                (right - r, top + r),
                (left + r, bottom - r),
                (right - r, bottom - r),
            ]

            for cx, cy in corners:
                # Équation quadratique de l'intersection droite / cercle
                A = dx**2 + dy**2
                if A == 0:
                    continue
                    
                B = 2 * (dx*(x0 - cx) + dy*(y0 - cy))
                C = (x0 - cx)**2 + (y0 - cy)**2 - r**2

                discriminant = B**2 - 4*A*C
                if discriminant < 0:
                    continue
                    
                sqrt_d = math.sqrt(discriminant)
                t_list = [(-B - sqrt_d) / (2*A), (-B + sqrt_d) / (2*A)]

                for t in t_list:
                    px = x0 + t*dx
                    py = y0 + t*dy

                    # Filtrage selon le quadrant
                    if cx < left + r*1.5:
                        if px > cx: 
                            continue
                    else:
                        if px < cx: 
                            continue
                    if cy < top + r*1.5:
                        if py > cy:
                            continue
                    else:
                        if py < cy:
                            continue

                    points.append(geometry.Point(px, py))

        # Suppression des doublons
        unique_points = []
        seen = set()
        for p in points:
            key = (round(p.x, 6), round(p.y, 6))
            if key not in seen:
                unique_points.append(p)
                seen.add(key)

        if not unique_points:
            return None

        # Tri par paramètre t
        def t_of(p):
            return ((p.x - x0)/dx) if dx != 0 else ((p.y - y0)/dy)

        unique_points.sort(key=t_of)
        return tuple(unique_points)

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, filling: bool=None, color: pygame.Color=None, 
             border: bool=None, border_width: int=None, border_color: pygame.Color=None):
        """
        Dessine le rect sur une surface donnée

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
        rect = self.rect
        filling = self._filling if filling is None else filling
        color = self._color if color is None else _to_color(color)
        border = self._border if border is None else border
        border_width = self._border_width if border_width is None else border_width
        border_color = self._border_color if border_color is None else _to_color(border_color)
        border_around = self._border_around
        border_radius = self._border_radius
        border_topleft_radius = self._border_topleft_radius
        border_topright_radius = self._border_topright_radius
        border_bottomleft_radius = self._border_bottomleft_radius
        border_bottomright_radius = self._border_bottomright_radius

        # remplissage
        if filling:
            pygame.draw.rect(surface, color, rect, 0, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)
        
        # bordure
        if border:
            if border_around:
                rect_around = pygame.Rect(rect.left - border_width, rect.top - border_width, rect.width + 2 * border_width, rect.height + 2 * border_width)
                pygame.draw.rect(surface, border_color, rect_around, border_width, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)
            else:
                pygame.draw.rect(surface, border_color, rect, border_width, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)