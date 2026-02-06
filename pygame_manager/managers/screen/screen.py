# ======================================== IMPORTS ========================================
from ... import context
import os
import math
try:
    import pygame
except ImportError:
    raise RuntimeError("[ScreenManager] requieres pygame to work normally\nTry to download it with : pip install pygame")


# ======================================== GESTIONNAIRE ========================================
class ScreenManager:
    """
    Gestionnaire pygame de l'affichage

    Fonctionnalités:
        gère semi-automatiquement l'écran et la fenêtre (nécessite de wrapper le dessin dans un with)
        supporte la quasi totalité des méthodes de pygame.Surface
        facilite grandement le paramètrage et la maintenance de la fenêtre
        permet un transformation automatique de l'écran virtuel vers la fenêtre réel
    """
    def __init__(self, screen: tuple[int]=(1920, 1080), window: tuple[int]=(1280, 720)):
        # initialisation
        if not pygame.get_init():
            pygame.init()
        self._opened = True
        
        # écran virtuel
        self._screen_width = screen[0]
        self._screen_height = screen[1]
        self._screen = pygame.Surface((self._screen_width, self._screen_height))
        self._screen.fill((255, 255, 255))

        # écran intermédiaire (taille réelle mais sans bandes noires)
        self._screen_resized_width = self._screen_width
        self._screen_resized_height = self._screen_height
        self._screen_resized_x_offset = 0                                                                          # bandes verticales
        self._screen_resized_y_offset = 0                                                                          # bandes horizontales

        # fenêtre pygame
        self._window_width = window[0]
        self._window_height = window[1]
        self._window = pygame.display.set_mode((self._window_width, self._window_height), pygame.RESIZABLE, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=False)
        self._window_resizable = True                                                                              # possibilité de redimensionner la fenêtre

        # plein écran
        self._fullscreen = False
        self._windowed_width = self._window_width                                                                 # sauvegarde de la dernière largeur
        self._windowed_height = self._window_height                                                               # sauvegarde de la dernière hauteur

        # paramètres
        self._smooth_rendering = True                                                                              # utilisation du smoothscale pour le redimensionnement
        self._vsync = False                                                                                        # utilisation de la vsync (anti tearing)

        # BLACKLIST pour le proxy Surface
        self._SURFACE_BLACKLIST = {
            # destructif / interne
            'convert', 'convert_alpha',
            'set_clip', 'set_colorkey', 'set_alpha', 'set_palette',
            'set_palette_at', 'set_at', 'set_masks',
            'set_locked', 'lock', 'unlock',
            
            # accès brut / buffer
            'get_buffer', 'get_view',

            # scroll modifie directement la surface
            'scroll',

            # attributs internes Python
            '__dict__', '__class__'
        }

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self._class__.__name__}].{method} : {text}")
    
    def __getattribute__(self, name):
        """
        Bloque tout accès externe aux attributs privés manglés
        """
        return super().__getattribute__(name)
    
    def __getattr__(self, name):
        """
        Proxy automatique vers la surface virtuelle
        """
        if name in self._SURFACE_BLACKLIST:
            raise AttributeError(f"{self._class__.__name__}: access to Surface.{name} is forbidden")
        return getattr(self._screen, name)
    
    def __enter__(self):
        """
        Début du with
        """
        self._update()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Fin du with
        """
        self._flip()
        return False
    
    def _update(self):
        """
        Méthode appelée au début du with
        """
        if self._opened:
            self._update_screen()

    def _flip(self):
        """
        Méthode appelée à la fin du with
        """
        if self._opened:
            # redimensionnement
            if not self._smooth_rendering:                                                                                                      # rendu pixelisé
                self._screen_resized = pygame.transform.scale(self._screen, (self._screen_resized_width, self._screen_resized_height))
            else:                                                                                                                                # rendu vectoriel
                self._screen_resized = pygame.transform.smoothscale(self._screen, (self._screen_resized_width, self._screen_resized_height))
            self._window.fill((0, 0, 0))                                                                                                        # bandes noires
            self._window.blit(self._screen_resized, (self._screen_resized_x_offset, self._screen_resized_y_offset))

            # affichage curseur
            context.mouse._draw()

            # actualisation
            pygame.display.flip()
    
    def _update_screen(self):
        """
        Met à jour l'écran
        """
        # récupération des dimensions de la fenêtre réelle
        self._window_width = self._window.get_width()
        self._window_height = self._window.get_height()

        # on prend le ratio min
        if self._screen_width == 0 or self._screen_height == 0:
            self._raise_error('_update_screen', 'Screen size cannot be set to zero')
        scale = min(
            self._window_width / self._screen_width,
            self._window_height / self._screen_height
        )

        # calcul de la taille redimensionnée de l'écran
        self._screen_resized_width = int(self._screen_width * scale)
        self._screen_resized_height = int(self._screen_height * scale)

        # calcul des décalages pour les bandes noires
        self._screen_resized_x_offset = (self._window_width - self._screen_resized_width) // 2
        self._screen_resized_y_offset = (self._window_height - self._screen_resized_height) // 2

    # ======================================== GETTERS ========================================
    @property
    def opened(self) -> bool:
        """
        Vérifie que la fenêtre soit ouverte
        """
        return self._opened
    
    @property
    def surface(self) -> pygame.Surface:
        return self._screen

    def get_screen_size(self) -> tuple[int, int]:
        """
        Renvoie les dimensions de l'écran virtuel
        """
        return (self._screen_width, self._screen_height)
    
    @property
    def width(self) -> int:
        """
        Renvoie la largeur de l'écran virtuel
        """
        return self._screen_width
    
    @property
    def height(self) -> int:
        """
        Renvoie la hauteur de l'écran virtuel
        """
        return self._screen_height
    
    @property
    def center(self) -> tuple[float]:
        """
        Renvoie les coordonnées du centre de l'écran
        """
        return (self._screen_width / 2, self._screen_height / 2)
    
    @property
    def centerx(self) -> float:
        """
        Renvoie la coordonnée horizontale du centre de l'écran
        """
        return self._screen_width / 2
    
    @property
    def centery(self) -> float:
        """
        Renvoie la coordonnée verticale du centre de l'écran
        """
        return self._screen_height / 2

    def get_window_size(self) -> tuple[int, int]:
        """
        Renvoie les dimensions de la fenêtre
        """
        return (self._window_width, self._window_height)

    def get_window_resizable(self) -> bool:
        """
        Vérifie si la fenêtre est redimensionnable
        """
        return self._window_resizable
    
    @property
    def scale(self) -> float:
        """
        Renvoie le rapport entre écran virtuel et écran réel
        """
        return self._screen_resized_width / self._screen_width
    
    @property
    def offset_x(self) -> float:
        """
        Renvoie la largeur des bandes noires verticales
        """
        return self._screen_resized_x_offset
    
    @property
    def offset_y(self) -> float:
        """
        Renvoie la hauteur des bandes noires horizontales
        """
        return self._screen_resized_y_offset
    
    def get_vsync(self) -> bool:
        """
        Vérifie l'utilisation de la vsync
        """
        return self._vsync

    # ======================================== SETTERS ========================================
    def set_caption(self, caption: str):
        """
        Fixe le titre de la fenêtre

        Args:
            caption (str) : nouveau titre de la fenêtre
        """
        if not isinstance(caption, str):
            self._raise_error('set_caption', 'Window caption type must be str')    
        pygame.display.set_caption(caption)

    def set_icon(self, icon: pygame.Surface):
        """
        Fixe le logo de la fenêtre

        Args:
            icon (pygame.Surface) : nouveau logo de la fenêtre
        """
        if not isinstance(icon, pygame.Surface):
            self._raise_error('set_icon', 'Window icon must be a Surface object')    
        pygame.display.set_icon(icon)
    
    def set_window_resizable(self, value: bool):
        """
        Fixe la possibilité de redimensionner la fenêtre

        Args:
            value (bool) : activation ou non du redimensionnement
        """
        if not isinstance(value, bool):
            self._raise_error('set_window_resizable', 'resizable parameter must be a boolean')
        self._window_resizable = value
        if self._fullscreen:
            return
        self._window = pygame.display.set_mode((self._window_width, self._window_height), pygame.RESIZABLE if self._window_resizable else 0, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=self._vsync)

    def set_smooth_rendering(self, value: bool):
        """
        Fixe le type de rendu
        
        Args:
            value (bool) : activation ou non du rendu vectoriel
        """
        if not isinstance(value, bool):
            self._raise_error('set_smooth_rendering', 'Value type must be boolean')
        self._smooth_rendering = value

    def set_vsync(self, value: bool):
        """
        Fixe l'utilisation de la vsync

        Args:
            value (bool) : vsync activée ou non
        """
        if not isinstance(value, bool):
            self._raise_error('set_vsync', 'Value type must be boolean')
        self._vsync = value
        self.recreate()
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def create(self, screen: tuple[int]=(1920, 1080), window: tuple[int]=(1280, 720)):
        """
        Crée une instance de l'écran
        """
        if not self._opened:
            self._init__(screen=screen, window=window)
    
    def recreate(self):
        """
        Recrée une instance de l'écran
        """
        size = (0, 0) if self._fullscreen else (self._window_width, self._window_height)
        behavior = pygame.FULLSCREEN if self._fullscreen else pygame.RESIZABLE
        vsync = int(self._vsync)
        self._window = pygame.display.set_mode(size, behavior, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=vsync)
    
    def close(self):
        """
        Ferme une instance de l'écran
        """
        if self._opened:
            self._opened = False
            pygame.display.quit()
            pygame.quit()

    def resize_window(self, size : tuple[int, int]=(0, 0), resizable: bool=True):
        """
        Force le redimensionnement de la fenêtre

        Args :
            size (tuple[int, int]) : nouvelles dimensions de la fenêtre
            resizable (bool) : fenêtre redimensionnable ou non
        """
        if not (isinstance(size, tuple) and all(isinstance(e, int) for e in size)):
            self._raise_error('resize_window', 'Window size must be a tuple containing int values')
        if not isinstance(resizable, bool):
            self._raise_error('resize_window', 'resizable parameter must be a boolean')
        self._window_resizable = resizable
        os.environ['SDL_VIDEO_CENTERED'] = '1'                                                                              # recentrage de la fenêtre
        self._window = pygame.display.set_mode(size, pygame.RESIZABLE if self._window_resizable else 0, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=self._vsync)
        self._update_screen()
   
    def toggle_fullscreen(self, fullscreen: bool=None):
        """
        Bascule entre mode fenêtré et plein écran

        Args :
            fullscreen (bool) : mise sur une position forcée
        """
        if fullscreen is None:                                                                                              # alternance
            self._fullscreen = not self._fullscreen
        else:                                                                                                               # mise sur une position forcée
            self._fullscreen = fullscreen
        
        if self._fullscreen:                                                                                               # passage en plein écran
            self._windowed_width, self._windowed_height = self._window_width, self._window_height                       # sauvegarde des dimensions de la fenêtre
            self._window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=self._vsync)
        else:                                                                                                               # passage en mode fenêtré
            os.environ['SDL_VIDEO_CENTERED'] = '1'                                                                          # recentrage de la fenêtre
            self._window = pygame.display.set_mode((self._windowed_width, self._windowed_height), pygame.RESIZABLE if self._window_resizable else 0, pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=self._vsync)

        self._update_screen()                                                                                               # recalcul des dimensions

    def clear(self, color=(0,0,0)):
        """
        Nettoie l'écran virtuel en le remplissant d'une couleur

        Args:
            color (tuple[int, int, int]) : couleur de remplissage
        """
        self._screen.fill(color)

    def window_to_screen(self, pos: tuple[float, float]) -> tuple[float, float]:
        """
        Convertit les positions de la fenêtre à l'écran virtuel

        Args :
            pos (tuple[float, float]) : position sur la fenêtre
        """
        if not isinstance(pos, tuple) or not all(isinstance(e, (int, float)) for e in pos):
            self._raise_error('window_to_screen', 'Position must be a tuple containing int or float values')
        x, y = pos
        return (
            (x - self._screen_resized_x_offset) / self.scale,
            (y - self._screen_resized_y_offset) / self.scale
        )
    
    def screen_to_window(self, pos: tuple[float, float]) -> tuple[float, float]:
        """
        Convertit les positions de l'écran virtuel à la fenêtre

        Args :
            pos (tuple[float, float]) : position sur l'écran virtuel
        """
        if not isinstance(pos, tuple) or not all(isinstance(e, (int, float)) for e in pos):
            self._raise_error('screen_to_window', 'Position must be a tuple containing int or float values')
        x, y = pos
        return (
            x * self.scale + self._screen_resized_x_offset,
            y * self.scale + self._screen_resized_y_offset
        )
    
    def subsurface(self, rect: pygame.Rect) -> pygame.Surface:
        """
        Renvoie une vue partielle de l'écran

        Args :
            rect (pygame.Rect) : position et dimension de la vue
        """
        return self._screen.subsurface(rect).copy()

    def screenshot(self, path: str = None) -> pygame.Surface:
        """
        Prend une capture de l'écran virtuel
        
        Args:
            path (str) : chemin de sauvegarde
        """
        if not isinstance(path, str) and path is not None:
            self._raise_error('screenshot', 'Path type must be str')
        capture = self._screen.copy()
        if path:
            pygame.image.save(capture, path)
        return capture


# ======================================== INSTANCE ========================================
screen_manager = ScreenManager()