"""
Phase Manager for controlling game phase transitions.
"""

from typing import Dict, Optional
import pygame

from .base_phase import GamePhaseState


class PhaseManager:
    """Manages game phase transitions following State Pattern."""
    
    def __init__(self) -> None:
        self._current_state: Optional[GamePhaseState] = None
        self._states: Dict[str, GamePhaseState] = {}
    
    def register_state(self, name: str, state: GamePhaseState) -> None:
        """
        Register a state with the manager.
        
        Args:
            name: Name identifier for the state.
            state: The state instance to register.
        """
        self._states[name] = state
    
    def transition_to(self, phase_name: str) -> bool:
        """
        Transition to a new phase.
        
        Validates transition and calls enter/exit hooks.
        
        Args:
            phase_name: Name of the phase to transition to.
            
        Returns:
            True if transition succeeded, False otherwise.
        """
        # Check if target phase exists
        if phase_name not in self._states:
            return False
        
        # Check if we have a current state
        if self._current_state is not None:
            # Validate the transition
            if not self._current_state.can_transition_to(phase_name):
                return False
            
            # Exit current state
            self._current_state.exit()
        
        # Transition to new state
        self._current_state = self._states[phase_name]
        self._current_state.enter()
        
        return True
    
    def update(self, dt: float) -> None:
        """
        Update current phase.
        
        Args:
            dt: Delta time in seconds since last update.
        """
        if self._current_state is not None:
            self._current_state.update(dt)
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Route input to current phase.
        
        Args:
            event: Pygame event to handle.
            
        Returns:
            True if event was consumed by the phase, False otherwise.
        """
        if self._current_state is not None:
            return self._current_state.handle_input(event)
        return False
    
    @property
    def current_phase_name(self) -> Optional[str]:
        """Get name of current phase."""
        if self._current_state is not None:
            return self._current_state.name
        return None
    
    @property
    def current_state(self) -> Optional[GamePhaseState]:
        """Get the current state instance."""
        return self._current_state
    
    def get_state(self, name: str) -> Optional[GamePhaseState]:
        """
        Get a registered state by name.
        
        Args:
            name: Name of the state to retrieve.
            
        Returns:
            The state instance, or None if not found.
        """
        return self._states.get(name)
