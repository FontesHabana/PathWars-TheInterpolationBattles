"""
Game Server Module.

Implements the authoritative game server that manages game state
and processes commands from connected clients.
"""

import logging
import re
from queue import Queue
from typing import Callable, Dict, Optional, Tuple

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
        
        # Authoritative game state
        self._game_state: Optional[object] = None
        
        # Command handlers registry
        self._command_handlers: Dict[str, Callable[[GameCommand], bool]] = {
            'PLACE_TOWER': self._handle_place_tower,
            'MODIFY_CONTROL_POINT': self._handle_modify_control_point,
            'SEND_MERCENARY': self._handle_send_mercenary,
            'RESEARCH': self._handle_research,
            'READY': self._handle_ready,
        }
        
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
    
    def set_game_state(self, game_state: object) -> None:
        """
        Set the authoritative game state to manage.
        
        Args:
            game_state: The game state instance to manage.
        """
        self._game_state = game_state
    
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
    
    def process_commands(self) -> Tuple[int, int]:
        """
        Process all pending commands in the queue.
        
        This method executes all queued commands, validating them
        against game rules and updating the authoritative game state.
        
        Returns:
            Tuple of (successful_count, failed_count).
        """
        success_count = 0
        fail_count = 0
        
        while not self.command_queue.empty():
            command = self.command_queue.get()
            if self._execute_command(command):
                success_count += 1
            else:
                fail_count += 1
        
        return (success_count, fail_count)
    
    def _execute_command(self, command: GameCommand) -> bool:
        """
        Execute a game command.
        
        Validates the command against game rules and updates state.
        
        Args:
            command: The command to execute.
            
        Returns:
            True if command was executed successfully, False otherwise.
        """
        # Determine command type from command class name
        # PlaceTowerCommand -> PLACE_TOWER
        command_class_name = type(command).__name__
        if command_class_name.endswith('Command'):
            command_class_name = command_class_name[:-7]  # Remove 'Command'
        
        # Convert CamelCase to SNAKE_CASE
        command_type = re.sub(r'(?<=[a-z])(?=[A-Z])', '_', command_class_name).upper()
        
        handler = self._command_handlers.get(command_type)
        
        if handler is None:
            logger.warning(f"Unknown command type: {command_type}")
            return False
        
        try:
            success = handler(command)
            if success:
                logger.info(f"Executed {command_type} from player {command.player_id}")
                # Broadcast state update to clients
                self._broadcast_state_update()
            else:
                logger.warning(f"Failed to execute {command_type}")
            return success
        except Exception as e:
            logger.error(f"Error executing {command_type}: {e}")
            return False
    
    def _handle_place_tower(self, command: GameCommand) -> bool:
        """
        Handle tower placement command.
        
        Validates:
        - Game state exists
        - Tower type and position are provided
        
        Args:
            command: PlaceTowerCommand instance.
            
        Returns:
            True if validation passes, False otherwise.
        """
        if self._game_state is None:
            return False
        
        # Extract data from command attributes
        tower_type = getattr(command, 'tower_type', None)
        x = getattr(command, 'x', None)
        y = getattr(command, 'y', None)
        
        if tower_type is None or x is None or y is None:
            logger.warning("Invalid PLACE_TOWER command data")
            return False
        
        # TODO: Validate phase, money, position
        # TODO: Create tower and add to game state
        # For now, just validate the structure
        
        logger.debug(f"Would place {tower_type} at ({x}, {y})")
        return True
    
    def _handle_modify_control_point(self, command: GameCommand) -> bool:
        """
        Handle control point modification command.
        
        Validates:
        - Game state exists
        - Index and coordinates are provided
        
        Args:
            command: ModifyControlPointCommand instance.
            
        Returns:
            True if validation passes, False otherwise.
        """
        if self._game_state is None:
            return False
        
        # Extract data from command attributes
        index = getattr(command, 'index', None)
        x = getattr(command, 'x', None)
        y = getattr(command, 'y', None)
        
        if index is None or x is None or y is None:
            logger.warning("Invalid MODIFY_CONTROL_POINT command data")
            return False
        
        # TODO: Validate phase is OFFENSE_PLANNING
        # TODO: Apply modification to curve state
        
        logger.debug(f"Would modify control point {index} to ({x}, {y})")
        return True
    
    def _handle_send_mercenary(self, command: GameCommand) -> bool:
        """
        Handle mercenary send command.
        
        Validates:
        - Game state exists
        - Mercenary type and target player are provided
        
        Args:
            command: SendMercenaryCommand instance.
            
        Returns:
            True if validation passes, False otherwise.
        """
        if self._game_state is None:
            return False
        
        # Extract data from command attributes
        mercenary_type = getattr(command, 'mercenary_type', None)
        target_player_id = getattr(command, 'target_player_id', None)
        
        if mercenary_type is None or target_player_id is None:
            logger.warning("Invalid SEND_MERCENARY command data")
            return False
        
        # TODO: Validate cost, create mercenaries
        
        logger.debug(f"Would send {mercenary_type} to {target_player_id}")
        return True
    
    def _handle_research(self, command: GameCommand) -> bool:
        """
        Handle research command.
        
        Validates:
        - Game state exists
        - Research type is provided
        
        Args:
            command: ResearchCommand instance.
            
        Returns:
            True if validation passes, False otherwise.
        """
        if self._game_state is None:
            return False
        
        # Extract data from command attributes
        research_type = getattr(command, 'research_type', None)
        
        if research_type is None:
            logger.warning("Invalid RESEARCH command data")
            return False
        
        # TODO: Validate cost, prerequisites, apply research
        
        logger.debug(f"Would research {research_type}")
        return True
    
    def _handle_ready(self, command: GameCommand) -> bool:
        """
        Handle ready state command.
        
        Validates:
        - Game state exists
        - Ready state is provided
        
        Args:
            command: ReadyCommand instance.
            
        Returns:
            True if validation passes, False otherwise.
        """
        if self._game_state is None:
            return False
        
        # Extract data from command attributes
        is_ready = getattr(command, 'is_ready', False)
        
        # TODO: Track ready state per player
        # TODO: Check if both players ready, then transition phase
        
        logger.debug(f"Player {command.player_id} ready: {is_ready}")
        return True
    
    def _broadcast_state_update(self) -> None:
        """Broadcast current state to all connected clients."""
        if self._game_state is None:
            return
        
        # Check if game_state has to_dict method
        if hasattr(self._game_state, 'to_dict'):
            state_dict = self._game_state.to_dict()
            message = Message(
                msg_type=MessageType.GAME_STATE,
                payload=state_dict
            )
            self.network_manager.send(message)
    
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
