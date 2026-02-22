# ======================================== IMPORTS ========================================
from ._core import *
from typing import Any

# ======================================== OBJET ========================================
class InputButtonObject:
    """
    Object de l'interface : Bouton de saisie de touche

    Trois états visuels :
        - normal   : affiche la touche assignée
        - hovered  : affiche la touche assignée (couleur hover)
        - selected : en attente d'une entrée, affiche "[ ? ]"

    Au clic, passe en état selected et capture la prochaine touche pressée.
    Échap en état selected assigne None et repasse en normal.
    Le callback reçoit la touche capturée (int pygame key code, ou None).

    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1,
            height: Real = -1,
            anchor: str = "topleft",

            key: int = None,
            key_names: dict = None,

            filling: bool = True,
            filling_color: pygame.Color = (55, 55, 55, 255),
            filling_color_hover: pygame.Color = None,
            filling_color_selected: pygame.Color = None,

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_color_hover: pygame.Color = None,
            border_color_selected: pygame.Color = None,
            border_radius: int = 0,

            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color: pygame.Color = (220, 220, 220, 255),
            font_color_hover: pygame.Color = None,
            font_color_selected: pygame.Color = None,

            text_waiting: str = "[ ? ]",

            hover_scale_ratio: float = 1.0,
            hover_scale_duration: float = 0.0,

            id: Any = None,
            callback: callable = lambda key: None,
            callback_give_id: bool = False,

            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real)                                 : coordonnée x
            y (Real)                                 : coordonnée y
            width (Real)                             : largeur
            height (Real)                            : hauteur
            anchor (str, optional)                   : point d'ancrage du rectangle

            key (int, optional)                      : touche initiale assignée (pygame key code)
            key_names (dict, optional)               : dictionnaire {int: str} pour nommer les touches
                                                       (ex: {pygame.K_SPACE: "Espace"})
                                                       si None, utilise pygame.key.name()

            filling (bool, optional)                 : remplissage du fond
            filling_color (Color, optional)          : couleur de fond en état normal
            filling_color_hover (Color, optional)    : couleur de fond au survol
            filling_color_selected (Color, optional) : couleur de fond en attente de saisie

            border_width (int, optional)                 : épaisseur de la bordure
            border_color (Color, optional)               : couleur de la bordure en état normal
            border_color_hover (Color, optional)         : couleur de la bordure au survol
            border_color_selected (Color, optional)      : couleur de la bordure en attente de saisie
            border_radius (int, optional)                : rayon d'arrondissement des coins

            font (Font, optional)                        : police du texte
            font_path (str, optional)                    : chemin vers la police
            font_size (int, optional)                    : taille de la police (auto si None)
            font_color (Color, optional)                 : couleur du texte en état normal
            font_color_hover (Color, optional)           : couleur du texte au survol
            font_color_selected (Color, optional)        : couleur du texte en attente de saisie

            text_waiting (str, optional)                 : texte affiché en état selected (défaut "[ ? ]")

            hover_scale_ratio (float, optional)          : facteur de redimensionnement au survol
            hover_scale_duration (float, optional)       : durée de l'animation de redimensionnement (secondes)

            id (Any, optional)                           : id du bouton
            callback (callable, optional)                : appelé avec la touche capturée (int ou None)
            callback_give_id (bool, optional)            : passe également l'id en argument du callback

            panel (object, optional)                     : panel maître
            zorder (int, optional)                       : ordre d'affichage
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if key is not None and not isinstance(key, int): _raise_error(self, '__init__', 'Invalid key argument')
        if key_names is not None and not isinstance(key_names, dict): _raise_error(self, '__init__', 'Invalid key_names argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        filling_color_selected = _to_color(filling_color_selected, raised=False)
        border_color = _to_color(border_color, method='__init__')
        border_color_hover = _to_color(border_color_hover, raised=False)
        border_color_selected = _to_color(border_color_selected, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if font_size is not None and not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        font_color_selected = _to_color(font_color_selected, raised=False)
        if not isinstance(text_waiting, str): _raise_error(self, '__init__', 'Invalid text_waiting argument')
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if not isinstance(callback_give_id, bool): _raise_error(self, '__init__', 'Invalid callback_give_id argument')
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

        # touche
        self._key = key
        self._key_names = key_names or {}

        # couleurs de fond
        self._filling = filling
        self._filling_color          = filling_color
        self._filling_color_hover    = filling_color_hover    if filling_color_hover    is not None else filling_color
        self._filling_color_selected = filling_color_selected if filling_color_selected is not None else filling_color

        # bordure
        self._border_width          = max(0, border_width)
        self._border_color          = border_color
        self._border_color_hover    = border_color_hover    if border_color_hover    is not None else border_color
        self._border_color_selected = border_color_selected if border_color_selected is not None else border_color
        self._border_radius         = max(0, border_radius)

        # police
        self._font_size = font_size or max(3, int(height * 0.5))
        if font is None:
            try:    self._font = pygame.font.Font(font_path, self._font_size)
            except: self._font = pygame.font.Font(None, self._font_size)
        else:
            self._font = font

        self._font_color          = font_color
        self._font_color_hover    = font_color_hover    if font_color_hover    is not None else font_color
        self._font_color_selected = font_color_selected if font_color_selected is not None else font_color
        self._text_waiting        = text_waiting

        # hover scale
        self._scale_ratio        = 1.0
        self._last_scale_ratio   = 1.0
        self._hover_scale_ratio  = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # callback
        self._id              = id
        self._callback        = callback
        self._callback_give_id = callback_give_id

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # état
        self._selected = False
        self._visible  = True

    # ======================================== HELPERS ========================================
    def _key_label(self) -> str:
        """Renvoie le nom affiché de la touche assignée"""
        if self._key is None:
            return "—"
        if self._key in self._key_names:
            return self._key_names[self._key]
        name = pygame.key.name(self._key)
        return name.upper() if len(name) == 1 else name.capitalize()

    def _render_surface(self, text: str, bg: pygame.Color, bd: pygame.Color, fc: pygame.Color) -> pygame.Surface:
        """Génère une surface pour un état donné"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        local = pygame.Rect(0, 0, self._rect.width, self._rect.height)
        if self._filling:
            pygame.draw.rect(surface, bg, local, border_radius=self._border_radius)
        label = self._font.render(text, True, fc)
        surface.blit(label, label.get_rect(center=local.center))
        if self._border_width > 0:
            pygame.draw.rect(surface, bd, local, self._border_width, border_radius=self._border_radius)
        return surface

    def _build_surfaces(self) -> dict:
        """Pré-calcule les trois surfaces d'état"""
        label = self._key_label()
        return {
            "normal":   self._render_surface(label,             self._filling_color,          self._border_color,          self._font_color),
            "hovered":  self._render_surface(label,             self._filling_color_hover,    self._border_color_hover,    self._font_color_hover),
            "selected": self._render_surface(self._text_waiting, self._filling_color_selected, self._border_color_selected, self._font_color_selected),
        }

    # ======================================== GETTERS ========================================
    @property
    def zorder(self) -> int:
        return self._zorder

    @property
    def panel(self) -> object:
        return self._panel

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def rect(self) -> pygame.Rect:
        return self._rect.copy()

    @property
    def key(self) -> int | None:
        """Renvoie la touche actuellement assignée"""
        return self._key

    @property
    def selected(self) -> bool:
        """Vrai si le bouton est en attente de saisie"""
        return self._selected

    @property
    def callback(self) -> callable:
        return self._callback

    # ======================================== SETTERS ========================================
    @zorder.setter
    def zorder(self, value: int):
        if not isinstance(value, int): _raise_error(self, 'zorder', 'Invalid zorder argument')
        self._zorder = value

    @visible.setter
    def visible(self, value: bool):
        if not isinstance(value, bool): _raise_error(self, 'visible', 'Invalid value argument')
        self._visible = value

    @key.setter
    def key(self, value: int | None):
        """Assigne une touche manuellement"""
        if value is not None and not isinstance(value, int): _raise_error(self, 'key', 'Invalid key argument')
        self._key = value

    @callback.setter
    def callback(self, callback: callable):
        if not callable(callback): _raise_error(self, 'callback', 'Invalid callback argument')
        self._callback = callback

    # ======================================== PREDICATS ========================================
    def is_hovered(self) -> bool:
        return context.ui.get_hovered() == self

    @property
    def hovered(self) -> bool:
        return context.ui.get_hovered() == self

    def collidemouse(self) -> bool:
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== INTERACTION ========================================
    def _assign(self, key: int | None):
        """Assigne la touche, repasse en normal et déclenche le callback"""
        self._key      = key
        self._selected = False
        if self._callback_give_id:
            self._callback(key, id=self._id)
        else:
            self._callback(key)

    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        context.ui._remove(self)

    def update(self):
        if not self._visible:
            return

        # Capture clavier si selected
        if self._selected:
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_ESCAPE:
                    self._assign(None)
                else:
                    self._assign(event.key)
                break  # une seule touche à la fois

        # Calcul du scale
        target_ratio = self._hover_scale_ratio if (self.hovered and not self._selected) else 1.0
        if self._hover_scale_duration > 0:
            diff = target_ratio - self._scale_ratio
            self._scale_ratio += diff * min(context.time.dt / self._hover_scale_duration, 1.0)
        else:
            self._scale_ratio = target_ratio

        # Choix de l'état visuel
        surfaces = self._build_surfaces()
        if self._selected:
            base = surfaces["selected"]
        elif self.hovered:
            base = surfaces["hovered"]
        else:
            base = surfaces["normal"]

        # Redimensionnement
        if self._last_scale_ratio != self._scale_ratio:
            w = int(base.get_width()  * self._scale_ratio)
            h = int(base.get_height() * self._scale_ratio)
            self._surface = pygame.transform.smoothscale(base, (w, h))
            self._last_scale_ratio = self._scale_ratio
        else:
            self._surface = base

        self._surface_rect = self._surface.get_rect(center=self._rect.center)

    def draw(self):
        if not self._visible:
            return
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        surface.blit(self._surface, self._surface_rect)

    def left_click(self, up: bool = False):
        """Clic gauche : active la saisie"""
        if not up and not self._selected:
            self._selected = True

    def right_click(self, up: bool = False):
        """Clic droit : annule la saisie en cours"""
        if not up and self._selected:
            self._assign(None)