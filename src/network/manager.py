"""
Network Manager Module.

Implements the communication layer between players (Host/Client) using TCP Sockets.
Uses the Observer pattern to emit events when messages arrive, and threading for
non-blocking receives.
"""

import logging
import socket
import threading
import time
from typing import Callable, Dict, List, Optional, Tuple

from .protocol import Message, MessageType, Serializer

# Get logger for this module (let application configure logging)
logger = logging.getLogger(__name__)


# Type alias for message callback functions
MessageCallback = Callable[[Message], None]


class NetworkManager:
    """
    Manages network communication between Host and Client.

    Uses the Observer pattern to notify listeners when messages arrive.
    Supports both hosting (server) and connecting (client) modes.

    Attributes:
        is_host: True if this instance is hosting, False if connecting.
        is_connected: True if a connection is established.
    """

    _instance: Optional["NetworkManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs) -> "NetworkManager":
        """
        Implement Singleton pattern to ensure only one NetworkManager exists.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the NetworkManager."""
        # Prevent re-initialization if already initialized
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._serializer = Serializer()
        self._socket: Optional[socket.socket] = None
        self._client_socket: Optional[socket.socket] = None
        self._server_thread: Optional[threading.Thread] = None
        self._receive_thread: Optional[threading.Thread] = None
        self._running = False
        self._is_host = False
        self._is_connected = False
        self._observers: Dict[MessageType, List[MessageCallback]] = {}
        self._connection_observers: List[Callable[[bool], None]] = []
        self._client_address: Optional[Tuple[str, int]] = None

    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance (useful for testing).
        """
        with cls._lock:
            if cls._instance is not None:
                cls._instance.close()
                cls._instance._initialized = False
            cls._instance = None

    @property
    def is_host(self) -> bool:
        """Return True if this instance is hosting."""
        return self._is_host

    @property
    def is_connected(self) -> bool:
        """Return True if a connection is established."""
        return self._is_connected

    def subscribe(
        self, msg_type: MessageType, callback: MessageCallback
    ) -> None:
        """
        Subscribe to receive messages of a specific type.

        Args:
            msg_type: The type of message to subscribe to.
            callback: Function to call when a message of this type arrives.
        """
        if msg_type not in self._observers:
            self._observers[msg_type] = []
        self._observers[msg_type].append(callback)

    def unsubscribe(
        self, msg_type: MessageType, callback: MessageCallback
    ) -> None:
        """
        Unsubscribe from receiving messages of a specific type.

        Args:
            msg_type: The type of message to unsubscribe from.
            callback: The callback function to remove.
        """
        if msg_type in self._observers:
            try:
                self._observers[msg_type].remove(callback)
            except ValueError:
                pass

    def subscribe_connection(self, callback: Callable[[bool], None]) -> None:
        """
        Subscribe to connection status changes.

        Args:
            callback: Function to call when connection status changes.
                     Receives True when connected, False when disconnected.
        """
        self._connection_observers.append(callback)

    def _notify_observers(self, message: Message) -> None:
        """
        Notify all observers subscribed to this message type.

        Args:
            message: The message that was received.
        """
        if message.msg_type in self._observers:
            for callback in self._observers[message.msg_type]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}")

    def _notify_connection_observers(self, connected: bool) -> None:
        """
        Notify all connection observers of status change.

        Args:
            connected: The new connection status.
        """
        for callback in self._connection_observers:
            try:
                callback(connected)
            except Exception as e:
                logger.error(f"Error in connection callback: {e}")

    def start_host(self, port: int, host: str = "0.0.0.0") -> bool:  # noqa: S104
        """
        Start hosting a game server on the specified port.

        Note:
            The default host '0.0.0.0' binds to all network interfaces, which is
            intentional for a multiplayer game server that needs to accept
            connections from players on the local network or internet.
            To restrict to localhost only, pass host='127.0.0.1'.

        Args:
            port: The port to listen on.
            host: The host address to bind to (default: all interfaces).

        Returns:
            True if the server started successfully, False otherwise.
        """
        if self._running:
            logger.warning("NetworkManager is already running")
            return False

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.bind((host, port))
            self._socket.listen(1)
            self._socket.settimeout(1.0)  # Allow periodic checks for shutdown

            self._is_host = True
            self._running = True

            self._server_thread = threading.Thread(
                target=self._accept_connections, daemon=True
            )
            self._server_thread.start()

            logger.info(f"Server started on {host}:{port}")
            return True

        except OSError as e:
            logger.error(f"Failed to start host: {e}")
            self._cleanup_sockets()
            return False

    def _accept_connections(self) -> None:
        """
        Accept incoming connections in a separate thread.
        """
        while self._running:
            try:
                if self._socket is None:
                    break
                client_socket, address = self._socket.accept()
                self._client_socket = client_socket
                self._client_address = address
                self._is_connected = True

                logger.info(f"Client connected from {address}")
                self._notify_connection_observers(True)

                self._receive_thread = threading.Thread(
                    target=self._receive_loop,
                    args=(self._client_socket,),
                    daemon=True,
                )
                self._receive_thread.start()

                # Only accept one client for now
                break

            except ValueError:
                # Can happen with mocked sockets in tests
                break

            except socket.timeout:
                continue
            except OSError:
                break

    def connect_to_host(self, ip: str, port: int, timeout: float = 5.0) -> bool:
        """
        Connect to a game host.

        Args:
            ip: The IP address of the host.
            port: The port to connect to.
            timeout: Connection timeout in seconds.

        Returns:
            True if connection was successful, False otherwise.
        """
        if self._running:
            logger.warning("NetworkManager is already running")
            return False

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(timeout)
            self._socket.connect((ip, port))
            self._socket.settimeout(None)

            self._is_host = False
            self._running = True
            self._is_connected = True

            self._receive_thread = threading.Thread(
                target=self._receive_loop,
                args=(self._socket,),
                daemon=True,
            )
            self._receive_thread.start()

            logger.info(f"Connected to host at {ip}:{port}")
            self._notify_connection_observers(True)
            return True

        except (OSError, socket.timeout) as e:
            logger.error(f"Failed to connect to host: {e}")
            self._cleanup_sockets()
            return False

    def _receive_loop(self, sock: socket.socket) -> None:
        """
        Continuously receive messages from the socket.

        Args:
            sock: The socket to receive from.
        """
        while self._running and self._is_connected:
            try:
                # Read message length header
                header = self._recv_exact(sock, Serializer.HEADER_SIZE)
                if header is None:
                    break

                msg_length = self._serializer.read_header(header)

                # Read message body
                data = self._recv_exact(sock, msg_length)
                if data is None:
                    break

                message = self._serializer.deserialize(data)
                self._notify_observers(message)

            except (ConnectionResetError, BrokenPipeError):
                logger.info("Connection lost")
                break
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break

        self._handle_disconnect()

    def _recv_exact(self, sock: socket.socket, num_bytes: int) -> Optional[bytes]:
        """
        Receive exactly num_bytes from the socket.

        Args:
            sock: The socket to receive from.
            num_bytes: The exact number of bytes to receive.

        Returns:
            The received bytes, or None if connection was closed.
        """
        data = b""
        while len(data) < num_bytes:
            try:
                chunk = sock.recv(num_bytes - len(data))
                if not chunk:
                    return None
                data += chunk
            except socket.timeout:
                continue
            except OSError:
                return None
        return data

    def _handle_disconnect(self) -> None:
        """Handle disconnection cleanup."""
        if self._is_connected:
            self._is_connected = False
            self._notify_connection_observers(False)
            logger.info("Disconnected")

    def send(self, message: Message) -> bool:
        """
        Send a message to the connected peer.

        Args:
            message: The message to send.

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        if not self._is_connected:
            logger.warning("Cannot send: not connected")
            return False

        try:
            data = self._serializer.serialize(message)
            target_socket = (
                self._client_socket if self._is_host else self._socket
            )

            if target_socket is None:
                return False

            target_socket.sendall(data)
            return True

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            logger.error(f"Failed to send message: {e}")
            self._handle_disconnect()
            return False

    def close(self) -> None:
        """
        Close all connections and stop the network manager.
        """
        self._running = False
        self._is_connected = False
        self._cleanup_sockets()

        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=2.0)
        if self._receive_thread and self._receive_thread.is_alive():
            self._receive_thread.join(timeout=2.0)

        self._server_thread = None
        self._receive_thread = None
        self._observers.clear()
        self._connection_observers.clear()

        logger.info("NetworkManager closed")

    def _cleanup_sockets(self) -> None:
        """Clean up socket resources."""
        if self._client_socket:
            try:
                self._client_socket.close()
            except OSError:
                pass
            self._client_socket = None

        if self._socket:
            try:
                self._socket.close()
            except OSError:
                pass
            self._socket = None
