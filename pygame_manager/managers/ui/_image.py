# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class ImageObject:
    """
    Object de l'interface : Image
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            image: pygame.Surface = None,
            image_path: str = None,

            width: Real = None,
            height: Real = None,
            scale: float = 1.0,
            keep_ratio: bool = True,

            anchor: str = "topleft",

            auto: bool = True,
            panel: object = None,
            zorder: int = 0,
        ):
        """
        Args:
            x (Real) : coordonnée x
            y (Real) : coordonnée y
            image (Surface, optional) : surface pygame de l'image
            image_path (str, optional) : chemin vers l'image

            width (Real, optional) : largeur cible (si None, utilise la largeur originale * scale)
            height (Real, optional) : hauteur cible (si None, utilise la hauteur originale * scale)
            scale (float, optional) : facteur d'échelle si width/height non spécifiés
            keep_ratio (bool, optional) : conserver le ratio si width ou height seul spécifié

            anchor (str, optional) : point d'ancrage ("topleft", "center", "midtop", etc.)

            auto (bool, optional) : enregistrement automatique pour draw
            panel (object, optional) : panel maître
            zorder (int, optional) : ordre de rendu
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if image is not None and not isinstance(image, pygame.Surface): _raise_error(self, '__init__', 'Invalid image argument')
        if image_path is not None and not isinstance(image_path, str): _raise_error(self, '__init__', 'Invalid image_path argument')
        if image is None and image_path is None: _raise_error(self, '__init__', 'Either image or image_path must be provided')
        if width is not None and not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if height is not None and not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(scale, Real) or scale <= 0: _raise_error(self, '__init__', 'Invalid scale argument')
        if not isinstance(keep_ratio, bool): _raise_error(self, '__init__', 'Invalid keep_ratio argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(auto, bool): _raise_error(self, '__init__', 'Invalid auto argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        self._auto_draw = auto
        if self._auto:
            context.ui._append(self)

        # chargement de l'image
        if image is not None:
            self._original_image = image
        else:
            try:
                self._original_image = pygame.image.load(image_path).convert_alpha()
            except Exception as e:
                _raise_error(self, '__init__', f'Failed to load image: {e}')

        # position
        self._x = x
        self._y = y
        self._anchor = anchor

        # dimensions
        self._width = width
        self._height = height
        self._scale = scale
        self._keep_ratio = keep_ratio

        # surface et rect
        self._surface = None
        self._rect = None
        self._update_surface()

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
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy() if self._rect else pygame.Rect(self._x, self._y, 0, 0)

    @property
    def surface(self) -> pygame.Surface:
        """Renvoie la surface"""
        return self._surface

    @property
    def width(self) -> int:
        """Renvoie la largeur actuelle"""
        return self._rect.width if self._rect else 0

    @property
    def height(self) -> int:
        """Renvoie la hauteur actuelle"""
        return self._rect.height if self._rect else 0

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

    # ======================================== TRANSFORMATION ========================================
    def _update_surface(self):
        """Met à jour la surface selon les dimensions spécifiées"""
        orig_w, orig_h = self._original_image.get_size()

        # calculer les dimensions finales
        if self._width is not None and self._height is not None:
            final_w, final_h = int(self._width), int(self._height)
        elif self._width is not None:
            final_w = int(self._width)
            final_h = int(orig_h * final_w / orig_w) if self._keep_ratio else orig_h
        elif self._height is not None:
            final_h = int(self._height)
            final_w = int(orig_w * final_h / orig_h) if self._keep_ratio else orig_w
        else:
            final_w = int(orig_w * self._scale)
            final_h = int(orig_h * self._scale)

        # redimensionner si nécessaire
        if final_w == orig_w and final_h == orig_h:
            self._surface = self._original_image
        else:
            self._surface = pygame.transform.smoothscale(self._original_image, (final_w, final_h))

        # mettre à jour le rect
        self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_position(self, x: Real, y: Real):
        """Modifie la position"""
        self._x = x
        self._y = y
        if self._surface:
            self._rect = self._surface.get_rect(**{self._anchor: (self._x, self._y)})

    def set_size(self, width: Real = None, height: Real = None):
        """Modifie la taille"""
        if width is not None:
            self._width = width
        if height is not None:
            self._height = height
        self._update_surface()

    def set_scale(self, scale: float):
        """Modifie l'échelle"""
        if not isinstance(scale, Real) or scale <= 0:
            _raise_error(self, 'set_scale', 'Invalid scale argument')
        self._scale = scale
        self._width = None
        self._height = None
        self._update_surface()

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur l'image"""
        if not self._rect:
            return False
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        pass

    def draw(self):
        """Dessin par frame"""
        if not self._visible or not self._surface:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        
        surface.blit(self._surface, self._rect)
    
    def left_click(self, up: bool = False):
        """Clic gauche"""
        pass

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass