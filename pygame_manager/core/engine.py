import pygame
from pygame_manager import managers

class Engine:
    def __init__(self):
        # instanciation auto des managers
        for manager_name in managers.__all__:
            manager_class = getattr(managers, manager_name)
            setattr(self, manager_name[:-7].lower(), manager_class())

        self._loader = None  # le loader sera optionnel
        self._initialized = False
        self.running = False

    def init(self, loader: callable = None):
        """
        Initialise Pygame et lance le loader progressif si fourni

        Args :
            - loader (callable) : fonction d'initialisation supplémentaire
        """
        if self._initialized:
            return self

        # initialisation minimale
        if not pygame.get_init():
            pygame.init()

        self.screen.create()

        # transformer loader en générateur
        if loader:
            if hasattr(loader, "__iter__") and not callable(loader):
                gen = loader
            else:
                # wrapper pour transformer fonction simple en générateur
                def wrapper():
                    loader()
                    yield
                gen = wrapper()

            # boucle de chargement progressive
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop()
                        return

                try:
                    next(gen) # avancement du loader
                except StopIteration:
                    break

                # mise à jour de l'écran de chargement
                if hasattr(self, "loading"):
                    self.loading.update()

        self._initialized = True
        return self


    def run(self, update):
        """
        Lance la boucle d'éxécution
        """
        if not self.__initialized:
            self._raise_error("run", "Engine not initialized. Call init() first.")
        if not callable(update):
            self._raise_error("run", "update must be callable")

        self.__running = True

        while self.__running:
            self.time.tick()

            with self.screen:
                if self.screen.opened:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.__running = False
                        self.inputs.check(event)

                update(self.time.dt)

            if not self.__running:
                break

        self.stop()

    def stop(self):
        """
        Mets fin à la boucle d'éxécution
        """
        if self.__running:
            self.__running = False
            self.screen.close()
            pygame.quit()