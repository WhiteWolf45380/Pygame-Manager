# _panel.py
# ======================================== IMPORTS ========================================
from numbers import Real
from ... import context
import pygame

# ======================================== PANEL DE PARAMÈTRES ========================================
class SettingsPanel:
    """
    Panel auto-généré affichant et permettant la modification des paramètres.

    Widgets disponibles selon le champ 'widget' de chaque paramètre :
        'toggle'      → deux boutons Oui / Non
        'choice'      → un bouton par choix
        'textcase'    → champ de saisie texte (avec validation numérique si int/float)
        'slider'      → boutons − / valeur / + avec min, max et step
        'inputbutton' → bouton de capture de touche clavier
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
        """
        Args:
            name (str)                               : nom du panel pygame (doit être unique)

            x (Real)                                 : coordonnée x du coin supérieur gauche
            y (Real)                                 : coordonnée y du coin supérieur gauche
            width (Real)                             : largeur du panel
            height (Real)                            : hauteur du panel

            predecessor (str, optional)              : nom du panel prédecesseur
            centered (bool, optional)                : coordonnées à partir du centre de la surface maître
            border_width (int, optional)             : épaisseur de la bordure du panel
            border_color (Color, optional)           : couleur de la bordure du panel

            background_color (Color, optional)           : couleur de fond du panel

            text_color (Color, optional)                 : couleur des labels de paramètres
            text_color_description (Color, optional)     : couleur des sous-textes de description

            category_color (Color, optional)             : couleur de fond des onglets inactifs
            category_color_hover (Color, optional)       : couleur de fond des onglets au survol
            category_color_active (Color, optional)      : couleur de fond de l'onglet actif
            category_text_color (Color, optional)        : couleur du texte des onglets inactifs
            category_text_color_active (Color, optional) : couleur du texte de l'onglet actif

            item_color (Color, optional)                 : couleur de fond des lignes paires
            item_color_alt (Color, optional)             : couleur de fond des lignes impaires

            control_color (Color, optional)              : couleur de fond des contrôles
            control_color_hover (Color, optional)        : couleur de fond des contrôles au survol
            control_color_active (Color, optional)       : couleur de fond des contrôles actifs/sélectionnés

            category_height (int, optional)              : hauteur en pixels de la barre des catégories
            item_height (int, optional)                  : hauteur en pixels de chaque ligne de paramètre
            item_spacing (int, optional)                 : espacement en pixels entre les lignes
            padding (int, optional)                      : marge interne gauche/droite en pixels
            control_width_ratio (float, optional)        : ratio de la largeur réservé aux contrôles (0.2 – 0.7)
            font_size (int, optional)                    : taille de la police des labels (auto si None)
            border_radius (int, optional)                : rayon d'arrondissement des coins des éléments
        """
        self._manager = context.settings
        self._name    = name
        self._ui_objects = []
        self._current_category = None

        # Couleurs
        self._bg              = background_color
        self._text_color      = text_color
        self._text_desc       = text_color_description
        self._cat_color       = category_color
        self._cat_hover       = category_color_hover
        self._cat_active      = category_color_active
        self._cat_text        = category_text_color
        self._cat_text_active = category_text_color_active
        self._item_color      = item_color
        self._item_color_alt  = item_color_alt
        self._ctrl_color      = control_color
        self._ctrl_hover      = control_color_hover
        self._ctrl_active     = control_color_active

        # Layout
        self._cat_h      = category_height
        self._item_h     = item_height
        self._spacing    = item_spacing
        self._pad        = padding
        self._ctrl_ratio = max(0.2, min(0.7, control_width_ratio))
        self._font_size  = font_size or max(12, int(item_height * 0.36))
        self._radius     = border_radius
        self._w          = int(width)
        self._h          = int(height)

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
        n        = max(1, len(categories))
        base_w   = self._w // n

        for i, cat in enumerate(categories):
            is_active = (cat == self._current_category)
            w = base_w + (self._w - base_w * n if i == n - 1 else 0)

            def _make_cb(c):
                def _cb():
                    self._current_category = c
                    self.build()
                return _cb

            btn = context.ui.RectButton(
                x=i * base_w, y=0, width=w, height=self._cat_h, anchor="topleft",
                filling_color=self._cat_active if is_active else self._cat_color,
                filling_color_hover=self._cat_hover,
                text=cat, font_size=cat_font,
                font_color=self._cat_text_active if is_active else self._cat_text,
                border_radius=self._radius,
                callback=_make_cb(cat),
                panel=self._name, zorder=10,
            )
            self._ui_objects.append(btn)

    def _build_items(self, settings: dict):
        current = {k: v for k, v in settings.items()
                   if v.get('category', 'General') == self._current_category}

        ctrl_w  = int(self._w * self._ctrl_ratio)
        item_w  = self._w - self._pad * 2
        start_y = self._cat_h + self._pad

        for i, (name, setting) in enumerate(current.items()):
            iy = start_y + i * (self._item_h + self._spacing)
            if iy + self._item_h > self._h:
                break

            # Fond de ligne
            bg_col = self._item_color if i % 2 == 0 else self._item_color_alt
            bg = context.ui.RectButton(
                x=self._pad, y=iy, width=item_w, height=self._item_h, anchor="topleft",
                filling_color=bg_col, border_radius=self._radius,
                callback=lambda: None, panel=self._name, zorder=1,
            )
            self._ui_objects.append(bg)

            # Label + description
            label   = setting.get('label', name)
            desc    = setting.get('description')
            label_y = iy + self._item_h // 2 - (self._font_size // 3 if desc else 0)

            lbl = context.ui.Text(
                x=self._pad * 2, y=label_y, text=label, anchor="midleft",
                font_size=self._font_size, font_color=self._text_color,
                panel=self._name, zorder=2,
            )
            self._ui_objects.append(lbl)

            if desc:
                desc_fs = max(9, int(self._font_size * 0.72))
                desc_lbl = context.ui.Text(
                    x=self._pad * 2,
                    y=label_y + self._font_size // 2 + desc_fs // 2 + 2,
                    text=desc, anchor="midleft",
                    font_size=desc_fs, font_color=self._text_desc,
                    panel=self._name, zorder=2,
                )
                self._ui_objects.append(desc_lbl)

            # Contrôle
            ctrl_x  = self._w - self._pad - ctrl_w
            ctrl_cy = iy + self._item_h // 2
            ctrl_h  = int(self._item_h * 0.55)
            self._build_control(name, setting, ctrl_x, ctrl_cy, ctrl_w, ctrl_h)

    def _build_control(self, name: str, setting: dict, x: int, cy: int, width: int, height: int):
        """Crée le widget adapté au champ 'widget' du paramètre"""
        widget  = setting.get('widget', 'textcase')
        value   = setting['value']
        font_sz = max(10, int(height * 0.55))
        top_y   = cy - height // 2

        # ---- toggle : Oui / Non ----
        if widget == 'toggle':
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
                    x=x + j * (hw + gap), y=top_y, width=hw, height=height, anchor="topleft",
                    filling_color=self._ctrl_active if is_sel else self._ctrl_color,
                    filling_color_hover=self._ctrl_hover,
                    text=lbl, font_size=font_sz, font_color=self._text_color,
                    border_radius=self._radius,
                    callback=_make_cb(val), panel=self._name, zorder=3,
                )
                self._ui_objects.append(btn)

        # ---- choice : un bouton par choix ----
        elif widget == 'choice':
            choices = setting.get('choices', [])
            if not choices:
                return
            n  = len(choices)
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
                    x=x + j * (cw + gap), y=top_y, width=cw, height=height, anchor="topleft",
                    filling_color=self._ctrl_active if is_sel else self._ctrl_color,
                    filling_color_hover=self._ctrl_hover,
                    text=str(choice), font_size=font_sz, font_color=self._text_color,
                    border_radius=self._radius,
                    callback=_make_cb(choice), panel=self._name, zorder=3,
                )
                self._ui_objects.append(btn)

        # ---- slider : − | valeur | + ----
        elif widget == 'slider':
            mn   = setting.get('min')
            mx   = setting.get('max')
            step = setting.get('step') or (1 if isinstance(value, int) else 0.1)
            gap  = 3
            btn_w = int(height * 1.1)   # boutons − et + carrés
            val_w = width - 2 * btn_w - 2 * gap

            def _make_dec(n, s, mn_):
                def _cb():
                    v = self._manager._settings[n]['value']
                    v = round(v - s, 10)
                    if mn_ is not None: v = max(mn_, v)
                    self._manager.set(n, v)
                    self.build()
                return _cb

            def _make_inc(n, s, mx_):
                def _cb():
                    v = self._manager._settings[n]['value']
                    v = round(v + s, 10)
                    if mx_ is not None: v = min(mx_, v)
                    self._manager.set(n, v)
                    self.build()
                return _cb

            # Bouton −
            btn_dec = context.ui.RectButton(
                x=x, y=top_y, width=btn_w, height=height, anchor="topleft",
                filling_color=self._ctrl_color, filling_color_hover=self._ctrl_hover,
                text="−", font_size=font_sz, font_color=self._text_color,
                border_radius=self._radius,
                callback=_make_dec(name, step, mn), panel=self._name, zorder=3,
            )
            self._ui_objects.append(btn_dec)

            # Affichage valeur
            display = str(int(value)) if isinstance(value, int) else f"{value:.2f}".rstrip('0').rstrip('.')
            val_btn = context.ui.RectButton(
                x=x + btn_w + gap, y=top_y, width=val_w, height=height, anchor="topleft",
                filling_color=self._ctrl_color,
                text=display, font_size=font_sz, font_color=self._text_color,
                border_radius=self._radius,
                callback=lambda: None, panel=self._name, zorder=3,
            )
            self._ui_objects.append(val_btn)

            # Bouton +
            btn_inc = context.ui.RectButton(
                x=x + btn_w + gap + val_w + gap, y=top_y, width=btn_w, height=height, anchor="topleft",
                filling_color=self._ctrl_color, filling_color_hover=self._ctrl_hover,
                text="+", font_size=font_sz, font_color=self._text_color,
                border_radius=self._radius,
                callback=_make_inc(name, step, mx), panel=self._name, zorder=3,
            )
            self._ui_objects.append(btn_inc)

        # ---- textcase : saisie libre ----
        elif widget == 'textcase':
            is_numeric = isinstance(value, (int, float))
            mn = setting.get('min')
            mx = setting.get('max')
            placeholder = f"[{mn} – {mx}]" if is_numeric and mn is not None and mx is not None else ""
            display = str(int(value)) if isinstance(value, int) else str(value)

            cb = self._make_num_cb(name, isinstance(value, int), setting) if is_numeric else (
                lambda v: self._manager.set(name, v)
            )

            tc = context.ui.TextCase(
                x=x, y=top_y, width=width, height=height,
                text=display, placeholder=placeholder,
                font_size=font_sz, font_color=self._text_color,
                filling_color=self._ctrl_color,
                filling_color_hover=self._ctrl_hover,
                filling_color_focus=self._ctrl_active,
                border_width=1, border_color=self._ctrl_active,
                border_radius=self._radius,
                callback=cb, panel=self._name, zorder=3,
            )
            self._ui_objects.append(tc)

        # ---- inputbutton : capture de touche ----
        elif widget == 'inputbutton':
            key_names = setting.get('key_names', {})
            def _make_cb(n):
                def _cb(k):
                    self._manager.set(n, k)
                return _cb
            ib = context.ui.InputButton(
                x=x, y=top_y, width=width, height=height, anchor="topleft",
                key=value,
                key_names=key_names,
                filling_color=self._ctrl_color,
                filling_color_hover=self._ctrl_hover,
                filling_color_selected=self._ctrl_active,
                font_size=font_sz, font_color=self._text_color,
                border_radius=self._radius,
                callback=_make_cb(name), panel=self._name, zorder=3,
            )
            self._ui_objects.append(ib)

    def _make_num_cb(self, name: str, is_int: bool, setting: dict):
        mn = setting.get('min')
        mx = setting.get('max')
        def _cb(text: str):
            try:
                v = int(text) if is_int else float(text)
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
        self._panel.deactivate(pruning=pruning)

    def is_active(self) -> bool:
        return self._panel.is_active()

    @property
    def panel(self) -> object:
        return self._panel

    @property
    def name(self) -> str:
        return self._name