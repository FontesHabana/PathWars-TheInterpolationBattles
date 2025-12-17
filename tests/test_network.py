"""
Unit tests for the Network Core System.

Tests protocol serialization and network manager functionality.
"""

import json
import socket
import struct
import sys
import os
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from network.protocol import Message, MessageType, Serializer
from network.manager import NetworkManager


class TestMessageType:
    """Tests for MessageType enum."""

    def test_message_types_exist(self):
        """Test that all expected message types exist."""
        expected_types = [
            "CONNECT",
            "DISCONNECT",
            "GAME_STATE",
            "PLAYER_ACTION",
            "CHAT",
            "PING",
            "PONG",
            "ERROR",
        ]
        for msg_type in expected_types:
            assert hasattr(MessageType, msg_type)


class TestMessage:
    """Tests for Message dataclass."""

    def test_message_creation_basic(self):
        """Test creating a basic message."""
        msg = Message(msg_type=MessageType.PING)
        assert msg.msg_type == MessageType.PING
        assert msg.payload == {}
        assert msg.sender_id is None
        assert msg.timestamp is None

    def test_message_creation_with_payload(self):
        """Test creating a message with payload."""
        payload = {"x": 100, "y": 200, "action": "move"}
        msg = Message(
            msg_type=MessageType.PLAYER_ACTION,
            payload=payload,
            sender_id="player1",
            timestamp=1234567890.0,
        )
        assert msg.msg_type == MessageType.PLAYER_ACTION
        assert msg.payload == payload
        assert msg.sender_id == "player1"
        assert msg.timestamp == 1234567890.0

    def test_message_to_dict(self):
        """Test converting message to dictionary."""
        msg = Message(
            msg_type=MessageType.CHAT,
            payload={"text": "Hello!"},
            sender_id="player2",
        )
        result = msg.to_dict()

        assert result["msg_type"] == "CHAT"
        assert result["payload"] == {"text": "Hello!"}
        assert result["sender_id"] == "player2"
        assert result["timestamp"] is None

    def test_message_from_dict(self):
        """Test creating message from dictionary."""
        data = {
            "msg_type": "GAME_STATE",
            "payload": {"score": 100},
            "sender_id": "host",
            "timestamp": 1000.0,
        }
        msg = Message.from_dict(data)

        assert msg.msg_type == MessageType.GAME_STATE
        assert msg.payload == {"score": 100}
        assert msg.sender_id == "host"
        assert msg.timestamp == 1000.0

    def test_message_from_dict_minimal(self):
        """Test creating message from minimal dictionary."""
        data = {"msg_type": "PING"}
        msg = Message.from_dict(data)

        assert msg.msg_type == MessageType.PING
        assert msg.payload == {}
        assert msg.sender_id is None
        assert msg.timestamp is None

    def test_message_from_dict_invalid_type(self):
        """Test that invalid message type raises error."""
        data = {"msg_type": "INVALID_TYPE"}
        with pytest.raises(KeyError):
            Message.from_dict(data)

    def test_message_roundtrip(self):
        """Test message survives to_dict -> from_dict roundtrip."""
        original = Message(
            msg_type=MessageType.PLAYER_ACTION,
            payload={"action": "attack", "target": "enemy1"},
            sender_id="player1",
            timestamp=9999.0,
        )
        reconstructed = Message.from_dict(original.to_dict())

        assert reconstructed.msg_type == original.msg_type
        assert reconstructed.payload == original.payload
        assert reconstructed.sender_id == original.sender_id
        assert reconstructed.timestamp == original.timestamp


class TestSerializer:
    """Tests for Serializer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.serializer = Serializer()

    def test_serialize_returns_bytes(self):
        """Test that serialize returns bytes."""
        msg = Message(msg_type=MessageType.PING)
        result = self.serializer.serialize(msg)
        assert isinstance(result, bytes)

    def test_serialize_has_length_prefix(self):
        """Test that serialized data has correct length prefix."""
        msg = Message(msg_type=MessageType.PING, payload={"test": "data"})
        result = self.serializer.serialize(msg)

        # First 4 bytes should be the length
        length = struct.unpack(">I", result[:4])[0]
        # Rest should be JSON data
        json_data = result[4:]
        assert len(json_data) == length

    def test_deserialize_valid_json(self):
        """Test deserializing valid JSON data."""
        data = json.dumps({"msg_type": "PONG", "payload": {}}).encode("utf-8")
        msg = self.serializer.deserialize(data)

        assert msg.msg_type == MessageType.PONG
        assert msg.payload == {}

    def test_deserialize_invalid_json(self):
        """Test that invalid JSON raises error."""
        data = b"not valid json"
        with pytest.raises(json.JSONDecodeError):
            self.serializer.deserialize(data)

    def test_read_header(self):
        """Test reading message length from header."""
        # Pack a length of 1000
        header = struct.pack(">I", 1000)
        length = self.serializer.read_header(header)
        assert length == 1000

    def test_read_header_invalid_size(self):
        """Test that invalid header size raises error."""
        with pytest.raises(struct.error):
            self.serializer.read_header(b"\x00\x00")

    def test_serialize_deserialize_roundtrip(self):
        """Test full serialization roundtrip."""
        original = Message(
            msg_type=MessageType.GAME_STATE,
            payload={"players": [{"id": 1}, {"id": 2}]},
            sender_id="server",
            timestamp=12345.678,
        )
        serialized = self.serializer.serialize(original)

        # Skip the 4-byte header
        json_data = serialized[4:]
        reconstructed = self.serializer.deserialize(json_data)

        assert reconstructed.msg_type == original.msg_type
        assert reconstructed.payload == original.payload
        assert reconstructed.sender_id == original.sender_id
        assert reconstructed.timestamp == original.timestamp


class TestNetworkManagerUnit:
    """Unit tests for NetworkManager with mocked sockets."""

    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()

    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()

    def test_singleton_pattern(self):
        """Test that NetworkManager follows singleton pattern."""
        manager1 = NetworkManager()
        manager2 = NetworkManager()
        assert manager1 is manager2

    def test_reset_instance(self):
        """Test that reset_instance creates new instance."""
        manager1 = NetworkManager()
        NetworkManager.reset_instance()
        manager2 = NetworkManager()
        # After reset, we get a new instance (but singleton still works)
        assert manager1 is not manager2

    def test_initial_state(self):
        """Test initial state of NetworkManager."""
        manager = NetworkManager()
        assert manager.is_host is False
        assert manager.is_connected is False

    def test_subscribe_and_notify(self):
        """Test subscribing to message events."""
        manager = NetworkManager()
        received_messages = []

        def callback(msg):
            received_messages.append(msg)

        manager.subscribe(MessageType.PING, callback)

        # Manually trigger notification
        test_msg = Message(msg_type=MessageType.PING)
        manager._notify_observers(test_msg)

        assert len(received_messages) == 1
        assert received_messages[0].msg_type == MessageType.PING

    def test_unsubscribe(self):
        """Test unsubscribing from message events."""
        manager = NetworkManager()
        received_messages = []

        def callback(msg):
            received_messages.append(msg)

        manager.subscribe(MessageType.CHAT, callback)
        manager.unsubscribe(MessageType.CHAT, callback)

        test_msg = Message(msg_type=MessageType.CHAT)
        manager._notify_observers(test_msg)

        assert len(received_messages) == 0

    def test_connection_observers(self):
        """Test connection status observers."""
        manager = NetworkManager()
        status_changes = []

        def callback(connected):
            status_changes.append(connected)

        manager.subscribe_connection(callback)

        manager._notify_connection_observers(True)
        manager._notify_connection_observers(False)

        assert status_changes == [True, False]

    def test_send_when_not_connected(self):
        """Test that send fails when not connected."""
        manager = NetworkManager()
        msg = Message(msg_type=MessageType.PING)
        result = manager.send(msg)
        assert result is False

    @patch("socket.socket")
    def test_start_host_creates_socket(self, mock_socket_class):
        """Test that start_host creates and configures socket."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        manager = NetworkManager()
        result = manager.start_host(12345)

        assert result is True
        assert manager.is_host is True
        mock_socket.bind.assert_called_once_with(("0.0.0.0", 12345))
        mock_socket.listen.assert_called_once_with(1)

        manager.close()

    @patch("socket.socket")
    def test_start_host_failure(self, mock_socket_class):
        """Test start_host handles socket errors."""
        mock_socket = MagicMock()
        mock_socket.bind.side_effect = OSError("Address in use")
        mock_socket_class.return_value = mock_socket

        manager = NetworkManager()
        result = manager.start_host(12345)

        assert result is False
        assert manager.is_host is False

    @patch("socket.socket")
    def test_connect_to_host_success(self, mock_socket_class):
        """Test successful connection to host."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        manager = NetworkManager()
        result = manager.connect_to_host("127.0.0.1", 12345)

        assert result is True
        assert manager.is_connected is True
        assert manager.is_host is False
        mock_socket.connect.assert_called_once_with(("127.0.0.1", 12345))

        manager.close()

    @patch("socket.socket")
    def test_connect_to_host_failure(self, mock_socket_class):
        """Test connection failure handling."""
        mock_socket = MagicMock()
        mock_socket.connect.side_effect = OSError("Connection refused")
        mock_socket_class.return_value = mock_socket

        manager = NetworkManager()
        result = manager.connect_to_host("127.0.0.1", 12345)

        assert result is False
        assert manager.is_connected is False

    def test_close_clears_state(self):
        """Test that close clears all state."""
        manager = NetworkManager()
        manager.subscribe(MessageType.PING, lambda m: None)
        manager.subscribe_connection(lambda c: None)

        manager.close()

        # Internal state should be cleared
        assert manager._observers == {}
        assert manager._connection_observers == []


class TestNetworkManagerIntegration:
    """Integration tests with real sockets on localhost."""

    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()

    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()

    def test_host_client_connection(self):
        """Test host and client can connect."""
        # Create separate instances by resetting singleton between creations
        host_manager = NetworkManager()
        port = 55555

        # Start host
        assert host_manager.start_host(port) is True
        assert host_manager.is_host is True

        # Need a fresh instance for client (bypass singleton for testing)
        NetworkManager._instance = None
        client_manager = NetworkManager()

        # Give server time to start
        time.sleep(0.1)

        # Connect client
        assert client_manager.connect_to_host("127.0.0.1", port) is True
        assert client_manager.is_connected is True

        # Give time for host to accept connection
        time.sleep(0.2)
        assert host_manager.is_connected is True

        # Cleanup
        client_manager.close()
        host_manager.close()

    def test_send_receive_message(self):
        """Test sending and receiving messages."""
        received_messages = []
        received_event = threading.Event()

        def on_message(msg):
            received_messages.append(msg)
            received_event.set()

        # Create host
        host_manager = NetworkManager()
        host_manager.subscribe(MessageType.PING, on_message)
        port = 55556

        assert host_manager.start_host(port) is True

        # Create client (bypass singleton)
        NetworkManager._instance = None
        client_manager = NetworkManager()

        time.sleep(0.1)
        assert client_manager.connect_to_host("127.0.0.1", port) is True

        # Wait for connection to be established
        time.sleep(0.2)

        # Send message from client to host
        msg = Message(
            msg_type=MessageType.PING,
            payload={"data": "test"},
            sender_id="client",
        )
        assert client_manager.send(msg) is True

        # Wait for message to be received
        received_event.wait(timeout=2.0)

        assert len(received_messages) == 1
        assert received_messages[0].msg_type == MessageType.PING
        assert received_messages[0].payload == {"data": "test"}
        assert received_messages[0].sender_id == "client"

        # Cleanup
        client_manager.close()
        host_manager.close()

    def test_bidirectional_communication(self):
        """Test that both host and client can send/receive."""
        host_received = []
        client_received = []
        host_event = threading.Event()
        client_event = threading.Event()

        def on_host_message(msg):
            host_received.append(msg)
            host_event.set()

        def on_client_message(msg):
            client_received.append(msg)
            client_event.set()

        # Create host
        host_manager = NetworkManager()
        host_manager.subscribe(MessageType.CHAT, on_host_message)
        port = 55557

        assert host_manager.start_host(port) is True

        # Create client (bypass singleton)
        NetworkManager._instance = None
        client_manager = NetworkManager()
        client_manager.subscribe(MessageType.CHAT, on_client_message)

        time.sleep(0.1)
        assert client_manager.connect_to_host("127.0.0.1", port) is True
        time.sleep(0.2)

        # Client sends to host
        client_msg = Message(msg_type=MessageType.CHAT, payload={"text": "Hello host!"})
        assert client_manager.send(client_msg) is True

        host_event.wait(timeout=2.0)
        assert len(host_received) == 1
        assert host_received[0].payload["text"] == "Hello host!"

        # Host sends to client
        host_msg = Message(msg_type=MessageType.CHAT, payload={"text": "Hello client!"})
        assert host_manager.send(host_msg) is True

        client_event.wait(timeout=2.0)
        assert len(client_received) == 1
        assert client_received[0].payload["text"] == "Hello client!"

        # Cleanup
        client_manager.close()
        host_manager.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
