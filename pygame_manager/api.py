from pygame_manager.core.engine import PygameEngine

_engine = PygameEngine()

# génération automatique des raccourcis pour tous les managers
globals().update({
    name: getattr(_engine, name) for name in _engine.__dict__ if not name.startswith("_")
})

# ajout des fonctions principales
init = _engine.init
run = _engine.run
stop = _engine.stop

# exports
__all__ = [name for name in _engine.__dict__ if not name.startswith("_")] + ["init", "run", "stop"]
print(__all__)


"""
Syntaxe d'import depuis Git :
pip install git+https://github.com/WhiteWolf45380/pygame_managers.git

Syntaxe d'import depuis GitHub :
pip install https://github.com/WhiteWolf45380/Pygame-Manager/archive/refs/heads/main.zip
"""