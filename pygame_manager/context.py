from pygame_manager import managers

class Context:
    engine = None
    def __init__(self):
        for name in managers.__all__:
            if name.endswith("_manager"):
                attr = name[:-8].lower()
                setattr(self, attr, None)

context = Context()