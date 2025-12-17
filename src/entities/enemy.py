"""
Enemy entity classes for PathWars - The Interpolation Battles.

This module defines the Enemy class and enemy types that follow interpolated
paths across the game field.
"""

from enum import Enum, auto
from typing import List, Optional, Tuple

from entities.base import Entity, EntityState, EntityType, Vector2


class EnemyType(Enum):
    """Enumeration of enemy types in the game."""
    STUDENT = auto()      # Basic enemy
    VARIABLE_X = auto()   # Fast enemy


class Enemy(Entity):
    """
    An enemy entity that moves along a predefined path.

    Enemies follow an interpolated curve from start to end, taking damage
    from towers along the way.

    Attributes:
        enemy_type: The specific type of enemy.
        health: Current health points.
        max_health: Maximum health points.
        speed: Movement speed (path progress per second).
        path: List of points defining the path to follow.
        path_index: Current progress along the path (0.0 to len(path)-1).
    """

    # Default stats by enemy type
    _ENEMY_STATS = {
        EnemyType.STUDENT: {"health": 100, "speed": 1.0},
        EnemyType.VARIABLE_X: {"health": 50, "speed": 2.0},
    }

    def __init__(
        self,
        position: Vector2,
        enemy_type: EnemyType,
        path: List[Tuple[float, float]],
        health: Optional[int] = None,
        speed: Optional[float] = None,
    ) -> None:
        """
        Initialize a new Enemy.

        Args:
            position: Initial position of the enemy.
            enemy_type: The type of enemy to create.
            path: List of (x, y) tuples defining the path to follow.
            health: Override default health for this enemy type.
            speed: Override default speed for this enemy type.
        """
        super().__init__(position, EntityType.ENEMY)

        self._enemy_type = enemy_type
        stats = self._ENEMY_STATS[enemy_type]

        self._max_health: int = health if health is not None else stats["health"]
        self._health: int = self._max_health
        self._speed: float = speed if speed is not None else stats["speed"]

        self._path: List[Tuple[float, float]] = path
        self._path_index: float = 0.0
        self.state = EntityState.ACTIVE

    @property
    def enemy_type(self) -> EnemyType:
        """Get the type of enemy."""
        return self._enemy_type

    @property
    def health(self) -> int:
        """Get current health."""
        return self._health

    @property
    def max_health(self) -> int:
        """Get maximum health."""
        return self._max_health

    @property
    def speed(self) -> float:
        """Get movement speed."""
        return self._speed

    @property
    def path(self) -> List[Tuple[float, float]]:
        """Get the path the enemy follows."""
        return self._path

    @property
    def path_progress(self) -> float:
        """
        Get path progress as a percentage (0.0 to 1.0).

        Returns:
            Progress along the path from 0.0 (start) to 1.0 (end).
        """
        if len(self._path) <= 1:
            return 1.0
        return self._path_index / (len(self._path) - 1)

    @property
    def has_reached_end(self) -> bool:
        """Check if the enemy has reached the end of its path."""
        if len(self._path) == 0:
            return True
        return self._path_index >= len(self._path) - 1

    def take_damage(self, damage: int) -> None:
        """
        Apply damage to the enemy.

        Args:
            damage: Amount of damage to apply.
        """
        self._health = max(0, self._health - damage)
        if self._health <= 0:
            self.state = EntityState.DEAD

    def update(self, dt: float) -> None:
        """
        Update enemy position along the path.

        Args:
            dt: Delta time since last update in seconds.
        """
        if self.state == EntityState.DEAD or len(self._path) < 2:
            return

        # Advance along the path based on speed and delta time
        self._path_index += self._speed * dt

        # Clamp to path bounds
        if self._path_index >= len(self._path) - 1:
            self._path_index = len(self._path) - 1
            # Set position to final point
            final_point = self._path[-1]
            self._position = Vector2(final_point[0], final_point[1])
            return

        # Interpolate between current and next path points
        current_idx = int(self._path_index)
        next_idx = min(current_idx + 1, len(self._path) - 1)
        t = self._path_index - current_idx

        current_point = self._path[current_idx]
        next_point = self._path[next_idx]

        # Linear interpolation between path points
        new_x = current_point[0] + t * (next_point[0] - current_point[0])
        new_y = current_point[1] + t * (next_point[1] - current_point[1])

        self._position = Vector2(new_x, new_y)
