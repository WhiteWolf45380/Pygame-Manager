# ======================================== IMPORTS ========================================
import pygame
from typing import Iterable

# ======================================== SUPERCLASS ========================================
class Menu:
    """
    Base class for menus.

    Predecessor/successor system forming a tree.
    The predecessor can be a State, a Menu, or None (→ screen.surface).
    Each menu has its own surface and draws on the surface of its predecessor.
    Successors are ordered (z-order): index 0 = background.

    Automatically registers in MenusManager upon instantiation.
    """
    def __init__(self, name: str, predecessor: str = None, predecessor_type: str = None,
                 width: int = 1920, height: int = 1080):
        """
        Args:
            name (str): unique menu name
            predecessor (str | None): name of the predecessor (State or Menu). None = screen.surface
            predecessor_type (str | None): "state" or "menu". Ignored if predecessor is None
            width (int): surface width
            height (int): surface height
        """
        # validations
        if not isinstance(name, str):
            self._raise_error('__init__', 'Invalid name argument')
        if not isinstance(width, int) or width <= 0:
            self._raise_error('__init__', 'Invalid width argument')
        if not isinstance(height, int) or height <= 0:
            self._raise_error('__init__', 'Invalid height argument')
        if predecessor is not None:
            if not isinstance(predecessor, str):
                self._raise_error('__init__', 'predecessor must be a string or None')
            if predecessor_type not in ("state", "menu"):
                self._raise_error('__init__', 'predecessor_type must be "state" or "menu" when predecessor is set')

        # properties
        self.name = name
        self.predecessor = predecessor
        self.predecessor_type = predecessor_type  # None if predecessor is None

        # surface
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((self.surface_width, self.surface_height))
        self.surface_rect = self.surface.get_rect()

        # auto-registration
        from .menus import menus_manager
        self.manager = menus_manager
        self.manager.register(self)

    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== CALLBACKS ========================================
    def on_enter(self):
        """Called when the menu becomes active"""
        pass

    def on_exit(self):
        """Called when the menu becomes inactive"""
        pass

    # ======================================== RENDER ========================================
    def update(self, *args, **kwargs):
        """Frame-to-frame logic — to be overridden"""
        pass

    def draw(self, surface: pygame.Surface):
        """Draws this surface onto the predecessor's surface"""
        if not isinstance(surface, pygame.Surface):
            return
        surface.blit(self.surface, self.surface_rect)

    # ======================================== ACTIVATION ========================================
    def activate(self):
        """Activates this menu"""
        self.manager.activate(self.name)

    def deactivate(self):
        """Deactivates this menu (and the whole subtree)"""
        self.manager.deactivate(self.name)

    def is_active(self) -> bool:
        return self.manager.is_active(self.name)

    # ======================================== SWITCH ========================================
    def switch(self, to_close: str | Iterable, to_activate: str):
        """
        Closes one or more successors and activates another.
        All must be direct successors of this menu.

        Args:
            to_close (str | Iterable[str]): successor(s) to close
            to_activate (str): successor to activate
        """
        self.manager.switch(self.name, to_close, to_activate)

    # ======================================== Z-ORDER ========================================
    def move_forward(self):
        """Moves one position forward in the predecessor's successor list"""
        self.manager.reorder(self.name, "forward")

    def move_backward(self):
        """Moves one position backward"""
        self.manager.reorder(self.name, "backward")

    def bring_to_front(self):
        """Moves to the last position (foreground)"""
        self.manager.reorder(self.name, "bring_to_front")

    def send_to_back(self):
        """Moves to the first position (background)"""
        self.manager.reorder(self.name, "send_to_back")

    def set_layer(self, n: int):
        """Sets to index n in the predecessor's successor list"""
        self.manager.reorder(self.name, "set_layer", n)

    # ======================================== COORDINATES ========================================
    def get_absolute(self, point: tuple) -> tuple:
        """Converts a point relative to this menu into absolute (screen) coordinates"""
        return self.manager.absolute(point, self.name)

    def get_relative(self, point: tuple) -> tuple:
        """Converts an absolute point (screen) into coordinates relative to this menu"""
        return self.manager.relative(point, self.name)
