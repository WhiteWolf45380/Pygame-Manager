from pygame_manager.managers.audio import AudioManager
from pygame_manager.managers.data import DataManager
from pygame_manager.managers.inputs import InputsManager
from pygame_manager.managers.languages import LanguagesManager
from pygame_manager.managers.screen import ScreenManager
from pygame_manager.managers.settings import SettingsManager
from pygame_manager.managers.states import StatesManager
from pygame_manager.managers.time import TimeManager
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
states: StatesManager
time: TimeManager

__all__: List[str]