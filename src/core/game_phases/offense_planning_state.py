"""
Offense Planning state for editing attack paths on rival map.
"""

from typing import TYPE_CHECKING, List, Tuple, Optional
import pygame

from .base_phase import GamePhaseState

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class OffensePlanningState(GamePhaseState):
    """
    Offense Planning phase state.
    
    Allows player to edit control points on the rival map.
    Has a configurable time limit (default: 60 seconds).
    On exit, locks the current control points.
    """
    
    def __init__(
        self, 
        phase_manager: 'PhaseManager',
        time_limit: float = 60.0
    ) -> None:
        super().__init__(phase_manager)
        self._time_limit = time_limit
        self._control_points: List[Tuple[float, float]] = []
        self._locked_points: List[Tuple[float, float]] = []
        self._editing_enabled: bool = True
    
    @property
    def name(self) -> str:
        """Return the name of this phase."""
        return "OffensePlanning"
    
    @property
    def control_points(self) -> List[Tuple[float, float]]:
        """Get current control points."""
        return self._control_points.copy()
    
    @property
    def locked_points(self) -> List[Tuple[float, float]]:
        """Get locked control points from previous waves."""
        return self._locked_points.copy()
    
    def enter(self) -> None:
        """Called when entering this phase."""
        self._elapsed_time = 0.0
        self._editing_enabled = True
        # Control points from current wave remain unlocked
        # Locked points from previous waves remain locked
    
    def exit(self) -> None:
        """Called when exiting this phase."""
        # Lock current control points when exiting
        self._locked_points.extend(self._control_points)
        self._control_points.clear()
        self._editing_enabled = False
    
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        self._elapsed_time += dt
        
        # Auto-transition to DefensePlanning when time runs out
        if self._time_limit is not None and self._elapsed_time >= self._time_limit:
            self.request_transition("DefensePlanning")
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        if not self._editing_enabled:
            return False
        
        # Handle control point editing
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click - add point
                self._control_points.append((float(event.pos[0]), float(event.pos[1])))
                return True
            elif event.button == 3:  # Right click - remove last point
                if self._control_points:
                    self._control_points.pop()
                    return True
        
        # Handle manual phase transition
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.request_transition("DefensePlanning")
                return True
        
        return False
    
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        # OffensePlanning can only transition to DefensePlanning
        return next_phase == "DefensePlanning"
    
    def add_control_point(self, x: float, y: float) -> bool:
        """
        Add a control point if editing is enabled.
        Returns True if added successfully.
        """
        if not self._editing_enabled:
            return False
        self._control_points.append((x, y))
        return True
    
    def remove_control_point(self, index: int) -> bool:
        """
        Remove a control point by index if editing is enabled.
        Returns True if removed successfully.
        """
        if not self._editing_enabled or index < 0 or index >= len(self._control_points):
            return False
        self._control_points.pop(index)
        return True
