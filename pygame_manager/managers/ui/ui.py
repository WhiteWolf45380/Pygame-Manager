# ======================================== IMPORTS ========================================
from ._core import *
from ._rect_button import RectButtonObject
from ._circle_button import CircleButtonObject
from ._rect_selector import RectSelectorObject
from ._circle_selector import CircleSelectorObject
from ._text_case import TextCaseObject
from ._section import SectionObject
from ._text import TextObject
from ._image import ImageObject
from ._overlay import OverlayObject
from ._scrollbar import ScrollBarObject

# ======================================== GESTIONNAIRE ========================================
class UiManager:
    """
    Gestionnaire pygame de l'interface utilisateur

    Fonctionnalités:
        créer des éléments pygame de l'ui
        manipuler ces éléments
        les actualiser
    """
    def __init__(self):
        self._objects = []              # ensemble des objets
        self._hovered_object = None     # objet survolé

        self._selections = {}           # {"id_selection": "id_selector", ...}
        self._selections_limits = {}    # {"id_selection": selectors_limit}

        # Ensemble des objets disponibles
        self.RectButton = RectButtonObject
        self.CircleButton = CircleButtonObject
        self.RectSelector = RectSelectorObject
        self.CircleSelector = CircleSelectorObject
        self.TextCase = TextCaseObject
        self.Section = SectionObject
        self.Text = TextObject
        self.Image = ImageObject
        self.Overlay = OverlayObject
        self.ScrollBar = ScrollBarObject

    def _init(self):
        """Initialisation sécurisée"""
        context.inputs.add_listener(1, self._click_down, args=[self], up=False)
        context.inputs.add_listener(1, self._click_up, args=[self], up=True)
        context.inputs.add_listener(3, self._click_down, args=[self], up=False)
        context.inputs.add_listener(3, self._click_up, args=[self], up=True)

        for obj in self._objects:
            if hasattr(obj, '_init') and callable(obj._init):
                obj._init()

    # ======================================== METHODES PRIVEES ========================================
    # Objets
    def _sort(self):
        """Tri des objets par zorder"""
        self._objects = sorted(self._objects, key=lambda o: getattr(o, 'zorder', 0), reverse=True)

    def _append(self, obj: object):
        """Enregistrement d'un objet en maintenant l'ordre z"""
        self._objects.append(obj)
        self._objects.sort(key=lambda o: getattr(o, 'zorder', 0))
    
    # Souris
    def _update_hover(self):
        """Actualise le survol"""
        hovered_panel = context.panels.hovered
        self._hovered_object = None
        for obj in reversed(self._objects):
            if obj.panel == hovered_panel and obj.collidemouse():
                self._hovered_object = obj
                return

    def _click(self, key: int, up: bool = False):
        """Clic utilisateur"""
        if self._hovered_object is not None:
            if key == 1: name = 'left_click'
            elif key == 3: name = 'rightclick'
            else: return
            method = getattr(self._hovered_object, name)
            if method is not None and callable(method):
                method(up=up)
    
    def _click_down(self, key: int = None):
        """Pression"""
        self._click(key, up=False)
    
    def _click_up(self, key: int = None):
        """Relâchement"""
        self._click(key, up=True)

    # ======================================== METHODES PUBLIQUES ========================================
    def update(self):
        """Actualisation par frame"""
        self._update_hover()
        for obj in self._objects:
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()

    def draw(self):
        """Affichage pas frame"""
        for obj in self._objects:
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw()
    
    def get_hovered(self) -> object | None:
        """Renvoie l'objet survolé"""
        return self._hovered_object

    # Selectors
    def add_selection(self, id_selection: str, limit=1):
        """Ajoute une séléction"""
        if id_selection not in self._selections:
            self._selections[id_selection] = []
            self._selections_limits[id_selection] = limit
    
    def select(self, id_selection: str, id_selector: str):
        """Modifie une séléction"""
        if id_selection in self._selections and id_selector not in self._selections[id_selection]:
            self._selections[id_selection].append(id_selector)
            if len(self._selections[id_selection]) > self._selections_limits.get(id_selection, 1):
                self._selections[id_selection].pop(0)

    def unselect(self, id_selection: str, id_selector: str):
        """Remet une séléction à None"""
        if id_selection in self._selections and id_selector in self._selections[id_selection]:
            self._selections[id_selection].remove(id_selector)

    def get_selections(self) -> list[str]:
        """Renvoie l'ensemble des sélections"""
        return self._selections.keys()

    def get_selected(self, id_selection: str) -> list[str]:
        """Renvoie la liste des sélecteurs sélectionnés"""
        return self._selections.get(id_selection, [])

# ======================================== INSTANCE ========================================
ui_manager = UiManager()