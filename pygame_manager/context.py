import sys
from pathlib import Path

class Context:
    def __init__(self):
        self.engine = None
        managers_dir = Path(__file__).parent / "managers"
        for p in managers_dir.iterdir():
            if p.is_dir() and not p.name.startswith("_") and (p / "__init__.py").exists():
                setattr(self, p.name, None)

    def __getattr__(self, name):
        raise AttributeError(f"context has no attribute {name!r}")

sys.modules[__name__] = Context()