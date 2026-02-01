# ======================================== IMPORTS ========================================
from ._state import State

# ======================================== MANAGER ========================================
class StatesManager:
    """
    Gestionnaire d'états avec exclusivité par layer.

    Fonctionnalités :
        plusieurs states actifs simultanément sur des layers différents
        exclusivité par layer (activer un state ferme l'ancien sur le même layer)
        cascade vers le haut : activer/changer un state ferme tous les layers supérieurs
        callbacks on_enter / on_exit
    """
    def __init__(self):
        self._dict = {}           # { name: { "layer": int, "state_obj": State } }
        self._active_states = {}  # { layer: name }

        self.state = State

    def __repr__(self):
        if self._active_states:
            active_list = [f"{name}(L{layer})" for layer, name in sorted(self._active_states.items())]
            active = ', '.join(active_list)
        else:
            active = 'None'
        return f"<StatesManager: {len(self._dict)} states | Active: [{active}]>"

    # ======================================== METHODES PRIVEES ========================================
    def _clear_upper_layers(self, layer: int):
        """Désactive tous les states sur les layers strictement supérieurs"""
        layers_to_remove = [l for l in self._active_states if l > layer]
        for l in sorted(layers_to_remove):
            state_name = self._active_states[l]
            state_obj = self._dict[state_name]["state_obj"]
            state_obj.on_exit()
            del self._active_states[l]

    # ======================================== GETTERS ========================================
    def get_states(self) -> list:
        """Renvoie l'ensemble des états"""
        return list(self._dict.keys())
    
    def get_layer(self, name: str) -> int:
        """Renvoie l'ensemble des états sur une couche donnée"""
        if name not in self._dict:
            self._raise_error('get_layer', f'state "{name}" does not exist')
        return self._dict[name]["layer"]

    def get_active_states(self) -> list:
        """Renvoie les états actifs triés par couche croissante"""
        return [self._active_states[l] for l in sorted(self._active_states)]

    def get_active_by_layer(self, layer: int) -> str | None:
        """Renvoie l'état actif à une couche donnée"""
        return self._active_states.get(layer)
    
    def __getitem__(self, key):
        """Renvoie l'objet d'un état donné"""
        if key not in self._dict:
            self._raise_error('__getitem__', f'state "{key}" does not exist')
        return self._dict[key]["state_obj"]
    
    def get_object(self, name: str) -> State | None:
        """Renvoie l'objet d'un état donné"""
        if name not in self._dict:
            return None
        return self._dict[name]["state_obj"]
    
    # ======================================== PREDICATS ========================================
    def __contains__(self, state: str | State):
        """Vérifie l'enregistrement d'un état"""
        if isinstance(state, str):
            return state in self._dict.keys()
        return state in self._dict.values()

    def is_active(self, name: str) -> bool:
        """Vérifie qu'un état soit actif"""
        return name in self._active_states.values()
    
    def is_layer_active(self, layer: int) -> bool:
        """Vérifie qu'une couche soit active"""
        return self._active_states.get(layer) is not None

    # ======================================== ENREGISTREMENT ========================================
    def register(self, name: str, obj: State, layer: int=0):
        """Enregistre un objet State"""
        if name in self._dict:
            self._raise_error('register', f'state "{name}" already exists')
        self._dict[name] = {
            "layer": layer,
            "state_obj": obj,
        }

    # ======================================== ACTIVATION ========================================
    def activate(self, name: str):
        """
        Active un state
        Remplace l'ancien state sur le même layer (on_exit) et ferme les layers supérieurs

        Args:
            name (str) : nom de l'état à activer
        """
        if name not in self._dict:
            self._raise_error('activate', f'state "{name}" does not exist')

        layer = self._dict[name]["layer"]

        if layer in self._active_states:
            old_name = self._active_states[layer]
            old_obj = self._dict[old_name]["state_obj"]
            old_obj.on_exit()

        self._active_states[layer] = name
        self._clear_upper_layers(layer)
        self._dict[name]["state_obj"].on_enter()

    def deactivate(self, name: str, pruning: bool = True):
        """
        Désactive un state

        Args:
            name (str) : nom de l'état à désactiver
            pruning (bool, optional) : fermeture de tous les états supérieurs
        """
        if name not in self._dict:
            return

        layer = self._dict[name]["layer"]
        if layer in self._active_states and self._active_states[layer] == name:
            self._dict[name]["state_obj"].on_exit()
            del self._active_states[layer]
            if pruning:
                self._clear_upper_layers(layer)

    def deactivate_layer(self, layer: int, pruning: bool = True):
        """
        Désactive l'état sur une couche donnée

        Args:
            layer (int) : couche à désactiver
            pruning (bool) : désactivation des couches supérieures
        """
        if layer in self._active_states:
            name = self._active_states[layer]
            self._dict[name]["state_obj"].on_exit()
            del self._active_states[layer]
            if pruning:
                self._clear_upper_layers(layer)

    def deactivate_all(self):
        """
        Désactive tous les states
        """
        for layer in sorted(self._active_states, reverse=True):
            name = self._active_states[layer]
            self._dict[name]["state_obj"].on_exit()
        self._active_states = {}

    # ======================================== UPDATE ========================================
    def update(self):
        """
        Exécute update() de tous les states actifs,
        """
        for layer in sorted(self._active_states):
            name = self._active_states[layer]
            state_obj = self._dict[name]["state_obj"]
            state_obj.update()

# ======================================== INSTANCE ========================================
states_manager = StatesManager()