"""
Base entity classes and types for PathWars - The Interpolation Battles.

This module defines the abstract base Entity class and common types used by
all game entities including enemies and towers.
"""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Tuple


class EntityType(Enum):
    """Enumeration of all entity types in the game."""
    ENEMY = auto()
    TOWER = auto()


class EntityState(Enum):
    """Enumeration of possible entity states."""
    IDLE = auto()
    ACTIVE = auto()
    DEAD = auto()


@dataclass
class Vector2:
    """
    A 2D vector representing position or direction.

    Attributes:
        x: The x coordinate.
        y: The y coordinate.
    """
    x: float
    y: float

    def __add__(self, other: "Vector2") -> "Vector2":
        """Add two vectors."""
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Vector2") -> "Vector2":
        """Subtract two vectors."""
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> "Vector2":
        """Multiply vector by a scalar."""
        return Vector2(self.x * scalar, self.y * scalar)

    def distance_to(self, other: "Vector2") -> float:
        """Calculate Euclidean distance to another vector."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def as_tuple(self) -> Tuple[float, float]:
        """Return vector as a tuple."""
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, t: Tuple[float, float]) -> "Vector2":
        """Create a Vector2 from a tuple."""
        return cls(t[0], t[1])


class Entity(ABC):
    """
    Abstract base class for all game entities.

    Attributes:
        id: Unique identifier for the entity.
        position: Current position in 2D space.
        entity_type: The type of entity (ENEMY or TOWER).
        state: Current state of the entity.
    """

    def __init__(
        self,
        position: Vector2,
        entity_type: EntityType,
    ) -> None:
        """
        Initialize a new Entity.

        Args:
            position: Initial position of the entity.
            entity_type: The type of entity being created.
        """
        self._id: str = str(uuid.uuid4())
        self._position: Vector2 = position
        self._entity_type: EntityType = entity_type
        self._state: EntityState = EntityState.IDLE

    @property
    def id(self) -> str:
        """Get the unique identifier of the entity."""
        return self._id

    @property
    def position(self) -> Vector2:
        """Get the current position of the entity."""
        return self._position

    @position.setter
    def position(self, value: Vector2) -> None:
        """Set the position of the entity."""
        self._position = value

    @property
    def entity_type(self) -> EntityType:
        """Get the type of the entity."""
        return self._entity_type

    @property
    def state(self) -> EntityState:
        """Get the current state of the entity."""
        return self._state

    @state.setter
    def state(self, value: EntityState) -> None:
        """Set the state of the entity."""
        self._state = value

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the entity state. Called each game tick.

        Args:
            dt: Delta time since last update in seconds.
        """
        pass
