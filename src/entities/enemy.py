"""
Enemy entity logic for the game.

This module defines enemy behavior including movement along interpolated paths.
"""

from enum import Enum
from typing import List, Tuple
from .base import Entity, Vector2


class EnemyType(Enum):
    """Types of enemies in the game."""
    BASIC = "basic"  # Basic student - balanced stats
    FAST = "fast"    # Variable X - high speed, low health
    TANK = "tank"    # Heavy student - high health, slow


class EnemyState(Enum):
    """Possible states for an enemy."""
    MOVING = "moving"
    REACHED_END = "reached_end"
    DEAD = "dead"


class Enemy(Entity):
    """
    Enemy entity that moves along a predefined path.

    Attributes:
        enemy_type: Type of the enemy
        health: Current health points
        max_health: Maximum health points
        speed: Movement speed (units per second)
        path: List of waypoints defining the enemy's route
        path_index: Current position in the path
        state: Current state of the enemy
        reward: Money rewarded when killed
    """

    def __init__(
        self,
        position: Vector2,
        enemy_type: EnemyType,
        path: List[Tuple[float, float]],
        health: float = 100.0,
        speed: float = 50.0,
        reward: int = 10
    ):
        """
        Initialize an enemy.

        Args:
            position: Starting position
            enemy_type: Type of the enemy
            path: List of (x, y) coordinates defining the path
            health: Initial and maximum health
            speed: Movement speed in units per second
            reward: Money reward for killing this enemy
        """
        super().__init__(position)
        self.enemy_type = enemy_type
        self.max_health = health
        self.health = health
        self.speed = speed
        self.path = path
        self.path_index = 0.0  # Float for smooth interpolation
        self.state = EnemyState.MOVING
        self.reward = reward

    def update(self, dt: float) -> None:
        """
        Update enemy position based on path and speed.

        Args:
            dt: Delta time since last update in seconds
        """
        if self.state != EnemyState.MOVING:
            return

        if not self.path or len(self.path) < 2:
            self.state = EnemyState.REACHED_END
            return

        # Calculate how far to move along the path
        distance_to_move = self.speed * dt

        while distance_to_move > 0 and self.state == EnemyState.MOVING:
            # Get current and next waypoint
            current_idx = int(self.path_index)

            if current_idx >= len(self.path) - 1:
                # Reached the end
                self.state = EnemyState.REACHED_END
                if len(self.path) > 0:
                    self.position.x = self.path[-1][0]
                    self.position.y = self.path[-1][1]
                break

            current_pos = self.path[current_idx]
            next_pos = self.path[current_idx + 1]

            # Calculate distance to next waypoint
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            segment_length = (dx ** 2 + dy ** 2) ** 0.5

            if segment_length == 0:
                # Points are the same, skip to next
                self.path_index = current_idx + 1
                continue

            # Calculate current position within the segment
            segment_progress = self.path_index - current_idx

            # Calculate remaining distance in current segment
            remaining_in_segment = segment_length * (1.0 - segment_progress)

            if distance_to_move >= remaining_in_segment:
                # Move to next segment
                distance_to_move -= remaining_in_segment
                self.path_index = current_idx + 1
            else:
                # Move within current segment
                progress_increment = distance_to_move / segment_length
                self.path_index += progress_increment
                distance_to_move = 0

            # Update actual position
            current_idx = int(self.path_index)
            if current_idx >= len(self.path) - 1:
                self.position.x = self.path[-1][0]
                self.position.y = self.path[-1][1]
                self.state = EnemyState.REACHED_END
            else:
                segment_progress = self.path_index - current_idx
                current_pos = self.path[current_idx]
                next_pos = self.path[current_idx + 1]
                self.position.x = current_pos[0] + \
                    (next_pos[0] - current_pos[0]) * segment_progress
                self.position.y = current_pos[1] + \
                    (next_pos[1] - current_pos[1]) * segment_progress

    def take_damage(self, amount: float) -> bool:
        """
        Apply damage to the enemy.

        Args:
            amount: Damage amount

        Returns:
            True if the enemy died, False otherwise
        """
        if self.state == EnemyState.DEAD:
            return False

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.state = EnemyState.DEAD
            return True
        return False

    def is_alive(self) -> bool:
        """
        Check if the enemy is still alive.

        Returns:
            True if alive, False otherwise
        """
        return self.state != EnemyState.DEAD

    def has_reached_end(self) -> bool:
        """
        Check if the enemy has reached the end of the path.

        Returns:
            True if reached end, False otherwise
        """
        return self.state == EnemyState.REACHED_END
