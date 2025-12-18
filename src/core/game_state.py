"""
Game State module for managing the global game state.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional


class GamePhase(Enum):
    """Enumeration of game phases."""
    PLANNING = auto()
    WAITING = auto()
    BATTLE = auto()
    RESULT = auto()


class InsufficientFundsError(Exception):
    """Raised when there are insufficient funds for an operation."""
    pass


class InvalidPhaseTransitionError(Exception):
    """Raised when attempting an invalid phase transition."""
    pass


class GameState:
    """
    Singleton class managing the global game state.
    
    Implements the Singleton pattern to ensure only one instance exists
    per application. Uses the State pattern for game phase management.
    
    Attributes:
        money: Current amount of money available.
        lives: Current number of lives remaining.
        current_phase: Current game phase.
        entities_collection: Collection of game entities.
    """
    
    _instance: Optional['GameState'] = None
    
    def __new__(cls) -> 'GameState':
        """Create or return the singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize the game state if not already initialized."""
        if self._initialized:
            return
        
        self._money: int = 1000
        self._lives: int = 10
        self._current_phase: GamePhase = GamePhase.PLANNING
        self._entities_collection: Dict[str, List[Any]] = {
            'towers': [],
            'enemies': [],
        }
        self._initialized = True
    
    @classmethod
    def reset_instance(cls) -> None:
        """
        Reset the singleton instance. Useful for testing.
        """
        cls._instance = None
    
    def reset(self) -> None:
        """
        Reset the game state to initial values for a new game.
        """
        self._money = 1000
        self._lives = 10
        self._current_phase = GamePhase.PLANNING
        self._entities_collection = {
            'towers': [],
            'enemies': [],
        }

    
    @property
    def money(self) -> int:
        """Return current money amount."""
        return self._money
    
    @property
    def lives(self) -> int:
        """Return current lives."""
        return self._lives
    
    @property
    def current_phase(self) -> GamePhase:
        """Return current game phase."""
        return self._current_phase
    
    @property
    def entities_collection(self) -> Dict[str, List[Any]]:
        """
        Return a copy of the entities collection.
        
        Returns a copy to prevent accidental mutation by UI.
        """
        return {
            key: list(value) for key, value in self._entities_collection.items()
        }
    
    def change_phase(self, new_phase: GamePhase) -> None:
        """
        Change the current game phase.
        
        Validates that the phase transition is allowed.
        
        Args:
            new_phase: The new phase to transition to.
            
        Raises:
            InvalidPhaseTransitionError: If the transition is not allowed.
        """
        valid_transitions = {
            GamePhase.PLANNING: [GamePhase.WAITING],
            GamePhase.WAITING: [GamePhase.BATTLE],
            GamePhase.BATTLE: [GamePhase.RESULT, GamePhase.PLANNING],
            GamePhase.RESULT: [GamePhase.PLANNING],
        }
        
        allowed = valid_transitions.get(self._current_phase, [])
        if new_phase not in allowed:
            raise InvalidPhaseTransitionError(
                f"Cannot transition from {self._current_phase.name} to {new_phase.name}"
            )
        
        self._current_phase = new_phase
    
    def deduct_money(self, amount: int) -> None:
        """
        Deduct money from the current balance.
        
        Args:
            amount: The amount to deduct.
            
        Raises:
            ValueError: If amount is negative.
            InsufficientFundsError: If there are insufficient funds.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        
        if amount > self._money:
            raise InsufficientFundsError(
                f"Insufficient funds: have {self._money}, need {amount}"
            )
        
        self._money -= amount
    
    def add_money(self, amount: int) -> None:
        """
        Add money to the current balance.
        
        Args:
            amount: The amount to add.
            
        Raises:
            ValueError: If amount is negative.
        """
        if amount < 0:
            raise ValueError("Amount must be non-negative")
        self._money += amount
    
    def lose_life(self) -> bool:
        """
        Lose one life.
        
        Returns:
            True if lives remain, False if game over.
        """
        self._lives -= 1
        return self._lives > 0
    
    def add_entity(self, entity_type: str, entity: Any) -> None:
        """
        Add an entity to the collection.
        
        Args:
            entity_type: Type of entity ('towers' or 'enemies').
            entity: The entity to add.
        """
        if entity_type not in self._entities_collection:
            self._entities_collection[entity_type] = []
        self._entities_collection[entity_type].append(entity)
    
    def remove_entity(self, entity_type: str, entity: Any) -> bool:
        """
        Remove an entity from the collection.
        
        Args:
            entity_type: Type of entity ('towers' or 'enemies').
            entity: The entity to remove.
            
        Returns:
            True if the entity was removed, False otherwise.
        """
        if entity_type not in self._entities_collection:
            return False
        
        try:
            self._entities_collection[entity_type].remove(entity)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the game state to a dictionary.
        
        Includes money, lives, phase, and an entities summary (counts and positions).
        This is used for network synchronization with clients.
        
        Returns:
            Dictionary representation of the game state.
        """
        entities_summary: Dict[str, List[Dict[str, Any]]] = {}
        
        for entity_type, entities in self._entities_collection.items():
            entities_summary[entity_type] = []
            for entity in entities:
                entity_data: Dict[str, Any] = {}
                # Include entity id if available
                if hasattr(entity, 'id'):
                    entity_data['id'] = entity.id
                # Include position if available
                if hasattr(entity, 'position'):
                    pos = entity.position
                    if hasattr(pos, 'x') and hasattr(pos, 'y'):
                        entity_data['position'] = {'x': pos.x, 'y': pos.y}
                    elif hasattr(pos, 'as_tuple'):
                        x, y = pos.as_tuple()
                        entity_data['position'] = {'x': x, 'y': y}
                entities_summary[entity_type].append(entity_data)
        
        return {
            'money': self._money,
            'lives': self._lives,
            'phase': self._current_phase.name,
            'entities': entities_summary,
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update the game state from a dictionary (server snapshot).
        
        This method applies authoritative state from the server,
        updating money, lives, and phase. Note that entities are
        handled separately through entity-specific synchronization.
        
        Args:
            data: Dictionary containing game state data.
        """
        if 'money' in data:
            self._money = data['money']
        
        if 'lives' in data:
            self._lives = data['lives']
        
        if 'phase' in data:
            phase_name = data['phase']
            # Convert string phase name to GamePhase enum
            try:
                self._current_phase = GamePhase[phase_name]
            except KeyError:
                pass  # Keep current phase if invalid name provided
