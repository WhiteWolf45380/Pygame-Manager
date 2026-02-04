# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
from math import sqrt

# ======================================== OBJET ========================================
class CircleEntity(Entity):
    """
    Entity avec un cercle géométrique et propriétés d'affichage
    
    Attributes:
        _circle (context.geometry.Circle): Objet géométrique cercle
        _filling (bool): Active le remplissage
        _color (tuple[int, int, int]): Couleur de remplissage RGB
        _border (bool): Active la bordure
        _border_color (tuple[int, int, int]): Couleur de la bordure RGB
        _border_width (int): Épaisseur de la bordure
        _border_around (bool): Bordure autour (True) ou intérieure (False)
    """
    def __init__(
            self,
            center: tuple[float, float],
            radius: Real, zorder: int = -1,
            panel: str | None = None
            ):
        """
        Initialise le cercle
        
        Args:
            center (tuple[float, float]): Coordonnées du centre du cercle
            radius (float): Rayon du cercle
            zorder (int): Ordre d'affichage (défaut: -1)
            panel (str | None): Nom du panel (défaut: None)
        """
        # Vérifications
        center = context.geometry._to_point(center, copy=False)
        if not isinstance(radius, Real): _raise_error(self, '__init__', 'Invalid radius argument')

        # Initialisation d'Entity
        super().__init__(zorder=zorder, panel=panel)
        
        # Objet géométrique
        self._circle = context.geometry.Circle(center, radius)

        # Paramètres d'affichage
        self._filling = True
        self._color = (255, 255, 255)
        
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False
    
    # ======================================== PROXY GEOMETRIQUE ========================================
    @property
    def center(self) -> tuple[float, float]:
        """Renvoie les coordonnées du centre"""
        return self._circle.center
    
    @center.setter
    def center(self, value: tuple[float, float]):
        """
        Fixe les coordonnées du centre
        
        Args:
            value (tuple[float, float]): Nouvelles coordonnées (x, y)
        """
        self._circle.center = value
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self._circle.centerx
    
    @centerx.setter
    def centerx(self, value: float):
        """
        Fixe la coordonnée x du centre
        
        Args:
            value (float): Nouvelle coordonnée x
        """
        self._circle.centerx = value
    
    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self._circle.centery
    
    @centery.setter
    def centery(self, value: float):
        """
        Fixe la coordonnée y du centre
        
        Args:
            value (float): Nouvelle coordonnée y
        """
        self._circle.centery = value
    
    @property
    def radius(self) -> float:
        """Renvoie le rayon du cercle"""
        return self._circle.radius
    
    @radius.setter
    def radius(self, value: float):
        """
        Fixe le rayon du cercle
        
        Args:
            value (float): Nouveau rayon
        """
        self._circle.radius = value
    
    @property
    def diameter(self) -> float:
        """Renvoie le diamètre du cercle"""
        return self._circle.diameter
    
    @diameter.setter
    def diameter(self, value: float):
        """
        Fixe le diamètre du cercle
        
        Args:
            value (float): Nouveau diamètre
        """
        self._circle.diameter = value
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du centre (alias)"""
        return self._circle.centerx
    
    @x.setter
    def x(self, value: float):
        """
        Fixe la coordonnée x du centre
        
        Args:
            value (float): Nouvelle coordonnée x
        """
        self._circle.centerx = value
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du centre (alias)"""
        return self._circle.centery
    
    @y.setter
    def y(self, value: float):
        """
        Fixe la coordonnée y du centre
        
        Args:
            value (float): Nouvelle coordonnée y
        """
        self._circle.centery = value
    
    @property
    def top(self):
        """Renvoie la coordonnée y du haut"""
        return self._circle.centery - self._circle.radius
    
    @top.setter
    def top(self, value: float):
        """
        Fixe la coordonnée y du haut

        Args:
            value (float): Nouvelle coordonnée y
        """
        self._circle.centery = value + self._circle.radius
    
    @property
    def right(self):
        """Renvoie la coordonnée x de la droite"""
        return self._circle.centerx + self._circle.radius
    
    @right.setter
    def right(self, value: float):
        """
        Fixe la coordonnée x de la droite

        Args:
            value (float): Nouvelle coordonnée x
        """
        self._circle.centerx = value - self._circle.radius
    
    @property
    def bottom(self):
        """Renvoie la coordonnée y du bas"""
        return self._circle.centery + self._circle.radius

    @bottom.setter
    def bottom(self, value: float):
        """
        Fixe la coordonnée y du bas

        Args:
            value (float): Nouvelle coordonnée y
        """
        self._circle.centery = value - self._circle.radius
    
    @property
    def left(self):
        """Renvoie la coordonnée x de la gauche"""
        return self._circle.centerx - self._circle.radius
    
    @left.setter
    def left(self, value: float):
        """
        Fixe la coordonnée x de la gauche

        Args:
            value (float): Nouvelle coordonnée x
        """
        self._circle.centerx = value + self._circle.radius

    # ======================================== PARAMETRES D'AFFICHAGE ========================================
    @property
    def filling(self) -> bool:
        """Vérifie si le remplissage est actif"""
        return self._filling
    
    @filling.setter
    def filling(self, value: bool):
        """
        Active ou désactive le remplissage
        
        Args:
            value (bool): État du remplissage
            
        Raises:
            TypeError: Si value n'est pas un bool
        """
        if not isinstance(value, bool):
            _raise_error(self, 'filling', 'Invalid value argument')
        self._filling = value
    
    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur de remplissage"""
        return self._color
    
    @color.setter
    def color(self, color: pygame.Color):
        """
        Fixe la couleur de remplissage
        
        Args:
            color (pygame.Color): Nouvelle couleur
        """
        self._color = _to_color(color)
    
    @property
    def border(self) -> bool:
        """Vérifie si la bordure est active"""
        return self._border
    
    @border.setter
    def border(self, value: bool):
        """
        Active ou désactive la bordure
        
        Args:
            value (bool): État de la bordure
            
        Raises:
            TypeError: Si value n'est pas un bool
        """
        if not isinstance(value, bool):
            _raise_error(self, 'border', 'Invalid value argument')
        self._border = value
    
    @property
    def border_color(self) -> pygame.Color:
        """Renvoie la couleur de la bordure"""
        return self._border_color
    
    @border_color.setter
    def border_color(self, color: pygame.Color):
        """
        Fixe la couleur de la bordure
        
        Args:
            color (pygame.Color): Nouvelle couleur
        """
        self._border_color = _to_color(color)
    
    @property
    def border_width(self) -> int:
        """Renvoie l'épaisseur de la bordure"""
        return self._border_width
    
    @border_width.setter
    def border_width(self, width: int):
        """
        Fixe l'épaisseur de la bordure
        
        Args:
            width (int): Nouvelle épaisseur
            
        Raises:
            ValueError: Si width <= 0
        """
        if not isinstance(width, int) or width <= 0:
            _raise_error(self, 'border_width', 'Invalid width argument')
        self._border_width = width
    
    @property
    def border_around(self) -> bool:
        """Vérifie si la bordure est autour du cercle"""
        return self._border_around
    
    @border_around.setter
    def border_around(self, value: bool):
        """
        Active ou désactive la bordure extérieure
        
        Args:
            value (bool): État de la bordure extérieure
            
        Raises:
            TypeError: Si value n'est pas un bool
        """
        if not isinstance(value, bool):
            _raise_error(self, 'border_around', 'Invalid value argument')
        self._border_around = value
    
    # ======================================== MOUVEMENTS ========================================
    def move_up(self, dy: float = 1):
        """
        Déplace le cercle vers le haut
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
        """
        self._circle.centery -= dy
    
    def move_down(self, dy: float = 1):
        """
        Déplace le cercle vers le bas
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
        """
        self._circle.centery += dy
    
    def move_left(self, dx: float = 1):
        """
        Déplace le cercle vers la gauche
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
        """
        self._circle.centerx -= dx
    
    def move_right(self, dx: float = 1):
        """
        Déplace le cercle vers la droite
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
        """
        self._circle.centerx += dx
    
    def move_up_left(self, n: float = 1):
        """
        Déplace le cercle en diagonale haut-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._circle.centerx -= d
        self._circle.centery -= d
    
    def move_up_right(self, n: float = 1):
        """
        Déplace le cercle en diagonale haut-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._circle.centerx += d
        self._circle.centery -= d
    
    def move_down_left(self, n: float = 1):
        """
        Déplace le cercle en diagonale bas-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._circle.centerx -= d
        self._circle.centery += d
    
    def move_down_right(self, n: float = 1):
        """
        Déplace le cercle en diagonale bas-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._circle.centerx += d
        self._circle.centery += d
    
    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """
        Vérifie la collision avec un point
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si collision
        """
        return self._circle.collidepoint(point)
    
    def collidesegment(self, segment) -> bool:
        """
        Vérifie la collision avec un segment
        
        Args:
            segment (context.geometry.Segment): Segment à tester
            
        Returns:
            bool: True si collision
        """
        return self._circle.collidesegment(segment)
    
    def collideline(self, line) -> bool:
        """
        Vérifie la collision avec une droite
        
        Args:
            line (context.geometry.Line): Droite à tester
            
        Returns:
            bool: True si collision
        """
        return self._circle.collideline(line)
    
    def collidecircle(self, circle) -> bool:
        """
        Vérifie la collision avec un cercle
        
        Args:
            circle (context.geometry.Circle): Cercle à tester
            
        Returns:
            bool: True si collision
        """
        return self._circle.collidecircle(circle)
    
    def colliderect(self, rect) -> bool:
        """
        Vérifie la collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): Rectangle à tester
            
        Returns:
            bool: True si collision
        """
        return self._circle.colliderect(rect)
    
    def collidepolygon(self, polygon) -> bool:
        """
        Vérifie la collision avec un polygone
        
        Args:
            polygon (context.geometry.Polygon): Polygone à tester
            
        Returns:
            bool: True si collision
        """
        return polygon._collidecircle(self._circle)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass
    
    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """
        Affiche le cercle sur la surface
        
        Args:
            surface (pygame.Surface): Surface de dessin
        """
        center_pos = (int(self._circle.centerx), int(self._circle.centery))
        radius = int(self._circle.radius)
        
        if self._filling:
            pygame.draw.circle(surface, self._color, center_pos, radius)
        
        if self._border:
            if self._border_around:
                pygame.draw.circle(surface, self._border_color, center_pos, radius + self._border_width, self._border_width)
            else:
                pygame.draw.circle(surface, self._border_color, center_pos, radius, self._border_width)