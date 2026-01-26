class SettingsManager:
    """
    Gestionnaire des paramètres

    Fonctionnalités :
        créer des paramètres
        accéder à des paramètres
        modifier des paramètres
    """
    def __init__(self):
        self.__settings = {}

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def __getitem__(self, key):
        if key not in self.__settings:
            self._raise_error("__getitem__", f"Setting {key} does not exist")
        return self.__settings[key]
    
    def __getattr__(self, name):
        try:
            return self.__settings[name]
        except KeyError:
            raise AttributeError(name)
    
    # ======================================== METHODES INTERACTIVES ========================================
    def create(self, name: str, value: object):
        """
        Création d'un paramètre

        Args :
            name (str) : nom du paramètre
            value (object) : valeur du paramètre
        """
        if not isinstance(name, str):
            self._raise_error('create', 'Setting name must be a string object')
        if name in self.__settings:
            self._raise_error('create', f'Setting {name} already exists')
        self.__settings[name] = value

    def get(self, name: str, fallback: object=None):
        """
        Renvoie la valeur d'un paramètre

        Args :
            name (str) : nom du paramètre
            fallback (object) : renvoie si le paramètre n'est pas trouvé
        """
        if name not in self.__settings:
            return fallback
        return self.__settings[name]
    
    def get_item(self, name: str, index: int, fallback: object=None):
        """
        Renvoie la valeur d'un paramètre

        Args :
            name (str) : nom du paramètre
            index (int) : indice dans la paramètre de type liste
            fallback (object) : renvoie si le paramètre n'est pas trouvé
        """
        if name not in self.__settings or index >= len(self.__settings[name]):
            return fallback
        return self.__settings[name][index]
    
    def set(self, name: str, value: object, index: int=-1, f: bool=False):
        """
        Modification d'un paramètre

        Args :
            name (str) : nom du paramètre
            value (object) : valeur du paramètre
            index (int) : indice dans un paramètre de type list
            f (bool) : forcer la création  du paramètre si nécessaire
        """
        if not isinstance(name, str):
            self._raise_error('create', 'Setting name must be a string object')
        if name not in self.__settings:
            if not f:
                self._raise_error('set', f'Setting {name} does not exist\nTry to create it with create(name, value)')
            self.create(name, value)

        if index == -1 or not isinstance(self.__settings[name], list):
            self.__settings[name] = value
        else:
            self.__settings[name][index] = value
    
    def remove(self, name: str):
        """
        Suppression d'un paramètre
        """
        if not isinstance(name, str):
            self._raise_error('create', 'Setting name must be a string object')
        if name not in self.__settings:
            self._raise_error('remove', f'Setting {name} doest not exist')
        del self.__settings[name]


# ======================================== INSTANCE ========================================
settings_manager = SettingsManager()