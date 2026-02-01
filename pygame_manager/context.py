from pathlib import Path

managers_dir = Path(__file__).parent / "managers"

engine = None
__all__ = ["engine"]

for p in managers_dir.iterdir():
    if (p.is_dir() and not p.name.startswith("_") and (p / "__init__.py").exists()):
        globals()[p.name] = None
        __all__.append(p.name)

def __getattr__(name):
    raise AttributeError(f"context has no attribute {name!r}")