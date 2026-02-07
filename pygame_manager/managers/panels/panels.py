# ======================================== IMPORTS ========================================
from ._core import *
from ._panel import Panel

# ======================================== MANAGER ========================================
class PanelsManager:
    """
    Gestionnaire de panels avec système predecessor/successor.
    """
    def __init__(self):
        self._dict = {}
        self._zorder = []
        self._active_panels = []
        self._hovered = None

        self.Panel = Panel

    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def __repr__(self):
        active = ', '.join(name for name in self._active_panels) or 'None'
        return f"<panelsManager: {len(self._dict)} panels | Active: [{active}]>"

    # ======================================== METHODES INTERNES ========================================
    def _update_zorder(self):
        """Exploration récursive pour construire la liste de Z-order"""
        self._zorder = []

        def visit(name: str):
            if name not in self._dict:
                return
            self._zorder.append(name)
            for child in self._dict[name]["successors"]:
                visit(child)

        for name, info in self._dict.items():
            if info["predecessor"] is None:
                visit(name)
        
        self._sort_active_panels()

    def _sort_active_panels(self):
        """Tri des panels actifs selon le zorder"""
        active = set(self._active_panels)
        self._active_panels = list(filter(lambda name: name in active, self._zorder))

    def _get_subtree(self, name: str) -> list:
        """Retourne tous les descendants d'un panel (lui-même inclus), en ordre BFS"""
        result = []
        queue = [name]
        while queue:
            current = queue.pop(0)
            result.append(current)
            if current in self._dict:
                queue.extend(self._dict[current]["successors"])
        return result

    def _deactivate_subtree(self, name: str):
        """Désactive un panel et tout son sous-arbre (on_exit en ordre inverse = feuilles d'abord)"""
        subtree = self._get_subtree(name)
        for panel_name in reversed(subtree):
            if panel_name in self._active_panels:
                obj = self._dict[panel_name]["object"]
                obj.on_exit()
                self._active_panels.remove(panel_name)
    
    def _update_hover(self):
        """Renvoie le panel survolé par la souris"""
        for name in reversed(self._active_panels):
            obj = self._dict[name]["object"]
            if not hasattr(obj, '_surface_rect'): continue
            if not getattr(obj, "_hoverable", True): continue
            if any(p not in self._active_panels for p in self._get_chain(name)): continue
            if 0 <= obj.mouse_x <= obj._surface_rect.width and 0 <= obj.mouse_y <= obj._surface_rect.height:
                self._hovered = name
                return
        self._hovered = None

    # ======================================== GETTERS ========================================
    def get_panels(self) -> list:
        """Renvoie l'ensemble des panels enregistrés"""
        return list(self._dict.keys())

    def get_active_panels(self) -> list:
        """Renvoie l'ensemble des panels actifs"""
        return self._active_panels

    def get_object(self, name: str) -> Panel | None:
        """Renvoie l'objet d'un panel"""
        if name not in self._dict:
            return None
        return self._dict[name]["object"]
    
    def __getitem__(self, key):
        """Renvoie l'objet d'un panel"""
        if isinstance(key, Panel): key = str(key)
        if key not in self._dict.keys():
            _raise_error(self, '__getitem__', f'panel "{key}" does not exist')
        return self._dict[key]["object"]

    def get_predecessor(self, name: str) -> str | None:
        """Renvoie le prédecesseur d'un panel"""
        if name not in self._dict:
            return None
        return self._dict[name]["predecessor"]

    def get_successors(self, name: str) -> list:
        """Renvoie les successeurs d'un panel"""
        if name not in self._dict:
            return []
        return list(self._dict[name]["successors"])
    
    def get_hovered(self) -> str | None:
        """Renvoie le panel survolé"""
        return self._hovered
    
    @property
    def hovered(self) -> str | None:
        """Renvoie le panel survolé"""
        return self._hovered

    # ======================================== ENREGISTREMENT ========================================
    def register(self, obj: Panel):
        """
        Enregistre un objet panel

        Args:
            obj (panel) : objet du panel à enregistrer
        """
        name = obj._name
        if name in self._dict:
            _raise_error(self, 'register', f'panel "{name}" already exists')

        predecessor = obj._predecessor
        if predecessor not in self._dict and predecessor is not None:
            _raise_error(self, 'register', f'predecessor panel "{predecessor}" does not exist')

        self._dict[name] = {
            "predecessor": predecessor,
            "successors": [],
            "object": obj
        }

        if predecessor is not None:
            self._dict[predecessor]["successors"].append(name)
        self._update_zorder()
    
    # ======================================== PREDICATS ========================================
    def __contains__(self, panel: str | Panel):
        """Vérifie l'enregistrement d'un panel"""
        if isinstance(panel, str):
            return panel in self._dict
        return panel in [data["object"] for data in self._dict.values()]
        
    def is_active(self, panel: str | Panel) -> bool:
        """Vérifie qu'un panel soit actif"""
        if isinstance(panel, str):
            return panel in self._active_panels
        return panel in [data["object"] for name, data in self._dict.items() if name in self._active_panels]

    # ======================================== ACTIVATION ========================================
    def activate(self, name: str):
        """
        Active un panel

        Args:
            name (str) : nom du panel
        """
        if name not in self._dict:
            _raise_error(self, 'activate', f'panel "{name}" does not exist')
        if name in self._active_panels:
            return
        self._active_panels.append(name)
        self._sort_active_panels()
        self._dict[name]["object"].on_enter()

    def deactivate(self, name: str, pruning: bool = True):
        """
        Désactive un panel

        Args:
            name (str) : nom du panel à désactiver
            pruning (bool, optional) : fermeture de tous les panels successeurs
        """
        if name not in self._dict:
            return
        if name not in self._active_panels:
            return
        if not pruning:
            obj = self._dict[name]["object"]
            obj.on_exit()
            self._active_panels.remove(name)
            return
        self._deactivate_subtree(name)
        self._sort_active_panels()

    def deactivate_all(self):
        """Désactive tous les panels actifs"""
        for name in list(self._active_panels):
            self._dict[name]["object"].on_exit()
        self._active_panels = []

    # ======================================== SWITCH ========================================
    def switch(self, to_close: str | Iterable[str], to_activate: str, pruning: bool = True):
        """
        Ferme un ou plusieurs panel(s) et en active un autre

        Args:
            to_close (str | Iterable[str]) : panel(s) à fermer
            to_activate (str) : panel à activer
            pruning (bool, optional) : femeture des panels successeurs
        """
        if isinstance(to_close, str):
            to_close = [to_close]
        else:
            to_close = list(to_close)

        if any(tc not in self._dict for tc in to_close):
            _raise_error(self, 'switch', 'Invalid panels to close')
        if to_activate not in self._dict:
            _raise_error(self, 'switch', f'{to_activate} panel does not exist')

        for name in to_close:
            self.deactivate(name, pruning=pruning)
        self.activate(to_activate)

    # ======================================== Z-ORDER ========================================
    def reorder(self, name: str, direction: str, index: int = None):
        """
        Réordonne un panel dans la liste des successeurs de son predecessor.

        Args:
            name (str) : panel à réordoner
            direction (str) : "forward", "backward", "front", "back", "index"
            index (int | None) : utilisé uniquement avec "index"
        """
        if name not in self._dict:
            _raise_error(self, 'reorder', f'panel "{name}" does not exist')

        predecessor = self._dict[name]["predecessor"]
        if predecessor is None:
            return

        successors = self._dict[predecessor]["successors"]
        if name not in successors:
            return

        i = successors.index(name)
        if direction == "forward":
            if i < len(successors) - 1:
                successors[i], successors[i + 1] = successors[i + 1], successors[i]

        elif direction == "backward":
            if i > 0:
                successors[i], successors[i - 1] = successors[i - 1], successors[i]

        elif direction == "front":
            successors.remove(name)
            successors.append(name)

        elif direction == "back":
            successors.remove(name)
            successors.insert(0, name)

        elif direction == "index":
            if index is None:
                _raise_error(self, 'reorder', '"index" requires an index')
            successors.remove(name)
            successors.insert(index, name)

        self._update_zorder()

    # ======================================== COORDONNÉES ========================================
    def _get_chain(self, name: str) -> list:
        """
        Remonte la chaîne predecessor depuis un panel jusqu'à la racine.
        Retourne la liste des noms du panel vers la racine (panel lui-même inclus).
        """
        chain = []
        current = name
        while current is not None:
            chain.append(current)
            if current in self._dict:
                current = self._dict[current]["predecessor"]
            else:
                break
        return chain

    def absolute(self, point: tuple[Real, Real], panel_name: str) -> tuple[float, float]:
        """
        Convertit un point relatif à un panel en coordonnées absolues

        Args:
            point (tuple[Real, Real]) : (x, y) relatif au panel
            panel_name (str) : nom du panel de référence
        """
        if panel_name not in self._dict:
            _raise_error(self, 'absolute', f'panel "{panel_name}" does not exist')

        x, y = map(float, point)
        chain = self._get_chain(panel_name)

        for name in chain:
            rect = None
            if hasattr(self._dict[name]["object"], 'surface_rect'):
                rect = self._dict[name]["object"].surface_rect
            x += rect.x if rect is not None else 0
            y += rect.y if rect is not None else 0

        return (x, y)

    def relative(self, point: tuple[Real, Real], panel_name: str) -> tuple[float, float]:
        """
        Convertit un point absol en coordonnées relatives à un panel

        Args:
            point (tuple[Real, Real]) : (x, y) en coordonnées absolues
            panel_name (str) : nom du panel de référence
        """
        if panel_name not in self._dict:
            _raise_error(self, 'relative', f'panel "{panel_name}" does not exist')

        x, y = map(float, point)
        chain = self._get_chain(panel_name)

        for name in chain:
            rect = None
            if hasattr(self._dict[name]["object"], 'surface_rect'):
                rect = self._dict[name]["object"].surface_rect
            x -= rect.x if rect is not None else 0
            y -= rect.y if rect is not None else 0

        return (x, y)

    # ======================================== METHODES DYNAMIQUES ========================================
    def update(self):
        """
        Exécute update de tous les panels actifs
        """
        self._update_hover()
        for name in self._active_panels:
            obj = self._dict[name]["object"]
            if hasattr(obj, 'update'):
                obj.update()

    def draw_back(self):
        """
        Exécute draw_back de tous les panels actifs et affichés 
        """
        for name in self._active_panels:
            predecessor = self._dict[name]["predecessor"]
            if predecessor is not None and predecessor not in self._active_panels:
                continue

            obj = self._dict[name]["object"]
            if hasattr(obj, 'draw_back'):
                obj.draw_back(obj._surface)

    def draw_between(self):
        """
        Exécute draw_between de tous les panels actifs et affichés 
        """
        for name in self._active_panels:
            predecessor = self._dict[name]["predecessor"]
            if predecessor is not None and predecessor not in self._active_panels:
                continue

            obj = self._dict[name]["object"]
            if hasattr(obj, 'draw_between'):
                obj.draw_between(obj._surface)

    def draw(self):
        """
        Exécute draw de tous les panels actifs et affichés 
        """
        for name in self._active_panels:
            predecessor = self._dict[name]["predecessor"]
            if predecessor is not None and predecessor not in self._active_panels:
                continue

            if predecessor is not None: predecessor_surface = getattr(self._dict[predecessor]["object"], 'surface')
            else: predecessor_surface = context.screen.surface

            obj = self._dict[name]["object"]
            if hasattr(obj, 'draw'):
                obj.draw(predecessor_surface)

# ======================================== INSTANCE ========================================
panels_manager = PanelsManager()