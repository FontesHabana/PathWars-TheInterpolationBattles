"""
Network module for PathWars multiplayer communication.

This module implements the communication layer between players (Host/Client) using TCP Sockets.
"""

from .protocol import Message, MessageType, Serializer
from .manager import NetworkManager
from .commands import (
    GameCommand,
    PlaceTowerCommand,
    ModifyControlPointCommand,
    SendMercenaryCommand,
    ResearchCommand,
    ReadyCommand,
    deserialize_command,
)
from .server import GameServer
from .client import GameClient

__all__ = [
    "Message",
    "MessageType",
    "Serializer",
    "NetworkManager",
    "GameCommand",
    "PlaceTowerCommand",
    "ModifyControlPointCommand",
    "SendMercenaryCommand",
    "ResearchCommand",
    "ReadyCommand",
    "deserialize_command",
    "GameServer",
    "GameClient",
]
