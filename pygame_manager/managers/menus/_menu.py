# ======================================== IMPORTS ========================================
import pygame
from ... import context

# ======================================== SUPERCLASS ========================================
class Menu:
    """
    Classe de base pour les menus

    Fonctionnalités:
        Auto-registration en tant que menu
        gestion automatique de la surface
        z-ordre manipulable

    Ne pas override _name, _predecessor
    N'override surface, surface_rect, draw(surface) qu'en connaissance des conséquences
    """
    def __init__(self, name: str, predecessor: str = None, rect: pygame.Rect=(0, 0, 1920, 1080), hoverable: bool = True):
        """
        Args:
            name (str) : nom du menu (doit être unique)
            predecessor (str, optional) : nom du menu prédecesseur
            rect (RectObject, optional) : dimensions du menu (accepte aussi les tuples (x, y, width, height))
            hoverable (bool, optional) : peut être survolé
        """
        rect = context.geometry._to_rect(rect, raised=False)

        # vérifications
        if not isinstance(name, str): self._raise_error('__init__', 'Invalid name argument')
        if name in context.menus: self._raise_error('__init__', f'Menu "{name}" already exists')
        if not isinstance(predecessor, str): self._raise_error('__init__', 'Invalid predecessor argument')
        if predecessor not in context.menus: self._raise_error('__init__', f'Menu "{predecessor}" does not exist')
        if rect is None: self._raise_error('__init__', 'Invalid rect argument')
        if not isinstance(hoverable, bool): self._raise_error('__init__', 'Invalid hoverable argument')

        # properties
        self._name = name
        self._predecessor = predecessor

        # surface
        self.surface_rect = rect.rect
        self.surface_width = rect.width
        self.surface_height = rect.height
        self.surface = pygame.Surface((self.surface_width, self.surface_height))

        # auto-registration
        context.menus.register(self)

    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== CALLBACKS ========================================
    def on_enter(self):
        """Appelé quand le menu devient actif (à override)"""
        pass

    def on_exit(self):
        """Appelé quand le menu devient inactif (à override)"""
        pass

    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame lorsque le menu est actif (à override)"""
        pass

    def draw(self, surface: pygame.Surface):
        """Dessin sur la surface du prédecesseur"""
        if not isinstance(surface, pygame.Surface):
            return
        surface.blit(self.surface, self.surface_rect)

    # ======================================== ACTIVATION ========================================
    def activate(self):
        """Active le menu"""
        context.menus.activate(self._name)

    def deactivate(self, pruning: bool = True):
        """
        Désactive le menu

        Args:
            pruning (bool, optional) : fermeture automatique des successeurs
        """
        context.menus.deactivate(self._name, pruning=pruning)

    def is_active(self) -> bool:
        """Vérifie que le menu soit actif"""
        return context.menus.is_active(self.name)

    def switch(self, to_activate: str, pruning: bool = True):
        """
        Ferme le menu pour un ouvrir un autre

        Args:
            to_activate (str): Menu à activer
            pruning (bool, optional) : fermeture automatique des successeurs
        """
        context.menus.switch(self._name, to_activate, pruning=pruning)

    # ======================================== Z-ORDER ========================================
    def move_forward(self):
        """Déplace le menu vers l'avant dans le Z-order"""
        context.menus.reorder(self._name, "forward")

    def move_backward(self):
        """Déplace le menu vers l'arrière dans le Z-order"""
        context.menus.reorder(self._name, "backward")

    def bring_to_front(self):
        """Place le menu au premier plan dans le Z-order"""
        context.menus.reorder(self._name, "front")

    def send_to_back(self):
        """Place le menu au dernier plan dans le Z-order"""
        context.menus.reorder(self._name, "back")

    def set_index(self, n: int):
        """Place le menu à l'indice n dans le Z-order"""
        context.menus.reorder(self._name, "index", n)

    # ======================================== COORDONNEES ========================================
    def get_absolute(self, point: tuple) -> tuple:
        """Converts a point relative to this menu into absolute (screen) coordinates"""
        return context.menus.absolute(point, self._name)

    def get_relative(self, point: tuple) -> tuple:
        """Converts an absolute point (screen) into coordinates relative to this menu"""
        return context.menus.relative(point, self._name)
    
    @property
    def mouse_pos(self) -> tuple[float, float]:
        """Renvoie la position relative de la souris"""
        return self.get_relative(context.screen.get_mouse_pos())
    
    @property
    def mouse_x(self) -> float:
        """Renvoie la coordonnée x relative de la souris"""
        return self.mouse_pos[0]
    
    @property
    def mouse_y(self) -> float:
        """Renvoie la coordonnée y relative de la souris"""
        return self.mouse_pos[1]