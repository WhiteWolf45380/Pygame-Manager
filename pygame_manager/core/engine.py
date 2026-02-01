import pygame
from pygame_manager import managers
from ..context import context

class Engine:
    def __init__(self):
        # initialisation minimale
        if not pygame.get_init():
            pygame.init()
    
        # instanciation auto des managers
        for manager_name in managers.__all__:
            if manager_name.endswith("_manager"):
                manager_instance = getattr(managers, manager_name)
                attr = manager_name[:-8].lower()
                setattr(self, attr, manager_instance)
                setattr(context, attr, manager_instance)
        context.engine = self
        self.__initialized = False
        self.__running = False

    def init(self):
        """
        Initialise Pygame et lance le loader progressif si fourni

        Args:
            loader (callable) : fonction d'initialisation supplémentaire (mettre des yield entre les étapes)
        """
        if self.__initialized: # déjà initialisé
            return self

        # création de la fenêtre
        self.screen.create()

        # toggle fullscreen
        self.inputs.add_listener(pygame.K_F11, self.screen.toggle_fullscreen)

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
                update()
                self.states.update()
                self.menus.update()
                self.ui.update()
                self.menus.draw()

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