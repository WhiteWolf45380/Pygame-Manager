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

    def init(self):
        """
        Initialise Pygame et lance le loader progressif si fourni

        Args:
            loader (callable) : fonction d'initialisation supplémentaire (mettre des yield entre les étapes)
        """
        if self._initialized: # déjà initialisé
            return self

        # création de la fenêtre
        self.screen.create()

        # toggle fullscreen
        self.inputs.add_listener(pygame.K_F11, self.screen.toggle_fullscreen)

        # confirmation
        self._initialized = True
        return self

    def run(self, update):
        """Lance la boucle d'éxécution"""
        # Vérifications
        if not self._initialized:
            self._raise_error("run", "Engine not initialized. Call init() first.")
        if not callable(update):
            self._raise_error("run", "update must be callable")

        # Boucle principale
        self._running = True
        while self._running:
            self.time.tick()

            # Permet l'affichage à l'écran
            with self.screen:
                # Entrées utilisateur
                self.mouse._update()
                if not self.inputs.check_all():
                    break

                # Actualisation
                update()
                self.states.update()
                self.panels.update()
                self.entities.update()
                self.ui.update()

                # Affichage
                self.panels.draw_back()
                self.entities.draw()
                self.ui.draw()
                self.panels.draw()

        # Fin d'éxécution
        self.stop()

    def stop(self):
        """Mets fin à la boucle d'éxécution"""
        if self._running:
            self._running = False
            self.screen.close()
            pygame.quit()