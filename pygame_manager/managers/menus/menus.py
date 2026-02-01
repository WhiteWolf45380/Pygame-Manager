# ======================================== IMPORTS ========================================
from typing import Iterable
from numbers import Real
from ... import context
from ._menu import Menu

# ======================================== MANAGER ========================================
class MenusManager:
    """
    Gestionnaire de menus avec système predecessor/successor.
    """
    def __init__(self):
        self._dict = {}
        self._zorder = []
        self._active_menus = []
        self._hovered = None

        self.Menu = Menu

    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def __repr__(self):
        active = ', '.join(name for name in self._active_menus) or 'None'
        return f"<MenusManager: {len(self._dict)} menus | Active: [{active}]>"

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
        
        self._sort_active_menus()

    def _sort_active_menus(self):
        """Tri des menus actifs selon le zorder"""
        active = set(self._active_menus)
        self._active_menus = list(filter(lambda name: name in active, self._zorder))

    def _get_subtree(self, name: str) -> list:
        """Retourne tous les descendants d'un menu (lui-même inclus), en ordre BFS"""
        result = []
        queue = [name]
        while queue:
            current = queue.pop(0)
            result.append(current)
            if current in self._dict:
                queue.extend(self._dict[current]["successors"])
        return result

    def _deactivate_subtree(self, name: str):
        """Désactive un menu et tout son sous-arbre (on_exit en ordre inverse = feuilles d'abord)"""
        subtree = self._get_subtree(name)
        for menu_name in reversed(subtree):
            if menu_name in self._active_menus:
                obj = self._dict[menu_name]["object"]
                obj.on_exit()
                self._active_menus.remove(menu_name)
    
    def _update_hovered(self):
        """Renvoie le menu survolé par la souris"""
        for name in reversed(self._active_menus):
            obj = self._dict[name]["object"]
            if not hasattr(obj, 'surface_rect'): continue
            if not getattr(obj, "hoverable", True): continue
            if any(p not in self._active_menus for p in self._get_chain(name)): continue
            if 0 <= obj.mouse_x <= obj.surface_rect.width and 0 <= obj.mouse_y <= obj.surface_rect.height:
                self._hovered = name
                return
        self._hovered = None

    # ======================================== GETTERS ========================================
    def get_menus(self) -> list:
        """Renvoie l'ensemble des menus enregistrés"""
        return list(self._dict.keys())

    def get_active_menus(self) -> list:
        """Renvoie l'ensemble des menus actifs"""
        return self._active_menus

    def get_object(self, name: str) -> Menu | None:
        """Renvoie l'objet d'un menu"""
        if name not in self._dict:
            return None
        return self._dict[name]["object"]
    
    def __getitem__(self, key):
        """Renvoie l'objet d'un menu"""
        if key not in self._dict.keys():
            self._raise_error('__getitem__', f'menu "{key}" does not exist')
        return self._dict[key]["object"]

    def get_predecessor(self, name: str) -> str | None:
        """Renvoie le prédecesseur d'un menu"""
        if name not in self._dict:
            return None
        return self._dict[name]["predecessor"]

    def get_successors(self, name: str) -> list:
        """Renvoie les successeurs d'un menu"""
        if name not in self._dict:
            return []
        return list(self._dict[name]["successors"])
    
    def get_hovered(self) -> str | None:
        """Renvoie le menu survolé"""
        return self._hovered
    
    @property
    def hovered(self) -> str | None:
        """Renvoie le menu survolé"""
        return self._hovered

    # ======================================== ENREGISTREMENT ========================================
    def register(self, obj: Menu):
        """
        Enregistre un objet Menu

        Args:
            obj (Menu) : objet du menu à enregistrer
        """
        name = obj._name
        if name in self._dict:
            self._raise_error('register', f'menu "{name}" already exists')

        predecessor = obj._predecessor
        if predecessor not in self._dict and predecessor is not None:
            self._raise_error('register', f'predecessor menu "{predecessor}" does not exist')

        self._dict[name] = {
            "predecessor": predecessor,
            "successors": [],
            "object": obj
        }

        if predecessor is not None:
            self._dict[predecessor]["successors"].append(name)
        self._update_zorder()
    
    # ======================================== PREDICATS ========================================
    def __contains__(self, menu: str | Menu):
        """Vérifie l'enregistrement d'un menu"""
        if isinstance(menu, str):
            return menu in self._dict
        
    def is_active(self, name: str) -> bool:
        """Vérifie qu'un menu soit actif"""
        return name in self._active_menus

    # ======================================== ACTIVATION ========================================
    def activate(self, name: str):
        """
        Active un menu

        Args:
            name (str) : nom du menu
        """
        if name not in self._dict:
            self._raise_error('activate', f'menu "{name}" does not exist')
        if name in self._active_menus:
            return
        self._active_menus.append(name)
        self._sort_active_menus()
        self._dict[name]["object"].on_enter()

    def deactivate(self, name: str, pruning: bool = True):
        """
        Désactive un menu

        Args:
            name (str) : nom du menu à désactiver
            pruning (bool, optional) : fermeture de tous les menus successeurs
        """
        if name not in self._dict:
            return
        if name not in self._active_menus:
            return
        if not pruning:
            obj = self._dict[name]["object"]
            obj.on_exit()
            self._active_menus.remove(name)
            return
        self._deactivate_subtree(name)
        self._sort_active_menus()

    def deactivate_all(self):
        """Désactive tous les menus actifs"""
        for name in list(self._active_menus):
            self._dict[name]["object"].on_exit()
        self._active_menus = []

    # ======================================== SWITCH ========================================
    def switch(self, to_close: str | Iterable[str], to_activate: str, pruning: bool = True):
        """
        Ferme un ou plusieurs menu(s) et en active un autre

        Args:
            to_close (str | Iterable[str]) : menu(s) à fermer
            to_activate (str) : menu à activer
            pruning (bool, optional) : femeture des menus successeurs
        """
        if isinstance(to_close, str):
            to_close = [to_close]
        else:
            to_close = list(to_close)

        if any(tc not in self._dict for tc in to_close):
            self._raise_error('switch', 'Invalid menus to close')
        if to_activate not in self._dict:
            self._raise_error('switch', f'{to_activate} menu does not exist')

        for name in to_close:
            self.deactivate(name, pruning=pruning)
        self.activate(to_activate)

    # ======================================== Z-ORDER ========================================
    def reorder(self, name: str, direction: str, index: int = None):
        """
        Réordonne un menu dans la liste des successeurs de son predecessor.

        Args:
            name (str) : menu à réordoner
            direction (str) : "forward", "backward", "front", "back", "index"
            index (int | None) : utilisé uniquement avec "index"
        """
        if name not in self._dict:
            self._raise_error('reorder', f'menu "{name}" does not exist')

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
                self._raise_error('reorder', '"index" requires an index')
            successors.remove(name)
            successors.insert(index, name)

        self._update_zorder()

    # ======================================== COORDONNÉES ========================================
    def _get_chain(self, name: str) -> list:
        """
        Remonte la chaîne predecessor depuis un menu jusqu'à la racine.
        Retourne la liste des noms du menu vers la racine (menu lui-même inclus).
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

    def absolute(self, point: tuple[Real, Real], menu_name: str) -> tuple[float, float]:
        """
        Convertit un point relatif à un menu en coordonnées absolues

        Args:
            point (tuple[Real, Real]) : (x, y) relatif au menu
            menu_name (str) : nom du menu de référence
        """
        if menu_name not in self._dict:
            self._raise_error('absolute', f'menu "{menu_name}" does not exist')

        x, y = map(float, point)
        chain = self._get_chain(menu_name)

        for name in chain:
            rect = None
            if hasattr(self._dict[name]["object"], 'surface_rect'):
                rect = self._dict[name]["object"].surface_rect
            x += rect.x if rect is not None else 0
            y += rect.y if rect is not None else 0

        return (x, y)

    def relative(self, point: tuple[Real, Real], menu_name: str) -> tuple[float, float]:
        """
        Convertit un point absol en coordonnées relatives à un menu

        Args:
            point (tuple[Real, Real]) : (x, y) en coordonnées absolues
            menu_name (str) : nom du menu de référence
        """
        if menu_name not in self._dict:
            self._raise_error('relative', f'menu "{menu_name}" does not exist')

        x, y = map(float, point)
        chain = self._get_chain(menu_name)

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
        Exécute update de tous les menus actifs
        """
        self._update_hovered()
        for name in self._active_menus:
            obj = self._dict[name]["object"]
            if hasattr(obj, 'update'):
                obj.update()

    def draw(self):
        """
        Exécute draw de tous les menus actifs et affichés 
        """
        for name in self._active_menus:
            predecessor = self._dict[name]["predecessor"]
            if predecessor is not None and predecessor not in self._active_menus:
                continue

            obj = self._dict[name]["object"]
            if hasattr(obj, 'draw'):
                if predecessor is not None: predecessor_surface = getattr(self._dict[predecessor]["object"], 'surface')
                else: predecessor_surface = context.screen.surface
                obj.draw(predecessor_surface)

# ======================================== INSTANCE ========================================
menus_manager = MenusManager()