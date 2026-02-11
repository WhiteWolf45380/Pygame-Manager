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
        """Renvoie une représentation du réseau"""
        return f"<NetworkManager {'host' if self._is_host else 'client'} | {'connected' if self._connected else 'idle'}>"

    # ========================= HOST =========================
    def host(self, port: int = GAME_PORT, max_players: int = 2, max_spectators: int | None = None, **kwargs) -> bool:
        """Héberge un lobby"""
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
        """Rejoint un lobby"""
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

        if self._broadcast_thread:
            self._broadcast_thread.join(timeout=2)
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2)

        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except OSError:
                pass
            self._tcp_socket = None

        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
            self._server_socket = None

        with self._lock:
            for c in self._clients:
                try:
                    c.close()
                except OSError:
                    pass
            self._clients.clear()
            self._clients_info.clear()

        with self._role_lock:
            self._role_client = None

        self._latest_data = None
        self._is_host = False
        self._lobby_info = {}
        print("[Network] Disconnected cleanly")

    # ========================= UPDATE =========================
    def update(self):
        """Récupère les lobbies (client) et Envoie sa présence (host)"""
        self._receive_lobbies()
        self._cleanup_lobbies()
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
        """Renvoie la liste des lobbies"""
        return [
            (ip, lobby)
            for ip, lobby in self._lobbies.items()
            if all(lobby.get(k) == v for k, v in filters.items())
        ]

    # ========================= ACCEPT CLIENTS =========================
    def _accept_clients(self):
        """Accepte la connexion d'un client"""
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
                    self._clients_info[client] = {"role": role, "last_data": None, "last_seen": time.time()}

                threading.Thread(target=self._receive_loop_host, args=(client,), daemon=True).start()

                try:
                    client.sendall((json.dumps({"role": role}) + "\n").encode())
                except (ConnectionResetError, BrokenPipeError):
                    print(f"[Network] Failed to send role to {addr}, closing")
                    with self._lock:
                        client.close()
                        if client in self._clients:
                            self._clients.remove(client)
                        self._clients_info.pop(client, None)
                    continue

                with self._lock:
                    self._lobby_info["players"] = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
                    self._lobby_info["spectators"] = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")

                if not self._game_started and self.is_lobby_ready():
                    self._game_started = True
                    self.send({"type": "start_game"})
                elif self._game_started:
                    client.send({"type": "start_game"})

                print(f"[Network] Client connected: {addr} as {role}")

        except BlockingIOError:
            return

    # ========================= SEND =========================
    def send(self, data: dict[str, Any]) -> bool:
        """Envoie un dictionnaire de données"""
        msg = (json.dumps(data) + "\n").encode()
        if self._is_host:
            with self._lock:
                clients = list(self._clients)
            for c in clients:
                try:
                    c.sendall(msg)
                except (ConnectionResetError, BrokenPipeError) as e:
                    print(f"[Network] Warning: client {c} send failed ({e})")
        else:
            try:
                self._tcp_socket.sendall(msg)
            except (ConnectionResetError, BrokenPipeError) as e:
                print(f"[Network] Client send error: {e}")
                return False
        return True

    # ========================= RECEIVE =========================
    def receive(self):
        """Récupère un dictionnaire de données"""
        if not self._is_host:
            with self._lock:
                data = self._latest_data
                self._latest_data = None
                return data

        with self._lock:
            if not self._clients:
                return None

            for _ in range(len(self._clients)):
                client = self._clients[0]
                info = self._clients_info.get(client)
                if info and info["role"] == "player" and info["last_data"] is not None:
                    data = info["last_data"]
                    info["last_data"] = None
                    self._clients.rotate(-1)
                    return data
                else:
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
                    print("[Network] Warning: client buffer overflow, clearing buffer")
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
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as e:
                print(f"[Network] Client receive error: {e}")
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
                    print(f"[Network] Warning: client {client} buffer overflow, clearing buffer")
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
                                else:
                                    print(f"[Network] Spectator {client} tried to send data → ignored")
                                info["last_seen"] = time.time()
                    except json.JSONDecodeError:
                        continue
            except BlockingIOError:
                time.sleep(0.01)
            except (ConnectionResetError, BrokenPipeError):
                break
            except Exception as e:
                print(f"[Network] Host receive error: {e}")
                break
        print("[Network] Client disconnected (lazy)")

    # ========================= HEARTBEAT / CLEANUP =========================
    def _start_heartbeat(self):
        """Démarre le nettoyage des cleints inactifs"""
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _cleanup_dead_clients(self):
        """Coupe la connexion avec les clients inactifs"""
        now = time.time()
        should_disconnect = False
        
        with self._lock:
            for client in list(self._clients):
                info = self._clients_info.get(client)
                if info and now - info["last_seen"] > CLIENT_TIMEOUT:
                    role = info["role"]
                    try:
                        client.close()
                    except OSError:
                        pass
                    self._clients.remove(client)
                    self._clients_info.pop(client, None)
                    if role == "player":
                        print("[Network] Player disconnected → closing session")
                        should_disconnect = True
                        break
            if not should_disconnect:
                self._lobby_info["players"] = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
                self._lobby_info["spectators"] = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")
        
        if should_disconnect:
            self.disconnect()

    def _heartbeat_loop(self):
        """Boucle de nettoyage"""
        while self._connected:
            self._cleanup_dead_clients()
            time.sleep(self._heartbeat_interval)

    # ========================= BROADCAST =========================
    def _start_broadcast(self):
        """Démarre la diffusion UDP"""
        self._broadcast_running = True
        self._broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._broadcast_thread.start()

    def _broadcast_loop(self):
        """Boucle de diffusion UDP"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_addr = "255.255.255.255"
        while self._broadcast_running:
            sock.sendto(json.dumps(self._lobby_info).encode(), (broadcast_addr, DISCOVERY_PORT))
            time.sleep(BROADCAST_INTERVAL)
        sock.close()

    def _stop_broadcast(self):
        """Arrête la diffusion UDP"""
        self._broadcast_running = False

    # ========================= PREDICATS =========================
    def is_hosting(self) -> bool:
        """Vérifie que la machine soit l'hébergeur"""
        return self._is_host

    def is_connected(self) -> bool:
        """Vérifie que la connexion soit active"""
        return self._connected

    def is_player(self, client: socket.socket) -> bool:
        """Vérifie que le client soit un joueur"""
        with self._lock:
            info = self._clients_info.get(client)
            return info is not None and info["role"] == "player"

    def is_spectator(self, client: socket.socket) -> bool:
        """Vérifie que le client soit un spectateur"""
        with self._lock:
            info = self._clients_info.get(client)
            return info is not None and info["role"] == "spectator"

    def get_role(self) -> str | None:
        """Renvoie le rôle du client"""
        with self._role_lock:
            return self._role_client
    
    def is_lobby_ready(self) -> bool:
        """Vérifie que le lobby soit plein (joueurs uniquement)"""
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            return num_players >= self._max_players
    
    def is_lobby_full(self) -> bool:
        """Vérifie que le lobby soit plein (joueurs et spectateurs)"""
        if not self._is_host:
            return False
        with self._lock:
            num_players = sum(1 for i in self._clients_info.values() if i["role"] == "player") + 1
            num_spectators = sum(1 for i in self._clients_info.values() if i["role"] == "spectator")
            players_full = num_players >= self._max_players
            spectators_full = self._max_spectators is None or num_spectators >= self._max_spectators
            return players_full and spectators_full
    
    def is_game_started(self) -> bool:
        """Vérifie que la partie soit lancée"""
        return self._game_started

# ========================= INSTANCE =========================
network_manager = NetworkManager()