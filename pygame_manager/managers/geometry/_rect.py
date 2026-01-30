# ======================================== OBJET ========================================
from __future__ import annotations
from _core.imports import *
from _core.utils import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list, np.ndarray)

# ======================================== OBJET ========================================
class RectObject:
    """
    Object géométrique 2D : Rectangle
    """
    __slots__ = ["_O", "_w", "_h", "_filling", "_color", "_border", "_border_color", "_border_width", "_border_around", "_border_radius"
                , "_border_topleft_radius", "_border_topright_radius", "_border_bottomleft_radius", "_border_bottomright_radius"]
    def __init__(self, point: PointObject, width: numbers.Real, height: numbers.Real):
        # point
        self._O = _to_point(point)
        self._O.reshape(2)

        # vecteur horizontal
        if not isinstance(width, numbers.Real) or width <= 0:
            _raise_error(self, '__init__', 'Invalid width argument')
        self._w = VectorObject(width, 0)

        # vecteur vertical
        if not isinstance(height, numbers.Real) or height <= 0:
            _raise_error(self, '__init__', 'Invalid height argument')
        self._h = VectorObject(height, 0)

        # remplissage
        self._filling = True
        self._color = (255, 255, 255)

        # bordure
        self._border = True
        self._border_color = (0, 0, 0)
        self._border_width = 2
        self._border_around = False

        # forme
        self._border_radius = -1
        self._border_topleft_radius = -1
        self._border_topright_radius = -1
        self._border_bottomleft_radius = -1
        self._border_bottomright_radius = -1

    # ======================================== METHODES FONCTIONNELLES ========================================  
    def __repr__(self) -> str:
        """Représentation du rect"""
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
    
    def __iter__(self) -> Iterator[float]:
        """Itération sur les sommets"""
        for vertex in [self.topleft, self.topright, self.bottomleft, self.bottomright]: yield vertex 

    def __hash__(self) -> int:
        """Renvoie le rect hashé"""
        return hash(self.to_tuple())
    
    # ======================================== GETTERS ========================================
    # pygame
    @property
    def rect(self) -> pygame.Rect:
        """Renvoie l'objet pygame.Rect"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    # position    
    def get_pos(self) -> tuple[float]:
        """Renvoie la position"""
        return self.x, self.y
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x"""
        return self._O.x
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y"""
        return self._O.y
    
    @property
    def topleft(self) -> tuple[float]:
        """Renvoie les coordonnées du point haut gauche"""
        return self.x, self.y
    
    @property
    def top(self) -> float:
        """Renvoie la coordonnée du haut"""
        return self.y
    
    @property
    def topright(self) -> tuple[float]:
        """Renvoie les coordonnées du point haut droit"""
        return self.x + self.width, self.y
    
    @property
    def right(self) -> float:
        """Renvoie la coordonnée de la droite"""
        return self.x + self.width
    
    @property
    def bottomright(self) -> tuple[float]:
        """Renvoie les coordonnées du point haut gauche"""
        return self.x + self.width, self.y + self.height
    
    @property
    def bottom(self) -> float:
        """Renvoie la coordonnée du bas"""
        return self.y + self.height
    
    @property
    def bottomleft(self) -> tuple[float]:
        """Renvoie les coordonnées du point bas gauche"""
        return self.x, self.y + self.height
    
    @property
    def left(self) -> float:
        """Renvoie la coordonnée de la gauche"""
        return self.x
    
    @property
    def center(self) -> tuple[float]:
        """Renvoie les coordonnées du centre"""
        return self.x + self.width / 2, self.y + self.height / 2
    
    @property
    def centerx(self) -> float:
        """Renvoie la coordonnée x du center"""
        return self.x + self.width / 2

    @property
    def centery(self) -> float:
        """Renvoie la coordonnée y du centre"""
        return self.y + self.height / 2

    # taille
    def get_size(self) -> tuple[float]:
        """Renvoie les dimensions du rect"""
        return self.width, self.height
    
    @property
    def width(self) -> float:
        """Renvoie la largeur"""
        return self._w.norm
    
    @property
    def height(self) -> float:
        """Renvoie la hauteur"""
        return self._h.norm
    
    # paramètres d'affichage
    @property
    def filling(self) -> bool:
        """Vérifie le remplissage"""
        return self._filling

    @property
    def color(self) -> tuple[int, int, int]:
        """Renvoie la couleur"""
        return self._color
    
    @property
    def border(self) -> bool:
        """Vérifie la bordure"""
        return self._border
    
    @property
    def border_color(self) -> tuple[int, int, int]:
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
        """Renvoie l'arrondi du coin bas gauche"""
        return self._border_bottomright_radius

    # ======================================== SETTERS ========================================
    # position
    @x.setter
    def x(self, coordinate: numbers.Real):
        """Fixe la coordonnée x"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_x', 'Invalid coordinate argument')
        self._O.x = float(coordinate)
    
    @y.setter
    def y(self, coordinate: numbers.Real):
        """Fixe la coordonnée y"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_y', 'Invalid coordinate argument')
        self._O.y = float(coordinate)

    @topleft.setter
    def topleft(self, point: PointObject):
        """Fixe les coordonnées du coin haut gauche"""
        self._O = _to_point(point)

    @top.setter
    def top(self, coordinate: numbers.Real):
        """Fixe la coordonnée du haut"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_top', 'Invalid coordinate argument')
        self._O.y = float(coordinate)

    @topright.setter
    def topright(self, point: PointObject):
        """Fixe les coordonnées du coin haut droit"""
        self._O = _to_point(point) - self._w
    
    @right.setter
    def right(self, coordinate: numbers.Real):
        """Fixe la coordonnée de la droite"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_right', 'Invalid coordinate argument')
        self._O.x = float(coordinate) - self.width

    @bottomright.setter
    def bottomright(self, point: PointObject):
        """Fixe les coordonnées du coin bas droit"""
        self._O = _to_point(point) - self._w - self._h
    
    @bottom.setter
    def bottom(self, coordinate: numbers.Real):
        """Fixe la coordonnée du bas"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_bottom', 'Invalid coordinate argument')
        self._O.y = float(coordinate) - self.height
    
    @bottomleft.setter
    def bottomleft(self, point: PointObject):
        """Fixe les coordonnées du coin bas gauche"""
        self._O = _to_point(point) - self._h

    @left.setter
    def left(self, coordinate: numbers.Real):
        """Fixe la coordonnée de la gauche"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_left', 'Invalid coordinate argument')
        self._O.x = float(coordinate)
    
    @center.setter
    def center(self, point: PointObject):
        """Fixe les coordonnées du centre"""
        self._O = _to_point(point) - 0.5 * (self._h + self._w)

    @centerx.setter
    def centerx(self, coordinate: numbers.Real):
        """Fixe la coordonnée x du centre"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_centerx', 'Invalid coordinate argument')
        self._O.x = float(coordinate) - 0.5 * self.width
    
    @centery.setter
    def centery(self, coordinate: numbers.Real):
        """Fixe la coordonnée x du centre"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_centery', 'Invalid coordinate argument')
        self._O.y = float(coordinate) - 0.5 * self.height
    
    # taille
    @width.setter
    def width(self, width: numbers.Real):
        """Fixe la largeur"""
        if not isinstance(width, numbers.Real) or width <= 0:
            _raise_error(self, 'set_width', 'Invalid width argument')
        self._w.set_norm(width)

    @height.setter
    def height(self, height: numbers.Real):
        """Fixe la hauteur"""
        if not isinstance(height, numbers.Real) or height <= 0:
            _raise_error(self, 'set_height', 'Invalid height argument')
        self._h.set_norm(height)

    # paramètres d'affichage
    @filling.setter
    def filling(self, value: bool):
        """Active ou non le remplissage"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_filling', 'Invalid value argument')
        self._filling = value

    @color.setter
    def color(self, color: tuple[int, int, int]):
        """fixe la couleur"""
        if not isinstance(color, tuple) or len(color) != 3 or any(not isinstance(c, int) or c < 0 for c in color):
            _raise_error(self, 'set_color', 'Invalid color argument')
        self._color = color

    @border.setter
    def border(self, value: bool):
        """Active ou non la bordure"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_border', 'Invalid value argument')
        self._border = value
    
    @border_color.setter
    def border_color(self, color: tuple[int, int, int]):
        """Fixe la couleur de la bordure"""
        if not isinstance(color, tuple) or len(color) != 3 or any(not isinstance(c, int) for c in color):
            _raise_error(self, 'set_border_color', 'Invalid color argument')
        self._border_color = color

    @border_width.setter
    def border_width(self, width: int):
        """Fixe l'épaisseur de la bordure"""
        if not isinstance(width, int):
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
        self._border_radius = radius

    @border_topleft_radius.setter
    def border_topleft_radius(self, radius: int):
        """Fixe l'arrondi du coin haut gauche"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_topleft_radius', 'Invalid radius argument')
        self._border_topleft_radius = radius
    
    @border_topright_radius.setter
    def border_topright_radius(self, radius: int):
        """Fixe l'arrondi du coin haut droite"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_topright_radius', 'Invalid radius argument')
        self._border_topright_radius = radius

    @border_bottomleft_radius.setter
    def border_bottomleft_radius(self, radius: int):
        """Fixe l'arrondi du coin bas gauche"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_bottomleft_radius', 'Invalid radius argument')
        self._border_bottomleft_radius = radius

    @border_bottomright_radius.setter
    def border_bottomright_radius(self, radius: int):
        """Fixe l'arrondi des coins"""
        if not isinstance(radius, int):
            _raise_error(self, 'set_border_bottomright_radius', 'Invalid radius argument')
        self._border_bottomright_radius = radius

    # ======================================== OPERATIONS ========================================
    def __add__(self, vector: VectorObject) -> RectObject:
        """renvoie l'image du rect par le vecteur donné"""
        if not isinstance(vector, VectorObject): return NotImplemented
        return self.translate(vector)
    
    def __radd__(self, vector: VectorObject) -> RectObject:
        """renvoie l'image du rect par le vecteur donné"""
        if not isinstance(vector, VectorObject): return NotImplemented
        return self.translate(vector)
    
    def __sub__(self, vector: VectorObject) -> RectObject:
        """renvoie l'image du rect par l'opposé du vecteur donné"""
        if not isinstance(vector, VectorObject): return NotImplemented
        return self.translate(vector)

    def __rsub__(self, vector: VectorObject) -> RectObject:
        """renvoie l'image du rect par l'opposé du vecteur donné"""
        if not isinstance(vector, VectorObject): return NotImplemented
        return self.translate(vector)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> RectObject:
        """
        Renvoie une copie du rect
        """
        return deepcopy(self)

    def to_tuple(self) -> tuple[float]:
        """
        Renvoie les propriétés dans un tuple
        """
        return (self.x, self.y, self.width, self.height)

    def to_list(self) -> list[float]:
        """
        Renvoie les propriétés dans une liste
        """
        return [self.x, self.y, self.width, self.height]
    
    def translate(self, vector: VectorObject):
        """
        Renvoie l'image du rect par le vecteur donné

        Args:
            vector (VectorObject) : vecteur de translation
        """
        vector = _to_vector(vector)
        self.x += vector.x
        self.y += vector.y

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface, filling: bool=None, color: tuple[int, int, int]=None, border: bool=None, border_width: int=None, border_color: tuple[int, int, int]=None):
        """
        Dessine le rect sur une surface donnée
        Par défaut les paramètres sont ceux définis pour le RectObject en question

        Args:
            surface (pygame.Surface) : surface de dessin
            filling (bool, optional) : remplissage
            color (tuple[int, int, int], optional) : couleur de remplissage
            border (bool, optional) : bordure
            border_width (int, optional) : épaisseur de la bordure
            border_color (tuple[int, int, int], optional) : couleur de la bordure
        """
        if not isinstance(surface, pygame.Surface): _raise_error(self, 'draw', 'Invalid surface argument')
        if filling is not None and not isinstance(filling, bool): _raise_error(self, 'draw', 'Invalid filling argument')
        if color is not None and (not isinstance(color, Sequence) or any(not isinstance(c, int) for c in color)): _raise_error(self, 'draw', 'Invalid color argument')
        if border is not None and not isinstance(border, bool): _raise_error(self, 'draw', 'Invalid border argument')
        if border_width is not None and not isinstance(border_width, bool): _raise_error(self, 'draw', 'Invalid border_width argument')
        if border_color is not None and (not isinstance(border_color, Sequence) or any(not isinstance(c, int) for c in border_color)): _raise_error(self, 'draw', 'Invalid border_color argument')
        
        # paramètres d'affichage
        rect = self.rect
        filling = self._filling if filling is None else filling
        color = self._color if color is None else color
        border = self._border if border is None else border
        border_width = self._border_width if border_width is None else border_width
        border_color = self._border_color if border_color is None else border_color
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
        if border_around:
            rect_around = pygame.Rect(rect.left - border_width, rect.top - border_width, rect.width + 2 * border_width, rect.height + 2 * border_width)
            pygame.draw.rect(surface, border_color, rect_around, border_width, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)
        else:
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)