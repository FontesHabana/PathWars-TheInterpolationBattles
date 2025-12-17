"""
Base entity classes for the game.

This module defines the fundamental Entity class and Vector2 helper class.
"""

import uuid
from abc import ABC, abstractmethod
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Vector2:
    """
    A 2D vector representing a position or direction.
    
    Attributes:
        x: The x-coordinate.
        y: The y-coordinate.
    """
    x: float
    y: float
    
    def __iter__(self):
        """Allow unpacking as tuple."""
        return iter((self.x, self.y))
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert to tuple representation."""
        return (self.x, self.y)
    
    def distance_to(self, other: 'Vector2') -> float:
        """
        Calculate Euclidean distance to another Vector2.
        
        Args:
            other: The target Vector2.
            
        Returns:
            The distance between the two vectors.
        """
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


class Entity(ABC):
    """
    Abstract base class for all game entities.
    
    Entities are objects in the game world (Towers, Enemies) with a position
    and unique identifier.
    
    Attributes:
        position: The entity's position in 2D space.
        id: A unique identifier for the entity.
    """
    
    def __init__(self, position: Vector2):
        """
        Initialize an Entity.
        
        Args:
            position: The starting position of the entity.
        """
        self.position = position
        self.id = str(uuid.uuid4())
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the entity's state.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        pass
