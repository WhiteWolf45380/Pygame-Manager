# ======================================== IMPORTS ========================================
import socket
import json
import threading
from typing import Any

# ======================================== GESTIONNAIRE ========================================
class NetworkManager:
    """
    Gestionnaire de connexion réseau pour synchroniser des variables entre deux clients.
    
    Usage:
        # Host
        pm.network.host()
        pm.network.send({"paddle_y": 150, "score": 5})
        data = pm.network.receive()
        
        # Client
        pm.network.join("192.168.1.10")
        pm.network.send({"paddle_y": 300})
        data = pm.network.receive()
    """
    
    def __init__(self):
        self._socket = None
        self._server_socket = None
        self._is_host = False
        self._connected = False
        self._buffer = ""
        self._latest_data = None
        self._lock = threading.Lock()
    
    # ======================================== CONNECTION ========================================
    def host(self, port: int = 5555, timeout: float = 30.0) -> bool:
        """
        Héberge une session et attend une connexion.
        
        Args:
            port: Port d'écoute
            timeout: Temps d'attente max pour une connexion (secondes)
            
        Returns:
            True si connexion établie, False sinon
        """
        try:
            self._is_host = True
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", port))
            self._server_socket.listen(1)
            self._server_socket.settimeout(timeout)
            
            # Affiche les IPs disponibles
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            print(f"[Network] Hosting on port {port}")
            print(f"[Network] Local: 127.0.0.1:{port}")
            print(f"[Network] LAN: {local_ip}:{port}")
            
            self._socket, addr = self._server_socket.accept()
            self._socket.setblocking(False)
            self._connected = True
            print(f"[Network] Client connected: {addr}")
            
            # Lance le thread de réception
            threading.Thread(target=self._receive_loop, daemon=True).start()
            return True
            
        except socket.timeout:
            print("[Network] Connection timeout")
            self._cleanup()
            return False
        except Exception as e:
            print(f"[Network] Host error: {e}")
            self._cleanup()
            return False
    
    def join(self, ip: str, port: int = 5555, timeout: float = 10.0) -> bool:
        """
        Rejoint une session hébergée.
        
        Args:
            ip: Adresse IP du host
            port: Port de connexion
            timeout: Temps d'attente max pour connexion (secondes)
            
        Returns:
            True si connexion établie, False sinon
        """
        try:
            self._is_host = False
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((ip, port))
            self._socket.setblocking(False)
            self._connected = True
            print(f"[Network] Connected to {ip}:{port}")
            
            # Lance le thread de réception
            threading.Thread(target=self._receive_loop, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"[Network] Join error: {e}")
            self._cleanup()
            return False
    
    # ======================================== DATA TRANSFER ========================================
    def send(self, data: dict[str, Any]) -> bool:
        """
        Envoie un dictionnaire de données.
        
        Args:
            data: Dictionnaire à envoyer (sera converti en JSON)
            
        Returns:
            True si envoi réussi, False sinon
        """
        if not self._connected or self._socket is None:
            return False
            
        try:
            message = json.dumps(data) + "\n"
            self._socket.sendall(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[Network] Send error: {e}")
            self._connected = False
            return False
    
    def receive(self) -> dict[str, Any] | None:
        """
        Récupère les dernières données reçues (non-bloquant).
        
        Returns:
            Dictionnaire des données reçues, ou None si rien de nouveau
        """
        with self._lock:
            data = self._latest_data
            self._latest_data = None
            return data
    
    def _receive_loop(self):
        """Thread interne de réception des données."""
        while self._connected:
            try:
                chunk = self._socket.recv(4096).decode('utf-8')
                if not chunk:
                    self._connected = False
                    break
                    
                self._buffer += chunk
                
                # Traite tous les messages complets dans le buffer
                while "\n" in self._buffer:
                    line, self._buffer = self._buffer.split("\n", 1)
                    try:
                        data = json.loads(line)
                        with self._lock:
                            self._latest_data = data
                    except json.JSONDecodeError:
                        pass
                        
            except BlockingIOError:
                # Normal pour un socket non-bloquant
                pass
            except Exception as e:
                print(f"[Network] Receive error: {e}")
                self._connected = False
                break
    
    # ======================================== DISCONNECTION ========================================
    def disconnect(self):
        """Ferme la connexion proprement."""
        self._connected = False
        self._cleanup()
        print("[Network] Disconnected")
    
    def _cleanup(self):
        """Nettoie les ressources réseau."""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
            
        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None
    
    # ======================================== PROPERTIES ========================================
    @property
    def is_host(self) -> bool:
        """Indique si cette instance est le host."""
        return self._is_host
    
    @property
    def is_connected(self) -> bool:
        """Indique si la connexion est active."""
        return self._connected
    
    def __repr__(self):
        status = "connected" if self._connected else "disconnected"
        role = "host" if self._is_host else "client"
        return f"<NetworkManager: {role}, {status}>"
    
# ======================================== INSTANCIATION ========================================
network_manager = NetworkManager