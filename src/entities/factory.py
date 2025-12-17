"""
Factory for creating game entities in PathWars - The Interpolation Battles.

This module implements the Factory Method pattern for spawning different types
of towers and enemies.
"""

from typing import List, Optional, Tuple

from entities.base import Vector2
from entities.enemy import Enemy, EnemyType
from entities.tower import Tower, TowerType


class EntityFactory:
    """
    Factory for creating game entities.

    Provides static methods to create enemies and towers with default or
    custom configurations.
    """

    @staticmethod
    def create_enemy(
        enemy_type: EnemyType,
        path: List[Tuple[float, float]],
        health: Optional[int] = None,
        speed: Optional[float] = None,
    ) -> Enemy:
        """
        Create a new enemy of the specified type.

        Args:
            enemy_type: The type of enemy to create.
            path: List of (x, y) tuples defining the path to follow.
            health: Optional custom health value.
            speed: Optional custom speed value.

        Returns:
            A new Enemy instance.

        Raises:
            ValueError: If path is empty.
        """
        if not path:
            raise ValueError("Path cannot be empty")

        initial_position = Vector2(path[0][0], path[0][1])
        return Enemy(
            position=initial_position,
            enemy_type=enemy_type,
            path=path,
            health=health,
            speed=speed,
        )

    @staticmethod
    def create_tower(
        tower_type: TowerType,
        position: Tuple[float, float],
        damage: Optional[int] = None,
        attack_range: Optional[float] = None,
        cooldown: Optional[float] = None,
    ) -> Tower:
        """
        Create a new tower of the specified type.

        Args:
            tower_type: The type of tower to create.
            position: Tuple (x, y) for tower placement.
            damage: Optional custom damage value.
            attack_range: Optional custom attack range.
            cooldown: Optional custom cooldown time.

        Returns:
            A new Tower instance.
        """
        tower_position = Vector2(position[0], position[1])
        return Tower(
            position=tower_position,
            tower_type=tower_type,
            damage=damage,
            attack_range=attack_range,
            cooldown=cooldown,
        )

    @staticmethod
    def create_enemy_wave(
        enemy_type: EnemyType,
        path: List[Tuple[float, float]],
        count: int,
        health: Optional[int] = None,
        speed: Optional[float] = None,
    ) -> List[Enemy]:
        """
        Create a wave of enemies of the same type.

        Args:
            enemy_type: The type of enemies to create.
            path: List of (x, y) tuples defining the path to follow.
            count: Number of enemies to create.
            health: Optional custom health value for all enemies.
            speed: Optional custom speed value for all enemies.

        Returns:
            A list of Enemy instances.
        """
        return [
            EntityFactory.create_enemy(enemy_type, path, health, speed)
            for _ in range(count)
        ]
