# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class ScrollBarObject:
    """
    Object de l'interface : Barre de défilement
    
    Scrollbar vertical ou horizontal avec curseur draggable.
    Permet d'obtenir un ratio de défilement entre 0.0 et 1.0.
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            length: Real = -1,
            thickness: Real = 20,

            orientation: str = "vertical",

            track_color: pygame.Color = (200, 200, 200, 255),
            thumb_color: pygame.Color = (100, 100, 100, 255),
            thumb_color_hover: pygame.Color = (80, 80, 80, 255),
            thumb_color_drag: pygame.Color = (60, 60, 60, 255),

            thumb_ratio: float = 0.2,
            scroll_ratio: float = 0.0,

            border_radius: int = 5,

            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée de la gauche
            y (Real) : coordonnée du haut
            length (Real) : longueur de la scrollbar (hauteur si vertical, largeur si horizontal)
            thickness (Real) : épaisseur de la scrollbar (largeur si vertical, hauteur si horizontal)

            orientation (str) : orientation ("vertical" ou "horizontal")

            track_color (Color, optional) : couleur de la piste
            thumb_color (Color, optional) : couleur du curseur
            thumb_color_hover (Color, optional) : couleur du curseur en survol
            thumb_color_drag (Color, optional) : couleur du curseur en drag

            thumb_ratio (float, optional) : ratio de la taille du curseur par rapport à la piste (0.0 à 1.0)
            scroll_ratio (float, optional) : position initiale du scroll (0.0 à 1.0)

            border_radius (int, optional) : rayon d'arrondissement

            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(length, Real) or length <= 0: _raise_error(self, '__init__', 'Invalid length argument')
        if not isinstance(thickness, Real) or thickness <= 0: _raise_error(self, '__init__', 'Invalid thickness argument')
        if not isinstance(orientation, str) or orientation not in ["vertical", "horizontal"]:
            _raise_error(self, '__init__', 'Invalid orientation argument (must be "vertical" or "horizontal")')
        track_color = _to_color(track_color, method='__init__')
        thumb_color = _to_color(thumb_color, method='__init__')
        thumb_color_hover = _to_color(thumb_color_hover, method='__init__')
        thumb_color_drag = _to_color(thumb_color_drag, method='__init__')
        if not isinstance(thumb_ratio, Real) or not (0.0 < thumb_ratio <= 1.0):
            _raise_error(self, '__init__', 'Invalid thumb_ratio argument (must be between 0.0 and 1.0)')
        if not isinstance(scroll_ratio, Real) or not (0.0 <= scroll_ratio <= 1.0):
            _raise_error(self, '__init__', 'Invalid scroll_ratio argument (must be between 0.0 and 1.0)')
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        context.ui._append(self)

        # orientation
        self._orientation = orientation
        self._vertical = orientation == "vertical"

        # dimensions
        if self._vertical:
            width = int(thickness)
            height = int(length)
        else:
            width = int(length)
            height = int(thickness)

        self._rect = pygame.Rect(x, y, width, height)

        # couleurs
        self._track_color = track_color
        self._thumb_color = thumb_color
        self._thumb_color_hover = thumb_color_hover
        self._thumb_color_drag = thumb_color_drag

        # curseur
        self._thumb_ratio = max(0.05, min(1.0, thumb_ratio))
        self._scroll_ratio = max(0.0, min(1.0, scroll_ratio))

        # style
        self._border_radius = max(0, border_radius)

        # panel maître
        self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # état
        self._dragging = False
        self._drag_offset = 0
        self._visible = True

        # surfaces
        self._surface = None
        self._surface_rect = None

    def _init(self):
        """Initialisation sécurisée"""
        context.inputs.add_lister(1, self.stop_drag(), args=[self], up=True, priority=1)

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
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy()

    @property
    def scroll_ratio(self) -> float:
        """Renvoie le ratio de défilement (0.0 à 1.0)"""
        return self._scroll_ratio

    @property
    def dragging(self) -> bool:
        """Vérifie si le curseur est en train d'être déplacé"""
        return self._dragging

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

    @scroll_ratio.setter
    def scroll_ratio(self, value: float):
        """Fixe le ratio de défilement"""
        if not isinstance(value, Real):
            _raise_error(self, 'set_scroll_ratio', 'Invalid value argument')
        self._scroll_ratio = max(0.0, min(1.0, value))

    # ======================================== GEOMETRIE ========================================
    def _get_thumb_rect(self) -> pygame.Rect:
        """Calcule le rect du curseur selon le scroll_ratio actuel"""
        if self._vertical:
            thumb_height = int(self._rect.height * self._thumb_ratio)
            max_y = self._rect.height - thumb_height
            thumb_y = int(self._scroll_ratio * max_y)
            return pygame.Rect(0, thumb_y, self._rect.width, thumb_height)
        else:
            thumb_width = int(self._rect.width * self._thumb_ratio)
            max_x = self._rect.width - thumb_width
            thumb_x = int(self._scroll_ratio * max_x)
            return pygame.Rect(thumb_x, 0, thumb_width, self._rect.height)

    def _get_thumb_world_rect(self) -> pygame.Rect:
        """Renvoie le rect du curseur en coordonnées monde"""
        local_thumb = self._get_thumb_rect()
        return pygame.Rect(
            self._rect.x + local_thumb.x,
            self._rect.y + local_thumb.y,
            local_thumb.width,
            local_thumb.height
        )

    # ======================================== INTERACTION ========================================
    def start_drag(self, mouse_pos: tuple):
        """Commence le drag du curseur"""
        thumb_rect = self._get_thumb_world_rect()
        if self._vertical:
            self._drag_offset = mouse_pos[1] - thumb_rect.y
        else:
            self._drag_offset = mouse_pos[0] - thumb_rect.x
        self._dragging = True

    def update_drag(self, mouse_pos: tuple):
        """Met à jour la position pendant le drag"""
        if not self._dragging:
            return

        if self._vertical:
            thumb_height = int(self._rect.height * self._thumb_ratio)
            max_y = self._rect.height - thumb_height
            target_y = mouse_pos[1] - self._rect.y - self._drag_offset
            self._scroll_ratio = max(0.0, min(1.0, target_y / max_y if max_y > 0 else 0.0))
        else:
            thumb_width = int(self._rect.width * self._thumb_ratio)
            max_x = self._rect.width - thumb_width
            target_x = mouse_pos[0] - self._rect.x - self._drag_offset
            self._scroll_ratio = max(0.0, min(1.0, target_x / max_x if max_x > 0 else 0.0))

    def stop_drag(self):
        """Arrête le drag"""
        self._dragging = False

    def scroll(self, delta: float):
        """
        Scroll par un delta donné
        
        Args:
            delta (float) : changement du ratio (-1.0 à 1.0)
        """
        self._scroll_ratio = max(0.0, min(1.0, self._scroll_ratio + delta))

    # ======================================== PREDICATS ========================================
    def is_hovered(self) -> bool:
        """Vérifie que la scrollbar soit survolée"""
        return context.ui.get_hovered() == self

    @property
    def hovered(self) -> bool:
        """Vérifie que la scrollbar soit survolée"""
        return context.ui.get_hovered() == self

    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur la scrollbar"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.screen.get_mouse_pos()
        return self._rect.collidepoint(mouse_pos)

    def thumb_collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le curseur"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.screen.get_mouse_pos()
        return self._get_thumb_world_rect().collidepoint(mouse_pos)

    # ======================================== DESSIN ========================================
    def _render_surface(self) -> pygame.Surface:
        """Génère la surface de la scrollbar"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        local_rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)

        # piste
        pygame.draw.rect(surface, self._track_color, local_rect, border_radius=self._border_radius)

        # curseur
        thumb_rect = self._get_thumb_rect()
        if self._dragging:
            thumb_color = self._thumb_color_drag
        elif self.thumb_collidemouse():
            thumb_color = self._thumb_color_hover
        else:
            thumb_color = self._thumb_color

        pygame.draw.rect(surface, thumb_color, thumb_rect, border_radius=self._border_radius)

        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        if self._dragging:
            self.update_drag()
        self._surface = self._render_surface()
        self._surface_rect = self._surface.get_rect(topleft=self._rect.topleft)

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return

        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface

        surface.blit(self._surface, self._surface_rect)
    
    def left_click(self, up: bool = False):
        """Clic gauche"""
        if not up:
            self.start_drag()