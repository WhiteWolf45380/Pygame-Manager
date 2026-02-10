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

        # ================= DATA =================
        self._latest_data = None
        self._latest_by_client: dict[socket.socket, dict | None] = {}
        self._last_seen: dict[socket.socket, float] = {}
        self._lock = threading.Lock()

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

    # ========================= HOST =========================
    def host(self, port: int = GAME_PORT, max_players: int | None = None, **kwargs) -> bool:
        try:
            self._is_host = True
            self._connected = True

            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen()
            self._server_socket.setblocking(False)

            self._lobby_info = {
                **kwargs,
                "port": port,
                "players": 1,
                "max_players": max_players,
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
        self._connected = False
        self._broadcast_running = False

        if self._tcp_socket:
            try:
                self._tcp_socket.close()
            except OSError:
                pass
            self._tcp_socket = None

        with self._lock:
            for c in self._clients:
                try:
                    c.close()
                except OSError:
                    pass
            self._clients.clear()
            self._latest_by_client.clear()
            self._last_seen.clear()

        self._latest_data = None
        self._is_host = False
        self._lobby_info = {}
        print("[Network] Disconnected cleanly")

    # ========================= UPDATE =========================
    def update(self):
        self._receive_lobbies()
        self._cleanup_lobbies()
        if self._is_host:
            self._accept_clients()
            self._cleanup_dead_clients()

    # ========================= LOBBIES =========================
    def _receive_lobbies(self):
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
        now = time.time()
        for ip in list(self._lobbies.keys()):
            if now - self._last_lobby_seen[ip] > LOBBY_TIMEOUT:
                del self._lobbies[ip]
                del self._last_lobby_seen[ip]

    def get_lobbies(self, **filters):
        return [
            (ip, lobby)
            for ip, lobby in self._lobbies.items()
            if all(lobby.get(k) == v for k, v in filters.items())
        ]

    # ========================= ACCEPT CLIENTS =========================
    def _accept_clients(self):
        try:
            while True:
                with self._lock:
                    max_players = self._lobby_info.get("max_players")
                    if max_players and len(self._clients) >= max_players:
                        return

                client, addr = self._server_socket.accept()
                client.setblocking(False)

                with self._lock:
                    self._clients.append(client)
                    self._latest_by_client[client] = None
                    self._last_seen[client] = time.time()
                    self._lobby_info["players"] += 1

                threading.Thread(target=self._receive_loop_host, args=(client,), daemon=True).start()
                print(f"[Network] Client connected: {addr}")

        except BlockingIOError:
            pass

    # ========================= SEND =========================
    def send(self, data: dict[str, Any]) -> bool:
        msg = (json.dumps(data) + "\n").encode()
        if self._is_host:
            with self._lock:
                clients = list(self._clients)
            for c in clients:
                try:
                    c.sendall(msg)
                except OSError:
                    print(f"[Network] Warning: client {c} send failed")
        else:
            try:
                self._tcp_socket.sendall(msg)
            except Exception as e:
                print(f"[Network] Send error: {e}")
                return False
        return True

    # ========================= RECEIVE =========================
    def receive(self):
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
                data = self._latest_by_client.get(client)

                if data is None:
                    try:
                        client.close()
                    except OSError:
                        pass
                    self._clients.popleft()
                    self._latest_by_client.pop(client, None)
                    self._last_seen.pop(client, None)
                    self._lobby_info["players"] = max(1, len(self._clients) + 1)
                    if not self._clients:
                        return None
                    continue

                self._latest_by_client[client] = None
                self._clients.rotate(-1)
                return client, data
        return None

    # ========================= RECEIVE LOOPS =========================
    def _receive_loop_client(self):
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
                    with self._lock:
                        self._latest_data = json.loads(line)
            except BlockingIOError:
                pass
            except Exception as e:
                print(f"[Network] Client receive error: {e}")
                break
        self.disconnect()

    def _receive_loop_host(self, client: socket.socket):
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
                    data = json.loads(line)
                    with self._lock:
                        self._latest_by_client[client] = data
                        self._last_seen[client] = time.time()
            except BlockingIOError:
                pass
            except Exception as e:
                print(f"[Network] Host receive error: {e}")
                break
        print("[Network] Client disconnected (lazy)")

    # ========================= HEARTBEAT / CLEANUP =========================
    def _start_heartbeat(self):
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _heartbeat_loop(self):
        while self._connected:
            now = time.time()
            with self._lock:
                for client in list(self._clients):
                    if now - self._last_seen.get(client, 0) > CLIENT_TIMEOUT:
                        try:
                            client.close()
                        except OSError:
                            pass
                        self._clients.remove(client)
                        self._latest_by_client.pop(client, None)
                        self._last_seen.pop(client, None)
                        self._lobby_info["players"] = max(1, len(self._clients) + 1)
            time.sleep(self._heartbeat_interval)

    # ========================= BROADCAST =========================
    def _start_broadcast(self):
        self._broadcast_running = True
        self._broadcast_thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self._broadcast_thread.start()

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_addr = "<broadcast>"
        try:
            sock.sendto(b"", ("255.255.255.255", DISCOVERY_PORT))
        except OSError:
            broadcast_addr = "<broadcast>"
        while self._broadcast_running:
            sock.sendto(json.dumps(self._lobby_info).encode(), (broadcast_addr, DISCOVERY_PORT))
            time.sleep(BROADCAST_INTERVAL)
        sock.close()

    def _stop_broadcast(self):
        self._broadcast_running = False

    # ========================= PROPS =========================
    @property
    def is_connected(self):
        return self._connected

    @property
    def is_host(self):
        return self._is_host

    def __repr__(self):
        return f"<NetworkManager {'host' if self._is_host else 'client'} | {'connected' if self._connected else 'idle'}>"

# ========================= INSTANCE =========================
network_manager = NetworkManager()