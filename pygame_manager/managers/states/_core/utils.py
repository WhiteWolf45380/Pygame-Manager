# ======================================== IMPORTS ========================================
from .imports import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list)

# ======================================== FONCTIONS UTILES ========================================
def _raise_error(obj: object, method: str, text: str):
    """Lève une erreur"""
    raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

# ======================================== EXPORTS ========================================
__all__ = [
    "Sequence",
    "_raise_error",
]