"""
Unit tests for SyncEngine.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from multiplayer.sync_engine import SyncEngine, SyncMessage, SyncMessageType
from network.manager import NetworkManager
from network.protocol import Message, MessageType
from core.curve_state import CurveState


class TestSyncMessage:
    """Tests for SyncMessage serialization."""
    
    def test_sync_message_to_payload(self):
        """Test converting SyncMessage to payload."""
        msg = SyncMessage(
            sync_type=SyncMessageType.CURVE_POINT_ADD,
            data={'x': 5.0, 'y': 10.0},
            sequence=42
        )
        
        payload = msg.to_payload()
        
        assert payload['sync_type'] == 'CURVE_POINT_ADD'
        assert payload['data'] == {'x': 5.0, 'y': 10.0}
        assert payload['sequence'] == 42
    
    def test_sync_message_from_payload(self):
        """Test creating SyncMessage from payload."""
        payload = {
            'sync_type': 'CURVE_METHOD_CHANGE',
            'data': {'method': 'spline'},
            'sequence': 10
        }
        
        msg = SyncMessage.from_payload(payload)
        
        assert msg.sync_type == SyncMessageType.CURVE_METHOD_CHANGE
        assert msg.data == {'method': 'spline'}
        assert msg.sequence == 10
    
    def test_sync_message_roundtrip(self):
        """Test SyncMessage survives to_payload -> from_payload roundtrip."""
        original = SyncMessage(
            sync_type=SyncMessageType.FULL_SYNC,
            data={'control_points': [(0, 0), (10, 10)], 'interpolation_method': 'linear'},
            sequence=5
        )
        
        payload = original.to_payload()
        reconstructed = SyncMessage.from_payload(payload)
        
        assert reconstructed.sync_type == original.sync_type
        assert reconstructed.data == original.data
        assert reconstructed.sequence == original.sequence


class TestSyncEngine:
    """Tests for SyncEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
        self.network_manager = NetworkManager()
        self.sync_engine = SyncEngine(self.network_manager)
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_sync_engine_initial_state(self):
        """Test SyncEngine initial state."""
        assert self.sync_engine._sequence_number == 0
        assert self.sync_engine._observers == {}
    
    def test_sync_engine_subscribes_to_network(self):
        """Test that SyncEngine subscribes to NetworkManager."""
        # The subscription happens in __init__, so we can verify by checking
        # that the network manager has observers for GAME_STATE
        assert MessageType.GAME_STATE in self.network_manager._observers
        assert len(self.network_manager._observers[MessageType.GAME_STATE]) > 0
    
    def test_sync_full_curve_sends_all_points(self):
        """Test that sync_full_curve sends complete curve state."""
        # Mock the send method
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        # Create a curve state with points
        curve = CurveState()
        curve.add_point(0.0, 5.0)
        curve.add_point(10.0, 15.0)
        curve.set_method('lagrange')
        
        # Sync the curve
        result = self.sync_engine.sync_full_curve(curve)
        
        assert result is True
        assert self.network_manager.send.called
        
        # Verify the message content
        call_args = self.network_manager.send.call_args
        message = call_args[0][0]
        assert message.msg_type == MessageType.GAME_STATE
        assert message.payload['sync_type'] == 'FULL_SYNC'
        assert message.payload['data']['control_points'] == [(0.0, 5.0), (10.0, 15.0)]
        assert message.payload['data']['interpolation_method'] == 'lagrange'
    
    def test_sync_point_added(self):
        """Test syncing point addition."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_point_added(5.0, 10.0)
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'CURVE_POINT_ADD'
        assert message.payload['data'] == {'x': 5.0, 'y': 10.0}
    
    def test_sync_point_moved(self):
        """Test syncing point movement."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_point_moved(2, 7.5, 12.5)
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'CURVE_POINT_MOVE'
        assert message.payload['data'] == {'index': 2, 'x': 7.5, 'y': 12.5}
    
    def test_sync_point_removed(self):
        """Test syncing point removal."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_point_removed(1)
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'CURVE_POINT_REMOVE'
        assert message.payload['data'] == {'index': 1}
    
    def test_sync_method_changed(self):
        """Test syncing interpolation method change."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_method_changed('spline')
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'CURVE_METHOD_CHANGE'
        assert message.payload['data'] == {'method': 'spline'}
    
    def test_sync_tower_placed(self):
        """Test syncing tower placement."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_tower_placed('basic', 5, 10)
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'TOWER_PLACE'
        assert message.payload['data'] == {'tower_type': 'basic', 'x': 5, 'y': 10}
    
    def test_sync_tower_removed(self):
        """Test syncing tower removal."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        result = self.sync_engine.sync_tower_removed(5, 10)
        
        assert result is True
        message = self.network_manager.send.call_args[0][0]
        assert message.payload['sync_type'] == 'TOWER_REMOVE'
        assert message.payload['data'] == {'x': 5, 'y': 10}
    
    def test_observer_notification(self):
        """Test that observers are notified of sync messages."""
        received_messages = []
        
        def callback(msg):
            received_messages.append(msg)
        
        # Subscribe to CURVE_POINT_ADD
        self.sync_engine.subscribe(SyncMessageType.CURVE_POINT_ADD, callback)
        
        # Simulate receiving a network message
        network_msg = Message(
            msg_type=MessageType.GAME_STATE,
            payload={
                'sync_type': 'CURVE_POINT_ADD',
                'data': {'x': 3.0, 'y': 7.0},
                'sequence': 1
            }
        )
        
        self.sync_engine._on_network_message(network_msg)
        
        assert len(received_messages) == 1
        assert received_messages[0].sync_type == SyncMessageType.CURVE_POINT_ADD
        assert received_messages[0].data == {'x': 3.0, 'y': 7.0}
    
    def test_remote_curve_update_applied(self):
        """Test that remote curve updates are properly parsed."""
        received_syncs = []
        
        def on_full_sync(msg):
            received_syncs.append(msg)
        
        self.sync_engine.subscribe(SyncMessageType.FULL_SYNC, on_full_sync)
        
        # Simulate receiving a full sync message
        network_msg = Message(
            msg_type=MessageType.GAME_STATE,
            payload={
                'sync_type': 'FULL_SYNC',
                'data': {
                    'control_points': [(0, 0), (5, 10), (10, 5)],
                    'interpolation_method': 'spline'
                },
                'sequence': 0
            }
        )
        
        self.sync_engine._on_network_message(network_msg)
        
        assert len(received_syncs) == 1
        assert received_syncs[0].data['control_points'] == [(0, 0), (5, 10), (10, 5)]
        assert received_syncs[0].data['interpolation_method'] == 'spline'
    
    def test_sequence_numbers_increment(self):
        """Test that sequence numbers increment correctly."""
        self.network_manager.send = MagicMock(return_value=True)
        self.network_manager._is_connected = True
        
        # Send multiple messages
        self.sync_engine.sync_point_added(1.0, 2.0)
        self.sync_engine.sync_point_added(3.0, 4.0)
        self.sync_engine.sync_method_changed('linear')
        
        # Check that sequence numbers incremented
        calls = self.network_manager.send.call_args_list
        assert calls[0][0][0].payload['sequence'] == 0
        assert calls[1][0][0].payload['sequence'] == 1
        assert calls[2][0][0].payload['sequence'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
