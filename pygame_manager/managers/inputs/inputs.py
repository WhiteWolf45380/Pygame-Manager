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

    # Constantes pour les boutons de souris
    MOUSELEFT = 1
    MOUSEWHEEL = 2
    MOUSERIGHT = 3
    MOUSEWHEELUP = 4
    MOUSEWHEELDOWN = 5
    MOUSEBACKWARD = 8
    MOUSEFORWARD = 9

    def __init__(self):
        self._listeners = {}            # ensemble des listeners
        self._step = []                 # touches qui viennent d'être pressées
        self._pressed = {}              # touches pressées

        # nouveaux systèmes
        self._any_listeners = []        # listeners globaux (any)
        self._all_listeners = []        # listeners combos (all)
        self._triggered_combos = set()  # combos déjà déclenchés

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur

        Args :
            method (str) : méthode dans laquelle l'erreur survient
            text (str) : message d'erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    # ======================================== METHODES INTERACTIVES ========================================
    @staticmethod
    def get_id(event):
        """
        Abstraction du type d'input en int unique
        
        Args :
            event (pygame.event.Event) : événement en tout genre
            
        Returns :
            int : identifiant unique de l'événement
        """
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            return event.button
        elif event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            return event.key
        else:
            return event.type

    # ======================================== LISTENERS SIMPLES ========================================

    def add_listener(self, event_id: int, callback: callable, args: list=None, kwargs: dict=None,
                     up: bool=False, condition: callable=None, once: bool=False,
                     repeat: bool=False, priority: int=0, give_key: bool=False):
        """
        Ajoute un listener sur une entrée utilisateur
        
        Args :
            event_id (int) : identifiant de l'événement (touche clavier, bouton souris, etc.)
            callback (callable) : fonction à appeler lors du déclenchement
            args (list) : arguments positionnels à passer au callback
            kwargs (dict) : arguments nommés à passer au callback
            up (bool) : si True, déclenche au relâchement ; si False, déclenche à la pression
            condition (callable) : fonction retournant un booléen pour conditionner le déclenchement
            once (bool) : si True, supprime le listener après la première activation
            repeat (bool) : si True, déclenche à chaque frame tant que la touche est maintenue
            priority (int) : priorité d'exécution (plus élevé = exécuté en premier)
            give_key (bool) : si True, passe l'event_id en paramètre 'key' au callback
        """
        if args is None: args = []
        if kwargs is None: kwargs = {}

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
            event_id (int) : identifiant de l'événement
            callback (callable) : fonction callback à supprimer
        """
        if event_id in self._listeners:
            self._listeners[event_id] = [
                l for l in self._listeners[event_id]
                if l["callback"] != callback
            ]
            
            # Nettoyer l'entrée si elle est vide
            if not self._listeners[event_id]:
                del self._listeners[event_id]

    # ======================================== WHEN ANY ========================================

    def when_any(self, callback: callable, exclude: list=None,
                 args: list=None, kwargs: dict=None,
                 once: bool=False, condition: callable=None,
                 priority: int=0, give_key: bool=False):
        """
        Déclenche le callback lorsqu'une touche est pressée,
        sauf celles présentes dans exclude
        
        Args :
            callback (callable) : fonction à appeler lors du déclenchement
            exclude (list) : liste des event_id à exclure
            args (list) : arguments positionnels à passer au callback
            kwargs (dict) : arguments nommés à passer au callback
            once (bool) : si True, supprime le listener après la première activation
            condition (callable) : fonction retournant un booléen pour conditionner le déclenchement
            priority (int) : priorité d'exécution (plus élevé = exécuté en premier)
            give_key (bool) : si True, passe l'event_id en paramètre 'key' au callback
        """
        if exclude is None: exclude = []
        if args is None: args = []
        if kwargs is None: kwargs = {}

        listener = {
            "callback": callback,
            "exclude": set(exclude),
            "args": args,
            "kwargs": kwargs,
            "once": once,
            "condition": condition,
            "priority": priority,
            "give_key": give_key
        }

        for i, l in enumerate(self._any_listeners):
            if priority > l["priority"]:
                self._any_listeners.insert(i, listener)
                return

        self._any_listeners.append(listener)

    # ======================================== WHEN ALL ========================================

    def when_all(self, keys: list, callback: callable,
                 args: list=None, kwargs: dict=None,
                 once: bool=False, condition: callable=None,
                 repeat: bool=False, priority: int=0):
        """
        Déclenche le callback lorsque toutes les touches de la liste sont pressées
        
        Args :
            keys (list) : liste des event_id qui doivent être pressés simultanément
            callback (callable) : fonction à appeler lors du déclenchement
            args (list) : arguments positionnels à passer au callback
            kwargs (dict) : arguments nommés à passer au callback
            once (bool) : si True, supprime le listener après la première activation
            condition (callable) : fonction retournant un booléen pour conditionner le déclenchement
            repeat (bool) : si True, déclenche à chaque frame tant que le combo est maintenu
            priority (int) : priorité d'exécution (plus élevé = exécuté en premier)
        """
        if args is None: args = []
        if kwargs is None: kwargs = {}

        listener = {
            "keys": set(keys),
            "callback": callback,
            "args": args,
            "kwargs": kwargs,
            "once": once,
            "condition": condition,
            "repeat": repeat,
            "priority": priority
        }

        for i, l in enumerate(self._all_listeners):
            if priority > l["priority"]:
                self._all_listeners.insert(i, listener)
                return

        self._all_listeners.append(listener)

    # ======================================== SUPPRESSION GLOBALE ========================================

    def remove_callback(self, callback: callable):
        """
        Supprime un callback de tous les types de listeners
        
        Args :
            callback (callable) : fonction callback à supprimer partout
        """
        # Suppression des listeners simples
        for event_id in list(self._listeners.keys()):
            self._listeners[event_id] = [
                l for l in self._listeners[event_id]
                if l["callback"] != callback
            ]
            
            # Nettoyer l'entrée si elle est vide
            if not self._listeners[event_id]:
                del self._listeners[event_id]

        # Suppression des listeners any
        self._any_listeners = [
            l for l in self._any_listeners
            if l["callback"] != callback
        ]

        # Suppression des listeners all
        self._all_listeners = [
            l for l in self._all_listeners
            if l["callback"] != callback
        ]

    # ======================================== VERIFICATION ========================================

    def check_event(self, event):
        """
        Vérifie les actions associées à l'entrée
        
        Args :
            event (pygame.event.Event) : événement pygame à traiter
        """
        event_id = self.get_id(event)
        down = event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]
        up = event.type in [pygame.MOUSEBUTTONUP, pygame.KEYUP]

        if up:
            self._pressed[event_id] = False
            if event_id in self._step:
                self._step.remove(event_id)
        else:
            self._step.append(event_id)

        # listeners simples
        to_remove = []
        for listener in self._listeners.get(event_id, []):
            if (listener["condition"] and not listener["condition"]()) or up != listener["up"]:
                continue

            if listener["repeat"] and down:
                continue

            if listener["give_key"]:
                listener["callback"](*listener["args"], **listener["kwargs"], key=event_id)
            else:
                listener["callback"](*listener["args"], **listener["kwargs"])

            if listener["once"]:
                to_remove.append(listener)

        for listener in to_remove:
            self._listeners[event_id].remove(listener)
            
        # Nettoyer l'entrée si elle est vide
        if event_id in self._listeners and not self._listeners[event_id]:
            del self._listeners[event_id]

        # WHEN ANY
        if down:
            to_remove = []
            for listener in self._any_listeners:
                if event_id in listener["exclude"]:
                    continue
                if listener["condition"] and not listener["condition"]():
                    continue

                if listener["give_key"]:
                    listener["callback"](*listener["args"], **listener["kwargs"], key=event_id)
                else:
                    listener["callback"](*listener["args"], **listener["kwargs"])

                if listener["once"]:
                    to_remove.append(listener)

            for listener in to_remove:
                self._any_listeners.remove(listener)

    def _is_currently_pressed(self, event_id: int) -> bool:
        """Vérifie si une touche est pressée"""
        return self._pressed.get(event_id, False) or event_id in self._step

    def check_pressed(self):
        """
        Vérifie les listeners de maintien (repeat et combos)
        """
        for event_id, listeners in self._listeners.items():
            if self._is_currently_pressed(event_id):
                for listener in listeners:
                    if listener["repeat"]:
                        if listener["condition"] and not listener["condition"]():
                            continue
                        if listener["give_key"]:
                            listener["callback"](*listener["args"], **listener["kwargs"], key=event_id)
                        else:
                            listener["callback"](*listener["args"], **listener["kwargs"])

        to_remove = []
        for listener in self._all_listeners:
            if not all(self._is_currently_pressed(k) for k in listener["keys"]):
                continue

            if listener["condition"] and not listener["condition"]():
                continue

            combo_key = frozenset(listener["keys"])
            
            if listener["repeat"]:
                listener["callback"](*listener["args"], **listener["kwargs"])
                if listener["once"]:
                    to_remove.append(listener)
            else:
                if combo_key not in self._triggered_combos:
                    listener["callback"](*listener["args"], **listener["kwargs"])
                    self._triggered_combos.add(combo_key)
                    if listener["once"]:
                        to_remove.append(listener)

        active_combos = set()
        for listener in self._all_listeners:
            if all(self._is_currently_pressed(k) for k in listener["keys"]):
                active_combos.add(frozenset(listener["keys"]))
        
        self._triggered_combos = self._triggered_combos & active_combos

        for listener in to_remove:
            self._all_listeners.remove(listener)

        for event_id in self._step:
            self._pressed[event_id] = True

        self._step = []

    def check_all(self):
        """
        Vérifie l'ensemble des listeners et traite tous les événements pygame
        
        Returns :
            bool : True si l'application continue, False si elle doit s'arrêter
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
            event_id (int) : identifiant de l'événement à vérifier
            
        Returns :
            bool : True si la touche/bouton est enfoncé, False sinon
        """
        return self._pressed.get(event_id, False)

# ======================================== INSTANCE ========================================
inputs_manager = InputsManager()