import pygame
from pygame_manager import managers


class Engine:
    def __init__(self):
        # instanciation automatique des managers
        for manager_name in managers.__all__:
            manager_class = getattr(managers, manager_name)
            # attribut accessible en minuscule
            setattr(self, manager_name[:-7].lower(), manager_class())

        self.__initialized = False
        self.__running = False

    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def init(self, loader: callable=None):
        """
        Chargement des différents objets

        Args :
            - loader (callable) : fonction de chargement supplémentaire
        """
        if self.__initialized:
            return self

        if not pygame.get_init():
            pygame.init()

        self.screen.create()

        if loader:
            if hasattr(loader, "__iter__") and not callable(loader):
                gen = loader
            else:
                def wrapper():
                    loader()
                    yield
                gen = wrapper()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop()
                        return self

                try:
                    next(gen)
                except StopIteration:
                    break

                self.screen.loading.update()

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