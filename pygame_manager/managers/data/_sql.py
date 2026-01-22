import sqlite3
from pathlib import Path


class SQLHandler:
    """
    Gestionnaire SQL

    Fonctionnalités : 
        - manipulation de Bases De Données
        - envoie de requêtes SQL
    """
    def __init__(self):
        self.__path = None
        self.__conn = None
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close(save=exc is None)

    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str, text: str):
        """
        Lève une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")

    def connect(self, path: str):
        """
        Initialise la connexion avec la base de données
        """
        if self.__conn is not None:
            self._raise_error('connect', 'Already connected.\nPls end the connection first with sql.close()')

        self.__path = Path(path)
        self.__path.parent.mkdir(parents=True, exist_ok=True)
        
        self.__conn = sqlite3.connect(self.__path)
        self.__conn.row_factory = sqlite3.Row

    def execute(self, sql, params=()):
        """
        Exécute une requête SQL avec paramètres

        Args:
            sql (str): Requête SQL à exécuter
            params (tuple): Paramètres associés à la requête
        """
        if self.__conn is None:
            self._raise_error('excecute', 'Not connected to DataBase.\nTry to start a connection with sql.connect(path)')
        cursor = self.__conn.cursor()
        cursor.execute(sql, params)
        return cursor
    
    def fetchall(self, sql, params=()):
        """
        Exécute une requête SQL et retourne toutes les lignes résultantes

        Args:
            sql (str): Requête SQL SELECT
            params (tuple): Paramètres associés à la requête
        """
        if self.__conn is None:
            self._raise_error('fetchall', 'Not connected to DataBase.\nTry to start a connection with sql.connect(path)')
        cursor = self.execute(sql, params)
        return cursor.fetchall()

    def fetchone(self, sql, params=()):
        """
        Exécute une requête SQL et retourne une seule ligne

        Args:
            sql (str): Requête SQL SELECT
            params (tuple): Paramètres associés à la requête
        """
        if self.__conn is None:
            self._raise_error('fetchone', 'Not connected to DataBase.\nTry to start a connection with sql.connect(path)')
        cursor = self.execute(sql, params)
        return cursor.fetchone()

    def commit(self):
        """
        Sauvegarde les modifications transitionnelles
        """
        if self.__conn:
            self.__conn.commit()

    def close(self, save: bool=True):
        """
        Met fin à la connexion avec la base de données
        """
        if save:
            self.commit()
        if self.__conn:
            self.__conn.close()
            self.__conn = None

"""
Exemple d'utilisation

sql = SQLHandler()
sql.connect("data/test.db")

sql.execute("
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER
)
")

sql.execute(
    "INSERT INTO users (name, age) VALUES (?, ?)",
    ("Alice", 25)
)

sql.commit()

user = sql.fetchone(
    "SELECT * FROM users WHERE name = ?",
    ("Alice",)
)

print(dict(user))

sql.close()

"""