# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class TextCaseObject:
    """
    Object de l'interface : Zone de texte

    Permet la saisie de texte par l'utilisateur.
    Supporte le focus, le cursor clignotant, et les états visuels default / hover / focus.
    Gestion des entrées entièrement automatique via context.inputs.
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """

    # Délai initial avant répétition (secondes) et intervalle entre répétitions
    _HOLD_INITIAL_DELAY  = 0.4
    _HOLD_REPEAT_INTERVAL = 0.05

    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1,
            height: Real = -1,
            anchor: str = "topleft",

            text: str = "",
            placeholder: str = None,
            max_length: int = None,

            font: pygame.font.Font | str = "bahnschrift",
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

            callback: callable = lambda _: None,
            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée x
            y (Real) : coordonnée y
            width (Real) : largeur
            height (Real) : hauteur
            anchor (str, optional) : point d'ancrage ("topleft", "center", "midtop", etc.)

            text (str, optional) : texte initial
            placeholder (str, optional) : texte affiché quand la zone est vide
            max_length (int, optional) : nombre maximum de caractères

            font (Font | str, optional) : police pygame ou nom de sysfont
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
            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if placeholder is not None and not isinstance(placeholder, str): _raise_error(self, '__init__', 'Invalid placeholder argument')
        if max_length is not None and (not isinstance(max_length, int) or max_length <= 0): _raise_error(self, '__init__', 'Invalid max_length argument')
        if font is not None and not isinstance(font, (str, pygame.font.Font)): _raise_error(self, '__init__', 'Invalid font argument')
        if isinstance(font, str) and font not in pygame.font.get_fonts(): _raise_error(self, '__init__', 'Invalid font argument')
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
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        context.ui._append(self)

        # anchor + position et taille
        width = min(1920, max(5, width))
        height = min(1080, max(5, height))
        self._anchor = anchor
        self._local_rect = pygame.Rect(0, 0, width, height)
        tmp = pygame.Rect(0, 0, width, height)
        setattr(tmp, anchor, (x, y))
        self._rect = tmp

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

        if isinstance(font, pygame.font.Font):
            self._font = font
        else:
            self._sysfont = font if isinstance(font, str) else None
            if self._font_path is not None:
                try:
                    self._font = pygame.font.Font(self._font_path, self._font_size)
                except Exception:
                    if self._sysfont is not None:
                        self._font = pygame.font.SysFont(self._sysfont, self._font_size)
                    else:
                        self._font = pygame.font.Font(None, self._font_size)
            else:
                if self._sysfont is not None:
                    self._font = pygame.font.SysFont(self._sysfont, self._font_size)
                else:
                    self._font = pygame.font.Font(None, self._font_size)

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

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # paramètres dynamiques
        self._visible = True
        self._focused = False

        # scroll horizontal (blit_x du texte : padding si ça rentre, sinon ancré à droite)
        self._text_blit_x = self._padding

        # système de répétition avec cooldown pour backspace/delete
        self._held_action  = None   # 'backspace' | 'delete' | None
        self._held_timer   = 0.0
        self._held_initial = True   # True = on attend le délai initial, False = répétition

        # pré-render
        self._update_text_offset()
        self._surface = self._render_frame()
        self._surface_rect = self._surface.get_rect(topleft=self._rect.topleft)

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
    def text(self) -> str:
        return self._text

    @property
    def focused(self) -> bool:
        return self._focused

    @property
    def callback(self) -> callable:
        return self._callback

    # ======================================== SETTERS ========================================
    @zorder.setter
    def zorder(self, value: int):
        if not isinstance(value, int):
            _raise_error(self, 'set_zorder', 'Invalid zorder argument')
        self._zorder = value

    @visible.setter
    def visible(self, value: bool):
        if not isinstance(value, bool):
            _raise_error(self, 'set_visible', 'Invalid value argument')
        self._visible = value

    @text.setter
    def text(self, value: str):
        if not isinstance(value, str):
            _raise_error(self, 'set_text', 'Invalid value argument')
        if self._max_length is not None:
            value = value[:self._max_length]
        self._text = value
        self._cursor_pos = len(value)
        self._update_text_offset()
        self._callback(self._text)

    @callback.setter
    def callback(self, callback: callable):
        if not callable(callback):
            _raise_error(self, 'set_callback', 'Invalid callback argument')
        self._callback = callback

    def set_position(self, x: Real, y: Real):
        """Modifie la position (selon l'anchor)"""
        setattr(self._rect, self._anchor, (x, y))

    # ======================================== SCROLL TEXTE ========================================
    def _update_text_offset(self):
        """
        Si le texte dépasse la zone disponible, on fixe son bord droit
        sur le bord droit de la cellule (rect.width - padding).
        blit_x = rect.width - padding - total_width  (valeur négative = débordement à gauche)
        Si le texte rentre, blit_x = padding (aligné à gauche).
        """
        available = self._rect.width - 2 * self._padding
        total_width = self._font.size(self._text)[0]
        if total_width <= available:
            self._text_blit_x = self._padding
        else:
            # bord droit du texte = rect.width - padding
            self._text_blit_x = self._rect.width - self._padding - total_width

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
    def focus(self):
        """Met la zone en focus et enregistre les listeners clavier/souris"""
        if self._focused:
            return
        self._focused = True
        pygame.key.start_text_input()
        self._register_input_listeners()

    def unfocus(self):
        """Retire le focus et supprime les listeners clavier/souris"""
        if not self._focused:
            return
        self._focused = False
        self._held_action = None
        pygame.key.stop_text_input()
        self._unregister_input_listeners()

    # ======================================== LISTENERS AUTO ========================================
    def _register_input_listeners(self):
        inp = context.inputs
        inp.add_listener(pygame.TEXTINPUT,    self._on_text_input)
        inp.add_listener(pygame.K_BACKSPACE,  self._on_backspace_down)
        inp.add_listener(pygame.K_BACKSPACE,  self._on_backspace_up,  up=True)
        inp.add_listener(pygame.K_DELETE,     self._on_delete_down)
        inp.add_listener(pygame.K_DELETE,     self._on_delete_up,     up=True)
        inp.add_listener(pygame.K_LEFT,       self._on_left,          repeat=True)
        inp.add_listener(pygame.K_RIGHT,      self._on_right,         repeat=True)
        inp.add_listener(pygame.K_HOME,       self._on_home)
        inp.add_listener(pygame.K_END,        self._on_end)
        inp.add_listener(pygame.K_RETURN,     self.unfocus)
        inp.add_listener(pygame.K_KP_ENTER,   self.unfocus)
        inp.add_listener(pygame.K_ESCAPE,     self.unfocus)
        inp.add_listener(inp.MOUSELEFT,       self._on_click_outside)

    def _unregister_input_listeners(self):
        inp = context.inputs
        inp.remove_listener(pygame.TEXTINPUT,   self._on_text_input)
        inp.remove_listener(pygame.K_BACKSPACE,  self._on_backspace_down)
        inp.remove_listener(pygame.K_BACKSPACE,  self._on_backspace_up)
        inp.remove_listener(pygame.K_DELETE,     self._on_delete_down)
        inp.remove_listener(pygame.K_DELETE,     self._on_delete_up)
        inp.remove_listener(pygame.K_LEFT,       self._on_left)
        inp.remove_listener(pygame.K_RIGHT,      self._on_right)
        inp.remove_listener(pygame.K_HOME,       self._on_home)
        inp.remove_listener(pygame.K_END,        self._on_end)
        inp.remove_listener(pygame.K_RETURN,     self.unfocus)
        inp.remove_listener(pygame.K_KP_ENTER,   self.unfocus)
        inp.remove_listener(pygame.K_ESCAPE,     self.unfocus)
        inp.remove_listener(inp.MOUSELEFT,       self._on_click_outside)

    # ---- callbacks internes ----

    def _on_text_input(self):
        event = context.inputs._current_event
        if event is None or not hasattr(event, 'text'):
            return
        if self._max_length is not None and len(self._text) >= self._max_length:
            return
        self._text = self._text[:self._cursor_pos] + event.text + self._text[self._cursor_pos:]
        self._cursor_pos += len(event.text)
        self._update_text_offset()
        self._callback(self._text)

    # backspace : pression initiale + démarrage du cooldown
    def _on_backspace_down(self):
        self._do_backspace()
        self._held_action  = 'backspace'
        self._held_timer   = 0.0
        self._held_initial = True

    def _on_backspace_up(self):
        if self._held_action == 'backspace':
            self._held_action = None

    # delete : idem
    def _on_delete_down(self):
        self._do_delete()
        self._held_action  = 'delete'
        self._held_timer   = 0.0
        self._held_initial = True

    def _on_delete_up(self):
        if self._held_action == 'delete':
            self._held_action = None

    def _do_backspace(self):
        if self._cursor_pos > 0:
            self._text = self._text[:self._cursor_pos - 1] + self._text[self._cursor_pos:]
            self._cursor_pos -= 1
            self._update_text_offset()
            self._callback(self._text)

    def _do_delete(self):
        if self._cursor_pos < len(self._text):
            self._text = self._text[:self._cursor_pos] + self._text[self._cursor_pos + 1:]
            self._update_text_offset()
            self._callback(self._text)

    def _on_left(self):
        self._cursor_pos = max(0, self._cursor_pos - 1)
        self._update_text_offset()

    def _on_right(self):
        self._cursor_pos = min(len(self._text), self._cursor_pos + 1)
        self._update_text_offset()

    def _on_home(self):
        self._cursor_pos = 0
        self._update_text_offset()

    def _on_end(self):
        self._cursor_pos = len(self._text)
        self._update_text_offset()

    def _on_click_outside(self):
        if not self.collidemouse():
            self.unfocus()

    # ======================================== DESSIN ========================================
    def _get_cursor_x(self) -> int:
        """Position x locale du curseur (en suivant le blit_x du texte)"""
        cursor_x_in_text = self._font.size(self._text[:self._cursor_pos])[0]
        return self._text_blit_x + cursor_x_in_text

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
        available = self._rect.width - 2 * self._padding
        if self._text:
            text_surface = self._font.render(self._text, True, self._font_color)
            text_y = (self._rect.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (self._text_blit_x, text_y))
        elif self._placeholder is not None:
            ph_surface = self._font.render(self._placeholder, True, self._font_color_placeholder)
            text_y = (self._rect.height - ph_surface.get_height()) // 2
            surface.blit(ph_surface, (self._padding, text_y))

        # cursor (dessiné seulement dans la zone visible)
        if self._focused and self._cursor_visible:
            cursor_x = self._get_cursor_x()
            if self._padding <= cursor_x <= self._rect.width - self._padding:
                pygame.draw.line(surface, self._cursor_color,
                                 (cursor_x, self._padding),
                                 (cursor_x, self._rect.height - self._padding), 2)

        # bordure (par-dessus tout pour couvrir les débordements éventuels)
        if self._border_width > 0:
            pygame.draw.rect(surface, bd_color, self._local_rect, self._border_width,
                             border_radius=self._border_radius)

        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        """Détruit l'objet"""
        if self._focused:
            self.unfocus()
        context.ui._remove(self)

    def update(self):
        """Actualisation par frame"""
        if not self._visible:
            return

        # répétition avec cooldown pour backspace / delete
        if self._held_action is not None:
            self._held_timer += context.time.dt
            threshold = self._HOLD_INITIAL_DELAY if self._held_initial else self._HOLD_REPEAT_INTERVAL
            if self._held_timer >= threshold:
                self._held_timer = 0.0
                self._held_initial = False
                if self._held_action == 'backspace':
                    self._do_backspace()
                elif self._held_action == 'delete':
                    self._do_delete()

        # clignotement du cursor
        if self._focused:
            self._cursor_timer += context.time.dt
            if self._cursor_timer >= self._cursor_blink_rate:
                self._cursor_visible = not self._cursor_visible
                self._cursor_timer = 0.0
        else:
            self._cursor_visible = True
            self._cursor_timer = 0.0

        self._surface = self._render_frame()
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
        if not up:
            self.focus()

    def right_click(self, up: bool = False):
        if not up:
            self.unfocus()