import json
from pathlib import Path
from typing import Optional


# ======================================== GESTIONNAIRE ========================================
class LanguagesManager:
    """
    Gestionnaire de langues / traductions

    Fonctionnalités :
    - chargement de fichiers JSON
    - changement de langue à chaud
    - récupération de traductions avec variables
    """

    def __init__(self, default_lang: str = "en", fallback_lang: str="en"):
        self.__lang = default_lang
        self.__fallback_lang = fallback_lang        # langue de secours
        self.__translations = {}

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

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
    
    def load_directory(self, directory: str, pattern: str = "{lang}.json"):
        """
        Charge toutes les langues d'un dossier
        
        Args:
            - directory (str) : dossier contenant les fichiers
            - pattern (str) : format des fichiers (ex: "lang_{lang}.json")
        """
        folder = Path(directory)
        
        if not folder.exists():
            self._raise_error("load_directory", f"Directory not found: {directory}")
        
        for file in folder.glob("*.json"):
            lang_code = file.stem
            if "{lang}" in pattern:
                prefix = pattern.split("{lang}")[0]
                if file.name.startswith(prefix):
                    lang_code = file.stem.replace(prefix, "")
            self.load_language(lang_code, str(file))

    def set_language(self, lang: str, fallback: bool = True):
        """
        Change la langue active
        
        Args:
            - lang (str) : code de langue
            - fallback (bool) : utiliser la langue de secours si non trouvée
        """
        if lang not in self.__translations:
            if fallback and self.__fallback_lang in self.__translations:
                print(f"Warning: Language '{lang}' not found, using fallback '{self.__fallback_lang}'")
                self.__lang = self.__fallback_lang
            else:
                self._raise_error("set_language", f"Language '{lang}' not loaded")
        else:
            self.__lang = lang

    def get_language(self) -> str:
        """
        Renvoie la langue actuelle
        """
        return self.__lang
    
    def get_available_languages(self) -> list[str]:
        """Envoie la liste des langues chargées"""
        return list(self.__translations.keys())

    # ======================================== TRADUCTION ========================================
    def __call__(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """
        Traduit une clé
        
        Args:
            - key (str) : clé de traduction
            - lang (str) : langue spécifique (None = langue actuelle)
            - kwargs : variables de formatage
        """
        target_lang = lang or self.__lang
        
        # recherche dans la langue cible
        text = self.__translations.get(target_lang, {}).get(key)
        
        # fallback sur la langue de secours
        if text is None and target_lang != self.__fallback_lang:
            text = self.__translations.get(self.__fallback_lang, {}).get(key)
        
        # clé manquante
        if text is None:
            return f"[{key}]"
        
        # formatage
        try:
            return text.format(**kwargs)
        except KeyError as e:
            return f"[Missing var '{e.args[0]}' in '{key}']"
        except Exception as e:
            return f"[Format error in '{key}': {e}]"
        

"""
Exemple d'utilisation :

from languages_manager import LanguagesManager

# Initialisation avec langue par défaut et fallback
lang = LanguagesManager(default_lang="fr", fallback_lang="en")

# Charger des langues manuellement
lang.load_language("en", "languages/en.json")
lang.load_language("fr", "languages/fr.json")
lang.load_language("es", "languages/es.json")

# Ou charger tout un dossier automatiquement
lang.load_directory("languages")  # Charge en.json, fr.json, es.json...

# Changer de langue
lang.set_language("fr")
print(f"Langue active: {lang.get_language()}")

# Afficher les langues disponibles
print(f"Langues chargées: {lang.get_available_languages()}")

# Traductions simples
title = lang("menu.title")
play_button = lang("menu.play")
quit_button = lang("menu.quit")

# Traductions avec variables
score_text = lang("game.score", score=1250)
lives_text = lang("game.lives", count=3)
welcome = lang("game.welcome", player_name="Alice")

# Forcer une langue spécifique
english_title = lang("menu.title", lang="en")

# Utilisation dans une boucle de jeu
while running:
    # ...
    if button_clicked:
        message = lang("game.paused")
        resume_text = lang("menu.resume")
    
    # Afficher du texte avec variables dynamiques
    timer_text = lang("game.timer", seconds=int(remaining_time))
    health_text = lang("game.health", current=player_health, max=100)

# Si une clé n'existe pas, affiche [key_name]
missing = lang("non.existent.key")  # Affiche: [non.existent.key]

# Si une variable manque, affiche l'erreur
error = lang("game.score")  # Affiche: [Missing var 'score' in 'game.score']
"""

"""
Exemple de fichier JSON (en.json) :

{
    "menu.title": "My Game",
    "menu.play": "Play",
    "menu.quit": "Quit",
    "menu.resume": "Resume",
    "game.score": "Score: {score}",
    "game.lives": "Lives: {count}",
    "game.health": "Health: {current}/{max}",
    "game.welcome": "Welcome, {player_name}!",
    "game.paused": "Game Paused",
    "game.timer": "Time: {seconds}s"
}
"""

"""
Exemple de fichier JSON (fr.json) :

{
    "menu.title": "Mon Jeu",
    "menu.play": "Jouer",
    "menu.quit": "Quitter",
    "menu.resume": "Reprendre",
    "game.score": "Score : {score}",
    "game.lives": "Vies : {count}",
    "game.health": "Santé : {current}/{max}",
    "game.welcome": "Bienvenue, {player_name} !",
    "game.paused": "Jeu en Pause",
    "game.timer": "Temps : {seconds}s"
}
"""