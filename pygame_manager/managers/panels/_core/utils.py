# ======================================== IMPORTS ========================================
from .imports import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list)

# ======================================== FONCTIONS UTILES ========================================
def _raise_error(obj: object, method: str, text: str):
    """Lève une erreur"""
    raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

def _to_color(color: pygame.Color | Iterable[int], fallback: object=None, raised: bool=None, method: str='_to_color', message: str='Invalid color argument') -> pygame.Color:
    """Transforme en couleur pygame si besoin l'est"""
    if isinstance(color, pygame.Color):
        return color
    elif isinstance(color, Sequence) and len(color) in (3, 4) and all(isinstance(c, int) and 0 <= c <= 255 for c in color):
        return pygame.Color(color)
    return fallback if fallback is not None else _raise_error(pygame.Color, method, message) if raised else None

# ======================================== EXPORTS ========================================
__all__ = [
    "Sequence",
    "_raise_error",
    "_to_color",
]