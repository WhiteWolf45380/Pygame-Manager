# ======================================== IMPORTS ========================================
from _core import *
from ._sprite import Sprite
from math import sqrt

# ======================================== OBJET ========================================
class SpriteEntity(Sprite):
    def __init__(self, zorder: int = -1, panel: str | None = None):
        super().__init__(zorder=zorder, panel=panel)

        self._image: pygame.Surface | None = None
        self._rect: pygame.Rect | None = None
        self._alpha: int = 255
        self._angle: float = 0.0

    # ======================================== IMAGE ========================================
    @property
    def image(self) -> pygame.Surface | None:
        return self._image

    @image.setter
    def image(self, surface: pygame.Surface):
        if not isinstance(surface, pygame.Surface):
            _raise_error(self, 'image', 'image must be a pygame.Surface')

        self._image = surface
        self._image.set_alpha(self._alpha)

        if self._rect is None:
            self._rect = surface.get_rect()

    # ======================================== RECT ========================================
    @property
    def rect(self) -> pygame.Rect:
        if self._rect is None:
            self._rect = pygame.Rect(0, 0, 0, 0)
        return self._rect

    @rect.setter
    def rect(self, rect: pygame.Rect):
        if not isinstance(rect, pygame.Rect):
            _raise_error(self, 'rect', 'rect must be a pygame.Rect')
        self._rect = rect

    # ======================================== ROTATION ========================================
    def rotate(self, angle: float):
        if self._image is None:
            return

        self._angle = (self._angle + angle) % 360
        center = self.rect.center
        self._image = pygame.transform.rotate(self._image, angle)
        self._rect = self._image.get_rect(center=center)

    # ======================================== POSITION ET ANCRAGES ========================================
    @property
    def x(self): return self.rect.x
    @x.setter
    def x(self, v): self.rect.x = int(v)

    @property
    def y(self): return self.rect.y
    @y.setter
    def y(self, v): self.rect.y = int(v)

    @property
    def center(self): return self.rect.center
    @center.setter
    def center(self, v): self.rect.center = v

    @property
    def centerx(self): return self.rect.centerx
    @centerx.setter
    def centerx(self, v): self.rect.centerx = int(v)

    @property
    def centery(self): return self.rect.centery
    @centery.setter
    def centery(self, v): self.rect.centery = int(v)

    @property
    def topleft(self): return self.rect.topleft
    @topleft.setter
    def topleft(self, v): self.rect.topleft = v

    @property
    def top(self): return self.rect.top
    @top.setter
    def top(self, v): self.rect.top = int(v)

    @property
    def topright(self): return self.rect.topright
    @topright.setter
    def topright(self, v): self.rect.topright = v

    @property
    def right(self): return self.rect.right
    @right.setter
    def right(self, v): self.rect.right = int(v)

    @property
    def bottomright(self): return self.rect.bottomright
    @bottomright.setter
    def bottomright(self, v): self.rect.bottomright = v

    @property
    def bottom(self): return self.rect.bottom
    @bottom.setter
    def bottom(self, v): self.rect.bottom = int(v)

    @property
    def bottomleft(self): return self.rect.bottomleft
    @bottomleft.setter
    def bottomleft(self, v): self.rect.bottomleft = v

    @property
    def left(self): return self.rect.left
    @left.setter
    def left(self, v): self.rect.left = int(v)

    # ======================================== OPACITE ========================================
    @property
    def alpha(self) -> int:
        """Renvoie l'opacité"""
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        """Fixe l'opacité"""
        self._alpha = max(0, min(255, int(value)))
        if self._image:
            self._image.set_alpha(self._alpha)

    # ======================================== MOUVEMENTS ========================================
    def move_up(self, dy=1):
        """Déplacement haut"""
        self.y -= dy

    def move_down(self, dy=1):
        """Déplacement bas"""
        self.y += dy

    def move_left(self, dx=1):
        """Déplacement gauche"""
        self.x -= dx

    def move_right(self, dx=1):
        """Déplacement droit"""
        self.x += dx

    def move_up_left(self, n=1):
        """Déplacement diagonal haut gauche"""
        d = n / sqrt(2)
        self.x -= d
        self.y -= d

    def move_up_right(self, n=1):
        """Déplacement diagonal haut droit"""
        d = n / sqrt(2)
        self.x += d
        self.y -= d

    def move_down_left(self, n=1):
        """Déplacement diagonal bas gauche"""
        d = n / sqrt(2)
        self.x -= d
        self.y += d

    def move_down_right(self, n=1):
        """Déplacement diagonal bas droit"""
        d = n / sqrt(2)
        self.x += d
        self.y += d

    # ======================================== COLLISIONS ========================================
    def collidepoint(self, point: tuple[float, float]):
        """Vérifie la collision avec un point"""
        return self.rect.collidepoint(point)

    def colliderect(self, other: pygame.Rect):
        """Vérifie la collision avec un rect"""
        if isinstance(other, SpriteEntity):
            return self.rect.colliderect(other.rect)
        return self.rect.colliderect(other)
    
    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """Affichage automatique"""
        surface.blit(self._image, self.rect)