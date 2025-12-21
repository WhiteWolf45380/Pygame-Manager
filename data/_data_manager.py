import json


class DataManager:
    """
    Gestionnaire de données

    Fonctionnalités :
    - chargement et sauvegarde de fichiers JSON
    - gestion de plusieurs fichiers de données
    - accès simple aux valeurs (get / set)
    """

    def __init__(self):
        self.__name = "DataManager"

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        raise RuntimeError(f"[{self.__name}].{method} : {text}")

    # ======================================== FICHIERS ========================================
    def load(self, path: str) -> dict:
        """
        Charge un fichier JSON en mémoire

        Args:
            - path (str) : chemin d'accès au fichier
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self._raise_error("load", f"Cannot load file at {path}")

    def save(self, datas: dict, path: str):
        """
        Sauvegarde un fichier JSON sur le disque

        Args:
            - datas (dict) : données à stocker
            - path (str) : chemin d'accès au fichier
        """
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(datas, f, indent=4)
        except Exception as e:
            self._raise_error("load", f"Cannot save file at {path}")


"""
Exemple d'utilisation :

data = DataManager()

# charger un fichier de configuration
config = data.load("config.json")

# modifier des valeurs
config["volume"] = 0.8
config["fullscreen"] = True

# sauvegarder les changements
data.save(config, "config.json")

# créer une sauvegarde de jeu
save = {
    "level": 3,
    "score": 1250,
    "player_position": [120, 340]
}

data.save(save, "save_1.json")

# recharger une sauvegarde existante
save = data.load("save_1.json")
"""