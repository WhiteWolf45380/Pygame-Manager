# ======================================== IMPORTS ========================================
from ... import context
import pygame
import math

# ======================================== GESTIONNAIRE ========================================
class MouseManager:
    """
    Gestionnaire de la souris
    """
    def __init__(self):
        # Position
        self._x = 0                                 # position x du curseur
        self._y = 0                                 # position y du curseur

        # Affichage
        self._icon = None                    # logo du curseur
        self._icon_scaled = None             # logo du curseur redimensionné
        self._icon_centered = False          # centrage ou non du logo du curseur
        self._last_scale = 0                 # cache du dernier scale pour optimiser les calculs

        # Propriétés
        self._visible = True                 # visibilité du curseur
        self._out = False                    # curseur en dehors de l'écran
    
    # ======================================== ACTUALISATION ========================================
    def _update(self):
        """
        Met à jour la position du curseur
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        left, right = context.screen._screen_resized_x_offset, context.screen._screen_resized_x_offset + context.screen._screen_resized_width          # bords horizontaux
        top, bottom = context.screen._screen_resized_y_offset, context.screen._screen_resized_y_offset + context.screen._screen_resized_height         # bords verticaux
        if not left <= mouse_x <= right or not top <= mouse_y <= bottom :                                                   # limites de l'écran
            self._out = True
        else:
            self._out = False
        self._x = (mouse_x - context.screen._screen_resized_x_offset) / self.scale                                            # conversion de la coordonée x
        self._y = (mouse_y - context.screen._screen_resized_y_offset) / self.scale                                            # conversion de la coordonée y

    # ======================================== AFFICHAGE ========================================
    def _draw(self):
        """
        Affiche le curseur curstomisé
        """
        if self._icon and not self._out and self._visible:
            if self.scale != self._last_scale:
                s = 0.8 + 0.4 / (1 + math.exp(-4 * (self.scale - 1)))                                                                    # scale sigmoïdal doux
                w, h = self._icon.get_size()
                self._icon_scaled = pygame.transform.smoothscale(self._icon, (int(w * s), int(h * s)))
                self._last_scale = self.scale
            mx, my = pygame.mouse.get_pos()
            if self._icon_centered:
                context.screen._window.blit(self._icon_scaled, (mx - self._icon_scaled.get_width()//2, my - self._icon_scaled.get_height()//2))
            else:
                context.screen._window.blit(self._icon_scaled, (mx, my))

    # ======================================== GETTERS ========================================
    def get_mouse_pos(self) -> tuple[float, float]:
        """
        Renvoie les coordonnées du curseur
        """
        return (self._x, self._y)
    
    @property
    def mouse_x(self) -> float:
        """
        Renvoie la position horizontale du curseur
        """
        return self._x
    
    @property
    def mouse_y(self) -> float:
        """
        Renvoie la position verticale du curseur
        """
        return self._y
    
    def get_mouse_grab(self) -> bool:
        """
        Vérifie si le maintient du curseur est activé
        """
        return pygame.event.get_grab()
    
    def get_mouse_visible(self) -> bool:
        """
        Vérifie la visibilité du curseur
        """
        return self._visible
    
    # ======================================== SETTERS ========================================
    def set_mouse_icon(self, icon: pygame.Surface | None, centered: bool=False):
        """
        Fixe le logo de la souris

        Args:
            icon (pygame.Surface) : nouvelle image de la souris
            centered (bool) : icon du curseur centré ou non
        """
        if icon is None:
            self._icon = None
            pygame.mouse.set_visible(self._visible)
            return
        if not isinstance(icon, pygame.Surface):
            self._raise_error('set_mouse_icon', 'Mouse icon must be a Surface object')
        if not isinstance(centered, bool):
            self._raise_error('set_mouse_icon', 'Centered parameter must be a boolean')
        self._icon = icon
        pygame.mouse.set_visible(False)
        self._icon_centered = centered

    def set_mouse_grab(self, value: bool):
        """
        Fixe le maintient du curseur dans la fenêtre

        Args:
            value (bool) : maintient ou non du curseur
        """
        if not isinstance(value, bool):
            self._raise_error('set_mouse_grab', 'Value type must be boolean')
        pygame.event.set_grab(value)
    
    def set_mouse_visible(self, value: bool):
        """
        Fixe la visibilité du curseur

        Args:
            value (bool) : curseur visible ou non
        """
        if not isinstance(value, bool):
            self._raise_error('set_mouse_visible', 'Value type must be boolean')
        self._visible = value
        pygame.mouse.set_visible(value and self._icon is None)

# ======================================== INSTANCIATION ========================================
mouse_manager = MouseManager()