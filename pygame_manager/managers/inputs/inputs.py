# ======================================== GESTIONNAIRE ========================================
from ... import context
import pygame

# ======================================== GESTIONNAIRE ========================================
class InputsManager:
    """
    Gestionnaire des entrées utilisateur

    Fonctionnalités :
        éxécuter une fonction prédéfinie de gestion des entrées
        ajouter des listeners à certaines entrées
    """
    def __init__(self):
        self._listeners = {}       # ensemble des listeners
        self._step = []            # touches qui viennent d'être pressées
        self._pressed = {}         # touches pressées

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur

        Args :
            method (str) : méthode dans laquelle l'erreur survient
            text (str) : message d'erreur
        """
        raise RuntimeError(f"[{self._class__.__name__}].{method} : {text}")

    # ======================================== METHODES INTERACTIVES ========================================
    @staticmethod
    def get_id(event):
        """
        Abstraction du type d'input en int unique
        
        Args :
            event (pygame.event.Event) : événement en tout genre
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

    def add_listener(self, event_id: int, callback: callable, args: list=[], kwargs: dict={}, up: bool=False, condition: callable=None, once: bool=False, repeat: bool=False, priority: int=0, give_key: bool = False):
        """
        Ajoute un listener sur une entrée utilisateur

        Args:
            event_id (int) : événement utilisateur correspondant
            callback (callable) : fonction associée
            up (bool, optional) : action lorsque la touche est relâchée
            condition (callable, optional) : condition supplémentaire
            once (bool, optional) : n'éxécute l'action qu'une fois
            repeat (bool, optional) : le maintient du boutton répète l'action
            priority (int, optional) : niveau de priorité du listener si plusieurs ont été associés au même événement
            give_key (bool, optional) : passe la clé de l'entrée au callback
        """
        listener = {
            "callback": callback,
            "up": up,
            "condition": condition,
            "once": once,
            "repeat": repeat,
            "priority": priority,
            "give_key": give_key,
            "args": args,
            "kwargs": kwargs,
        }

        if event_id not in self._listeners:
            self._listeners[event_id] = [listener]
            return
        for i, l in enumerate(self._listeners[event_id]):
            if priority > l["priority"]:
                self._listeners[event_id].insert(i, listener)
                return
        self._listeners[event_id].append(listener)

    def remove_listener(self, event_id: int, callback: callable):
        """
        Supprime un listener sur une entrée utilisateur

        Args :
            event_id (int) : entrée utilisateur
            callback (callable) : fonction associée
        """
        if event_id in self._listeners:
            self._listeners[event_id] = [l for l in self._listeners[event_id] if l["callback"] != callback]

    def check_event(self, event):
        """
        Vérifie les actions associées à l'entrée

        Args :
            event : événement pygame / entrée utilisateur
        """
        event_id = self.get_id(event)
        up = event.type in [pygame.MOUSEBUTTONUP, pygame.KEYUP]

        # maintient / relâchement
        if up:
            self._pressed[event_id] = False
        else:
            self._step.append(event_id)
        
        # listeners
        to_remove = []
        for listener in self._listeners.get(event_id, []):            
            if listener["condition"] and not listener["condition"]() or up != listener["up"]:
                continue
            
            if listener["give_key"]: listener["callback"](*listener["args"], **listener["kwargs"], key=event_id)
            else: listener["callback"](*listener["args"], **listener["kwargs"])

            if listener["once"]:
                to_remove.append(listener)

        # suppression du listener
        for listener in to_remove:
            self._listeners[event_id].remove(listener)
    
    def check_pressed(self):
        """
        Vérifie les listeners de maintient
        """
        for event_id, listeners in self._listeners.items():
            if self._pressed.get(event_id, False):
                for listener in listeners:
                    if listener["repeat"]:
                        if listener["condition"] and not listener["condition"]():
                            continue
                        listener["callback"](*listener["args"], **listener["kwargs"])
        
        # ajout des nouvelles touches pressées
        for event_id in self._step:
            self._pressed[event_id] = True
        self._step = []
    
    def check_all(self):
        """
        Vérifie l'ensemble des listeners
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                context.engine.stop()
                return False
            self.check_event(event)
        self.check_pressed()
        return True
    
    def is_pressed(self, event_id: int) -> bool:
        """
        Vérifie si une touche ou un bouton est actuellement enfoncé

        Args :
            event_id (int) : identifiant unifié de l'entrée
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