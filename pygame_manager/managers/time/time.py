try:
    import pygame
except ImportError:
    raise RuntimeError("[TimeManager] requieres pygame to work normally\nTry to download it with : pip install pygame")


# ======================================== GESTIONNAIRE ========================================
class TimeManager:
    """
    Gestionnaire pygame du temps et des performances

    Fonctionnalités:
        gérer les performances et la vitesse d'éxécution
        adapter les valeurs au temps
        adapter les animations au temps
    """
    def __init__(self, max_fps: int=60):
        # clock pygame
        self._clock = pygame.time.Clock()

        # paramètres
        self._dt = 0.0  # temps écoulé depuis la dernière boucle (en secondes)
        self._current_fps = 0.0 # nombre actuel de fps (en frames)
        self._max_fps = max_fps # nombre maximal de fps
        self._fps_buffer = [] # buffer de fps pour une moyenne lissée
        self._time_scale = 1.0 # vitesse d'éxécution du jeu
        self._frame_count = 0 # nombre de frames écoulées

        # stocke les débuts d’animations
        self._start_times = {}
    
    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str='', text: str=''):
        """
        Raise une erreur
        """
        raise RuntimeError(f"[{self.__class__.__name__}].{method} : {text}")
    
    # ======================================== GETTERS ========================================
    def get_ticks(self):
        """
        Renvoie le temps écoulé depuis le début du programme (en ms)
        """
        return pygame.time.get_ticks()
    
    @property
    def frame_count(self):
        """
        Renvoie le nombre de frames écoulées depuis le début du programme
        """
        return self._frame_count

    def get_dt(self):
        """
        Renvoie le delta time (temps écoulé depuis la dernière frame) en secondes
        """
        return self._dt
    
    @property
    def dt(self):
        """
        Renvoie le delta time (temps écoulé depuis la dernière frame) en secondes
        """
        return self._dt
    
    def get_fps(self):
        """
        Renvoie le nombre actuel de frames par seconde
        """
        return self._current_fps
    
    @property
    def fps(self):
        """
        Renvoie le nombre actuel de frames par seconde
        """
        return self._current_fps
    
    def get_smoothfps(self):
        """
        Renvoie le nombre lissé de frames par seconde
        """
        if len(self._fps_buffer) == 0:
            return self._current_fps
        return round(sum(self._fps_buffer) / len(self._fps_buffer))
    
    @property
    def smoothfps(self):
        """
        Renvoie le nombre lissé de frames par seconde
        """
        if len(self._fps_buffer) == 0:
            return self._current_fps
        return round(sum(self._fps_buffer) / len(self._fps_buffer))
    
    def get_fps_limit(self):
        """
        Renvoie la limite de frames par seconde
        """
        return self._max_fps
    
    @property
    def fps_limits(self):
        """
        Renvoie la limite de frames par seconde
        """
        return self._max_fps
    
    # ======================================== SETTERS ========================================
    def set_fps_limit(self, n: int):
        """
        Fixe une limite de fps

        Args:
            n (int) : nombre de fps
        """
        if not isinstance(n, int):
            self._raise_error("set_fps_limit", "fps limit must be an integer")
        self._max_fps = n

    def set_time_scale(self, t: float):
        """
        modifie l'écoulement du temps pour des effets d'accélération ou de slow-motion

        Args:
            t (float) : le coefficient d'écoulement du temps
        """
        if not isinstance(t, (int, float)):
            self._raise_error("set_time_scale", "Time coefficient must be a float")
        if t < 0:
            self._raise_error("set_time_scale", "Time coefficient must be >= 0")
        self._time_scale = t
    
    # ======================================== METHODES DYNAMIQUES ========================================
    def tick(self) -> float:
        """
        À appeler à chaque frame, en premier
        """
        # frame actuelle
        self._frame_count += 1

        # temps brut écoulé depuis la dernière frame
        raw_dt = (self._clock.tick(self._max_fps)) / 1000.0

        # clamp pour éviter les pics de dt trop grands ou nuls
        self._dt = max(0.001, min(raw_dt, 0.07)) * self._time_scale # entre 15 et 1000 fps

        # calcul des fps
        if self._dt > 0:
            self._current_fps = round(1.0 / self._dt)
            self._fps_buffer.append(self._current_fps)
            if len(self._fps_buffer) > 30:
                self._fps_buffer.pop(0)

        return self._dt

    def scale_value(self, value_per_second: float) -> float:
        """
        Adapte une valeur dépendante du temps au framerate (ex: vitesse)

        Args:
            value_per_second : nombre par seconde voulu
        """
        return value_per_second * self._dt
    
    def pause(self):
        """
        Met toutes les animations et tous les mouvements en suspend
        """
        self.set_time_scale(0)
    
    def unpause(self):
        """
        Enlève la pause
        """
        self.set_time_scale(1)

    def get_frame(self, anim_id: str, anim_duration: float, frame_count: int, loop: bool=False, start: bool=False, forced_frame: int=None) -> tuple[int, bool]:
        """
        Retourne la frame à afficher pour une animation donnée

        Args:
            anim_id (str) : nom unique de l'animation
            anim_duration (float) : durée de l'animation en secondes
            frame_count (int) : nombre total de frames de l'animation
            loop (bool) : répétition de l'animation lorsqu'elle se termine
            start (bool) : forcer le retour à la première frame
            forced_frame (int) : forcer le saut vers une frame donnée
        """
        # erreur d'entrée
        if anim_duration <= 0 or frame_count <= 0:
            return 0, False
        
        # démarrage d'une nouvelle animation
        if anim_id not in self._start_times or start:
            self._start_times[anim_id] = {"time": 0.0}

        # récupération des données de l'animation
        anim_data = self._start_times[anim_id]

        # calcul de la durée d'une frame
        frame_duration = anim_duration / frame_count

        if forced_frame is None:
            anim_data["time"] += self._dt # incrémentation temporelle
        else:
            if not isinstance(forced_frame, int) or forced_frame >= frame_count:
                self._raise_error("get_frame", "Forced_frame must be an integer between 0 et frames_count - 1")
            anim_data["time"] = forced_frame * frame_duration # démarrage directement à une frame donnée

        # durée écoulée depuis le début de l'animation
        elapsed = anim_data["time"]

        finished = False
        if loop:
            cycle_time = elapsed % anim_duration # boucle
        else:
            cycle_time = min(elapsed, anim_duration) # limite à la durée max
            if elapsed >= anim_duration:
                finished = True
                self._clear_anim(anim_id) # fin de l'animation

        progress = cycle_time / anim_duration # calcul du progrès
        frame_index = int(progress * frame_count) # calcul de la frame actuelle

        return min(frame_index, frame_count - 1), finished

    def _clear_anim(self, anim_id: str):
        """
        Oublie complètement une animation
        """
        self._start_times.pop(anim_id, None)


# ======================================== INSTANCE ========================================
time_manager = TimeManager()


"""
Exemple d'utilisation :

import pygame
pygame.init()

time = TimeManager(max_fps=60)

# à appeler une fois par frame
time.tick()

# récupérer les infos de temps
dt = time.get_dt()
fps = time.get_fps()

# adapter une valeur au temps (ex: déplacement)
movement = time.scale_value(200)  # 200 unités par seconde

# pause / reprise
time.pause()
time.unpause()

# gestion d'animation
frame, finished = time.get_frame(
    anim_id="run",
    anim_duration=1.0,
    frame_count=6
)

# animation en boucle
frame, finished = time.get_frame(
    anim_id="idle",
    anim_duration=0.8,
    frame_count=4,
    loop=True
)

# forcer une frame précise
frame, finished = time.get_frame(
    anim_id="attack",
    anim_duration=0.6,
    frame_count=5,
    forced_frame=2
)

# redémarrer une animation
frame, finished = time.get_frame(
    anim_id="jump",
    anim_duration=0.7,
    frame_count=5,
    start=True
)
"""