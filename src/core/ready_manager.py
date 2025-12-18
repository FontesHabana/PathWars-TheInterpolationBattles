"""
Ready Manager module for managing player ready states and wave start triggers.

Implements an observer pattern to notify when all players are ready, 
when the timer expires, or when manually forced.
"""

from enum import Enum, auto
from typing import Set, Callable, List
import logging

logger = logging.getLogger(__name__)


class ReadyTrigger(Enum):
    """Enumeration of ready trigger types."""
    ALL_READY = auto()
    TIMER_EXPIRED = auto()
    FORCED = auto()


class ReadyManager:
    """
    Manages player ready states and triggers wave start based on conditions.
    
    Tracks which players are ready and notifies observers when:
    - All players are ready
    - The timer expires
    - Host forces ready state
    
    Attributes:
        player_count: Number of players required to be ready.
        ready_timeout: Timeout in seconds (0 to disable).
    """
    
    def __init__(self, player_count: int = 1, ready_timeout: float = 60.0) -> None:
        """
        Initialize the ReadyManager.
        
        Args:
            player_count: Number of players (minimum 1).
            ready_timeout: Timeout in seconds (minimum 0, 0 disables timer).
        """
        self._player_count = max(1, player_count)
        self._ready_timeout = max(0.0, ready_timeout)
        self._is_active = False
        self._ready_players: Set[int] = set()
        self._time_remaining = 0.0
        self._observers: List[Callable[[ReadyTrigger], None]] = []
    
    @property
    def player_count(self) -> int:
        """Return the number of players required."""
        return self._player_count
    
    @property
    def ready_timeout(self) -> float:
        """Return the ready timeout in seconds."""
        return self._ready_timeout
    
    @property
    def is_active(self) -> bool:
        """Return whether the ready manager is accepting ready states."""
        return self._is_active
    
    @property
    def ready_count(self) -> int:
        """Return the number of ready players."""
        return len(self._ready_players)
    
    @property
    def all_ready(self) -> bool:
        """Return True if all required players are ready."""
        return len(self._ready_players) >= self._player_count
    
    @property
    def time_remaining(self) -> float:
        """Return seconds remaining until timer expires."""
        return max(0.0, self._time_remaining)
    
    def start(self) -> None:
        """Activate the ready phase, reset state, and start timer."""
        logger.info(f"ReadyManager started: {self._player_count} players, {self._ready_timeout}s timeout")
        self._is_active = True
        self._ready_players.clear()
        self._time_remaining = self._ready_timeout
    
    def stop(self) -> None:
        """Deactivate the ready manager without triggering callbacks."""
        logger.info("ReadyManager stopped")
        self._is_active = False
        self._ready_players.clear()
        self._time_remaining = 0.0
    
    def set_ready(self, player_id: int) -> bool:
        """
        Mark a player as ready.
        
        Args:
            player_id: The ID of the player.
            
        Returns:
            True if the player state changed, False otherwise.
        """
        if not self._is_active:
            return False
        
        if player_id in self._ready_players:
            return False
        
        self._ready_players.add(player_id)
        logger.info(f"Player {player_id} ready ({len(self._ready_players)}/{self._player_count})")
        
        # Check if all players are now ready
        if self.all_ready:
            self._trigger(ReadyTrigger.ALL_READY)
        
        return True
    
    def set_unready(self, player_id: int) -> bool:
        """
        Mark a player as not ready.
        
        Args:
            player_id: The ID of the player.
            
        Returns:
            True if the player state changed, False otherwise.
        """
        if player_id not in self._ready_players:
            return False
        
        self._ready_players.remove(player_id)
        logger.info(f"Player {player_id} unready ({len(self._ready_players)}/{self._player_count})")
        return True
    
    def is_player_ready(self, player_id: int) -> bool:
        """
        Check if a specific player is ready.
        
        Args:
            player_id: The ID of the player.
            
        Returns:
            True if the player is ready, False otherwise.
        """
        return player_id in self._ready_players
    
    def force_ready(self) -> None:
        """Trigger ready immediately (host override)."""
        if self._is_active:
            logger.info("ReadyManager forced")
            self._trigger(ReadyTrigger.FORCED)
    
    def subscribe(self, callback: Callable[[ReadyTrigger], None]) -> None:
        """
        Subscribe to ready trigger events.
        
        Args:
            callback: Function to call when ready is triggered.
                     Receives a ReadyTrigger parameter.
        """
        if callback not in self._observers:
            self._observers.append(callback)
            logger.debug(f"Observer subscribed (total: {len(self._observers)})")
    
    def unsubscribe(self, callback: Callable[[ReadyTrigger], None]) -> None:
        """
        Unsubscribe from ready trigger events.
        
        Args:
            callback: The callback function to remove.
        """
        if callback in self._observers:
            self._observers.remove(callback)
            logger.debug(f"Observer unsubscribed (total: {len(self._observers)})")
    
    def update(self, dt: float) -> None:
        """
        Update the ready manager timer.
        
        Should be called every frame during the planning phase.
        
        Args:
            dt: Time elapsed since last update in seconds.
        """
        if not self._is_active:
            return
        
        # Only update timer if timeout is enabled (> 0)
        if self._ready_timeout > 0:
            self._time_remaining -= dt
            
            # Check for timer expiration
            if self._time_remaining <= 0:
                logger.info("ReadyManager timer expired")
                self._trigger(ReadyTrigger.TIMER_EXPIRED)
    
    def reset(self) -> None:
        """Clear all state."""
        logger.info("ReadyManager reset")
        self._is_active = False
        self._ready_players.clear()
        self._time_remaining = 0.0
    
    def _trigger(self, trigger: ReadyTrigger) -> None:
        """
        Trigger ready callbacks and deactivate.
        
        Args:
            trigger: The type of trigger that occurred.
        """
        if not self._is_active:
            return
        
        # Deactivate first to prevent re-triggering
        self._is_active = False
        
        # Notify all observers
        logger.info(f"ReadyManager triggered: {trigger.name}")
        for callback in self._observers:
            try:
                callback(trigger)
            except Exception as e:
                logger.error(f"Error in ready callback: {e}", exc_info=True)
