# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
import math

# ======================================== OBJET ========================================
class SegmentEntity(Entity):
    """
    Entity avec un segment géométrique et propriétés d'affichage
    
    Attributes:
        _segment (context.geometry.Segment): Objet géométrique segment
        _color (tuple[int, int, int]): Couleur du segment RGB
        _width (int): Épaisseur du segment
        _dashed (bool): Active l'affichage en pointillés
        _dash (int): Longueur des segments en pointillés
        _gap (int): Longueur des espaces entre segments
    """
    
    def __init__(
            self,
            start: tuple[float, float],
            end: tuple[float, float],
            zorder: int = -1,
            panel: str | None = None
            ):
        """
        Initialise le segment
        
        Args:
            start (tuple[float, float]): Point de départ (x, y)
            end (tuple[float, float]): Point d'arrivée (x, y)
            zorder (int): Ordre d'affichage (défaut: -1)
            panel (str | None): Nom du panel (défaut: None)
        """
        # Vérifications
        start = context.geometry._to_point(start, copy=False)
        end = context.geometry._to_point(end, copy=False)

        # Initialisation d'Entity
        super().__init__(zorder=zorder, panel=panel)
        
        # Object géométrique
        self._segment = context.geometry.Segment(start, end)

        # Paramètres d'affichage
        self._color = (0, 0, 0)
        self._width = 1
        
        self._dashed = False
        self._dash = 10
        self._gap = 6
    
    # ======================================== PROXY GEOMETRIQUE ========================================
    @property
    def segment(self):
        """Renvoie le segment"""
        return self._segment

    @property
    def start(self) -> tuple[float, float]:
        """Renvoie le point de départ du segment"""
        return self._segment.start
    
    @start.setter
    def start(self, value: tuple[float, float]):
        """
        Fixe le point de départ du segment
        
        Args:
            value (tuple[float, float]): Nouveau point de départ (x, y)
        """
        self._segment.start = value
    
    @property
    def end(self) -> tuple[float, float]:
        """Renvoie le point d'arrivée du segment"""
        return self._segment.end
    
    @end.setter
    def end(self, value: tuple[float, float]):
        """
        Fixe le point d'arrivée du segment
        
        Args:
            value (tuple[float, float]): Nouveau point d'arrivée (x, y)
        """
        self._segment.end = value
    
    @property
    def midpoint(self) -> tuple[float, float]:
        """Renvoie le point au milieu du segment"""
        return self._segment.midpoint
    
    @property
    def vector(self) -> tuple[float, float]:
        """Renvoie le vecteur directeur du segment"""
        return self._segment.vector
    
    @property
    def length(self) -> float:
        """Renvoie la longueur du segment"""
        return self._segment.length
    
    def __getitem__(self, i: int) -> tuple[float, float]:
        """
        Renvoie l'une des deux extrémités
        
        Args:
            i (int): Index (0 pour start, 1 pour end)
            
        Returns:
            tuple[float, float]: Coordonnées de l'extrémité
        """
        return self._segment[i]
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du milieu"""
        return self._segment.midpoint[0]
    
    @x.setter
    def x(self, value: float):
        """
        Déplace le segment pour que son milieu ait cette coordonnée x
        
        Args:
            value (float): Nouvelle coordonnée x du milieu
        """
        mx, my = self._segment.midpoint
        dx = value - mx
        self._segment.translate(dx, 0)
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du milieu"""
        return self._segment.midpoint[1]
    
    @y.setter
    def y(self, value: float):
        """
        Déplace le segment pour que son milieu ait cette coordonnée y
        
        Args:
            value (float): Nouvelle coordonnée y du milieu
        """
        mx, my = self._segment.midpoint
        dy = value - my
        self._segment.translate(0, dy)
    
    # ======================================== PARAMETRES D'AFFICHAGE ========================================
    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur du segment"""
        return self._color
    
    @color.setter
    def color(self, color: pygame.Color):
        """
        Fixe la couleur du segment
        
        Args:
            color (pygame.Color): Nouvelle couleur
        """
        self._color = _to_color(color)
    
    @property
    def width(self) -> int:
        """Renvoie l'épaisseur du segment"""
        return self._width
    
    @width.setter
    def width(self, width: int):
        """
        Fixe l'épaisseur du segment
        
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
        Vérifie qu'un point est sur le segment
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si le point est sur le segment
        """
        return self._segment.contains(point)
    
    def is_parallel(self, other) -> bool:
        """
        Vérifie si deux segments sont parallèles
        
        Args:
            other: Segment à tester (SegmentEntity ou Segment)
            
        Returns:
            bool: True si parallèles
        """
        if isinstance(other, SegmentEntity):
            return self._segment.is_parallel(other._segment)
        return self._segment.is_parallel(other)
    
    def is_orthogonal(self, other) -> bool:
        """
        Vérifie si deux segments sont orthogonaux
        
        Args:
            other: Segment à tester (SegmentEntity ou Segment)
            
        Returns:
            bool: True si orthogonaux
        """
        if isinstance(other, SegmentEntity):
            return self._segment.is_orthogonal(other._segment)
        return self._segment.is_orthogonal(other)
    
    def is_secant(self, other) -> bool:
        """
        Vérifie si deux segments sont sécants
        
        Args:
            other: Segment à tester (SegmentEntity ou Segment)
            
        Returns:
            bool: True si sécants
        """
        if isinstance(other, SegmentEntity):
            return self._segment.is_secant(other._segment)
        return self._segment.is_secant(other)
    
    def project(self, point: tuple[float, float]) -> tuple[float, float]:
        """
        Renvoie le projeté d'un point sur le segment
        
        Args:
            point (tuple[float, float]): Point à projeter
            
        Returns:
            tuple[float, float]: Coordonnées du projeté
        """
        return self._segment.project(point)
    
    def distance(self, point: tuple[float, float]) -> float:
        """
        Renvoie la distance entre un point et le segment
        
        Args:
            point (tuple[float, float]): Point distant
            
        Returns:
            float: Distance
        """
        return self._segment.distance(point)
    
    def intersection(self, other) -> tuple[float, float] | None:
        """
        Renvoie le point d'intersection de deux segments
        
        Args:
            other: Segment à intersecter (SegmentEntity ou Segment)
            
        Returns:
            tuple[float, float] | None: Coordonnées du point ou None si pas d'intersection
        """
        if isinstance(other, SegmentEntity):
            return self._segment.intersection(other._segment)
        return self._segment.intersection(other)
    
    def angle_with(self, other) -> float:
        """
        Renvoie l'angle entre deux segments (en radians)
        
        Args:
            other: Segment à comparer (SegmentEntity ou Segment)
            
        Returns:
            float: Angle en radians
        """
        if isinstance(other, SegmentEntity):
            return self._segment.angle_with(other._segment)
        return self._segment.angle_with(other)
    
    def translate(self, dx: float, dy: float):
        """
        Translate le segment
        
        Args:
            dx (float): Déplacement en x
            dy (float): Déplacement en y
        """
        self._segment.translate(dx, dy)
    
    # ======================================== MOUVEMENTS ========================================
    def move_up(self, dy: float = 1, min: float = None):
        """
        Déplace le segment vers le haut
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale y
        """
        self._segment.translate(0, -dy)
        if min is not None:
            y1, y2 = self._segment.start[1], self._segment.end[1]
            center_y = (y1 + y2) / 2
            if center_y < min:
                self._segment.translate(0, min - center_y)
    
    def move_down(self, dy: float = 1, max: float = None):
        """
        Déplace le segment vers le bas
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale y
        """
        self._segment.translate(0, dy)
        if max is not None:
            y1, y2 = self._segment.start[1], self._segment.end[1]
            center_y = (y1 + y2) / 2
            if center_y > max:
                self._segment.translate(0, max - center_y)
    
    def move_left(self, dx: float = 1, min: float = None):
        """
        Déplace le segment vers la gauche
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale x
        """
        self._segment.translate(-dx, 0)
        if min is not None:
            x1, x2 = self._segment.start[0], self._segment.end[0]
            center_x = (x1 + x2) / 2
            if center_x < min:
                self._segment.translate(min - center_x, 0)
    
    def move_right(self, dx: float = 1, max: float = None):
        """
        Déplace le segment vers la droite
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale x
        """
        self._segment.translate(dx, 0)
        if max is not None:
            x1, x2 = self._segment.start[0], self._segment.end[0]
            center_x = (x1 + x2) / 2
            if center_x > max:
                self._segment.translate(max - center_x, 0)
    
    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """
        Vérifie la collision avec un point
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si collision
        """
        return self._segment.collidepoint(point)
    
    def collidesegment(self, segment) -> bool:
        """
        Vérifie la collision avec un segment
        
        Args:
            segment (context.geometry.Segment): Segment à tester
            
        Returns:
            bool: True si collision
        """
        return self._segment.collidesegment(segment)
    
    def collideline(self, line) -> bool:
        """
        Vérifie la collision avec une droite
        
        Args:
            line (context.geometry.Line): Droite à tester
            
        Returns:
            bool: True si collision
        """
        return line.collidesegment(self._segment)

    def collidecircle(self, circle) -> bool:
        """
        Vérifie la collision avec un cercle
        
        Args:
            circle (context.geometry.Circle): Cercle à tester
            
        Returns:
            bool: True si collision
        """
        return self._segment.collidecircle(circle)
    
    def colliderect(self, rect) -> bool:
        """
        Vérifie la collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): Rectangle à tester
            
        Returns:
            bool: True si collision
        """
        return self._segment.colliderect(rect)
    
    def collidepolygon(self, polygon) -> bool:
        """
        Vérifie la collision avec un polygone
        
        Args:
            polygon (context.geometry.Polygon): Polygone à tester
            
        Returns:
            bool: True si collision
        """
        return polygon._collidesegment(self._segment)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass
    
    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """
        Affiche le segment sur la surface
        
        Args:
            surface (pygame.Surface): Surface de dessin
        """
        start_pos = (int(self._segment.start[0]), int(self._segment.start[1]))
        end_pos = (int(self._segment.end[0]), int(self._segment.end[1]))
        
        if self._dashed:
            self._draw_dashed(surface, start_pos, end_pos)
        elif self._width == 1:
            pygame.draw.aaline(surface, self._color, start_pos, end_pos)
        else:
            pygame.draw.line(surface, self._color, start_pos, end_pos, self._width)
    
    def _draw_dashed(self, surface: pygame.Surface, start: tuple[int, int], end: tuple[int, int]):
        """
        Dessine un segment en pointillés
        
        Args:
            surface (pygame.Surface): Surface de dessin
            start (tuple[int, int]): Point de départ
            end (tuple[int, int]): Point d'arrivée
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