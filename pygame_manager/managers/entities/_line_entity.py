# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
import math

# ======================================== OBJET ========================================
class LineEntity(Entity):
    """
    Entity avec une droite géométrique et propriétés d'affichage
    
    Attributes:
        _line (context.geometry.Line): Objet géométrique droite
        _color (pygame.Color): Couleur de la droite RGB
        _width (int): Épaisseur de la droite
        _dashed (bool): Active l'affichage en pointillés
        _dash (int): Longueur des segments en pointillés
        _gap (int): Longueur des espaces entre segments
    """
    def __init__(
            self,
            point: tuple[Real, Real],
            vector: tuple[float, float],
            zorder: int = -1,
            panel: str | None = None
            ):
        """
        Initialise la droite
        
        Args:
            point (tuple[float, float]) : Point d'origine (x, y)
            vector (tuple[float, float]) : Vecteur directeur (vx, vy)
            zorder (int) : Ordre d'affichage (défaut: -1)
            panel (str | None) : Nom du panel (défaut: None)
        """
        # Vérifications
        point = context.geometry._to_point(point, copy=False)
        vector = context.geometry._to_vector(vector, copy=False)

        # Initialisation d'Entity
        super().__init__(zorder=zorder, panel=panel)
        
        # Objet géométrique
        self._line = context.geometry.Line(point, vector)

        # Paramètres d'affichage
        self._color = (0, 0, 0)
        self._width = 1

        self._dashed = False
        self._dash = 10
        self._gap = 6
    
    # ======================================== PROXY GEOMETRIQUE ========================================
    @property
    def line(self):
        """Renvoie la droite"""
        return self._line

    @property
    def origin(self) -> tuple[float, float]:
        """Renvoie le point d'origine de la droite"""
        return self._line.origin
    
    @origin.setter
    def origin(self, value: tuple[float, float]):
        """
        Fixe le point d'origine de la droite
        
        Args:
            value (tuple[float, float]): Nouveau point d'origine (x, y)
        """
        self._line.origin = value
    
    @property
    def vector(self) -> tuple[float, float]:
        """Renvoie le vecteur directeur de la droite"""
        return self._line.vector
    
    @vector.setter
    def vector(self, value: tuple[float, float]):
        """
        Fixe le vecteur directeur de la droite
        
        Args:
            value (tuple[float, float]): Nouveau vecteur directeur (vx, vy)
        """
        self._line.vector = value
    
    def get_cartesian_equation(self) -> dict[str, float]:
        """
        Renvoie l'équation cartésienne de la droite : ax + by + c = 0
        
        Returns:
            dict[str, float]: Dictionnaire avec clés 'a', 'b', 'c'
        """
        return self._line.get_cartesian_equation()
    
    # ======================================== PARAMETRES D'AFFICHAGE ========================================
    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur de la droite"""
        return self._color
    
    @color.setter
    def color(self, color: pygame.Color):
        """
        Fixe la couleur de la droite
        
        Args:
            color (pygame.Color): Nouvelle couleur
        """
        self._color = _to_color(color)
    
    @property
    def width(self) -> int:
        """Renvoie l'épaisseur de la droite"""
        return self._width
    
    @width.setter
    def width(self, width: int):
        """
        Fixe l'épaisseur de la droite
        
        Args:
            width (int): Nouvelle épaisseur
            
        Raises:
            ValueError: Si width <= 0
        """
        if not isinstance(width, int) or width <= 0:
            _raise_error(self, 'width', 'Invalid width argument')
        self._width = width
    
    @property
    def dashed(self) -> bool:
        """Vérifie si l'affichage en pointillés est actif"""
        return self._dashed
    
    @dashed.setter
    def dashed(self, value: bool):
        """
        Active ou désactive l'affichage en pointillés
        
        Args:
            value (bool): État de l'affichage en pointillés
            
        Raises:
            TypeError: Si value n'est pas un bool
        """
        if not isinstance(value, bool):
            _raise_error(self, 'dashed', 'Invalid value argument')
        self._dashed = value
    
    @property
    def dash(self) -> int:
        """Renvoie la longueur des segments en pointillés"""
        return self._dash
    
    @dash.setter
    def dash(self, length: int):
        """
        Fixe la longueur des segments en pointillés
        
        Args:
            length (int): Nouvelle longueur
            
        Raises:
            ValueError: Si length <= 0
        """
        if not isinstance(length, int) or length <= 0:
            _raise_error(self, 'dash', 'Invalid length argument')
        self._dash = length
    
    @property
    def gap(self) -> int:
        """Renvoie la longueur des espaces entre segments"""
        return self._gap
    
    @gap.setter
    def gap(self, length: int):
        """
        Fixe la longueur des espaces entre segments
        
        Args:
            length (int): Nouvelle longueur
            
        Raises:
            ValueError: Si length <= 0
        """
        if not isinstance(length, int) or length <= 0:
            _raise_error(self, 'gap', 'Invalid length argument')
        self._gap = length
    
    # ======================================== METHODES GEOMETRIQUES ========================================
    def contains(self, point: tuple[float, float]) -> bool:
        """
        Vérifie qu'un point est sur la droite
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si le point est sur la droite
        """
        return self._line.contains(point)
    
    def is_parallel(self, other) -> bool:
        """
        Vérifie si deux droites sont parallèles
        
        Args:
            other: Droite à tester (LineEntity ou Line)
            
        Returns:
            bool: True si parallèles
        """
        if isinstance(other, LineEntity):
            return self._line.is_parallel(other._line)
        return self._line.is_parallel(other)
    
    def is_orthogonal(self, other) -> bool:
        """
        Vérifie si deux droites sont orthogonales
        
        Args:
            other: Droite à tester (LineEntity ou Line)
            
        Returns:
            bool: True si orthogonales
        """
        if isinstance(other, LineEntity):
            return self._line.is_orthogonal(other._line)
        return self._line.is_orthogonal(other)
    
    def is_secant(self, other) -> bool:
        """
        Vérifie si deux droites sont sécantes
        
        Args:
            other: Droite à tester (LineEntity ou Line)
            
        Returns:
            bool: True si sécantes
        """
        if isinstance(other, LineEntity):
            return self._line.is_secant(other._line)
        return self._line.is_secant(other)
    
    def point(self, t: float) -> tuple[float, float]:
        """
        Renvoie le point de paramètre t : P = O + t*v
        
        Args:
            t (float): Paramètre
            
        Returns:
            tuple[float, float]: Coordonnées du point
        """
        return self._line.point(t)
    
    def project(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Renvoie le projeté d'un point sur la droite
        
        Args:
            point (tuple[float, float]): Point à projeter
            
        Returns:
            tuple[float, float]: Coordonnées du projeté
        """
        return self._line.project(point)
    
    def distance(self, point: tuple[float, float]) -> float:
        """
        Renvoie la distance entre un point et la droite
        
        Args:
            point (tuple[float, float]): Point distant
            
        Returns:
            float: Distance
        """
        return self._line.distance(point)
    
    def intersection(self, other) -> tuple[float, float] | None:
        """
        Renvoie le point d'intersection de deux droites
        
        Args:
            other: Droite à intersecter (LineEntity ou Line)
            
        Returns:
            tuple[float, float] | None: Coordonnées du point ou None si parallèles
        """
        if isinstance(other, LineEntity):
            return self._line.intersection(other._line)
        return self._line.intersection(other)
    
    def angle_with(self, other) -> float:
        """
        Renvoie l'angle entre deux droites (en radians)
        
        Args:
            other: Droite à comparer (LineEntity ou Line)
            
        Returns:
            float: Angle en radians
        """
        if isinstance(other, LineEntity):
            return self._line.angle_with(other._line)
        return self._line.angle_with(other)
    
    def symmetric(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Renvoie le symétrique d'un point par rapport à la droite
        
        Args:
            point (tuple[float, float]): Point à symétriser
            
        Returns:
            tuple[float, float]: Coordonnées du symétrique
        """
        return self._line.symmetric(point)
    
    #  ======================================== DEPLACMEMENT ========================================
    def translate(self, dx: float, dy: float):
        """
        Translate la droite
        
        Args:
            dx (float): Déplacement en x
            dy (float): Déplacement en y
        """
        self._line.translate(dx, dy)
    
    def move_up(self, dy: float = 1, min: float = None):
        """
        Déplace le segment vers le haut
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale y
        """
        self._line.translate(0, -dy)
        if min is not None:
            y1, y2 = self._line.start[1], self._line.end[1]
            center_y = (y1 + y2) / 2
            if center_y < min:
                self._line.translate(0, min - center_y)
    
    def move_down(self, dy: float = 1, max: float = None):
        """
        Déplace le segment vers le bas
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale y
        """
        self._line.translate(0, dy)
        if max is not None:
            y1, y2 = self._line.start[1], self._line.end[1]
            center_y = (y1 + y2) / 2
            if center_y > max:
                self._line.translate(0, max - center_y)
    
    def move_left(self, dx: float = 1, min: float = None):
        """
        Déplace le segment vers la gauche
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale x
        """
        self._line.translate(-dx, 0)
        if min is not None:
            x1, x2 = self._line.start[0], self._line.end[0]
            center_x = (x1 + x2) / 2
            if center_x < min:
                self._line.translate(min - center_x, 0)
    
    def move_right(self, dx: float = 1, max: float = None):
        """
        Déplace le segment vers la droite
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale x
        """
        self._line.translate(dx, 0)
        if max is not None:
            x1, x2 = self._line.start[0], self._line.end[0]
            center_x = (x1 + x2) / 2
            if center_x > max:
                self._line.translate(max - center_x, 0)
    
    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """
        Vérifie la collision avec un point
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si collision
        """
        return self._line.collidepoint(point)
    
    def collidesegment(self, segment) -> bool:
        """
        Vérifie la collision avec un segment
        
        Args:
            segment (context.geometry.Segment): Segment à tester
            
        Returns:
            bool: True si collision
        """
        return self._line.collidesegment(segment)
    
    def collideline(self, line) -> bool:
        """
        Vérifie la collision avec une droite
        
        Args:
            line (context.geometry.Line): Droite à tester
            
        Returns:
            bool: True si collision
        """
        return self._line.collideline(line)
    
    def collidecircle(self, circle) -> bool:
        """
        Vérifie la collision avec un cercle
        
        Args:
            circle (context.geometry.Circle): Cercle à tester
            
        Returns:
            bool: True si collision
        """
        return self._line.collidecircle(circle)
    
    def colliderect(self, rect) -> bool:
        """
        Vérifie la collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): Rectangle à tester
            
        Returns:
            bool: True si collision
        """
        return self._line.colliderect(rect)
    
    def collidepolygon(self, polygon) -> bool:
        """
        Vérifie la collision avec un polygone
        
        Args:
            polygon (context.geometry.Polygon): Polygone à tester
            
        Returns:
            bool: True si collision
        """
        return polygon._collideline(self._line)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass
    
    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, x_min: float = None, x_max: float = None,
             y_min: float = None, y_max: float = None):
        """
        Affiche la droite sur la surface
        
        Args:
            surface (pygame.Surface): Surface de dessin
            x_min (float): Limite gauche (défaut: 0)
            x_max (float): Limite droite (défaut: largeur surface)
            y_min (float): Limite haute (défaut: 0)
            y_max (float): Limite basse (défaut: hauteur surface)
        """
        x_min = 0 if x_min is None else x_min
        x_max = surface.get_width() if x_max is None else x_max
        y_min = 0 if y_min is None else y_min
        y_max = surface.get_height() if y_max is None else y_max
        
        borders = {
            "left": context.geometry.Line((x_min, y_min), (0, 1)),
            "top": context.geometry.Line((x_min, y_min), (1, 0)),
            "right": context.geometry.Line((x_max, y_max), (0, 1)),
            "bottom": context.geometry.Line((x_min, y_max), (1, 0))
        }
        
        points = []
        for border in borders.values():
            p = self._line.intersection(border)
            if p is None:
                continue
            x, y = p
            if x_min <= x <= x_max and y_min <= y <= y_max:
                points.append((x, y))
        
        points = list(dict.fromkeys(points))
        if len(points) < 2:
            return
        
        start_pos, end_pos = points[0], points[1]
        
        if self._dashed:
            self._draw_dashed(surface, start_pos, end_pos)
        elif self._width == 1:
            pygame.draw.aaline(surface, self._color, start_pos, end_pos)
        else:
            pygame.draw.line(surface, self._color, start_pos, end_pos, self._width)
    
    def _draw_dashed(self, surface: pygame.Surface, start: tuple[float, float], 
                     end: tuple[float, float]):
        """
        Dessine une droite en pointillés
        
        Args:
            surface (pygame.Surface): Surface de dessin
            start (tuple[float, float]): Point de départ
            end (tuple[float, float]): Point d'arrivée
        """
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
            seg_len = self._dash if draw else self._gap
            seg_len = min(seg_len, length - pos)
            
            if draw:
                sx = x1 + ux * pos
                sy = y1 + uy * pos
                ex = x1 + ux * (pos + seg_len)
                ey = y1 + uy * (pos + seg_len)
                
                if self._width == 1:
                    pygame.draw.aaline(surface, self._color, (sx, sy), (ex, ey))
                else:
                    pygame.draw.line(surface, self._color, (sx, sy), (ex, ey), self._width)
            
            pos += seg_len
            draw = not draw