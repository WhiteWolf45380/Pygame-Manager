# ======================================== IMPORTS ========================================
from ._panel import SettingsPanel

# ======================================== HELPER ========================================
def _infer_type(value: object, choices: list) -> str:
    """Infère le type d'un paramètre depuis sa valeur"""
    if choices:        return 'choice'
    if isinstance(value, bool): return 'bool'   # bool avant int !
    if isinstance(value, int):  return 'int'
    if isinstance(value, float):return 'float'
    return 'str'

# ======================================== GESTIONNAIRE DE PARAMÈTRES ========================================
class SettingsManager:
    """
    Gestionnaire des paramètres

    Fonctionnalités :
        créer des paramètres (avec type, catégorie, contraintes)
        accéder à des paramètres
        modifier des paramètres
        générer un panel de réglages via settings_manager.Panel(...)
    """
    def __init__(self):
        # Structure interne : {name: {value, type, category, label, description, min, max, choices}}
        self._settings = {}

        # Panel auto-généré
        self.Panel = SettingsPanel

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def __getitem__(self, key: str):
        if key not in self._settings:
            self._raise_error("__getitem__", f"Setting '{key}' does not exist")
        return self._settings[key]['value']

    def __getattr__(self, name: str):
        # Éviter la récursion sur les attributs privés/spéciaux
        if name.startswith('_'):
            raise AttributeError(name)
        try:
            return self._settings[name]['value']
        except KeyError:
            raise AttributeError(name)

    def __contains__(self, name: str) -> bool:
        return name in self._settings

    def __repr__(self) -> str:
        return f"<SettingsManager: {len(self._settings)} paramètre(s)>"

    # ======================================== CREATION / SUPPRESSION ========================================
    def create(
        self,
        name: str,
        value: object,
        *,
        category: str = "General",
        type: str = None,
        label: str = None,
        description: str = None,
        min: object = None,
        max: object = None,
        choices: list = None,
    ):
        """
        Création d'un paramètre

        Args :
            name (str)          : identifiant unique du paramètre
            value (object)      : valeur initiale
            category (str)      : catégorie d'appartenance (affiché comme onglet dans le panel)
            type (str)          : type forcé parmi 'bool', 'int', 'float', 'str', 'choice'
                                  (inféré automatiquement si None)
            label (str)         : texte affiché dans le panel (défaut = name)
            description (str)   : sous-texte optionnel affiché sous le label
            min (object)        : valeur minimale pour int/float
            max (object)        : valeur maximale pour int/float
            choices (list)      : liste des choix possibles (force type='choice')
        """
        if not isinstance(name, str):
            self._raise_error('create', 'Le nom du paramètre doit être une chaîne')
        if name in self._settings:
            self._raise_error('create', f"Le paramètre '{name}' existe déjà")

        inferred_type = type or _infer_type(value, choices or [])

        self._settings[name] = {
            'value':       value,
            'type':        inferred_type,
            'category':    category,
            'label':       label or name,
            'description': description,
            'min':         min,
            'max':         max,
            'choices':     choices or [],
        }

    def remove(self, name: str):
        """Suppression d'un paramètre"""
        if not isinstance(name, str):
            self._raise_error('remove', 'Le nom du paramètre doit être une chaîne')
        if name not in self._settings:
            self._raise_error('remove', f"Le paramètre '{name}' n'existe pas")
        del self._settings[name]

    # ======================================== ACCÈS ========================================
    def get(self, name: str, fallback: object = None) -> object:
        """
        Renvoie la valeur d'un paramètre

        Args :
            name (str)       : nom du paramètre
            fallback (object): valeur de repli si le paramètre est introuvable
        """
        if name not in self._settings:
            return fallback
        return self._settings[name]['value']

    def get_item(self, name: str, index: int, fallback: object = None) -> object:
        """
        Renvoie un élément d'un paramètre de type liste

        Args :
            name (str)       : nom du paramètre
            index (int)      : indice dans la liste
            fallback (object): valeur de repli
        """
        if name not in self._settings:
            return fallback
        val = self._settings[name]['value']
        if not isinstance(val, (list, tuple)) or index >= len(val):
            return fallback
        return val[index]

    def get_meta(self, name: str) -> dict | None:
        """Renvoie l'entrée complète (valeur + métadonnées) d'un paramètre"""
        return self._settings.get(name)

    # ======================================== MODIFICATION ========================================
    def set(self, name: str, value: object, index: int = -1, f: bool = False):
        """
        Modification d'un paramètre

        Args :
            name (str)    : nom du paramètre
            value (object): nouvelle valeur
            index (int)   : indice dans un paramètre de type list (-1 = remplace tout)
            f (bool)      : force la création si le paramètre n'existe pas
        """
        if not isinstance(name, str):
            self._raise_error('set', 'Le nom du paramètre doit être une chaîne')
        if name not in self._settings:
            if not f:
                self._raise_error('set', f"Le paramètre '{name}' n'existe pas\n"
                                         "Utilisez create(name, value) ou passez f=True")
            self.create(name, value)
            return

        entry = self._settings[name]
        if index != -1 and isinstance(entry['value'], list):
            entry['value'][index] = value
        else:
            entry['value'] = value

# ======================================== INSTANCE ========================================
settings_manager = SettingsManager()