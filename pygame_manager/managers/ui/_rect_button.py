# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== Objet ========================================
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
            color: pygame.Color = (255, 255, 255, 255),
            color_hover: pygame.Color = None,
            text: str = 'Click',
            font: pygame.font.Font = None,
            font_path: str = None,
            font_size: int = None,
            font_color : pygame.Color = (0, 0, 0, 255),
            font_color_hover : pygame.Color = None,
            border_width : int = 0,
            border_color : pygame.Color = (0, 0, 0, 255),
            border_radius: int = 0,
            hover_effect: bool = False,
            hover_effect_factor: float = 0.95,
            hover_effect_speed: float = 1.0,
            callback: callable = lambda: None,
            menu: object=None
        ):
        """
        Args:
            x (Real) : coordonnée de la gauche
            y (Real) : coordonnée du haut
            width (Real) : largeur
            height (Real) : hauteur
            color (Color, optional) : couleur de fond
            color_hover (Color, optional) : couleur de fond lors du survol
            text (str, optional) : texte du boutton
            font (Font, optional) : police du texte
            font_path (str, optional) : chemin vers la police
            font_size (int, optional) : taille de la police
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol
            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_radius (int, optional) : rayon d'arrondissement des coins
            hover_effect (bool, optional) : effet de dezoom lors du survol
            hover_effect_ratio (float, optional) : facteur de dezoom lors du survol
            hover_effect_speed (float, optional) : facteur de vitesse de dezoom au moment du survol (0 pour instantanné)
            callback (callable, optional) : action en cas de pression du bouton
            menu (object, optional) : menu maître pour affichage automatique sur la surface
        """
        # auto-registration
        from .ui import ui_manager
        self.manager = ui_manager
        self.manager._append(self)

        # forme
        from ..geometry._rect import RectObject
        self._rect = RectObject((x, y), width, height)

    def update(self):
        """Actualisation par frame"""
        pass

    def draw(self):
        """Dessin par frame"""
        if self._menu is not None and hasattr(self._menu, 'surface'):
            pygame.draw.rect(self._menu.surface, )
        else:
            from ... import screen
            pygame.draw.rect(screen.surface, )