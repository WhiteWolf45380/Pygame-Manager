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
from ._message import MessageObject

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
        self._system_messages = []      # liste des messages système actifs
        self._message_spacing = 10      # espacement vertical entre messages
        self._message_base_y = 50       # position Y du premier message

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
        self.Message = MessageObject

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
    # Objets
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
        # Retirer des messages système si présent
        if obj in self._system_messages:
            self._system_messages.remove(obj)
            self._reposition_messages()
    
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

    # Messages système
    def _reposition_messages(self):
        """Repositionne tous les messages système"""
        current_y = self._message_base_y
        for msg in self._system_messages:
            msg.set_position(context.screen.centerx, current_y)
            current_y += msg.rect.height + self._message_spacing

    # ======================================== METHODES PUBLIQUES ========================================
    def update_filter(self):
        """Actualisation des objects filtrés"""
        self._filtered = []
        for obj in self._objects:
            panel = getattr(obj, '_panel', None)
            if panel is not None and not context.panels.is_active(panel): continue
            self._filtered.append(obj)

    def update(self):
        """Actualisation par frame"""
        self.update_filter()
        self._update_hover()
        
        # Update des objets normaux
        for obj in self._filtered:
            if hasattr(obj, 'update') and callable(obj.update):
                obj.update()
        
        # Update des messages système
        messages_to_remove = []
        for msg in self._system_messages:
            if hasattr(msg, 'update') and callable(msg.update):
                msg.update()
            # Vérifier si le message doit être supprimé
            if not msg.visible or msg._elapsed_time >= msg._lifetime:
                messages_to_remove.append(msg)
        
        # Supprimer les messages expirés
        for msg in messages_to_remove:
            self._system_messages.remove(msg)
        
        # Repositionner les messages restants
        if messages_to_remove:
            self._reposition_messages()

    def draw(self):
        """Affichage pas frame"""
        # Draw des objets normaux
        for obj in self._filtered:
            if hasattr(obj, 'draw') and callable(obj.draw):
                obj.draw()
        
        # Draw des messages système (utilisent blit_last donc s'affichent au-dessus)
        for msg in self._system_messages:
            if hasattr(msg, 'draw') and callable(msg.draw):
                msg.draw()
    
    def get_hovered(self) -> object | None:
        """Renvoie l'objet survolé"""
        return self._hovered_object
    
    @property
    def hovered(self) -> object | None:
        """Renvoie l'objet survolé"""
        return self._hovered_object

    # Messages système
    def show_message(
        self, 
        text: str, 
        sender: str = None,
        lifetime: float = 3.0,
        fade_duration: float = 0.5,
        font_size: int = 16,
        font_color: tuple = (200, 200, 200, 255),
        sender_color: tuple = (100, 150, 255, 255),
    ) -> MessageObject:
        """
        Affiche un message système temporaire
        
        Args:
            text (str): contenu du message
            sender (str, optional): expéditeur du message
            lifetime (float, optional): durée d'affichage en secondes
            fade_duration (float, optional): durée du fondu de sortie
            font_size (int, optional): taille de la police
            font_color (tuple, optional): couleur du texte
            sender_color (tuple, optional): couleur du sender
            
        Returns:
            MessageObject: l'objet message créé
        """
        # Calculer la position Y en fonction des messages existants
        y_position = self._message_base_y
        for msg in self._system_messages:
            y_position += msg.rect.height + self._message_spacing
        
        # Créer le message en mode système
        message = MessageObject(
            text=text,
            sender=sender,
            x=context.screen.centerx,
            y=y_position,
            anchor="midtop",
            font_size=font_size,
            font_color=font_color,
            sender_color=sender_color,
            lifetime=lifetime,
            fade_duration=fade_duration,
            system_message=True,  # Active le mode système avec blit_last
            auto=False,  # Ne pas enregistrer dans le système normal
            zorder=1000
        )
        
        # Ajouter à la liste des messages système
        self._system_messages.append(message)
        
        return message

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
        selected = self._selections.get(id_selection, [])
        if len(selected) == 0:
            return None
        elif len(selected) == 1:
            return selected[0]
        return selected

# ======================================== INSTANCE ========================================
ui_manager = UiManager()