# ======================================== IMPORTS ========================================
from ._core import _raise_error, context
from ._state import State, pygame
from typing import Optional

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
        # Stockage
        self._dict = {}           # { name: { "layer": int, "state_obj": State } }
        self._active_states = {}  # { layer: name }

        # Etats disponibles
        self.State = State

        # Paramètres
        self._transition_surface = pygame.Surface((1920, 1080))
        self._transition_surface.fill((0, 0, 0))
        self._transition_alpha = 0
        self._transition_surface.set_alpha(0)
        self._transition_duration = 0.5
        self._transition_active = False
        self._transition_timer = 0.0
        self._transition_old = None
        self._transition_new = None
        self._transition_new_layer = 0
        self._transition_switched = False

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

    def _start_transition(self, duration: Optional[float] = None):
        """Initialise une transition"""
        if duration is None:
            duration = self._transition_duration
        self._transition_active = True
        self._transition_timer = 0.0
        self._transition_switched = False
    
    def _update_transition(self, screen_size):
        """Met à jour la transition en cours"""
        self._transition_timer = min(self._transition_duration, self._transition_timer + context.time.dt)
        progress = self._transition_timer / self._transition_duration
        
        if progress < 0.5:
            self._transition_alpha = progress * 2 * 255
        else:
            self._transition_alpha = (1 - (progress - 0.5) * 2) * 255
            if not self._transition_switched:
                self._midstep_transition()
                self._transition_switched = True
        
        if self._transition_timer >= self._transition_duration:
            self._end_transition()

    def _midstep_transition(self):
        """Moitié de la transition"""
        if self._transition_old is not None:
            old_obj = self._dict[self._transition_old]["state_obj"]
            old_obj.on_exit()

        self._active_states[self._transition_new_layer] = self._transition_new
        self._clear_upper_layers(self._transition_new_layer)
        self._dict[self._transition_new]["state_obj"].on_enter()
    
    def _end_transition(self):
        """Fin de la transition"""
        self._transition_active = False
        self._transition_timer = 0.0
        self._transition_alpha = 0
        self._transition_old = None
        self._transition_new = None
        self._transition_switched = False

    def _draw_transition(self):
        """Dessine le voile de transition"""
        if self._transition_active and self._transition_surface is not None:
            self._transition_surface.set_alpha(int(self._transition_alpha))
            context.screen.blit_last(self._transition_surface, (0, 0))

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
    
    def get_transition_duration(self) -> float:
        """Renvoie la durée de transition en secondes"""
        return self._transition_duration
    
    # ======================================== SETTERS ========================================
    def set_transition_duration(self, duration: float):
        """Définit la durée de transition en secondes"""
        if not isinstance(duration, float) or duration < 0:
            _raise_error(self, 'set_transition_duration', 'Invalid duration argument')
        self._transition_duration = duration
    
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
    def activate(self, name: str, transition: bool = True):
        """
        Active un state
        Remplace l'ancien state sur le même layer (on_exit) et ferme les layers supérieurs

        Args:
            name (str) : nom de l'état à activer
            transition (bool) : active une transition en fondu
        """
        if name not in self._dict:
            self._raise_error('activate', f'state "{name}" does not exist')
        self._transition_new = name

        self._transition_new_layer = self._dict[name]["layer"]
        if self._transition_new_layer in self._active_states: self._transition_old = self._active_states[self._transition_new_layer]
        else: self._transition_old = None
        
        if not transition:
            self._midstep_transition()
            self._end_transition()
            return
        self._start_transition()

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
        if self._transition_active:
            self._update_transition(None)
        
        for layer in sorted(self._active_states):
            name = self._active_states[layer]
            state_obj = self._dict[name]["state_obj"]
            state_obj.update()
        
        self._draw_transition()

# ======================================== INSTANCE ========================================
states_manager = StatesManager()