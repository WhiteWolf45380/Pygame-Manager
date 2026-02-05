# ======================================== IMPORTS ========================================
from ._core import *
from ._entity import Entity
from math import sqrt

# ======================================== ENTITE ========================================
class SpriteEntity(Entity):
    """
    Entity avec une image pygame et gestion de la rotation
    
    Attributes:
        _image (pygame.Surface | None): Image actuelle du sprite
        _original_image (pygame.Surface | None): Image originale pour les rotations
        _rect (pygame.Rect): Rectangle de collision
        _angle (float): Angle de rotation actuel en degrés
        _x (float): Coordonnée x du coin haut gauche
        _y (float): Coordonnée y du coin haut gauche
        _alpha (int): Opacité (0-255)
    """
    
    def __init__(
            self,
            image: pygame.Surface | None = None,
            x: Real = 0,
            y: Real = 0,
            zorder: int = -1,
            panel: str | None = None,
            ):
        """
        Initialise le sprite
        
        Args:
            image (pygame.Surface) : image du sprite
            x (Real) : coordonnée x du sprite
            y (Real) : coordonnée y du sprite
            zorder (int): Ordre d'affichage (défaut: -1)
            panel (str | None): Nom du panel (défaut: None)
        """
        # Vérifications
        if image is not None and not isinstance(image, pygame.Surface): _raise_error(self, '__init__', 'Invalid image argument')
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')

        # Initialisation d'Entity
        super().__init__(zorder=zorder, panel=panel)

        # Image
        self._image: pygame.Surface | None = None
        self._original_image: pygame.Surface | None = None

        # Position
        self._rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self._x: float = float(x)
        self._y: float = float(y)

        # Paramètres d'affichage
        self._angle: float = 0.0
        self._alpha: int = 255

        # Chargement
        if image is not None:
            self.image = image

    # ======================================== IMAGE ========================================
    @property
    def image(self) -> pygame.Surface | None:
        """Renvoie l'image du sprite"""
        return self._image

    @image.setter
    def image(self, surface: pygame.Surface):
        """
        Fixe l'image du sprite
        
        Args:
            surface (pygame.Surface): Nouvelle image
            
        Raises:
            TypeError: Si surface n'est pas une pygame.Surface
        """
        if not isinstance(surface, pygame.Surface):
            _raise_error(self, 'image', 'image must be a pygame.Surface')

        self._image = surface
        self._original_image = surface.copy()
        self._image.set_alpha(self._alpha)
        self._rect = surface.get_rect()

    # ======================================== HITBOX ========================================
    @property
    def rect(self) -> pygame.Rect:
        """Renvoie une copie de la hitbox du sprite"""
        return self._rect.copy()

    @property
    def width(self) -> float:
        """Renvoie la largeur de la hitbox"""
        return self._rect.width
    
    @property
    def height(self) -> float:
        """Renvoie la hauteur de la hitbox"""
        return self._rect.height

    # ======================================== ROTATION ========================================
    def rotate(self, angle: float):
        """
        Effectue une rotation dans le sens trigonométrique
        
        Args:
            angle (float): Angle de rotation en degrés
        """
        if self._original_image is None:
            return

        self._angle = (self._angle + angle) % 360
        center = self._rect.center
        self._image = pygame.transform.rotate(self._original_image, self._angle)
        self._image.set_alpha(self._alpha)
        self._rect = self._image.get_rect()
        self.center = center

    # ======================================== POSITION ET ANCRAGES ========================================
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x du coin haut gauche"""
        return self._x

    @x.setter
    def x(self, v: Real):
        """
        Fixe la coordonnée x du coin haut gauche
        
        Args:
            v (Real): Nouvelle coordonnée x
        """
        self._x = float(v)

    @property
    def y(self) -> float:
        """Renvoie la coordonnée y du coin haut gauche"""
        return self._y

    @y.setter
    def y(self, v: Real):
        """
        Fixe la coordonnée y du coin haut gauche
        
        Args:
            v (Real): Nouvelle coordonnée y
        """
        self._y = float(v)

    @property
    def center(self) -> tuple[float, float]:
        """Renvoie les coordonnées du centre"""
        return (self._x + self._rect.width / 2, self._y + self._rect.height / 2)

    @center.setter
    def center(self, v: tuple[Real, Real]):
        """
        Fixe les coordonnées du centre
        
        Args:
            v (tuple[Real, Real]): Nouvelles coordonnées (x, y)
        """
        self._x, self._y = float(v[0]) - self._rect.width / 2, float(v[1]) - self._rect.height / 2

    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du centre"""
        return self._x + self._rect.width / 2

    @centerx.setter
    def centerx(self, v: Real):
        """
        Fixe la coordonnée x du centre
        
        Args:
            v (Real): Nouvelle coordonnée x du centre
        """
        self._x = float(v) - self._rect.width / 2

    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self._y + self._rect.height / 2

    @centery.setter
    def centery(self, v: Real):
        """
        Fixe la coordonnée y du centre
        
        Args:
            v (Real): Nouvelle coordonnée y du centre
        """
        self._y = float(v) - self._rect.height / 2

    @property
    def topleft(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin haut gauche"""
        return self._x, self._y

    @topleft.setter
    def topleft(self, v: tuple[Real, Real]):
        """
        Fixe les coordonnées du coin haut gauche
        
        Args:
            v (tuple[Real, Real]): Nouvelles coordonnées (x, y)
        """
        self._x, self._y = float(v[0]), float(v[1])

    @property
    def top(self) -> float:
        """Renvoie la coordonnée y du haut"""
        return self._y

    @top.setter
    def top(self, v: Real):
        """
        Fixe la coordonnée y du haut
        
        Args:
            v (Real): Nouvelle coordonnée y
        """
        self._y = float(v)

    @property
    def topright(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin haut droit"""
        return self._x + self._rect.width, self._y

    @topright.setter
    def topright(self, v: tuple[Real, Real]):
        """
        Fixe les coordonnées du coin haut droit
        
        Args:
            v (tuple[Real, Real]): Nouvelles coordonnées (x, y)
        """
        self._x, self._y = float(v[0]) - self._rect.width, float(v[1])

    @property
    def right(self) -> float:
        """Renvoie la coordonnée x de la droite"""
        return self._x + self._rect.width

    @right.setter
    def right(self, v: Real):
        """
        Fixe la coordonnée x de la droite
        
        Args:
            v (Real): Nouvelle coordonnée x
        """
        self._x = float(v) - self._rect.width

    @property
    def bottomright(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin bas droit"""
        return self._x + self._rect.width, self._y + self._rect.height

    @bottomright.setter
    def bottomright(self, v: tuple[Real, Real]):
        """
        Fixe les coordonnées du coin bas droit
        
        Args:
            v (tuple[Real, Real]): Nouvelles coordonnées (x, y)
        """
        self._x, self._y = float(v[0]) - self._rect.width, float(v[1]) - self._rect.height

    @property
    def bottom(self) -> float:
        """Renvoie la coordonnée y du bas"""
        return self._y + self._rect.height

    @bottom.setter
    def bottom(self, v: Real):
        """
        Fixe la coordonnée y du bas
        
        Args:
            v (Real): Nouvelle coordonnée y
        """
        self._y = float(v) - self._rect.height

    @property
    def bottomleft(self) -> tuple[float, float]:
        """Renvoie les coordonnées du coin bas gauche"""
        return self._x, self._y + self._rect.height

    @bottomleft.setter
    def bottomleft(self, v: tuple[Real, Real]):
        """
        Fixe les coordonnées du coin bas gauche
        
        Args:
            v (tuple[Real, Real]): Nouvelles coordonnées (x, y)
        """
        self._x, self._y = float(v[0]), float(v[1]) - self._rect.height

    @property
    def left(self) -> float:
        """Renvoie la coordonnée x de la gauche"""
        return self._x

    @left.setter
    def left(self, v: Real):
        """
        Fixe la coordonnée x de la gauche
        
        Args:
            v (Real): Nouvelle coordonnée x
        """
        self._x = float(v)

    # ======================================== OPACITE ========================================
    @property
    def alpha(self) -> int:
        """Renvoie l'opacité (0-255)"""
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        """
        Fixe l'opacité
        
        Args:
            value (int): Nouvelle opacité (0-255)
        """
        self._alpha = max(0, min(255, int(value)))
        if self._image:
            self._image.set_alpha(self._alpha)

    # ======================================== MOUVEMENTS ========================================
    def move_up(self, dy: float = 1, min: float = None):
        """
        Déplace le sprite vers le haut
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale y
        """
        self._y -= dy
        if min is not None and self._y < min:
            self._y = min

    def move_down(self, dy: float = 1, max: float = None):
        """
        Déplace le sprite vers le bas
        
        Args:
            dy (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale y
        """
        self._y += dy
        if max is not None and self._y > max:
            self._y = max

    def move_left(self, dx: float = 1, min: float = None):
        """
        Déplace le sprite vers la gauche
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            min (float): Position minimale x
        """
        self._x -= dx
        if min is not None and self._x < min:
            self._x = min

    def move_right(self, dx: float = 1, max: float = None):
        """
        Déplace le sprite vers la droite
        
        Args:
            dx (float): Distance de déplacement (défaut: 1)
            max (float): Position maximale x
        """
        self._x += dx
        if max is not None and self._x > max:
            self._x = max

    def move_up_left(self, n: float = 1, xmin: float = None, ymin: float = None):
        """
        Déplace le sprite en diagonale haut-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
            xmin (float): Position minimale x
            ymin (float): Position minimale y
        """
        d = n / sqrt(2)
        self._x -= d
        self._y -= d
        if xmin is not None and self._x < xmin:
            self._x = xmin
        if ymin is not None and self._y < ymin:
            self._y = ymin

    def move_up_right(self, n: float = 1, xmax: float = None, ymin: float = None):
        """
        Déplace le sprite en diagonale haut-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
            xmax (float): Position maximale x
            ymin (float): Position minimale y
        """
        d = n / sqrt(2)
        self._x += d
        self._y -= d
        if xmax is not None and self._x > xmax:
            self._x = xmax
        if ymin is not None and self._y < ymin:
            self._y = ymin

    def move_down_left(self, n: float = 1, xmin: float = None, ymax: float = None):
        """
        Déplace le sprite en diagonale bas-gauche
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
            xmin (float): Position minimale x
            ymax (float): Position maximale y
        """
        d = n / sqrt(2)
        self._x -= d
        self._y += d
        if xmin is not None and self._x < xmin:
            self._x = xmin
        if ymax is not None and self._y > ymax:
            self._y = ymax

    def move_down_right(self, n: float = 1, xmax: float = None, ymax: float = None):
        """
        Déplace le sprite en diagonale bas-droite
        
        Args:
            n (float): Distance de déplacement (défaut: 1)
            xmax (float): Position maximale x
            ymax (float): Position maximale y
        """
        d = n / sqrt(2)
        self._x += d
        self._y += d
        if xmax is not None and self._x > xmax:
            self._x = xmax
        if ymax is not None and self._y > ymax:
            self._y = ymax

    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]) -> bool:
        """
        Vérifie la collision avec un point
        
        Args:
            point (tuple[float, float]): Point à tester
            
        Returns:
            bool: True si collision
        """
        return self._rect.collidepoint(point)
    
    def collidesegment(self, segment) -> bool:
        """
        Vérifie la collision avec un segment
        
        Args:
            segment (context.geometry.Segment): Segment à tester
            
        Returns:
            bool: True si collision
        """
        return segment.colliderect(self._rect)
    
    def collideline(self, line) -> bool:
        """
        Vérifie la collision avec une droite
        
        Args:
            line (context.geometry.Line): Droite à tester
            
        Returns:
            bool: True si collision
        """
        return line.colliderect(self._rect)
    
    def collidecircle(self, circle) -> bool:
        """
        Vérifie la collision avec un cercle
        
        Args:
            circle (context.geometry.Circle): Cercle à tester
            
        Returns:
            bool: True si collision
        """
        return circle.colliderect(self._rect)
    
    def colliderect(self, rect) -> bool:
        """
        Vérifie la collision avec un rectangle
        
        Args:
            rect (context.geometry.Rect): Rectangle à tester
            
        Returns:
            bool: True si collision
        """
        return rect.colliderect(self._rect)
    
    def collidepolygon(self, polygon) -> bool:
        """
        Vérifie la collision avec un polygone
        
        Args:
            polygon (context.geometry.Polygon): Polygone à tester
            
        Returns:
            bool: True si collision
        """
        return polygon.colliderect(self._rect)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """
        Affiche le sprite sur la surface
        
        Args:
            surface (pygame.Surface): Surface de dessin
        """
        if self._image is None:
            return
        self._rect.topleft = self._x, self._y
        surface.blit(self._image, self._rect)