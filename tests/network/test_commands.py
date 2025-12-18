"""
Unit tests for Command Pattern implementation.

Tests command serialization, deserialization, and server/client instantiation.
"""

import time

import pytest

from network.commands import (
    GameCommand,
    PlaceTowerCommand,
    ModifyControlPointCommand,
    SendMercenaryCommand,
    ResearchCommand,
    ReadyCommand,
    deserialize_command,
)
from network.server import GameServer
from network.client import GameClient
from network.manager import NetworkManager


class TestPlaceTowerCommand:
    """Tests for PlaceTowerCommand."""
    
    def test_creation(self):
        """Test creating a PlaceTowerCommand."""
        cmd = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10,
        )
        
        assert cmd.player_id == "player1"
        assert cmd.tower_type == "dean"
        assert cmd.x == 5
        assert cmd.y == 10
        assert isinstance(cmd.timestamp, float)
    
    def test_to_dict(self):
        """Test serializing PlaceTowerCommand to dictionary."""
        cmd = PlaceTowerCommand(
            player_id="player1",
            timestamp=1234567890.0,
            tower_type="calculus",
            x=3,
            y=7,
        )
        
        result = cmd.to_dict()
        
        assert result["command_type"] == "PlaceTowerCommand"
        assert result["player_id"] == "player1"
        assert result["timestamp"] == 1234567890.0
        assert result["tower_type"] == "calculus"
        assert result["x"] == 3
        assert result["y"] == 7
    
    def test_from_dict(self):
        """Test deserializing PlaceTowerCommand from dictionary."""
        data = {
            "command_type": "PlaceTowerCommand",
            "player_id": "player2",
            "timestamp": 9999.0,
            "tower_type": "physics",
            "x": 12,
            "y": 8,
        }
        
        cmd = PlaceTowerCommand.from_dict(data)
        
        assert cmd.player_id == "player2"
        assert cmd.timestamp == 9999.0
        assert cmd.tower_type == "physics"
        assert cmd.x == 12
        assert cmd.y == 8
    
    def test_roundtrip(self):
        """Test command survives to_dict -> from_dict roundtrip."""
        original = PlaceTowerCommand(
            player_id="player3",
            timestamp=5555.5,
            tower_type="algebra",
            x=1,
            y=2,
        )
        
        reconstructed = PlaceTowerCommand.from_dict(original.to_dict())
        
        assert reconstructed.player_id == original.player_id
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.tower_type == original.tower_type
        assert reconstructed.x == original.x
        assert reconstructed.y == original.y


class TestModifyControlPointCommand:
    """Tests for ModifyControlPointCommand."""
    
    def test_creation(self):
        """Test creating a ModifyControlPointCommand."""
        cmd = ModifyControlPointCommand(
            player_id="player1",
            index=2,
            x=15,
            y=20,
        )
        
        assert cmd.player_id == "player1"
        assert cmd.index == 2
        assert cmd.x == 15
        assert cmd.y == 20
    
    def test_to_dict(self):
        """Test serializing ModifyControlPointCommand to dictionary."""
        cmd = ModifyControlPointCommand(
            player_id="player1",
            timestamp=1111.0,
            index=0,
            x=5,
            y=5,
        )
        
        result = cmd.to_dict()
        
        assert result["command_type"] == "ModifyControlPointCommand"
        assert result["player_id"] == "player1"
        assert result["timestamp"] == 1111.0
        assert result["index"] == 0
        assert result["x"] == 5
        assert result["y"] == 5
    
    def test_roundtrip(self):
        """Test command survives to_dict -> from_dict roundtrip."""
        original = ModifyControlPointCommand(
            player_id="player2",
            timestamp=2222.2,
            index=3,
            x=10,
            y=15,
        )
        
        reconstructed = ModifyControlPointCommand.from_dict(original.to_dict())
        
        assert reconstructed.player_id == original.player_id
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.index == original.index
        assert reconstructed.x == original.x
        assert reconstructed.y == original.y


class TestSendMercenaryCommand:
    """Tests for SendMercenaryCommand."""
    
    def test_creation(self):
        """Test creating a SendMercenaryCommand."""
        cmd = SendMercenaryCommand(
            player_id="player1",
            mercenary_type="student",
            target_player_id="player2",
        )
        
        assert cmd.player_id == "player1"
        assert cmd.mercenary_type == "student"
        assert cmd.target_player_id == "player2"
    
    def test_to_dict(self):
        """Test serializing SendMercenaryCommand to dictionary."""
        cmd = SendMercenaryCommand(
            player_id="player1",
            timestamp=3333.0,
            mercenary_type="variable_x",
            target_player_id="player2",
        )
        
        result = cmd.to_dict()
        
        assert result["command_type"] == "SendMercenaryCommand"
        assert result["player_id"] == "player1"
        assert result["timestamp"] == 3333.0
        assert result["mercenary_type"] == "variable_x"
        assert result["target_player_id"] == "player2"
    
    def test_roundtrip(self):
        """Test command survives to_dict -> from_dict roundtrip."""
        original = SendMercenaryCommand(
            player_id="player3",
            timestamp=4444.4,
            mercenary_type="constant_pi",
            target_player_id="player4",
        )
        
        reconstructed = SendMercenaryCommand.from_dict(original.to_dict())
        
        assert reconstructed.player_id == original.player_id
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.mercenary_type == original.mercenary_type
        assert reconstructed.target_player_id == original.target_player_id


class TestResearchCommand:
    """Tests for ResearchCommand."""
    
    def test_creation(self):
        """Test creating a ResearchCommand."""
        cmd = ResearchCommand(
            player_id="player1",
            research_type="lagrange",
        )
        
        assert cmd.player_id == "player1"
        assert cmd.research_type == "lagrange"
    
    def test_to_dict(self):
        """Test serializing ResearchCommand to dictionary."""
        cmd = ResearchCommand(
            player_id="player1",
            timestamp=5555.0,
            research_type="spline",
        )
        
        result = cmd.to_dict()
        
        assert result["command_type"] == "ResearchCommand"
        assert result["player_id"] == "player1"
        assert result["timestamp"] == 5555.0
        assert result["research_type"] == "spline"
    
    def test_roundtrip(self):
        """Test command survives to_dict -> from_dict roundtrip."""
        original = ResearchCommand(
            player_id="player2",
            timestamp=6666.6,
            research_type="tangent_control",
        )
        
        reconstructed = ResearchCommand.from_dict(original.to_dict())
        
        assert reconstructed.player_id == original.player_id
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.research_type == original.research_type


class TestReadyCommand:
    """Tests for ReadyCommand."""
    
    def test_creation(self):
        """Test creating a ReadyCommand."""
        cmd = ReadyCommand(
            player_id="player1",
            is_ready=True,
        )
        
        assert cmd.player_id == "player1"
        assert cmd.is_ready is True
    
    def test_to_dict(self):
        """Test serializing ReadyCommand to dictionary."""
        cmd = ReadyCommand(
            player_id="player1",
            timestamp=7777.0,
            is_ready=False,
        )
        
        result = cmd.to_dict()
        
        assert result["command_type"] == "ReadyCommand"
        assert result["player_id"] == "player1"
        assert result["timestamp"] == 7777.0
        assert result["is_ready"] is False
    
    def test_roundtrip(self):
        """Test command survives to_dict -> from_dict roundtrip."""
        original = ReadyCommand(
            player_id="player2",
            timestamp=8888.8,
            is_ready=True,
        )
        
        reconstructed = ReadyCommand.from_dict(original.to_dict())
        
        assert reconstructed.player_id == original.player_id
        assert reconstructed.timestamp == original.timestamp
        assert reconstructed.is_ready == original.is_ready


class TestDeserializeCommand:
    """Tests for deserialize_command function."""
    
    def test_deserialize_place_tower(self):
        """Test deserializing a PlaceTowerCommand."""
        data = {
            "command_type": "PlaceTowerCommand",
            "player_id": "player1",
            "timestamp": 1000.0,
            "tower_type": "dean",
            "x": 5,
            "y": 10,
        }
        
        cmd = deserialize_command(data)
        
        assert isinstance(cmd, PlaceTowerCommand)
        assert cmd.player_id == "player1"
        assert cmd.tower_type == "dean"
    
    def test_deserialize_modify_control_point(self):
        """Test deserializing a ModifyControlPointCommand."""
        data = {
            "command_type": "ModifyControlPointCommand",
            "player_id": "player2",
            "timestamp": 2000.0,
            "index": 1,
            "x": 8,
            "y": 12,
        }
        
        cmd = deserialize_command(data)
        
        assert isinstance(cmd, ModifyControlPointCommand)
        assert cmd.player_id == "player2"
        assert cmd.index == 1
    
    def test_deserialize_send_mercenary(self):
        """Test deserializing a SendMercenaryCommand."""
        data = {
            "command_type": "SendMercenaryCommand",
            "player_id": "player3",
            "timestamp": 3000.0,
            "mercenary_type": "student",
            "target_player_id": "player4",
        }
        
        cmd = deserialize_command(data)
        
        assert isinstance(cmd, SendMercenaryCommand)
        assert cmd.player_id == "player3"
        assert cmd.mercenary_type == "student"
    
    def test_deserialize_research(self):
        """Test deserializing a ResearchCommand."""
        data = {
            "command_type": "ResearchCommand",
            "player_id": "player4",
            "timestamp": 4000.0,
            "research_type": "lagrange",
        }
        
        cmd = deserialize_command(data)
        
        assert isinstance(cmd, ResearchCommand)
        assert cmd.player_id == "player4"
        assert cmd.research_type == "lagrange"
    
    def test_deserialize_ready(self):
        """Test deserializing a ReadyCommand."""
        data = {
            "command_type": "ReadyCommand",
            "player_id": "player5",
            "timestamp": 5000.0,
            "is_ready": True,
        }
        
        cmd = deserialize_command(data)
        
        assert isinstance(cmd, ReadyCommand)
        assert cmd.player_id == "player5"
        assert cmd.is_ready is True
    
    def test_deserialize_unknown_command_type(self):
        """Test that unknown command type raises error."""
        data = {
            "command_type": "UnknownCommand",
            "player_id": "player1",
            "timestamp": 1000.0,
        }
        
        with pytest.raises(KeyError):
            deserialize_command(data)


class TestGameServer:
    """Tests for GameServer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_instantiation(self):
        """Test that GameServer can be instantiated."""
        server = GameServer()
        
        assert server is not None
        assert isinstance(server, GameServer)
        assert server.is_running is False
        assert server.network_manager is not None
        assert server.command_queue is not None
    
    def test_start_success(self):
        """Test that server can be started."""
        server = GameServer()
        
        # Use a random high port for testing
        result = server.start(55558)
        
        assert result is True
        assert server.is_running is True
        
        # Clean up
        server.stop()
    
    def test_start_already_running(self):
        """Test that starting an already running server returns False."""
        server = GameServer()
        
        server.start(55559)
        result = server.start(55559)
        
        assert result is False
        
        # Clean up
        server.stop()
    
    def test_process_commands_empty_queue(self):
        """Test processing commands with empty queue."""
        server = GameServer()
        
        processed = server.process_commands()
        
        assert processed == 0
    
    def test_process_commands_with_commands(self):
        """Test processing commands in the queue."""
        server = GameServer()
        
        # Manually add commands to queue
        cmd1 = PlaceTowerCommand(player_id="player1", tower_type="dean", x=5, y=10)
        cmd2 = ReadyCommand(player_id="player2", is_ready=True)
        
        server.command_queue.put(cmd1)
        server.command_queue.put(cmd2)
        
        processed = server.process_commands()
        
        assert processed == 2
        assert server.command_queue.empty()
    
    def test_stop(self):
        """Test stopping the server."""
        server = GameServer()
        server.start(55560)
        
        server.stop()
        
        assert server.is_running is False


class TestGameClient:
    """Tests for GameClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_instantiation(self):
        """Test that GameClient can be instantiated."""
        client = GameClient(player_id="player1")
        
        assert client is not None
        assert isinstance(client, GameClient)
        assert client.player_id == "player1"
        assert client.is_connected is False
        assert client.network_manager is not None
    
    def test_connect_failure(self):
        """Test connection failure when no server is running."""
        client = GameClient(player_id="player1")
        
        # Try to connect to non-existent server
        result = client.connect("127.0.0.1", 55561, timeout=0.5)
        
        assert result is False
        assert client.is_connected is False
        
        # Clean up
        client.disconnect()
    
    def test_send_command_not_connected(self):
        """Test that sending command when not connected fails."""
        client = GameClient(player_id="player1")
        
        cmd = PlaceTowerCommand(player_id="player1", tower_type="dean", x=5, y=10)
        result = client.send_command(cmd)
        
        assert result is False
    
    def test_disconnect(self):
        """Test disconnecting the client."""
        client = GameClient(player_id="player1")
        
        client.disconnect()
        
        assert client.is_connected is False


class TestServerClientIntegration:
    """Integration tests for GameServer and GameClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        NetworkManager.reset_instance()
    
    def teardown_method(self):
        """Clean up after tests."""
        NetworkManager.reset_instance()
    
    def test_client_connects_to_server(self):
        """Test that a client can connect to a server."""
        server = GameServer()
        port = 55562
        
        # Start server
        assert server.start(port) is True
        
        # Create client with separate NetworkManager instance
        # Note: We bypass the singleton pattern here because we need both
        # a server and client NetworkManager in the same process for testing.
        # This is a known limitation of the singleton pattern in test scenarios.
        NetworkManager._instance = None
        client = GameClient(player_id="player1")
        
        # Give server time to start
        time.sleep(0.1)
        
        # Connect client
        assert client.connect("127.0.0.1", port) is True
        
        # Give time for connection to be established
        time.sleep(0.2)
        
        assert client.is_connected is True
        assert server.network_manager.is_connected is True
        
        # Clean up
        client.disconnect()
        server.stop()
    
    def test_client_sends_command_to_server(self):
        """Test that client can send commands to server."""
        server = GameServer()
        port = 55563
        
        # Start server
        assert server.start(port) is True
        
        # Create client with separate NetworkManager instance
        # Note: We bypass the singleton pattern here because we need both
        # a server and client NetworkManager in the same process for testing.
        # This is a known limitation of the singleton pattern in test scenarios.
        NetworkManager._instance = None
        client = GameClient(player_id="player1")
        
        time.sleep(0.1)
        assert client.connect("127.0.0.1", port) is True
        time.sleep(0.2)
        
        # Send command
        cmd = PlaceTowerCommand(
            player_id="player1",
            tower_type="dean",
            x=5,
            y=10,
        )
        assert client.send_command(cmd) is True
        
        # Give time for message to be received and queued
        time.sleep(0.2)
        
        # Process commands on server
        processed = server.process_commands()
        
        # Should have received and processed the command
        assert processed >= 1
        
        # Clean up
        client.disconnect()
        server.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
