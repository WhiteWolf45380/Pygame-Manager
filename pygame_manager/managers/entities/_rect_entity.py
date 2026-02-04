# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
from math import sqrt

# ======================================== OBJET ========================================
class RectEntity(Entity):
    """
    Entity avec un rectangle géométrique et propriétés d'affichage
    
    Attributes:
        _rect (context.geometry.Rect): Objet géométrique rectangle
        _filling (bool): Active le remplissage
        _color (tuple[int, int, int]): Couleur de remplissage RGB
        _border (bool): Active la bordure
        _border_color (tuple[int, int, int]): Couleur de la bordure RGB
        _border_width (int): Épaisseur de la bordure
        _border_around (bool): Bordure autour (True) ou intérieure (False)
        _border_topleft_radius (int): Rayon d'arrondi coin haut gauche
        _border_topright_radius (int): Rayon d'arrondi coin haut droit
        _border_bottomleft_radius (int): Rayon d'arrondi coin bas gauche
        _border_bottomright_radius (int): Rayon d'arrondi coin bas droit
    """
    
    def __init__(self, x: float, y: float, width: float, height: float, zorder: int = -1, panel: str | None = None):
        """
        Initialise le rectangle
        
        Args:
            x (float): Coordonnée x du coin haut gauche
            y (float): Coordonnée y du coin haut gauche
            width (float): Largeur
            height (float): Hauteur
            zorder (int): Ordre d'affichage (défaut: -1)
            panel (str | None): Nom du panel (défaut: None)
        """
        super().__init__(zorder=zorder, panel=panel)
        
        self._rect = context.geometry.Rect(x, y, width, height)
        self._filling = True
        self._color = (255, 255, 255)
        self._border = False
        self._border_color = (0, 0, 0)
        self._border_width = 1
        self._border_around = False
        self._border_topleft_radius = -1
        self._border_topright_radius = -1
        self._border_bottomleft_radius = -1
        self._border_bottomright_radius = -1
    
    # ======================================== PROXY GEOMETRIQUE ========================================
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du coin haut gauche"""
        return self._rect.x
    
    @x.setter
    def x(self, value: float):
        """Fixe la coordonnée x du coin haut gauche"""
        self._rect.x = value
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du coin haut gauche"""
        return self._rect.y
    
    @y.setter
    def y(self, value: float):
        """Fixe la coordonnée y du coin haut gauche"""
        self._rect.y = value
    
    @property
    def width(self) -> float:
        """Renvoie la largeur"""
        return self._rect.width
    
    @width.setter
    def width(self, value: float):
        """Fixe la largeur"""
        self._rect.width = value
    
    @property
    def height(self) -> float:
        """Renvoie la hauteur"""
        return self._rect.height
    
    @height.setter
    def height(self, value: float):
        """Fixe la hauteur"""
        self._rect.height = value
    
    @property
    def topleft(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin haut gauche"""
        return self._rect.topleft
    
    @topleft.setter
    def topleft(self, value: tuple[float, float]):
        """Fixe les coordonnées du coin haut gauche"""
        self._rect.topleft = value
    
    @property
    def top(self) -> float:
        """Renvoie la coordonnée y du haut"""
        return self._rect.top
    
    @top.setter
    def top(self, value: float):
        """Fixe la coordonnée y du haut"""
        self._rect.top = value
    
    @property
    def topright(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin haut droit"""
        return self._rect.topright
    
    @topright.setter
    def topright(self, value: tuple[float, float]):
        """Fixe les coordonnées du coin haut droit"""
        self._rect.topright = value
    
    @property
    def right(self) -> float:
        """Renvoie la coordonnée x de la droite"""
        return self._rect.right
    
    @right.setter
    def right(self, value: float):
        """Fixe la coordonnée x de la droite"""
        self._rect.right = value
    
    @property
    def bottomright(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin bas droit"""
        return self._rect.bottomright
    
    @bottomright.setter
    def bottomright(self, value: tuple[float, float]):
        """Fixe les coordonnées du coin bas droit"""
        self._rect.bottomright = value
    
    @property
    def bottom(self) -> float:
        """Renvoie la coordonnée y du bas"""
        return self._rect.bottom
    
    @bottom.setter
    def bottom(self, value: float):
        """Fixe la coordonnée y du bas"""
        self._rect.bottom = value
    
    @property
    def bottomleft(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin bas gauche"""
        return self._rect.bottomleft
    
    @bottomleft.setter
    def bottomleft(self, value: tuple[float, float]):
        """Fixe les coordonnées du coin bas gauche"""
        self._rect.bottomleft = value
    
    @property
    def left(self) -> float:
        """Renvoie la coordonnée x de la gauche"""
        return self._rect.left
    
    @left.setter
    def left(self, value: float):
        """Fixe la coordonnée x de la gauche"""
        self._rect.left = value
    
    @property
    def center(self) -> tuple[float, float]:
        """Renvoie les coordonnées du centre"""
        return self._rect.center
    
    @center.setter
    def center(self, value: tuple[float, float]):
        """Fixe les coordonnées du centre"""
        self._rect.center = value
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self._rect.centerx
    
    @centerx.setter
    def centerx(self, value: float):
        """Fixe la coordonnée x du centre"""
        self._rect.centerx = value
    
    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self._rect.centery
    
    @centery.setter
    def centery(self, value: float):
        """Fixe la coordonnée y du centre"""
        self._rect.centery = value
    
    # ======================================== PARAMETRES D'AFFICHAGE ========================================
    @property
    def filling(self) -> bool:
        """Vérifie si le remplissage est actif"""
        return self._filling
    
    @filling.setter
    def filling(self, value: bool):
        """Active ou désactive le remplissage"""
        if not isinstance(value, bool):
            _raise_error(self, 'filling', 'Invalid value argument')
        self._filling = value
    
    @property
    def color(self) -> pygame.Color:
        """Renvoie la couleur de remplissage"""
        return self._color
    
    @color.setter
    def color(self, color: pygame.Color):
        """Fixe la couleur de remplissage"""
        self._color = _to_color(color)
    
    @property
    def border(self) -> bool:
        """Vérifie si la bordure est active"""
        return self._border
    
    @border.setter
    def border(self, value: bool):
        """Active ou désactive la bordure"""
        if not isinstance(value, bool):
            _raise_error(self, 'border', 'Invalid value argument')
        self._border = value
    
    @property
    def border_color(self) -> pygame.Color:
        """Renvoie la couleur de la bordure"""
        return self._border_color
    
    @border_color.setter
    def border_color(self, color: pygame.Color):
        """Fixe la couleur de la bordure"""
        self._border_color = _to_color(color)
    
    @property
    def border_width(self) -> int:
        """Renvoie l'épaisseur de la bordure"""
        return self._border_width
    
    @border_width.setter
    def border_width(self, width: int):
        """Fixe l'épaisseur de la bordure"""
        if not isinstance(width, int) or width <= 0:
            _raise_error(self, 'border_width', 'Invalid width argument')
        self._border_width = width
    
    @property
    def border_around(self) -> bool:
        """Vérifie si la bordure est autour du rectangle"""
        return self._border_around
    
    @border_around.setter
    def border_around(self, value: bool):
        """Active ou désactive la bordure extérieure"""
        if not isinstance(value, bool):
            _raise_error(self, 'border_around', 'Invalid value argument')
        self._border_around = value
    
    @property
    def border_radius(self) -> int:
        """Renvoie le rayon d'arrondi des coins"""
        return self._rect.border_radius
    
    @border_radius.setter
    def border_radius(self, radius: int):
        """Fixe le rayon d'arrondi des coins"""
        self._rect.border_radius = radius
    
    # ======================================== MOUVEMENTS ========================================
    def move_up(self, dy: float = 1):
        """Déplace le rectangle vers le haut"""
        self._rect.y -= dy
    
    def move_down(self, dy: float = 1):
        """Déplace le rectangle vers le bas"""
        self._rect.y += dy
    
    def move_left(self, dx: float = 1):
        """Déplace le rectangle vers la gauche"""
        self._rect.x -= dx
    
    def move_right(self, dx: float = 1):
        """Déplace le rectangle vers la droite"""
        self._rect.x += dx
    
    def move_up_left(self, n: float = 1):
        """Déplace le rectangle en diagonale haut-gauche"""
        d = n / sqrt(2)
        self._rect.x -= d
        self._rect.y -= d
    
    def move_up_right(self, n: float = 1):
        """Déplace le rectangle en diagonale haut-droite"""
        d = n / sqrt(2)
        self._rect.x += d
        self._rect.y -= d
    
    def move_down_left(self, n: float = 1):
        """Déplace le rectangle en diagonale bas-gauche"""
        d = n / sqrt(2)
        self._rect.x -= d
        self._rect.y += d
    
    def move_down_right(self, n: float = 1):
        """Déplace le rectangle en diagonale bas-droite"""
        d = n / sqrt(2)
        self._rect.x += d
        self._rect.y += d
    
    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """Vérifie la collision avec un point"""
        return self._rect.collidepoint(point)
    
    def collidesegment(self, segment: context.geometry.Segment) -> bool:
        """Vérifie la collision avec un segment"""
        return self._rect.collidesegment(segment)
    
    def collideline(self, line: context.geometry.Line) -> bool:
        """Vérifie la collision avec une droite"""
        return self._rect.collideline(line)
    
    def collidecircle(self, circle: context.geometry.Circle) -> bool:
        """Vérifie la collision avec un cercle"""
        return self._rect.collidecircle(circle)
    
    def colliderect(self, rect: context.geometry.Rect) -> bool:
        """Vérifie la collision avec un rectangle"""
        return self._rect.colliderect(rect)
    
    def collidepolygon(self, polygon: context.geometry.Polygon) -> bool:
        """Vérifie la collision avec un polygone"""
        return polygon._colliderect(self._rect)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass
    
    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """Affiche le rectangle sur la surface"""
        rect = self._rect.rect
        
        border_radius = self._rect.border_radius
        border_topleft = self._border_topleft_radius if self._border_topleft_radius >= 0 else border_radius
        border_topright = self._border_topright_radius if self._border_topright_radius >= 0 else border_radius
        border_bottomleft = self._border_bottomleft_radius if self._border_bottomleft_radius >= 0 else border_radius
        border_bottomright = self._border_bottomright_radius if self._border_bottomright_radius >= 0 else border_radius
        
        if self._filling:
            pygame.draw.rect(surface, self._color, rect, 0, border_radius, border_topleft, border_topright, border_bottomleft, border_bottomright)
        
        if self._border:
            if self._border_around:
                rect_around = pygame.Rect(rect.left - self._border_width, rect.top - self._border_width, rect.width + 2 * self._border_width,  rect.height + 2 * self._border_width)
                pygame.draw.rect(surface, self._border_color, rect_around, self._border_width, border_radius, border_topleft, border_topright, border_bottomleft, border_bottomright)
            else:
                pygame.draw.rect(surface, self._border_color, rect, self._border_width, border_radius, border_topleft, border_topright, border_bottomleft, border_bottomright)