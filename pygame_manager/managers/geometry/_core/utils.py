# ======================================== GESTION DES ERREURS ========================================
def _raise_error(obj: object, method: str, text: str):
        """Lève une erreur"""
        raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

# ======================================== IMPORTS PARTIELLES ========================================
from _core.imports import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list, np.ndarray)

# ======================================== EXPORTS ========================================
__all__ = [
    "_raise_error",
    "Sequence",
]