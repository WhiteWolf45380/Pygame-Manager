import pygame
import os


class LoadingManager:
    """Gestionnaire de l'animation de chargement."""

    def __init__(self, folder_path: str = "_loading_frames", text: str = "Chargement...", icon_size=(50, 50)):
        """
        Args:
            folder_path : chemin relatif au dossier contenant les frames PNG
            text : texte à afficher
            icon_size : taille (width, height) des frames
        """
        self._icon_size = icon_size

        # déterminer le chemin absolu des frames
        current_dir = os.path.dirname(__file__)
        frames_dir = os.path.join(current_dir, folder_path)

        # chargement des frames
        self._frames = []
        for file in sorted(os.listdir(frames_dir)):
            if file.endswith(".png"):
                path = os.path.join(frames_dir, file)
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, self._icon_size)
                self._frames.append(image)

        if not self._frames:
            raise RuntimeError("Aucune frame trouvée pour le loader !")

        self._current_frame = 0
        self._text = text
        self._font = pygame.font.SysFont(None, 36)
        self._text_surface = self._font.render(self._text, True, (255, 255, 255))

    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def update(self, screen: pygame.Surface):
        """Met à jour l'écran de chargement."""
        # fond noir
        self._screen.fill((0, 0, 0))

        # afficher le texte
        text_rect = self._text_surface.get_rect(topleft=(20, 20))
        self._screen.blit(self._text_surface, text_rect)

        # afficher la frame actuelle
        frame = self._frames[self._current_frame]
        rect = frame.get_rect(
            bottomright=(self._screen.get_width() - 20, self._screen.get_height() - 20)
        )
        self._screen.blit(frame, rect)

        # passer à la frame suivante
        self._current_frame = (self._current_frame + 1) % len(self._frames)

        pygame.display.flip()

    def set_text(self, text: str):
        """Modifier le texte de chargement."""
        if not isinstance(text, str):
            self._raise_error("set_text", "Text type must be str")
        self._text = text
        self._text_surface = self._font.render(self._text, True, (255, 255, 255))

    def set_icon(self, folder_path: str, icon_size=None):
        """Modifier les frames de l'animation."""
        if not isinstance(folder_path, str):
            self._raise_error("set_icon", "Folder must be a folder path")
        if icon_size:
            self._icon_size = icon_size

        current_dir = os.path.dirname(__file__)
        frames_dir = os.path.join(current_dir, folder_path)

        self._frames = []
        for file in sorted(os.listdir(frames_dir)):
            if file.endswith(".png"):
                path = os.path.join(frames_dir, file)
                image = pygame.image.load(path)
                image = pygame.transform.scale(image, self._icon_size)
                self._frames.append(image)

        if not self._frames:
            self._raise_error("set_icon", "Aucune frame trouvée dans ce dossier !")

        self._current_frame = 0