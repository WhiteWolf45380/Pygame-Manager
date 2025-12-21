import random
try:
    import pygame
except ImportError:
    raise RuntimeError("[AudioManager] requieres pygame to work normally\nTry to download it with : pip install pygame")


# -_____________________________________________- Manager Audio -_____________________________________________-
class AudioManager:
    """
    Gestionnaire audio pour Pygame

    Fonctionnalités :
    - Création et gestion de groupes de sons (channels, volume)
    - Ajout et manipulation de sons avec variations et cooldown
    - Gestion des musiques (play, stop, volume)
    - Volumes globaux et par groupe
    """

    def __init__(self):
        self.__name = "AudioManager"

        # initialisation
        pygame.mixer.init()
        pygame.mixer.set_num_channels(0)

        # groupes (=catégories) de sons
        self.__groups = {}
        self.create_group("default", channels=5, volume=1.0) # groupe par défaut

        # sons
        self.__sounds = {}

        # musiques
        self.__musics = {}
        self.__music_volume = 1.0
        self.__current_music = None

        # paramètres globaux
        self.__master_volume = 1.0
    
    # ======================================== METHODES FONCTIONNELLES ========================================
    def _raise_error(self, method: str='', text: str=''):
        """
        Raise une erreur
        """
        raise RuntimeError(f"[{self.__name}].{method} : {text}")
    
    def __str__(self):
        """
        renvoie une description textuelle du gestionnaire audio
        """
        txt = ""
        for group in self.__groups:
            txt += f"\n{group} ({self.__groups[group]['channels']} channels):"
            for sound in [s for s in self.__sounds if self.__sounds[s].get("group") == group]:
                txt += f"   - {sound}"
        return txt
    
    # ======================================== GROUPES DE SONS ========================================
    def show_groups(self):
        """
        Affiche l'ensemble des groupes
        """
        txt = ""
        for group in self.__groups:
            txt += f"- {group} : {self.__groups[group]['channels']} channels"
        print(txt)

    def create_group(self, name: str, channels: int=3, volume: float=1.0):
        """
        Crée un groupe de sons

        Args:
            - name (str) : Nom du groupe
            - channels (int) : Nombre de canaux alloués
            - volume (float) entre 0 et 1 : volume de tous les sons du groupe
        """
        if name in self.__groups:
            self._raise_error("create_group", f"Group {name} already exists")
        if not isinstance(channels, int) and channels > 0:
            self._raise_error("create_group", "Channels number must be an integer")
        if not isinstance(volume, (int, float)):
            self._raise_error("create_group", "Group's volume must be a float")
        self.__groups[name] = {"channels": channels, "volume": volume}
        self._update_partition()
    
    def set_group_channels(self, name: str, channels: int):
        """
        Modifie la taille d'un groupe de sons

        Args:
            - name (str) : Nom du groupe
            - channels (int) : Nombre de canaux alloués
        """
        if name not in self.__groups:
            self._raise_error("update_group_channels", f"Group {name} does not exist. If you want to create it, try : create_group(name: str)")
        if not isinstance(channels, int) and channels > 0:
            self._raise_error("update_group_channels", "Channels number must be an integer")
        self.__groups[name]["channels"] = channels
        self._update_partition()

    def set_group_volume(self, name: str, volume: float):
        """
        Modifie le volume d'un groupe de sons

        Args:
            - name (str) : Nom du groupe
            - volume (float) entre 0 et 1 : volume de tous les sons du groupe
        """
        if name not in self.__groups:
            self._raise_error("update_group_volume", f"Group {name} does not exist. If you want to create it, try : create_group(name: str)")
        if not isinstance(volume, (int, float)):
            self._raise_error("update_group_volume", "Group's volume must be a float")
        self.__groups[name]["volume"] = volume
    
    def delete_group(self, name: str):
        """
        Supprime un groupe de sons

        Args:
            - name (str) : Nom du groupe
        """
        if name not in self.__groups:
            self._raise_error("delete_group", f"Group {name} does not exist")
        if name == "default":
            self._raise_error("delete_group", "Group default cannot be deleted")
        self.__groups.pop(name)
        self._update_partition()
    
    def _update_partition(self):
        """
        Distribue les salons aux groupes
        """
        i = 0
        for group in self.__groups.values():
            group["first"] = i
            i = i + group["channels"]
            group["last"] = i - 1
        pygame.mixer.set_num_channels(i)

    # ======================================== SONS ========================================
    def show_sounds(self):
        """
        Affiche l'ensemble des sons
        """
        txt = ""
        for sound in self.__sounds:
            txt += f"{sound} :"
            txt += f"    - volume : {self.__sounds[sound]['volume']}"
            txt += f"    - délai : {self.__sounds[sound]['cooldown']}"
            txt += f"    - groupe : {self.__sounds[sound]['group']}\n"
        print(txt)
        
    def add_sound(self, name: str, path: str, volume: float= 1.0, cooldown: float=0.0, group: str='default'):
        """
        Ajoute un nouveau son

        Args:
            - name (str) : Nom unique du son
            - path (str) : chemin d'accès au son
            - volume (float) entre 0 et 1 : volume de tous les sons du groupe
            - cooldown (float) : délai minimal entre les utilisations du son (en secondes)
            - group (str) : le groupe auquel appartient le son
        """
        if name in self.__sounds:
            self._raise_error("create_group", f"Group {name} already exists. If you want to remove it, try : remove_sound(name: str)")
        if not isinstance(name, str):
            self._raise_error("create_group", f"Sound's name must be a string")
        if not isinstance(path, str):
            self._raise_error("create_group", f"Sound's path must be a string")
        if not isinstance(volume, (int, float)):
            self._raise_error("create_group", f"Sound's volume must be a float")
        if not isinstance(cooldown, float):
            self._raise_error("create_group", f"Sound's cooldown must be a float")
        if not group in self.__groups:
            self._raise_error(f"create_group", f"Group {group} does not exist. If you want to create it, try : create_group(name: str, channels: int)")
        self.__sounds[name] = {
            'audios': [pygame.mixer.Sound(path)],
            'volume': volume,
            'cooldown_duration': cooldown * 1000, # stockage en secondes
            'cooldown': 0,
            'group': group
        }
    
    def set_sound_add(self, name: str, path: str):
        """
        Ajoute des variations à un son

        Args:
            - name (str) : Nom du son
            - path (str) : chemin d'accès au son
        """
        if not name in self.__sounds:
            self._raise_error("update_sound_add", f"Sound {name} does not exist. If you want to create it, try : add_sound(name: str, path: str)")
        if not isinstance(path, str):
            self._raise_error("update_sound_add", "Sound's path must be a string")
        self.__sounds[name]["audios"].append(pygame.mixer.Sound(path))
    
    def set_sound_volume(self, name: str, volume: float):
        """
        Modifie le volume d'un son

        Args:
            - name (str) : Nom du son
            - volume (float) entre 0 et 1 : volume de tous les sons du groupe
        """
        if not name in self.__sounds:
            self._raise_error("update_sound_volume", f"Sound {name} does not exist. If you want to create it, try : add_sound(name: str, path: str)")
        if not isinstance(volume, (int, float)):
            self._raise_error("update_sound_volume", "Sound's volume must be an integer")
        self.__sounds[name]["volume"] = volume

    def set_sound_cooldown(self, name: str, cooldown: float):
        """
        Modifie le délai d'un son
        
        Args:
            - name (str) : Nom du son
            - cooldown (float) : délai minimal entre les utilisations du son (en secondes)
        """
        if not name in self.__sounds:
            self._raise_error("update_sound_cooldown", f"Sound {name} does not exist. If you want to create it, try : add_sound(name: str, path: str)")
        if not isinstance(cooldown, float):
            self._raise_error("update_sound_cooldown", "Sound's cooldown must be an integer")
        self.__sounds[name]["cooldown_duration"] = cooldown

    def set_sound_group(self, name: str, group: str):
        """
        Modifie le groupe d'un son

        Args:
            - name (str) : Nom du son
            - group (str) : le groupe auquel appartient le son
        """
        if not name in self.__sounds:
            self._raise_error("update_sound_group", f"Sound {name} does not exist. If you want to create it, try : add_sound(name: str, path: str)")
        if not group in self.__groups:
            self._raise_error("update_sound_group", f"Group {group} does not exist. If you want to create it, try : create_group(name: str, channels: int)")
        self.__sounds[name]["group"] = group

    def remove_sound(self, name: str):
        """
        Supprime un son

        Args:
            - name (str) : Nom du son
        """
        if not name in self.__sounds:
            self._raise_error("remove_sound", f"Sound {name} doest not exist")
        self.__sounds.pop(name)
    
    # ======================================== MUSIQUES ========================================
    def show_musics(self):
        """
        Affiche l'ensemble des musiques
        """
        txt = ""
        for music in self.__musics:
            txt += f"{music} :"
            txt += f"   - volume : {self.__musics[music]['volume']}"
        print(txt)

    def add_music(self, name: str, path: str, volume: float= 1.0):
        """
        Ajoute une nouvelle musique

        Args:
            - name (str) : Nom unique de la musique
            - path (str) : chemin d'accès à la musique
            - volume (float) : volume de la musique
        """
        if name in self.__musics:
            self._raise_error("add_music", f"Music {name} already exists. If you want to remove it, try : remove_music(name: str)")
        if not isinstance(name, str):
            self._raise_error("add_music", "Music's name must be a string")
        if not isinstance(path, str):
            self._raise_error("add_music", "Music's path must be a string")
        if not isinstance(volume, (int, float)):
            self._raise_error("add_music", "Music's volume must be a float")
        self.__musics[name] = {
            "path": path,
            "volume": volume,
        }
    
    def set_music_path(self, name: str, path: str):
        """
        Modifie le chemin d'une musique

        Args:
            - name (str) : Nom unique de la musique
            - path (str) : chemin d'accès à la musique
        """
        if not name in self.__musics:
            self._raise_error("remove_music", f"Music {name} does not exist")
        if not isinstance(path, str):
            self._raise_error("add_music", "Music's path must be a string")
        self.__musics[name]["path"] = path
    
    def set_music_volume(self, name: str, volume: float):
        """
        Modifie le volume d'une musique

        Args:
            - name (str) : Nom unique de la musique
            - volume (float) : volume de la musique
        """
        if not name in self.__musics:
            self._raise_error("remove_music", f"Music {name} does not exist")
        if not isinstance(volume, (int, float)):
            self._raise_error("add_music", "Music's volume must be a float")
        self.__musics[name]["volume"] = volume
    
    def remove_music(self, name: str):
        """
        Supprime une musique

        Args:
            - name (str) : Nom unique de la musique
        """
        if not name in self.__musics:
            self._raise_error("remove_music", f"Music {name} does not exist")
        if name == self.__current_music:
            self.stop_music()
        self.__musics.pop(name)

    # ======================================== MANIPULATION ========================================
    def _get_free_channel(self, group):
        """
        renvoie un salon libre pour le groupe demandé si possible
        """
        first, last = self.__groups[group]["first"], self.__groups[group]["last"]
        for i in range(first, last + 1):
            channel = pygame.mixer.Channel(i)
            if not channel.get_busy():
                return channel
        return None

    def play_sound(self, sound: str):
        """
        Joue un son si possible

        Args:
            - sound (str) : nom du son
        """
        if not sound in self.__sounds:
            self._raise_error("play_sound", f"No Sound named {sound}")
        if pygame.time.get_ticks() - self.__sounds[sound]["cooldown"] < self.__sounds[sound]["cooldown_duration"]:
            return
        group = self.__sounds[sound]["group"]
        channel = self._get_free_channel(group)
        if channel:
            audio = random.choice(self.__sounds[sound]["audios"])
            audio.set_volume(self.__master_volume * self.__groups[group]["volume"] * self.__sounds[sound]["volume"])
            channel.play(audio)
            print(channel)
            self.__sounds[sound]["cooldown"] = pygame.time.get_ticks()
        else:
            print(f"[AudioManager].play_sound : No free channel for {group} sound {sound}")

    def stop_sounds(self):
        """
        Arrête l'ensemble des sons joués
        """
        pygame.mixer.stop()

    def play_music(self, name: str, loop: bool=True, fade_ms: float=0):
        """
        Joue une musique

        Args:
            - name (str) : nom de la musique
            - loop (bool) : répétition de la musique
            - fade_ms (float) : fondu en ouverture en millisecondes
        """
        if not name in self.__musics:
            self._raise_error("play_music", f"Music {name} doest not exist. If you want to create it, try : create_music(name: str, path: str)")
        pygame.mixer.music.load(self.__musics[name]["path"])
        pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
        self.__current_music = name
        self._update_volumes()

    def stop_music(self, fade_ms: float=0):
        """
        Arrête la musique jouée

        Args:
            - fade_ms : fondu en fermeture en millisecondes
        """
        if fade_ms == 0:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.fadeout(fade_ms)

    def update_master_volume(self, volume: float):
        """
        Modifie le volume général

        Args:
            - volume (float) : volume général entre 0 et 1
        """
        if not isinstance(volume, (int, float)):
            self._raise_error("set_master_volume", "Master volume must be a float")
        self.__master_volume = volume
        self._update_volumes()

    def update_music_volume(self, volume: float):
        """
        Modifie le volume musical

        Args:
            - volume (float) : volume musical entre 0 et 1
        """
        if not isinstance(volume, (int, float)):
            self._raise_error("set_music_volume", "Music's volume must be a float")
        self.__music_volume = volume
        self._update_volumes()
    
    def _update_volumes(self):
        """
        Met à jour le volume de la musique
        """
        if self.__current_music is None:
            return
        pygame.mixer.music.set_volume(self.__master_volume * self.__music_volume * self.__musics[self.__current_music]["volume"])


"""
Exemple d'utilisation :

import time
from pygame_managers import AudioManager

# Initialisation du gestionnaire audio
audio = AudioManager()

# Création de groupes
audio.create_group("ui", channels=2, volume=1.0) # groupe pour l'ui avec deux canaux disponibles et un volume maximal
audio.create_group("sfx", channels=4, volume=0.8) # groupe pour le sfx avec quatre canaux disponibles et un volume de 80%

# Ajout de sons
audio.add_sound("shoot", "shoot.mp3", volume=1.0, cooldown=0.5, group="ui") # un son de tire avec volume maximal, délai d'une demi seconde et appartenant au groupe ui
audio.add_sound("footstep", "footstep.mp3", volume=0.6, cooldown=0.2, group="sfx") # un son de pas de volume 60% , avec un délai de 0.2s et appartenant au groupe sfx

# Jouer un son
audio.play_sound("shoot") # activation du son de tire
time.sleep(1)
audio.play_sound("footstep") # activation du son de pas

# Ajouter de la musique
audio.add_music("title_screen", "title_screen.mp3", volume=0.7) # ajout d'une musique d'écran titre de volume 70%

# Jouer la musique en boucle
audio.play_music("title_screen", loop=True, fade_ms=500) # activation de la musique avec répétition et fondu en ouverture de 0.5s

# Modifier les volumes
audio.update_master_volume(0.8) # volume global à 80%
audio.update_music_volume(0.5) # volume musical à 50%
audio.set_group_volume('ui', 0.4) # volume du groupe UI à 40%

# Arrêter tous les sons et la musique
audio.stop_sounds()
audio.stop_music(fade_ms=1000)

"""