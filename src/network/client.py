"""
Game Client Module.

Implements the game client that connects to the server
and sends commands for execution.
"""

import logging
from typing import Optional

from .commands import GameCommand
from .manager import NetworkManager
from .protocol import Message, MessageType

# Get logger for this module
logger = logging.getLogger(__name__)


class GameClient:
    """
    Game client for connecting to and communicating with the game server.
    
    The client sends player commands to the server and receives
    game state updates. Rendering and local effects are handled separately
    from the authoritative game state maintained by the server.
    
    Attributes:
        network_manager: NetworkManager instance for server connection.
        is_connected: Whether the client is connected to a server.
        player_id: Identifier for this player.
    """
    
    def __init__(self, player_id: str) -> None:
        """
        Initialize the GameClient.
        
        Args:
            player_id: Unique identifier for this player.
        """
        self.network_manager = NetworkManager()
        self.is_connected = False
        self.player_id = player_id
        
        # Subscribe to connection status changes
        self.network_manager.subscribe_connection(self._on_connection_change)
    
    def connect(self, ip: str, port: int, timeout: float = 5.0) -> bool:
        """
        Connect to the game server.
        
        Args:
            ip: The IP address of the server.
            port: The port to connect to.
            timeout: Connection timeout in seconds.
            
        Returns:
            True if connection was successful, False otherwise.
        """
        success = self.network_manager.connect_to_host(ip, port, timeout)
        if success:
            logger.info(f"GameClient ({self.player_id}) connected to {ip}:{port}")
        else:
            logger.error(f"GameClient ({self.player_id}) failed to connect to {ip}:{port}")
        
        return success
    
    def _on_connection_change(self, connected: bool) -> None:
        """
        Handle connection status changes.
        
        Args:
            connected: The new connection status.
        """
        self.is_connected = connected
        if connected:
            logger.info(f"GameClient ({self.player_id}) connection established")
        else:
            logger.warning(f"GameClient ({self.player_id}) connection lost")
    
    def send_command(self, command: GameCommand) -> bool:
        """
        Send a game command to the server.
        
        Args:
            command: The command to send.
            
        Returns:
            True if the command was sent successfully, False otherwise.
        """
        if not self.is_connected:
            logger.warning("Cannot send command: not connected to server")
            return False
        
        # Serialize command and wrap in a message
        message = Message(
            msg_type=MessageType.PLAYER_ACTION,
            payload=command.to_dict(),
            sender_id=self.player_id,
        )
        
        success = self.network_manager.send(message)
        if success:
            logger.debug(
                f"Sent {type(command).__name__} from player {self.player_id}"
            )
        else:
            logger.error(
                f"Failed to send {type(command).__name__} from player {self.player_id}"
            )
        
        return success
    
    def disconnect(self) -> None:
        """
        Disconnect from the server and clean up resources.
        """
        self.network_manager.close()
        self.is_connected = False
        logger.info(f"GameClient ({self.player_id}) disconnected")
