# ======================================== IMPORTS ========================================
from _core import *

# ======================================== OBJET ========================================
class Sprite:
    """
    Objet de base pour les sprites

    Fonctionnalités:
        auto-registration
        auto-update
    """
    def __init__(self, zorder: Optional[int] = None, panel: Optional[str] = None):
        # vérifications
        if zorder is not None and not isinstance(zorder, int): _raise_error(self, '__init__', "Invalid zorder argument")
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')

        # affichage
        self._zorder = zorder
        self._panel = panel

        # paramètres
        self._active = True
        self._visible = True

        # auto-registration
        context.sprites.register(self)

    # ======================================== GETTERS ========================================

    # ======================================== SETTERS ========================================

    # ======================================== PREDICATS ========================================
    def is_active(self) -> bool:
        """Vérifie que le sprite ne soit pas gelé"""
        return self._active
    
    def is_visible(self) -> bool:
        """Vérifie que le sprite soit visible"""
        return self._visible

    # ======================================== Z-ORDER ========================================
    def move_forward(self):
        """Déplace le panel vers l'avant dans le Z-order"""
        context.sprites.reorder(self._panel, self, "forward")

    def move_backward(self):
        """Déplace le panel vers l'arrière dans le Z-order"""
        context.sprites.reorder(self._panel, self, "backward")

    def bring_to_front(self):
        """Place le panel au premier plan dans le Z-order"""
        context.sprites.reorder(self._panel, self, "front")

    def send_to_back(self):
        """Place le panel au dernier plan dans le Z-order"""
        context.sprites.reorder(self._panel, self, "back")

    def set_index(self, n: int):
        """Place le panel à l'indice n dans le Z-order"""
        context.sprites.reorder(self._panel, self, "index", n)

    # ======================================== METHODES DYNAMIQUES ========================================
    def freeze(self):
        """Rend le sprite inactif"""
        self._active = False

    def unfreeze(self):
        """Rend le sprite actif"""
        self._active = True

    def show(self):
        """Rend le sprite visible"""
        self._visible = True
    
    def hide(self):
        """Rend le sprite invisible"""
        self._visible = False

    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass

    def _update(self):
        """Proxy vers update"""
        if not self._active:
            return
        self.update()

    def draw(self, surface: pygame.Surface):
        """Appelé à chaque frame (à override)"""
        pass

    def _draw(self, surface: pygame.Surface):
        """Proxy vers draw"""
        if not self._visible:
            return
        self.draw(surface)