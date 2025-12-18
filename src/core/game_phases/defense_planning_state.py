"""
Defense Planning state for placing towers on own map.
"""

from typing import TYPE_CHECKING, List, Tuple, Optional
import pygame

from .base_phase import GamePhaseState

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class DefensePlanningState(GamePhaseState):
    """
    Defense Planning phase state.
    
    Allows player to place towers on their own map.
    Has a configurable time limit (default: 45 seconds).
    """
    
    def __init__(
        self, 
        phase_manager: 'PhaseManager',
        time_limit: float = 45.0
    ) -> None:
        super().__init__(phase_manager)
        self._time_limit = time_limit
        self._tower_placements: List[Tuple[int, int, str]] = []  # (x, y, tower_type)
        self._placement_enabled: bool = True
    
    @property
    def name(self) -> str:
        """Return the name of this phase."""
        return "DefensePlanning"
    
    @property
    def tower_placements(self) -> List[Tuple[int, int, str]]:
        """Get current tower placements."""
        return self._tower_placements.copy()
    
    def enter(self) -> None:
        """Called when entering this phase."""
        self._elapsed_time = 0.0
        self._placement_enabled = True
        # Keep existing towers from previous waves
    
    def exit(self) -> None:
        """Called when exiting this phase."""
        self._placement_enabled = False
    
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        self._elapsed_time += dt
        
        # Auto-transition to Battle when time runs out
        if self._time_limit is not None and self._elapsed_time >= self._time_limit:
            self.request_transition("Battle")
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        if not self._placement_enabled:
            return False
        
        # Handle tower placement
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - place tower
                # Default tower type
                grid_x = event.pos[0] // 32  # Assuming 32px grid cells
                grid_y = event.pos[1] // 32
                self._tower_placements.append((grid_x, grid_y, "basic"))
                return True
            elif event.button == 3:  # Right click - remove last tower
                if self._tower_placements:
                    self._tower_placements.pop()
                    return True
        
        # Handle manual phase transition
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.request_transition("Battle")
                return True
        
        return False
    
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        # DefensePlanning can only transition to Battle
        return next_phase == "Battle"
    
    def place_tower(self, x: int, y: int, tower_type: str = "basic") -> bool:
        """
        Place a tower at the specified grid position.
        Returns True if placed successfully.
        """
        if not self._placement_enabled:
            return False
        self._tower_placements.append((x, y, tower_type))
        return True
    
    def remove_tower(self, x: int, y: int) -> bool:
        """
        Remove a tower at the specified grid position.
        Returns True if removed successfully.
        """
        if not self._placement_enabled:
            return False
        
        for i, (tx, ty, _) in enumerate(self._tower_placements):
            if tx == x and ty == y:
                self._tower_placements.pop(i)
                return True
        return False
