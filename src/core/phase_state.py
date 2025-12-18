"""
Game Phase State Pattern implementation.

This module implements the State Pattern for managing game phases.
Each phase defines specific behavior and allowed transitions.

MULTIPLAYER ASYMMETRIC MODEL:
In multiplayer, the game uses an asymmetric model:
- PATH_MODIFICATION/PREPARATION: Players edit control points on the RIVAL's map
  to design the attack path for their enemies.
- BUILDING: Players place towers on their OWN map to defend against the rival's
  incoming enemies.
- COMBAT: Enemies follow paths, towers defend. Players can CONTINUE to build/upgrade
  towers during combat.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto


class PhaseType(Enum):
    """Enumeration of phase types in the game loop."""
    PREPARATION = auto()      # Initial round only: place 2 starting points
    PATH_MODIFICATION = auto() # Modify path, change strategy, queue mercenaries
    BUILDING = auto()         # Place/upgrade towers
    COMBAT = auto()           # Wave execution
    ROUND_END = auto()        # Between rounds


class InvalidPhaseActionError(Exception):
    """Raised when an invalid action is attempted in the current phase."""
    pass


class GamePhaseState(ABC):
    """
    Abstract base class for game phase states.
    
    Implements the State Pattern for game phase management.
    Each concrete state defines what actions are allowed and
    what transitions are valid.
    """
    
    @property
    @abstractmethod
    def phase_type(self) -> PhaseType:
        """Return the type of this phase."""
        pass
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this phase."""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this phase."""
        pass
    
    @abstractmethod
    def can_place_tower(self) -> bool:
        """Return whether towers can be placed in this phase."""
        pass
    
    @abstractmethod
    def can_modify_path(self) -> bool:
        """Return whether control points can be modified in this phase."""
        pass
    
    @abstractmethod
    def can_send_mercenaries(self) -> bool:
        """Return whether mercenaries can be sent in this phase."""
        pass
    
    @abstractmethod
    def can_research(self) -> bool:
        """Return whether research can be conducted in this phase."""
        pass
    
    @abstractmethod
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Return list of valid phase transitions from this state."""
        pass


class PreparationPhaseState(GamePhaseState):
    """
    Initial preparation phase (Round 1 only).
    
    In multiplayer: Players place 2 initial control points on the RIVAL's map
    (start/end borders) to define the attack path their enemies will follow.
    These points can be moved freely during this phase.
    """
    
    @property
    def phase_type(self) -> PhaseType:
        return PhaseType.PREPARATION
    
    def enter(self) -> None:
        """Initialize preparation phase."""
        pass
    
    def exit(self) -> None:
        """Lock initial points when exiting preparation."""
        pass
    
    def can_place_tower(self) -> bool:
        """Cannot place towers during preparation."""
        return False
    
    def can_modify_path(self) -> bool:
        """Can modify path (place initial 2 points)."""
        return True
    
    def can_send_mercenaries(self) -> bool:
        """Cannot send mercenaries during initial preparation."""
        return False
    
    def can_research(self) -> bool:
        """Cannot research during preparation."""
        return False
    
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Can only transition to building phase."""
        return [PhaseType.BUILDING]


class PathModificationPhaseState(GamePhaseState):
    """
    Path modification phase (Rounds 2+).
    
    In multiplayer: Players modify control points on the RIVAL's map to adjust
    the attack path for their enemies.
    
    Players can:
    - Add or remove at most 1 control point on the rival's map
    - Change interpolation method
    - Queue mercenaries for the rival
    
    Previously placed points cannot be moved, only removed.
    """
    
    @property
    def phase_type(self) -> PhaseType:
        return PhaseType.PATH_MODIFICATION
    
    def enter(self) -> None:
        """Initialize path modification phase."""
        pass
    
    def exit(self) -> None:
        """Lock any new points when exiting."""
        pass
    
    def can_place_tower(self) -> bool:
        """Cannot place towers during path modification."""
        return False
    
    def can_modify_path(self) -> bool:
        """Can modify path (add/remove 1 point)."""
        return True
    
    def can_send_mercenaries(self) -> bool:
        """Can send mercenaries during path modification."""
        return True
    
    def can_research(self) -> bool:
        """Can conduct research during path modification."""
        return True
    
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Can transition to building phase."""
        return [PhaseType.BUILDING]


class BuildingPhaseState(GamePhaseState):
    """
    Building phase.
    
    In multiplayer: Players place towers or upgrade existing ones on their OWN map
    to defend against the rival's incoming enemies.
    
    This happens before enemies spawn but after the attack path is set.
    """
    
    @property
    def phase_type(self) -> PhaseType:
        return PhaseType.BUILDING
    
    def enter(self) -> None:
        """Initialize building phase."""
        pass
    
    def exit(self) -> None:
        """Finalize building phase."""
        pass
    
    def can_place_tower(self) -> bool:
        """Can place towers during building phase."""
        return True
    
    def can_modify_path(self) -> bool:
        """Cannot modify path during building."""
        return False
    
    def can_send_mercenaries(self) -> bool:
        """Cannot send mercenaries during building."""
        return False
    
    def can_research(self) -> bool:
        """Cannot research during building."""
        return False
    
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Can transition to combat phase."""
        return [PhaseType.COMBAT]


class CombatPhaseState(GamePhaseState):
    """
    Combat phase (Wave execution).
    
    Enemies spawn and travel the interpolated path.
    Players can continue building/upgrading towers during combat.
    Phase ends when wave is cleared or lives reach 0.
    """
    
    @property
    def phase_type(self) -> PhaseType:
        return PhaseType.COMBAT
    
    def enter(self) -> None:
        """Initialize combat phase."""
        pass
    
    def exit(self) -> None:
        """Clean up combat phase."""
        pass
    
    def can_place_tower(self) -> bool:
        """Can place towers during combat."""
        return True
    
    def can_modify_path(self) -> bool:
        """Cannot modify path during combat."""
        return False
    
    def can_send_mercenaries(self) -> bool:
        """Cannot send mercenaries during combat."""
        return False
    
    def can_research(self) -> bool:
        """Cannot research during combat."""
        return False
    
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Can transition to round end."""
        return [PhaseType.ROUND_END]


class RoundEndPhaseState(GamePhaseState):
    """
    Round end phase.
    
    Brief pause between rounds to show results.
    Transitions back to path modification for next round.
    """
    
    @property
    def phase_type(self) -> PhaseType:
        return PhaseType.ROUND_END
    
    def enter(self) -> None:
        """Initialize round end phase."""
        pass
    
    def exit(self) -> None:
        """Transition to next round."""
        pass
    
    def can_place_tower(self) -> bool:
        """Cannot place towers during round end."""
        return False
    
    def can_modify_path(self) -> bool:
        """Cannot modify path during round end."""
        return False
    
    def can_send_mercenaries(self) -> bool:
        """Cannot send mercenaries during round end."""
        return False
    
    def can_research(self) -> bool:
        """Cannot research during round end."""
        return False
    
    def get_allowed_transitions(self) -> list[PhaseType]:
        """Can transition to path modification for next round."""
        return [PhaseType.PATH_MODIFICATION]


# Factory for creating phase state instances
_PHASE_STATE_MAP = {
    PhaseType.PREPARATION: PreparationPhaseState,
    PhaseType.PATH_MODIFICATION: PathModificationPhaseState,
    PhaseType.BUILDING: BuildingPhaseState,
    PhaseType.COMBAT: CombatPhaseState,
    PhaseType.ROUND_END: RoundEndPhaseState,
}


def create_phase_state(phase_type: PhaseType) -> GamePhaseState:
    """
    Factory function to create phase state instances.
    
    Args:
        phase_type: The type of phase to create.
        
    Returns:
        A new instance of the appropriate phase state.
        
    Raises:
        ValueError: If phase_type is invalid.
    """
    state_class = _PHASE_STATE_MAP.get(phase_type)
    if state_class is None:
        raise ValueError(f"Unknown phase type: {phase_type}")
    return state_class()
