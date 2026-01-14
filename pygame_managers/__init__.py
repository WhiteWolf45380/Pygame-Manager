from .audio import AudioGate
from .data import DataGate
from .time import TimeGate
from .languages import LanguagesGate
from .screen import ScreenGate

audio = AudioGate()
data = DataGate()
time = TimeGate()
languages = LanguagesGate()
screen = ScreenGate()

__all__ = ["audio", "data", "time", "languages", "screen"]


"""
Syntaxe d'import depuis GitHub :
pip install git+https://github.com/WhiteWolf45380/pygame_managers.git
"""