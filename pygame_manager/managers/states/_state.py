# ======================================== SUPER-CLASSE ========================================
class StateObject:
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
        from .states import states_manager
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