try:
    import pygame
except ImportError:
    raise RuntimeError("[ScreenManager] requieres pygame to work normally\nTry to download it with : pip install pygame")


class ScreenManager:
    """
    Gestionnaire pygame de la fenêtre

    Fonctionnalités:
    """
    def __init__(self, screen: tuple[int]=(1920, 1080), window: tuple[int]=(1280, 720)):
        # initialisation
        if not pygame.get_init():
            pygame.init()
        
        # écran virtuel
        self._screen_width = screen[0]
        self._screen_height = screen[1]
        self._screen = pygame.Surface((self._screen_width, self._screen_height))
        self._screen.fill((255, 255, 255))

        # écran intermédiaire (taille réelle mais sans bandes noires)
        self._screen_resized_width = self.screen_width
        self._screen_resized_height = self.screen_height
        self._screen_resized_x_offset = 0 # bandes verticales
        self._screen_resized_y_offset = 0 # bandes horizontales

        # fenêtre pygame
        self._window_width = window[0]
        self._window_height = window[1]
        self._window = pygame.display.set_mode((self._window_width, self._window_height), pygame.RESIZABLE, pygame.SRCALPHA)

        # plein écran
        self._fullscreen = False
        self._windowed_width = self._window_width   # sauvegarde de la dernière largeur
        self._windowed_height = self._window_height # sauvegarde de la dernière hauteur

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__name}].{method} : {text}")
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def set_caption(self, caption: str):
        """Fixe le titre de la fenêtre"""
        if not isinstance(caption, str):
            self._raise_error('set_caption', 'Window caption type must be str')    
        pygame.display.set_caption(caption)

    def set_icon(self, icon: pygame.Surface):
        if not isinstance(icon, pygame.Surface):
            self._raise_error('set_icon', 'Window icon must be a Surface object')    
        pygame.display.set_icon(icon)