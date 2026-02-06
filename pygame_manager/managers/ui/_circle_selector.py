# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class CircleSelectorObject:
    """
    Object de l'interface : Sélecteur circulaire

    Appartient à un groupe de sélection identifié par selection_id.
    Un seul sélecteur par groupe peut être actif à la fois (radio-style).
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            radius: Real = -1,

            selection_id: str = "",
            selector_id: str = "",

            filling: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color = None,
            filling_color_selected: pygame.Color = None,

            icon: pygame.Surface = None,
            icon_hover: pygame.Surface = None,
            icon_selected: pygame.Surface = None,

            text: str = None,
            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color: pygame.Color = (0, 0, 0, 255),
            font_color_hover: pygame.Color = None,
            font_color_selected: pygame.Color = None,

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),

            hover_scale_ratio: float = 1.0,
            hover_scale_duration: float = 0.0,

            callback: callable = lambda: None,
            panel: object = None
        ):
        """
        Args:
            x (Real) : coordonnée x du centre
            y (Real) : coordonnée y du centre
            radius (Real) : rayon du cercle

            selection_id (str) : identifiant du groupe de sélection
            selector_id (str) : identifiant unique de ce sélecteur dans le groupe

            filling (bool, optional) : remplissage
            filling_color (Color, optional) : couleur de fond
            filling_color_hover (Color, optional) : couleur de fond lors du survol
            filling_color_selected (Color, optional) : couleur de fond lorsque sélectionné
            icon (Surface, optional) : image de fond
            icon_hover (Surface, optional) : image lors du survol
            icon_selected (Surface, optional) : image lorsque sélectionné

            text (str, optional) : texte du sélecteur
            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol
            font_color_selected (Color, optional) : couleur de la police lorsque sélectionné

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure

            hover_scale_ratio (float, optional) : facteur de redimensionnement lors du survol
            hover_scale_duration (float, optional) : durée de redimensionnement (en secondes)

            callback (callable, optional) : action en cas de sélection
            panel (object, optional) : panel maître
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(radius, Real) or radius <= 0: _raise_error(self, '__init__', 'Invalid radius argument')
        if not isinstance(selection_id, str) or not selection_id: _raise_error(self, '__init__', 'Invalid selection_id argument')
        if selection_id not in context.ui.get_selections(): _raise_error(self, '__init__', f"Selection {selection_id} does not exist")
        if not isinstance(selector_id, str) or not selector_id: _raise_error(self, '__init__', 'Invalid selector_id argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        filling_color_selected = _to_color(filling_color_selected, raised=False)
        if icon is not None and not isinstance(icon, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon argument')
        if icon_hover is not None and not isinstance(icon_hover, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon_hover argument')
        if icon_selected is not None and not isinstance(icon_selected, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon_selected argument')
        if text is not None and not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if font_size is not None and not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        font_color_selected = _to_color(font_color_selected, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')

        # auto-registration
        context.ui._append(self)
        context.ui._add_selection(selection_id)

        # zorder
        self._zorder = 0

        # surface
        self._surface = None
        self._surface_rect = None

        # sélection
        self._selection_id = selection_id
        self._selector_id = selector_id

        # position et taille
        self._radius = int(min(540, max(3, radius)))
        self._center = (int(x), int(y))
        diameter = self._radius * 2
        self._rect = pygame.Rect(x - self._radius, y - self._radius, diameter, diameter)
        self._local_center = (self._radius, self._radius)

        # background
        self._filling = filling
        self._filling_color = filling_color
        self._filling_color_hover = filling_color_hover
        self._filling_color_selected = filling_color_selected

        # images — 3 états
        self._icon = None
        self._icon_rect = None
        if icon is not None:
            max_icon = int(self._radius * 1.2)
            iwidth, iheight = icon.get_size()
            ratio = min(max_icon / iwidth, max_icon / iheight)
            self._icon = pygame.transform.smoothscale(icon, (int(iwidth * ratio), int(iheight * ratio)))
            self._icon_rect = self._icon.get_rect(center=self._local_center)

        self._icon_hover = self._icon
        self._icon_hover_rect = self._icon_rect
        if icon_hover is not None:
            max_icon = int(self._radius * 1.2)
            iwidth, iheight = icon_hover.get_size()
            ratio = min(max_icon / iwidth, max_icon / iheight)
            self._icon_hover = pygame.transform.smoothscale(icon_hover, (int(iwidth * ratio), int(iheight * ratio)))
            self._icon_hover_rect = self._icon_hover.get_rect(center=self._local_center)

        self._icon_selected = self._icon
        self._icon_selected_rect = self._icon_rect
        if icon_selected is not None:
            max_icon = int(self._radius * 1.2)
            iwidth, iheight = icon_selected.get_size()
            ratio = min(max_icon / iwidth, max_icon / iheight)
            self._icon_selected = pygame.transform.smoothscale(icon_selected, (int(iwidth * ratio), int(iheight * ratio)))
            self._icon_selected_rect = self._icon_selected.get_rect(center=self._local_center)

        # texte — 3 états
        self._text = text
        self._font = font
        self._font_path = font_path
        self._font_size = font_size
        self._font_color = font_color
        self._font_color_hover = font_color_hover if font_color_hover is not None else font_color
        self._font_color_selected = font_color_selected if font_color_selected is not None else font_color

        self._text_object = None
        self._text_object_hover = None
        self._text_object_selected = None
        self._text_object_rect = None
        self._text_blit = False

        if self._text is not None:
            if self._font_size is None:
                self._font_size = max(3, int(self._radius * 0.7))

            if self._font is None:
                try:
                    self._font = pygame.font.Font(self._font_path, self._font_size)
                except Exception as _:
                    self._font = pygame.font.Font(None, self._font_size)

            self._text_object = self._font.render(self._text, True, self._font_color)
            self._text_object_hover = self._font.render(self._text, True, self._font_color_hover)
            self._text_object_selected = self._font.render(self._text, True, self._font_color_selected)
            self._text_object_rect = self._text_object.get_rect(center=self._local_center)
            self._text_blit = True

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color

        # effet de survol
        self._hover_scale_ratio = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # action de clique
        self._callback = callback

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None

        # préchargement
        self._preloaded = {}
        self._preloaded["default"] = self.load_default()
        self._preloaded["hover"] = self.load_hover()
        self._preloaded["selected"] = self.load_selected()

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
    def rect(self) -> pygame.Rect:
        """Renvoie la bounding box pygame"""
        return self._rect.copy()

    @property
    def callback(self) -> callable:
        """Renvoie le callback"""
        return self._callback

    @property
    def selected(self) -> bool:
        """Vérifie que le sélecteur soit actif dans son groupe"""
        return context.ui._selections.get(self._selection_id) == self._selector_id

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

    @callback.setter
    def callback(self, callback: callable):
        """Fixe le callback"""
        if not callable(callback):
            _raise_error(self, 'set_callback', 'Invalid callback argument')
        self._callback = callback

    # ======================================== PREDICATS ========================================
    def is_hovered(self) -> bool:
        """Vérifie que le sélecteur soit survolé"""
        return context.ui.get_hovered() == self

    @property
    def hovered(self) -> bool:
        """Vérifie que le sélecteur soit survolé"""
        return context.ui.get_hovered() == self

    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le sélecteur (distance au centre <= rayon)"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.screen.get_mouse_pos()
        dx = mouse_pos[0] - self._center[0]
        dy = mouse_pos[1] - self._center[1]
        return dx * dx + dy * dy <= self._radius * self._radius

    # ======================================== DESSIN ========================================
    def load_default(self) -> pygame.Surface:
        """Génère la surface par défaut"""
        diameter = self._radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        if self._filling:
            pygame.draw.circle(surface, self._filling_color, self._local_center, self._radius)
        if self._icon is not None:
            surface.blit(self._icon, self._icon_rect)
        if self._text_blit:
            surface.blit(self._text_object, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.circle(surface, self._border_color, self._local_center, self._radius, self._border_width)
        return surface

    def load_hover(self) -> pygame.Surface:
        """Génère la surface survolée"""
        surface = self._preloaded["default"].copy()
        if self._filling_color_hover is not None:
            pygame.draw.circle(surface, self._filling_color_hover, self._local_center, self._radius)
        if self._icon_hover is not None:
            surface.blit(self._icon_hover, self._icon_hover_rect)
        if self._text_blit:
            surface.blit(self._text_object_hover, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.circle(surface, self._border_color, self._local_center, self._radius, self._border_width)
        return surface

    def load_selected(self) -> pygame.Surface:
        """Génère la surface sélectionnée"""
        surface = self._preloaded["default"].copy()
        if self._filling_color_selected is not None:
            pygame.draw.circle(surface, self._filling_color_selected, self._local_center, self._radius)
        if self._icon_selected is not None:
            surface.blit(self._icon_selected, self._icon_selected_rect)
        if self._text_blit:
            surface.blit(self._text_object_selected, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.circle(surface, self._border_color, self._local_center, self._radius, self._border_width)
        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def select(self):
        """Sélectionne ce sélecteur dans son groupe et lance le callback"""
        context.ui._select(self._selection_id, self._selector_id)
        self._callback()

    def update(self):
        """Actualisation par frame"""
        if self.selected:
            self._surface = self._preloaded["selected"]
        elif self.hovered:
            self._surface = self._preloaded["hover"]
        else:
            self._surface = self._preloaded["default"]
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
            context.ui.select(self._selection_id, self._selector_id)
            self.callback()

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass