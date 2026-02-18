import pygame
from .. import context
from pygame_manager import managers

class Engine:
    def __init__(self):
        # initialisation minimale
        if not pygame.get_init():
            pygame.init()

        # exposition auto des managers
        for manager_name in managers.__all__:
            if manager_name.endswith("_manager"):
                manager_instance = getattr(managers, manager_name)
                attr = manager_name[:-8].lower()
                setattr(self, attr, manager_instance)
                setattr(context, attr, manager_instance)
        context.engine = self
    
        self._initialized = False
        self._running = False

    def _raise_error(obj: object, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

    def init(self):
        """Initialise Pygame Manager"""
        if self._initialized: # déjà initialisé
            return self

        # création de la fenêtre
        self.screen.create()

        # toggle fullscreen
        self.inputs.add_listener(pygame.K_F11, self.screen.toggle_fullscreen)

        # confirmation
        self._initialized = True

        # initialisation sécurisée des managers
        self.ui._init()

        return self

    def run(self, update, final: callable = None):
        """Lance la boucle d'éxécution"""
        # Vérifications
        if not self._initialized:
            self._raise_error("run", "Engine not initialized. Call init() first.")
        if not callable(update):
            self._raise_error("run", "update must be callable")
        if final is not None and not callable(final):
            self._raise_error("run", "final must be callable")

        # Boucle principale
        self._running = True
        try:
            while self._running:
                self.time.tick()

                # Permet l'affichage à l'écran
                with self.screen:
                    # Actualisation réseau
                    self.network.update()

                    # Entrées utilisateur
                    self.mouse.update()
                    self.inputs.check_all()

                    # Actualisation
                    update()
                    self.states.update()
                    self.panels.update()
                    self.entities.update()
                    self.ui.update()

                    # Affichage
                    self.panels.draw_back()
                    self.entities.draw()
                    self.panels.draw_between()
                    self.ui.draw()
                    self.panels.draw()
        finally:
            try:
                if final is not None:
                    final()
            finally:
                # Fin d'éxécution
                self.end()

    def stop(self):
        """Mets fin à la boucle d'éxécution"""
        if self._running:
            self._running = False
    
    def _end(self):
        """Ferme pygame"""
        self.screen.close()
        pygame.quit()