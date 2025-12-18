"""
Base class for game phase states using State Pattern.
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .phase_manager import PhaseManager


class GamePhaseState(ABC):
    """Abstract base class for game phase states (State Pattern)."""
    
    def __init__(self, phase_manager: 'PhaseManager') -> None:
        self._phase_manager = phase_manager
        self._time_limit: Optional[float] = None  # None = no limit
        self._elapsed_time: float = 0.0
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this phase."""
        ...
    
    @property
    def time_remaining(self) -> Optional[float]:
        """Return remaining time, or None if no limit."""
        if self._time_limit is None:
            return None
        return max(0.0, self._time_limit - self._elapsed_time)
    
    @abstractmethod
    def enter(self) -> None:
        """Called when entering this phase."""
        ...
    
    @abstractmethod
    def exit(self) -> None:
        """Called when exiting this phase."""
        ...
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """Update the phase each frame."""
        ...
    
    @abstractmethod
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.
        Returns True if event was consumed.
        """
        ...
    
    @abstractmethod
    def can_transition_to(self, next_phase: str) -> bool:
        """Check if transition to the specified phase is valid."""
        ...
    
    def request_transition(self, next_phase: str) -> bool:
        """Request a phase transition through the manager."""
        return self._phase_manager.transition_to(next_phase)
