# ======================================== IMPORTS ========================================
import socket
import json
import threading
import time

# ======================================== VARIABLES ========================================
DISCOVERY_PORT = 50000
GAME_PORT = 5555
BROADCAST_INTERVAL = 1.0
LOBBY_TIMEOUT = 3.0

# ======================================== GESTIONNAIRE ========================================
class NetworkManager:
    def __init__(self):
        self._tcp_socket = None
        self._server_socket = None
        self._connected = False
        self._is_host = False

        # Lobby discovery
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._udp_sock.bind(("", DISCOVERY_PORT))
        self._udp_sock.setblocking(False)

        self._lobbies: dict[str, dict] = {}
        self._last_seen: dict[str, float] = {}

        # Lobby broadcast
        self._broadcast_thread = None
        self._broadcast_running = False
        self._lobby_info = {}

    # ======================================== HOST ========================================
    def host(self, port: int = GAME_PORT, **kwargs) -> bool:
        try:
            self._is_host = True

            # TCP server
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen(1)

            # lobby info
            self._lobby_info = {
                **kwargs,
                "port": port,
                "players": 1,
            }

            self._start_broadcast()
            print(f"[Network] Hosting lobby: {self._lobby_info}")
            return True

        except Exception as e:
            print(f"[Network] Host error: {e}")
            return False

    # ======================================== JOIN ========================================
    def join(self, ip: str, port: int | None = None) -> bool:
        try:
            port = port or GAME_PORT
            self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._tcp_socket.connect((ip, port))
            self._connected = True
            self._is_host = False

            self._stop_broadcast()
            print(f"[Network] Joined {ip}:{port}")
            return True

        except Exception as e:
            print(f"[Network] Join error: {e}")
            return False

    # ======================================== DISCOVERY ========================================
    def update(self):
        """À appeler dans la game loop"""
        self._receive_lobbies()
        self._cleanup_lobbies()

        if self._is_host and not self._connected:
            self._accept_client()

    def _receive_lobbies(self):
        try:
            while True:
                data, addr = self._udp_sock.recvfrom(2048)
                lobby = json.loads(data.decode())
                ip = addr[0]

                self._lobbies[ip] = lobby
                self._last_seen[ip] = time.time()

        except BlockingIOError:
            pass

    def _cleanup_lobbies(self):
        now = time.time()
        for ip in list(self._lobbies.keys()):
            if now - self._last_seen[ip] > LOBBY_TIMEOUT:
                del self._lobbies[ip]
                del self._last_seen[ip]

    def get_lobbies(self, **filters) -> list[tuple[str, dict]]:
        results = []
        for ip, lobby in self._lobbies.items():
            if all(lobby.get(k) == v for k, v in filters.items()):
                results.append((ip, lobby))
        return results

    # ======================================== TCP ========================================
    def _accept_client(self):
        try:
            self._server_socket.setblocking(False)
            self._tcp_socket, addr = self._server_socket.accept()
            self._connected = True
            self._stop_broadcast()
            print(f"[Network] Client connected: {addr}")
        except BlockingIOError:
            pass

    # ======================================== BROADCAST ========================================
    def _start_broadcast(self):
        self._broadcast_running = True
        self._broadcast_thread = threading.Thread(
            target=self._broadcast_loop, daemon=True
        )
        self._broadcast_thread.start()

    def _broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while self._broadcast_running:
            msg = json.dumps(self._lobby_info).encode()
            sock.sendto(msg, ("<broadcast>", DISCOVERY_PORT))
            time.sleep(BROADCAST_INTERVAL)

        sock.close()

    def _stop_broadcast(self):
        self._broadcast_running = False

    # ======================================== UTILS ========================================
    @property
    def is_host(self):
        return self._is_host

    @property
    def is_connected(self):
        return self._connected

    def __repr__(self):
        role = "host" if self._is_host else "client"
        status = "connected" if self._connected else "idle"
        return f"<NetworkManager {role} | {status}>"

# ======================================== INSTANCE ========================================
network_manager = NetworkManager()