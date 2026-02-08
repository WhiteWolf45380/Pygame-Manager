# ======================================== IMPORTS ========================================
from ._core import *
import numpy as np

# ======================================== OBJET ========================================
class SurfaceObject:
    """
    Object de l'interface : Surface colorée
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = 100,
            height: Real = 100,
            
            color: pygame.Color = (255, 255, 255, 255),
            anchor: str = "topleft",
            
            border: bool = False,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_width: int = 1,
            border_radius: int = 0,
            
            gradient: bool = False,
            gradient_color: pygame.Color | None = None,
            gradient_direction: str = "horizontal",
            gradient_fluctuation: bool = False,
            gradient_fluctuation_speed: float = 2.0,
            gradient_fluctuation_amplitude: float = 0.3,
            gradient_fluctuation_bands: int = 60,
            gradient_brightness_pulse: bool = False,
            gradient_brightness_amplitude: float = 0.05,
            
            auto: bool = True,
            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée x
            y (Real) : coordonnée y
            width (Real) : largeur de la surface
            height (Real) : hauteur de la surface
            
            color (Color, optional) : couleur de la surface
            anchor (str, optional) : point d'ancrage ("topleft", "center", "midtop", etc.)
            
            border (bool, optional) : afficher une bordure
            border_color (Color, optional) : couleur de la bordure
            border_width (int, optional) : épaisseur de la bordure
            border_radius (int, optional) : rayon des coins arrondis
            
            gradient (bool, optional) : dégradé
            gradient_color (Color, optional) : seconde couleur
            gradient_direction (str, optional) : direction du dégradé parmi ('horizontal', 'vertical', 'diagonal')
            gradient_fluctuation (bool, optional) : fluctuation du dégradé
            gradient_fluctuation_speed (float, optional) : vitesse de fluctuation
            gradient_fluctuation_amplitude (float, optional) : amplitude de fluctuation
            gradient_fluctuation_bands (int, optional) : nombre de bandes pour la fluctuation (plus = qualité, moins = perf)
            gradient_brightness_pulse (bool, optional) : pulsation de luminosité
            gradient_brightness_amplitude (float, optional) : amplitude de la pulsation (0.0-1.0)
            
            auto (bool, optional) : enregistrement automatique pour draw
            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real) or width <= 0: _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real) or height <= 0: _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        color = _to_color(color, method='__init__')
        if not isinstance(border, bool): _raise_error(self, '__init__', 'Invalid border argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(border_width, int) or border_width < 0: _raise_error(self, '__init__', 'Invalid border_width argument')
        if not isinstance(border_radius, int) or border_radius < 0: _raise_error(self, '__init__', 'Invalid border_radius argument')
        if not isinstance(gradient, bool): _raise_error(self, '__init__', 'Invalid gradient argument')
        gradient_color = _to_color(gradient_color, raised=False)
        if not isinstance(gradient_direction, str) or gradient_direction not in ('horizontal', 'vertical', 'diagonal'): _raise_error(self, '__init__', 'Invalid gradient_direction argument')
        if not isinstance(gradient_fluctuation, bool): _raise_error(self, '__init__', 'Invalid gradient_fluctuation argument')
        if not isinstance(gradient_fluctuation_speed, float) or gradient_fluctuation_speed <= 0: _raise_error(self, '__init__', 'Invalid gradient_fluctuation_speed argument')
        if not isinstance(gradient_fluctuation_amplitude, float) or gradient_fluctuation_amplitude <= 0: _raise_error(self, '__init__', 'Invalid gradient_fluctuation_amplitude argument')
        if not isinstance(gradient_fluctuation_bands, int) or gradient_fluctuation_bands <= 0: _raise_error(self, '__init__', 'Invalid gradient_fluctuation_bands argument')
        if not isinstance(gradient_brightness_pulse, bool): _raise_error(self, '__init__', 'Invalid gradient_brightness_pulse argument')
        if not isinstance(gradient_brightness_amplitude, float) or gradient_brightness_amplitude < 0 or gradient_brightness_amplitude > 1: _raise_error(self, '__init__', 'Invalid gradient_brightness_amplitude argument')
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

        # dimensions
        self._width = int(width)
        self._height = int(height)

        # couleur
        self._color = color

        # bordure
        self._border = border
        self._border_color = border_color
        self._border_width = border_width
        self._border_radius = border_radius

        # dégradé
        self._gradient = gradient if gradient_color is not None else False
        self._gradient_color = gradient_color
        self._gradient_direction = gradient_direction
        self._gradient_fluctuation = gradient_fluctuation
        self._gradient_fluctuation_speed = gradient_fluctuation_speed
        self._gradient_fluctuation_amplitude = gradient_fluctuation_amplitude
        self._gradient_fluctuation_bands = gradient_fluctuation_bands
        self._gradient_fluctuation_timer = 0.0
        self._gradient_brightness_pulse = gradient_brightness_pulse
        self._gradient_brightness_amplitude = gradient_brightness_amplitude

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

    # ======================================== RENDU ========================================
    def _render(self):
        """Génère la surface"""
        if self._gradient:
            return self._render_gradient()
        
        self._surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        
        if self._border_radius > 0:
            pygame.draw.rect(self._surface, self._color, (0, 0, self._width, self._height), border_radius=self._border_radius)
        else:
            self._surface.fill(self._color)
        
        if self._border:
            if self._border_radius > 0:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), width=self._border_width, border_radius=self._border_radius)
            else:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), width=self._border_width)
        
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def _render_gradient(self):
        """Render la surface avec un dégradé statique selon direction"""
        self._surface = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        
        c1 = self._color
        c2 = self._gradient_color

        if self._gradient_direction == "vertical":
            for y in range(self._height):
                t = y / (self._height - 1) if self._height > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                a = int(c1[3] + (c2[3] - c1[3]) * t) if len(c1) > 3 and len(c2) > 3 else 255
                pygame.draw.line(self._surface, (r, g, b, a), (0, y), (self._width, y))

        elif self._gradient_direction == "horizontal":
            for x in range(self._width):
                t = x / (self._width - 1) if self._width > 1 else 0
                r = int(c1[0] + (c2[0] - c1[0]) * t)
                g = int(c1[1] + (c2[1] - c1[1]) * t)
                b = int(c1[2] + (c2[2] - c1[2]) * t)
                a = int(c1[3] + (c2[3] - c1[3]) * t) if len(c1) > 3 and len(c2) > 3 else 255
                pygame.draw.line(self._surface, (r, g, b, a), (x, 0), (x, self._height))

        elif self._gradient_direction == "diagonal":
            for y in range(self._height):
                for x in range(self._width):
                    t = ((x / (self._width - 1 if self._width > 1 else 1)) +
                        (y / (self._height - 1 if self._height > 1 else 1))) * 0.5
                    r = int(c1[0] + (c2[0] - c1[0]) * t)
                    g = int(c1[1] + (c2[1] - c1[1]) * t)
                    b = int(c1[2] + (c2[2] - c1[2]) * t)
                    a = int(c1[3] + (c2[3] - c1[3]) * t) if len(c1) > 3 and len(c2) > 3 else 255
                    self._surface.set_at((x, y), (r, g, b, a))

        if self._border:
            if self._border_radius > 0:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), width=self._border_width, border_radius=self._border_radius)
            else:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), width=self._border_width)

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
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy() if self._rect else pygame.Rect(self._x, self._y, 0, 0)

    @property
    def surface(self) -> pygame.Surface:
        """Renvoie la surface rendue"""
        return self._surface

    @property
    def width(self) -> int:
        """Renvoie la largeur"""
        return self._width

    @property
    def height(self) -> int:
        """Renvoie la hauteur"""
        return self._height

    @property
    def x(self) -> Real:
        """Renvoie la position x"""
        return self._x

    @property
    def y(self) -> Real:
        """Renvoie la position y"""
        return self._y

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

    @x.setter
    def x(self, value: Real):
        """Fixe la position x"""
        if not isinstance(value, Real):
            _raise_error(self, 'set_x', 'Invalid value argument')
        self._x = value
        if self._surface:
            self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    @y.setter
    def y(self, value: Real):
        """Fixe la position y"""
        if not isinstance(value, Real):
            _raise_error(self, 'set_y', 'Invalid value argument')
        self._y = value
        if self._surface:
            self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_position(self, x: Real, y: Real):
        """Modifie la position"""
        self._x = x
        self._y = y
        if self._surface:
            self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_size(self, width: Real, height: Real):
        """Modifie la taille et re-render"""
        if not isinstance(width, Real) or width <= 0:
            _raise_error(self, 'set_size', 'Invalid width argument')
        if not isinstance(height, Real) or height <= 0:
            _raise_error(self, 'set_size', 'Invalid height argument')
        self._width = int(width)
        self._height = int(height)
        self._render()

    def set_color(self, color: pygame.Color):
        """Modifie la couleur et re-render"""
        self._color = _to_color(color, method='set_color')
        self._render()

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur la surface"""
        if not self._rect:
            return False
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        self.update_gradient()

    def draw(self):
        """Dessin par frame"""
        if not self._visible or not self._surface:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        
        surface.blit(self._surface, self._rect)
    
    def update_gradient(self):
        """Dégradé animé ultra-léger avec bandes"""
        if not self._gradient or not self._gradient_fluctuation:
            return

        self._gradient_fluctuation_timer += context.time.dt

        c1 = self._color
        c2 = self._gradient_color
        
        timer = self._gradient_fluctuation_timer * self._gradient_fluctuation_speed
        num_bands = self._gradient_fluctuation_bands
        
        if self._gradient_direction == "horizontal":
            band_width = self._width / num_bands
            for i in range(num_bands):
                t = i / (num_bands - 1) if num_bands > 1 else 0
                wave = 0.5 + self._gradient_fluctuation_amplitude * np.sin(t * 2 * np.pi + timer)
                
                r = int(c1[0] * (1 - wave) + c2[0] * wave)
                g = int(c1[1] * (1 - wave) + c2[1] * wave)
                b = int(c1[2] * (1 - wave) + c2[2] * wave)
                
                x = int(i * band_width)
                w = int(band_width) + 1
                pygame.draw.rect(self._surface, (r, g, b), (x, 0, w, self._height))
        
        elif self._gradient_direction == "vertical":
            band_height = self._height / num_bands
            for i in range(num_bands):
                t = i / (num_bands - 1) if num_bands > 1 else 0
                wave = 0.5 + self._gradient_fluctuation_amplitude * np.sin(t * 2 * np.pi + timer)
                
                r = int(c1[0] * (1 - wave) + c2[0] * wave)
                g = int(c1[1] * (1 - wave) + c2[1] * wave)
                b = int(c1[2] * (1 - wave) + c2[2] * wave)
                
                y = int(i * band_height)
                h = int(band_height) + 1
                pygame.draw.rect(self._surface, (r, g, b), (0, y, self._width, h))
        
        elif self._gradient_direction == "diagonal":
            # Pour diagonal, on fait un mix horizontal simplifié
            band_width = self._width / num_bands
            for i in range(num_bands):
                t = i / (num_bands - 1) if num_bands > 1 else 0
                wave = 0.5 + self._gradient_fluctuation_amplitude * np.sin(t * 2 * np.pi + timer)
                
                r = int(c1[0] * (1 - wave) + c2[0] * wave)
                g = int(c1[1] * (1 - wave) + c2[1] * wave)
                b = int(c1[2] * (1 - wave) + c2[2] * wave)
                
                x = int(i * band_width)
                w = int(band_width) + 1
                pygame.draw.rect(self._surface, (r, g, b), (x, 0, w, self._height))

        # Pulsation de luminosité (optionnelle, très peu coûteuse)
        if self._gradient_brightness_pulse:
            brightness = int(255 * (1.0 - self._gradient_brightness_amplitude + 
                                    self._gradient_brightness_amplitude * np.sin(timer)))
            overlay = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, int(brightness * 0.04)))  # Alpha très faible pour effet subtil
            self._surface.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # Bordure
        if self._border:
            if self._border_radius > 0:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), 
                               width=self._border_width, border_radius=self._border_radius)
            else:
                pygame.draw.rect(self._surface, self._border_color, (0, 0, self._width, self._height), 
                               width=self._border_width)

        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def left_click(self, up: bool = False):
        """Clic gauche"""
        pass

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass