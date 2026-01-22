import pygame


# ======================================== GESTIONNAIRE ========================================
class InputsManager:
    """
    Gestionnaire des entrées utilisateur

    Fonctionnalités :
        - éxécuter une fonction prédéfinie de gestion des entrées
        - ajouter des listeners à certaines entrées
    """
    def __init__(self):
        self.__listeners = {}       # ensemble des listeners
        self.__step = []            # touches qui viennent d'être pressées
        self.__pressed = {}         # touches pressées

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur

        Args :
            - method (str) : méthode dans laquelle l'erreur survient
            - text (str) : message d'erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== METHODES INTERACTIVES ========================================
    @staticmethod
    def get_id(event):
        """
        Abstraction du type d'input en int unique
        
        Args :
            - event (pygame.event.Event) : événement en tout genre
        """
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            return event.button
        elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            return event.key
        else:
            return event.type
    
    @property
    def MOUSELEFT(self):
        """Renvoie l'id correspondant au bouton gauche de la souris"""
        return 1
    
    @property
    def MOUSEWHEEL(self):
        """Renvoie l'id correspondant au bouton central de la souris"""
        return 2
    
    @property
    def MOUSERIGHT(self):
        """Renvoie l'id correspondant au bouton droit de la souris"""
        return 3
    
    @property
    def MOUSEWHEELUP(self):
        """Renvoie l'id correspondant au scroll vers la haut"""
        return 4
    
    @property
    def MOUSEWHEELDOWN(self):
        """Renvoie l'id correspondant au scroll vers le bas"""
        return 5
    
    @property
    def MOUSEBACKWARD(self):
        """Renvoie l'id correspondant au bouton droit de la souris"""
        return 8
    
    @property
    def MOUSEFORWARD(self):
        """Renvoie l'id correspondant au premier latéral de la souris"""
        return 9

    def add_listener(self, event_id: int, callback: callable, up: bool=False,condition: callable=None, once: bool=False, one_frame: bool=False, repeat: bool=False, priority: int=0):
        """
        Ajoute un listener sur une entrée utilisateur

        Args :
            - event_id (int) : événement utilisateur correspondant
            - callback (calable) : fonction associée
            - up (bool) : action lorsque la touche est relâchée
            - condition (callable) : condition supplémentaire
            - once (bool) : n'éxécute l'action qu'une fois
            - one_frame (bool) : supprime automatiquement le lister à la fin de la frame
            - repeat (bool) : le maintient du boutton répète l'action
            - priority (int) : niveau de priorité du listener si plusieurs ont été associés au même événement
        """
        listener = {
            "callback": callback,
            "up": up,
            "condition": condition,
            "once": once,
            "one_frame": one_frame,
            "repeat": repeat,
            "priority": priority,
        }

        if event_id not in self.__listeners:
            self.__listeners[event_id] = [listener]
            return
        for i, l in enumerate(self.__listeners[event_id]):
            if priority > l["priority"]:
                self.__listeners[event_id].insert(i, listener)
                return
        self.__listeners[event_id].append(listener)

    def remove_listener(self, event_id: int, callback: callable):
        """
        Supprime un listener sur une entrée utilisateur

        Args :
            - event_id (int) : entrée utilisateur
            - callback (callable) : fonction associée
        """
        if event_id in self.__listeners:
            self.__listeners[event_id] = [l for l in self.__listeners[event_id] if l["callback"] != callback]

    def check_event(self, event):
        """
        Vérifie les actions associées à l'entrée

        Args :
            - event : événement pygame / entrée utilisateur
        """
        event_id = self.get_id(event)
        up = event.type in [pygame.MOUSEBUTTONUP, pygame.KEYUP]

        # maintient / relâchement
        if up:
            self.step.append(event_id)
        else:
            self.__pressed[event_id] = True
        
        # listeners
        to_remove = []
        for listener in self.__listeners.get(event_id, []):
            if listener["one_frame"]:
                to_remove.append(listener)
            
            if listener["condition"] and not listener["condition"]() or up != listener["up"]:
                continue

            listener["callback"]()

            if listener["once"] and not listener["one_frame"]:
                to_remove.append(listener)

        # suppression du listener
        for listener in to_remove:
            self.__listeners[event_id].remove(listener)
    
    def check_pressed(self):
        """
        Vérifie les listeners de maintient
        """
        for event_id, listener in self.__listeners.items():
            if listener["repeat"] and not self.__pressed[event_id]:
                if listener["condition"] and not listener["condition"]():
                    continue
                listener["callback"]()
        
        # ajout des nouvelles touches pressées
        for event_id in self.__step:
            self.__pressed[event_id] = True
    
    def check_all(self):
        """
        Vérifie l'ensemble des listeners
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            self.check_event(event)
        self.check_pressed()
        return True
    
    def is_pressed(self, event_id: int) -> bool:
        """
        Vérifie si une touche ou un bouton est actuellement enfoncé

        Args :
            - event_id (int) : identifiant unifié de l'entrée
        """
        # clavier
        pressed_keys = pygame.key.get_pressed()
        if 0 <= event_id < len(pressed_keys):
            return pressed_keys[event_id]

        # boutons souris
        pressed_buttons = pygame.mouse.get_pressed()
        if 1 <= event_id <= 3:  # boutons 1 à 3
            return pressed_buttons[event_id - 1]

        # autres types
        return False
    

# ======================================== INSTANCE ========================================
inputs_manager = InputsManager()