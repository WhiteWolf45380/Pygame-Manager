from .managers.audio import AudioManager
from .managers.data import DataManager
from .managers.inputs import InputsManager
from .managers.languages import LanguagesManager
from .managers.screen import ScreenManager
from .managers.settings import SettingsManager
from .managers.menus import MenusManager
from .managers.time import TimeManager
from .managers.geometry import GeometryManager
from .managers.ui import UiManager
from typing import List

# === Engine lifecycle ===
def init() -> None: ...
def run() -> None: ...
def stop() -> None: ...

# === Managers ===
audio: AudioManager
data: DataManager
inputs: InputsManager
languages: LanguagesManager
screen: ScreenManager
settings: SettingsManager
manus: MenusManager
time: TimeManager
geometry: GeometryManager
ui: UiManager

__all__: List[str]