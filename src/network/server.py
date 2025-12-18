"""
Game Server Module.

Implements the authoritative game server that manages game state
and processes commands from connected clients.
"""

import logging
from queue import Queue
from typing import Optional

from .commands import GameCommand, deserialize_command
from .manager import NetworkManager
from .protocol import Message, MessageType

# Get logger for this module
logger = logging.getLogger(__name__)


class GameServer:
    """
    Authoritative game server managing multiplayer game state.
    
    The server acts as the single source of truth for game state,
    validates all commands from clients, and broadcasts state updates.
    
    Attributes:
        network_manager: NetworkManager instance for handling connections.
        command_queue: Queue of commands awaiting processing.
        is_running: Whether the server is currently running.
    """
    
    def __init__(self) -> None:
        """Initialize the GameServer."""
        self.network_manager = NetworkManager()
        self.command_queue: Queue[GameCommand] = Queue()
        self.is_running = False
        
        # Subscribe to network messages
        self.network_manager.subscribe(
            MessageType.PLAYER_ACTION,
            self._on_player_action
        )
    
    def start(self, port: int, host: str = "0.0.0.0") -> bool:  # noqa: S104
        """
        Start the game server on the specified port.
        
        Note:
            The default host '0.0.0.0' binds to all network interfaces, which is
            intentional for a multiplayer game server. To restrict to localhost
            only, pass host='127.0.0.1'.
        
        Args:
            port: The port to listen on.
            host: The host address to bind to (default: all interfaces).
            
        Returns:
            True if the server started successfully, False otherwise.
        """
        if self.is_running:
            logger.warning("Server is already running")
            return False
        
        success = self.network_manager.start_host(port, host)
        if success:
            self.is_running = True
            logger.info(f"GameServer started on {host}:{port}")
        else:
            logger.error("Failed to start GameServer")
        
        return success
    
    def _on_player_action(self, message: Message) -> None:
        """
        Handle incoming player action messages.
        
        Args:
            message: The message containing the player action.
        """
        try:
            # Deserialize command from message payload
            command = deserialize_command(message.payload)
            self.command_queue.put(command)
            logger.debug(f"Queued command: {type(command).__name__}")
        except (KeyError, ValueError) as e:
            logger.error(f"Failed to deserialize command: {e}")
    
    def process_commands(self) -> int:
        """
        Process all pending commands in the queue.
        
        This method executes all queued commands. Currently implements
        placeholder logging, but will be extended to validate and apply
        commands to the authoritative game state.
        
        Returns:
            The number of commands processed.
        """
        processed_count = 0
        
        while not self.command_queue.empty():
            command = self.command_queue.get()
            self._execute_command(command)
            processed_count += 1
        
        return processed_count
    
    def _execute_command(self, command: GameCommand) -> None:
        """
        Execute a game command.
        
        This is a placeholder implementation that logs the command.
        In a complete implementation, this would:
        1. Validate the command against game rules
        2. Update the authoritative game state
        3. Broadcast state changes to clients
        
        Args:
            command: The command to execute.
        """
        logger.info(
            f"Executing {type(command).__name__} from player {command.player_id}"
        )
        
        # Placeholder: Log command details
        # Future implementation will validate and apply to game state
        command_dict = command.to_dict()
        logger.debug(f"Command details: {command_dict}")
    
    def stop(self) -> None:
        """
        Stop the game server and clean up resources.
        """
        self.is_running = False
        self.network_manager.close()
        
        # Clear the command queue
        while not self.command_queue.empty():
            self.command_queue.get()
        
        logger.info("GameServer stopped")
