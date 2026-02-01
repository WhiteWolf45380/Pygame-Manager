# ======================================== IMPORTS ========================================
from ._core import *
from ...context import ui, screen, time, menus

# ======================================== OBJET ========================================
class TextCaseObject:
    """
    Object de l'interface : Zone de texte

    Permet la saisie de texte par l'utilisateur.
    Supporte le focus, le cursor clignotant, et les états visuels default / hover / focus.
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1,
            height: Real = -1,

            text: str = "",
            placeholder: str = None,
            max_length: int = None,

            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color: pygame.Color = (0, 0, 0, 255),
            font_color_placeholder: pygame.Color = (180, 180, 180, 255),

            filling: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color = None,
            filling_color_focus: pygame.Color = None,

            border_width: int = 1,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_color_hover: pygame.Color = None,
            border_color_focus: pygame.Color = None,
            border_radius: int = 0,

            cursor_color: pygame.Color = (0, 0, 0, 255),
            cursor_blink_rate: float = 0.5,

            padding: int = 5,

            callback: callable = lambda text: None,
            menu: object = None
        ):
        """
        Args:
            x (Real) : coordonnée de la gauche
            y (Real) : coordonnée du haut
            width (Real) : largeur
            height (Real) : hauteur

            text (str, optional) : texte initial
            placeholder (str, optional) : texte affiché quand la zone est vide
            max_length (int, optional) : nombre maximum de caractères

            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur du texte
            font_color_placeholder (Color, optional) : couleur du placeholder

            filling (bool, optional) : remplissage
            filling_color (Color, optional) : couleur de fond
            filling_color_hover (Color, optional) : couleur de fond lors du survol
            filling_color_focus (Color, optional) : couleur de fond en focus

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_color_hover (Color, optional) : couleur de la bordure lors du survol
            border_color_focus (Color, optional) : couleur de la bordure en focus
            border_radius (int, optional) : rayon d'arrondissement des coins

            cursor_color (Color, optional) : couleur du cursor
            cursor_blink_rate (float, optional) : vitesse du clignotement du cursor (secondes par demi-cycle)

            padding (int, optional) : marge interne du texte

            callback (callable, optional) : appelé à chaque modification du texte, reçoit le texte actuel
            menu (object, optional) : menu maître
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if placeholder is not None and not isinstance(placeholder, str): _raise_error(self, '__init__', 'Invalid placeholder argument')
        if max_length is not None and (not isinstance(max_length, int) or max_length <= 0): _raise_error(self, '__init__', 'Invalid max_length argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if font_size is not None and not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_placeholder = _to_color(font_color_placeholder, method='__init__')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        filling_color_focus = _to_color(filling_color_focus, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        border_color_hover = _to_color(border_color_hover, raised=False)
        border_color_focus = _to_color(border_color_focus, raised=False)
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        cursor_color = _to_color(cursor_color, method='__init__')
        if not isinstance(cursor_blink_rate, Real) or cursor_blink_rate <= 0: _raise_error(self, '__init__', 'Invalid cursor_blink_rate argument')
        if not isinstance(padding, int) or padding < 0: _raise_error(self, '__init__', 'Invalid padding argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if menu is not None and not isinstance(menu, str): _raise_error(self, '__init__', 'Invalid menu argument')

        # auto-registration
        ui._append(self)

        # zorder
        self._zorder = 0

        # surface
        self._surface = None
        self._surface_rect = None

        # position et taille
        width = min(1920, max(5, width))
        height = min(1080, max(5, height))
        self._rect = pygame.Rect(x, y, width, height)
        self._local_rect = pygame.Rect(0, 0, width, height)

        # texte
        self._text = text
        self._placeholder = placeholder
        self._max_length = max_length
        self._cursor_pos = len(text)

        # police
        self._font_path = font_path
        self._font_size = font_size if font_size is not None else max(3, int(height * 0.6))
        self._font_color = font_color
        self._font_color_placeholder = font_color_placeholder

        if font is None:
            try:
                self._font = pygame.font.Font(self._font_path, self._font_size)
            except Exception as _:
                self._font = pygame.font.Font(None, self._font_size)
        else:
            self._font = font

        # background
        self._filling = filling
        self._filling_color = filling_color
        self._filling_color_hover = filling_color_hover
        self._filling_color_focus = filling_color_focus

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_color_hover = border_color_hover if border_color_hover is not None else border_color
        self._border_color_focus = border_color_focus if border_color_focus is not None else border_color
        self._border_radius = max(0, border_radius)

        # cursor
        self._cursor_color = cursor_color
        self._cursor_blink_rate = float(cursor_blink_rate)
        self._cursor_timer = 0.0
        self._cursor_visible = True

        # padding
        self._padding = padding

        # callback
        self._callback = callback

        # menu maître
        self._menu = menu if menu in menus else None

        # paramètres dynamiques
        self._visible = True
        self._focused = False

    # ======================================== GETTERS ========================================
    @property
    def zorder(self) -> int:
        """Renvoie le zorder"""
        return self._zorder

    @property
    def menu(self) -> object:
        """Renvoie le menu maître"""
        return self._menu

    @property
    def visible(self) -> bool:
        """Vérifie la visibilité"""
        return self._visible

    @property
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy()

    @property
    def text(self) -> str:
        """Renvoie le texte actuel"""
        return self._text

    @property
    def focused(self) -> bool:
        """Vérifie que la zone soit en focus"""
        return self._focused

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

    @text.setter
    def text(self, value: str):
        """Fixe le texte"""
        if not isinstance(value, str):
            _raise_error(self, 'set_text', 'Invalid value argument')
        if self._max_length is not None:
            value = value[:self._max_length]
        self._text = value
        self._cursor_pos = len(value)
        self._callback(self._text)

    @callback.setter
    def callback(self, callback: callable):
        """Fixe le callback"""
        if not callable(callback):
            _raise_error(self, 'set_callback', 'Invalid callback argument')
        self._callback = callback

    # ======================================== PREDICATS ========================================
    def is_hovered(self) -> bool:
        """Vérifie que la zone soit survolée"""
        return ui.hovered_object == self

    @property
    def hovered(self) -> bool:
        """Vérifie que la zone soit survolée"""
        return ui.hovered_object == self

    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur la zone"""
        mouse_pos = self._menu.mouse_pos if self._menu is not None else screen.get_mouse_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== INTERACTION ========================================
    def focus(self):
        """Met la zone en focus"""
        self._focused = True
        pygame.key.start_text_input()

    def unfocus(self):
        """Retire le focus"""
        self._focused = False
        pygame.key.stop_text_input()

    def handle_event(self, event: pygame.event.Event):
        """
        Traite un événement pygame (à appeler depuis la boucle d'événements principale)

        Args:
            event (pygame.event.Event) : événement à traiter
        """
        if not self._focused:
            return

        if event.type == pygame.TEXTINPUT:
            if self._max_length is not None and len(self._text) >= self._max_length:
                return
            self._text = self._text[:self._cursor_pos] + event.text + self._text[self._cursor_pos:]
            self._cursor_pos += len(event.text)
            self._callback(self._text)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self._cursor_pos > 0:
                    self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
                    self._cursor_pos -= 1
                    self._callback(self._text)
            elif event.key == pygame.K_DELETE:
                if self._cursor_pos < len(self._text):
                    self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
                    self._callback(self._text)
            elif event.key == pygame.K_LEFT:
                self._cursor_pos = max(0, self._cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self._cursor_pos = 0
            elif event.key == pygame.K_END:
                self._cursor_pos = len(self._text)
            elif event.key == pygame.K_RETURN:
                self.unfocus()

    # ======================================== DESSIN ========================================
    def _get_cursor_x(self) -> int:
        """Calcule la position x du cursor en pixels (coordonnées locales)"""
        if self._cursor_pos == 0:
            return self._padding
        text_before = self._text[:self._cursor_pos]
        rendered = self._font.render(text_before, True, self._font_color)
        return self._padding + rendered.get_width()

    def _render_frame(self) -> pygame.Surface:
        """Génère la surface pour la frame courante selon l'état actuel"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)

        # couleurs selon l'état
        if self._focused:
            bg_color = self._filling_color_focus if self._filling_color_focus is not None else self._filling_color
            bd_color = self._border_color_focus
        elif self.hovered:
            bg_color = self._filling_color_hover if self._filling_color_hover is not None else self._filling_color
            bd_color = self._border_color_hover
        else:
            bg_color = self._filling_color
            bd_color = self._border_color

        # remplissage
        if self._filling:
            pygame.draw.rect(surface, bg_color, self._local_rect, border_radius=self._border_radius)

        # texte ou placeholder
        if self._text:
            text_surface = self._font.render(self._text, True, self._font_color)
        elif self._placeholder is not None:
            text_surface = self._font.render(self._placeholder, True, self._font_color_placeholder)
        else:
            text_surface = None

        if text_surface is not None:
            text_y = (self._rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (self._padding, text_y))

        # cursor
        if self._focused and self._cursor_visible:
            cursor_x = self._get_cursor_x()
            pygame.draw.line(surface, self._cursor_color, (cursor_x, self._padding), (cursor_x, self._rect.height - self._padding), 2)

        # bordure
        if self._border_width > 0:
            pygame.draw.rect(surface, bd_color, self._local_rect, self._border_width, border_radius=self._border_radius)

        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        # clignotement du cursor
        if self._focused:
            self._cursor_timer += time.dt
            if self._cursor_timer >= self._cursor_blink_rate:
                self._cursor_visible = not self._cursor_visible
                self._cursor_timer = 0.0
        else:
            self._cursor_visible = True
            self._cursor_timer = 0.0

        # pas de preloading : le texte change, on re-render chaque frame
        self._surface = self._render_frame()
        self._surface_rect = self._surface.get_rect(topleft=self._rect.topleft)

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return

        surface = screen.surface
        if self._menu is not None and hasattr(self._menu, 'surface'):
            surface = self._menu.surface

        surface.blit(self._surface, self._surface_rect)