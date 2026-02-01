# ======================================== IMPORTS ========================================
from ._core import *
from ._rect_button import RectButtonObject

# ======================================== GESTIONNAIRE ========================================
class UiManager:
    """
    Gestionnaire pygame de l'interface utilisateur

    Fonctionnalités:
        créer des éléments pygame de l'ui
        manipuler ces éléments
        les actualiser
    """
    OBJECTS = [RectButtonObject]
    def __init__(self):
        self._objects = []  # stockage de toutes les instances d'objet

        # ensemble des objets disponibles
        self.RectButton = RectButtonObject

    # ======================================== METHODES PRIVEES ========================================
    def _append(self, obj: object):
        """Enregistrement d'un objet"""
        if not isinstance(obj, self.OBJECTS):
            _raise_error(self, '_append', 'Invalid obj argument')
        self._objects.append(obj)

    # ======================================== METHODES INTERACTIVES ========================================
    def update(self):
        """Actualisation par frame"""
        for obj in self._objects:
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw()

# ======================================== INSTANCE ========================================
ui_manager = UiManager()