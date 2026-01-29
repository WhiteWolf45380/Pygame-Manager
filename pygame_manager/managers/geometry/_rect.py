# ======================================== OBJET ========================================
from __future__ import annotations
from _core.imports import *
from _core.utils import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list, np.ndarray)

# ======================================== OBJET ========================================
class RectObject:
    """
    Object géométrique : Rectangle
    """
    def __init__(self, O: PointObject | Iterable[numbers.Real], u: VectorObject | Iterable[numbers.Real], v: VectorObject | Iterable[numbers.Real]):
        # point
        if not isinstance(O, PointObject):
            if not isinstance(O, Sequence):
                _raise_error(self, '__init__', 'Invalid O point argument')
            if any(not isinstance(c, numbers.Real) for c in O):
                _raise_error(self, '__init__', 'Invalid O point coordinates')
            O = PointObject(*map(float, O))
        
        # vecteur u
        if not isinstance(u, VectorObject):
            if not isinstance(u, Sequence):
                _raise_error(self, '__init__', 'Invalid u vector argument')
            if any(not isinstance(c, numbers.Real) for c in u):
                _raise_error(self, '__init__', 'Invalid u vector coordinates')
            u = VectorObject(*map(float, u))
        
        # vecteur v
        if not isinstance(v, VectorObject):
            if not isinstance(v, Sequence):
                _raise_error(self, '__init__', 'Invalid v vector argument')
            if any(not isinstance(c, numbers.Real) for c in v):
                _raise_error(self, '__init__', 'Invalid v vector coordinates')
            v = VectorObject(*map(float, v))

        # égalisation des dimensions
        self._O, self._u, self._v = O.equalized_with_vectors(u, v)

        # vérification de l'orthogonalité
        if not self._u.is_orthogonal(self._v)

        # remplissage
        self._filling = True
        self._color = (255, 255, 255)

        # bordure
        self._border = True
        self._border_color = (0, 0, 0)
        self._border_width = 2

        # forme
        self._border_radius = -1
        self._border_topleft_radius = -1
        self._border_topright_radius = -1
        self._border_bottomleft_radius = -1
        self._border_bottomright_radius = -1

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __repr__(self) -> str:
        """Représentation du rect"""
        return f"Rect(P{self._P.to_tuple()}, w : {self._w.to_tuple()}, h : {self._h.to_tuple()})"
    
    def __iter__(self) -> Iterator[float]:
        """Itération sur les sommets"""
        for vertex in [self.topleft, self.topright, self.bottomleft, self.bottomright]: yield vertex 

    def __hash__(self) -> int:
        """Renvoie le rect hashé"""
        return hash(self.to_tuple())
    
    # ======================================== GETTERS ========================================
    @property
    def rect(self) -> pygame.Rect:
        """Renvoie l'objet pygame.Rect"""
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    @property
    def x(self) -> float:
        """Renvoie la coordonnée x"""
        return min(self._P.x, self._P.x + self._w.x)
    
    @property
    def y(self) -> float:
        """Renvoie la coordonnée y"""
        return min(self._P.y, self._P.y + self._h.y)
    
    def get_size(self) -> tuple[float]:
        """Renvoie les dimensions du rect"""
        return self._width, self._height
    
    @property
    def width(self) -> float:
        """Renvoie la largeur"""
        return self._width
    
    @property
    def height(self) -> float:
        """Renvoie la hauteur"""
        return self._height
    
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
    def border_color(self):
        """Renvoie la couleur de la bordure"""
        return self._border_color
    
    @property
    def border_width(self):
        """Renvoie l'épaisseur de la bordure"""
        return self._border_width
    
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
    @x.setter
    def x(self, coordinate: numbers.Real):
        """Fixe la coordonnée x"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_x', 'Invalid coordinate argument')
        self._x = float(coordinate)
    
    @y.setter
    def y(self, coordinate: numbers.Real):
        """Fixe la coordonnée y"""
        if not isinstance(coordinate, numbers.Real):
            _raise_error(self, 'set_y', 'Invalid coordinate argument')
        self._y = float(coordinate)

    @width.setter
    def width(self, width: numbers.Real):
        """Fixe la largeur"""
        if not isinstance(width, numbers.Real):
            _raise_error(self, 'set_width', 'Invalid width argument')
        self._width = float(width)

    @height.setter
    def height(self, height: numbers.Real):
        """Fixe la hauteur"""
        if not isinstance(height, numbers.Real):
            _raise_error(self, 'set_height', 'Invalid height argument')
        self._height = float(height)

    @filling.setter
    def filling(self, value: bool):
        """Active ou non le remplissage"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_filling', 'Invalid value argument')
        self._filling = value

    @color.setter
    def color(self, color: tuple[int, int, int]):
        """fixe la couleur"""
        if not isinstance(color, (tuple, list)) or any(not isinstance(c, int) for c in color):
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
        if not isinstance(color, (tuple, list)) or any(not isinstance(c, int) for c in color):
            _raise_error(self, 'set_border_color', 'Invalid color argument')
        self._border_color = color

    @border_width.setter
    def border_width(self, width: int):
        """Fixe l'épaisseur de la bordure"""
        if not isinstance(width, int):
            _raise_error(self, 'set_border_width', 'Invalid width argument')
        self._border_width = width

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
        return self.translate(vector)

    # ======================================== METHODES INTERACTIVES ========================================
    def copy(self) -> RectObject:
        """Renvoie une copie du rect"""
        new_rect = self.__class__.__new__(self.__class__)
        new_rect.__dict__ = dict(filter(lambda k: k != '_rect', self.__dict__.copy()))
        new_rect.__init__(rect=self._rect, _copy=True)
        return new_rect
    
    def to_tuple(self) -> tuple[float]:
        """Renvoie les propriétés dans un tuple"""
        return tuple(self.x, self.y, self.width, self.height)

    def to_list(self) -> list[float]:
        """Renvoie les propriétés dans une liste"""
        return list(self.x, self.y, self.width, self.height)
    
    def translate(self, vector: VectorObject):
        """Renvoie l'image du rect par le vecteur donné"""
        u = vector.copy().reshape[2]
        self.x += u.x
        self.y += u.y

    # ======================================== AFFICHAGE ========================================
    def draw(self, surface: pygame.Surface):
        """Dessine le rect sur une surface donnée"""
        if not isinstance(surface, pygame.Surface):
            _raise_error(self, 'draw', 'Invalid surface argument')
        
        # paramètres
        color = self._color
        rect = self._rect
        border_width = self._border_width if self._border else 0
        border_radius = self._border_radius
        border_topleft_radius = self._border_topleft_radius
        border_topright_radius = self._border_topright_radius
        border_bottomleft_radius = self._border_bottomleft_radius
        border_bottomright_radius = self._border_bottomright_radius

        # dessin
        pygame.draw.rect(surface, color, rect, border_width, border_radius, border_topleft_radius, border_topright_radius, border_bottomleft_radius, border_bottomright_radius)