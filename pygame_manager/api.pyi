from typing import List

from .managers.audio import AudioManager
from .managers.data import DataManager
from .managers.geometry import GeometryManager
from .managers.inputs import InputsManager
from .managers.languages import LanguagesManager
from .managers.menus import MenusManager
from .managers.screen import ScreenManager
from .managers.settings import SettingsManager
from .managers.states import StatesManager
from .managers.time import TimeManager
from .managers.ui import UiManager

# === Engine lifecycle ===
def init() -> None: ...
def run() -> None: ...
def stop() -> None: ...

# === Managers ===
audio: AudioManager
data: DataManager
geometry: GeometryManager
inputs: InputsManager
languages: LanguagesManager
menus: MenusManager
screen: ScreenManager
settings: SettingsManager
states: StatesManager
time: TimeManager
ui: UiManager

__all__: List[str]