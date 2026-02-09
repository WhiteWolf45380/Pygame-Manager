# ======================================== IMPORTS ========================================
from ._core import *
import numpy as np

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
            anchor: str = "topleft",

            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = 24,
            font_color: pygame.Color = (0, 0, 0, 255),
            antialias: bool = True,

            bold: bool = False,
            italic: bool = False,
            underline: bool = False,
            shadow: bool = False,
            shadow_color: pygame.Color = (0, 0, 0),
            shadow_offset: int = 2,

            gradient: bool = False,
            gradient_color: pygame.Color | None = None,
            gradient_direction: str = "horizontal",
            gradient_fluctuation: bool = False,
            gradient_fluctuation_speed: float = 2.0,
            gradient_fluctuation_amplitude: float = 0.3,

            background: pygame.Color = None,

            auto: bool = True,
            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée x
            y (Real) : coordonnée y
            text (str) : texte à afficher
            anchor (str, optional) : point d'ancrage ("topleft", "center", "midtop", etc.)

            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur du texte
            antialias (bool, optional) : antialiasing du texte

            bold (bool, optional) : texte en gras
            italic (bool, optional) : texte en italique
            underline (bool, optional) : texte souligné
            shadow (bool, optional) : ombre du texte
            shadow_color (Color, optional) : couleur de l'ombre
            shadow_offset (int, optional) : décalage de l'ombre

            gradient (bool, optional) : dégradé
            gradient_color (Color, optional) : seconde couleur
            gradient_direction (str, optional) : direction du dégradé parmi ('horizontal', 'vertical', 'diagonal')
            gradient_fluctuation (bool, optional) : fluctuation du dégradé

            background (Color, optional) : couleur de fond

            auto (bool, optional) : enregistrement automatique pour draw
            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if font is not None and not isinstance(font, pygame.font.Font): _raise_error(self, '__init__', 'Invalid font argument')
        if font_path is not None and not isinstance(font_path, str): _raise_error(self, '__init__', 'Invalid font_path argument')
        if not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        if not isinstance(antialias, bool): _raise_error(self, '__init__', 'Invalid antialias argument')
        if not isinstance(bold, bool): _raise_error(self, "__init__", "Invalid bool argument")
        if not isinstance(italic, bool): _raise_error(self, "__init__", "Invalid italic argument")
        if not isinstance(underline, bool): _raise_error(self, "__init__", "Invalid underline argument")
        if not isinstance(shadow, bool): _raise_error(self, "__init__", "Invalid shadow argument")
        shadow_color = _to_color(shadow_color, method='__init__')
        if not isinstance(shadow_offset, int): _raise_error(self, "__init__", "Invalid shadow_offset argument")
        if background is not None: background = _to_color(background)
        if not isinstance(gradient, bool): _raise_error(self, '__init__', 'Invalid gradient argument')
        gradient_color = _to_color(gradient_color, raised=False)
        if not isinstance(gradient_direction, str) or gradient_direction not in ('horizontal', 'vertical', 'diagonal'): _raise_error(self, '__init__', 'Invalid gradient_direction argument')
        if not isinstance(gradient_fluctuation, bool): _raise_error(self, '__init__', 'Invalid gradient_fluctuation argument')
        if not isinstance(gradient_fluctuation_speed, float) or gradient_fluctuation_speed <= 0: _raise_error(self, '__init__', 'Invalid gradient_fluctuation_speed argument')
        if not isinstance(gradient_fluctuation_amplitude, float) or gradient_fluctuation_amplitude <= 0: _raise_error(self, '__init__', 'Invalid gradient_fluctuation_amplitude argument')
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
                self._font: pygame.font.Font = pygame.font.Font(font_path, font_size)
            except Exception as _:
                self._font: pygame.font.Font = pygame.font.Font(None, font_size)
        else:
            self._font: pygame.font.Font = font

        # Effets
        self._font.set_bold(bold)
        self._font.set_italic(italic)
        self._font.set_underline(underline)
        self._shadow = shadow
        self._shadow_color = shadow_color
        self._shadow_offset = shadow_offset
        self._shadow_surface = None

        # Fond
        self._background = background

        # dégradé
        self._gradient = gradient if gradient_color is not None else False
        self._gradient_color = gradient_color
        self._gradient_direction = gradient_direction
        self._gradient_fluctuation = gradient_fluctuation
        self._gradient_fluctuation_speed = gradient_fluctuation_speed
        self._gradient_fluctuation_amplitude = gradient_fluctuation_amplitude
        self._gradient_fluctuation_timer = 0.0

        # surface
        self._surface = None
        self._surface_init = None
        self._rect = None
        if self._gradient: self._render_gradient()
        self._render()

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # paramètres dynamiques
        self._visible = True

    # ======================================== RENDU ========================================
    def _render(self):
        """Génère la surface du texte"""
        if self._gradient:
            return self._render_gradient()
        self._surface = self._font.render(self._text, self._antialias, self._font_color, self._background)
        self._surface_init = self._surface.copy()
        self._shadow_surface = self._font.render(self._text, self._antialias, self._shadow_color)
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def _render_gradient(self):
        """Render le texte avec un dégradé statique selon direction"""
        text_surf = self._font.render(self._text, self._antialias, (255, 255, 255))
        w, h = text_surf.get_size()

        gradient = pygame.Surface((w, h), pygame.SRCALPHA)

        c1 = self._font_color
        c2 = self._gradient_color

        if self._gradient_direction == "vertical":
            for y in range(h):
                t = y / (h - 1) if h > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                pygame.draw.line(gradient, (r, g, b), (0, y), (w, y))

        elif self._gradient_direction == "horizontal":
            for x in range(w):
                t = x / (w - 1) if w > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                pygame.draw.line(gradient, (r, g, b), (x, 0), (x, h))

        elif self._gradient_direction == "diagonal":
            for y in range(h):
                for x in range(w):
                    t = ((x / (w - 1 if w > 1 else 1)) +
                        (y / (h - 1 if h > 1 else 1))) * 0.5
                    r = int(c1[0] + (c2[0] - c1[0]) * t)
                    g = int(c1[1] + (c2[1] - c1[1]) * t)
                    b = int(c1[2] + (c2[2] - c1[2]) * t)
                    gradient.set_at((x, y), (r, g, b))

        gradient.blit(text_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self._surface = gradient
        self._surface_init = self._surface.copy()
        self._shadow_surface = self._font.render(self._text, self._antialias, self._shadow_color)
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})


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
    
    def set_alpha(self, alpha: int):
        """Modifie l'opacité"""
        if not isinstance(alpha, int) or not 0 <= alpha <= 255:
            _raise_error(self, 'set_alpha', 'Invalid alpha argument')
        self._surface.set_alpha(alpha)

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le bouton"""
        if self._panel is not None:
            mouse_pos = self._panel.mouse_pos
        else:
            mouse_pos = context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        """Détruit l'objet"""
        context.ui._remove(self)

    def scale(self, ratio: Real):
        """Redimensionne l'objet"""
        if not isinstance(ratio, Real) or not 0.0 < ratio <= 1.0:
            _raise_error(self, 'scale', 'Invalid ratio_argument')
        self._surface = pygame.transform.smoothscale(self._surface_init, (self._surface_init.get_width() * ratio, self._surface_init.get_height() * ratio))
        self._rect = self._surface.get_rect(center=self._rect.center)

    def update(self):
        """Actualisation par frame"""
        if not self._visible:
            return
        self.update_gradient()

    def draw(self):
        """Dessin par frame"""
        if not self._visible or not self._surface:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        
        if self._shadow is not None:
            surface.blit(self._shadow_surface, (self._rect.x + self._shadow_offset, self._rect.y + self._shadow_offset))
        surface.blit(self._surface, self._rect)
    
    def update_gradient(self):
        """Dégradé animé type 'cycles', optimisé avec numpy, avec amplitude et direction"""
        if not self._gradient or not self._gradient_fluctuation:
            return

        self._gradient_fluctuation_timer += context.time.dt

        text_surf = self._font.render(self._text, True, (255, 255, 255))
        w, h = text_surf.get_size()
        gradient = pygame.Surface((w, h), pygame.SRCALPHA)

        c1 = np.array(self._font_color[:3], dtype=np.float32)
        c2 = np.array(self._gradient_color[:3], dtype=np.float32)
        amp = self._gradient_fluctuation_amplitude
        timer = self._gradient_fluctuation_timer * self._gradient_fluctuation_speed

        if self._gradient_direction == "horizontal":
            pos = np.linspace(0, 1, w, dtype=np.float32).reshape((w, 1))
            pos = np.tile(pos, (1, h))
        elif self._gradient_direction == "vertical":
            pos = np.linspace(0, 1, h, dtype=np.float32).reshape((1, h))
            pos = np.tile(pos, (w, 1))
        elif self._gradient_direction == "diagonal":
            xv = np.linspace(0, 1, w, dtype=np.float32).reshape((w, 1))
            yv = np.linspace(0, 1, h, dtype=np.float32).reshape((1, h))
            pos = (np.tile(xv, (1, h)) + np.tile(yv, (w, 1))) / 2
        else:
            pos = np.linspace(0, 1, w, dtype=np.float32).reshape((w, 1))
            pos = np.tile(pos, (1, h))

        wave = 0.5 + amp * np.sin(pos * np.pi * 2 + timer)

        array = np.zeros((w, h, 3), dtype=np.uint8)
        array[..., 0] = (c1[0] * (1 - wave) + c2[0] * wave).astype(np.uint8)
        array[..., 1] = (c1[1] * (1 - wave) + c2[1] * wave).astype(np.uint8)
        array[..., 2] = (c1[2] * (1 - wave) + c2[2] * wave).astype(np.uint8)

        pygame.surfarray.blit_array(gradient, array)

        gradient.blit(text_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self._surface = gradient
        self._surface_init = self._surface.copy()
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def left_click(self, up: bool = False):
        """Clic gauche"""
        pass

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass