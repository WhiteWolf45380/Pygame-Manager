# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== SUPER-CLASSE ========================================
class State:
    """
    Classe de base pour les states

    Fonctionnalités:
        S'enregistre automatiquement dans StatesManager lors de l'instanciation
        Méthode update() à override pour la logique frame-to-frame
        Méthode draw(surface) à n'override qu'en connaissance des conséquences
        Les panels liés (bound_panels) sont auto-ouverts/fermés avec le state
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

        # panels automatiquement ouverts/fermés avec ce state
        self._bound_panels = []

        # auto-registration
        context.states.register(self._name, self, layer=self._layer)
    
    def __str__(self):
        """Renvoie le nom de l'état"""
        return self._name
    
    # ======================================== CALLBACKS ========================================
    def on_enter(self):
        """Appelé quand le state devient actif"""
        for panel_name in self._bound_panels:
            if panel_name not in context.panels:
                continue
            context.panels.activate(panel_name)

    def on_exit(self):
        """Appelé quand le state devient inactif — désactive les bound panels"""
        for panel_name in self._bound_panels:
            if panel_name not in context.panels:
                continue
            context.panels.deactivate(panel_name)

    # ======================================== BIND ========================================
    def bind_panel(self, panel: str | object):
        """Rattache un panel racine à ce state (auto ouvert/fermé)"""
        if isinstance(panel, context.panels.Panel):
            panel = panel._name
        if panel not in self._bound_panels:
            self._bound_panels.append(panel)

    def unbind_panel(self, panel: str | object):
        """Détache un panel racine de ce state"""
        if isinstance(panel, context.panels.Panel):
            panel = panel._name
        if panel in self._bound_panels:
            self._bound_panels.remove(panel)

    # ======================================== RENDER ========================================
    def update(self, *args, **kwargs):
        """Logique frame-to-frame à override"""
        pass

    # ======================================== RACCOURCIS ========================================
    def activate(self):
        """Active l'état"""
        context.states.activate(self.name)

    def deactivate(self):
        """Désactive l'état"""
        context.states.deactivate(self.name)

    def is_active(self) -> bool:
        """Vérifie l'activation de l'état"""
        return context.states.is_active(self.name)