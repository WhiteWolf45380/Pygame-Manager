# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class RectSelectorObject:
    """
    Object de l'interface : Sélecteur rectangulaire

    Appartient à un groupe de sélection identifié par selection_id.
    Un seul sélecteur par groupe peut être actif à la fois (radio-style).
    S'enregistre et s'actualise automatiquement en tant qu'objet lors de l'instanciation.
    """
    def __init__(
            self,
            x: Real = -1,
            y: Real = -1,
            width: Real = -1,
            height: Real = -1,
            anchor: str = "topleft",

            selection_id: str = "",
            selector_id: str = "",

            filling: bool = True,
            filling_color: pygame.Color = (255, 255, 255, 255),
            filling_color_hover: pygame.Color = None,
            filling_color_selected: pygame.Color = None,

            icon: pygame.Surface = None,
            icon_hover: pygame.Surface = None,
            icon_selected: pygame.Surface = None,
            icon_keep_ratio: bool = True,
            icon_scale_ratio: float = 0.8,

            title: str = None,
            text: str = None,
            description: str = None,
            text_anchor: str = "center",  # Position du bloc de texte
            text_width_ratio: float = 0.8,
            text_height_ratio: float = 0.8,
            font_color: pygame.Color = (0, 0, 0, 255),
            font_color_hover: pygame.Color = None,
            font_color_selected: pygame.Color = None,

            border_width: int = 0,
            border_color: pygame.Color = (0, 0, 0, 255),
            border_radius: int = 0,

            hover_scale_ratio: float = 1.0,
            hover_scale_duration: float = 0.0,

            callback: callable = lambda: None,
            panel: object = None
        ):
        """
        Args:
            x (Real) : coordonnée de la gauche
            y (Real) : coordonnée du haut
            width (Real) : largeur
            height (Real) : hauteur
            anchor (str) : point d'ancrage du rectangle

            selection_id (str) : identifiant du groupe de sélection
            selector_id (str) : identifiant unique de ce sélecteur dans le groupe

            filling (bool, optional) : remplissage
            filling_color (Color, optional) : couleur de fond
            filling_color_hover (Color, optional) : couleur de fond lors du survol
            filling_color_selected (Color, optional) : couleur de fond lorsque sélectionné

            icon (Surface, optional) : image de fond
            icon_hover (Surface, optional) : image lors du survol
            icon_selected (Surface, optional) : image lorsque sélectionné
            icon_keep_ratio (bool, optional) : pas de déformation, ratio_locker
            icon_scale_ratio (float, optional) : ratio maximum par rapport aux dimensions du bouton

            title/text/description (str, optional) : textes du sélecteur
            text_anchor (str, optional) : position du bloc de texte (ex: "topleft", "center", "bottomright")
            text_width_ratio (float, optional) : ratio max du texte par rapport à la largeur
            text_height_ratio (float, optional) : ratio max du texte par rapport à la hauteur
            font_color (Color, optional) : couleur de la police
            font_color_hover (Color, optional) : couleur de la police lors du survol
            font_color_selected (Color, optional) : couleur de la police lorsque sélectionné

            border_width (int, optional) : épaisseur de la bordure
            border_color (Color, optional) : couleur de la bordure
            border_radius (int, optional) : rayon d'arrondissement des coins

            hover_scale_ratio (float, optional) : facteur de redimensionnement lors du survol
            hover_scale_duration (float, optional) : durée de redimensionnement (en secondes)

            callback (callable, optional) : action en cas de sélection
            panel (object, optional) : panel maître
        """
        # vérifications
        if not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(width, Real): _raise_error(self, '__init__', 'Invalid width argument')
        if not isinstance(height, Real): _raise_error(self, '__init__', 'Invalid height argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(selection_id, str) or not selection_id: _raise_error(self, '__init__', 'Invalid selection_id argument')
        if selection_id not in context.ui.get_selections(): _raise_error(self, '__init__', f"Selection {selection_id} does not exist")
        if not isinstance(selector_id, str) or not selector_id: _raise_error(self, '__init__', 'Invalid selector_id argument')
        if not isinstance(filling, bool): _raise_error(self, '__init__', 'Invalid filling argument')
        filling_color = _to_color(filling_color, method='__init__')
        filling_color_hover = _to_color(filling_color_hover, raised=False)
        filling_color_selected = _to_color(filling_color_selected, raised=False)
        if icon is not None and not isinstance(icon, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon argument')
        if icon_hover is not None and not isinstance(icon_hover, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon_hover argument')
        if icon_selected is not None and not isinstance(icon_selected, pygame.Surface): _raise_error(self, '__init__', 'Invalid icon_selected argument')
        if not isinstance(icon_keep_ratio, bool): _raise_error(self, '__init__', 'Invalid icon_keep_ratio argument')
        if not isinstance(icon_scale_ratio, Real): _raise_error(self, '__init__', 'Invalid icon_scale_ratio argument')
        if not isinstance(text_anchor, str): _raise_error(self, '__init__', 'Invalid text_anchor argument')
        if not isinstance(text_width_ratio, (float, int)) or not (0 < text_width_ratio <= 1): _raise_error(self, '__init__', 'Invalid text_width_ratio argument')
        if not isinstance(text_height_ratio, (float, int)) or not (0 < text_height_ratio <= 1): _raise_error(self, '__init__', 'Invalid text_height_ratio argument')
        font_color = _to_color(font_color, method='__init__')
        font_color_hover = _to_color(font_color_hover, raised=False)
        font_color_selected = _to_color(font_color_selected, raised=False)
        if not isinstance(border_width, int): _raise_error(self, '__init__', 'Invalid border_width argument')
        border_color = _to_color(border_color, method='__init__')
        if not isinstance(border_radius, int): _raise_error(self, '__init__', 'Invalid border_radius argument')
        if not isinstance(hover_scale_ratio, Real) or hover_scale_ratio <= 0: _raise_error(self, '__init__', 'Invalid hover_scale_ratio argument')
        if not isinstance(hover_scale_duration, Real) or hover_scale_duration < 0: _raise_error(self, '__init__', 'Invalid hover_scale_duration argument')
        if not callable(callback): _raise_error(self, '__init__', 'Invalid callback argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')

        # auto-registration
        context.ui._append(self)
        context.ui.add_selection(selection_id)

        # zorder
        self._zorder = 0

        # surface
        self._surface = None
        self._surface_rect = None

        # sélection
        self._selection_id = selection_id
        self._selector_id = selector_id

        # position et taille
        width = min(1920, max(5, width))
        height = min(1080, max(5, height))
        self._rect = pygame.Rect(0, 0, width, height)
        setattr(self._rect, anchor, (x, y))
        self._local_rect = pygame.Rect(0, 0, width, height)

        # background
        self._filling = filling
        self._filling_color = filling_color
        self._filling_color_hover = filling_color_hover
        self._filling_color_selected = filling_color_selected

        # images — 3 états
        self._icon_keep_ratio = icon_keep_ratio
        self._icon_scale_ratio = icon_scale_ratio

        self._icon = None
        self._icon_rect = None
        if icon is not None:
            iwidth, iheight = icon.get_size()
            if self._icon_keep_ratio:
                width_ratio = (width * self._icon_scale_ratio) / iwidth
                height_ratio = (height * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = int(min(iwidth, width * self._icon_scale_ratio))
                iheight = int(min(iheight, height * self._icon_scale_ratio))
            self._icon = pygame.transform.smoothscale(icon, (iwidth, iheight))
            self._icon_rect = self._icon.get_rect(center=self._local_rect.center)

        self._icon_hover = self._icon
        self._icon_hover_rect = self._icon_rect
        if icon_hover is not None:
            iwidth, iheight = icon_hover.get_size()
            if self._icon_keep_ratio:
                width_ratio = (width * self._icon_scale_ratio) / iwidth
                height_ratio = (height * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = int(min(iwidth, width * self._icon_scale_ratio))
                iheight = int(min(iheight, height * self._icon_scale_ratio))
            self._icon_hover = pygame.transform.smoothscale(icon_hover, (iwidth, iheight))
            self._icon_hover_rect = self._icon_hover.get_rect(center=self._local_rect.center)

        self._icon_selected = self._icon
        self._icon_selected_rect = self._icon_rect
        if icon_selected is not None:
            iwidth, iheight = icon_selected.get_size()
            if self._icon_keep_ratio:
                width_ratio = (width * self._icon_scale_ratio) / iwidth
                height_ratio = (height * self._icon_scale_ratio) / iheight
                scale_ratio = min(width_ratio, height_ratio)
                iwidth = int(iwidth * scale_ratio)
                iheight = int(iheight * scale_ratio)
            else:
                iwidth = int(min(iwidth, width * self._icon_scale_ratio))
                iheight = int(min(iheight, height * self._icon_scale_ratio))
            self._icon_selected = pygame.transform.smoothscale(icon_selected, (iwidth, iheight))
            self._icon_selected_rect = self._icon_selected.get_rect(center=self._local_rect.center)

        # texte — gestion title / text / description
        self._text_anchor = text_anchor
        self._text_width_ratio = text_width_ratio
        self._text_height_ratio = text_height_ratio
        self._font_color = font_color
        self._font_color_hover = font_color_hover if font_color_hover is not None else font_color
        self._font_color_selected = font_color_selected if font_color_selected is not None else font_color

        self._texts = {
            "title": title,
            "text": text,
            "description": description
        }

        self._text_objects = {}
        self._text_objects_hover = {}
        self._text_objects_selected = {}
        self._text_rects = {}
        self._text_blit = any(self._texts.values())

        if self._text_blit:
            # Calcul de hauteur cumulée pour les 3 textes
            total_texts = sum(1 for t in self._texts.values() if t)
            available_height = self._rect.height * self._text_height_ratio / max(total_texts,1)
            available_width = self._rect.width * self._text_width_ratio

            for ttype, tstr in self._texts.items():
                if tstr is None:
                    continue
                # Taille de base
                base_size = max(9, int(min(available_height*0.8, available_width*0.1)))
                font = pygame.font.Font(None, base_size)
                # Ajustement si nécessaire
                test_size = base_size
                test_render = font.render(tstr, True, (0,0,0))
                while (test_render.get_width() > available_width or test_render.get_height() > available_height) and test_size > 5:
                    test_size -= 1
                    font = pygame.font.Font(None, test_size)
                    test_render = font.render(tstr, True, (0,0,0))
                # Création surfaces
                self._text_objects[ttype] = font.render(tstr, True, self._font_color)
                self._text_objects_hover[ttype] = font.render(tstr, True, self._font_color_hover)
                self._text_objects_selected[ttype] = font.render(tstr, True, self._font_color_selected)
                self._text_rects[ttype] = self._text_objects[ttype].get_rect()

            # Calcul positions verticales
            self._calculate_text_positions()

        # bordure
        self._border_width = max(0, border_width)
        self._border_color = border_color
        self._border_radius = max(0, border_radius)

        # effet de survol
        self._scale_ratio = 1.0
        self._last_scale_ratio = 1.0
        self._hover_scale_ratio = float(hover_scale_ratio)
        self._hover_scale_duration = float(hover_scale_duration)

        # action de clique
        self._callback = callback

        # panel maître
        if isinstance(panel, str): self._panel = context.panels[panel]
        else: self._panel = panel if panel in context.panels else None

        # préchargement
        self._preloaded = {}
        self._preloaded["default"] = self.load_default()
        self._preloaded["hover"] = self.load_hover()
        self._preloaded["selected"] = self.load_selected()

        # paramètres dynamiques
        self._visible = True

    # ======================================== CALCUL POSITIONS TEXTE ========================================
    def _calculate_text_positions(self):
        """
        Calcule les positions verticales des textes title -> text -> description
        selon text_anchor.
        """
        if not self._text_blit:
            return
        # Décalage vertical cumulatif
        total_height = sum([surf.get_height()*1.2 for surf in self._text_objects.values()])
        y_start = getattr(self._local_rect, self._text_anchor) - total_height//2 if "center" in self._text_anchor else getattr(self._local_rect, self._text_anchor)
        current_y = y_start
        for ttype in ["title", "text", "description"]:
            if ttype not in self._text_objects:
                continue
            rect = self._text_objects[ttype].get_rect()
            rect.centerx = self._local_rect.centerx
            rect.y = current_y
            self._text_rects[ttype] = rect
            current_y += rect.height*1.2

    # ======================================== GETTERS ========================================
    @property
    def zorder(self) -> int:
        """Renvoie le zorder"""
        return self._zorder

    @property
    def panel(self) -> object:
        """Renvoie le panel maître"""
        return self._panel

    @property
    def visible(self) -> bool:
        """Vérifie la visibilité"""
        return self._visible

    @property
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame"""
        return self._rect.copy()

    @property
    def callback(self) -> callable:
        """Renvoie le callback"""
        return self._callback

    @property
    def selected(self) -> bool:
        """Vérifie que le sélecteur soit actif dans son groupe"""
        return context.ui._selections.get(self._selection_id) == self._selector_id

    # ======================================== SETTERS ========================================
    @zorder.setter
    def zorder(self, value: int):
        """Fixe le zorder"""
        if not isinstance(value, int):
            _raise_error(self, 'set_zorder', 'Invalid zorder argument')
        self._zorder = value

    @visible.setter
    def visible(self, value: bool):
        """Fixe la visibilité"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_visible', 'Invalid value argument')
        self._visible = value

    @callback.setter
    def callback(self, callback: callable):
        """Fixe le callback"""
        if not callable(callback):
            _raise_error(self, 'set_callback', 'Invalid callback argument')
        self._callback = callback

    # ======================================== PREDICATS ========================================
    def is_hovered(self) -> bool:
        """Vérifie que le sélecteur soit survolé"""
        return context.ui.get_hovered() == self

    @property
    def hovered(self) -> bool:
        """Vérifie que le sélecteur soit survolé"""
        return context.ui.get_hovered() == self

    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le sélecteur"""
        mouse_pos = self._panel.mouse_pos if self._panel is not None else context.mouse.get_pos()
        return self._rect.collidepoint(mouse_pos)

    # ======================================== DESSIN ========================================
    def load_default(self) -> pygame.Surface:
        """Génère la surface par défaut"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        if self._filling:
            pygame.draw.rect(surface, self._filling_color, self._local_rect, border_radius=self._border_radius)
        if self._icon is not None:
            surface.blit(self._icon, self._icon_rect)
        if self._text_blit:
            for ttype in ["title","text","description"]:
                if ttype in self._text_objects:
                    surface.blit(self._text_objects[ttype], self._text_rects[ttype])
        if self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, self._local_rect, self._border_width, border_radius=self._border_radius)
        return surface

    def load_hover(self) -> pygame.Surface:
        """Génère la surface survolée"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        hover_color = self._filling_color_hover if self._filling_color_hover is not None else self._filling_color
        if self._filling:
            pygame.draw.rect(surface, hover_color, self._local_rect, border_radius=self._border_radius)
        if self._icon_hover is not None:
            surface.blit(self._icon_hover, self._icon_hover_rect)
        if self._text_blit:
            for ttype in ["title","text","description"]:
                if ttype in self._text_objects_hover:
                    surface.blit(self._text_objects_hover[ttype], self._text_rects[ttype])
        if self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, self._local_rect, self._border_width, border_radius=self._border_radius)
        return surface

    def load_selected(self) -> pygame.Surface:
        """Génère la surface sélectionnée"""
        surface = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
        selected_color = self._filling_color_selected if self._filling_color_selected is not None else self._filling_color
        if self._filling:
            pygame.draw.rect(surface, selected_color, self._local_rect, border_radius=self._border_radius)
        if self._icon_selected is not None:
            surface.blit(self._icon_selected, self._icon_selected_rect)
        if self._text_blit:
            for ttype in ["title","text","description"]:
                if ttype in self._text_objects_selected:
                    surface.blit(self._text_objects_selected[ttype], self._text_rects[ttype])
        if self._border_width > 0:
            pygame.draw.rect(surface, self._border_color, self._local_rect, self._border_width, border_radius=self._border_radius)
        return surface

    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        """Détruit l'objet"""
        context.ui._remove(self)

    def select(self):
        """Sélectionne ce sélecteur dans son groupe et lance le callback"""
        context.ui._select(self._selection_id, self._selector_id)
        self._callback()

    def update(self):
        """Actualisation par frame"""
        if not self._visible:
            return
        # Calcul du ratio de taille
        target_ratio = self._hover_scale_ratio if self.hovered else 1.0
        if self._hover_scale_duration > 0:
            diff = target_ratio - self._scale_ratio
            step = diff * min(context.time.dt / self._hover_scale_duration, 1.0)
            self._scale_ratio += step
        else:
            self._scale_ratio = target_ratio

        # Redimensionnement
        surface = self._preloaded["selected" if self.selected else "hover" if self.hovered else "default"]
        surface_rect = surface.get_rect()
        if self._last_scale_ratio != self._scale_ratio:
            new_width = int(surface_rect.width * self._scale_ratio)
            new_height = int(surface_rect.height * self._scale_ratio)
            self._surface = pygame.transform.smoothscale(surface, (new_width, new_height))
            self._last_scale_ratio = self._scale_ratio
        else:
            self._surface = surface
        self._surface_rect = self._surface.get_rect(topleft=self._rect.topleft)

    def draw(self):
        """Dessin par frame"""
        if not self._visible:
            return
        surface = context.screen.surface
        if self._panel is not None and hasattr(self._panel, 'surface'):
            surface = self._panel.surface
        surface.blit(self._surface, self._surface_rect)

    def left_click(self, up: bool = False):
        """Clic gauche"""
        if not up:
            context.ui.select(self._selection_id, self._selector_id)
            self._callback()

    def right_click(self, up: bool = False):
        """Clic droit"""
        pass