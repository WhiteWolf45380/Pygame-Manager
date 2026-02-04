# ======================================== IMPORTS ========================================
from .imports import *
from typing import Protocol, TYPE_CHECKING

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list, dict, set, np.ndarray)

class Reshapable(Protocol):
    @property
    def dim(self) -> int:
        """Renvoie la dimension de l'objet"""
        ...

    def reshape(self, dim: int) -> None:
        """Redimensionne l'objet"""
        ...

# ======================================== FONCTIONS UTILES ========================================
def _raise_error(obj: object, method: str, text: str):
    """Lève une erreur"""
    raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

def _deepcopy(obj: object, memo=None) -> object:
    """
    Renvoie une copie profonde de l'objet

    Args:
        obj: l'objet à copier
        memo: dictionnaire pour gérer les références déjà copiées (prévenir les cycles)
    """
    if memo is None:
        memo = {}

    obj_id = id(obj)
    if obj_id in memo:
        return memo[obj_id]

    # types immuables
    if isinstance(obj, (int, float, str, bool, type(None))):
        return obj

    # built-ins mutables
    if isinstance(obj, list):
        copied = [_deepcopy(x, memo) for x in obj]
        memo[obj_id] = copied
        return copied

    if isinstance(obj, tuple):
        copied = tuple(_deepcopy(x, memo) for x in obj)
        memo[obj_id] = copied
        return copied

    if isinstance(obj, dict):
        copied = {_deepcopy(k, memo): _deepcopy(v, memo) for k, v in obj.items()}
        memo[obj_id] = copied
        return copied

    if isinstance(obj, set):
        copied = {_deepcopy(x, memo) for x in obj}
        memo[obj_id] = copied
        return copied

    # objets custom
    cls = obj.__class__
    new_obj = cls.__new__(cls)
    memo[obj_id] = new_obj

    # copier les slots
    for slot in getattr(cls, '__slots__', []):
        value = getattr(obj, slot)
        setattr(new_obj, slot, _deepcopy(value, memo))

    # copier le dict si présent
    if hasattr(obj, '__dict__'):
        for k, v in obj.__dict__.items():
            setattr(new_obj, k, _deepcopy(v, memo))

    return new_obj

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
    "Reshapable",
    "_raise_error",
    "_deepcopy",
    "_to_color"
]