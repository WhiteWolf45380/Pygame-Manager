# ======================================== PORTAIL ========================================
class InputsGate:
    """
    Portail d'accès au gestionnaire des entrées utilisateur
    """
    def __init__(self):
        self.__inputs = InputsManager()
    
    def __getattr__(self, name):
        return getattr(self.__inputs, name)


# ======================================== GESTIONNAIRE ========================================
class InputsManager:
    """
    Gestionnaire des entrées utilisateur

    Fonctionnalités :
        - éxécuter une fonction prédéfinie de gestion des entrées
        - ajouter des listeners à certaines entrées
    """
    def __init__(self):
        pass

    def check(event):
        """
        Vérifie les actions associées à l'entrée

        Args :
            - event : événement pygame / entrée utilisateur
        """
        pass