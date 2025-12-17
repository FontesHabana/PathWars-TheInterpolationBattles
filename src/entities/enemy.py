"""
Enemy entity implementation.

Enemies move along an interpolated path and can be targeted by towers.
"""

from typing import List, Tuple, Optional
from enum import Enum
from .base import Entity, Vector2


class EnemyType(Enum):
    """Types of enemies in the game."""
    STUDENT = "student"  # Basic enemy
    VARIABLE_X = "variable_x"  # Fast enemy


class EnemyState(Enum):
    """States an enemy can be in."""
    ALIVE = "alive"
    DEAD = "dead"
    REACHED_END = "reached_end"


class Enemy(Entity):
    """
    Enemy entity that follows an interpolated path.
    
    Enemies move along a predefined path (curve) and can be attacked by towers.
    When they reach the end of the path, they damage the player's base.
    
    Attributes:
        enemy_type: The type of enemy (affects stats).
        path: List of (x, y) positions defining the enemy's route.
        speed: Movement speed in units per second.
        health: Current health points.
        max_health: Maximum health points.
        state: Current state of the enemy.
        path_index: Current position index along the path.
        reward: Gold/currency awarded when defeated.
    """
    
    def __init__(
        self,
        position: Vector2,
        path: List[Tuple[float, float]],
        enemy_type: EnemyType = EnemyType.STUDENT,
        speed: float = 50.0,
        health: float = 100.0,
        reward: int = 10
    ):
        """
        Initialize an Enemy.
        
        Args:
            position: Starting position (should match path[0]).
            path: List of (x, y) coordinates defining the movement path.
            enemy_type: Type of enemy determining its characteristics.
            speed: Movement speed in units per second.
            health: Starting and maximum health.
            reward: Currency awarded when defeated.
        """
        super().__init__(position)
        self.enemy_type = enemy_type
        self.path = path
        self.speed = speed
        self.health = health
        self.max_health = health
        self.state = EnemyState.ALIVE
        self.path_index = 0.0  # Float for smooth interpolation
        self.reward = reward
        
        # Apply type-specific modifiers
        if enemy_type == EnemyType.VARIABLE_X:
            self.speed *= 1.5
            self.health *= 0.7
            self.reward = int(self.reward * 1.2)
    
    def update(self, dt: float) -> None:
        """
        Update enemy position along the path.
        
        Args:
            dt: Delta time since last update in seconds.
        """
        if self.state != EnemyState.ALIVE:
            return
        
        if not self.path or len(self.path) < 2:
            return
        
        # Calculate how far to move along the path
        distance_to_travel = self.speed * dt
        
        # Move along the path
        while distance_to_travel > 0 and self.path_index < len(self.path) - 1:
            current_idx = int(self.path_index)
            next_idx = current_idx + 1
            
            # Get current and next positions
            current_pos = Vector2(*self.path[current_idx])
            next_pos = Vector2(*self.path[next_idx])
            
            # Calculate distance to next point
            distance_to_next = current_pos.distance_to(next_pos)
            
            if distance_to_travel >= distance_to_next:
                # Move to next point
                self.path_index = float(next_idx)
                distance_to_travel -= distance_to_next
                self.position = next_pos
            else:
                # Interpolate between current and next point
                ratio = distance_to_travel / distance_to_next
                remaining_fraction = self.path_index - int(self.path_index)
                
                self.path_index += ratio
                
                # Update position by interpolating
                t = self.path_index - int(self.path_index)
                current_pos = Vector2(*self.path[int(self.path_index)])
                next_pos = Vector2(*self.path[min(int(self.path_index) + 1, len(self.path) - 1)])
                
                self.position = Vector2(
                    current_pos.x + (next_pos.x - current_pos.x) * t,
                    current_pos.y + (next_pos.y - current_pos.y) * t
                )
                distance_to_travel = 0
        
        # Check if reached the end
        if self.path_index >= len(self.path) - 1:
            self.state = EnemyState.REACHED_END
            self.position = Vector2(*self.path[-1])
    
    def take_damage(self, damage: float) -> None:
        """
        Apply damage to the enemy.
        
        Args:
            damage: Amount of damage to apply.
        """
        if self.state != EnemyState.ALIVE:
            return
        
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.state = EnemyState.DEAD
    
    def is_alive(self) -> bool:
        """Check if the enemy is still alive."""
        return self.state == EnemyState.ALIVE
    
    def has_reached_end(self) -> bool:
        """Check if the enemy reached the end of the path."""
        return self.state == EnemyState.REACHED_END
    
    def get_progress(self) -> float:
        """
        Get progress along the path as a fraction (0.0 to 1.0).
        
        Returns:
            Progress value between 0.0 (start) and 1.0 (end).
        """
        if not self.path or len(self.path) <= 1:
            return 1.0
        return min(self.path_index / (len(self.path) - 1), 1.0)
