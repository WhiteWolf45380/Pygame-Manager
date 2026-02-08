# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class CircleButtonObject:
    """
    Object de l'interface : Bouton circulaire
    
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            radius: Real = -1,

            filling: bool = True,
            filling_hover: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color = None,

            icon: pygame.Surface = None,
            icon_hover: pygame.Surface = None,
            icon_keep_ratio: bool = True,
            icon_scale_ratio: float = 0.8,

            text: str = None,
            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color: pygame.Color = (0, 0, 0, 255),
            font_color_hover: pygame.Color | None = None,

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_color_hover: pygame.Color | None = None,

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

            filling (bool, optional) : remplissage
            filling_hover (bool, optional) : remplissage lors du survol
            filling_color (Color, optional) : couleur de fond
            filling_color_hover (Color, optional) : couleur de fond lors du survol

            icon (Surface, optional) : image de fond
            icon_hover (Surface, optional) : image de fond lors du survol
            icon_keep_ratio (Surface, optional) : pas de déformation, ratio_locker
            icon_scale_ratio (Surface, optional) : ratio maximum par rapport aux dimensions du bouton

            text (str, optional) : texte du bouton
            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_color_hover (Color, optional) : couleur de la bordure lors du survol

            hover_scale_ratio (float, optional) : facteur de redimensionnement lors du survol
            hover_scale_duration (float, optional) : durée de redimensionnement (en secondes)

            callback (callable, optional) : action en cas de pression du bouton
            panel (object, optional) : panel maître pour affichage automatique sur la surface
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(radius, Real) or radius <= 0: _raise_error(self, '__init__', 'Invalid radius argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        if not isinstance(filling_hover, bool): _raise_error(self, '__init__', 'Invalid filling_hover argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        if icon is not None and not isinstance(icon, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon argument')
        if icon_hover is not None and not isinstance(icon_hover, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon_hover argument')
        if not isinstance(icon_keep_ratio, bool): _raise_error(self, '__init__', 'Invalid icon_keep_ratio argument')
        if not isinstance(icon_scale_ratio, Real): _raise_error(self, '__init__', 'Invalid icon_scale_ratio argument')
        if text is not None and not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if font_size is not None and not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        border_color_hover = _to_color(border_color_hover, raised=False)
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')

        # auto-registration
        context.ui._append(self)

        # surface
        self._surface = None
        self._surface_rect = None

        # position et taille
        self._radius = int(min(540, max(3, radius)))
        self._center = (int(x), int(y))
        diameter = self._radius * 2
        self._rect = pygame.Rect(x - self._radius, y - self._radius, diameter, diameter)
        self._local_center = (self._radius, self._radius)

        # background
        self._filling = filling
        self._filling_hover = filling_hover
        self._filling_color = filling_color
        self._filling_color_hover = filling_color_hover if filling_color_hover is not None else filling_color

        # Image
        self._icon_keep_ratio = icon_keep_ratio
        self._icon_scale_ratio = icon_scale_ratio

        self._icon = None
        self._icon_rect = None
        if icon is not None:
            iwidth, iheight = icon.get_size()
            
            if self._icon_keep_ratio:
                width_ratio = (self._radius * self._icon_scale_ratio) / iwidth
                height_ratio = (self._radius * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = min(iwidth, self._radius * self._icon_scale_ratio)
                iheight = min(iheight, self._radius * self._icon_scale_ratio)
            
            self._icon = pygame.transform.smoothscale(icon, (iwidth, iheight))
            self._icon_rect = self._icon.get_rect(center=self._rect.center)

        self._icon_hover = self._icon
        self._icon_hover_rect = self._icon_rect
        if icon_hover is not None:
            iwidth, iheight = icon_hover.get_size()
            
            if self._icon_keep_ratio:
                width_ratio = (self._radius * self._icon_scale_ratio) / iwidth
                height_ratio = (self._radius * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = min(iwidth, self._radius * self._icon_scale_ratio)
                iheight = min(iheight, self._radius * self._icon_scale_ratio)
            
            self._icon_hover = pygame.transform.smoothscale(icon_hover, (iwidth, iheight))
            self._icon_hover_rect = self._icon_hover.get_rect(center=self._rect.center)

        # texte
        self._text = text
        self._font = font
        self._font_path = font_path
        self._font_size = font_size
        self._font_color = font_color
        self._font_color_hover = font_color_hover if font_color_hover is not None else font_color

        self._text_object = None
        self._text_object_hover = None
        self._text_object_rect = None
        self._text_blit = False

        if self._text is not None:
            if self._font_size is None:
                self._font_size = max(3, int(self._radius * 0.75))

            if self._font is None:
                try:
                    self._font = pygame.font.Font(self._font_path, self._font_size)
                except Exception as _:
                    self._font = pygame.font.Font(None, self._font_size)

            self._text_object = self._font.render(self._text, True, self._font_color)
            self._text_object_hover = self._font.render(self._text, True, self._font_color_hover)
            self._text_object_rect = self._text_object.get_rect(center=self._local_center)
            self._text_blit = True

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_color_hover = border_color_hover if border_color_hover is not None else border_color

        # effet de survol
        self._scale_ratio = 1.0
        self._last_scale_ratio = 1.0
        self._hover_scale_ratio = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # action de clique
        self._callback = callback

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = 0

        # préchargement
        self._preloaded = {
            "default": self.load_default(),
            "hover": self.load_hover(),
        }

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
        """Vérifie que le bouton soit survolé"""
        return context.ui.get_hovered() == self
    
    @property
    def hovered(self) -> bool:
        """Vérifie que le bouton soit survolé"""
        return context.ui.hovered_object == self
    
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le bouton (distance au centre <= rayon)"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        dx = mouse_pos[0] - self._center[0]
        dy = mouse_pos[1] - self._center[1]
        return dx * dx + dy * dy <= self._radius * self._radius

    # ======================================== DESSIN DU BOUTON ========================================
    def load_default(self) -> pygame.Surface:
        """Génère la surface par défaut du bouton"""
        diameter = self._radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        if self._filling:
            pygame.draw.circle(surface, self._filling_color, self._local_center, self._radius)
        if self._icon is not None:
            surface.blit(self._icon, self._icon_rect)
        if self._text_blit:
            surface.blit(self._text_object, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.circle(surface, self._border_color_hover, self._local_center, self._radius, self._border_width)
        return surface

    def load_hover(self) -> pygame.Surface:
        """Génère la surface survolée du bouton"""
        diameter = self._radius * 2
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        if self._filling_hover:
            pygame.draw.circle(surface, self._filling_color_hover, self._local_center, self._radius)
        if self._icon_hover is not None:
            surface.blit(self._icon_hover, self._icon_hover_rect)
        if self._text_blit:
            surface.blit(self._text_object_hover, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.circle(surface, self._border_color_hover, self._local_center, self._radius, self._border_width)
        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        if not self._visible:
            return
        # Calcul du ratio de taille
        target_ratio = self._hover_scale_ratio if self.hovered else 1.0
        if self._hover_scale_duration > 0:
            diff = target_ratio - self._scale_ratio
            step = diff * min(context.time.dt / self._hover_scale_duration, 1.0)
            self._scale_ratio += step
        else:
            self._scale_ratio = target_ratio

        # Redimensionnement
        surface = self._preloaded["hover" if self.hovered else "default"]
        surface_rect = surface.get_rect()
        if self._last_scale_ratio != self._scale_ratio:
            self._surface = pygame.transform.smoothscale(surface, (surface_rect.width * self._scale_ratio, surface_rect.height * self._scale_ratio))
        else:
            self._surface = surface
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
        if self.callback is not None and not up:
            self.callback()

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass