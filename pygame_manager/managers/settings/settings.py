# ======================================== IMPORTS ========================================
from ._panel import SettingsPanel

# ======================================== HELPER ========================================
def _infer_widget_type(value: object, choices: list, min, max) -> str:
    """Infère le type de widget depuis la valeur et les contraintes"""
    if choices: return 'choice'
    if isinstance(value, bool): return 'toggle'
    if isinstance(value, (int, float)) and min is not None and max is not None: return 'slider'
    if isinstance(value, (int, float)): return 'textcase'
    return 'textcase'

# ======================================== GESTIONNAIRE DE PARAMÈTRES ========================================
class SettingsManager:
    """
    Gestionnaire des paramètres

    Fonctionnalités :
        créer des paramètres (avec widget, catégorie, contraintes)
        accéder à des paramètres
        modifier des paramètres
        générer un panel de réglages via settings_manager.Panel(...)
    """
    def __init__(self):
        # Structure interne : {name: {value, widget, category, label, description, min, max, step, choices}}
        self._settings = {}
        self._default_settings = {}
        self._temporary_settings = {}

        # Panel auto-généré
        self.Panel = SettingsPanel

        # Paramètres dynamiques
        self._auto_apply = True

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def __getitem__(self, key: str):
        if key not in self._settings:
            self._raise_error("__getitem__", f"Setting '{key}' does not exist")
        return self._settings[key]['value']

    def __getattr__(self, name: str):
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
        category: str = "General",
        widget: str = None,
        label: str = None,
        description: str = None,
        min: object = None,
        max: object = None,
        step: object = None,
        choices: list = None,
        key_names: dict = None,
    ):
        """
        Création d'un paramètre

        Args :
            name (str) : identifiant unique du paramètre
            value (object) : valeur initiale
            category (str) : catégorie d'appartenance (affiché comme onglet dans le panel)
            widget (str) : type de widget parmi 'toggle', 'choice', 'textcase', 'slider', 'inputbutton'
            label (str) : texte affiché dans le panel (défaut = name)
            description (str) : sous-texte optionnel affiché sous le label
            min (object) : valeur minimale pour slider/textcase numérique
            max (object) : valeur maximale pour slider/textcase numérique
            step (object) : pas d'incrément pour le slider (défaut : 1 pour int, 0.1 pour float)
            choices (list) : liste des choix possibles pour le widget 'choice'
            key_names (dict) : {int: str} noms personnalisés des touches pour 'inputbutton'
        """
        if not isinstance(name, str):
            self._raise_error('create', 'Le nom du paramètre doit être une chaîne')
        if name in self._settings:
            self._raise_error('create', f"Le paramètre '{name}' existe déjà")

        widget_type = widget or _infer_widget_type(value, choices or [], min, max)
        self._settings[name] = {
            'value': value,
            'widget': widget_type,
            'category': category,
            'label': label or name,
            'description': description,
            'min': min,
            'max': max,
            'step': step,
            'choices': choices or [],
            'key_names': key_names or {},
        }

    def remove(self, name: str):
        """Suppression d'un paramètre"""
        if not isinstance(name, str):
            self._raise_error('remove', 'Le nom du paramètre doit être une chaîne')
        if name not in self._settings:
            self._raise_error('remove', f"Le paramètre '{name}' n'existe pas")
        del self._settings[name]

    # ======================================== GETTERS ========================================
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
    
    def get_auto_apply(self) -> bool:
        """Vérifie l'auto-application des paramètres"""
        return self._auto_apply

    # ======================================== SETTERS ========================================
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
    
    def set_auto_apply(self, value: bool):
        """Fixe l'auto-application des paramètres"""
        if not isinstance(value, bool):
            self._raise_error('set_auto_apply', 'Invalid value argument')
        self._auto_apply = value

    # ======================================== METHODES DYNAMIQUES ========================================
    def save_as_default(self):
        """Enregistre les paramètres actuels comme les paramètres par défaut"""
        self._default_settings = self._settings.copy()

    def apply(self):
        """Applique les modifications"""
        self._settings = self._temporary_settings.copy()

# ======================================== INSTANCE ========================================
settings_manager = SettingsManager()