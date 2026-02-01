import os

class Context:
    engine = None

    def __init__(self):
        # chemin vers le dossier managers
        managers_path = os.path.join(os.path.dirname(__file__), "managers")
        
        # lister les fichiers *_manager.py sans les importer
        for filename in os.listdir(managers_path):
            if filename.endswith("_manager.py"):
                # enlever l'extension et le suffixe "_manager"
                attr = filename[:-12].lower()  # "_manager.py" = 12 caractères
                setattr(self, attr, None)

# instance globale
context = Context()
