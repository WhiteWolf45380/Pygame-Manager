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
from ._surface import SurfaceObject
from ._overlay import OverlayObject
from ._scrollbar import ScrollBarObject
from ._input_button import InputButtonObject

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
        self._filtered = []             # objets actifs
        self._hovered_object = None     # objet survolé

        self._selections = {}           # {"id_selection": "id_selector", ...}
        self._selections_limits = {}    # {"id_selection": selectors_limit}

        # Messages système
        self._system_messages = []
        self._message_spacing = 20
        self._message_base_y = 100

        # Ensemble des objets disponibles
        self.RectButton = RectButtonObject
        self.CircleButton = CircleButtonObject
        self.RectSelector = RectSelectorObject
        self.CircleSelector = CircleSelectorObject
        self.TextCase = TextCaseObject
        self.Section = SectionObject
        self.Text = TextObject
        self.Image = ImageObject
        self.Surface = SurfaceObject
        self.Overlay = OverlayObject
        self.ScrollBar = ScrollBarObject
        self.InputButton = InputButtonObject

    def _init(self):
        """Initialisation sécurisée"""
        context.inputs.add_listener(1, self._click_down, give_key=True, up=False)
        context.inputs.add_listener(1, self._click_up, give_key=True, up=True)
        context.inputs.add_listener(3, self._click_down, give_key=True, up=False)
        context.inputs.add_listener(3, self._click_up, give_key=True, up=True)
        for obj in self._objects:
            if hasattr(obj, '_init') and callable(obj._init):
                obj._init()

    # ======================================== METHODES PRIVEES ========================================
    def _sort(self):
        """Tri des objets par zorder"""
        self._objects = sorted(self._objects, key=lambda o: getattr(o, 'zorder', 0), reverse=True)

    def _append(self, obj: object):
        """Enregistrement d'un objet en maintenant l'ordre z"""
        if obj in self._objects: return
        self._objects.append(obj)
        self._objects.sort(key=lambda o: getattr(o, 'zorder', 0))
    
    def _remove(self, obj: object):
        """Suppression d'un objet"""
        if obj not in self._objects: return
        self._objects.remove(obj)
    
    # Souris
    def _update_hover(self):
        """Actualise le survol"""
        hovered_panel = context.panels.hovered
        self._hovered_object = None
        for obj in reversed(self._filtered):
            if str(obj.panel) == str(hovered_panel) and obj.collidemouse() and obj.visible:
                self._hovered_object = obj
                return

    def _click(self, key: int, up: bool = False):
        """Clic utilisateur"""
        if self._hovered_object is not None:
            if key == 1: name = 'left_click'
            elif key == 3: name = 'rightclick'
            else: return
            method = getattr(self._hovered_object, name, None)
            if method is not None and callable(method):
                method(up=up)
    
    def _click_down(self, key: int = None):
        """Pression"""
        self._click(key, up=False)
    
    def _click_up(self, key: int = None):
        """Relâchement"""
        self._click(key, up=True)

    def _reposition_messages(self):
        """Repositionne tous les messages"""
        current_y = self._message_base_y
        for msg_data in self._system_messages:
            text_obj = msg_data['text']
            text_obj.set_position(context.screen.centerx, current_y)
            current_y += text_obj.rect.height + self._message_spacing

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        self._update_filter()
        self._update_hover()
        for obj in self._filtered:
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
        self._update_messages()

    def _update_filter(self):
        """Actualisation des objects filtrés"""
        self._filtered = []
        for obj in self._objects:
            panel = getattr(obj, '_panel', None)
            if panel is not None and not context.panels.is_active(panel): continue
            self._filtered.append(obj)
    
    def _update_messages(self):
        """Actualisation des messages"""
        messages_to_remove = []
        for msg_data in self._system_messages:
            text_obj = msg_data['text']
            msg_data['elapsed'] += context.time.dt
            
            if msg_data['elapsed'] >= (msg_data['lifetime'] - msg_data['fade_duration']):
                fade_elapsed = msg_data['elapsed'] - (msg_data['lifetime'] - msg_data['fade_duration'])
                fade_progress = min(1.0, fade_elapsed / msg_data['fade_duration'])
                alpha = int(255 * (1.0 - fade_progress))
                text_obj.set_alpha(max(0, alpha))
            
            if msg_data['elapsed'] >= msg_data['lifetime']:
                messages_to_remove.append(msg_data)
                text_obj.kill()
        
        for msg_data in messages_to_remove:
            self._system_messages.remove(msg_data)
        if messages_to_remove:
            self._reposition_messages()

    # ======================================== AFFICHAGE ========================================
    def draw(self):
        """Affichage pas frame"""
        for obj in self._filtered:
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw()
        self._draw_messages()

    def _draw_messages(self):
        """Affichage des messages"""
        for msg_data in self._system_messages:
            text_obj = msg_data['text']
            if text_obj._surface and text_obj.visible:
                if text_obj._shadow_surface:
                    context.screen.blit_last(text_obj._shadow_surface,(text_obj._rect.x + text_obj._shadow_offset, text_obj._rect.y + text_obj._shadow_offset), end_priority=0)
                context.screen.blit_last(text_obj._surface, text_obj._rect, end_priority=1)

    # ======================================== GETTERS ========================================
    def get_hovered(self) -> object | None:
        """Renvoie l'objet survolé"""
        return self._hovered_object
    
    @property
    def hovered(self) -> object | None:
        """Renvoie l'objet survolé"""
        return self._hovered_object
    
    def get_selections(self) -> list[str]:
        """Renvoie l'ensemble des sélections"""
        return self._selections.keys()

    def get_selected(self, id_selection: str) -> list[str]:
        """Renvoie la liste des sélecteurs sélectionnés"""
        selected = self._selections.get(id_selection, [])
        if len(selected) == 0:
            return None
        elif len(selected) == 1:
            return selected[0]
        return selected
    
    def get_messages_y(self) -> int | float:
        """Renvoie la coordonnée y initiale des messages"""
        return self._message_base_y
    
    def get_messages_spacing(self) -> int | float:
        """Renvoie l'espacement entre les messages"""
        return self._message_spacing

    # ======================================== SETTERS ========================================
    def set_messages_y(self, y: int | float):
        """Fixe la coordonnée y initiale des messages"""
        if not isinstance(y, (int, float)):
            _raise_error(self, '__init__', 'Invalid y argument')
        self._message_base_y = y

    def set_messages_spacing(self, spacing: int| float):
        """Fixe l'espacement entre les messages"""
        if not isinstance(spacing, (int, float)):
            _raise_error(self, '__init__', 'Invalid spacing argument')
        self._message_spacing = spacing
    
    # ======================================== METHODES PUBLIQUES ========================================
    def sys_message(self, text: TextObject, lifetime: float = 3.0, fade_duration: float = 0.5):
        """
        Affiche un TextObject comme message système
        
        Args:
            text (TextObject): objet texte à afficher (doit avoir auto=False)
            lifetime (float, optional): durée d'affichage en secondes (default: 3.0)
            fade_duration (float, optional): durée du fondu en secondes (default: 0.5)
        """
        if not isinstance(text, TextObject):
            raise RuntimeError("[UiManager].sys_message : text must be a TextObject")

        if text in self._objects:
            self._objects.remove(text)
        
        y_position = self._message_base_y
        for msg_data in self._system_messages:
            y_position += msg_data['text'].rect.height + self._message_spacing
        
        text.set_position(context.screen.centerx, y_position)
        
        self._system_messages.append({
            'text': text,
            'lifetime': lifetime,
            'fade_duration': fade_duration,
            'elapsed': 0.0
        })

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

    def unselect(self, id_selection: str, id_selector: str = None):
        """Remet une séléction à None"""
        if id_selection in self._selections:
            if id_selector is None:
                self._selections[id_selection] = []
            elif id_selector in self._selections[id_selection]:
                self._selections[id_selection].remove(id_selector)

# ======================================== INSTANCE ========================================
ui_manager = UiManager()