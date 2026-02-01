from pathlib import Path

class Context:
    def __init__(self):
        self.engine = None

        managers_dir = Path(__file__).parent / "managers"
        for p in managers_dir.iterdir():
            if (p.is_dir() and not p.name.startswith("_") and (p / "__init__.py").exists()):
                setattr(self, p.name, None)

context = Context()
__all__ = [context.__dict__.keys()]