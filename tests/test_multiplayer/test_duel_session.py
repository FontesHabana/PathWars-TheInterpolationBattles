"""
Unit tests for DuelSession.
"""

import sys
import os
import pytest
import time
from unittest.mock import MagicMock, Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from multiplayer.duel_session import DuelSession, DuelPhase, DuelPlayer
from multiplayer.player_role import PlayerRole
from network.manager import NetworkManager


class TestDuelSession:
    """Tests for DuelSession."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
        self.session = DuelSession()
    
    def teardown_method(self):
        """Clean up after tests."""
        if hasattr(self, 'session'):
            self.session.disconnect()
        NetworkManager.reset_instance()
    
    def test_initial_state_is_lobby(self):
        """Test that initial phase is LOBBY."""
        assert self.session.phase == DuelPhase.LOBBY
        assert self.session.role is None
        assert self.session.local_player is None
        assert self.session.remote_player is None
    
    @patch.object(NetworkManager, 'start_host')
    def test_host_game_success(self, mock_start_host):
        """Test successful game hosting."""
        mock_start_host.return_value = True
        
        result = self.session.host_game(12345)
        
        assert result is True
        assert self.session.phase == DuelPhase.WAITING_OPPONENT
        mock_start_host.assert_called_once_with(12345)
    
    @patch.object(NetworkManager, 'start_host')
    def test_host_game_sets_role_to_host(self, mock_start_host):
        """Test that hosting sets role to HOST."""
        mock_start_host.return_value = True
        
        self.session.host_game(12345)
        
        assert self.session.role == PlayerRole.HOST
    
    @patch.object(NetworkManager, 'start_host')
    def test_host_game_failure_returns_to_lobby(self, mock_start_host):
        """Test that failed hosting returns to LOBBY."""
        mock_start_host.return_value = False
        
        result = self.session.host_game(12345)
        
        assert result is False
        assert self.session.phase == DuelPhase.LOBBY
    
    @patch.object(NetworkManager, 'connect_to_host')
    def test_join_game_success(self, mock_connect):
        """Test successful game joining."""
        mock_connect.return_value = True
        
        result = self.session.join_game("127.0.0.1", 12345)
        
        assert result is True
        mock_connect.assert_called_once_with("127.0.0.1", 12345)
    
    @patch.object(NetworkManager, 'connect_to_host')
    def test_join_game_sets_role_to_client(self, mock_connect):
        """Test that joining sets role to CLIENT."""
        mock_connect.return_value = True
        
        self.session.join_game("127.0.0.1", 12345)
        
        assert self.session.role == PlayerRole.CLIENT
    
    @patch.object(NetworkManager, 'connect_to_host')
    def test_join_game_failure_returns_to_lobby(self, mock_connect):
        """Test that failed joining returns to LOBBY."""
        mock_connect.return_value = False
        
        result = self.session.join_game("127.0.0.1", 12345)
        
        assert result is False
        assert self.session.phase == DuelPhase.LOBBY
    
    def test_connection_triggers_syncing_phase(self):
        """Test that connection triggers SYNCING phase and then PLANNING."""
        # Simulate connection
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # After initialization, phase should be PLANNING (sync happens quickly)
        assert self.session.phase == DuelPhase.PLANNING
    
    def test_initial_sync_creates_curves(self):
        """Test that initial sync creates curve states."""
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # After initialization, should be in PLANNING phase
        assert self.session.phase == DuelPhase.PLANNING
        assert self.session.local_edit_curve is not None
        assert self.session.local_incoming_curve is not None
        assert self.session.local_player is not None
        assert self.session.remote_player is not None
    
    def test_set_ready_sends_sync(self):
        """Test that set_ready sends sync message."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # Mock the sync engine's send
        self.session.sync_engine._send_sync = MagicMock(return_value=True)
        
        # Set ready
        self.session.set_ready(True)
        
        assert self.session.local_player.ready is True
        assert self.session.sync_engine._send_sync.called
    
    def test_both_ready_triggers_battle(self):
        """Test that both players ready triggers BATTLE phase."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # Mock sync engine
        self.session.sync_engine._send_sync = MagicMock(return_value=True)
        
        # Set both players ready
        self.session.local_player.ready = True
        self.session.remote_player.ready = True
        
        # Trigger ready check
        self.session.set_ready(True)
        
        assert self.session.phase == DuelPhase.BATTLE
    
    def test_report_damage_updates_lives(self):
        """Test that report_damage is sent via sync."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # Mock sync engine
        self.session.sync_engine.sync_game_event = MagicMock(return_value=True)
        
        # Report damage
        self.session.report_damage(2)
        
        self.session.sync_engine.sync_game_event.assert_called_once_with('damage', {'damage': 2})
    
    def test_report_damage_syncs_to_opponent(self):
        """Test that damage is synced to opponent."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        initial_lives = self.session.local_player.lives
        
        # Simulate receiving damage from opponent
        from multiplayer.sync_engine import SyncMessage, SyncMessageType
        damage_msg = SyncMessage(
            sync_type=SyncMessageType.GAME_EVENT,
            data={'event_type': 'damage', 'event_data': {'damage': 3}}
        )
        
        self.session._on_game_event(damage_msg)
        
        assert self.session.local_player.lives == initial_lives - 3
    
    def test_round_completion(self):
        """Test round completion handling."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        self.session._phase = DuelPhase.BATTLE
        
        # Mock sync
        self.session.sync_engine.sync_game_event = MagicMock(return_value=True)
        
        # Report round complete
        self.session.report_round_complete()
        
        assert self.session.phase == DuelPhase.PLANNING
        assert self.session.current_round == 2
    
    def test_match_end_after_5_rounds(self):
        """Test that match ends after 5 rounds."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        self.session._current_round = 5
        self.session._phase = DuelPhase.BATTLE
        
        # Complete round 5
        self.session._handle_round_complete()
        
        assert self.session.phase == DuelPhase.MATCH_END
    
    def test_match_end_when_no_lives(self):
        """Test that match ends when local player has no lives."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        self.session._phase = DuelPhase.BATTLE
        
        # Lose all lives
        self.session.local_player.lives = 0
        
        # Complete round
        self.session._handle_round_complete()
        
        assert self.session.phase == DuelPhase.MATCH_END
    
    def test_disconnect_cleanup(self):
        """Test that disconnect properly cleans up."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # Disconnect
        self.session.disconnect()
        
        assert self.session.phase == DuelPhase.DISCONNECTED
        assert self.session._network_manager.is_connected is False
    
    def test_asymmetric_curves_setup(self):
        """Test that asymmetric curves are set up correctly."""
        # Initialize session
        self.session._role = PlayerRole.HOST
        self.session._on_connection_change(True)
        
        # Verify curves exist and are different objects
        assert self.session.local_edit_curve is not None
        assert self.session.local_incoming_curve is not None
        assert self.session.local_edit_curve is not self.session.local_incoming_curve
        
        # Verify player curve assignments
        assert self.session.local_player.curve_state is self.session.local_edit_curve
        assert self.session.remote_player.curve_state is self.session.local_incoming_curve


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
