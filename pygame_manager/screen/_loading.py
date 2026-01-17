import pygame
import os

# ======================================== GESTIONNAIRE ========================================
class LoadingHandler:
    """Gestionnaire de l'animation de chargement"""
    def __init__(self, screen, folder_path: str = "_loading_frames", text: str = "Chargement...", icon_size=(50, 50)):
        """
        Initialise le gestionnaire de loading

        Args :
            - screen : surface pygame sur laquelle dessiner
            - folder_path (str) : chemin relatif vers le dossier des frames du logo
            - text (str) : texte de chargement
            - icon_size (tuple) : taille (width, height) des frames de l'icône
        """
        self.__screen = screen
        self.__icon_size = icon_size

        # chemin du module courant
        current_dir = os.path.dirname(__file__)
        frames_dir = os.path.join(current_dir, folder_path)

        # chargement des frames
        self.__frames = []
        for file in sorted(os.listdir(frames_dir)):
            if file.endswith(".png"):
                path = os.path.join(frames_dir, file)
                image = pygame.image.load(path).convert_alpha()
                # redimensionner
                image = pygame.transform.scale(image, self.__icon_size)
                self.__frames.append(image)

        if not self.__frames:
            raise RuntimeError("Aucune frame trouvée pour le loader !")

        self.__current_frame = 0
        self.__text = text
        self.__font = pygame.font.SysFont(None, 36)
        self.__text_surface = self.__font.render(self.__text, True, (255, 255, 255))

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur

        Args :
            - method (str) : méthode dans laquelle l'erreur survient
            - text (str) : message d'erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== METHODES INTERACTIVES ========================================
    def update(self):
        """
        Mise à jour de l'écran de chargement
        """
        if not self.__screen:
            self._raise_error("update", "Screen non défini")

        # fond noir
        self.__screen.fill((0, 0, 0))

        # afficher le texte
        text_rect = self.__text_surface.get_rect(topleft=(20, 20))
        self.__screen.blit(self.__text_surface, text_rect)

        # affichage de la frame actuelle de l'animation
        frame = self.__frames[self.__current_frame]
        rect = frame.get_rect(bottomright=(self.__screen.get_width() - 20,
                                           self.__screen.get_height() - 20))
        self.__screen.blit(frame, rect)

        # passage à la frame suivante
        self.__current_frame = (self.__current_frame + 1) % len(self.__frames)

        pygame.display.flip()  # ou pygame.display.update([text_rect, rect]) pour plus de performance

    def set_text(self, text: str):
        """
        Modifie le texte de chargement

        Args :
            - text (str) : texte de chargement
        """
        if not isinstance(text, str):
            self._raise_error('set_text', 'Text type must be str')
        self.__text = text
        self.__text_surface = self.__font.render(self.__text, True, (255, 255, 255))

    def set_icon(self, folder_path: str, icon_size=None):
        """
        Modifie l'icone de chargement

        Args :
            - folder_path (str) : chemin du dossier vers les frames de l'icone
            - icon_size (tuple, optional) : nouvelle taille des frames (width, height)
        """
        if not isinstance(folder_path, str):
            self._raise_error('set_icon', 'Folder must be a folder path')

        if icon_size:
            self.__icon_size = icon_size

        current_dir = os.path.dirname(__file__)
        frames_dir = os.path.join(current_dir, folder_path)

        # chargement des frames
        self.__frames = []
        for file in sorted(os.listdir(frames_dir)):
            if file.endswith(".png"):
                path = os.path.join(frames_dir, file)
                image = pygame.image.load(path).convert_alpha()
                image = pygame.transform.scale(image, self.__icon_size)
                self.__frames.append(image)

        if not self.__frames:
            self._raise_error("set_icon", "Aucune frame trouvée dans ce dossier !")

        self.__current_frame = 0
