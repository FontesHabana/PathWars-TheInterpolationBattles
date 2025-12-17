"""
Factory for creating game entities.

Provides convenient methods for spawning towers and enemies with proper configurations.
"""

from typing import List, Tuple
from .base import Vector2
from .enemy import Enemy, EnemyType
from .tower import Tower, TowerType


class EntityFactory:
    """
    Factory class for creating game entities.
    
    Uses the Factory Method pattern to centralize entity creation
    and ensure consistent initialization.
    """
    
    # Wave generation constants
    INITIAL_ENEMIES_PER_WAVE = 5
    ENEMIES_PER_WAVE_INCREASE = 3
    MAX_FAST_ENEMY_RATIO = 0.3
    FAST_ENEMY_RATIO_INCREMENT = 0.05
    
    @staticmethod
    def create_enemy(
        enemy_type: EnemyType,
        path: List[Tuple[float, float]],
        speed: float = None,
        health: float = None,
        reward: int = None
    ) -> Enemy:
        """
        Create an enemy of the specified type.
        
        Args:
            enemy_type: The type of enemy to create.
            path: The interpolated path the enemy will follow.
            speed: Override default speed (optional).
            health: Override default health (optional).
            reward: Override default reward (optional).
            
        Returns:
            A new Enemy instance.
            
        Raises:
            ValueError: If path is empty or invalid.
        """
        if not path or len(path) < 2:
            raise ValueError("Path must contain at least 2 points")
        
        # Starting position is the first point in the path
        start_pos = Vector2(*path[0])
        
        # Default stats based on enemy type
        default_stats = {
            EnemyType.STUDENT: {
                'speed': 50.0,
                'health': 100.0,
                'reward': 10
            },
            EnemyType.VARIABLE_X: {
                'speed': 75.0,  # Will be multiplied by 1.5 in Enemy.__init__
                'health': 70.0,  # Will be multiplied by 0.7 in Enemy.__init__
                'reward': 15
            }
        }
        
        stats = default_stats.get(enemy_type, default_stats[EnemyType.STUDENT])
        
        # Override with provided values
        if speed is not None:
            stats['speed'] = speed
        if health is not None:
            stats['health'] = health
        if reward is not None:
            stats['reward'] = reward
        
        return Enemy(
            position=start_pos,
            path=path,
            enemy_type=enemy_type,
            speed=stats['speed'],
            health=stats['health'],
            reward=stats['reward']
        )
    
    @staticmethod
    def create_tower(
        tower_type: TowerType,
        position: Tuple[float, float],
        level: int = 1
    ) -> Tower:
        """
        Create a tower of the specified type.
        
        Args:
            tower_type: The type of tower to create.
            position: The (x, y) position where the tower will be placed.
            level: The initial level of the tower (default: 1).
            
        Returns:
            A new Tower instance.
            
        Raises:
            ValueError: If level is less than 1.
        """
        if level < 1:
            raise ValueError("Tower level must be at least 1")
        
        pos = Vector2(*position)
        
        return Tower(
            position=pos,
            tower_type=tower_type,
            level=level
        )
    
    @staticmethod
    def create_wave(
        wave_number: int,
        path: List[Tuple[float, float]]
    ) -> List[Enemy]:
        """
        Create a wave of enemies for a given wave number.
        
        Generates an appropriate mix and difficulty of enemies based on
        the wave number.
        
        Args:
            wave_number: The wave number (1-5 typically).
            path: The path that enemies will follow.
            
        Returns:
            A list of Enemy instances for this wave.
            
        Raises:
            ValueError: If path is invalid.
        """
        if not path or len(path) < 2:
            raise ValueError("Path must contain at least 2 points")
        
        enemies = []
        
        # Scale difficulty with wave number
        base_count = (EntityFactory.INITIAL_ENEMIES_PER_WAVE + 
                     (wave_number - 1) * EntityFactory.ENEMIES_PER_WAVE_INCREASE)
        fast_enemy_ratio = min(EntityFactory.MAX_FAST_ENEMY_RATIO, 
                              wave_number * EntityFactory.FAST_ENEMY_RATIO_INCREMENT)
        
        fast_count = int(base_count * fast_enemy_ratio)
        student_count = base_count - fast_count
        
        # Create student enemies
        for _ in range(student_count):
            enemy = EntityFactory.create_enemy(
                EnemyType.STUDENT,
                path,
                health=100.0 + (wave_number - 1) * 20.0
            )
            enemies.append(enemy)
        
        # Create fast enemies
        for _ in range(fast_count):
            enemy = EntityFactory.create_enemy(
                EnemyType.VARIABLE_X,
                path,
                health=70.0 + (wave_number - 1) * 15.0
            )
            enemies.append(enemy)
        
        return enemies
