import sys

class Context:
    def __init__(self):
        pass

sys.modules[__name__] = Context()
def __getattr__(self, name):
    raise AttributeError(f"context has no attribute {name!r}")