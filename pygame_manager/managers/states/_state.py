# ======================================== IMPORTS ========================================
import pygame

# ======================================== SUPER-CLASSE ========================================
class StateObject:
    """
    Classe de base pour les états
    
    S'enregistre automatiquement dans StatesManager lors de l'instanciation
    Méthode update() à override pour actualisation automatique
    Méthode draw(surface) affiche la surface de l'état sur une surface donnée
    """
    def __init__(self, name: str, layer: int = 0, width: int=1920, height: int=1080):
        """
        Args:
            name (str) : nom de l'état
            manager (StatesManager) : gestionnaire d'états
            layer (int) : niveau de priorité
            width (int, optional) : largeur de la surface de l'état
            height (int, optional) : hauteur de la surface de l'état
        """
        # vérifications
        if not isinstance(name , str): self._raise_error('__init__', 'Invalid name argument')
        if not isinstance(layer , int): self._raise_error('__init__', 'Invalid layer argument')
        if not isinstance(width , int) or width <= 0: self._raise_error('__init__', 'Invalid width argument')
        if not isinstance(height , int): self._raise_error('__init__', 'Invalid height argument')

        # propriétés de l'état
        self.name = name
        self.layer = layer

        # surface
        self.surface_width = width
        self.surface_height = height
        self.surface = pygame.Surface((self.surface_width, self.surface_height))
        self.surface_rect = self.surface.get_rect()
        
        # auto-registration
        from .states import states_manager
        self.manager = states_manager
        self.manager.register(self)
    
    def _raise_error(self, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def update(self, *args, **kwargs):
        """
        Méthode appelée chaque frame quand l'état est actif
        À override dans les sous-classes
        """
        pass

    def draw(self, surface: pygame.Surface):
        """Affiche la surface de l'état"""
        if not isinstance(surface, pygame.Surface):
            return None
        surface.blit(self.surface, self.surface_rect)
    
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