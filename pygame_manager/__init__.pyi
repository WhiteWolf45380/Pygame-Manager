"""API publique du framework pygame_manager"""

from typing import List
from . import types

# ========================================== ENGINE LIFECYCLE ==========================================
def init() -> None:
    """Initialise le moteur"""
    from .core.engine import init as _init
    _init()

def run() -> None:
    """Lance la boucle principale"""
    from .core.engine import run as _run
    _run()

def stop() -> None:
    """Arrête le moteur"""
    from .core.engine import stop as _stop
    _stop()

# ========================================== MANAGERS ==========================================
from .managers.audio import AudioManager
from .managers.data import DataManager
from .managers.entities import EntitiesManager
from .managers.geometry import GeometryManager
from .managers.inputs import InputsManager
from .managers.languages import LanguagesManager
from .managers.mouse import MouseManager
from .managers.network import NetworkManager
from .managers.panels import PanelsManager
from .managers.screen import ScreenManager
from .managers.settings import SettingsManager
from .managers.states import StatesManager
from .managers.time import TimeManager
from .managers.ui import UiManager

# ========================================== MANAGERS INSTANCES ==========================================
audio = AudioManager()
data = DataManager()
entities = EntitiesManager()
geometry = GeometryManager()
inputs = InputsManager()
languages = LanguagesManager()
mouse = MouseManager()
network = NetworkManager()
panels = PanelsManager()
screen = ScreenManager()
settings = SettingsManager()
states = StatesManager()
time = TimeManager()
ui = UiManager()

# ========================================== EXPOSITION ==========================================
__all__: List[str] = [
    # Lifecycle
    "init",
    "run",
    "stop",
    
    # Managers
    "audio",
    "data",
    "entities",
    "geometry",
    "inputs",
    "languages",
    "mouse",
    "network",
    "panels",
    "screen",
    "settings",
    "states",
    "time",
    "ui",

    # Types
    "types",
]