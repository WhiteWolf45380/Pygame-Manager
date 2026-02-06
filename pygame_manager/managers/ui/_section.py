# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class SectionObject:
    """
    Object de l'interface : Section rectangulaire
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1, 
            height: Real = -1,

            filling: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_radius: int = 0,

            shadow: bool = False,
            shadow_offset: tuple = (5, 5),
            shadow_color: pygame.Color = (0, 0, 0, 100),

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

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_radius (int, optional) : rayon d'arrondissement des coins

            shadow (bool, optional) : activer l'ombre portée
            shadow_offset (tuple, optional) : décalage de l'ombre (x, y)
            shadow_color (Color, optional) : couleur de l'ombre

            panel (object, optional) : panel maître pour affichage automatique sur la surface
            zorder (int, optional) : ordre de rendu (plus élevé = au dessus)
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if not isinstance(shadow, bool): _raise_error(self, '__init__', 'Invalid shadow argument')
        if not isinstance(shadow_offset, tuple) or len(shadow_offset) != 2: _raise_error(self, '__init__', 'Invalid shadow_offset argument')
        shadow_color = _to_color(shadow_color, method='__init__')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')

        # auto-registration
        context.ui._append(self)

        # surface
        self._surface = None
        self._surface_rect = None

        # position et taille
        width = min(1920, max(1, width))
        height = min(1080, max(1, height))
        self._rect = pygame.Rect(x, y, width, height)
        self._local_rect = pygame.Rect(0, 0, width, height)

        # background
        self._filling = filling
        self._filling_color = filling_color

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_radius = max(0, border_radius)

        # ombre
        self._shadow = shadow
        self._shadow_offset = shadow_offset
        self._shadow_color = shadow_color

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None
        self._zorder = zorder

        # préchargement
        self._preloaded = self._load_surface()

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

    # ======================================== DESSIN ========================================
    def _load_surface(self) -> pygame.Surface:
        """Génère la surface de la section"""
        # calculer la taille totale avec ombre
        if self._shadow:
            total_width = self._rect.width + abs(self._shadow_offset[0])
            total_height = self._rect.height + abs(self._shadow_offset[1])
            surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
            
            # dessiner l'ombre
            shadow_rect = pygame.Rect(
                max(0, self._shadow_offset[0]),
                max(0, self._shadow_offset[1]),
                self._rect.width,
                self._rect.height
            )
            pygame.draw.rect(surface, self._shadow_color, shadow_rect, border_radius=self._border_radius)
            
            # dessiner la section principale
            main_rect = pygame.Rect(
                max(0, -self._shadow_offset[0]),
                max(0, -self._shadow_offset[1]),
                self._rect.width,
                self._rect.height
            )
        else:
            surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
            main_rect = self._local_rect

        # remplissage
        if self._filling:
            pygame.draw.rect(surface, self._filling_color, main_rect, border_radius=self._border_radius)

        # bordure
        if self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, main_rect, self._border_width, border_radius=self._border_radius)

        return surface

    def reload(self):
        """Recharge la surface (après modification des propriétés)"""
        self._preloaded = self._load_surface()

    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur la section"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        self._surface = self._preloaded
        if self._shadow:
            offset_x = max(0, -self._shadow_offset[0])
            offset_y = max(0, -self._shadow_offset[1])
            self._surface_rect = self._surface.get_rect(topleft=(self._rect.x - offset_x, self._rect.y - offset_y))
        else:
            self._surface_rect = self._surface.get_rect(topleft=self._rect.topleft)

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return
    
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        
        surface.blit(self._surface, self._surface_rect)