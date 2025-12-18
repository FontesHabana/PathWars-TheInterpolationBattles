"""
Command Pattern for Game Actions.

Implements the Command pattern for network synchronization.
Each command encapsulates a game action that can be serialized,
transmitted over the network, and executed on the server.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class GameCommand(ABC):
    """
    Abstract base class for game commands.
    
    All game commands must implement serialization methods
    and contain player identification and timing information.
    
    Attributes:
        player_id: Identifier of the player issuing the command.
        timestamp: Unix timestamp when the command was created.
    """
    
    player_id: str
    timestamp: float = field(default_factory=time.time)
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the command to a dictionary.
        
        Returns:
            Dictionary representation of the command.
        """
        pass
    
    @staticmethod
    @abstractmethod
    def from_dict(data: Dict[str, Any]) -> "GameCommand":
        """
        Deserialize a command from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A GameCommand instance.
        """
        pass


@dataclass
class PlaceTowerCommand(GameCommand):
    """
    Command to place a tower on the game grid.
    
    Attributes:
        tower_type: Type identifier for the tower to place.
        x: X coordinate on the grid.
        y: Y coordinate on the grid.
    """
    
    tower_type: str = ""
    x: int = 0
    y: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the command to a dictionary."""
        return {
            "command_type": "PlaceTowerCommand",
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "tower_type": self.tower_type,
            "x": self.x,
            "y": self.y,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "PlaceTowerCommand":
        """
        Deserialize a PlaceTowerCommand from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A PlaceTowerCommand instance.
        """
        return PlaceTowerCommand(
            player_id=data["player_id"],
            timestamp=data["timestamp"],
            tower_type=data["tower_type"],
            x=data["x"],
            y=data["y"],
        )


@dataclass
class ModifyControlPointCommand(GameCommand):
    """
    Command to modify a control point in the path.
    
    Attributes:
        index: Index of the control point to modify.
        x: New X coordinate for the control point.
        y: New Y coordinate for the control point.
    """
    
    index: int = 0
    x: int = 0
    y: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the command to a dictionary."""
        return {
            "command_type": "ModifyControlPointCommand",
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "index": self.index,
            "x": self.x,
            "y": self.y,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ModifyControlPointCommand":
        """
        Deserialize a ModifyControlPointCommand from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A ModifyControlPointCommand instance.
        """
        return ModifyControlPointCommand(
            player_id=data["player_id"],
            timestamp=data["timestamp"],
            index=data["index"],
            x=data["x"],
            y=data["y"],
        )


@dataclass
class SendMercenaryCommand(GameCommand):
    """
    Command to send mercenaries to attack the opponent.
    
    Attributes:
        mercenary_type: Type identifier for the mercenary to send.
        target_player_id: Identifier of the player to attack.
    """
    
    mercenary_type: str = ""
    target_player_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the command to a dictionary."""
        return {
            "command_type": "SendMercenaryCommand",
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "mercenary_type": self.mercenary_type,
            "target_player_id": self.target_player_id,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "SendMercenaryCommand":
        """
        Deserialize a SendMercenaryCommand from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A SendMercenaryCommand instance.
        """
        return SendMercenaryCommand(
            player_id=data["player_id"],
            timestamp=data["timestamp"],
            mercenary_type=data["mercenary_type"],
            target_player_id=data["target_player_id"],
        )


@dataclass
class ResearchCommand(GameCommand):
    """
    Command to research a new technology or upgrade.
    
    Attributes:
        research_type: Type identifier for the research to unlock.
    """
    
    research_type: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the command to a dictionary."""
        return {
            "command_type": "ResearchCommand",
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "research_type": self.research_type,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ResearchCommand":
        """
        Deserialize a ResearchCommand from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A ResearchCommand instance.
        """
        return ResearchCommand(
            player_id=data["player_id"],
            timestamp=data["timestamp"],
            research_type=data["research_type"],
        )


@dataclass
class ReadyCommand(GameCommand):
    """
    Command to signal player ready status for phase transition.
    
    Attributes:
        is_ready: Whether the player is ready to proceed.
    """
    
    is_ready: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize the command to a dictionary."""
        return {
            "command_type": "ReadyCommand",
            "player_id": self.player_id,
            "timestamp": self.timestamp,
            "is_ready": self.is_ready,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ReadyCommand":
        """
        Deserialize a ReadyCommand from a dictionary.
        
        Args:
            data: Dictionary containing command data.
            
        Returns:
            A ReadyCommand instance.
        """
        return ReadyCommand(
            player_id=data["player_id"],
            timestamp=data["timestamp"],
            is_ready=data["is_ready"],
        )


# Command factory mapping for deserialization
COMMAND_TYPES = {
    "PlaceTowerCommand": PlaceTowerCommand,
    "ModifyControlPointCommand": ModifyControlPointCommand,
    "SendMercenaryCommand": SendMercenaryCommand,
    "ResearchCommand": ResearchCommand,
    "ReadyCommand": ReadyCommand,
}


def deserialize_command(data: Dict[str, Any]) -> GameCommand:
    """
    Deserialize a command from a dictionary using the command type.
    
    Args:
        data: Dictionary containing command data with a 'command_type' field.
        
    Returns:
        A GameCommand instance of the appropriate type.
        
    Raises:
        KeyError: If command_type is missing or unknown.
    """
    command_type = data["command_type"]
    command_class = COMMAND_TYPES[command_type]
    return command_class.from_dict(data)
