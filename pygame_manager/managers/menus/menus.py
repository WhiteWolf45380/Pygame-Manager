# ======================================== IMPORTS ========================================
from ._menus import Menu

# ======================================== GESTIONNAIRE ========================================
class MenusManager:
    """
    Gestionnaire des états multi-layers avec remplacement par layer

    Fonctionnalités :
        stocker différentes méthodes d'état
        gérer plusieurs états actifs simultanément
        système de layers avec remplacement automatique sur le même layer
        désactivation en cascade des layers supérieurs
        callbacks on_enter/on_exit
    """
    def __init__(self):
        # gestion des états
        self._dict = {}
        self._active_menus = {}

        # super-classe
        self.menu = Menu

    # ======================================== METHODES FONCTIONNELLES ========================================
    def __repr__(self):
        if self._active_menus:
            active_list = [f"{name}(L{layer})" for layer, name in sorted(self._active_menus.items())]
            active = ', '.join(active_list)
        else:
            active = 'None'
        return f"<menusManager: {len(self._dict)} menus | Active: [{active}]>"
    
    def __getitem__(self, key):
        if key not in self._dict:
            self._raise_error('__getitem__', f'menu {key} does not exist')
        return self._dict.get(key)["menu_obj"]

    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def _clear_upper_layers(self, layer: int):
        """Désactive tous les états sur les layers supérieurs"""
        layers_to_remove = [l for l in self._active_menus.keys() if l > layer]
        for l in layers_to_remove:
            menu_name = self._active_menus[l]
            menu_obj = self._dict[menu_name]["menu_obj"]
            # Appeler on_exit si la méthode existe
            if hasattr(menu_obj, 'on_exit') and callable(getattr(menu_obj, 'on_exit')):
                menu_obj.on_exit()
            del self._active_menus[l]
    
    # ======================================== GETTERS ========================================
    def get_menus(self) -> list:
        """Retourne la liste de tous les états disponibles"""
        return list(self._dict.keys())

    def get_active_menus(self) -> list:
        """Retourne la liste des états actifs (triés par layer)"""
        sorted_layers = sorted(self._active_menus.keys())
        return [self._active_menus[layer] for layer in sorted_layers]

    def get_active_by_layer(self, layer: int) -> str | None:
        """Retourne l'état actif sur un layer donné"""
        return self._active_menus.get(layer)

    def get_layer(self, name: str) -> int:
        """Retourne le layer d'un état"""
        if name not in self._dict:
            self._raise_error('get_layer', f'menu "{name}" does not exist')
        return self._dict[name]["layer"]

    def is_active(self, name: str) -> bool:
        """Vérifie si un état est actif"""
        if name not in self._dict:
            return False
        layer = self._dict[name]["layer"]
        return self._active_menus.get(layer) == name
    
    def get_menu_object(self, name: str):
        """Retourne l'objet menu associé à un nom"""
        if name not in self._dict:
            return None
        return self._dict[name]["menu_obj"]

    # ======================================== METHODES INTERACTIVES ========================================
    def register(self, menu_obj):
        """
        Enregistre un objet état

        Args:
            menu_obj : objet menu avec attributs name, layer et méthode update
        """
        if not hasattr(menu_obj, 'name') or not isinstance(menu_obj.name, str):
            self._raise_error('register', 'menu object must have a "name" attribute (str)')
        if not hasattr(menu_obj, 'layer'):
            self._raise_error('register', 'menu object must have a "layer" attribute')
        if not hasattr(menu_obj, 'update') or not callable(getattr(menu_obj, 'update')):
            self._raise_error('register', 'menu object must have a callable "update" method')
        
        name = menu_obj.name
        if name in self._dict:
            self._raise_error('register', f'menu "{name}" already exists')
        
        self._dict[name] = {
            "layer": menu_obj.layer,
            "menu_obj": menu_obj
        }

    def set(self, name: str, layer: int = None):
        """
        Modifie un état existant

        Args:
            name (str) : nom de l'état
            layer (int, optional) : nouveau layer
        """
        if not isinstance(name, str):
            self._raise_error('set', 'menu name must be a string object')
        if name not in self._dict:
            self._raise_error('set', f'menu "{name}" does not exist')
        
        if layer is not None:
            old_layer = self._dict[name]["layer"]
            self._dict[name]["layer"] = layer
            menu_obj = self._dict[name]["menu_obj"]
            menu_obj.layer = layer
            
            # Si l'état était actif, le déplacer vers le nouveau layer
            if old_layer in self._active_menus and self._active_menus[old_layer] == name:
                del self._active_menus[old_layer]
                self._active_menus[layer] = name
                # Nettoyer les layers supérieurs au nouveau layer
                self._clear_upper_layers(layer)

    def activate(self, name: str):
        """
        Active un état (remplace l'état sur le même layer et désactive les layers supérieurs)

        Args:
            name (str) : nom de l'état à activer
        """
        if name not in self._dict:
            self._raise_error('activate', f'menu "{name}" does not exist')
        
        layer = self._dict[name]["layer"]
        
        # on_exit pour l'ancien état du même layer
        if layer in self._active_menus:
            old_menu_name = self._active_menus[layer]
            old_menu_obj = self._dict[old_menu_name]["menu_obj"]
            if hasattr(old_menu_obj, 'on_exit') and callable(getattr(old_menu_obj, 'on_exit')):
                old_menu_obj.on_exit()
        
        # Activation
        self._active_menus[layer] = name
        
        # Nettoyer tous les layers au-dessus
        self._clear_upper_layers(layer)
        
        # on_enter pour le nouvel état
        menu_obj = self._dict[name]["menu_obj"]
        if hasattr(menu_obj, 'on_enter') and callable(getattr(menu_obj, 'on_enter')):
            menu_obj.on_enter()

    def deactivate(self, name: str):
        """
        Désactive un état (et tous les layers supérieurs)

        Args:
            name (str) : nom de l'état à désactiver
        """
        if name not in self._dict:
            return
        
        layer = self._dict[name]["layer"]
        if layer in self._active_menus and self._active_menus[layer] == name:
            # on_exit
            menu_obj = self._dict[name]["menu_obj"]
            if hasattr(menu_obj, 'on_exit') and callable(getattr(menu_obj, 'on_exit')):
                menu_obj.on_exit()
            
            del self._active_menus[layer]
            # Nettoyer tous les layers au-dessus
            self._clear_upper_layers(layer)

    def switch(self, name: str):
        """
        Change d'état en mode exclusif (désactive tout sauf cet état)
        
        Args:
            name (str) : nom de l'état à activer
        """
        if name not in self._dict:
            self._raise_error('switch', f'menu "{name}" does not exist')
        
        # on_exit pour tous les états actifs
        for layer, menu_name in list(self._active_menus.items()):
            menu_obj = self._dict[menu_name]["menu_obj"]
            if hasattr(menu_obj, 'on_exit') and callable(getattr(menu_obj, 'on_exit')):
                menu_obj.on_exit()
        
        # Reset complet
        layer = self._dict[name]["layer"]
        self._active_menus = {layer: name}
        
        # on_enter pour le nouvel état
        menu_obj = self._dict[name]["menu_obj"]
        if hasattr(menu_obj, 'on_enter') and callable(getattr(menu_obj, 'on_enter')):
            menu_obj.on_enter()

    def deactivate_layer(self, layer: int):
        """Désactive l'état sur un layer spécifique (et tous les layers supérieurs)"""
        if layer in self._active_menus:
            menu_name = self._active_menus[layer]
            menu_obj = self._dict[menu_name]["menu_obj"]
            if hasattr(menu_obj, 'on_exit') and callable(getattr(menu_obj, 'on_exit')):
                menu_obj.on_exit()
            
            del self._active_menus[layer]
            self._clear_upper_layers(layer)

    def deactivate_all(self):
        """Désactive tous les états"""
        # on_exit pour tous
        for menu_name in self._active_menus.values():
            menu_obj = self._dict[menu_name]["menu_obj"]
            if hasattr(menu_obj, 'on_exit') and callable(getattr(menu_obj, 'on_exit')):
                menu_obj.on_exit()
        
        self._active_menus = {}

    # ======================================== UPDATE ========================================
    def update(self):
        """
        Exécute les fonctions update de tous les états actifs
        (dans l'ordre des layers, du plus bas au plus haut)
        """
        sorted_layers = sorted(self._active_menus.keys())
        for i in range(len(sorted_layers)):
            menu_name = self._active_menus[sorted_layers[i]]
            menu_obj = self._dict[menu_name]["menu_obj"]
            getattr(menu_obj, "update", lambda: None)()
            if i == 0:
                from ... import screen
                menu_obj.draw(screen.surface)
            else:
                master_name = self._active_menus[sorted_layers[i-1]]
                master_obj = self._dict[master_name]["menu_obj"]
                master_surface = getattr(master_obj, "surface", lambda: None)
                getattr(menu_obj, "draw", lambda surface: None)(master_surface)

# ======================================== INSTANCE ========================================
menus_manager = MenusManager()