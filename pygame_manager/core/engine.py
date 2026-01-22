import pygame
from pygame_manager import managers

class Engine:
    def __init__(self):
        # initialisation minimale
        if not pygame.get_init():
            pygame.init()
    
        # instanciation auto des managers
        for manager_name in managers.__all__:
            manager_instance = getattr(managers, manager_name)
            setattr(self, manager_name[:-8].lower(), manager_instance)

        self.__initialized = False
        self.__running = False

    def init(self):
        """
        Initialise Pygame et lance le loader progressif si fourni

        Args :
            - loader (callable) : fonction d'initialisation supplémentaire (mettre des yield entre les étapes)
        """
        if self.__initialized: # déjà initialisé
            return self

        # création de la fenêtre
        self.screen.create()

        # confirmation
        self.__initialized = True
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
                    self.__running = self.inputs.check_all()

                self.inputs.check_listeners()
                update()

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