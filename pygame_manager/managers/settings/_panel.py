# ======================================== IMPORTS ========================================
from typing import Real
from ... import context
import pygame

# ======================================== PANEL DE PARAMÈTRES ========================================
class SettingsPanel:
    """
    Panel auto-généré affichant et permettant la modification des paramètres.

    Utilisation :
        panel = settings_manager.Panel("settings_panel", x=100, y=50, width=500, height=600)
        panel.activate()
    """
    def __init__(
        self,
        name: str = "settings",
        # --- Position et taille ---
        x: Real = 0,
        y: Real = 0,
        width: Real = 1920,
        height: Real = 1080,
        # --- Params Panel standard ---
        predecessor: str = None,
        centered: bool = False,
        border_width: int = 0,
        border_color: pygame.Color = (0, 0, 0, 255),
        # --- Fond ---
        background_color: pygame.Color = (30, 30, 30, 255),
        # --- Texte ---
        text_color: pygame.Color = (220, 220, 220, 255),
        text_color_description: pygame.Color = (140, 140, 140, 255),
        # --- Barre des catégories ---
        category_color: pygame.Color = (42, 42, 42, 255),
        category_color_hover: pygame.Color = (62, 62, 62, 255),
        category_color_active: pygame.Color = (65, 105, 185, 255),
        category_text_color: pygame.Color = (160, 160, 160, 255),
        category_text_color_active: pygame.Color = (255, 255, 255, 255),
        # --- Items ---
        item_color: pygame.Color = (38, 38, 38, 255),
        item_color_alt: pygame.Color = (43, 43, 43, 255),
        # --- Contrôles ---
        control_color: pygame.Color = (55, 55, 55, 255),
        control_color_hover: pygame.Color = (75, 75, 75, 255),
        control_color_active: pygame.Color = (65, 105, 185, 255),
        # --- Layout ---
        category_height: int = 38,
        item_height: int = 52,
        item_spacing: int = 3,
        padding: int = 10,
        control_width_ratio: float = 0.38,
        font_size: int = None,
        border_radius: int = 5,
    ):
        self._manager = context.settings
        self._name = "settings"
        self._ui_objects = []
        self._current_category = None

        # Couleurs
        self._bg                  = background_color
        self._text_color          = text_color
        self._text_desc           = text_color_description
        self._cat_color           = category_color
        self._cat_hover           = category_color_hover
        self._cat_active          = category_color_active
        self._cat_text            = category_text_color
        self._cat_text_active     = category_text_color_active
        self._item_color          = item_color
        self._item_color_alt      = item_color_alt
        self._ctrl_color          = control_color
        self._ctrl_hover          = control_color_hover
        self._ctrl_active         = control_color_active

        # Layout
        self._cat_h    = category_height
        self._item_h   = item_height
        self._spacing  = item_spacing
        self._pad      = padding
        self._ctrl_ratio = max(0.2, min(0.7, control_width_ratio))
        self._font_size = font_size or max(12, int(item_height * 0.36))
        self._radius   = border_radius
        self._w        = int(width)
        self._h        = int(height)

        # Création du panel pygame avec fond auto-rempli
        _bg = background_color

        class _PanelImpl(context.panels.Panel):
            def draw_back(self_inner, surface: pygame.Surface):
                surface.fill(_bg)

        self._panel = _PanelImpl(
            name=name,
            predecessor=predecessor,
            rect=(x, y, width, height),
            centered=centered,
            border_width=border_width,
            border_color=border_color,
        )

    # ======================================== CONSTRUCTION ========================================
    def _clear(self):
        """Supprime tous les objets UI créés"""
        for obj in self._ui_objects:
            if hasattr(obj, 'kill'):
                obj.kill()
        self._ui_objects = []

    def build(self):
        """(Re)construit l'interface complète du panel"""
        self._clear()
        settings = self._manager._settings
        if not settings:
            return

        # Catégories dans l'ordre d'insertion (sans doublon)
        cats_seen = {}
        for s in settings.values():
            cats_seen[s.get('category', 'General')] = True
        categories = list(cats_seen.keys())

        if not categories:
            return

        if self._current_category is None or self._current_category not in categories:
            self._current_category = categories[0]

        self._build_category_bar(categories)
        self._build_items(settings)

    def _build_category_bar(self, categories: list):
        cat_font = max(10, int(self._cat_h * 0.42))
        n = max(1, len(categories))
        base_w = self._w // n

        for i, cat in enumerate(categories):
            is_active = (cat == self._current_category)
            # Dernière catégorie prend le reste
            w = base_w + (self._w - base_w * n if i == n - 1 else 0)

            def _make_cb(c):
                def _cb():
                    self._current_category = c
                    self.build()
                return _cb

            btn = context.ui.RectButton(
                x=i * base_w,
                y=0,
                width=w,
                height=self._cat_h,
                anchor="topleft",
                filling_color=self._cat_active if is_active else self._cat_color,
                filling_color_hover=self._cat_hover,
                text=cat,
                font_size=cat_font,
                font_color=self._cat_text_active if is_active else self._cat_text,
                border_radius=self._radius,
                callback=_make_cb(cat),
                panel=self._name,
                zorder=10,
            )
            self._ui_objects.append(btn)

    def _build_items(self, settings: dict):
        current = {
            k: v for k, v in settings.items()
            if v.get('category', 'General') == self._current_category
        }

        ctrl_w  = int(self._w * self._ctrl_ratio)
        item_w  = self._w - self._pad * 2
        start_y = self._cat_h + self._pad

        for i, (name, setting) in enumerate(current.items()):
            iy = start_y + i * (self._item_h + self._spacing)
            if iy + self._item_h > self._h:
                break

            bg_col = self._item_color if i % 2 == 0 else self._item_color_alt

            # Fond item (non-cliquable fonctionnellement)
            bg = context.ui.RectButton(
                x=self._pad,
                y=iy,
                width=item_w,
                height=self._item_h,
                anchor="topleft",
                filling_color=bg_col,
                border_radius=self._radius,
                callback=lambda: None,
                panel=self._name,
                zorder=1,
            )
            self._ui_objects.append(bg)

            # Label principal
            label = setting.get('label', name)
            desc  = setting.get('description')
            label_y = iy + self._item_h // 2 - (self._font_size // 3 if desc else 0)

            lbl = context.ui.Text(
                x=self._pad * 2,
                y=label_y,
                text=label,
                anchor="midleft",
                font_size=self._font_size,
                font_color=self._text_color,
                panel=self._name,
                zorder=2,
            )
            self._ui_objects.append(lbl)

            # Description optionnelle (sous le label)
            if desc:
                desc_fs = max(9, int(self._font_size * 0.72))
                desc_lbl = context.ui.Text(
                    x=self._pad * 2,
                    y=label_y + self._font_size // 2 + desc_fs // 2 + 2,
                    text=desc,
                    anchor="midleft",
                    font_size=desc_fs,
                    font_color=self._text_desc,
                    panel=self._name,
                    zorder=2,
                )
                self._ui_objects.append(desc_lbl)

            # Contrôle à droite
            ctrl_x  = self._w - self._pad - ctrl_w
            ctrl_cy = iy + self._item_h // 2
            ctrl_h  = int(self._item_h * 0.55)
            self._build_control(name, setting, ctrl_x, ctrl_cy, ctrl_w, ctrl_h)

    def _build_control(self, name: str, setting: dict, x: int, cy: int, width: int, height: int):
        """Crée le widget de contrôle adapté au type du paramètre"""
        stype  = setting.get('type', 'str')
        value  = setting['value']
        font_sz = max(10, int(height * 0.55))
        top_y  = cy - height // 2

        # ---- bool : deux boutons Oui / Non ----
        if stype == 'bool':
            gap = 3
            hw  = (width - gap) // 2
            for j, (lbl, val) in enumerate([("Oui", True), ("Non", False)]):
                is_sel = (value == val)
                def _make_cb(v):
                    def _cb():
                        self._manager.set(name, v)
                        self.build()
                    return _cb
                btn = context.ui.RectButton(
                    x=x + j * (hw + gap),
                    y=top_y,
                    width=hw,
                    height=height,
                    anchor="topleft",
                    filling_color=self._ctrl_active if is_sel else self._ctrl_color,
                    filling_color_hover=self._ctrl_hover,
                    text=lbl,
                    font_size=font_sz,
                    font_color=self._text_color,
                    border_radius=self._radius,
                    callback=_make_cb(val),
                    panel=self._name,
                    zorder=3,
                )
                self._ui_objects.append(btn)

        # ---- choice : un bouton par choix ----
        elif stype == 'choice':
            choices = setting.get('choices', [])
            if not choices:
                return
            n   = len(choices)
            gap = 2
            cw  = max(1, (width - gap * (n - 1)) // n)
            for j, choice in enumerate(choices):
                is_sel = (value == choice)
                def _make_cb(c):
                    def _cb():
                        self._manager.set(name, c)
                        self.build()
                    return _cb
                btn = context.ui.RectButton(
                    x=x + j * (cw + gap),
                    y=top_y,
                    width=cw,
                    height=height,
                    anchor="topleft",
                    filling_color=self._ctrl_active if is_sel else self._ctrl_color,
                    filling_color_hover=self._ctrl_hover,
                    text=str(choice),
                    font_size=font_sz,
                    font_color=self._text_color,
                    border_radius=self._radius,
                    callback=_make_cb(choice),
                    panel=self._name,
                    zorder=3,
                )
                self._ui_objects.append(btn)

        # ---- int / float : TextCase avec validation ----
        elif stype in ('int', 'float'):
            mn = setting.get('min')
            mx = setting.get('max')
            placeholder = f"[{mn} – {mx}]" if mn is not None and mx is not None else ""
            display = str(int(value)) if stype == 'int' else str(value)
            tc = context.ui.TextCase(
                x=x,
                y=top_y,
                width=width,
                height=height,
                text=display,
                placeholder=placeholder,
                font_size=font_sz,
                font_color=self._text_color,
                filling_color=self._ctrl_color,
                filling_color_hover=self._ctrl_hover,
                filling_color_focus=self._ctrl_active,
                border_width=1,
                border_color=self._ctrl_active,
                border_radius=self._radius,
                callback=self._make_num_cb(name, stype, setting),
                panel=self._name,
                zorder=3,
            )
            self._ui_objects.append(tc)

        # ---- str : TextCase libre ----
        else:
            def _str_cb(v):
                self._manager.set(name, v)
            tc = context.ui.TextCase(
                x=x,
                y=top_y,
                width=width,
                height=height,
                text=str(value),
                font_size=font_sz,
                font_color=self._text_color,
                filling_color=self._ctrl_color,
                filling_color_hover=self._ctrl_hover,
                filling_color_focus=self._ctrl_active,
                border_width=1,
                border_color=self._ctrl_active,
                border_radius=self._radius,
                callback=_str_cb,
                panel=self._name,
                zorder=3,
            )
            self._ui_objects.append(tc)

    def _make_num_cb(self, name: str, stype: str, setting: dict):
        """Callback de validation pour les champs numériques"""
        mn = setting.get('min')
        mx = setting.get('max')
        def _cb(text: str):
            try:
                v = int(text) if stype == 'int' else float(text)
                if mn is not None: v = max(mn, v)
                if mx is not None: v = min(mx, v)
                self._manager.set(name, v)
            except ValueError:
                pass
        return _cb

    # ======================================== INTERFACE PUBLIQUE ========================================
    def refresh(self):
        """Force une reconstruction complète de l'interface"""
        self.build()

    def activate(self):
        """Active le panel et construit son interface"""
        self._panel.activate()
        self.build()

    def deactivate(self, pruning: bool = True):
        """Désactive le panel"""
        self._panel.deactivate(pruning=pruning)

    def is_active(self) -> bool:
        return self._panel.is_active()

    @property
    def panel(self) -> object:
        """Renvoie le panel pygame sous-jacent"""
        return self._panel

    @property
    def name(self) -> str:
        return self._name