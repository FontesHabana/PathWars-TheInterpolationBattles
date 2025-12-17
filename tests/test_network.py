"""
Unit tests for the network module.

Tests protocol serialization/deserialization, NetworkManager with mocked sockets,
and full integration with server + client threads.
"""

import pytest
import sys
import os
import time
import threading
from unittest.mock import Mock, MagicMock, patch
import socket as socket_module

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from network.protocol import Message, MessageType, Serializer
from network.manager import NetworkManager


class TestProtocol:
    """Test protocol serialization and deserialization."""
    
    def test_message_creation(self):
        """Test Message dataclass creation."""
        msg = Message(
            msg_type=MessageType.HANDSHAKE,
            payload={'player_name': 'Alice'},
            sender_id='player1'
        )
        
        assert msg.msg_type == MessageType.HANDSHAKE
        assert msg.payload['player_name'] == 'Alice'
        assert msg.sender_id == 'player1'
    
    def test_message_to_dict(self):
        """Test Message conversion to dictionary."""
        msg = Message(
            msg_type=MessageType.ROUTE_DATA,
            payload={'points': [(0, 0), (10, 10)]},
            sender_id='player2'
        )
        
        msg_dict = msg.to_dict()
        
        assert msg_dict['msg_type'] == 'route_data'
        assert msg_dict['payload']['points'] == [(0, 0), (10, 10)]
        assert msg_dict['sender_id'] == 'player2'
    
    def test_message_from_dict(self):
        """Test Message creation from dictionary."""
        msg_dict = {
            'msg_type': 'game_state',
            'payload': {'hp': 100, 'money': 500},
            'sender_id': 'player3'
        }
        
        msg = Message.from_dict(msg_dict)
        
        assert msg.msg_type == MessageType.GAME_STATE
        assert msg.payload['hp'] == 100
        assert msg.payload['money'] == 500
        assert msg.sender_id == 'player3'
    
    def test_json_serialization(self):
        """Test JSON serialization and deserialization."""
        original = Message(
            msg_type=MessageType.TOWER_PLACEMENT,
            payload={'x': 5, 'y': 10, 'tower_type': 'cannon'},
            sender_id='player1'
        )
        
        serialized = Serializer.serialize_json(original)
        
        # Check length prefix
        assert len(serialized) >= 4
        length = int.from_bytes(serialized[:4], byteorder='big')
        assert length == len(serialized) - 4
        
        # Deserialize without length prefix
        deserialized = Serializer.deserialize_json(serialized[4:])
        
        assert deserialized.msg_type == original.msg_type
        assert deserialized.payload == original.payload
        assert deserialized.sender_id == original.sender_id
    
    def test_pickle_serialization(self):
        """Test Pickle serialization and deserialization."""
        original = Message(
            msg_type=MessageType.ACK,
            payload={'status': 'ok', 'timestamp': 12345},
            sender_id='player2'
        )
        
        serialized = Serializer.serialize_pickle(original)
        
        # Check length prefix
        assert len(serialized) >= 4
        length = int.from_bytes(serialized[:4], byteorder='big')
        assert length == len(serialized) - 4
        
        # Deserialize without length prefix
        deserialized = Serializer.deserialize_pickle(serialized[4:])
        
        assert deserialized.msg_type == original.msg_type
        assert deserialized.payload == original.payload
        assert deserialized.sender_id == original.sender_id
    
    def test_generic_serialize_json(self):
        """Test generic serialize method with JSON."""
        msg = Message(
            msg_type=MessageType.DISCONNECT,
            payload={'reason': 'timeout'}
        )
        
        serialized = Serializer.serialize(msg, use_json=True)
        deserialized = Serializer.deserialize(serialized[4:], use_json=True)
        
        assert deserialized.msg_type == msg.msg_type
        assert deserialized.payload == msg.payload
    
    def test_generic_serialize_pickle(self):
        """Test generic serialize method with Pickle."""
        msg = Message(
            msg_type=MessageType.HANDSHAKE,
            payload={'version': '1.0', 'features': [1, 2, 3]}
        )
        
        serialized = Serializer.serialize(msg, use_json=False)
        deserialized = Serializer.deserialize(serialized[4:], use_json=False)
        
        assert deserialized.msg_type == msg.msg_type
        assert deserialized.payload == msg.payload


class TestNetworkManagerMocked:
    """Test NetworkManager with mocked sockets."""
    
    def setup_method(self):
        """Reset singleton before each test."""
        NetworkManager._instance = None
    
    def test_singleton_pattern(self):
        """Test that NetworkManager implements singleton pattern."""
        nm1 = NetworkManager()
        nm2 = NetworkManager()
        
        assert nm1 is nm2
    
    def test_observer_registration(self):
        """Test observer registration and unregistration."""
        nm = NetworkManager()
        
        callback = Mock()
        nm.register_observer(MessageType.HANDSHAKE, callback)
        
        assert MessageType.HANDSHAKE in nm.observers
        assert nm.observers[MessageType.HANDSHAKE] == callback
        
        nm.unregister_observer(MessageType.HANDSHAKE)
        assert MessageType.HANDSHAKE not in nm.observers
    
    def test_notify_observers(self):
        """Test that observers are notified correctly."""
        nm = NetworkManager()
        
        callback = Mock()
        nm.register_observer(MessageType.GAME_STATE, callback)
        
        msg = Message(
            msg_type=MessageType.GAME_STATE,
            payload={'hp': 80}
        )
        
        nm._notify_observers(msg)
        callback.assert_called_once_with(msg)
    
    def test_send_without_connection(self):
        """Test that send fails when not connected."""
        nm = NetworkManager()
        
        msg = Message(
            msg_type=MessageType.ACK,
            payload={}
        )
        
        result = nm.send(msg)
        assert result is False
    
    def test_is_connected(self):
        """Test connection status checking."""
        nm = NetworkManager()
        
        assert nm.is_connected() is False
        
        nm.connected = True
        assert nm.is_connected() is True
    
    def test_get_role(self):
        """Test role retrieval."""
        nm = NetworkManager()
        
        assert nm.get_role() is None
        
        nm.role = 'host'
        assert nm.get_role() == 'host'
        
        nm.role = 'client'
        assert nm.get_role() == 'client'


class TestNetworkManagerIntegration:
    """Integration tests with real sockets in localhost."""
    
    def setup_method(self):
        """Reset singleton and prepare for each test."""
        NetworkManager._instance = None
        self.host = None
        self.client = None
        self.received_messages = []
        self.host_port = 15555  # Use non-standard port for testing
    
    def teardown_method(self):
        """Clean up after each test."""
        if self.host:
            self.host.close()
        if self.client:
            self.client.close()
        NetworkManager._instance = None
    
    def test_host_client_connection(self):
        """Test that host and client can connect to each other."""
        # Start host in a thread
        def start_host():
            self.host = NetworkManager()
            self.host.start_host(port=self.host_port)
        
        host_thread = threading.Thread(target=start_host, daemon=True)
        host_thread.start()
        
        # Give host time to start
        time.sleep(0.5)
        
        # Connect client
        self.client = NetworkManager()
        # Create new instance for client (bypassing singleton for testing)
        NetworkManager._instance = None
        self.client = NetworkManager()
        result = self.client.connect_to_host('127.0.0.1', port=self.host_port)
        
        assert result is True
        assert self.client.is_connected()
        
        # Wait for host thread to accept
        host_thread.join(timeout=2.0)
        
        # Give connection time to establish
        time.sleep(0.5)
    
    def test_send_message_host_to_client(self):
        """Test sending message from host to client."""
        received = []
        
        def on_message(msg: Message):
            received.append(msg)
        
        # Start host
        def start_host():
            self.host = NetworkManager()
            self.host.start_host(port=self.host_port)
            time.sleep(0.5)
            
            # Send message
            msg = Message(
                msg_type=MessageType.HANDSHAKE,
                payload={'greeting': 'Hello Client'}
            )
            self.host.send(msg)
        
        host_thread = threading.Thread(target=start_host, daemon=True)
        host_thread.start()
        
        time.sleep(0.5)
        
        # Connect client and register observer
        NetworkManager._instance = None
        self.client = NetworkManager()
        self.client.register_observer(MessageType.HANDSHAKE, on_message)
        self.client.connect_to_host('127.0.0.1', port=self.host_port)
        
        # Wait for message
        time.sleep(1.0)
        
        assert len(received) > 0
        assert received[0].msg_type == MessageType.HANDSHAKE
        assert received[0].payload['greeting'] == 'Hello Client'
        
        host_thread.join(timeout=2.0)
    
    def test_send_message_client_to_host(self):
        """Test sending message from client to host."""
        received = []
        
        def on_message(msg: Message):
            received.append(msg)
        
        # Start host with observer
        def start_host():
            self.host = NetworkManager()
            self.host.register_observer(MessageType.ROUTE_DATA, on_message)
            self.host.start_host(port=self.host_port)
            time.sleep(2.0)  # Keep alive to receive message
        
        host_thread = threading.Thread(target=start_host, daemon=True)
        host_thread.start()
        
        time.sleep(0.5)
        
        # Connect client
        NetworkManager._instance = None
        self.client = NetworkManager()
        self.client.connect_to_host('127.0.0.1', port=self.host_port)
        
        time.sleep(0.5)
        
        # Send message from client
        msg = Message(
            msg_type=MessageType.ROUTE_DATA,
            payload={'points': [(0, 0), (5, 5), (10, 10)]}
        )
        self.client.send(msg)
        
        # Wait for host to receive
        time.sleep(1.0)
        
        assert len(received) > 0
        assert received[0].msg_type == MessageType.ROUTE_DATA
        # JSON converts tuples to lists, so compare as lists
        assert received[0].payload['points'] == [[0, 0], [5, 5], [10, 10]]
        
        host_thread.join(timeout=3.0)
    
    def test_bidirectional_communication(self):
        """Test bidirectional message exchange."""
        host_received = []
        client_received = []
        
        def on_host_message(msg: Message):
            host_received.append(msg)
        
        def on_client_message(msg: Message):
            client_received.append(msg)
        
        # Start host
        def start_host():
            self.host = NetworkManager()
            self.host.register_observer(MessageType.ACK, on_host_message)
            self.host.start_host(port=self.host_port)
            time.sleep(0.5)
            
            # Send message to client
            msg = Message(
                msg_type=MessageType.GAME_STATE,
                payload={'phase': 'planning'}
            )
            self.host.send(msg)
            time.sleep(2.0)
        
        host_thread = threading.Thread(target=start_host, daemon=True)
        host_thread.start()
        
        time.sleep(0.5)
        
        # Connect client
        NetworkManager._instance = None
        self.client = NetworkManager()
        self.client.register_observer(MessageType.GAME_STATE, on_client_message)
        self.client.connect_to_host('127.0.0.1', port=self.host_port)
        
        time.sleep(0.5)
        
        # Send acknowledgment from client
        ack_msg = Message(
            msg_type=MessageType.ACK,
            payload={'status': 'ready'}
        )
        self.client.send(ack_msg)
        
        # Wait for messages
        time.sleep(1.5)
        
        # Verify both sides received messages
        assert len(client_received) > 0
        assert client_received[0].msg_type == MessageType.GAME_STATE
        
        assert len(host_received) > 0
        assert host_received[0].msg_type == MessageType.ACK
        
        host_thread.join(timeout=3.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
