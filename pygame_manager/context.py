class Context:
    def __init__(self):
        pass

    def __getattr__(self, name):
        return None