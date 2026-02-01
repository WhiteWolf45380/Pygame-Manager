# ======================================== IMPORTS ========================================
from _core import *

# ======================================== SUPER-CLASSE ========================================
class State:
    """
    Classe de base pour les states

    Fonctionnalités:
        S'enregistre automatiquement dans StatesManager lors de l'instanciation.
        Méthode update() à override pour la logique frame-to-frame.
        Méthode draw(surface) à n'override qu'en connaissance des conséquences.
        Les menus liés (bound_menus) sont auto-ouverts/fermés avec le state.
    """
    def __init__(self, name: str, layer: int = 0):
        """
        Args:
            name (str) : nom du state
            layer (int) : couche de priorité
        """
        # vérifications
        if not isinstance(name, str): self._raise_error('__init__', 'Invalid name argument')
        if not isinstance(layer, int): self._raise_error('__init__', 'Invalid layer argument')

        # paramètres d'état
        self._name = name
        self._layer = layer

        # menus automatiquement ouverts/fermés avec ce state
        self._bound_menus = []

        # auto-registration
        from .states import states_manager
        self.manager = states_manager
        self.manager.register(self)
    
    # ======================================== CALLBACKS ========================================
    def on_enter(self):
        """Appelé quand le state devient actif"""
        from ..menus import menus_manager
        for menu_name in self._bound_menus:
            menus_manager.activate(menu_name)

    def on_exit(self):
        """Appelé quand le state devient inactif — désactive les bound menus"""
        from ..menus import menus_manager
        for menu_name in self._bound_menus:
            menus_manager.deactivate(menu_name)

    # ======================================== BIND ========================================
    def bind_menu(self, menu_name: str):
        """Rattache un menu racine à ce state (auto ouvert/fermé)"""
        if menu_name not in self._bound_menus:
            self._bound_menus.append(menu_name)

    def unbind_menu(self, menu_name: str):
        """Détache un menu racine de ce state"""
        if menu_name in self._bound_menus:
            self._bound_menus.remove(menu_name)

    # ======================================== RENDER ========================================
    def update(self, *args, **kwargs):
        """Logique frame-to-frame à override"""
        pass

    # ======================================== RACCOURCIS ========================================
    def activate(self):
        self.manager.activate(self.name)

    def deactivate(self):
        self.manager.deactivate(self.name)

    def is_active(self) -> bool:
        return self.manager.is_active(self.name)