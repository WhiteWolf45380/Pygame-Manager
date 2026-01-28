import pygame
from ._point import PointObject


# ======================================== OBJET ========================================
class RectObject:
    """
    Object géométrique : Rectangle
    """
    __slots__ = ["_vertexs"]
    def __init__(self, x: int|float=0, y: int|float=0, width: int|float=0, height: int|float=0, rect: pygame.Rect=None):
        if rect is not None:
            self._rect = rect.copy()
        else:
            self._rect = pygame.Rect(x, y, width, height)