# ======================================== IMPORTS ========================================
from ._menu import Menu
import pygame

# ======================================== MANAGER ========================================
class MenusManager:
    """
    Gestionnaire de menus avec système predecessor/successor.

    _all_menus : topologie complète de tous les menus enregistrés
        { name: { "predecessor": str|None, "predecessor_type": str|None,
                  "successors": [str, ...], "menu_obj": Menu } }

    _active_menus : set des noms de menus actuellement actifs

    Règle de propagation : désactiver un menu désactive tout son sous-arbre.
    """
    def __init__(self):
        self._all_menus = {}
        self._active_menus = set()

        self.menu = Menu

    # ======================================== REPR ========================================
    def __repr__(self):
        active = ', '.join(sorted(self._active_menus)) if self._active_menus else 'None'
        return f"<MenusManager: {len(self._all_menus)} menus | Active: [{active}]>"

    def __getitem__(self, key):
        if key not in self._all_menus:
            self._raise_error('__getitem__', f'menu "{key}" does not exist')
        return self._all_menus[key]["menu_obj"]

    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== INTERNAL ========================================
    def _get_subtree(self, name: str) -> list:
        """Retourne tous les descendants d'un menu (lui-même inclus), en ordre BFS"""
        result = []
        queue = [name]
        while queue:
            current = queue.pop(0)
            result.append(current)
            if current in self._all_menus:
                queue.extend(self._all_menus[current]["successors"])
        return result

    def _deactivate_subtree(self, name: str):
        """Désactive un menu et tout son sous-arbre (on_exit en ordre inverse = feuilles d'abord)"""
        subtree = self._get_subtree(name)
        # on_exit des feuilles vers la racine du sous-arbre
        for menu_name in reversed(subtree):
            if menu_name in self._active_menus:
                menu_obj = self._all_menus[menu_name]["menu_obj"]
                menu_obj.on_exit()
                self._active_menus.discard(menu_name)

    # ======================================== GETTERS ========================================
    def get_menus(self) -> list:
        return list(self._all_menus.keys())

    def get_active_menus(self) -> list:
        return list(self._active_menus)

    def is_active(self, name: str) -> bool:
        return name in self._active_menus

    def get_menu_object(self, name: str) -> Menu | None:
        if name not in self._all_menus:
            return None
        return self._all_menus[name]["menu_obj"]

    def get_predecessor(self, name: str) -> str | None:
        if name not in self._all_menus:
            return None
        return self._all_menus[name]["predecessor"]

    def get_successors(self, name: str) -> list:
        if name not in self._all_menus:
            return []
        return list(self._all_menus[name]["successors"])

    # ======================================== REGISTER ========================================
    def register(self, menu_obj: Menu):
        """Enregistre un objet Menu dans la topologie"""
        name = menu_obj.name
        if name in self._all_menus:
            self._raise_error('register', f'menu "{name}" already exists')

        predecessor = menu_obj.predecessor
        predecessor_type = menu_obj.predecessor_type

        # vérifie que le predecessor existe (si ce n'est pas None)
        if predecessor is not None:
            if predecessor_type == "state":
                from ..states import states_manager
                if states_manager.get_state_object(predecessor) is None:
                    self._raise_error('register', f'predecessor state "{predecessor}" does not exist')
            elif predecessor_type == "menu":
                if predecessor not in self._all_menus:
                    self._raise_error('register', f'predecessor menu "{predecessor}" does not exist')

        # enregistrement
        self._all_menus[name] = {
            "predecessor": predecessor,
            "predecessor_type": predecessor_type,
            "successors": [],
            "menu_obj": menu_obj
        }

        # ajoute comme successeur du predecessor (si ce n'est pas None/screen)
        if predecessor is not None and predecessor_type == "menu":
            self._all_menus[predecessor]["successors"].append(name)

    # ======================================== ACTIVATION ========================================
    def activate(self, name: str):
        """Active un menu"""
        if name not in self._all_menus:
            self._raise_error('activate', f'menu "{name}" does not exist')
        if name in self._active_menus:
            return  # déjà actif

        self._active_menus.add(name)
        self._all_menus[name]["menu_obj"].on_enter()

    def deactivate(self, name: str):
        """Désactive un menu et tout son sous-arbre"""
        if name not in self._all_menus:
            return
        if name not in self._active_menus:
            return
        self._deactivate_subtree(name)

    def deactivate_all(self):
        """Désactive tous les menus actifs"""
        # on_exit sur tous (pas de garantie d'ordre particulier entre branches indépendantes)
        for name in list(self._active_menus):
            self._all_menus[name]["menu_obj"].on_exit()
        self._active_menus = set()

    # ======================================== SWITCH ========================================
    def switch(self, predecessor_name: str, to_close, to_activate: str):
        """
        Sur un predecessor donné, ferme un ou plusieurs successeurs et active un autre.

        Args:
            predecessor_name (str) : nom du predecessor qui effectue le switch
            to_close (str | Iterable[str]) : successeur(s) à fermer
            to_activate (str) : successeur à activer
        """
        if predecessor_name not in self._all_menus:
            self._raise_error('switch', f'menu "{predecessor_name}" does not exist')

        successors = self._all_menus[predecessor_name]["successors"]

        # normalise to_close en liste
        if isinstance(to_close, str):
            to_close = [to_close]
        else:
            to_close = list(to_close)

        # vérifie que to_activate est un successeur du predecessor
        if to_activate not in successors:
            self._raise_error('switch', f'"{to_activate}" is not a successor of "{predecessor_name}"')

        # vérifie que tous les to_close sont des successeurs du predecessor
        for name in to_close:
            if name not in successors:
                self._raise_error('switch', f'"{name}" is not a successor of "{predecessor_name}"')

        # ferme les successeurs demandés (avec propagation sous-arbre)
        for name in to_close:
            self.deactivate(name)

        # active le successeur cible
        self.activate(to_activate)

    # ======================================== Z-ORDER ========================================
    def reorder(self, name: str, direction: str, index: int = None):
        """
        Réordonne un menu dans la liste des successeurs de son predecessor.

        Args:
            name (str) : menu à réordoner
            direction (str) : "devant", "derriere", "premier_plan", "dernier_plan", "fixer_plan"
            index (int | None) : utilisé uniquement avec "fixer_plan"
        """
        if name not in self._all_menus:
            self._raise_error('reorder', f'menu "{name}" does not exist')

        predecessor = self._all_menus[name]["predecessor"]

        # si pas de predecessor menu, pas de liste à réordoner
        if predecessor is None or self._all_menus[name]["predecessor_type"] != "menu":
            return

        successors = self._all_menus[predecessor]["successors"]
        if name not in successors:
            return  # ne devrait pas arriver mais just in case

        i = successors.index(name)

        if direction == "devant":
            if i < len(successors) - 1:
                successors[i], successors[i + 1] = successors[i + 1], successors[i]

        elif direction == "derriere":
            if i > 0:
                successors[i], successors[i - 1] = successors[i - 1], successors[i]

        elif direction == "premier_plan":
            successors.remove(name)
            successors.append(name)

        elif direction == "dernier_plan":
            successors.remove(name)
            successors.insert(0, name)

        elif direction == "fixer_plan":
            if index is None:
                self._raise_error('reorder', '"fixer_plan" requires an index')
            successors.remove(name)
            successors.insert(index, name)

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
            if current in self._all_menus:
                current = self._all_menus[current]["predecessor"]
            else:
                # c'est un State — on s'arrête ici
                break
        return chain

    def absolute(self, point: tuple, menu_name: str) -> tuple:
        """
        Convertit un point relatif à un menu en coordonnées absolues (screen/virtual_screen).
        Remonte la chaîne en accumulant les surface_rect.topleft.

        Args:
            point (tuple) : (x, y) relatif au menu
            menu_name (str) : nom du menu de référence
        """
        if menu_name not in self._all_menus:
            self._raise_error('absolute', f'menu "{menu_name}" does not exist')

        x, y = point
        chain = self._get_chain(menu_name)

        # accumule les offsets de chaque nœud de la chaîne
        for name in chain:
            if name in self._all_menus:
                rect = self._all_menus[name]["menu_obj"].surface_rect
                x += rect.x
                y += rect.y
            else:
                # c'est un State — récupère son offset via le states_manager
                from ..states import states_manager
                state_obj = states_manager.get_state_object(name)
                if state_obj is not None and hasattr(state_obj, 'surface_rect'):
                    x += state_obj.surface_rect.x
                    y += state_obj.surface_rect.y

        return (x, y)

    def relative(self, point: tuple, menu_name: str) -> tuple:
        """
        Convertit un point absolu (screen/virtual_screen) en coordonnées relatives à un menu.
        Fait l'inverse de absolute().

        Args:
            point (tuple) : (x, y) en coordonnées absolues
            menu_name (str) : nom du menu de référence
        """
        if menu_name not in self._all_menus:
            self._raise_error('relative', f'menu "{menu_name}" does not exist')

        x, y = point
        chain = self._get_chain(menu_name)

        # soustrait les offsets dans le même ordre (même accumulation, même résultat inversé)
        for name in chain:
            if name in self._all_menus:
                rect = self._all_menus[name]["menu_obj"].surface_rect
                x -= rect.x
                y -= rect.y
            else:
                from ..states import states_manager
                state_obj = states_manager.get_state_object(name)
                if state_obj is not None and hasattr(state_obj, 'surface_rect'):
                    x -= state_obj.surface_rect.x
                    y -= state_obj.surface_rect.y

        return (x, y)

    # ======================================== UPDATE ========================================
    def _draw_tree(self, name: str, parent_surface: pygame.Surface):
        """
        Dessine récursivement un menu et ses successeurs actifs.
        L'ordre des successeurs dans la liste = ordre de draw (index 0 = arrière-plan).
        """
        if name not in self._active_menus:
            return

        menu_obj = self._all_menus[name]["menu_obj"]

        # update + draw sur la surface du parent
        menu_obj.update()
        menu_obj.draw(parent_surface)

        # dessine les successeurs actifs sur la surface de ce menu
        for successor in self._all_menus[name]["successors"]:
            self._draw_tree(successor, menu_obj.surface)

    def update(self):
        """
        Exécute update + draw de tous les menus actifs.
        Part des racines (menus sans predecessor menu) et descend récursivement.
        """
        from .. import screen

        for name, data in self._all_menus.items():
            if name not in self._active_menus:
                continue

            predecessor = data["predecessor"]
            predecessor_type = data["predecessor_type"]

            # on ne part que des racines de l'arbre des menus
            # racine = predecessor est None ou predecessor est un State
            if predecessor_type == "menu":
                continue  # sera traité par la récursion depuis son ancestor

            # détermine la surface parent
            if predecessor is None:
                # pas de predecessor → screen.surface
                parent_surface = screen.surface
            else:
                # predecessor est un State
                from ..states import states_manager
                state_obj = states_manager.get_state_object(predecessor)
                if state_obj is None:
                    continue
                parent_surface = getattr(state_obj, 'surface', screen.surface)

            self._draw_tree(name, parent_surface)


# ======================================== INSTANCE ========================================
menus_manager = MenusManager()