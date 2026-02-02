# ======================================== IMPORTS ========================================
from _core import *
from collections import defaultdict
from ._sprite import Sprite
from ._sprite_entity import SpriteEntity

# ======================================== GESTIONNAIRE ========================================
class SpritesManager:
    """
    Gestionnaire de l'ensemble des sprites

    Fonctionnalités:
        gestion du zorder
    """
    def __init__(self):
        self._all = defaultdict(list)          # {"panel": [Sprite1, Sprite2], ...}

        self.Sprite = Sprite
        self.SpriteEntity = SpriteEntity

    # ======================================== ENREGISTREMENT ========================================
    def register(self, sprite: Sprite):
        """Enregistre un nouveau sprite"""
        panel =  getattr(sprite, '_panel')
        z = getattr(sprite, '_zorder', None)
        if sprite not in self._all[panel]:
            if z is None:
                self._all[sprite._panel].append(sprite)
            else:
                self._all[sprite._panel].insert(z, sprite)

    # ======================================== Z-ORDER ========================================
    def reorder(self, panel: str | None, sprite: Sprite, direction: str, index: int = None):
        """
        Réordonne un sprite dans la liste de son panel

        Args:
            name (str) : sprite à réordoner
            direction (str) : "forward", "backward", "front", "back", "index"
            index (int | None) : utilisé uniquement avec "index"
        """
        panel_sprites = self._all.get(panel, [])
        if sprite not in panel_sprites:
            _raise_error(self, 'reorder', f'Sprite "{sprite}" does not exist')
        
        i = panel_sprites.index(sprite)
        if direction == "forward":
            if i < len(panel_sprites) - 1:
                panel_sprites[i], panel_sprites[i + 1] = panel_sprites[i + 1], panel_sprites[i]

        elif direction == "backward":
            if i > 0:
                panel_sprites[i], panel_sprites[i - 1] = panel_sprites[i - 1], panel_sprites[i]

        elif direction == "front":
            panel_sprites.remove(sprite)
            panel_sprites.append(sprite)

        elif direction == "back":
            panel_sprites.remove(sprite)
            panel_sprites.insert(0, sprite)

        elif direction == "index":
            if index is None:
                _raise_error(self, 'reorder', '"index" requires an index')
            panel_sprites.remove(sprite)
            panel_sprites.insert(index, sprite)

    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Execute update de tous les sprites"""
        for panel_name in self._all:
            for sprite in self._all[panel_name]:
                getattr(sprite, '_update', lambda: None)()

    def draw(self):
        """Execute draw de tous les sprites"""
        for panel_name in self._all:
            for sprite in self._all[panel_name]:
                if panel_name in context.panels:
                    panel_surface = getattr(context.panels[panel_name], 'surface', context.screen.surface)
                else:
                    panel_surface = context.screen.surface
                getattr(sprite, '_draw', lambda _: None)(panel_surface)