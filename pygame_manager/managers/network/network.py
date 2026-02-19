import socket
import json
import threading
import time
from collections import deque
from typing import Any, Callable

DISCOVERY_PORT = 50000
GAME_PORT = 5555
BROADCAST_INTERVAL = 1.0
LOBBY_TIMEOUT = 3.0
CLIENT_TIMEOUT = 5.0
MAX_BUFFER_SIZE = 65536
CONNECTION_TIMEOUT = 5.0


class NetworkManager:
    def __init__(self):
        """Initialise le manager réseau"""
        # ================= TCP =================
        self._server_socket = None
        self._clients: deque[socket.socket] = deque()
        self._tcp_socket: socket.socket | None = None

        self._connected = False
        self._is_host = False
        self._game_started = False

        # ================= DATA =================
        self._clients_info: dict[socket.socket, dict] = {}
        self._lock = threading.Lock()

        self._latest_data = None
        self._role_client: str | None = None
        self._role_lock = threading.Lock()

        # ================= ERROR HANDLING =================
        self._last_error: str | None = None
        self._error_callback: Callable[[str], None] | None = None
        self._connection_lost = False

        # ================= UDP =================
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._udp_sock.bind(("", DISCOVERY_PORT))
        self._udp_sock.setblocking(False)

        self._lobbies: dict[str, dict] = {}
        self._last_lobby_seen: dict[str, float] = {}

        # ================= BROADCAST =================
        self._broadcast_running = False
        self._broadcast_thread = None
        self._lobby_info = {}

        # ================= HEARTBEAT =================
        self._heartbeat_interval = 1.0
        self._heartbeat_thread = None

        # ================= CONFIG =================
        self._max_players: int = 1
        self._max_spectators: int | None = None

    def __repr__(self):
        """Représentation du manager réseau"""
        return f"<NetworkManager {'host' if self._is_host else 'client'} | {'connected' if self._connected else 'idle'}>"

    # ========================= HOST =========================
    def host(self, port: int = GAME_PORT, max_players: int = 2, max_spectators: int | None = None, **kwargs) -> bool:
        """Héberge un lobby sur le réseau local
        
        Crée un serveur TCP qui accepte les connexions entrantes et diffuse
        les informations du lobby via UDP pour la découverte automatique.

        Args:
            port: Port TCP sur lequel écouter (défaut: 5555)
            max_players: Nombre maximum de joueurs autorisés (défaut: 2)
            max_spectators: Nombre maximum de spectateurs (None = illimité)
            **kwargs: Métadonnées supplémentaires du lobby (nom, mode de jeu, etc.)

        Returns:
            True si le lobby a été créé avec succès, False sinon
        """
        try:
            self._is_host = True
            self._connected = True
            self._game_started = False
            self._connection_lost = False
            self._last_error = None

            self._max_players = max_players
            self._max_spectators = max_spectators

            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen()
            self._server_socket.setblocking(False)

            self._lobby_info = {
                **kwargs,
                "port": port,
                "players": 1,
                "spectators": 0,
                "max_players": max_players,
                "max_spectators": max_spectators,
                "status": "open",
            }

            self._start_broadcast()
            self._start_heartbeat()
            print(f"[Network] Hosting lobby {self._lobby_info}")
            return True
        except Exception as e:
            error_msg = f"Failed to host lobby: {e}"
            self._set_error(error_msg)
            return False

    # ========================= JOIN =========================
    def join(self, ip: str, port: int | None = None, timeout: float = CONNECTION_TIMEOUT) -> bool:
        """Rejoint un lobby distant en tant que client
        
        Établit une connexion TCP avec un serveur host et s'enregistre
        en tant que joueur ou spectateur selon la disponibilité.

        Args:
            ip: Adresse IP du serveur host
            port: Port TCP du serveur (défaut: 5555)
            timeout: Délai max pour établir la connexion en secondes (défaut: 5.0)

        Returns:
            True si la connexion a réussi, False sinon
        """
        try:
            port = port or GAME_PORT
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.settimeout(timeout)  # Timeout bloquant temporaire
            
            try:
                self._tcp_socket.connect((ip, port))
            except socket.timeout:
                error_msg = f"Connection timeout: {ip}:{port} did not respond"
                self._set_error(error_msg)
                self._tcp_socket.close()
                self._tcp_socket = None
                self._lobbies.pop(ip, None)
                self._last_lobby_seen.pop(ip, None)
                self._flush_udp_buffer()
                return False
            except ConnectionRefusedError:
                error_msg = f"Connection refused by {ip}:{port}"
                self._set_error(error_msg)
                self._tcp_socket.close()
                self._tcp_socket = None
                self._lobbies.pop(ip, None)
                self._last_lobby_seen.pop(ip, None)
                self._flush_udp_buffer()
                return False
            
            self._tcp_socket.setblocking(False)
            self._connected = True
            self._is_host = False
            self._connection_lost = False
            self._last_error = None
            self._stop_broadcast()

            threading.Thread(target=self._receive_loop_client, daemon=True).start()
            print(f"[Network] Joined {ip}:{port}")
            return True
            
        except Exception as e:
            error_msg = f"Failed to join {ip}:{port}: {e}"
            self._set_error(error_msg)
            if self._tcp_socket:
                try:
                    self._tcp_socket.close()
                except:
                    pass
                self._tcp_socket = None
            self._lobbies.pop(ip, None)
            self._last_lobby_seen.pop(ip, None)
            self._flush_udp_buffer()
            return False

    # ========================= DISCONNECT =========================
    def disconnect(self, infos: dict = None):
        """Ferme toutes les connexions et réinitialise l'état réseau
        
        Args:
            infos (dict, optional): dernières informations à transmettre avant arrêt de la connexion
        """
        was_connected = self._connected
        self._connected = False
        self._game_started = False
        self._broadcast_running = False

        if infos is None:
            infos = {}
        infos["type"] = "disconnect"
        infos["reason"] = "host_closed" if self._is_host else "client_closed"

        if self._is_host and was_connected:
            try:
                self.send(infos)
                time.sleep(0.1)
            except:
                pass

        if not self._is_host and was_connected and self._tcp_socket:
            try:
                self._tcp_socket.sendall((json.dumps(infos) + "\n").encode())
                time.sleep(0.05)
            except:
                pass

        if self._tcp_socket:
            try:
                self._tcp_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self._tcp_socket.close()
            except:
                pass
            self._tcp_socket = None

        if self._server_socket:
            try:
                self._server_socket.shutdown(socket.SHUT_RDWR)
            except:
                pass
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None

        with self._lock:
            for c in self._clients:
                try:
                    c.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    c.close()
                except:
                    pass
            self._clients.clear()
            self._clients_info.clear()

        with self._role_lock:
            self._role_client = None

        self._latest_data = None
        self._is_host = False
        self._lobby_info = {}

        try:
            while True:
                self._udp_sock.recvfrom(2048)
        except BlockingIOError:
            pass
        self._lobbies = {}

        if was_connected and not self._connection_lost:
            print("[Network] Disconnected normally")
    
    # ========================= ERROR HANDLING =========================
    def set_error_callback(self, callback: Callable[[str], None]):
        """Définit une fonction appelée automatiquement en cas d'erreur réseau
        
        Args:
            callback: Fonction prenant un string (message d'erreur) en paramètre
        """
        self._error_callback = callback
    
    def _set_error(self, error: str):
        """Enregistre une erreur et notifie via callback (usage interne)
        
        Args:
            error: Message d'erreur décrivant le problème
        """
        self._last_error = error
        print(f"[Network] Error: {error}")
        if self._error_callback:
            try:
                self._error_callback(error)
            except Exception as e:
                print(f"[Network] Error callback failed: {e}")
    
    def get_last_error(self) -> str | None:
        """Récupère et efface la dernière erreur enregistrée
        
        Returns:
            Message d'erreur ou None si aucune erreur
        """
        error = self._last_error
        self._last_error = None
        return error
    
    def has_error(self) -> bool:
        """Vérifie si une erreur est en attente de traitement
        
        Returns:
            True si une erreur non-récupérée existe
        """
        return self._last_error is not None
    
    def is_connection_lost(self) -> bool:
        """Vérifie si la connexion a été perdue de manière inattendue
        
        Returns:
            True si déconnexion inattendue (timeout, crash, etc.)
        """
        return self._connection_lost

    # ========================= UPDATE =========================
    def update(self, f: bool = False):
        """Met à jour l'état du réseau (à appeler régulièrement dans la game loop)
        
        Nettoie les lobbies obsolètes, reçoit les annonces UDP, et accepte
        les nouvelles connexions si on est host.

        Args:
            f: Force l'update même si non connecté (pour la découverte de lobbies)
        """
        if not f and (not self._connected or not self._is_host):
            return
        self._cleanup_lobbies()
        self._receive_lobbies()
        if self._is_host:
            self._accept_clients()

    # ========================= LOBBIES =========================
    def _flush_udp_buffer(self):
        """Vide le buffer UDP des anciens paquets (usage interne)"""
        try:
            while True:
                self._udp_sock.recvfrom(2048)
        except BlockingIOError:
            pass

    def _receive_lobbies(self):
        """Reçoit et stocke les annonces UDP de lobbies disponibles (usage interne)
        
        Lit tous les paquets UDP disponibles sans bloquer et met à jour
        le dictionnaire des lobbies découverts.
        """
        try:
            while True:
                data, addr = self._udp_sock.recvfrom(2048)
                try:
                    lobby = json.loads(data.decode())
                except json.JSONDecodeError:
                    continue
                ip = addr[0]
                self._lobbies[ip] = lobby
                self._last_lobby_seen[ip] = time.time()
        except BlockingIOError:
            pass

    def _cleanup_lobbies(self):
        """Supprime les lobbies qui n'ont pas émis depuis LOBBY_TIMEOUT (usage interne)"""
        now = time.time()
        for ip in list(self._lobbies.keys()):
            if now - self._last_lobby_seen[ip] > LOBBY_TIMEOUT:
                del self._lobbies[ip]
                del self._last_lobby_seen[ip]

    def get_lobbies(self, **filters):
        """Renvoie la liste des lobbies découverts avec filtrage optionnel
        
        Args:
            **filters: Paires clé-valeur pour filtrer les lobbies
                      (ex: status="open", max_players=2)

        Returns:
            Liste de tuples (ip, lobby_info)
        """
        self.update(f=True)
        return [
            (ip, lobby)
            for ip, lobby in self._lobbies.items()
            if all(lobby.get(k) == v for k, v in filters.items())
        ]

    # ========================= ACCEPT CLIENTS =========================
    def _accept_clients(self):
        """Accepte les nouvelles connexions TCP entrantes (usage interne, host uniquement)
        
        Gère l'attribution automatique des rôles (player/spectator), lance
        les threads de réception, et démarre la partie si le lobby est prêt.
        """
        try:
            while True:
                client, addr = self._server_socket.accept()
                client.setblocking(False)

                with self._lock:
                    num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
                    num_spectators = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

                    if num_players < self._max_players:
                        role = "player"
                    elif self._max_spectators is None or num_spectators < self._max_spectators:
                        role = "spectator"
                    else:
                        client.close()
                        continue

                    self._clients.append(client)
                    self._clients_info[client] = {
                        "role": role,
                        "last_data": None,
                        "last_seen": time.time()
                    }

                threading.Thread(target=self._receive_loop_host, args=(client,), daemon=True).start()

                try:
                    client.sendall((json.dumps({"role": role}) + "\n").encode())
                except (ConnectionResetError, BrokenPipeError, OSError):
                    with self._lock:
                        if client in self._clients:
                            self._clients.remove(client)
                        self._clients_info.pop(client, None)
                    client.close()
                    continue

                with self._lock:
                    self._lobby_info["players"] = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
                    self._lobby_info["spectators"] = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

                if not self._game_started and self.is_lobby_ready():
                    self._game_started = True
                    self.send({"type": "start_game"})
                elif self._game_started:
                    client.sendall((json.dumps({"type": "start_game"}) + "\n").encode())

                if self.is_lobby_full():
                    self._stop_broadcast()

        except BlockingIOError:
            return

    # ========================= SEND =========================
    def send(self, data: dict[str, Any]) -> bool:
        """Envoie des données à tous les clients (host) ou au serveur (client)
        
        Args:
            data: Dictionnaire sérialisable en JSON

        Returns:
            True si l'envoi a réussi, False sinon
        """
        if not self._connected:
            return False

        msg = (json.dumps(data) + "\n").encode()

        if self._is_host:
            with self._lock:
                clients = list(self._clients)

            for c in clients:
                try:
                    c.sendall(msg)
                except (ConnectionResetError, BrokenPipeError, OSError):
                    with self._lock:
                        if c in self._clients:
                            self._clients.remove(c)
                        self._clients_info.pop(c, None)
                    try:
                        c.close()
                    except:
                        pass
        else:
            # Client : envoyer au serveur
            try:
                self._tcp_socket.sendall(msg)
            except (ConnectionResetError, BrokenPipeError, OSError):
                return False

        return True

    # ========================= RECEIVE =========================
    def receive(self):
        """Récupère le prochain message reçu
        
        Pour le client: renvoie les données du host
        Pour le host: renvoie les données d'un joueur (round-robin)

        Returns:
            Dictionnaire de données ou None si aucun message
        """
        if not self._is_host:
            with self._lock:
                data = self._latest_data
                self._latest_data = None
                return data

        with self._lock:
            for _ in range(len(self._clients)):
                client = self._clients[0]
                info = self._clients_info.get(client)
                if info and info["role"] == "player" and info["last_data"] is not None:
                    data = info["last_data"]
                    info["last_data"] = None
                    self._clients.rotate(-1)
                    return data
                self._clients.rotate(-1)
        return None

    # ========================= RECEIVE LOOPS =========================
    def _receive_loop_client(self):
        """Thread de réception côté client (usage interne)
        
        Lit continuellement les données du serveur, gère le buffering,
        parse le JSON, et stocke les messages reçus. Se termine proprement
        en cas de déconnexion.
        """
        buffer = ""
        while self._connected:
            try:
                chunk = self._tcp_socket.recv(4096).decode()
                if not chunk:
                    if not self._connection_lost:
                        print("[Network] Host disconnected normally")
                    break

                buffer += chunk
                if len(buffer) > MAX_BUFFER_SIZE:
                    buffer = ""

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        msg = json.loads(line)

                        if "role" in msg:
                            with self._role_lock:
                                self._role_client = msg["role"]

                        elif msg.get("type") == "start_game":
                            self._game_started = True

                        elif msg.get("type") == "disconnect":
                            print(f"[Network] Host closing: {msg.get('reason', 'unknown')}")
                            break

                        else:
                            with self._lock:
                                self._latest_data = msg

                    except json.JSONDecodeError:
                        continue

            except BlockingIOError:
                time.sleep(0.01)
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                self._connection_lost = True
                self._set_error(f"Connection lost: {e}")
                break
            except Exception as e:
                self._connection_lost = True
                self._set_error(f"Unexpected error: {e}")
                break

        self.disconnect()

    def _receive_loop_host(self, client: socket.socket):
        """Thread de réception côté host pour un client spécifique (usage interne)
        
        Lit les données d'un client connecté, met à jour son timestamp,
        et détecte les déconnexions. Si un joueur se déconnecte, déclenche
        la fermeture du lobby.
        
        Args:
            client: Socket TCP du client à surveiller
        """
        buffer = ""
        client_role = None
        
        with self._lock:
            info = self._clients_info.get(client)
            if info:
                client_role = info["role"]

        while self._connected:
            try:
                chunk = client.recv(4096).decode()
                if not chunk:
                    print(f"[Network] Client disconnected ({client_role})")
                    
                    if client_role == "player":
                        pass 
                    break

                buffer += chunk
                if len(buffer) > MAX_BUFFER_SIZE:
                    buffer = ""

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        data = json.loads(line)
                        
                        if data.get("type") == "disconnect":
                            print(f"[Network] Client closing properly ({client_role})")
                            break
                        
                        with self._lock:
                            info = self._clients_info.get(client)
                            if info:
                                if info["role"] == "player":
                                    info["last_data"] = data
                                info["last_seen"] = time.time()
                    except json.JSONDecodeError:
                        continue

            except BlockingIOError:
                time.sleep(0.01)
            except (ConnectionResetError, BrokenPipeError, OSError) as e:
                print(f"[Network] Client connection error ({client_role}): {e}")
                
                if client_role == "player":
                    self._set_error(f"Player connection error: {e}")
                    self._connection_lost = True
                    threading.Thread(target=self.disconnect, daemon=True).start()
                break

        with self._lock:
            if client in self._clients:
                self._clients.remove(client)
            self._clients_info.pop(client, None)

        try:
            client.close()
        except:
            pass

    # ========================= HEARTBEAT / CLEANUP =========================
    def _start_heartbeat(self):
        """Démarre le thread de nettoyage périodique des clients (usage interne)"""
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _cleanup_dead_clients(self):
        """Supprime les clients qui n'ont pas répondu depuis CLIENT_TIMEOUT (usage interne)
        
        Vérifie chaque seconde si des clients sont inactifs. Si un joueur
        est détecté mort (pas de données depuis 5s), ferme le lobby.
        """
        now = time.time()
        should_disconnect = False

        with self._lock:
            for client in list(self._clients):
                info = self._clients_info.get(client)
                if info and now - info["last_seen"] > CLIENT_TIMEOUT:
                    role = info["role"]
                    print(f"[Network] Client timeout ({role})")
                    
                    try:
                        client.close()
                    except:
                        pass
                    self._clients.remove(client)
                    self._clients_info.pop(client, None)

                    if role == "player":
                        self._set_error(f"Player disconnected due to timeout")
                        should_disconnect = True
                        break

            self._lobby_info["players"] = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            self._lobby_info["spectators"] = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

        if should_disconnect:
            self._connection_lost = True
            threading.Thread(target=self.disconnect, daemon=True).start()

    def _heartbeat_loop(self):
        """Boucle infinie de nettoyage (tourne dans un thread dédié)"""
        while self._connected:
            self._cleanup_dead_clients()
            time.sleep(1)

    # ========================= BROADCAST =========================
    def _start_broadcast(self):
        """Démarre le thread de diffusion UDP du lobby (usage interne)"""
        if self._broadcast_running:
            return

        self._broadcast_running = True
        self._broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._broadcast_thread.start()

    def _broadcast_loop(self):
        """Diffuse les infos du lobby via UDP toutes les secondes (usage interne)
        
        Envoie un broadcast UDP contenant les métadonnées du lobby
        pour permettre la découverte automatique par les clients.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_addr = "255.255.255.255"

        while self._broadcast_running:
            try:
                sock.sendto(json.dumps(self._lobby_info).encode(), (broadcast_addr, DISCOVERY_PORT))
            except:
                pass
            time.sleep(1)

        sock.close()

    def _stop_broadcast(self):
        """Arrête la diffusion UDP (usage interne)"""
        self._broadcast_running = False

    # ========================= PREDICATS =========================
    def is_hosting(self) -> bool:
        """Vérifie si cette instance est le serveur host
        
        Returns:
            True si on héberge le lobby, False si on est client
        """
        return self._is_host

    def is_connected(self) -> bool:
        """Vérifie si une connexion réseau est active
        
        Returns:
            True si connecté (host ou client), False sinon
        """
        return self._connected

    def get_role(self) -> str | None:
        """Récupère le rôle attribué par le serveur (client uniquement)
        
        Returns:
            "player", "spectator", ou None si pas encore reçu
        """
        with self._role_lock:
            return self._role_client

    def is_lobby_ready(self) -> bool:
        """Vérifie si le lobby a atteint le nombre de joueurs requis (host uniquement)
        
        Returns:
            True si assez de joueurs pour démarrer
        """
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            return num_players >= self._max_players

    def is_lobby_full(self) -> bool:
        """Vérifie si le lobby est complètement plein (host uniquement)
        
        Returns:
            True si joueurs ET spectateurs sont au max
        """
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            num_spectators = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

            players_full = num_players >= self._max_players
            spectators_full = self._max_spectators is None or num_spectators >= self._max_spectators

            return players_full and spectators_full

    def is_game_started(self) -> bool:
        """Vérifie si la partie a démarré
        
        Returns:
            True si le signal start_game a été envoyé/reçu
        """
        return self._game_started

# ========================= INSTANCE =========================
network_manager = NetworkManager()