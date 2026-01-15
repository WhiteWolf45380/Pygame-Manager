import os
import math
try:
    import pygame
except ImportError:
    raise RuntimeError("[ScreenManager] requieres pygame to work normally\nTry to download it with : pip install pygame")


# ======================================== PORTAIL ========================================
class ScreenGate:
    """
    Portail d'accès au gestionnaire de l'affichage
    """
    def __init__(self):
        self.__screen = None

    def __getattr__(self, name):
        if self.__screen is None:
            raise AttributeError(f"ScreenManager not initialized. Call 'create()' first.")
        return getattr(self.__screen, name)

    def __enter__(self):
        """Délègue au manager"""
        if self.__screen:
            return self.__screen.__enter__()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Délègue au manager"""
        if self.__screen:
            return self.__screen.__exit__(exc_type, exc_val, exc_tb)

    def create(self, screen: tuple[int]=(1920, 1080), window: tuple[int]=(1280, 720)):
        """
        Crée une instance de l'écran
        """
        if self.__screen is None:
            self.__screen = ScreenManager(screen=screen, window=window)
    
    def close(self):
        """
        Ferme une instance de l'écran
        """
        if self.__screen:
            self.__screen.close_window()
            self.__screen = None


# ======================================== GESTIONNAIRE ========================================
class ScreenManager:
    """
    Gestionnaire pygame de l'affichage

    Fonctionnalités:
    - gère semi-automatiquement l'écran et la fenêtre (nécessite de wrapper le dessin dans un with)
    - supporte la quasi totalité des méthodes de pygame.Surface
    - facilite grandement le paramètrage et la maintenance de la fenêtre
    - permet un transformation automatique de l'écran virtuel vers la fenêtre réel
    """
    def __init__(self, screen: tuple[int]=(1920, 1080), window: tuple[int]=(1280, 720)):
        # initialisation
        if not pygame.get_init():
            pygame.init()
        
        # écran virtuel
        self.__screen_width = screen[0]
        self.__screen_height = screen[1]
        self.__screen = pygame.Surface((self.__screen_width, self.__screen_height))
        self.__screen.fill((255, 255, 255))

        # écran intermédiaire (taille réelle mais sans bandes noires)
        self.__screen_resized_width = self.__screen_width
        self.__screen_resized_height = self.__screen_height
        self.__screen_resized_x_offset = 0                                                                          # bandes verticales
        self.__screen_resized_y_offset = 0                                                                          # bandes horizontales

        # fenêtre pygame
        self.__window_width = window[0]
        self.__window_height = window[1]
        self.__window = pygame.display.set_mode((self.__window_width, self.__window_height), pygame.RESIZABLE)
        self.__window_resizable = True                                                                              # possibilité de redimensionner la fenêtre

        # plein écran
        self.__fullscreen = False
        self.__windowed_width = self.__window_width                                                                 # sauvegarde de la dernière largeur
        self.__windowed_height = self.__window_height                                                               # sauvegarde de la dernière hauteur

        # paramètres
        self.__smooth_rendering = True                                                                              # utilisation du smoothscale pour le redimensionnement

        # curseur
        self.__mouse_icon = None                                                                                    # logo du curseur
        self.__mouse_icon_scaled = None                                                                             # logo du curseur redimensionné
        self.__mouse_icon_centered = False                                                                          # centrage ou non du logo du curseur
        self.__mouse_last_scale = 0                                                                                 # cache du dernier scale pour optimiser les calculs
        self.__mouse_visible = True                                                                                 # visibilité du curseur
        self.__mouse_out = False                                                                                    # curseur en dehors de l'écran
        self.__mouse_x = 0                                                                                          # position x du curseur
        self.__mouse_y = 0                                                                                          # position y du curseur

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
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
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
            raise AttributeError(f"{self.__class__.__name__}: access to Surface.{name} is forbidden")
        return getattr(self.__screen, name)
    
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
        self._update_screen()
        self._update_mouse()

    def _flip(self):
        """
        Méthode appelée à la fin du with
        """
        # redimensionnement
        if not self.__smooth_rendering:                                                                                                      # rendu pixelisé
            self.__screen_resized = pygame.transform.scale(self.__screen, (self.__screen_resized_width, self.__screen_resized_height))
        else:                                                                                                                                # rendu vectoriel
            self.__screen_resized = pygame.transform.smoothscale(self.__screen, (self.__screen_resized_width, self.__screen_resized_height))
        self.__window.fill((0, 0, 0))                                                                                                        # bandes noires
        self.__window.blit(self.__screen_resized, (self.__screen_resized_x_offset, self.__screen_resized_y_offset))

        # affichage curseur
        self._draw_mouse()

        # actualisation
        pygame.display.flip()
    
    def _update_screen(self):
        """
        Met à jour l'écran
        """
        # récupération des dimensions de la fenêtre réelle
        self.__window_width = self.__window.get_width()
        self.__window_height = self.__window.get_height()

        # on prend le ratio min
        if self.__screen_width == 0 or self.__screen_height == 0:
            self._raise_error('_update_screen', 'Screen size cannot be set to zero')
        scale = min(
            self.__window_width / self.__screen_width,
            self.__window_height / self.__screen_height
        )

        # calcul de la taille redimensionnée de l'écran
        self.__screen_resized_width = int(self.__screen_width * scale)
        self.__screen_resized_height = int(self.__screen_height * scale)

        # calcul des décalages pour les bandes noires
        self.__screen_resized_x_offset = (self.__window_width - self.__screen_resized_width) // 2
        self.__screen_resized_y_offset = (self.__window_height - self.__screen_resized_height) // 2
    
    def _update_mouse(self):
        """
        Met à jour la position du curseur
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        left, right = self.__screen_resized_x_offset, self.__screen_resized_x_offset + self.__screen_resized_width          # bords horizontaux
        top, bottom = self.__screen_resized_y_offset, self.__screen_resized_y_offset + self.__screen_resized_height         # bords verticaux
        if not left <= mouse_x <= right or not top <= mouse_y <= bottom :                                                   # limites de l'écran
            self.__mouse_out = True
        else:
            self.__mouse_out = False
        self.__mouse_x = (mouse_x - self.__screen_resized_x_offset) / self.scale                                            # conversion de la coordonée x
        self.__mouse_y = (mouse_y - self.__screen_resized_y_offset) / self.scale                                            # conversion de la coordonée y

    def _draw_mouse(self):
        """
        Affiche le curseur curstomisé
        """
        if self.__mouse_icon and not self.__mouse_out and self.__mouse_visible:
            if self.scale != self.__mouse_last_scale:
                s = 0.8 + 0.4 / (1 + math.exp(-4 * (self.scale - 1)))                                                                    # scale sigmoïdal doux
                w, h = self.__mouse_icon.get_size()
                self.__mouse_icon_scaled = pygame.transform.smoothscale(self.__mouse_icon, (int(w * s), int(h * s)))
                self.__mouse_last_scale = self.scale
            mx, my = pygame.mouse.get_pos()
            if self.__mouse_icon_centered:
                self.__window.blit(self.__mouse_icon_scaled, (mx - self.__mouse_icon_scaled.get_width()//2, my - self.__mouse_icon_scaled.get_height()//2))
            else:
                self.__window.blit(self.__mouse_icon_scaled, (mx, my))

    # ======================================== GETTERS ========================================
    def get_screen_size(self) -> tuple[int, int]:
        """
        Renvoie les dimensions de l'écran virtuel
        """
        return (self.__screen_width, self.__screen_height)

    def get_window_size(self) -> tuple[int, int]:
        """
        Renvoie les dimensions de la fenêtre
        """
        return (self.__window_width, self.__window_height)

    def get_window_resizable(self) -> bool:
        """
        Vérifie si la fenêtre est redimensionnable
        """
        return self.__window_resizable
    
    @property
    def scale(self) -> float:
        """
        Renvoie le rapport entre écran virtuel et écran réel
        """
        return self.__screen_resized_width / self.__screen_width
    
    @property
    def offset_x(self) -> float:
        """
        Renvoie la largeur des bandes noires verticales
        """
        return self.__screen_resized_x_offset
    
    @property
    def offset_y(self) -> float:
        """
        Renvoie la hauteur des bandes noires horizontales
        """
        return self.__screen_resized_y_offset

    def get_mouse_pos(self) -> tuple[float, float]:
        """
        Renvoie les coordonnées du curseur
        """
        return (self.__mouse_x, self.__mouse_y)
    
    @property
    def mouse_x(self) -> float:
        """
        Renvoie la position horizontale du curseur
        """
        return self.__mouse_x
    
    @property
    def mouse_y(self) -> float:
        """
        Renvoie la position verticale du curseur
        """
        return self.__mouse_y
    
    def get_mouse_grab(self) -> bool:
        """
        Vérifie si le maintient du curseur est activé
        """
        return pygame.event.get_grab()
    
    def get_mouse_visible(self) -> bool:
        """
        Vérifie la visibilité du curseur
        """
        return self.__mouse_visible

    def window_to_screen(self, pos: tuple[float, float]) -> tuple[float, float]:
        """
        Convertit les positions de la fenêtre à l'écran virtuel

        Args :
            - pos (tuple[float, float]) : position sur la fenêtre
        """
        if not isinstance(pos, tuple) or not all(isinstance(e, (int, float)) for e in pos):
            self._raise_error('window_to_screen', 'Position must be a tuple containing int or float values')
        x, y = pos
        return (
            (x - self.__screen_resized_x_offset) / self.scale,
            (y - self.__screen_resized_y_offset) / self.scale
        )
    
    def screen_to_window(self, pos: tuple[float, float]) -> tuple[float, float]:
        """
        Convertit les positions de l'écran virtuel à la fenêtre

        Args :
            - pos (tuple[float, float]) : position sur l'écran virtuel
        """
        if not isinstance(pos, tuple) or not all(isinstance(e, (int, float)) for e in pos):
            self._raise_error('screen_to_window', 'Position must be a tuple containing int or float values')
        x, y = pos
        return (
            x * self.scale + self.__screen_resized_x_offset,
            y * self.scale + self.__screen_resized_y_offset
        )
    
    def subsurface(self, rect: pygame.Rect) -> pygame.Surface:
        """
        Renvoie une vue partielle de l'écran

        Args :
            - rect (pygame.Rect) : position et dimension de la vue
        """
        return self.__screen.subsurface(rect).copy()

    # ======================================== SETTERS ========================================
    def set_caption(self, caption: str):
        """
        Fixe le titre de la fenêtre

        Args :
            - caption (str) : nouveau titre de la fenêtre
        """
        if not isinstance(caption, str):
            self._raise_error('set_caption', 'Window caption type must be str')    
        pygame.display.set_caption(caption)

    def set_icon(self, icon: pygame.Surface):
        """
        Fixe le logo de la fenêtre

        Args :
            - icon (pygame.Surface) : nouveau logo de la fenêtre
        """
        if not isinstance(icon, pygame.Surface):
            self._raise_error('set_icon', 'Window icon must be a Surface object')    
        pygame.display.set_icon(icon)
    
    def set_window_resizable(self, value: bool):
        """
        Fixe la possibilité de redimensionner la fenêtre

        Args :
            - value (bool) : activation ou non du redimensionnement
        """
        if not isinstance(value, bool):
            self._raise_error('set_window_resizable', 'resizable parameter must be a boolean')
        self.__window_resizable = value
        if self.__fullscreen:
            return
        self.__window = pygame.display.set_mode((self.__window_width, self.__window_height), pygame.RESIZABLE if self.__window_resizable else 0)

    def set_smooth_rendering(self, value: bool):
        """
        Fixe le type de rendu
        
        Args :
            - value (bool) : activation ou non du rendu vectoriel
        """
        if not isinstance(value, bool):
            self._raise_error('set_smooth_rendering', 'Value type must be boolean')
        self.__smooth_rendering = value
    
    def set_mouse_icon(self, icon: pygame.Surface | None, centered: bool=False):
        """
        Fixe le logo de la souris

        Args :
            - icon (pygame.Surface) : nouvelle image de la souris
            - centered (bool) : icon du curseur centré ou non
        """
        if icon is None:
            self.__mouse_icon = None
            pygame.mouse.set_visible(self.__mouse_visible)
            return
        if not isinstance(icon, pygame.Surface):
            self._raise_error('set_mouse_icon', 'Mouse icon must be a Surface object')
        if not isinstance(centered, bool):
            self._raise_error('set_mouse_icon', 'Centered parameter must be a boolean')
        self.__mouse_icon = icon
        pygame.mouse.set_visible(False)
        self.__mouse_icon_centered = centered

    def set_mouse_grab(self, value: bool):
        """
        Fixe le maintient du curseur dans la fenêtre

        Args :
            - value (bool) : maintient ou non du curseur
        """
        if not isinstance(value, bool):
            self._raise_error('set_mouse_grab', 'Value type must be boolean')
        pygame.event.set_grab(value)
    
    def set_mouse_visible(self, value: bool):
        """
        Fixe la visibilité du curseur

        Args :
            - value (bool) : curseur visible ou non
        """
        if not isinstance(value, bool):
            self._raise_error('set_mouse_visible', 'Value type must be boolean')
        self.__mouse_visible = value
        pygame.mouse.set_visible(value and self.__mouse_icon is None)
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def resize_window(self, size : tuple[int, int]=(0, 0), resizable: bool=True):
        """
        Force le redimensionnement de la fenêtre

        Args :
            - size (tuple[int, int]) : nouvelles dimensions de la fenêtre
            - resizable (bool) : fenêtre redimensionnable ou non
        """
        if not (isinstance(size, tuple) and all(isinstance(e, int) for e in size)):
            self._raise_error('resize_window', 'Window size must be a tuple containing int values')
        if not isinstance(resizable, bool):
            self._raise_error('resize_window', 'resizable parameter must be a boolean')
        self.__window_resizable = resizable
        os.environ['SDL_VIDEO_CENTERED'] = '1'                                                                              # recentrage de la fenêtre
        self.__window = pygame.display.set_mode(size, pygame.RESIZABLE if self.__window_resizable else 0)
        self._update_screen()
   
    def toggle_fullscreen(self, fullscreen: bool=None):
        """
        Bascule entre mode fenêtré et plein écran

        Args :
            - fullscreen (bool) : mise sur une position forcée
        """
        if fullscreen is None:                                                                                              # alternance
            self.__fullscreen = not self.__fullscreen
        else:                                                                                                               # mise sur une position forcée
            self.__fullscreen = fullscreen
        
        if self.__fullscreen:                                                                                               # passage en plein écran
            self.__windowed_width, self.__windowed_height = self.__window_width, self.__window_height                       # sauvegarde des dimensions de la fenêtre
            self.__window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:                                                                                                               # passage en mode fenêtré
            os.environ['SDL_VIDEO_CENTERED'] = '1'                                                                          # recentrage de la fenêtre
            self.__window = pygame.display.set_mode((self.__windowed_width, self.__windowed_height), pygame.RESIZABLE if self.__window_resizable else 0)

        self._update_screen()                                                                                               # recalcul des dimensions

    def clear(self, color=(0,0,0)):
        """
        Nettoie l'écran virtuel en le remplissant d'une couleur

        Args:
            - color (tuple[int, int, int]) : couleur de remplissage
        """
        self.__screen.fill(color)

    def screenshot(self, path: str = None) -> pygame.Surface:
        """
        Prend une capture de l'écran virtuel
        
        Args:
            - path (str) : chemin de sauvegarde
        """
        if not isinstance(path, str) and path is not None:
            self._raise_error('screenshot', 'Path type must be str')
        capture = self.__screen.copy()
        if path:
            pygame.image.save(capture, path)
        return capture

    def close_window(self):
        """
        Fermeture de la fenêtre
        """
        pygame.display.quit()
        pygame.quit()


"""
Exemple d'utilisation :

import pygame
from screen_manager import ScreenManager

def main():
    screen = ScreenManager(screen=(800, 600), window=(1280, 720), fps=60)
    screen.set_caption("Mon Super Jeu")
    
    # Callback de redimensionnement
    def on_window_resize(scale, w, h):
        print(f"Fenêtre redimensionnée: {w}x{h} (échelle {scale:.2f}x)")
    screen.on_resize(on_window_resize)
    
    # Variables de jeu
    player_pos = [400, 300]
    player_speed = 200
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        # Événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen.toggle_fullscreen()
                elif event.key == pygame.K_F3:
                    screen.toggle_debug()
                elif event.key == pygame.K_F12:
                    screen.screenshot(f"screenshot_{pygame.time.get_ticks()}.png")
        
        # Frame automatique !
        with screen:
            screen.clear((30, 30, 50))
            
            # Mouvement avec delta_time
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_pos[0] -= player_speed * screen.delta_time
            if keys[pygame.K_RIGHT]:
                player_pos[0] += player_speed * screen.delta_time
            if keys[pygame.K_UP]:
                player_pos[1] -= player_speed * screen.delta_time
            if keys[pygame.K_DOWN]:
                player_pos[1] += player_speed * screen.delta_time
            
            # Dessin du joueur
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(player_pos[0]), int(player_pos[1])), 20)
            
            # Bouton cliquable
            button_rect = pygame.Rect(350, 500, 100, 40)
            button_color = (100, 200, 100) if screen.is_mouse_over(button_rect) else (50, 150, 50)
            pygame.draw.rect(screen, button_color, button_rect)
            
            if screen.is_clicked(button_rect):
                print("Bouton cliqué!")
            
            # Texte
            font = pygame.font.Font(None, 36)
            text = font.render(f"FPS: {screen.fps:.0f}", True, (255, 255, 255))
            screen.blit(text, (10, 10))
            
    screen.close_window()
"""