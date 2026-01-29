# ======================================== GESTION DES ERREURS ========================================
def _raise_error(obj: object, method: str, text: str):
    """Lève une erreur"""
    raise RuntimeError(f"[{obj.__class__.__name__}].{method} : {text}")

# ======================================== IMPORTS ========================================
from _core.imports import *

# ======================================== FAMILLES DE TYPES ========================================
Sequence = (tuple, list, np.ndarray)

# ======================================== FONCTIONS UTILES ========================================
def deepcopy(obj: object, memo=None) -> object:
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
        copied = [deepcopy(x, memo) for x in obj]
        memo[obj_id] = copied
        return copied

    if isinstance(obj, tuple):
        copied = tuple(deepcopy(x, memo) for x in obj)
        memo[obj_id] = copied
        return copied

    if isinstance(obj, dict):
        copied = {deepcopy(k, memo): deepcopy(v, memo) for k, v in obj.items()}
        memo[obj_id] = copied
        return copied

    if isinstance(obj, set):
        copied = {deepcopy(x, memo) for x in obj}
        memo[obj_id] = copied
        return copied

    # objets custom
    cls = obj.__class__
    new_obj = cls.__new__(cls)
    memo[obj_id] = new_obj

    # copier les slots
    for slot in getattr(cls, '__slots__', []):
        value = getattr(obj, slot)
        setattr(new_obj, slot, deepcopy(value, memo))

    # copier le dict si présent
    if hasattr(obj, '__dict__'):
        for k, v in obj.__dict__.items():
            setattr(new_obj, k, deepcopy(v, memo))

    return new_obj

# ======================================== EXPORTS ========================================
__all__ = [
    "_raise_error",
    "Sequence",
    "deepcopy",
]