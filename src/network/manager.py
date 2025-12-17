"""
Network Manager module for handling TCP socket connections.

This module implements the NetworkManager class which handles Host/Client
connections using TCP sockets with non-blocking receives and Observer pattern
for event handling.
"""

import socket
import threading
import selectors
from typing import Optional, Callable, Dict
import logging

from .protocol import Message, MessageType, Serializer


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkManager:
    """
    Manages network connections for multiplayer game.

    Implements Observer pattern for event handling and uses threading
    for non-blocking message receives. Separates transport layer (sockets)
    from protocol layer (serialization).

    Attributes:
        role: Either 'host' or 'client'.
        socket: The main socket connection.
        connected: Connection status flag.
        observers: Dictionary of event callbacks.
    """

    _instance = None
    _lock = threading.Lock()

    # Class constants
    THREAD_JOIN_TIMEOUT = 2.0  # seconds

    def __new__(cls):
        """
        Singleton pattern implementation.

        Ensures only one NetworkManager instance exists per process.
        This prevents multiple network connections from being created
        inadvertently.
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize NetworkManager."""
        if not hasattr(self, '_initialized'):
            self.role: Optional[str] = None
            self.socket: Optional[socket.socket] = None
            self.client_socket: Optional[socket.socket] = None
            self.connected: bool = False
            self.observers: Dict[MessageType, Callable] = {}
            self.receive_thread: Optional[threading.Thread] = None
            self._stop_event = threading.Event()
            self.use_json: bool = True
            self._initialized = True

    def register_observer(self, msg_type: MessageType, callback: Callable[[Message], None]):
        """
        Register an observer callback for a specific message type.

        Args:
            msg_type: Type of message to observe.
            callback: Function to call when message is received.
        """
        self.observers[msg_type] = callback
        logger.info(f"Registered observer for {msg_type.value}")

    def unregister_observer(self, msg_type: MessageType):
        """
        Remove an observer for a specific message type.

        Args:
            msg_type: Type of message to stop observing.
        """
        if msg_type in self.observers:
            del self.observers[msg_type]
            logger.info(f"Unregistered observer for {msg_type.value}")

    def _notify_observers(self, message: Message):
        """
        Notify observers when a message is received.

        Args:
            message: Received message.
        """
        if message.msg_type in self.observers:
            try:
                self.observers[message.msg_type](message)
            except Exception as e:
                logger.error(f"Error in observer callback: {e}")

    def start_host(self, port: int = 5555, bind_address: str = '127.0.0.1') -> bool:
        """
        Start as host (server) and listen for incoming connections.

        Args:
            port: Port number to listen on.
            bind_address: IP address to bind to. Defaults to '127.0.0.1' (localhost)
                         for security. Use '0.0.0.0' to accept connections from any
                         network interface (LAN/WAN), but be aware of security implications.

        Returns:
            True if host started successfully, False otherwise.

        Security Note:
            Binding to '0.0.0.0' exposes the server to all network interfaces,
            which may pose security risks. Only use this for trusted LAN environments.
        """
        try:
            self.role = 'host'
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((bind_address, port))
            self.socket.listen(1)
            logger.info(f"Host started on {bind_address}:{port}, waiting for client...")

            # Accept connection (blocking)
            self.client_socket, addr = self.socket.accept()
            logger.info(f"Client connected from {addr}")
            self.connected = True

            # Start receive thread
            self._start_receive_thread()
            return True

        except Exception as e:
            logger.error(f"Failed to start host: {e}")
            self.close()
            return False

    def connect_to_host(self, ip: str, port: int = 5555, timeout: int = 10) -> bool:
        """
        Connect to a host as a client.

        Args:
            ip: IP address of the host.
            port: Port number of the host.
            timeout: Connection timeout in seconds.

        Returns:
            True if connected successfully, False otherwise.
        """
        try:
            self.role = 'client'
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(timeout)

            logger.info(f"Connecting to host at {ip}:{port}...")
            self.socket.connect((ip, port))
            logger.info("Connected to host successfully")
            self.connected = True

            # For client, the main socket is used for communication
            self.client_socket = self.socket

            # Start receive thread
            self._start_receive_thread()
            return True

        except Exception as e:
            logger.error(f"Failed to connect to host: {e}")
            self.close()
            return False

    def _start_receive_thread(self):
        """Start the background thread for receiving messages."""
        self._stop_event.clear()
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("Receive thread started")

    def _receive_loop(self):
        """
        Main receive loop running in background thread.
        Uses selectors for non-blocking I/O.
        """
        sel = selectors.DefaultSelector()

        if self.client_socket:
            sel.register(self.client_socket, selectors.EVENT_READ)

        try:
            while not self._stop_event.is_set() and self.connected:
                # Wait for socket to be ready with timeout
                events = sel.select(timeout=0.5)

                for key, mask in events:
                    if mask & selectors.EVENT_READ:
                        try:
                            message = self._receive_message(key.fileobj)
                            if message:
                                self._notify_observers(message)
                            else:
                                # Connection closed
                                logger.info("Connection closed by peer")
                                self.connected = False
                                break
                        except Exception as e:
                            logger.error(f"Error receiving message: {e}")
                            self.connected = False
                            break
        finally:
            sel.close()
            logger.info("Receive loop terminated")

    def _receive_message(self, sock: socket.socket) -> Optional[Message]:
        """
        Receive a single message from socket.

        Args:
            sock: Socket to receive from.

        Returns:
            Received Message or None if connection closed.
        """
        # First, receive 4-byte length header
        length_data = self._recv_exact(sock, 4)
        if not length_data:
            return None

        msg_length = int.from_bytes(length_data, byteorder='big')

        # Then receive the message data
        msg_data = self._recv_exact(sock, msg_length)
        if not msg_data:
            return None

        # Deserialize
        message = Serializer.deserialize(msg_data, use_json=self.use_json)
        logger.debug(f"Received message: {message.msg_type.value}")
        return message

    def _recv_exact(self, sock: socket.socket, num_bytes: int) -> Optional[bytes]:
        """
        Receive exactly num_bytes from socket.

        Args:
            sock: Socket to receive from.
            num_bytes: Number of bytes to receive.

        Returns:
            Received bytes or None if connection closed.
        """
        data = bytearray()
        while len(data) < num_bytes:
            chunk = sock.recv(num_bytes - len(data))
            if not chunk:
                return None
            data.extend(chunk)
        return bytes(data)

    def send(self, message: Message) -> bool:
        """
        Send a message to the connected peer.

        Args:
            message: Message to send.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.connected or not self.client_socket:
            logger.error("Cannot send: not connected")
            return False

        try:
            serialized = Serializer.serialize(message, use_json=self.use_json)
            self.client_socket.sendall(serialized)
            logger.debug(f"Sent message: {message.msg_type.value}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.connected = False
            return False

    def close(self):
        """Close all connections and clean up resources."""
        logger.info("Closing network manager...")
        self.connected = False
        self._stop_event.set()

        # Wait for receive thread to finish
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=self.THREAD_JOIN_TIMEOUT)

        # Close sockets
        if self.client_socket and self.client_socket != self.socket:
            try:
                self.client_socket.close()
            except Exception:
                pass

        if self.socket:
            try:
                self.socket.close()
            except Exception:
                pass

        self.socket = None
        self.client_socket = None
        self.role = None
        logger.info("Network manager closed")

    def is_connected(self) -> bool:
        """
        Check if currently connected to a peer.

        Returns:
            True if connected, False otherwise.
        """
        return self.connected

    def get_role(self) -> Optional[str]:
        """
        Get the current role (host or client).

        Returns:
            Role string or None if not connected.
        """
        return self.role
