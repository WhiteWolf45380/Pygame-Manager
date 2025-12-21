import json


class LanguagesManager:
    """
    Gestionnaire de langues / traductions

    Fonctionnalités :
    - chargement de fichiers JSON
    - changement de langue à chaud
    - récupération de traductions avec variables
    """

    def __init__(self, default_lang: str = "en"):
        self.__name = "LanguagesManager"
        self.__lang = default_lang
        self.__translations = {}

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__name}].{method} : {text}")

    # ======================================== LANGUES ========================================
    def load_language(self, lang: str, path: str):
        """
        Charge un fichier de traduction JSON

        Args:
            - lang (str) : code de langue (ex: "en", "fr")
            - path (str) : chemin du fichier JSON
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.__translations[lang] = json.load(f)
        except Exception:
            self._raise_error("load_language", f"Cannot load language file {path}")

    def set_language(self, lang: str):
        """
        Change la langue active
        """
        if lang not in self.__translations:
            self._raise_error("set_language", f"Language '{lang}' not loaded")
        self.__lang = lang

    def get_language(self) -> str:
        """
        Renvoie la langue actuelle
        """
        return self.__lang

    # ======================================== TRADUCTION ========================================
    def t(self, key: str, **kwargs) -> str:
        """
        Traduit une clé

        Args:
            - key (str) : clé de traduction
            - kwargs : variables de formatage
        """
        text = self.__translations.get(self.__lang, {}).get(key)

        if text is None:
            return f"[{key}]"

        try:
            return text.format(**kwargs)
        except KeyError as e:
            return f"[Missing var '{e.args[0]}' in '{key}']"
        

"""
Exemple de fichier JSON :

{
    "menu.play": "Play",
    "menu.quit": "Quit",
    "game.score": "Score: {score}"
}
"""

"""
Exemple d'utilisation :

    lang = LanguagesManager()

    lang.load_language("en", "en.json")
    lang.load_language("fr", "fr.json")

    lang.set_language("en")

    title = lang.t("menu.play")
    score_text = lang.t("game.score", score=120)

"""