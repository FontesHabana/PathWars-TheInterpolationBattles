"""
Base entity classes for the game.

This module defines the abstract base class for all game entities.
"""

import uuid
from abc import ABC, abstractmethod


class Vector2:
    """
    Simple 2D vector class for position representation.

    Attributes:
        x: X coordinate
        y: Y coordinate
    """

    def __init__(self, x: float, y: float):
        """
        Initialize a 2D vector.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        """Return string representation of the vector."""
        return f"Vector2({self.x}, {self.y})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another Vector2."""
        if not isinstance(other, Vector2):
            return False
        return self.x == other.x and self.y == other.y

    def distance_to(self, other: 'Vector2') -> float:
        """
        Calculate Euclidean distance to another vector.

        Args:
            other: Target vector

        Returns:
            Distance to the other vector
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Entity(ABC):
    """
    Abstract base class for all game entities (towers, enemies, etc).

    Attributes:
        position: Current position of the entity
        id: Unique identifier for the entity
    """

    def __init__(self, position: Vector2):
        """
        Initialize an entity.

        Args:
            position: Initial position of the entity
        """
        self.position = position
        self.id = uuid.uuid4()

    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update entity state.

        Args:
            dt: Delta time since last update in seconds
        """
        pass
