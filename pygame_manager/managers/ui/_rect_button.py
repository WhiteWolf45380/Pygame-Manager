# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class RectButtonObject:
    """
    Object de l'interface : Bouton
    
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1, 
            height: Real = -1,

            filling: bool = True,
            filling_hover: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color = None,

            icon: pygame.Surface = None,
            icon_hover: pygame.Surface = None,

            text: str = None,
            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color : pygame.Color = (0, 0, 0, 255),
            font_color_hover : pygame.Color = None,

            border_width : int = 0,
            border_color : pygame.Color = (0, 0, 0, 255),
            border_radius: int = 0,

            hover_scale_ratio: float = 1.0,
            hover_scale_duration: float = 0.0,

            callback: callable = lambda: None,

            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée de la gauche
            y (Real) : coordonnée du haut
            width (Real) : largeur
            height (Real) : hauteur

            filling (bool, optional) : remplissage
            filling_color (Color, optional) : couleur de fond
            filling_color_hover (Color, optional) : couleur de fond lors du survol
            icon (Surface, optional) : image de fond

            text (str, optional) : texte du boutton
            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_radius (int, optional) : rayon d'arrondissement des coins

            hover_scale_ratio (float, optional) : facteur de redimensionnement lors du survol
            hover_scale_duration (float, optional) : durée de redimensionnement (en secondes)

            callback (callable, optional) : action en cas de pression du bouton
            panel (object, optional) : panel maître pour affichage automatique sur la surface
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        if not isinstance(filling_hover, bool): _raise_error(self, '__init__', 'Invalid filling_hover argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        if icon is not None and not isinstance(icon, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon argument')
        if text is not None and not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if font_size is not None and not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        context.ui._append(self)

        # surface
        self._surface = None
        self._surface_rect = None

        # position et taille
        width = min(1920, max(5, width))
        height = min(1080, max(5, height))
        self._rect = pygame.Rect(x, y, width, height)

        # background
        self._filling = filling
        self._filling_hover = filling_hover
        self._filling_color = filling_color
        self._filling_color_hover = filling_color_hover

        # image
        self._icon = None
        self._icon_rect = None
        if icon is not None:
            iwidth, iheight = icon.get_size()
            iwidth = min(iwidth, width * 0.8)
            iheight = min(iheight, height * 0.8)
            self._icon = pygame.transform.smoothscale(icon, (iwidth, iheight))
            self._icon_rect = self._icon.get_rect(center=self._rect.center)

        self._icon_hover = self._icon
        self._icon_hover_rect = self._icon_rect
        if icon_hover is not None:
            iwidth, iheight = icon_hover.get_size()
            iwidth = min(iwidth, width * 0.8)
            iheight = min(iheight, height * 0.8)
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

        if self._text is not None: # génération
            if self._font_size is None: # taille de police auto
                self._font = max(3, int(self._rect.height * 0.6))

            if self._font is None: # chargement de la police
                try:
                    self._font = pygame.font.Font(self._font_path, self._font_size)
                except Exception as _:
                    self._font = pygame.font.Font(None, self._font_size)

            self._text_object = self._font.render(self._text, 1, self._font_color)
            self._text_object_hover = self._font.render(self._text, 1, self._font_color_hover)
            self._text_object_rect = self._text_object.get_rect(center=self._rect.center)
            self._text_blit = True

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_radius = max(0, border_radius)
        
        # effet de survol
        self._hover_scale_ratio = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # action de clique
        self._callback = callback

        # panel maître
        self._panel = panel if panel in context.panels else None
        self._zorder = zorder

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
        """Renvoie le rect pygame"""
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
        return context.ui.hovered_object == self
    
    @property
    def hovered(self) -> bool:
        """Vérifie que le bouton soit survolé"""
        return context.ui.hovered_object == self
    
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le bouton"""
        if self._panel is not None:
            mouse_pos = self._panel.mouse_pos
        else:
            mouse_pos = context.screen.get_mouse_pos()
        return self._rect.collidepoint(mouse_pos)
    
    # ======================================== DESSIN DU BOUTON ========================================
    def load_default(self) -> dict[pygame.Surface]:
        """Renvoie la surface par défaut du bouton'"""
        default = pygame.Surface((self._rect.width, self._rect.height))
        if self._filling:
            pygame.draw.rect(default, self._filling_color, self._rect, border_radius=self._border_radius)
        if self._icon is not None:
            default.blit(self._icon, self._icon_rect)
        if self._text_blit:
            default.blit(self._text_object, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.rect(default, self._border_color, self._rect, border_radius=self._border_radius)
        return default

    def load_hover(self) -> dict[pygame.Surface]:
        """Renvoie la surface survolée du bouton'"""
        hover = pygame.Surface((self._rect.width, self._rect.height))
        if self._filling_hover:
            pygame.draw.rect(hover, self._filling_color_hover, self._rect, border_radius=self._border_radius)
        if self._icon_hover is not None:
            hover.blit(self._icon_hover, self._icon_hover_rect)
        if self._text_blit:
            hover.blit(self._text_object_hover, self._text_object_rect)
        if self._border_width > 0:
            pygame.draw.rect(hover, self._border_color, self._rect, border_radius=self._border_radius)
        return hover

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        self._surface = self._preloaded["hover" if self.hovered else "default"]
        self._surface_rect = self._surface.get_rect(center=self._rect.center)

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self.panel, 'surface'):
            surface = self._panel.surface
        
        surface.blit(self._surface, self._surface_rect)

    def left_click(self, up: bool = False):
        """Clic gauche"""
        if self.callback is not None and not up:
            self.callback()

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass