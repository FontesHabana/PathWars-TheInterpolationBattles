"""
Battle state for real-time wave execution.
"""

from typing import TYPE_CHECKING
import pygame

from .base_phase import GamePhaseState

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class BattleState(GamePhaseState):
    """
    Battle phase state for real-time wave execution.
    
    No time limit - ends when all enemies are defeated or reach the goal.
    Input is mostly disabled except for pause/camera controls.
    Can transition to OffensePlanning (next wave) or GameOver.
    """
    
    def __init__(self, phase_manager: 'PhaseManager') -> None:
        super().__init__(phase_manager)
        self._battle_complete: bool = False
        self._victory: bool = False
        self._paused: bool = False
    
    @property
    def name(self) -> str:
        """Return the name of this phase."""
        return "Battle"
    
    @property
    def is_paused(self) -> bool:
        """Check if battle is paused."""
        return self._paused
    
    @property
    def is_complete(self) -> bool:
        """Check if battle is complete."""
        return self._battle_complete
    
    def enter(self) -> None:
        """Called when entering this phase."""
        self._elapsed_time = 0.0
        self._battle_complete = False
        self._victory = False
        self._paused = False
    
    def exit(self) -> None:
        """Called when exiting this phase."""
        pass
    
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        if not self._paused:
            self._elapsed_time += dt
        
        # Battle logic would update enemies, towers, etc.
        # When battle completes, set _battle_complete = True
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        # Only allow pause and camera controls during battle
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                self._paused = not self._paused
                return True
            
            # Camera controls (arrows, WASD)
            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT,
                           pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                # Camera movement would be handled here
                return True
        
        return False
    
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        # Battle can transition to OffensePlanning (next wave) or GameOver
        return next_phase in ("OffensePlanning", "GameOver")
    
    def complete_battle(self, victory: bool) -> None:
        """
        Mark the battle as complete.
        
        Args:
            victory: True if player won, False if lost.
        """
        self._battle_complete = True
        self._victory = victory
    
    def is_victory(self) -> bool:
        """Check if the battle was won."""
        return self._victory
