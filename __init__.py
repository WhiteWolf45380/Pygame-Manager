from managers.audio import AudioGate
from managers.data import DataGate
from managers.time import TimeGate
from managers.languages import LanguagesGate
from managers.screen import ScreenGate

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