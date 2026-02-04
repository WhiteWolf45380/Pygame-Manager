# ========================================== ENTITIES ==========================================
from .managers.entities import Entity, SegmentEntity, LineEntity, CircleEntity, RectEntity, PolygonEntity

# ========================================== OBJECTS ==========================================
from .managers.geometry import VectorObject, PointObject, SegmentObject, LineObject, CircleObject, RectObject, PolygonObject

# ========================================== PANELS ==========================================
from .managers.panels import Panel

# ========================================== STATES ==========================================
from .managers.states import State

# ========================================== UI ==========================================
from .managers.ui import RectButtonObject, CircleButtonObject, RectSelectorObject, CircleSelectorObject, TextCaseObject

# ========================================== NAMESPACE ==========================================
class type:
    Entity: type[Entity]
    SegmentEntity: type[SegmentEntity]
    LineEntity: type[LineEntity]
    CircleEntity: type[CircleEntity]
    RectEntity: type[RectEntity]
    PolygonEntity: type[PolygonEntity]
    VectorObject: type[VectorObject]
    PointObject: type[PointObject]
    SegmentObject: type[SegmentObject]
    LineObject: type[LineObject]
    CircleObject: type[CircleObject]
    RectObject: type[RectObject]
    PolygonObject: type[PolygonObject]
    Panel: type[Panel]
    State: type[State]
    RectButtonObject: type[RectButtonObject]
    CircleButtonObject: type[CircleButtonObject]
    RectSelectorObject: type[RectSelectorObject]
    CircleSelectorObject: type[CircleSelectorObject]
    TextCaseObject: type[TextCaseObject]

# ========================================== ENGINE LIFECYCLE ==========================================
def init() -> None: ...
def run() -> None: ...
def stop() -> None: ...

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
audio: type[AudioManager]
data: type[DataManager]
entities: type[EntitiesManager]
geometry: type[GeometryManager]
inputs: type[InputsManager]
languages: type[LanguagesManager]
mouse: type[MouseManager]
network: type[NetworkManager]
panels: type[PanelsManager]
screen: type[ScreenManager]
settings: type[SettingsManager]
states: type[StatesManager]
time: type[TimeManager]
ui: type[UiManager]

# ========================================== EXPOSITION ==========================================
from typing import List
__all__: List[str]