import pygame


class PygameManager :

    def __init__(self):
        from .audio import AudioGate
        from .data import DataGate
        from .time import TimeGate
        from .languages import LanguagesGate
        from .screen import ScreenGate
        from.inputs import InputsGate

        self.screen = ScreenGate()
        self.time = TimeGate()
        self.audio = AudioGate()
        self.data = DataGate()
        self.languages = LanguagesGate()
        self.inputs = InputsGate
        
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
        if not self.initialized:
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
        if not isinstance(update, callable):
            self._raise_error('run', 'update must be callable')

        self.running = True
        while self.running:
            self.time.tick()
            with self.screen:
                # entrées utilisateur
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    self.inputs.check(event)
                
                # mise à jour
                update()
        
        self.stop()
    
    def stop(self):
        """
        Fermeture du programme pygame
        """
        pygame.quit()


# instance principale
pygame_manager = PygameManager()

# raccourcis pour imports partiels
screen = pygame_manager.screen
time = pygame_manager.time
audio = pygame_manager.audio
data = pygame_manager.data
languages = pygame_manager.languages
inputs = pygame_manager.inputs

# export
__all__ = [
    "pygame_manager",
    "screen",
    "time", 
    "audio",
    "data",
    "languages",
    "inputs"
]


"""
Syntaxe d'import depuis GitHub :
pip install git+https://github.com/WhiteWolf45380/pygame_managers.git
"""