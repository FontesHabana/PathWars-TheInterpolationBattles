"""
Factory for creating game entities.

This module provides factory methods for creating different types of enemies and towers.
"""

from typing import List, Tuple
from .base import Vector2
from .enemy import Enemy, EnemyType
from .tower import Tower, TowerType


class EntityFactory:
    """
    Factory class for creating game entities with predefined stats.
    """
    
    # Enemy stats by type
    ENEMY_STATS = {
        EnemyType.BASIC: {
            "health": 100.0,
            "speed": 50.0,
            "reward": 10
        },
        EnemyType.FAST: {
            "health": 50.0,
            "speed": 100.0,
            "reward": 15
        },
        EnemyType.TANK: {
            "health": 200.0,
            "speed": 25.0,
            "reward": 20
        }
    }
    
    # Tower stats by type
    TOWER_STATS = {
        TowerType.DEAN: {
            "damage": 10.0,
            "range": 80.0,
            "cooldown": 2.0
        },
        TowerType.CALCULUS: {
            "damage": 20.0,
            "range": 120.0,
            "cooldown": 0.8
        },
        TowerType.PHYSICS: {
            "damage": 50.0,
            "range": 150.0,
            "cooldown": 2.5
        },
        TowerType.STATISTICS: {
            "damage": 0.0,
            "range": 100.0,
            "cooldown": 1.5
        }
    }
    
    @staticmethod
    def create_enemy(
        enemy_type: EnemyType,
        path: List[Tuple[float, float]]
    ) -> Enemy:
        """
        Create an enemy of the specified type.
        
        Args:
            enemy_type: Type of enemy to create
            path: Path the enemy should follow (list of (x, y) coordinates)
            
        Returns:
            Enemy instance with appropriate stats
            
        Raises:
            ValueError: If enemy_type is not recognized
        """
        if enemy_type not in EntityFactory.ENEMY_STATS:
            raise ValueError(f"Unknown enemy type: {enemy_type}")
        
        stats = EntityFactory.ENEMY_STATS[enemy_type]
        
        # Start at the first point of the path
        if path and len(path) > 0:
            start_pos = Vector2(path[0][0], path[0][1])
        else:
            start_pos = Vector2(0, 0)
        
        return Enemy(
            position=start_pos,
            enemy_type=enemy_type,
            path=path,
            health=stats["health"],
            speed=stats["speed"],
            reward=stats["reward"]
        )
    
    @staticmethod
    def create_tower(
        tower_type: TowerType,
        position: Tuple[float, float]
    ) -> Tower:
        """
        Create a tower of the specified type.
        
        Args:
            tower_type: Type of tower to create
            position: Position to place the tower (x, y)
            
        Returns:
            Tower instance with appropriate stats
            
        Raises:
            ValueError: If tower_type is not recognized
        """
        if tower_type not in EntityFactory.TOWER_STATS:
            raise ValueError(f"Unknown tower type: {tower_type}")
        
        stats = EntityFactory.TOWER_STATS[tower_type]
        pos = Vector2(position[0], position[1])
        
        return Tower(
            position=pos,
            tower_type=tower_type,
            damage=stats["damage"],
            attack_range=stats["range"],
            cooldown=stats["cooldown"]
        )
