import pygame
import sys


class PygameManager :

    def __init__(self):
        from .audio import AudioManager
        from .data import DataManager
        from .time import TimeManager
        from .languages import LanguagesManager
        from .screen import ScreenManager
        from.inputs import InputsManager

        self.screen = ScreenManager()
        self.time = TimeManager()
        self.audio = AudioManager()
        self.data = DataManager()
        self.languages = LanguagesManager()
        self.inputs = InputsManager()
        
        self._initialized = False
        self.running = False

    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def init(self):
        """
        Méthode d'initialisation des éléments pygame
        """
        if not self._initialized:
            if not pygame.get_init():
                pygame.init()
            self.screen.create()
            self._initialized = True
        return self
    
    def run(self, update: callable):
        """
        Lance la boucle principale

        Args :
            - update (method) : fonction appelée à chaque frame
        """
        if not self._initialized:
            self._raise_error('run', 'PygameManager is not initialized. Call pygame_manager.init() first.')
        if not callable(update):
            self._raise_error('run', 'update must be callable')

        self.running = True
        while self.running:
            self.time.tick()
            with self.screen:
                if self.screen.opened:
                    # entrées utilisateur
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False
                        self.inputs.check(event)
                
                # mise à jour
                update()

                if not self.running:
                    return
        
        self.stop()
    
    def stop(self):
        """
        Fermeture du programme pygame
        """
        if self.running:
            self.running = False
            self.screen.close()
            pygame.quit()

# instance principale
pygame_manager = PygameManager()

# raccourcis
screen = pygame_manager.screen
audio = pygame_manager.audio
data = pygame_manager.data
languages = pygame_manager.languages
time = pygame_manager.time
inputs = pygame_manager.inputs

init = pygame_manager.init
run = pygame_manager.run
stop = pygame_manager.stop

# export
__all__ = [
    "screen",
    "audio",
    "data",
    "languages",
    "time",
    "input"

    "init",
    "run",
    "stop"
]


"""
Syntaxe d'import depuis GitHub :
pip install git+https://github.com/WhiteWolf45380/pygame_managers.git
"""