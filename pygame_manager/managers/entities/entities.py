# ======================================== IMPORTS ========================================
from ._core import *
from collections import defaultdict
from ._entity import Entity
from ._sprite_entity import SpriteEntity
from ._segment_entity import SegmentEntity
from ._line_entity import LineEntity
from ._circle_entity import CircleEntity
from ._rect_entity import RectEntity
from ._polygon_entity import PolygonEntity

# ======================================== GESTIONNAIRE ========================================
class EntitiesManager:
    """
    Gestionnaire de l'ensemble des entités

    Fonctionnalités:
        gestion du zorder
    """
    def __init__(self):
        self._all = defaultdict(list)          # {"panel": [Entity1, Entity2], ...}
        self._filtered = []

        self.Entity = Entity
        self.SpriteEntity = SpriteEntity
        self.SegmentEntity = SegmentEntity
        self.LineEntity = LineEntity
        self.RectEntity = RectEntity
        self.CircleEntity = CircleEntity
        self.PolygonEntity = PolygonEntity

    def __repr__(self) -> str:
        return f"<entitiesmanager: {sum(len(l) for l in self._all.values())} entities>"

    # ======================================== GETTERS ========================================
    def get_by_panel(self, panel: str | None) -> list[Entity]:
        """
        Renvoie la liset des entités associées à un panel

        Args:
            panel (str | None) : le panel de recherche
        """
        return self._all.get(panel, [])
    
    def get_by_type(self, cls: object.__class__, panel: str | None = None):
        """
        Recherche par type d'entité

        Args:
            cls (object.__class__) : le type d'objet recherché
            panel (str, optional) : limitation de la recherche à un panel
        """
        panels = [panel] if panel else self._all.keys()
        return [
            e for p in panels
            for e in self._all.get(p, [])
            if isinstance(e, cls)
        ]
    
    def get_by_filter(self, predicate: callable, panel: str | None = None):
        """
        Recherche selon un filtre

        Args:
            predicate (callable) : le prédicat de filtrage
            panel (str | None, optional) : limitation de la recherche à un panel
        """
        panels = [panel] if panel else self._all.keys()
        return [
            e for p in panels
            for e in self._all.get(p, [])
            if predicate(e)
        ]

    # ======================================== ENREGISTREMENT ========================================
    def register(self, entity: Entity):
        """
        Enregistre une nouvelle entité

        Args:
            entity (Entity) : l'objet de l'entité
        """
        panel =  getattr(entity, '_panel')
        z = getattr(entity, '_zorder', None)
        if entity not in self._all[panel]:
            if z is None:
                self._all[entity._panel].append(entity)
            else:
                self._all[entity._panel].insert(z, entity)

    def discard(self, entity: Entity):
        """
        Supprime une entité

        Args:
            entity (Entity) : objet de l'entité
        """
        panel = getattr(entity, '_panel', None)
        if panel in self._all and entity in self._all[panel]:
            self._all[panel].remove(entity)
            if not self._all[panel]: del self._all[panel]

    # ======================================== Z-ORDER ========================================
    def reorder(self, entity: Entity, direction: str, index: int = None, panel: str | None = None):
        """
        Réordonne une entité dans la liste de son panel

        Args:
            entity (Entity) : entité à réordoner
            direction (str) : "forward", "backward", "front", "back", "index"
            index (int | None) : utilisé uniquement avec "index"
            panel (str | None) : nom du panel de l'entité
        """
        panel_entities = self._all.get(panel, [])
        if entity not in panel_entities:
            _raise_error(self, 'reorder', f'Entity "{entity}" does not exist')
        
        i = panel_entities.index(entity)
        if direction == "forward":
            if i < len(panel_entities) - 1:
                panel_entities[i], panel_entities[i + 1] = panel_entities[i + 1], panel_entities[i]

        elif direction == "backward":
            if i > 0:
                panel_entities[i], panel_entities[i - 1] = panel_entities[i - 1], panel_entities[i]

        elif direction == "front":
            panel_entities.remove(entity)
            panel_entities.append(entity)

        elif direction == "back":
            panel_entities.remove(entity)
            panel_entities.insert(0, entity)

        elif direction == "index":
            if index is None:
                _raise_error(self, 'reorder', '"index" requires an index')
            panel_entities.remove(entity)
            panel_entities.insert(index, entity)

    # ======================================== METHODES DYNAMIQUES ========================================
    def clear_panel(self, panel: str | None):
        """
        Supprime toutes les entités du panel

        Args:
            panel (str | None) : panel à nettoyer
        """
        self._all.pop(panel, None)

    def clear(self):
        """Supprime toutes les entités"""
        self._all.clear()

    # ======================================== ACTUALISATION ========================================
    def update_filter(self):
        """Actualise les entités filtrées"""
        self._filtered = []
        for panel_name in self._all.keys():
            if panel_name is not None and not context.panels.is_active(panel_name):
                continue
            self._filtered.append(panel_name)

    def update(self):
        """Execute update de toutes les entités"""
        self.update_filter()
        for panel_name in self._filtered:
            for entity in self._all[panel_name]:
                getattr(entity, '_update', lambda: None)()

    def draw(self):
        """Execute draw de toutes les entités"""
        for panel_name in self._filtered:
            for entity in self._all[panel_name]:
                if panel_name in context.panels:
                    panel_surface = getattr(context.panels[panel_name], 'surface', context.screen.surface)
                else:
                    panel_surface = context.screen.surface
                getattr(entity, '_draw', lambda _: None)(panel_surface)

# ======================================== INSTANCIATION ========================================
entities_manager = EntitiesManager()