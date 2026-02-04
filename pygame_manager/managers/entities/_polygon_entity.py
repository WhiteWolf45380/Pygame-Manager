# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
from math import sqrt

# ======================================== OBJET ========================================
class PolygonEntity(Entity):
    """
    Entity avec un polygone géométrique et propriétés d'affichage
    
    Attributes:
        _polygon (context.geometry.Polygon): Objet géométrique polygone
        _filling (bool): Active le remplissage
        _color (tuple[int, int, int]): Couleur de remplissage RGB
        _border (bool): Active la bordure
        _border_color (tuple[int, int, int]): Couleur de la bordure RGB
        _border_width (int): Épaisseur de la bordure
        _border_around (bool): Bordure autour (True) ou intérieure (False)
    """
    def __init__(
            self,
            *points: tuple[Real, Real],
            zorder: int = -1,
            panel: str | None = None
            ):
        """
        Initialise le polygone
        
        Args:
            *points (tuple[float, float]): Liste de points (x, y) du polygone
            zorder (int): Ordre d'affichage (défaut: -1)
            panel (str | None): Nom du panel (défaut: None)
        """
        # Vérifications
        points = list(map(context.geometry._to_point, points))

        # Initialisation d'Entity
        super().__init__(zorder=zorder, panel=panel)
        
        # Objet géométrique
        self._polygon = context.geometry.Polygon(*points)

        # Paramètres d'affichage
        self._filling = True
        self._color = (255, 255, 255)
        
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False
    
    # ======================================== PROXY GEOMETRIQUE ========================================
    @property
    def vertices(self) -> list[tuple[float, float]]:
        """Renvoie la liste des sommets du polygone"""
        return self._polygon.vertices
    
    @property
    def n(self) -> int:
        """Renvoie le nombre de sommets"""
        return self._polygon.n
    
    def __len__(self) -> int:
        """Renvoie le nombre de sommets"""
        return len(self._polygon)
    
    def __getitem__(self, i: int) -> tuple[float, float]:
        """
        Renvoie le sommet à l'index i
        
        Args:
            i (int): Index du sommet
            
        Returns:
            tuple[float, float]: Coordonnées du sommet
        """
        return self._polygon[i]
    
    def __setitem__(self, i: int, point: tuple[float, float]):
        """
        Fixe le sommet à l'index i
        
        Args:
            i (int): Index du sommet
            point (tuple[float, float]): Nouvelles coordonnées
        """
        self._polygon[i] = point
    
    @property
    def center(self) -> tuple[float, float]:
        """Renvoie les coordonnées du centre (centroïde)"""
        return self._polygon.center
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self._polygon.center[0]
    
    @x.setter
    def x(self, value: float):
        """
        Déplace le polygone pour que son centre ait cette coordonnée x
        
        Args:
            value (float): Nouvelle coordonnée x du centre
        """
        cx, cy = self._polygon.center
        dx = value - cx
        self._polygon.translate(dx, 0)
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self._polygon.center[1]
    
    @y.setter
    def y(self, value: float):
        """
        Déplace le polygone pour que son centre ait cette coordonnée y
        
        Args:
            value (float): Nouvelle coordonnée y du centre
        """
        cx, cy = self._polygon.center
        dy = value - cy
        self._polygon.translate(0, dy)
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self._polygon.center[0]
    
    @centerx.setter
    def centerx(self, value: float):
        """
        Déplace le polygone pour que son centre ait cette coordonnée x
        
        Args:
            value (float): Nouvelle coordonnée x du centre
        """
        cx, cy = self._polygon.center
        dx = value - cx
        self._polygon.translate(dx, 0)
    
    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self._polygon.center[1]
    
    @centery.setter
    def centery(self, value: float):
        """
        Déplace le polygone pour que son centre ait cette coordonnée y
        
        Args:
            value (float): Nouvelle coordonnée y du centre
        """
        cx, cy = self._polygon.center
        dy = value - cy
        self._polygon.translate(0, dy)
    
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
        """Vérifie si la bordure est autour du polygone"""
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
        Déplace le polygone vers le haut
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
        """
        self._polygon.translate(0, -dy)
    
    def move_down(self, dy: float = 1):
        """
        Déplace le polygone vers le bas
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
        """
        self._polygon.translate(0, dy)
    
    def move_left(self, dx: float = 1):
        """
        Déplace le polygone vers la gauche
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
        """
        self._polygon.translate(-dx, 0)
    
    def move_right(self, dx: float = 1):
        """
        Déplace le polygone vers la droite
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
        """
        self._polygon.translate(dx, 0)
    
    def move_up_left(self, n: float = 1):
        """
        Déplace le polygone en diagonale haut-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._polygon.translate(-d, -d)
    
    def move_up_right(self, n: float = 1):
        """
        Déplace le polygone en diagonale haut-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._polygon.translate(d, -d)
    
    def move_down_left(self, n: float = 1):
        """
        Déplace le polygone en diagonale bas-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._polygon.translate(-d, d)
    
    def move_down_right(self, n: float = 1):
        """
        Déplace le polygone en diagonale bas-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
        """
        d = n / sqrt(2)
        self._polygon.translate(d, d)
    
    def rotate(self, angle: float, center: tuple[float, float] = None, degrees: bool = False):
        """
        Tourne le polygone
        
        Args:
            angle (float): Angle de rotation
            center (tuple[float, float]): Centre de rotation (défaut: centroïde)
            degrees (bool): True si angle en degrés, False si radians (défaut: False)
        """
        self._polygon.rotate(angle, center, degrees)
    
    def scale(self, ratio: float, center: tuple[float, float] = None):
        """
        Redimensionne le polygone
        
        Args:
            ratio (float): Ratio de redimensionnement
            center (tuple[float, float]): Centre de redimensionnement (défaut: centroïde)
        """
        self._polygon.scale(ratio, center)
    
    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """
        Vérifie la collision avec un point
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.collidepoint(point)
    
    def collidesegment(self, segment) -> bool:
        """
        Vérifie la collision avec un segment
        
        Args:
            segment (context.geometry.Segment): Segment à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.collidesegment(segment)
    
    def collideline(self, line) -> bool:
        """
        Vérifie la collision avec une droite
        
        Args:
            line (context.geometry.Line): Droite à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.collideline(line)
    
    def collidecircle(self, circle) -> bool:
        """
        Vérifie la collision avec un cercle
        
        Args:
            circle (context.geometry.Circle): Cercle à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.collidecircle(circle)
    
    def colliderect(self, rect) -> bool:
        """
        Vérifie la collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): Rectangle à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.colliderect(rect)
    
    def collidepolygon(self, polygon) -> bool:
        """
        Vérifie la collision avec un polygone
        
        Args:
            polygon (context.geometry.Polygon): Polygone à tester
            
        Returns:
            bool: True si collision
        """
        return self._polygon.collidepolygon(polygon)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass
    
    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """
        Affiche le polygone sur la surface
        
        Args:
            surface (pygame.Surface): Surface de dessin
        """
        points = [(int(x), int(y)) for x, y in self._polygon.vertices]
        
        if self._filling:
            pygame.draw.polygon(surface, self._color, points)
        
        if self._border:
            if self._border_around:
                pygame.draw.polygon(surface, self._border_color, points, self._border_width * 2)
                if self._filling:
                    pygame.draw.polygon(surface, self._color, points)
                else:
                    pygame.draw.polygon(surface, self._border_color, points, self._border_width)
            else:
                pygame.draw.polygon(surface, self._border_color, points, self._border_width)