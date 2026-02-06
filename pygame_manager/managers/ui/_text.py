# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class TextObject:
    """
    Object de l'interface : Texte
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            text: str = "",

            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = 24,
            font_color: pygame.Color = (0, 0, 0, 255),
            antialias: bool = True,

            background: pygame.Color = None,

            anchor: str = "topleft",

            auto: bool = True,
            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée x
            y (Real) : coordonnée y
            text (str) : texte à afficher

            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur du texte
            antialias (bool, optional) : antialiasing du texte

            anchor (str, optional) : point d'ancrage ("topleft", "center", "midtop", etc.)

            auto (bool, optional) : enregistrement automatique pour draw
            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        if not isinstance(antialias, bool): _raise_error(self, '__init__', 'Invalid antialias argument')
        if background is not None: background = _to_color(background)
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(auto, bool): _raise_error(self, '__init__', 'Invalid auto argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        if auto:
            context.ui._append(self)

        # position
        self._x = x
        self._y = y
        self._anchor = anchor

        # texte
        self._text = text
        self._font_color = font_color
        self._antialias = antialias

        # police
        if font is None:
            try:
                self._font = pygame.font.Font(font_path, font_size)
            except Exception as _:
                self._font = pygame.font.Font(None, font_size)
        else:
            self._font = font

        self._background = background

        # surface
        self._surface = None
        self._rect = None
        self._render()

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = zorder

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
    def text(self) -> str:
        """Renvoie le texte"""
        return self._text

    @property
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy() if self._rect else pygame.Rect(self._x, self._y, 0, 0)

    @property
    def surface(self) -> pygame.Surface:
        """Renvoie la surface rendue"""
        return self._surface

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

    @text.setter
    def text(self, value: str):
        """Fixe le texte et re-render"""
        if not isinstance(value, str):
            _raise_error(self, 'set_text', 'Invalid value argument')
        self._text = value
        self._render()

    # ======================================== RENDU ========================================
    def _render(self):
        """Génère la surface du texte"""
        self._surface = self._font.render(self._text, self._antialias, self._font_color, self._background)
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_position(self, x: Real, y: Real):
        """Modifie la position"""
        self._x = x
        self._y = y
        if self._surface:
            self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_color(self, color: pygame.Color):
        """Modifie la couleur et re-render"""
        self._font_color = _to_color(color, method='set_color')
        self._render()

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le bouton"""
        if self._panel is not None:
            mouse_pos = self._panel.mouse_pos
        else:
            mouse_pos = context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame (vide pour TextObject)"""
        pass

    def draw(self):
        """Dessin par frame"""
        if not self._visible or not self._surface:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        
        surface.blit(self._surface, self._rect)