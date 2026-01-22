import importlib
import pkgutil
import sys

__all__ = []

package = sys.modules[__name__]

# import automatique des modules dans le dossier
for _, module_name, _ in pkgutil.iter_modules(package.__path__):
    module = importlib.import_module(f"{__name__}.{module_name}")
    # récupération des classes finissant par "Manager"
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if attr_name.endswith("_manager"):
            globals()[attr_name] = attr
            __all__.append(attr_name)
