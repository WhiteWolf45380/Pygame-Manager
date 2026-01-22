# ======================================== GESTIONNAIRE ========================================
class StatesManager:
    """
    Gestionnaire des états multi-layers avec remplacement par layer

    Fonctionnalités :
        - stocker différentes méthodes d'état
        - gérer plusieurs états actifs simultanément
        - système de layers avec remplacement automatique sur le même layer
        - désactivation en cascade des layers supérieurs
    """
    def __init__(self):
        self.__dict = {}
        self.__active_states = {}

    # ======================================== METHODES FONCTIONNELLES ========================================
    def __repr__(self):
        if self.__active_states:
            active_list = [f"{name}(L{layer})" for layer, name in sorted(self.__active_states.items())]
            active = ', '.join(active_list)
        else:
            active = 'None'
        return f"<StatesManager: {len(self.__dict)} states | Active: [{active}]>"

    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def _clear_upper_layers(self, layer: int):
        """Désactive tous les états sur les layers supérieurs"""
        layers_to_remove = [l for l in self.__active_states.keys() if l > layer]
        for l in layers_to_remove:
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

    # ======================================== METHODES INTERACTIVES ========================================
    def add(self, name: str, update: callable, layer: int = 0):
        """
        Ajoute un nouvel état

        Args :
            - name (str) : nom de l'état
            - update (callable) : fonction d'actualisation par frame
            - layer (int) : niveau de priorité
        """
        if not isinstance(name, str):
            self._raise_error('add', 'State name must be a string object')
        if not callable(update):
            self._raise_error('add', 'State update must be a callable object')
        if name in self.__dict:
            self._raise_error('add', f'State "{name}" already exists.\nIf you want to modify it, try : set(name, update)')
        
        self.__dict[name] = {
            "layer": layer,
            "update": update
        }

    def set(self, name: str, update: callable = None, layer: int = None):
        """
        Modifie un état existant

        Args :
            - name (str) : nom de l'état
            - update (callable, optional) : nouvelle fonction d'actualisation
            - layer (int, optional) : nouveau layer
        """
        if not isinstance(name, str):
            self._raise_error('set', 'State name must be a string object')
        if name not in self.__dict:
            self._raise_error('set', f'State "{name}" does not exist.\nIf you want to add it, try : add(name, update, layer)')
        
        if update is not None:
            if not callable(update):
                self._raise_error('set', 'State update must be a callable object')
            self.__dict[name]["update"] = update
        
        if layer is not None:
            old_layer = self.__dict[name]["layer"]
            self.__dict[name]["layer"] = layer
            
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
        self.__active_states[layer] = name
        self._clear_upper_layers(layer)

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
            del self.__active_states[layer]
            self._clear_upper_layers(layer)

    def deactivate_layer(self, layer: int):
        """Désactive l'état sur un layer spécifique (et tous les layers supérieurs)"""
        if layer in self.__active_states:
            del self.__active_states[layer]
            self._clear_upper_layers(layer)

    def deactivate_all(self):
        """Désactive tous les états"""
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
            self.__dict[state_name]["update"]()


# ======================================== INSTANCE ========================================
states_manager = StatesManager()


# ======================================== SUPER-CLASSE ========================================
class State:
    """
    Classe de base pour les états
    
    S'enregistre automatiquement dans StatesManager lors de l'instanciation
    """
    def __init__(self, name: str, manager: StatesManager, layer: int = 0):
        """
        Args :
            - name (str) : nom de l'état
            - manager (StatesManager) : gestionnaire d'états
            - layer (int) : niveau de priorité
        """
        self.name = name
        self.layer = layer
        self.manager = manager
        
        # Auto-registration
        self.manager.add(self.name, self.update, self.layer)
    
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