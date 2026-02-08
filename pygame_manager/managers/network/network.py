import socket
import json
import threading
import time
from typing import Any

DISCOVERY_PORT = 50000
GAME_PORT = 5555
BROADCAST_INTERVAL = 1.0
LOBBY_TIMEOUT = 3.0


class NetworkManager:
    def __init__(self):
        self._tcp_socket = None
        self._server_socket = None
        self._connected = False
        self._is_host = False

        # ================= TCP SYNC =================
        self._buffer = ""
        self._latest_data: dict[str, Any] | None = None
        self._lock = threading.Lock()

        # ================= UDP DISCOVERY =================
        self._udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._udp_sock.bind(("", DISCOVERY_PORT))
        self._udp_sock.setblocking(True)

        self._lobbies: dict[str, dict] = {}
        self._last_seen: dict[str, float] = {}

        # ================= BROADCAST =================
        self._broadcast_running = False
        self._broadcast_thread = None
        self._lobby_info = {}

    # ========================= HOST =========================
    def host(self, port: int = GAME_PORT, **kwargs) -> bool:
        try:
            self._is_host = True

            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen(1)
            self._server_socket.setblocking(True)

            self._lobby_info = {
                **kwargs,
                "port": port,
                "players": 1,
                "status": "open",
            }

            self._start_broadcast()
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
            self._tcp_socket.setblocking(True)

            self._connected = True
            self._is_host = False
            self._stop_broadcast()

            self._start_receive_thread()
            print(f"[Network] Joined {ip}:{port}")
            return True

        except Exception as e:
            print(f"[Network] Join error: {e}")
            return False

    # ========================= UPDATE LOOP =========================
    def update(self):
        self._receive_lobbies()
        self._cleanup_lobbies()

        if self._is_host and not self._connected:
            self._accept_client()

    # ========================= LOBBIES =========================
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

    def get_lobbies(self, **filters):
        return [
            (ip, lobby)
            for ip, lobby in self._lobbies.items()
            if all(lobby.get(k) == v for k, v in filters.items())
        ]

    # ========================= TCP ACCEPT (HOST) =========================
    def _accept_client(self):
        try:
            client, addr = self._server_socket.accept()
            self._tcp_socket = client
            self._tcp_socket.setblocking(True)

            self._connected = True
            self._lobby_info["status"] = "in_game"
            self._stop_broadcast()

            self._start_receive_thread()
            print(f"[Network] Client connected: {addr}")
        except BlockingIOError:
            pass

    # ========================= DATA SYNC =========================
    def send(self, data: dict[str, Any]) -> bool:
        if not self._connected or not self._tcp_socket:
            return False

        try:
            msg = (json.dumps(data) + "\n").encode()
            self._tcp_socket.sendall(msg)
            return True

        except (BlockingIOError, OSError):
            # buffer plein → on drop ce frame
            return False

        except Exception as e:
            print(f"[Network] Send error: {e}")
            self._connected = False
            return False

    def receive(self) -> dict[str, Any] | None:
        with self._lock:
            data = self._latest_data
            self._latest_data = None
            return data

    def _start_receive_thread(self):
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _receive_loop(self):
        while self._connected:
            try:
                chunk = self._tcp_socket.recv(4096).decode()
                if not chunk:
                    self._connected = False
                    break

                self._buffer += chunk
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    data = json.loads(line)
                    with self._lock:
                        self._latest_data = data

            except BlockingIOError:
                pass
            except Exception as e:
                print(f"[Network] Receive error: {e}")
                self._connected = False
                break

    # ========================= BROADCAST =========================
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
            sock.sendto(
                json.dumps(self._lobby_info).encode(),
                ("<broadcast>", DISCOVERY_PORT),
            )
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