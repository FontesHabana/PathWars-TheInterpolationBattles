"""
Game Over state for displaying match results.
"""

from typing import TYPE_CHECKING, Optional
import pygame

from .base_phase import GamePhaseState

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class GameOverState(GamePhaseState):
    """
    Game Over phase state.
    
    Displays match results (victory or defeat).
    Can only transition back to Lobby for a new game.
    """
    
    def __init__(self, phase_manager: 'PhaseManager') -> None:
        super().__init__(phase_manager)
        self._winner: Optional[str] = None
        self._final_score: Optional[int] = None
    
    @property
    def name(self) -> str:
        """Return the name of this phase."""
        return "GameOver"
    
    @property
    def winner(self) -> Optional[str]:
        """Get the winner of the match."""
        return self._winner
    
    @property
    def final_score(self) -> Optional[int]:
        """Get the final score."""
        return self._final_score
    
    def enter(self) -> None:
        """Called when entering this phase."""
        self._elapsed_time = 0.0
    
    def exit(self) -> None:
        """Called when exiting this phase."""
        self._winner = None
        self._final_score = None
    
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        self._elapsed_time += dt
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        # Handle return to lobby
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.request_transition("Lobby")
                return True
            if event.key == pygame.K_ESCAPE:
                # Could also return to lobby
                self.request_transition("Lobby")
                return True
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Click anywhere to return to lobby
            self.request_transition("Lobby")
            return True
        
        return False
    
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        # GameOver can only transition to Lobby
        return next_phase == "Lobby"
    
    def set_results(self, winner: str, final_score: int) -> None:
        """
        Set the game results.
        
        Args:
            winner: Name of the winning player.
            final_score: Final score of the match.
        """
        self._winner = winner
        self._final_score = final_score
