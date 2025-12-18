"""
Unit tests for GameServer command execution.

Tests the real execution of commands in GameServer, including
validation, state management, and broadcasting.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from network.server import GameServer
from network.commands import (
    PlaceTowerCommand,
    ModifyControlPointCommand,
    SendMercenaryCommand,
    ResearchCommand,
    ReadyCommand,
)
from network.manager import NetworkManager
from network.protocol import MessageType


class TestCommandHandlerRegistry:
    """Tests for command handler registry."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_server_has_command_handlers(self):
        """Test that GameServer initializes with command handlers."""
        server = GameServer()
        
        assert hasattr(server, '_command_handlers')
        assert isinstance(server._command_handlers, dict)
        assert 'PLACE_TOWER' in server._command_handlers
        assert 'MODIFY_CONTROL_POINT' in server._command_handlers
        assert 'SEND_MERCENARY' in server._command_handlers
        assert 'RESEARCH' in server._command_handlers
        assert 'READY' in server._command_handlers
    
    def test_server_has_game_state_attribute(self):
        """Test that GameServer has game state attribute."""
        server = GameServer()
        
        assert hasattr(server, '_game_state')
        assert server._game_state is None
    
    def test_set_game_state(self):
        """Test setting game state."""
        server = GameServer()
        mock_state = Mock()
        
        server.set_game_state(mock_state)
        
        assert server._game_state is mock_state


class TestPlaceTowerCommandHandler:
    """Tests for PlaceTowerCommand handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_place_tower_success(self):
        """Test successful tower placement."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10
        )
        
        result = server._handle_place_tower(command)
        
        assert result is True
    
    def test_place_tower_no_game_state(self):
        """Test tower placement fails without game state."""
        server = GameServer()
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10
        )
        
        result = server._handle_place_tower(command)
        
        assert result is False
    
    def test_place_tower_missing_tower_type(self):
        """Test tower placement fails with missing tower type."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type=None,
            x=5,
            y=10
        )
        
        result = server._handle_place_tower(command)
        
        assert result is False
    
    def test_place_tower_missing_coordinates(self):
        """Test tower placement fails with missing coordinates."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=None,
            y=10
        )
        
        result = server._handle_place_tower(command)
        
        assert result is False


class TestModifyControlPointCommandHandler:
    """Tests for ModifyControlPointCommand handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_modify_control_point_success(self):
        """Test successful control point modification."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = ModifyControlPointCommand(
            player_id="player1",
            index=2,
            x=15,
            y=20
        )
        
        result = server._handle_modify_control_point(command)
        
        assert result is True
    
    def test_modify_control_point_no_game_state(self):
        """Test control point modification fails without game state."""
        server = GameServer()
        
        command = ModifyControlPointCommand(
            player_id="player1",
            index=2,
            x=15,
            y=20
        )
        
        result = server._handle_modify_control_point(command)
        
        assert result is False
    
    def test_modify_control_point_missing_data(self):
        """Test control point modification fails with missing data."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = ModifyControlPointCommand(
            player_id="player1",
            index=None,
            x=15,
            y=20
        )
        
        result = server._handle_modify_control_point(command)
        
        assert result is False


class TestSendMercenaryCommandHandler:
    """Tests for SendMercenaryCommand handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_send_mercenary_success(self):
        """Test successful mercenary send."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = SendMercenaryCommand(
            player_id="player1",
            mercenary_type="student",
            target_player_id="player2"
        )
        
        result = server._handle_send_mercenary(command)
        
        assert result is True
    
    def test_send_mercenary_no_game_state(self):
        """Test mercenary send fails without game state."""
        server = GameServer()
        
        command = SendMercenaryCommand(
            player_id="player1",
            mercenary_type="student",
            target_player_id="player2"
        )
        
        result = server._handle_send_mercenary(command)
        
        assert result is False
    
    def test_send_mercenary_missing_type(self):
        """Test mercenary send fails with missing type."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = SendMercenaryCommand(
            player_id="player1",
            mercenary_type=None,
            target_player_id="player2"
        )
        
        result = server._handle_send_mercenary(command)
        
        assert result is False
    
    def test_send_mercenary_missing_target(self):
        """Test mercenary send fails with missing target."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = SendMercenaryCommand(
            player_id="player1",
            mercenary_type="student",
            target_player_id=None
        )
        
        result = server._handle_send_mercenary(command)
        
        assert result is False


class TestResearchCommandHandler:
    """Tests for ResearchCommand handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_research_success(self):
        """Test successful research."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = ResearchCommand(
            player_id="player1",
            research_type="lagrange"
        )
        
        result = server._handle_research(command)
        
        assert result is True
    
    def test_research_no_game_state(self):
        """Test research fails without game state."""
        server = GameServer()
        
        command = ResearchCommand(
            player_id="player1",
            research_type="lagrange"
        )
        
        result = server._handle_research(command)
        
        assert result is False
    
    def test_research_missing_type(self):
        """Test research fails with missing type."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        command = ResearchCommand(
            player_id="player1",
            research_type=None
        )
        
        result = server._handle_research(command)
        
        assert result is False


class TestReadyCommandHandler:
    """Tests for ReadyCommand handler."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_ready_success(self):
        """Test successful ready command."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = ReadyCommand(
            player_id="player1",
            is_ready=True
        )
        
        result = server._handle_ready(command)
        
        assert result is True
    
    def test_ready_no_game_state(self):
        """Test ready fails without game state."""
        server = GameServer()
        
        command = ReadyCommand(
            player_id="player1",
            is_ready=True
        )
        
        result = server._handle_ready(command)
        
        assert result is False
    
    def test_ready_false_state(self):
        """Test ready command with false state."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = ReadyCommand(
            player_id="player1",
            is_ready=False
        )
        
        result = server._handle_ready(command)
        
        assert result is True


class TestCommandExecution:
    """Tests for _execute_command method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_execute_unknown_command(self):
        """Test execution of unknown command type."""
        server = GameServer()
        mock_state = Mock()
        server.set_game_state(mock_state)
        
        # Create a mock command with an unknown type
        mock_command = Mock()
        mock_command.__class__.__name__ = 'UnknownCommand'
        mock_command.player_id = "player1"
        
        result = server._execute_command(mock_command)
        
        assert result is False
    
    def test_execute_command_calls_handler(self):
        """Test that execute_command calls the appropriate handler."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10
        )
        
        # Patch the handler in the registry instead of the method directly
        mock_handler = Mock(return_value=True)
        server._command_handlers['PLACE_TOWER'] = mock_handler
        
        result = server._execute_command(command)
        
        assert result is True
        mock_handler.assert_called_once_with(command)
    
    def test_execute_command_broadcasts_on_success(self):
        """Test that successful command execution triggers broadcast."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={'money': 1000})
        server.set_game_state(mock_state)
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10
        )
        
        with patch.object(server, '_broadcast_state_update') as mock_broadcast:
            result = server._execute_command(command)
            
            assert result is True
            mock_broadcast.assert_called_once()
    
    def test_execute_command_no_broadcast_on_failure(self):
        """Test that failed command execution doesn't trigger broadcast."""
        server = GameServer()
        # No game state, so command should fail
        
        command = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10
        )
        
        with patch.object(server, '_broadcast_state_update') as mock_broadcast:
            result = server._execute_command(command)
            
            assert result is False
            mock_broadcast.assert_not_called()


class TestBroadcastStateUpdate:
    """Tests for _broadcast_state_update method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_broadcast_with_game_state(self):
        """Test broadcast with valid game state."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={'money': 1000, 'lives': 10})
        server.set_game_state(mock_state)
        
        with patch.object(server.network_manager, 'send') as mock_send:
            server._broadcast_state_update()
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args.msg_type == MessageType.GAME_STATE
            assert call_args.payload == {'money': 1000, 'lives': 10}
    
    def test_broadcast_without_game_state(self):
        """Test broadcast without game state does nothing."""
        server = GameServer()
        
        with patch.object(server.network_manager, 'send') as mock_send:
            server._broadcast_state_update()
            
            mock_send.assert_not_called()
    
    def test_broadcast_without_to_dict_method(self):
        """Test broadcast when game state lacks to_dict method."""
        server = GameServer()
        mock_state = Mock(spec=[])  # No methods
        server.set_game_state(mock_state)
        
        with patch.object(server.network_manager, 'send') as mock_send:
            server._broadcast_state_update()
            
            mock_send.assert_not_called()


class TestProcessCommands:
    """Tests for process_commands method."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_process_commands_returns_tuple(self):
        """Test that process_commands returns a tuple."""
        server = GameServer()
        
        result = server.process_commands()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result == (0, 0)
    
    def test_process_commands_all_success(self):
        """Test process_commands with all successful commands."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        cmd1 = PlaceTowerCommand(player_id="player1", tower_type="dean", x=5, y=10)
        cmd2 = ReadyCommand(player_id="player1", is_ready=True)
        
        server.command_queue.put(cmd1)
        server.command_queue.put(cmd2)
        
        success, fail = server.process_commands()
        
        assert success == 2
        assert fail == 0
    
    def test_process_commands_all_fail(self):
        """Test process_commands with all failing commands."""
        server = GameServer()
        # No game state, so all commands fail
        
        cmd1 = PlaceTowerCommand(player_id="player1", tower_type="dean", x=5, y=10)
        cmd2 = ReadyCommand(player_id="player1", is_ready=True)
        
        server.command_queue.put(cmd1)
        server.command_queue.put(cmd2)
        
        success, fail = server.process_commands()
        
        assert success == 0
        assert fail == 2
    
    def test_process_commands_mixed_results(self):
        """Test process_commands with mixed success and failure."""
        server = GameServer()
        mock_state = Mock()
        mock_state.to_dict = Mock(return_value={})
        server.set_game_state(mock_state)
        
        # Valid command
        cmd1 = PlaceTowerCommand(player_id="player1", tower_type="dean", x=5, y=10)
        # Invalid command (missing data)
        cmd2 = PlaceTowerCommand(player_id="player1", tower_type=None, x=5, y=10)
        # Valid command
        cmd3 = ReadyCommand(player_id="player1", is_ready=True)
        
        server.command_queue.put(cmd1)
        server.command_queue.put(cmd2)
        server.command_queue.put(cmd3)
        
        success, fail = server.process_commands()
        
        assert success == 2
        assert fail == 1
    
    def test_process_commands_empty_queue(self):
        """Test process_commands with empty queue."""
        server = GameServer()
        
        success, fail = server.process_commands()
        
        assert success == 0
        assert fail == 0
        assert server.command_queue.empty()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
