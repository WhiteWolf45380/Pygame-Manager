# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== SUPERCLASS ========================================
class Panel:
    """
    Classe de base pour les panels

    Fonctionnalités:
        Auto-registration en tant que panel
        gestion automatique de la surface
        z-ordre manipulable
        affichage automatique sur le panel prédecesseur

    Override update() et draw() pour l'actualisation et l'affichage
    """
    def __init__(
            self, 
            name: str, 
            predecessor: str = None, 
            rect: pygame.Rect=(0, 0, 1920, 1080), 
            centered: bool = False, 
            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_around: bool = False,
            hoverable: bool = True
            ):
        """
        Args:
            name (str) : nom du panel (doit être unique)
            predecessor (str, optional) : nom du panel prédecesseur
            rect (RectObject, optional) : dimensions du panel (accepte aussi les tuples (x, y, width, height))
            centered (bool, optional) : coordonnées à partir du centre de la surface maître
            border_width (int, optional) : épaisseur de la bordure du panel
            border_around (bool, optional) : affichage de la borddure à l'extérieur du panel
            hoverable (bool, optional) : peut être survolé
        """
        rect = context.geometry._to_rect(rect, raised=False)

        # vérifications
        if not isinstance(name, str): _raise_error(self, '__init__', 'Invalid name argument')
        if name in context.panels: _raise_error(self, '__init__', f'panel "{name}" already exists')
        if predecessor is not None and not isinstance(predecessor, str): _raise_error(self, '__init__', 'Invalid predecessor argument')
        if predecessor is not None and predecessor not in context.panels: _raise_error(self, '__init__', f'panel "{predecessor}" does not exist')
        if rect is None: _raise_error(self, '__init__', 'Invalid rect argument')
        if not isinstance(centered, bool): _raise_error(self, '__init__', 'Invalid centered argument')
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color)
        if not isinstance(border_around, bool): _raise_error(self, '__init__', 'Invalid border_around argument')
        if not isinstance(hoverable, bool): _raise_error(self, '__init__', 'Invalid hoverable argument')

        # properties
        self._name = name
        self._predecessor = predecessor

        # surface
        if centered: rect.center = context.menus["predecessor"].surface_rect.center if predecessor is not None else context.screen.center
        self._surface_rect = rect.rect
        self._surface_width = rect.width
        self._surface_height = rect.height
        self._surface = pygame.Surface((self._surface_width, self._surface_height))

        # bordure
        self._border_width = border_width
        self._border_color = border_color
        self._border_around = border_around

        self._border = None
        if self._border_width != 0:
            x = self._surface_rect.left - (self._border_width if self._border_around else 0)
            y = self._surface_rect.top - (self._border_width if self._border_around else 0)
            width = self._surface_rect.width + 2 * (self._border_width if self._border_around else 0)
            height = self._surface_rect.height + 2 * (self._border_width if self._border_around else 0)
            self._border = pygame.Rect(x, y, width, height)

        # survol
        self._hoverable = hoverable

        # auto-registration
        context.panels.register(self)

    def __str__(self):
        """Renvoie le nom du panel"""
        return self._name

    # ======================================== CALLBACKS ========================================
    def on_enter(self):
        """Appelé quand le panel devient actif (à override)"""
        pass

    def on_exit(self):
        """Appelé quand le panel devient inactif (à override)"""
        pass

    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame lorsque le panel est actif (à override)"""
        pass

    # ======================================== AFFICHAGE ========================================
    def draw_back(surface: pygame.Surface):
        """Appelé à chaque frame avant l'affichage du panel (à override)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Affichage du panel sur la surface du prédecesseur"""
        if not isinstance(surface, pygame.Surface):
            return
        surface.blit(self._surface, self._surface_rect)

        if self._border is not None:
            pygame.draw.rect(surface, self._border_color, self._border, self._border_width)
        
    # ======================================== ACTIVATION ========================================
    def activate(self):
        """Active le panel"""
        context.panels.activate(self._name)

    def deactivate(self, pruning: bool = True):
        """
        Désactive le panel

        Args:
            pruning (bool, optional) : fermeture automatique des successeurs
        """
        context.panels.deactivate(self._name, pruning=pruning)

    def is_active(self) -> bool:
        """Vérifie que le panel soit actif"""
        return context.panels.is_active(self.name)

    def switch(self, to_activate: str, pruning: bool = True):
        """
        Ferme le panel pour un ouvrir un autre

        Args:
            to_activate (str): panel à activer
            pruning (bool, optional) : fermeture automatique des successeurs
        """
        context.panels.switch(self._name, to_activate, pruning=pruning)

    # ======================================== Z-ORDER ========================================
    def move_forward(self):
        """Déplace le panel vers l'avant dans le Z-order"""
        context.panels.reorder(self._name, "forward")

    def move_backward(self):
        """Déplace le panel vers l'arrière dans le Z-order"""
        context.panels.reorder(self._name, "backward")

    def bring_to_front(self):
        """Place le panel au premier plan dans le Z-order"""
        context.panels.reorder(self._name, "front")

    def send_to_back(self):
        """Place le panel au dernier plan dans le Z-order"""
        context.panels.reorder(self._name, "back")

    def set_index(self, n: int):
        """Place le panel à l'indice n dans le Z-order"""
        context.panels.reorder(self._name, "index", n)
    
    # ======================================== SURVOL ========================================
    @property
    def hoverable(self) -> bool:
        """Vérifie que le panel soit survolable"""
        return self._hoverable
    
    @hoverable.setter
    def hoverable(self, value: bool):
        """Fixe le survol du panel"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_hoverable', 'Invalid value argument')
        self._hoverable = value

    # ======================================== GETTERS ========================================
    # Conversions
    def get_absolute(self, point: tuple) -> tuple:
        """Converts a point relative to this panel into absolute (screen) coordinates"""
        return context.panels.absolute(point, self._name)

    def get_relative(self, point: tuple) -> tuple:
        """Converts an absolute point (screen) into coordinates relative to this panel"""
        return context.panels.relative(point, self._name)
    
    # Souris
    @property
    def mouse_pos(self) -> tuple[float, float]:
        """Renvoie la position relative de la souris"""
        return self.get_relative(context.mouse.get_pos())
    
    @property
    def mouse_x(self) -> float:
        """Renvoie la coordonnée x relative de la souris"""
        return self.mouse_pos[0]
    
    @property
    def mouse_y(self) -> float:
        """Renvoie la coordonnée y relative de la souris"""
        return self.mouse_pos[1]
    
    # Surface
    @property
    def surface(self) -> pygame.Surface:
        """Surface du panel"""
        return self._surface
    
    @property
    def rect(self) -> pygame.Rect:
        """Rectangle du panel"""
        return self._surface_rect

    @property
    def x(self) -> int:
        """Position x du panel"""
        return self._surface_rect.x

    @property
    def y(self) -> int:
        """Position y du panel"""
        return self._surface_rect.y

    @property
    def width(self) -> int:
        """Largeur du panel"""
        return self._surface_rect.width

    @property
    def height(self) -> int:
        """Hauteur du panel"""
        return self._surface_rect.height

    # Positions (in)
    @property
    def center(self) -> tuple[float, float]:
        """Centre du panel"""
        return (self._surface_rect.width / 2, self._surface_rect.height / 2)

    @property
    def centerx(self) -> float:
        """Centre x du panel"""
        return self._surface_rect.width / 2

    @property
    def centery(self) -> float:
        """Centre y du panel"""
        return self._surface_rect.height / 2