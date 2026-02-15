# ======================================== IMPORTS ========================================
from ._core import *

# ======================================== OBJET ========================================
class MessageObject:
    """
    Object de l'interface : Message système
    """
    def __init__(
            self,
            text: str,
            sender: str = None,
            x: Real = None,
            y: Real = None,
            anchor: str = "midtop",
            
            font: pygame.font.Font | str = "arial",
            font_size: int = 16,
            font_color: pygame.Color = (200, 200, 200, 255),
            sender_color: pygame.Color = (100, 150, 255, 255),
            
            background: pygame.Color = (20, 20, 20, 200),
            padding: int = 8,
            
            lifetime: float = 3.0,
            fade_duration: float = 0.5,
            
            system_message: bool = False,
            
            auto: bool = True,
            panel: object = None,
            zorder: int = 1000,
        ):
        """
        Args:
            text (str): message à afficher
            sender (str, optional): expéditeur du message (sera affiché comme [Sender])
            x (Real, optional): coordonnée x (default: centerx de l'écran)
            y (Real, optional): coordonnée y (default: 50px du haut)
            anchor (str, optional): point d'ancrage ("topleft", "center", "midtop", etc.)
            
            font (Font, optional): police du texte
            font_size (int, optional): taille de la police
            font_color (Color, optional): couleur du message
            sender_color (Color, optional): couleur du sender
            
            background (Color, optional): couleur de fond
            padding (int, optional): espacement interne
            
            lifetime (float, optional): durée d'affichage en secondes (default: 3.0)
            fade_duration (float, optional): durée du fondu de sortie (default: 0.5)
            
            system_message (bool, optional): si True, utilise blit_last pour afficher au-dessus de tout
            
            auto (bool, optional): enregistrement automatique pour draw
            panel (object, optional): panel maître
            zorder (int, optional): ordre de rendu
        """
        # Vérifications
        if not isinstance(text, str): _raise_error(self, '__init__', 'Invalid text argument')
        if sender is not None and not isinstance(sender, str): _raise_error(self, '__init__', 'Invalid sender argument')
        if x is not None and not isinstance(x, Real): _raise_error(self, '__init__', 'Invalid x argument')
        if y is not None and not isinstance(y, Real): _raise_error(self, '__init__', 'Invalid y argument')
        if not isinstance(anchor, str): _raise_error(self, '__init__', 'Invalid anchor argument')
        if not isinstance(font_size, int): _raise_error(self, '__init__', 'Invalid font_size argument')
        font_color = _to_color(font_color, method='__init__')
        sender_color = _to_color(sender_color, method='__init__')
        if background is not None: background = _to_color(background)
        if not isinstance(padding, int): _raise_error(self, '__init__', 'Invalid padding argument')
        if not isinstance(lifetime, (int, float)) or lifetime <= 0: _raise_error(self, '__init__', 'Invalid lifetime argument')
        if not isinstance(fade_duration, (int, float)) or fade_duration < 0: _raise_error(self, '__init__', 'Invalid fade_duration argument')
        if not isinstance(system_message, bool): _raise_error(self, '__init__', 'Invalid system_message argument')
        if not isinstance(auto, bool): _raise_error(self, '__init__', 'Invalid auto argument')
        if panel is not None and not isinstance(panel, str): _raise_error(self, '__init__', 'Invalid panel argument')
        if not isinstance(zorder, int): _raise_error(self, '__init__', 'Invalid zorder argument')
        
        # Auto-registration
        if auto:
            context.ui._append(self)
        
        # Position par défaut (centre-haut de l'écran)
        if x is None:
            x = context.screen.centerx if panel is None else panel.centerx
        if y is None:
            y = context.screen.height * 0.1 if panel is None else panel.height * 0.1
        
        # Stockage des paramètres
        self._text = text
        self._sender = sender
        self._x = x
        self._y = y
        self._anchor = anchor
        self._font = font
        self._font_size = font_size
        self._font_color = font_color
        self._sender_color = sender_color
        self._background = background
        self._padding = padding
        self._panel = context.panels[panel] if isinstance(panel, str) else (panel if panel in context.panels else None)
        self._zorder = zorder
        self._visible = True
        self._system_message = system_message
        
        # Système de durée de vie
        self._lifetime = lifetime
        self._fade_duration = fade_duration
        self._elapsed_time = 0.0
        self._fading = False
        self._initial_alpha = 255
        self._current_alpha = 255
        
        # Création des TextObjects
        self._text_objects = []
        self._background_rect = None
        self._render()
    
    # ======================================== RENDU ========================================
    def _render(self):
        """Génère les TextObjects pour le message"""
        for obj in self._text_objects:
            obj.kill()
        self._text_objects.clear()
        
        auto_register = not self._system_message
        target_panel = None if self._system_message else self._panel
        
        if self._sender:
            sender_text = context.ui.Text(
                x=self._x + self._padding,
                y=self._y + self._padding,
                text=f"[{self._sender}] ",
                anchor=self._anchor,
                font=self._font,
                font_size=self._font_size,
                font_color=self._sender_color,
                bold=True,
                auto=auto_register,
                panel=target_panel,
                zorder=self._zorder + 1
            )
            self._text_objects.append(sender_text)
            
            sender_width = sender_text.rect.width
            message_x = self._x + self._padding + sender_width
        else:
            message_x = self._x + self._padding
        
        message_text = context.ui.Text(
            x=message_x,
            y=self._y + self._padding,
            text=self._text,
            anchor="topleft" if self._sender else self._anchor,
            font=self._font,
            font_size=self._font_size,
            font_color=self._font_color,
            auto=auto_register,
            panel=target_panel,
            zorder=self._zorder + 1
        )
        self._text_objects.append(message_text)
        
        if self._text_objects:
            combined_rect = self._text_objects[0].rect.copy()
            for obj in self._text_objects[1:]:
                combined_rect = combined_rect.union(obj.rect)
            
            self._background_rect = pygame.Rect(
                combined_rect.x - self._padding,
                combined_rect.y - self._padding,
                combined_rect.width + self._padding * 2,
                combined_rect.height + self._padding * 2
            )
    
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
    def text(self) -> str:
        """Renvoie le texte"""
        return self._text
    
    @property
    def sender(self) -> str:
        """Renvoie le sender"""
        return self._sender
    
    @property
    def rect(self) -> pygame.Rect:
        """Renvoie le rect pygame du message complet"""
        return self._background_rect.copy() if self._background_rect else pygame.Rect(self._x, self._y, 0, 0)
    
    # ======================================== SETTERS ========================================
    @zorder.setter
    def zorder(self, value: int):
        """Fixe le zorder"""
        if not isinstance(value, int):
            _raise_error(self, 'set_zorder', 'Invalid zorder argument')
        self._zorder = value
        for obj in self._text_objects:
            obj.zorder = value + 1
    
    @visible.setter
    def visible(self, value: bool):
        """Fixe la visibilité"""
        if not isinstance(value, bool):
            _raise_error(self, 'set_visible', 'Invalid value argument')
        self._visible = value
        for obj in self._text_objects:
            obj.visible = value
    
    @text.setter
    def text(self, value: str):
        """Fixe le texte et re-render"""
        if not isinstance(value, str):
            _raise_error(self, 'set_text', 'Invalid value argument')
        self._text = value
        self._render()
    
    @sender.setter
    def sender(self, value: str):
        """Fixe le sender et re-render"""
        if value is not None and not isinstance(value, str):
            _raise_error(self, 'set_sender', 'Invalid value argument')
        self._sender = value
        self._render()
    
    def set_position(self, x: Real, y: Real):
        """Modifie la position"""
        self._x = x
        self._y = y
        self._render()
    
    def set_alpha(self, alpha: int):
        """Modifie l'opacité"""
        if not isinstance(alpha, int) or not 0 <= alpha <= 255:
            _raise_error(self, 'set_alpha', 'Invalid alpha argument')
        for obj in self._text_objects:
            obj.set_alpha(alpha)
    
    # ======================================== PREDICATS ========================================
    def collidemouse(self) -> bool:
        """Vérifie que la souris soit sur le message"""
        if self._panel is not None:
            mouse_pos = self._panel.mouse_pos
        else:
            mouse_pos = context.mouse.get_pos()
        return self._background_rect.collidepoint(mouse_pos) if self._background_rect else False
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def kill(self):
        """Détruit l'objet"""
        for obj in self._text_objects:
            obj.kill()
        self._text_objects.clear()
        
        if self._system_message and self in context.ui._system_messages:
            context.ui._system_messages.remove(self)
            context.ui._reposition_messages()
        else:
            context.ui._remove(self)
    
    def reset(self):
        """Supprime les effets"""
        for obj in self._text_objects:
            obj.reset()
    
    def scale(self, ratio: Real):
        """Redimensionne l'objet"""
        if not isinstance(ratio, Real) or not 0.0 < ratio <= 1.0:
            _raise_error(self, 'scale', 'Invalid ratio_argument')
        for obj in self._text_objects:
            obj.scale(ratio)
        self._render()
    
    def blink(self, alpha_min: int = 0, alpha_max: int = 255, duration: float | None = None, speed: float = 1.0):
        """Fait clignoter le message"""
        for obj in self._text_objects:
            obj.blink(alpha_min, alpha_max, duration, speed)
    
    def stop_blink(self):
        """Met fin au clignotement"""
        for obj in self._text_objects:
            obj.stop_blink()
    
    # ======================================== ACTUALISATION ========================================
    def update(self):
        """Actualisation par frame"""
        if not self._visible:
            return
        
        self._elapsed_time += context.time.dt
        
        if not self._fading and self._elapsed_time >= (self._lifetime - self._fade_duration):
            self._fading = True
        
        if self._fading:
            fade_elapsed = self._elapsed_time - (self._lifetime - self._fade_duration)
            fade_progress = min(1.0, fade_elapsed / self._fade_duration)
            self._current_alpha = int(self._initial_alpha * (1.0 - fade_progress))
            self.set_alpha(self._current_alpha)
        
        if self._elapsed_time >= self._lifetime:
            self.kill()
            return
        
        for obj in self._text_objects:
            obj.update()
    
    # ======================================== AFFICHAGE ========================================
    def draw(self):
        """Dessin par frame"""
        if not self._visible or not self._background_rect:
            return
        
        if self._system_message:
            surface = context.screen.surface
            
            temp_surface = pygame.Surface((self._background_rect.width, self._background_rect.height), pygame.SRCALPHA)
            
            if self._background:
                temp_surface.fill(self._background)
            
            for obj in self._text_objects:
                if obj._surface:
                    offset_x = obj._rect.x - self._background_rect.x
                    offset_y = obj._rect.y - self._background_rect.y
                    if obj._shadow_surface:
                        temp_surface.blit(obj._shadow_surface, (offset_x + obj._shadow_offset, offset_y + obj._shadow_offset))
                    temp_surface.blit(obj._surface, (offset_x, offset_y))
            
            context.screen.blit_last(temp_surface, self._background_rect)
        else:
            surface = context.screen.surface
            if self._panel is not None and hasattr(self._panel, 'surface'):
                surface = self._panel.surface
            
            if self._background:
                background_surface = pygame.Surface((self._background_rect.width, self._background_rect.height), pygame.SRCALPHA)
                background_surface.fill(self._background)
                surface.blit(background_surface, self._background_rect)
            
            for obj in self._text_objects:
                obj.draw()
    
    # ======================================== HANDLERS ========================================
    def left_click(self, up: bool = False):
        """Clic gauche"""
        pass
    
    def right_click(self, up: bool = False):
        """Clic droit"""
        pass