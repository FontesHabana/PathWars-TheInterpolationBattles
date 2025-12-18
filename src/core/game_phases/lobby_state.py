"""
Lobby state for game configuration before starting.
"""

from typing import TYPE_CHECKING
import pygame

from .base_phase import GamePhaseState

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class LobbyState(GamePhaseState):
    """
    Lobby phase state for game configuration.
    
    Allows players to configure match parameters and validate
    that both players are connected before starting.
    """
    
    def __init__(self, phase_manager: 'PhaseManager') -> None:
        super().__init__(phase_manager)
        self._players_ready: int = 0
        self._both_players_connected: bool = False
    
    @property
    def name(self) -> str:
        """Return the name of this phase."""
        return "Lobby"
    
    def enter(self) -> None:
        """Called when entering this phase."""
        self._players_ready = 0
        self._both_players_connected = False
        self._elapsed_time = 0.0
    
    def exit(self) -> None:
        """Called when exiting this phase."""
        pass
    
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        self._elapsed_time += dt
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        # Handle ready/start game inputs
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Simulate player ready
                self._players_ready += 1
                return True
        return False
    
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        # Lobby can only transition to OffensePlanning
        return next_phase == "OffensePlanning"
    
    def set_players_connected(self, connected: bool) -> None:
        """Set whether both players are connected."""
        self._both_players_connected = connected
    
    def is_ready_to_start(self) -> bool:
        """Check if the lobby is ready to start the game."""
        return self._both_players_connected and self._players_ready >= 2
