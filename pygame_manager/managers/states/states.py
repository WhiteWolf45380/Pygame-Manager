# ======================================== GESTIONNAIRE ========================================
class StatesManager:
    """
    Gestionnaire des états multi-layers avec remplacement par layer

    Fonctionnalités :
        - stocker différentes méthodes d'état
        - gérer plusieurs états actifs simultanément
        - système de layers avec remplacement automatique sur le même layer
        - désactivation en cascade des layers supérieurs
        - callbacks on_enter/on_exit
    """
    def __init__(self):
        # gestion des états
        self.__dict = {}
        self.__active_states = {}

        # super-classe
        self.State = None

    # ======================================== METHODES FONCTIONNELLES ========================================
    def __repr__(self):
        if self.__active_states:
            active_list = [f"{name}(L{layer})" for layer, name in sorted(self.__active_states.items())]
            active = ', '.join(active_list)
        else:
            active = 'None'
        return f"<StatesManager: {len(self.__dict)} states | Active: [{active}]>"
    
    def __getitem__(self, key):
        return self.__dict.get(key)

    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def _clear_upper_layers(self, layer: int):
        """Désactive tous les états sur les layers supérieurs"""
        layers_to_remove = [l for l in self.__active_states.keys() if l > layer]
        for l in layers_to_remove:
            state_name = self.__active_states[l]
            state_obj = self.__dict[state_name]["state_obj"]
            # Appeler on_exit si la méthode existe
            if hasattr(state_obj, 'on_exit') and callable(getattr(state_obj, 'on_exit')):
                state_obj.on_exit()
            del self.__active_states[l]
    
    # ======================================== GETTERS ========================================
    def get_states(self) -> list:
        """Retourne la liste de tous les états disponibles"""
        return list(self.__dict.keys())

    def get_active_states(self) -> list:
        """Retourne la liste des états actifs (triés par layer)"""
        sorted_layers = sorted(self.__active_states.keys())
        return [self.__active_states[layer] for layer in sorted_layers]

    def get_active_by_layer(self, layer: int) -> str | None:
        """Retourne l'état actif sur un layer donné"""
        return self.__active_states.get(layer)

    def get_layer(self, name: str) -> int:
        """Retourne le layer d'un état"""
        if name not in self.__dict:
            self._raise_error('get_layer', f'State "{name}" does not exist')
        return self.__dict[name]["layer"]

    def is_active(self, name: str) -> bool:
        """Vérifie si un état est actif"""
        if name not in self.__dict:
            return False
        layer = self.__dict[name]["layer"]
        return self.__active_states.get(layer) == name
    
    def get_state_object(self, name: str):
        """Retourne l'objet State associé à un nom"""
        if name not in self.__dict:
            return None
        return self.__dict[name]["state_obj"]

    # ======================================== METHODES INTERACTIVES ========================================
    def register(self, state_obj):
        """
        Enregistre un objet état

        Args :
            - state_obj : objet State avec attributs name, layer et méthode update
        """
        if not hasattr(state_obj, 'name') or not isinstance(state_obj.name, str):
            self._raise_error('register', 'State object must have a "name" attribute (str)')
        if not hasattr(state_obj, 'layer'):
            self._raise_error('register', 'State object must have a "layer" attribute')
        if not hasattr(state_obj, 'update') or not callable(getattr(state_obj, 'update')):
            self._raise_error('register', 'State object must have a callable "update" method')
        
        name = state_obj.name
        if name in self.__dict:
            self._raise_error('register', f'State "{name}" already exists')
        
        self.__dict[name] = {
            "layer": state_obj.layer,
            "state_obj": state_obj
        }

    def set(self, name: str, layer: int = None):
        """
        Modifie un état existant

        Args :
            - name (str) : nom de l'état
            - layer (int, optional) : nouveau layer
        """
        if not isinstance(name, str):
            self._raise_error('set', 'State name must be a string object')
        if name not in self.__dict:
            self._raise_error('set', f'State "{name}" does not exist')
        
        if layer is not None:
            old_layer = self.__dict[name]["layer"]
            self.__dict[name]["layer"] = layer
            state_obj = self.__dict[name]["state_obj"]
            state_obj.layer = layer
            
            # Si l'état était actif, le déplacer vers le nouveau layer
            if old_layer in self.__active_states and self.__active_states[old_layer] == name:
                del self.__active_states[old_layer]
                self.__active_states[layer] = name
                # Nettoyer les layers supérieurs au nouveau layer
                self._clear_upper_layers(layer)

    def activate(self, name: str):
        """
        Active un état (remplace l'état sur le même layer et désactive les layers supérieurs)

        Args :
            - name (str) : nom de l'état à activer
        """
        if name not in self.__dict:
            self._raise_error('activate', f'State "{name}" does not exist')
        
        layer = self.__dict[name]["layer"]
        
        # on_exit pour l'ancien état du même layer
        if layer in self.__active_states:
            old_state_name = self.__active_states[layer]
            old_state_obj = self.__dict[old_state_name]["state_obj"]
            if hasattr(old_state_obj, 'on_exit') and callable(getattr(old_state_obj, 'on_exit')):
                old_state_obj.on_exit()
        
        # Activation
        self.__active_states[layer] = name
        
        # Nettoyer tous les layers au-dessus
        self._clear_upper_layers(layer)
        
        # on_enter pour le nouvel état
        state_obj = self.__dict[name]["state_obj"]
        if hasattr(state_obj, 'on_enter') and callable(getattr(state_obj, 'on_enter')):
            state_obj.on_enter()

    def deactivate(self, name: str):
        """
        Désactive un état (et tous les layers supérieurs)

        Args :
            - name (str) : nom de l'état à désactiver
        """
        if name not in self.__dict:
            return
        
        layer = self.__dict[name]["layer"]
        if layer in self.__active_states and self.__active_states[layer] == name:
            # on_exit
            state_obj = self.__dict[name]["state_obj"]
            if hasattr(state_obj, 'on_exit') and callable(getattr(state_obj, 'on_exit')):
                state_obj.on_exit()
            
            del self.__active_states[layer]
            # Nettoyer tous les layers au-dessus
            self._clear_upper_layers(layer)

    def switch(self, name: str):
        """
        Change d'état en mode exclusif (désactive tout sauf cet état)
        
        Args :
            - name (str) : nom de l'état à activer
        """
        if name not in self.__dict:
            self._raise_error('switch', f'State "{name}" does not exist')
        
        # on_exit pour tous les états actifs
        for layer, state_name in list(self.__active_states.items()):
            state_obj = self.__dict[state_name]["state_obj"]
            if hasattr(state_obj, 'on_exit') and callable(getattr(state_obj, 'on_exit')):
                state_obj.on_exit()
        
        # Reset complet
        layer = self.__dict[name]["layer"]
        self.__active_states = {layer: name}
        
        # on_enter pour le nouvel état
        state_obj = self.__dict[name]["state_obj"]
        if hasattr(state_obj, 'on_enter') and callable(getattr(state_obj, 'on_enter')):
            state_obj.on_enter()

    def deactivate_layer(self, layer: int):
        """Désactive l'état sur un layer spécifique (et tous les layers supérieurs)"""
        if layer in self.__active_states:
            state_name = self.__active_states[layer]
            state_obj = self.__dict[state_name]["state_obj"]
            if hasattr(state_obj, 'on_exit') and callable(getattr(state_obj, 'on_exit')):
                state_obj.on_exit()
            
            del self.__active_states[layer]
            self._clear_upper_layers(layer)

    def deactivate_all(self):
        """Désactive tous les états"""
        # on_exit pour tous
        for state_name in self.__active_states.values():
            state_obj = self.__dict[state_name]["state_obj"]
            if hasattr(state_obj, 'on_exit') and callable(getattr(state_obj, 'on_exit')):
                state_obj.on_exit()
        
        self.__active_states = {}

    # ======================================== UPDATE ========================================
    def update(self):
        """
        Exécute les fonctions update de tous les états actifs
        (dans l'ordre des layers, du plus bas au plus haut)
        """
        sorted_layers = sorted(self.__active_states.keys())
        for layer in sorted_layers:
            state_name = self.__active_states[layer]
            state_obj = self.__dict[state_name]["state_obj"]
            state_obj.update()


# ======================================== INSTANCE ========================================
states_manager = StatesManager()


# ======================================== SUPER-CLASSE ========================================
class State:
    """
    Classe de base pour les états
    
    S'enregistre automatiquement dans StatesManager lors de l'instanciation
    """
    def __init__(self, name: str, layer: int = 0):
        """
        Args :
            - name (str) : nom de l'état
            - manager (StatesManager) : gestionnaire d'états
            - layer (int) : niveau de priorité
        """
        global states_manager
        self.name = name
        self.layer = layer
        self.manager = states_manager
        
        # auto-registration
        self.manager.register(self)
    
    def update(self, *args, **kwargs):
        """
        Méthode appelée chaque frame quand l'état est actif
        À override dans les sous-classes
        """
        pass
    
    def on_enter(self):
        """Appelé quand l'état devient actif"""
        pass
    
    def on_exit(self):
        """Appelé quand l'état devient inactif"""
        pass
    
    def activate(self):
        """Active cet état"""
        self.manager.activate(self.name)
    
    def deactivate(self):
        """Désactive cet état"""
        self.manager.deactivate(self.name)
    
    def is_active(self) -> bool:
        """Vérifie si cet état est actif"""
        return self.manager.is_active(self.name)

states_manager.State = State