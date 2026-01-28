import pygame
from ._point import PointObject


# ======================================== OBJET ========================================
class RectObject:
    """
    Object géométrique : Rectangle
    """
    def __init__(self, x: int|float=0, y: int|float=0, width: int|float=0, height: int|float=0, rect: pygame.Rect=None):
        if rect is not None:
            if not isinstance(rect, pygame.Rect):
                self._raise_error('__init__', 'rect argument must be a pygame.Rect object')
            self._rect = rect.copy()
        else:
            self._rect = pygame.Rect(x, y, width, height)
        self._color = (0, 0, 0)
        self._border_radius = 0
        self._border_topleft_radius = 0
        self._border_topright_radius = 0
        self._border_bottomleft_radius = 0
        self._border_bottomright_radius = 0

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __repr__(self) -> str:
        """Représentation du rect"""
        return f"Rect({self.x, self.y, self.width, self.height})"

    def __getattr__(self, name):
        """Proxy get vers l'objet pygame.Rect"""
        return getattr(self._rect, name)
    
    def __setattr__(self, name, value):
        """Proxy set vers l'objet pygame.Rect"""
        if name == "_rect":
            return super().__setattr__(self, name, value)
        setattr(self._rect, name, value)
    
    # ======================================== GETTERS ========================================
    @property
    def rect(self):
        """Renvoie l'objet pygame.Rect"""
        return self._rect

    @property
    def color(self):
        """Renvoie la couleur"""
        return self._color
    
    @property
    def border_radius(self):
        """Renvoie l'arrondi des coins"""
        return self._border_radius
    
    @property
    def border_topleft_radius(self):
        """Renvoie l'arrondi du coin haut gauche"""
        return self.border_topleft_radius
    
    @property
    def border_topright_radius(self):
        """Renvoie l'arrondi du coin haut droit"""
        return self.border_topright_radius
    
    @property
    def border_bottomleft_radius(self):
        """Renvoie l'arrondi du coin bas gauche"""
        return self.border_bottomleft_radius
    
    @property
    def border_bottomright_radus(self):
        """Renvoie l'arrondi du coin bas gauche"""

    # ======================================== SETTERS ========================================

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """Dessine le rectangle sur une surface donnée"""