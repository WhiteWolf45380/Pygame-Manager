# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== ENTITE ========================================
class Entity:
    """
    Objet de base pour les entités

    Fonctionnalités:
        auto-registration
        auto-update
    """
    def __init__(
            self,
            zorder: Optional[int] = None,
            panel: Optional[str] | object = None,
            auto: Optional[bool] = True,
            ):
        """
        Args:
            zorder (int, optional) : priorité d'affichage (0 = derrière)
            panel (str, optional) : panel d'affichage
            auto (bool, option) : gestion automatique de l'actualisation
        """
        # Vérifications
        if zorder is not None and not isinstance(zorder, int): _raise_error(self, '__init__', "Invalid zorder argument")
        if panel is not None and not isinstance(panel, (str, context.panels.Panel)): _raise_error(self, '__init__', 'Invalid panel argument')

        # Affichage
        self._zorder = zorder
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None

        # Paramètres
        self._active = True
        self._visible = True

        # Auto-registration
        if auto:
            context.entities.register(self)
            self.on_register()

    # ======================================== GETTERS ========================================

    # ======================================== SETTERS ========================================

    # ======================================== PREDICATS ========================================
    def is_active(self) -> bool:
        """Vérifie que l'entité ne soit pas gelé"""
        return self._active
    
    def is_visible(self) -> bool:
        """Vérifie que l'entité soit visible"""
        return self._visible

    # ======================================== Z-ORDER ========================================
    def move_forward(self):
        """Déplace l'entité vers l'avant dans le Z-order"""
        context.entities.reorder(self._panel, self, "forward")

    def move_backward(self):
        """Déplace l'entité vers l'arrière dans le Z-order"""
        context.entities.reorder(self._panel, self, "backward")

    def bring_to_front(self):
        """Place l'entité au premier plan dans le Z-order"""
        context.entities.reorder(self._panel, self, "front")

    def send_to_back(self):
        """Place l'entité au dernier plan dans le Z-order"""
        context.entities.reorder(self._panel, self, "back")

    def set_index(self, n: int):
        """Place l'entité à l'indice n dans le Z-order"""
        context.entities.reorder(self._panel, self, "index", n)

    # ======================================== METHODES DYNAMIQUES ========================================
    def freeze(self):
        """Rend l'entité active"""
        self._active = False

    def unfreeze(self):
        """Rend l'entité inactive"""
        self._active = True

    def show(self):
        """Rend l'entité visible"""
        self._visible = True
    
    def hide(self):
        """Rend l'entité invisible"""
        self._visible = False

    # ======================================== LIFECYCLE HOOKS ========================================
    def on_register(self):
        """Appelé automatiquement lors de l'enregistrement de l'entité"""
        pass

    def on_discard(self):
        """Appelé automatiquement lors de la suppression de l'entité"""
        pass

    # ======================================== FIN DE VIE ========================================
    def kill(self):
        """
        Détruit proprement l'entité :
            - appel du hook on_discard
            - suppression du gestionnaire
            - empêche toute réutilisation
        """
        context.entities.discard(self)
        self.on_discard()

    # ======================================== ACTUALISATION ========================================
    def update(self, *args, **kwargs):
        """Appelé à chaque frame (à override)"""
        pass

    def _update(self):
        """Proxy vers update"""
        if not self._active:
            return
        self.update()

    # ======================================== DESSIN ========================================
    def draw_behind(self, surface: pygame.Surface):
        """Appelé à chaque frame avant draw (à override)"""

    def draw(self, surface: pygame.Surface):
        """Appelé à chaque frame (à override)"""
        pass

    def draw_front(self, surface: pygame.Surface):
        """Appelé à chaque frame après draw (à override)"""

    def _draw(self, surface: pygame.Surface):
        """Proxy vers draw"""
        if not self._visible:
            return
        self.draw_behind(surface)
        self.draw(surface)
        self.draw_front(surface)