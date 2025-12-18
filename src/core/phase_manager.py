"""
Phase Manager for orchestrating game loop and phase transitions.

This module implements the core game loop logic, managing phase transitions,
round tracking, and enforcing control point placement constraints.

MULTIPLAYER ASYMMETRIC MODEL:
In multiplayer matches, control points are placed on the RIVAL's map to design
attack paths, while towers are built on the player's OWN map for defense.
"""

import logging
from typing import Optional, Set

from .phase_state import (
    GamePhaseState,
    PhaseType,
    create_phase_state,
    InvalidPhaseActionError,
)

logger = logging.getLogger(__name__)


class InvalidPhaseTransitionError(Exception):
    """Raised when attempting an invalid phase transition."""
    pass


class ControlPointConstraintError(Exception):
    """Raised when control point placement violates constraints."""
    pass


class PhaseManager:
    """
    Manages game phases and enforces phase-specific rules.
    
    Handles:
    - Phase state transitions
    - Round tracking (1-5 or configurable)
    - Control point placement constraints
    - Initial preparation phase rules
    
    Attributes:
        current_phase: The current phase state.
        current_round: Current round number (1-based).
        max_rounds: Maximum number of rounds in the match.
        points_modified_this_round: Number of points added/removed this round.
        initial_points_placed: Number of initial points placed (preparation phase).
    """
    
    MAX_INITIAL_POINTS = 2
    MAX_POINTS_PER_ROUND = 1
    
    def __init__(self, max_rounds: int = 5) -> None:
        """
        Initialize the PhaseManager.
        
        Args:
            max_rounds: Maximum number of rounds (default: 5).
        """
        self._current_phase: GamePhaseState = create_phase_state(PhaseType.PREPARATION)
        self._current_round: int = 1
        self._max_rounds: int = max_rounds
        
        # Track modifications within current phase/round
        self._points_modified_this_round: int = 0
        self._initial_points_placed: int = 0
        
        # Track which points were placed in which round
        self._point_round_map: dict[int, int] = {}  # point_index -> round_number
        
        logger.info(f"PhaseManager initialized with {max_rounds} rounds")
    
    @property
    def current_phase(self) -> GamePhaseState:
        """Return the current phase state."""
        return self._current_phase
    
    @property
    def current_round(self) -> int:
        """Return the current round number (1-based)."""
        return self._current_round
    
    @property
    def max_rounds(self) -> int:
        """Return the maximum number of rounds."""
        return self._max_rounds
    
    @property
    def is_preparation_phase(self) -> bool:
        """Check if currently in preparation phase."""
        return self._current_phase.phase_type == PhaseType.PREPARATION
    
    @property
    def points_modified_this_round(self) -> int:
        """Return number of points modified in current round."""
        return self._points_modified_this_round
    
    @property
    def initial_points_placed(self) -> int:
        """Return number of initial points placed (preparation only)."""
        return self._initial_points_placed
    
    def can_add_control_point(self) -> bool:
        """
        Check if a control point can be added in the current phase.
        
        Returns:
            True if a point can be added, False otherwise.
        """
        if not self._current_phase.can_modify_path():
            return False
        
        # During preparation, can place up to 2 initial points
        if self.is_preparation_phase:
            return self._initial_points_placed < self.MAX_INITIAL_POINTS
        
        # During regular rounds, can modify at most 1 point
        return self._points_modified_this_round < self.MAX_POINTS_PER_ROUND
    
    def can_remove_control_point(self, point_index: int) -> bool:
        """
        Check if a control point can be removed.
        
        Args:
            point_index: Index of the point to check.
            
        Returns:
            True if the point can be removed, False otherwise.
        """
        if not self._current_phase.can_modify_path():
            return False
        
        # Cannot remove during preparation (points are being placed)
        if self.is_preparation_phase:
            return False
        
        # Can only remove points placed in current round
        point_round = self._point_round_map.get(point_index)
        if point_round is None or point_round != self._current_round:
            return False
        
        # Check modification limit
        return self._points_modified_this_round < self.MAX_POINTS_PER_ROUND
    
    def can_move_control_point(self, point_index: int) -> bool:
        """
        Check if a control point can be moved.
        
        Args:
            point_index: Index of the point to check.
            
        Returns:
            True if the point can be moved, False otherwise.
        """
        if not self._current_phase.can_modify_path():
            return False
        
        # During preparation, initial points can be moved freely
        if self.is_preparation_phase:
            return point_index < self._initial_points_placed
        
        # During regular rounds, points from previous rounds are locked
        point_round = self._point_round_map.get(point_index)
        return point_round == self._current_round
    
    def validate_initial_point_placement(
        self,
        x: float,
        y: float,
        grid_width: int,
        grid_height: int,
        is_start_point: bool
    ) -> None:
        """
        Validate that an initial control point is on the correct border.
        
        During preparation phase, the first point must be on the start border
        (left edge, x=0) and the second point must be on the end border
        (right edge, x=grid_width-1).
        
        Args:
            x: X coordinate of the point.
            y: Y coordinate of the point.
            grid_width: Width of the game grid.
            grid_height: Height of the game grid.
            is_start_point: True if this is the first point, False for second.
            
        Raises:
            ControlPointConstraintError: If point is not on required border.
        """
        if not self.is_preparation_phase:
            return  # Validation only applies during preparation
        
        # Start point must be on left border (x=0)
        if is_start_point:
            if x != 0:
                raise ControlPointConstraintError(
                    f"Start point must be on left border (x=0), got x={x}"
                )
        # End point must be on right border (x=grid_width-1)
        else:
            if x != grid_width - 1:
                raise ControlPointConstraintError(
                    f"End point must be on right border (x={grid_width-1}), got x={x}"
                )
        
        # Validate Y is within bounds
        if y < 0 or y >= grid_height:
            raise ControlPointConstraintError(
                f"Point Y coordinate must be within [0, {grid_height-1}], got y={y}"
            )
    
    def register_point_added(self, point_index: int) -> None:
        """
        Register that a control point was added.
        
        Args:
            point_index: Index of the added point.
            
        Raises:
            ControlPointConstraintError: If adding exceeds limits.
        """
        if not self.can_add_control_point():
            if self.is_preparation_phase:
                raise ControlPointConstraintError(
                    f"Cannot add more than {self.MAX_INITIAL_POINTS} points during preparation"
                )
            else:
                raise ControlPointConstraintError(
                    f"Cannot modify more than {self.MAX_POINTS_PER_ROUND} point per round"
                )
        
        if self.is_preparation_phase:
            self._initial_points_placed += 1
        else:
            self._points_modified_this_round += 1
        
        # Track which round this point was placed
        self._point_round_map[point_index] = self._current_round
        
        logger.debug(f"Point {point_index} added in round {self._current_round}")
    
    def register_point_removed(self, point_index: int) -> None:
        """
        Register that a control point was removed.
        
        Args:
            point_index: Index of the removed point.
            
        Raises:
            ControlPointConstraintError: If removal is not allowed.
        """
        if not self.can_remove_control_point(point_index):
            raise ControlPointConstraintError(
                f"Cannot remove point {point_index} - it's from a previous round or limit reached"
            )
        
        self._points_modified_this_round += 1
        
        # Remove from tracking
        if point_index in self._point_round_map:
            del self._point_round_map[point_index]
        
        logger.debug(f"Point {point_index} removed in round {self._current_round}")
    
    def transition_to(self, new_phase_type: PhaseType) -> None:
        """
        Transition to a new phase.
        
        Args:
            new_phase_type: The phase type to transition to.
            
        Raises:
            InvalidPhaseTransitionError: If transition is not allowed.
        """
        # Validate transition is allowed
        allowed_transitions = self._current_phase.get_allowed_transitions()
        if new_phase_type not in allowed_transitions:
            raise InvalidPhaseTransitionError(
                f"Cannot transition from {self._current_phase.phase_type.name} "
                f"to {new_phase_type.name}"
            )
        
        # Exit current phase
        self._current_phase.exit()
        
        # Create and enter new phase
        old_phase = self._current_phase.phase_type
        self._current_phase = create_phase_state(new_phase_type)
        self._current_phase.enter()
        
        # Reset modification counters when entering new modification phase
        if new_phase_type == PhaseType.PATH_MODIFICATION:
            self._points_modified_this_round = 0
        
        # Increment round when transitioning from combat to round end
        if old_phase == PhaseType.COMBAT and new_phase_type == PhaseType.ROUND_END:
            logger.info(f"Round {self._current_round} completed")
        
        # Increment round when starting new modification phase (after round end)
        if old_phase == PhaseType.ROUND_END and new_phase_type == PhaseType.PATH_MODIFICATION:
            self._current_round += 1
            logger.info(f"Starting round {self._current_round}")
        
        logger.info(f"Phase transition: {old_phase.name} -> {new_phase_type.name}")
    
    def reset(self, max_rounds: Optional[int] = None) -> None:
        """
        Reset the phase manager for a new game.
        
        Args:
            max_rounds: New maximum rounds (optional, keeps current if not provided).
        """
        if max_rounds is not None:
            self._max_rounds = max_rounds
        
        self._current_phase = create_phase_state(PhaseType.PREPARATION)
        self._current_round = 1
        self._points_modified_this_round = 0
        self._initial_points_placed = 0
        self._point_round_map.clear()
        
        logger.info(f"PhaseManager reset for new game ({self._max_rounds} rounds)")
    
    def is_match_complete(self) -> bool:
        """
        Check if the match is complete.
        
        Returns:
            True if all rounds have been completed, False otherwise.
        """
        return self._current_round > self._max_rounds
