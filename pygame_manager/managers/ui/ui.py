# ======================================== IMPORTS ========================================
from ._core import *
from ._rect_button import RectButtonObject
from ._circle_button import CircleButtonObject
from ._rect_selector import RectSelectorObject
from ._circle_selector import CircleSelectorObject
from ._text_case import TextCaseObject

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
        self._objects = []          # ensemble des objets
        self._hovered_object = None # objet survolé

        self._selections = {}       # {"id_selection": "id_selector", ...}

        # ensemble des objets disponibles
        self.RectButton = RectButtonObject
        self.CircleButton = CircleButtonObject
        self.RectSelector = RectSelectorObject
        self.CircleSelector = CircleSelectorObject
        self.TextCase = TextCaseObject

    # ======================================== METHODES PRIVEES ========================================
    def _sort(self):
        """Tri des objets par zorder"""
        self._objects = sorted(self._objects, key=lambda o: getattr(o, 'zorder', 0), reverse=True)

    def _append(self, obj: object):
        """Enregistrement d'un objet en maintenant l'ordre z"""
        self._objects.append(obj)
        self._objects.sort(key=lambda o: getattr(o, 'zorder', 0))

    def _add_selection(self, id_selection: str):
        """Ajoute une séléction"""
        if id_selection not in self._selections:
            self._selections[id_selection] = None
    
    def _select(self, id_selection: str, id_selector: str):
        """Modifie une séléction"""
        self._selections[id_selection] = id_selector

    def _unselect(self, id_selection: str):
        """Remet une séléction à None"""
        if id_selection in self._selections:
            self._selections[id_selection] = None

    # ======================================== METHODES INTERACTIVES ========================================
    def update(self):
        """Actualisation par frame"""
        self._update_hover()
        for obj in self._objects:
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw()

    def _update_hover(self):
        """Actualise le survol"""
        hovered_menu = context.menus.hovered
        self._hovered_object = None
        for obj in reversed(self._objects):
            if obj.menu == hovered_menu and obj.collidemouse():
                self._hovered_object = obj
                return

# ======================================== INSTANCE ========================================
ui_manager = UiManager()