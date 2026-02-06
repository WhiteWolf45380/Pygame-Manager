# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class OverlayObject:
    """
    Object de l'interface : Overlay repliable
    """
    def __init__(
            self,
            side: str = "left",
            size: Real = 300,

            filling: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 230),

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),

            collapsed: bool = False,
            collapse_duration: float = 0.3,

            panel: object = None,
            zorder: int = 100,
        ):
        """
        Args:
            side (str) : côté de l'overlay ("left", "right", "top", "bottom")
            size (Real) : largeur (left/right) ou hauteur (top/bottom) en pixels

            filling (bool, optional) : remplissage
            filling_color (Color, optional) : couleur de fond (supporte alpha pour transparence)

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure

            collapsed (bool, optional) : commence replié
            collapse_duration (float, optional) : durée de l'animation (secondes)

            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu (par défaut élevé pour être au-dessus)
        """
        # vérifications
        if not isinstance(side, str) or side not in ["left", "right", "top", "bottom"]: _raise_error(self, '__init__', 'Invalid side argument (must be "left", "right", "top", or "bottom")')
        if not isinstance(size, Real) or size <= 0: _raise_error(self, '__init__', 'Invalid size argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(collapsed, bool): _raise_error(self, '__init__', 'Invalid collapsed argument')
        if not isinstance(collapse_duration, Real) or collapse_duration < 0: _raise_error(self, '__init__', 'Invalid collapse_duration argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        context.ui._append(self)

        # configuration
        self._side = side
        self._size = int(size)
        self._filling = filling
        self._filling_color = filling_color
        self._border_width = max(0, border_width)
        self._border_color = border_color

        # animation
        self._collapsed = collapsed
        self._collapse_duration = float(collapse_duration)
        self._collapse_progress = 1.0 if collapsed else 0.0
        self._target_progress = 1.0 if collapsed else 0.0

        # panel maître
        self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # géométrie
        self._compute_geometry()

        # surface
        self._surface = None
        self._surface_rect = None

        # paramètres dynamiques
        self._visible = True

    # ======================================== GETTERS ========================================
    @property
    def zorder(self) -> int:
        """Renvoie le zorder"""
        return self._zorder

    @property
    def panel(self) -> object:
        """Renvoie le panel maître"""
        return self._panel

    @property
    def visible(self) -> bool:
        """Vérifie la visibilité"""
        return self._visible

    @property
    def collapsed(self) -> bool:
        """Vérifie si l'overlay est replié"""
        return self._collapsed

    @property
    def is_animating(self) -> bool:
        """Vérifie si l'animation est en cours"""
        return abs(self._collapse_progress - self._target_progress) > 0.01

    # ======================================== SETTERS ========================================
    @zorder.setter
    def zorder(self, value: int):
        """Fixe le zorder"""
        if not isinstance(value, int):
            _raise_error(self, 'set_zorder', 'Invalid zorder argument')
        self._zorder = value

    @visible.setter
    def visible(self, value: bool):
        """Fixe la visibilité"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_visible', 'Invalid value argument')
        self._visible = value

    # ======================================== GEOMETRIE ========================================
    def _compute_geometry(self):
        """Calcule les dimensions et positions selon le côté"""
        screen_w, screen_h = context.screen.size if hasattr(context.screen, 'size') else (1920, 1080)

        if self._side == "left":
            self._full_rect = pygame.Rect(0, 0, self._size, screen_h)
            self._collapsed_rect = pygame.Rect(-self._size, 0, self._size, screen_h)
        elif self._side == "right":
            self._full_rect = pygame.Rect(screen_w - self._size, 0, self._size, screen_h)
            self._collapsed_rect = pygame.Rect(screen_w, 0, self._size, screen_h)
        elif self._side == "top":
            self._full_rect = pygame.Rect(0, 0, screen_w, self._size)
            self._collapsed_rect = pygame.Rect(0, -self._size, screen_w, self._size)
        else:  # bottom
            self._full_rect = pygame.Rect(0, screen_h - self._size, screen_w, self._size)
            self._collapsed_rect = pygame.Rect(0, screen_h, screen_w, self._size)

    def _get_current_rect(self) -> pygame.Rect:
        """Calcule le rect actuel selon la progression du collapse"""
        t = self._collapse_progress
        x = self._full_rect.x + t * (self._collapsed_rect.x - self._full_rect.x)
        y = self._full_rect.y + t * (self._collapsed_rect.y - self._full_rect.y)
        return pygame.Rect(int(x), int(y), self._full_rect.width, self._full_rect.height)

    # ======================================== CONTROLE ========================================
    def collapse(self):
        """Replie l'overlay"""
        self._collapsed = True
        self._target_progress = 1.0

    def expand(self):
        """Déplie l'overlay"""
        self._collapsed = False
        self._target_progress = 0.0

    def toggle(self):
        """Bascule entre replié et déplié"""
        if self._collapsed:
            self.expand()
        else:
            self.collapse()

    # ======================================== DESSIN ========================================
    def _render_surface(self) -> pygame.Surface:
        """Génère la surface de l'overlay"""
        surface = pygame.Surface((self._full_rect.width, self._full_rect.height), pygame.SRCALPHA)
        local_rect = pygame.Rect(0, 0, self._full_rect.width, self._full_rect.height)

        # remplissage
        if self._filling:
            pygame.draw.rect(surface, self._filling_color, local_rect)

        # bordure
        if self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, local_rect, self._border_width)

        return surface

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur l'overlay"""
        current_rect = self._get_current_rect()
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.screen.get_mouse_pos()
        return current_rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        # animation du collapse
        if self._collapse_duration > 0 and abs(self._collapse_progress - self._target_progress) > 0.01:
            speed = context.time.dt / self._collapse_duration
            if self._collapse_progress < self._target_progress:
                self._collapse_progress = min(self._target_progress, self._collapse_progress + speed)
            else:
                self._collapse_progress = max(self._target_progress, self._collapse_progress - speed)

        # générer la surface
        self._surface = self._render_surface()
        self._surface_rect = self._get_current_rect()

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return

        # ne pas dessiner si complètement hors écran
        if self._collapse_progress >= 0.99:
            return

        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface

        surface.blit(self._surface, self._surface_rect)
    
    def left_click(self, up: bool = False):
        """Clic gauche"""
        pass

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass