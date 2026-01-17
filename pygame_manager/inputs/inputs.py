# ======================================== GESTIONNAIRE ========================================
class InputsManager:
    """
    Gestionnaire des entrées utilisateur

    Fonctionnalités :
        - éxécuter une fonction prédéfinie de gestion des entrées
        - ajouter des listeners à certaines entrées
    """
    def __init__(self):
        self.__listeners = {}

    # ======================================== METHODES INTERACTIVES ========================================
    def add_listener(self, event_type: int, callback: callable, condition: callable=None, once: bool=False, one_frame: bool=False, priority: int=0):
        """
        Ajoute un listener sur une entrée utilisateur

        Args :
            - event_type (int) : événement utilisateur correspondant
            - callback (calable) : fonction associée
            - condition (callable) : condition supplémentaire
            - once (bool) : n'éxécute l'action qu'une fois
            - one_frame (bool) : supprime automatiquement le lister à la fin de la frame
            - priority (int) : niveau de priorité du listener si plusieurs ont été associés au même événement
        """
        listener = {
            "callback" : callback,
            "condition": condition,
            "once": once,
            "one_frame": one_frame,
            "priority": priority,
        }

        if event_type not in self.__listeners:
            self.__listeners[event_type] = [listener]
            return
        for i, l in enumerate(self.__listeners[event_type]):
            if priority > l["priority"]:
                self.__listeners[event_type].insert(i, listener)
                return
        self.__listeners[event_type].append(listener)

    def remove_listener(self, event_type: int, callback: callable):
        """
        Supprime un listener sur une entrée utilisateur

        Args :
            - event_type (int) : entrée utilisateur
            - callback (callable) : fonction associée
        """
        self.__listeners[event_type] = list(filter(lambda l: l["callback"] != callback, self.__listeners[event_type]))

    def check(self, event: int):
        """
        Vérifie les actions associées à l'entrée

        Args :
            - event : événement pygame / entrée utilisateur
        """
        to_remove = []
        for listener in self.__listeners.get(event, []):
            if listener["one_frame"]:
                to_remove.append(listener)
            
            if listener["condition"] and not listener["condition"]():
                continue

            listener["callback"]()

            if listener["once"] and not listener["one_frame"]:
                to_remove.append(listener)

        for listener in to_remove:
            self.__listeners[event].remove(listener)