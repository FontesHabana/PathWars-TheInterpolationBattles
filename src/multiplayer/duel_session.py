"""
Duel Session Module.

Orchestrates multiplayer duel sessions, managing NetworkManager, SyncEngine,
and the duel lifecycle.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from network.manager import NetworkManager
from core.curve_state import CurveState
from .sync_engine import SyncEngine, SyncMessage, SyncMessageType
from .player_role import PlayerRole

logger = logging.getLogger(__name__)


class DuelPhase(Enum):
    """
    Enumeration of duel session phases.
    
    Represents the lifecycle of a multiplayer duel session.
    """
    LOBBY = auto()
    CONNECTING = auto()
    WAITING_OPPONENT = auto()
    SYNCING = auto()
    PLANNING = auto()
    WAITING_READY = auto()
    BATTLE = auto()
    ROUND_END = auto()
    MATCH_END = auto()
    DISCONNECTED = auto()


@dataclass
class DuelPlayer:
    """
    Represents a player in a duel.
    
    Attributes:
        role: The player's role (HOST or CLIENT).
        lives: Number of lives remaining.
        money: Current money amount.
        ready: Whether the player is ready to start battle.
        curve_state: The curve state this player is editing.
    """
    role: PlayerRole
    lives: int = 10
    money: int = 1000
    ready: bool = False
    curve_state: Optional[CurveState] = None


class DuelSession:
    """
    Orchestrates a multiplayer duel session.
    
    Manages the NetworkManager and SyncEngine, handles phase transitions,
    and coordinates the asymmetric pathing model where each player edits
    the path that their opponent's enemies will follow.
    
    Attributes:
        role: This player's role (HOST or CLIENT), None if not connected.
        phase: Current duel phase.
        is_connected: Whether network connection is established.
        local_player: The local player's data.
        remote_player: The remote player's data.
        local_edit_curve: CurveState that local player edits (opponent's incoming path).
        local_incoming_curve: CurveState edited by opponent (local player's incoming path).
        current_round: Current round number (1-5).
        sync_engine: The SyncEngine instance for state synchronization.
    """
    
    MAX_ROUNDS = 5
    
    def __init__(self) -> None:
        """Initialize the DuelSession."""
        self._network_manager = NetworkManager()
        self._sync_engine: Optional[SyncEngine] = None
        self._phase = DuelPhase.LOBBY
        self._role: Optional[PlayerRole] = None
        
        # Player data
        self._local_player: Optional[DuelPlayer] = None
        self._remote_player: Optional[DuelPlayer] = None
        
        # Asymmetric curves
        self._local_edit_curve: Optional[CurveState] = None
        self._local_incoming_curve: Optional[CurveState] = None
        
        # Match state
        self._current_round = 0
        
        # Subscribe to connection events
        self._network_manager.subscribe_connection(self._on_connection_change)
    
    @property
    def role(self) -> Optional[PlayerRole]:
        """Get this player's role."""
        return self._role
    
    @property
    def phase(self) -> DuelPhase:
        """Get the current duel phase."""
        return self._phase
    
    @property
    def is_connected(self) -> bool:
        """Check if network connection is established."""
        return self._network_manager.is_connected
    
    @property
    def local_player(self) -> Optional[DuelPlayer]:
        """Get the local player's data."""
        return self._local_player
    
    @property
    def remote_player(self) -> Optional[DuelPlayer]:
        """Get the remote player's data."""
        return self._remote_player
    
    @property
    def local_edit_curve(self) -> Optional[CurveState]:
        """Get the curve that the local player edits (opponent's incoming path)."""
        return self._local_edit_curve
    
    @property
    def local_incoming_curve(self) -> Optional[CurveState]:
        """Get the curve edited by opponent (local player's incoming path)."""
        return self._local_incoming_curve
    
    @property
    def current_round(self) -> int:
        """Get the current round number."""
        return self._current_round
    
    @property
    def sync_engine(self) -> Optional[SyncEngine]:
        """Get the SyncEngine instance."""
        return self._sync_engine
    
    def host_game(self, port: int) -> bool:
        """
        Start hosting a game.
        
        Args:
            port: Port number to listen on.
            
        Returns:
            True if hosting started successfully, False otherwise.
        """
        logger.info(f"Attempting to host game on port {port}")
        
        # Reset the network manager to ensure clean state
        self._network_manager.reset()
        # Re-subscribe to connection events after reset
        self._network_manager.subscribe_connection(self._on_connection_change)
        
        self._phase = DuelPhase.CONNECTING
        # Set role BEFORE starting host so callback has access to it
        self._role = PlayerRole.HOST
        
        if self._network_manager.start_host(port):
            self._phase = DuelPhase.WAITING_OPPONENT
            logger.info("Successfully started hosting")
            return True
        else:
            logger.error("Failed to start hosting")
            self._phase = DuelPhase.LOBBY
            self._role = None
            return False
    
    def join_game(self, ip: str, port: int) -> bool:
        """
        Join a hosted game.
        
        Args:
            ip: IP address of the host.
            port: Port number to connect to.
            
        Returns:
            True if connection successful, False otherwise.
        """
        logger.info(f"Attempting to join game at {ip}:{port}")
        
        # Reset the network manager to ensure clean state
        self._network_manager.reset()
        # Re-subscribe to connection events after reset
        self._network_manager.subscribe_connection(self._on_connection_change)
        
        self._phase = DuelPhase.CONNECTING
        # Set role BEFORE connecting so callback has access to it
        self._role = PlayerRole.CLIENT
        
        if self._network_manager.connect_to_host(ip, port):
            logger.info("Successfully joined game")
            return True
        else:
            logger.error("Failed to join game")
            self._phase = DuelPhase.LOBBY
            self._role = None
            return False
    
    def _on_connection_change(self, connected: bool) -> None:
        """
        Handle connection status changes.
        
        Args:
            connected: True if connected, False if disconnected.
        """
        if connected:
            logger.info("Connection established")
            # Make sure role is set before initializing sync
            if self._role is not None:
                self._phase = DuelPhase.SYNCING
                self._initialize_sync()
        else:
            logger.info("Connection lost")
            self._phase = DuelPhase.DISCONNECTED
    
    def _initialize_sync(self) -> None:
        """Initialize synchronization after connection is established."""
        # Create SyncEngine
        self._sync_engine = SyncEngine(self._network_manager)
        
        # Subscribe to sync messages
        self._sync_engine.subscribe(SyncMessageType.FULL_SYNC, self._on_full_sync)
        self._sync_engine.subscribe(SyncMessageType.CURVE_POINT_ADD, self._on_curve_point_add)
        self._sync_engine.subscribe(SyncMessageType.CURVE_POINT_MOVE, self._on_curve_point_move)
        self._sync_engine.subscribe(SyncMessageType.CURVE_POINT_REMOVE, self._on_curve_point_remove)
        self._sync_engine.subscribe(SyncMessageType.CURVE_METHOD_CHANGE, self._on_curve_method_change)
        self._sync_engine.subscribe(SyncMessageType.READY_STATE, self._on_ready_state)
        self._sync_engine.subscribe(SyncMessageType.GAME_EVENT, self._on_game_event)
        
        # Create player objects
        self._local_player = DuelPlayer(role=self._role)
        self._remote_player = DuelPlayer(role=self._role.opponent())
        
        # Create asymmetric curves
        self._local_edit_curve = CurveState()
        self._local_incoming_curve = CurveState()
        
        # Initialize with default start/end points
        self._local_edit_curve.add_point(0.0, 10.0)
        self._local_edit_curve.add_point(19.0, 10.0)
        
        self._local_incoming_curve.add_point(0.0, 10.0)
        self._local_incoming_curve.add_point(19.0, 10.0)
        
        # Assign curves to players
        self._local_player.curve_state = self._local_edit_curve
        self._remote_player.curve_state = self._local_incoming_curve
        
        # Send initial full sync
        if self._sync_engine:
            self._sync_engine.sync_full_curve(self._local_edit_curve)
        
        # Move to planning phase
        self._current_round = 1
        self._phase = DuelPhase.PLANNING
        logger.info("Sync initialized, entering PLANNING phase")
    
    def _on_full_sync(self, sync_msg: SyncMessage) -> None:
        """Handle full curve synchronization."""
        if self._local_incoming_curve:
            self._local_incoming_curve.clear_points()
            for x, y in sync_msg.data.get('control_points', []):
                self._local_incoming_curve.add_point(x, y)
            method = sync_msg.data.get('interpolation_method', 'linear')
            self._local_incoming_curve.set_method(method)
            logger.info("Received full curve sync")
    
    def _on_curve_point_add(self, sync_msg: SyncMessage) -> None:
        """Handle curve point addition."""
        if self._local_incoming_curve:
            x = sync_msg.data.get('x', 0.0)
            y = sync_msg.data.get('y', 0.0)
            self._local_incoming_curve.add_point(x, y)
            logger.debug(f"Remote added point at ({x}, {y})")
    
    def _on_curve_point_move(self, sync_msg: SyncMessage) -> None:
        """Handle curve point movement."""
        if self._local_incoming_curve:
            index = sync_msg.data.get('index', 0)
            x = sync_msg.data.get('x', 0.0)
            y = sync_msg.data.get('y', 0.0)
            self._local_incoming_curve.move_point(index, x, y)
            logger.debug(f"Remote moved point {index} to ({x}, {y})")
    
    def _on_curve_point_remove(self, sync_msg: SyncMessage) -> None:
        """Handle curve point removal."""
        if self._local_incoming_curve:
            index = sync_msg.data.get('index', 0)
            self._local_incoming_curve.remove_point(index)
            logger.debug(f"Remote removed point {index}")
    
    def _on_curve_method_change(self, sync_msg: SyncMessage) -> None:
        """Handle interpolation method change."""
        if self._local_incoming_curve:
            method = sync_msg.data.get('method', 'linear')
            self._local_incoming_curve.set_method(method)
            logger.debug(f"Remote changed method to {method}")
    
    def _on_ready_state(self, sync_msg: SyncMessage) -> None:
        """Handle ready state change."""
        if self._remote_player:
            self._remote_player.ready = sync_msg.data.get('ready', False)
            logger.info(f"Remote player ready: {self._remote_player.ready}")
            
            # Check if both players are ready
            if self._local_player and self._local_player.ready and self._remote_player.ready:
                self._start_battle()
    
    def _on_game_event(self, sync_msg: SyncMessage) -> None:
        """Handle game events."""
        event_type = sync_msg.data.get('event_type', '')
        event_data = sync_msg.data.get('event_data', {})
        
        if event_type == 'damage':
            damage = event_data.get('damage', 1)
            if self._local_player:
                self._local_player.lives -= damage
                logger.info(f"Took {damage} damage, lives: {self._local_player.lives}")
        elif event_type == 'round_complete':
            self._handle_round_complete()
    
    def set_ready(self, ready: bool) -> None:
        """
        Set the local player's ready state.
        
        Args:
            ready: Whether the player is ready.
        """
        if self._local_player:
            self._local_player.ready = ready
            logger.info(f"Set ready state to {ready}")
            
            # Sync ready state
            if self._sync_engine:
                sync_msg = SyncMessage(
                    sync_type=SyncMessageType.READY_STATE,
                    data={'ready': ready}
                )
                self._sync_engine._send_sync(sync_msg)
            
            # Check if both players are ready
            if self._remote_player and self._local_player.ready and self._remote_player.ready:
                self._start_battle()
    
    def _start_battle(self) -> None:
        """Start the battle phase."""
        self._phase = DuelPhase.BATTLE
        logger.info(f"Starting battle for round {self._current_round}")
    
    def report_damage(self, amount: int) -> None:
        """
        Report damage dealt to the local player.
        
        Args:
            amount: Amount of damage dealt.
        """
        if self._sync_engine:
            self._sync_engine.sync_game_event('damage', {'damage': amount})
    
    def report_round_complete(self) -> None:
        """Report that the current round is complete."""
        if self._sync_engine:
            self._sync_engine.sync_game_event('round_complete', {})
        self._handle_round_complete()
    
    def _handle_round_complete(self) -> None:
        """Handle round completion."""
        self._phase = DuelPhase.ROUND_END
        logger.info(f"Round {self._current_round} complete")
        
        # Check if match is complete
        if self._current_round >= self.MAX_ROUNDS:
            self._phase = DuelPhase.MATCH_END
            logger.info("Match complete!")
        elif self._local_player and self._local_player.lives <= 0:
            self._phase = DuelPhase.MATCH_END
            logger.info("Local player defeated!")
        elif self._remote_player and self._remote_player.lives <= 0:
            self._phase = DuelPhase.MATCH_END
            logger.info("Remote player defeated!")
        else:
            # Prepare for next round
            self._current_round += 1
            self._phase = DuelPhase.PLANNING
            if self._local_player:
                self._local_player.ready = False
            if self._remote_player:
                self._remote_player.ready = False
            logger.info(f"Starting round {self._current_round}")
    
    def disconnect(self) -> None:
        """Disconnect from the duel session."""
        logger.info("Disconnecting from duel session")
        self._network_manager.close()
        self._phase = DuelPhase.DISCONNECTED
    
    def update(self, dt: float) -> None:
        """
        Update the duel session.
        
        Args:
            dt: Delta time in seconds.
        """
        # Placeholder for any per-frame updates needed
        pass
