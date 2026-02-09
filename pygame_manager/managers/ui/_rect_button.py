# ======================================== IMPORTS ========================================
from ._core import *
from typing import Any

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
            anchor: str = "topleft",

            filling: bool = True,
            filling_hover: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color | None = None,

            icon: pygame.Surface = None,
            icon_hover: pygame.Surface = None,
            icon_keep_ratio: bool = True,
            icon_scale_ratio: float = 0.8,

            text: str = None,
            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_size_ratio_limit: float= 0.8,
            font_color : pygame.Color = (0, 0, 0, 255),
            font_color_hover : pygame.Color = None,

            bold: bool = False,
            italic: bool = False,
            underline: bool = False,

            border_width : int = 0,
            border_color : pygame.Color = (0, 0, 0, 255),
            border_color_hover: pygame.Color | None = None,
            border_radius: int = 0,

            hover_scale_ratio: float = 1.0,
            hover_scale_duration: float = 0.0,

            id: Any = None,
            callback: callable = lambda: None,
            callback_give_id: bool = False,

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
            icon_hover (Surface, optional) : image de fond lors du survol
            icon_keep_ratio (Surface, optional) : pas de déformation, ratio_locker
            icon_scale_ratio (Surface, optional) : ratio maximum par rapport aux dimensions du bouton
 
            text (str, optional) : texte du boutton
            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_size_ratio_limit (float, optional) : limite de la taille du texte par rapport à la largeur du boutton
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol

            bold (bool, optional): texte en gras
            italic (bool, optional): texte en italique
            underline (bool, optional): texte souligné

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_color_hover (Color, optional) : couleur de la bordure lors du survol
            border_radius (int, optional) : rayon d'arrondissement des coins

            hover_scale_ratio (float, optional) : facteur de redimensionnement lors du survol
            hover_scale_duration (float, optional) : durée de redimensionnement (en secondes)

            id (Any, optional) : id du bouton
            callback (callable, optional) : action en cas de pression du bouton
            callback_give_name (bool, optional) : passe l'id du bouton en argument du callback

            panel (object, optional) : panel maître pour affichage automatique sur la surface
            zorder (int, optional) : ordre d'affichage
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
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
        if not isinstance(font_size_ratio_limit, (float, int)): _raise_error(self, '__init__', 'Invalid font_size_ratio_limit argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        if not isinstance(bold, bool): _raise_error(self, '__init__', 'Invalid bold argument')
        if not isinstance(italic, bool): _raise_error(self, '__init__', 'Invalid italic argument')
        if not isinstance(underline, bool): _raise_error(self, '__init__', 'Invalid underline argument')
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if not isinstance(callback_give_id, bool): _raise_error(self, "__init__", 'Invalid callback_give_id argument')
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
        self._rect = pygame.Rect(0, 0, width, height)
        setattr(self._rect, anchor, (x, y))

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
                width_ratio = (width * self._icon_scale_ratio) / iwidth
                height_ratio = (height * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = min(iwidth, width * self._icon_scale_ratio)
                iheight = min(iheight, height * self._icon_scale_ratio)
            
            self._icon = pygame.transform.smoothscale(icon, (iwidth, iheight))
            self._icon_rect = self._icon.get_rect(center=self._rect.center)

        self._icon_hover = self._icon
        self._icon_hover_rect = self._icon_rect
        if icon_hover is not None:
            iwidth, iheight = icon_hover.get_size()
            
            if self._icon_keep_ratio:
                width_ratio = (width * self._icon_scale_ratio) / iwidth
                height_ratio = (height * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = min(iwidth, width * self._icon_scale_ratio)
                iheight = min(iheight, height * self._icon_scale_ratio)
            
            self._icon_hover = pygame.transform.smoothscale(icon_hover, (iwidth, iheight))
            self._icon_hover_rect = self._icon_hover.get_rect(center=self._rect.center)

        # texte
        self._text = text
        self._font = font
        self._font_path = font_path
        self._font_size = font_size
        self._font_size_ratio_limit = min(1.0, max(0.05, font_size_ratio_limit))
        self._font_color = font_color
        self._font_color_hover = font_color_hover if font_color_hover is not None else font_color

        self._text_object = None
        self._text_object_hover = None
        self._text_object_rect = None
        self._text_blit = False

        self.font_type = None
        if self._text is not None: # génération
            if self._font_size is None: # taille de police auto
                self._font_size = max(3, int(self._rect.height * 0.7))

            self.font_type = "font"
            if self._font is None: # chargement de la police
                try:
                    self._font = pygame.font.Font(self._font_path, self._font_size)
                    self.font_type = "path"
                except Exception as _:
                    self._font = pygame.font.Font(None, self._font_size)
                    self.font_type = "default"

            # Auto ajustement
            test_font_size = self._font_size
            test_font = self._font
            text_render_test = self._font.render(self._text, True, (0, 0, 0))
            while text_render_test.get_width() / self._rect.width > self._font_size_ratio_limit:
                test_font_size -= 1
                if self.font_type == "font":
                    test_font = self._font
                elif self.font_type == "path":
                    test_font = pygame.font.Font(self._font_path, test_font_size)
                else:
                    test_font = pygame.font.Font(None, test_font_size)
                text_render_test = test_font.render(self._text, True, (0, 0, 0))

            self._font_size = test_font_size
            self._font = test_font
            self._font_hover = test_font

            # Génération (classic)
            self._text_object = self._font.render(self._text, 1, self._font_color)

            # Effets
            self._font.set_bold(bold)
            self._font.set_italic(italic)
            self._font.set_underline(underline)
            
            # Génération (hover)
            self._text_object_hover = self._font.render(self._text, 1, self._font_color_hover)

            # Hitbox
            self._text_object_rect = self._text_object.get_rect(center=self._rect.center)
            self._text_blit = True

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_color_hover = border_color_hover if border_color_hover is not None else border_color
        self._border_radius = max(0, border_radius)
        
        # effet de survol
        self._scale_ratio = 1.0
        self._last_scale_ratio = 1.0
        self._hover_scale_ratio = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # action de clique
        self._id = id
        self._callback = callback
        self._callback_give_id = callback_give_id

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
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
        return context.ui.get_hovered() == self
    
    @property
    def hovered(self) -> bool:
        """Vérifie que le bouton soit survolé"""
        return context.ui.get_hovered() == self
    
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le bouton"""
        if self._panel is not None:
            mouse_pos = self._panel.mouse_pos
        else:
            mouse_pos = context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)
    
    # ======================================== DESSIN DU BOUTON ========================================
    def load_default(self) -> dict[pygame.Surface]:
        """Renvoie la surface par défaut du bouton'"""
        default = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        rect = default.get_rect()
        if self._filling:
            pygame.draw.rect(default, self._filling_color, rect, border_radius=self._border_radius)
        if self._icon is not None:
            default.blit(self._icon, self._icon.get_rect(center=rect.center))
        if self._text_blit:
            default.blit(self._text_object, self._text_object.get_rect(center=rect.center))
        if self._border_width > 0:
            pygame.draw.rect(default, self._border_color, rect, self._border_width, border_radius=self._border_radius)
        return default

    def load_hover(self) -> dict[pygame.Surface]:
        """Renvoie la surface survolée du bouton'"""
        hover = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        rect = hover.get_rect()
        if self._filling_hover:
            pygame.draw.rect(hover, self._filling_color_hover, rect, border_radius=self._border_radius)
        if self._icon_hover is not None:
            hover.blit(self._icon_hover, self._icon_hover.get_rect(center=rect.center))
        if self._text_blit:
            hover.blit(self._text_object_hover, self._text_object_hover.get_rect(center=rect.center))
        if self._border_width > 0:
            pygame.draw.rect(hover, self._border_color_hover, rect, self._border_width, border_radius=self._border_radius)
        return hover

    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        """Détruit l'objet"""
        context.ui._remove(self)

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
            if self._callback_give_id:
                self.callback(id=self._id)
            else:
                self.callback()

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass