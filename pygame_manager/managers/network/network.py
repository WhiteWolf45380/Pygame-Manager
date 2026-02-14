import socket
import json
import threading
import time
from collections import deque
from typing import Any

DISCOVERY_PORT = 50000
GAME_PORT = 5555
BROADCAST_INTERVAL = 1.0
LOBBY_TIMEOUT = 3.0
CLIENT_TIMEOUT = 5.0
MAX_BUFFER_SIZE = 65536


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

        self._latest_data = None                # client side
        self._role_client: str | None = None  # role côté client
        self._role_lock = threading.Lock()    # lock pour _role_client

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
        """Représentation du manager"""
        return f"<NetworkManager {'host' if self._is_host else 'client'} | {'connected' if self._connected else 'idle'}>"

    # ========================= HOST =========================
    def host(self, port: int = GAME_PORT, max_players: int = 2, max_spectators: int | None = None, **kwargs) -> bool:
        """Héberge un lobby

        Args:
            port: Port TCP pour le lobby
            max_players: Nombre maximum de joueurs
            max_spectators: Nombre maximum de spectateurs
        """
        try:
            self._is_host = True
            self._connected = True
            self._game_started = False

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
            print(f"[Network] Host error: {e}")
            return False

    # ========================= JOIN =========================
    def join(self, ip: str, port: int | None = None) -> bool:
        """Rejoint un lobby

        Args:
            ip: Adresse IP du host
            port: Port TCP du host
        """
        try:
            port = port or GAME_PORT
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.connect((ip, port))
            self._tcp_socket.setblocking(False)

            self._connected = True
            self._is_host = False
            self._stop_broadcast()

            threading.Thread(target=self._receive_loop_client, daemon=True).start()
            print(f"[Network] Joined {ip}:{port}")
            return True
        except Exception as e:
            print(f"[Network] Join error: {e}")
            return False

    # ========================= DISCONNECT =========================
    def disconnect(self):
        """Met fin à la connexion"""
        self._connected = False
        self._game_started = False
        self._broadcast_running = False

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

    # ========================= UPDATE =========================
    def update(self, f: bool = False):
        """Met à jour l'état du réseau

        Args:
            f: Forcer la mise à jour
        """
        if not f and (not self._connected or not self._is_host):
            return
        self._cleanup_lobbies()
        self._receive_lobbies()
        if self._is_host:
            self._accept_clients()

    # ========================= LOBBIES =========================
    def _receive_lobbies(self):
        """Récupère les lobbies présents"""
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
        """Nettoie les lobbies"""
        now = time.time()
        for ip in list(self._lobbies.keys()):
            if now - self._last_lobby_seen[ip] > LOBBY_TIMEOUT:
                del self._lobbies[ip]
                del self._last_lobby_seen[ip]

    def get_lobbies(self, **filters):
        """Renvoie les lobbies

        Args:
            filters: filtres à appliquer
        """
        self.update(f=True)
        return [
            (ip, lobby)
            for ip, lobby in self._lobbies.items()
            if all(lobby.get(k) == v for k, v in filters.items())
        ]

    # ========================= ACCEPT CLIENTS =========================
    def _accept_clients(self):
        """Accepte les clients entrants"""
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
        """Envoie un message

        Args:
            data: dictionnaire à envoyer
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
            try:
                self._tcp_socket.sendall(msg)
            except (ConnectionResetError, BrokenPipeError, OSError):
                return False

        return True

    # ========================= RECEIVE =========================
    def receive(self):
        """Reçoit un message"""
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
        """Boucle de réception côté client"""
        buffer = ""
        while self._connected:
            try:
                chunk = self._tcp_socket.recv(4096).decode()
                if not chunk:
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

                        else:
                            with self._lock:
                                self._latest_data = msg

                    except json.JSONDecodeError:
                        continue

            except BlockingIOError:
                time.sleep(0.01)
            except (ConnectionResetError, BrokenPipeError, OSError):
                break

        self.disconnect()

    def _receive_loop_host(self, client: socket.socket):
        """Boucle de réception côté hébergeur"""
        buffer = ""

        while self._connected:
            try:
                chunk = client.recv(4096).decode()
                if not chunk:
                    break

                buffer += chunk
                if len(buffer) > MAX_BUFFER_SIZE:
                    buffer = ""

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    try:
                        data = json.loads(line)
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
            except (ConnectionResetError, BrokenPipeError, OSError):
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
        """Démarre le nettoyage des clients"""
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop,daemon=True)
        self._heartbeat_thread.start()

    def _cleanup_dead_clients(self):
        """Supprime les clients morts"""
        now = time.time()
        should_disconnect = False

        with self._lock:
            for client in list(self._clients):
                info = self._clients_info.get(client)
                if info and now - info["last_seen"] > CLIENT_TIMEOUT:
                    role = info["role"]
                    try:
                        client.close()
                    except:
                        pass
                    self._clients.remove(client)
                    self._clients_info.pop(client, None)

                    if role == "player":
                        should_disconnect = True
                        break

            self._lobby_info["players"] = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            self._lobby_info["spectators"] = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

        if should_disconnect:
            threading.Thread(target=self.disconnect, daemon=True).start()

    def _heartbeat_loop(self):
        """Boucle du heartbeat"""
        while self._connected:
            self._cleanup_dead_clients()
            time.sleep(1)

    # ========================= BROADCAST =========================
    def _start_broadcast(self):
        """Démarre la diffusion UDP"""
        if self._broadcast_running:
            return

        self._broadcast_running = True
        self._broadcast_thread = threading.Thread(target=self._broadcast_loop,daemon=True)
        self._broadcast_thread.start()

    def _broadcast_loop(self):
        """Boucle de diffusion UDP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_addr = "255.255.255.255"

        while self._broadcast_running:
            try:
                sock.sendto(json.dumps(self._lobby_info).encode(),(broadcast_addr, DISCOVERY_PORT))
            except:
                pass
            time.sleep(1)

        sock.close()

    def _stop_broadcast(self):
        """Arrête la diffusion UDP"""
        self._broadcast_running = False

    # ========================= PREDICATS =========================
    def is_hosting(self) -> bool:
        """Vérifie si la machine est host"""
        return self._is_host

    def is_connected(self) -> bool:
        """Vérifie si la connexion est active"""
        return self._connected

    def get_role(self) -> str | None:
        """Récupère le rôle du client"""
        with self._role_lock:
            return self._role_client

    def is_lobby_ready(self) -> bool:
        """Vérifie si le lobby est prêt"""
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            return num_players >= self._max_players

    def is_lobby_full(self) -> bool:
        """Vérifie si le lobby est plein"""
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            num_spectators = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

            players_full = num_players >= self._max_players
            spectators_full = self._max_spectators is None or num_spectators >= self._max_spectators

            return players_full and spectators_full

    def is_game_started(self) -> bool:
        """Vérifie si la partie est lancée"""
        return self._game_started

# ========================= INSTANCE =========================
network_manager = NetworkManager()