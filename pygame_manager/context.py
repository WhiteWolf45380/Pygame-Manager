import sys
from pathlib import Path

class Context:
    def __init__(self):
        self.engine = None

        if getattr(sys, "_MEIPASS", None):
            managers_dir = Path(sys._MEIPASS) / "pygame_manager" / "managers"
        else:
            managers_dir = Path(__file__).parent / "managers"

        if managers_dir.exists():
            for p in managers_dir.iterdir():
                if p.is_dir() and not p.name.startswith("_") and (p / "__init__.py").exists():
                    setattr(self, p.name, None)
        else:
            print(f"Warning: managers_dir {managers_dir} does not exist.")

    def __getattr__(self, name):
        raise AttributeError(f"context has no attribute {name!r}")