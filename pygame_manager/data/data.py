import json
from pathlib import Path
import os
from ._sql import SQLHandler


# ======================================== PORTAIL ========================================
class DataGate:
    """
    Portail d'accès au gestionnaire de données
    """
    def __init__(self):
        self.__data = DataManager()
    
    def __getattr__(self, name):
        return getattr(self.__data, name)


# ======================================== GESTIONNAIRE ========================================
class DataManager:
    """
    Gestionnaire de données

    Fonctionnalités :
    - chargement et sauvegarde de fichiers JSON
    - gestion de plusieurs fichiers de données
    - accès simple aux valeurs (get / set)
    """
    def __init__(self, base_path: str="data"):
        if not isinstance(base_path, str):
            self._raise_error('__init__', 'base_path must be a string')
        self.__base_path = Path(base_path)
        self.__sql = SQLHandler()

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    def _resolve_path(self, path: str) -> Path:
        """Résout un chemin relatif au base_path"""
        if os.path.isabs(path):
            return Path(path)
        return self.__base_path / path
    
    # ======================================== GETTERS ========================================
    @property
    def sql(self):
        """
        Accès au gestionnaire SQL
        """
        return self.__sql

    # ======================================== FICHIERS ========================================
    def load(self, path: str) -> dict:
        """
        Charge un fichier JSON en mémoire

        Args:
            - path (str) : chemin d'accès au fichier
        """
        if not isinstance(path, str):
            self._raise_error('load', 'path must be a string')
        full_path = self._resolve_path(path)
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            self._raise_error("load", f"File not found: {full_path}")
        except json.JSONDecodeError as e:
            self._raise_error("load", f"Invalid JSON in {full_path}: {e}")
        except Exception as e:
            self._raise_error("load", f"Cannot load file {full_path}: {e}")

    def save(self, data: dict, path: str, create_dirs: bool=True, indent: int=4):
        """
        Sauvegarde un fichier JSON sur le disque

        Args:
            - data (dict) : données à stocker
            - path (str) : chemin d'accès au fichier
            - create_dirs (bool) : création ou non des fichiers parents
            - indent (int) : indentation du JSON
        """
        if not isinstance(path, str):
            self._raise_error('save', 'path must be a string')
        full_path = self._resolve_path(path)
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # Sauvegarde temporaire pour éviter corruption
            temp_path = full_path.with_suffix('.tmp')
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            # Remplacer l'ancien fichier
            temp_path.replace(full_path)
        except Exception as e:
            self._raise_error("save", f"Cannot save file {full_path}: {e}")
    
    def exists(self, path: str) -> bool:
        """Vérifie si un fichier existe"""
        if not isinstance(path, str):
            self._raise_error('exists', 'path must be a string')
        return self._resolve_path(path).exists()
    
    def delete(self, path: str):
        """Supprime un fichier"""
        if not isinstance(path, str):
            self._raise_error('delete', 'path must be a string')
        full_path = self._resolve_path(path)
        if full_path.exists():
            full_path.unlink()
    
    def get(self, path: str, key: str, default: object = None) -> object:
        """
        Récupère une valeur spécifique dans un fichier
        
        Args:
            - path (str) : chemin du fichier
            - key (str) : clé à récupérer (supporte "parent.child.value")
            - default (object) : valeur par défaut si non trouvée
        """
        if not isinstance(path, str):
            self._raise_error('get', 'path must be a string')
        if not isinstance(key, str):
            self._raise_error('get', 'key must be a string')

        data = self.load(path)
        keys = key.split('.')
        
        for k in keys:
            if isinstance(data, dict) and k in data:
                data = data[k]
            else:
                return default
        
        return data
    
    def set(self, path: str, key: str, value: object):
        """
        Définit une valeur dans un fichier
        
        Args:
            - path (str) : chemin du fichier
            - key (str) : clé (supporte "parent.child.value")
            - value (object) : nouvelle valeur
        """
        if not isinstance(path, str):
            self._raise_error('set', 'path must be a string')
        if not isinstance(key, str):
            self._raise_error('set', 'key must be a string')

        data = self.load(path) if self.exists(path) else {}
        keys = key.split('.')
        
        current = data
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        self.save(data, path)
    
    def list_files(self, pattern: str = "*.json") -> list[str]:
        """Liste les fichiers correspondant au pattern"""
        if not isinstance(pattern, str):
            self._raise_error('list_files', 'path must be a string')
        return [str(p.relative_to(self.__base_path)) for p in self.__base_path.glob(pattern)]


"""
Exemple d'utilisation :

from data_manager import DataManager

# Initialisation avec dossier de base
data = DataManager(base_path="game_data")

# Charger un fichier de configuration
config = data.load("config.json")
print(config["volume"])

# Modifier et sauvegarder
config["volume"] = 0.8
config["fullscreen"] = True
data.save(config, "config.json")

# Utiliser get/set pour accès rapide
# Notation pointée supportée
volume = data.get("config.json", "audio.volume", default=1.0)
data.set("config.json", "audio.volume", 0.7)
data.set("config.json", "graphics.resolution.width", 1920)

# Créer une sauvegarde de jeu
save_data = {
    "level": 3,
    "score": 1250,
    "player": {
        "position": [120, 340],
        "health": 100,
        "inventory": ["sword", "potion"]
    }
}
data.save(save_data, "saves/save_1.json", create_dirs=True)

# Charger une sauvegarde
save = data.load("saves/save_1.json")
player_health = data.get("saves/save_1.json", "player.health")

# Vérifier existence
if data.exists("saves/save_2.json"):
    save2 = data.load("saves/save_2.json")

# Lister les sauvegardes
saves = data.list_files("saves/*.json")
print(f"Sauvegardes disponibles: {saves}")

# Supprimer une sauvegarde
data.delete("saves/old_save.json")

# Utiliser des chemins absolus
data.save(config, "/tmp/backup_config.json")
"""