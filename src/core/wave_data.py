"""
Wave configuration data for PathWars - The Interpolation Battles.

This module defines the dataclasses for wave configurations and provides
predefined waves with increasing difficulty.
"""

from dataclasses import dataclass, field
from typing import List

from entities.enemy import EnemyType


@dataclass
class EnemySpawnConfig:
    """
    Configuration for a group of enemies to spawn in a wave.

    Attributes:
        enemy_type: The type of enemy to spawn.
        count: Number of enemies of this type to spawn.
        health_modifier: Multiplier for base health (default 1.0).
        speed_modifier: Multiplier for base speed (default 1.0).
    """
    enemy_type: EnemyType
    count: int
    health_modifier: float = 1.0
    speed_modifier: float = 1.0


@dataclass
class WaveConfig:
    """
    Configuration for a complete wave of enemies.

    Attributes:
        wave_number: The wave number (1-indexed).
        enemy_configs: List of enemy spawn configurations for this wave.
        spawn_interval: Time in seconds between each enemy spawn.
    """
    wave_number: int
    enemy_configs: List[EnemySpawnConfig]
    spawn_interval: float


def get_predefined_waves() -> List[WaveConfig]:
    """
    Get the list of predefined waves for the game.

    Returns a list of 5 waves with increasing difficulty.

    Returns:
        List of WaveConfig objects defining each wave.
    """
    waves = [
        # Wave 1: Easy introduction - only basic STUDENT enemies
        WaveConfig(
            wave_number=1,
            enemy_configs=[
                EnemySpawnConfig(
                    enemy_type=EnemyType.STUDENT,
                    count=5,
                    health_modifier=1.0,
                    speed_modifier=1.0
                ),
            ],
            spawn_interval=2.0
        ),
        # Wave 2: More students, first VARIABLE_X enemies appear
        WaveConfig(
            wave_number=2,
            enemy_configs=[
                EnemySpawnConfig(
                    enemy_type=EnemyType.STUDENT,
                    count=7,
                    health_modifier=1.0,
                    speed_modifier=1.0
                ),
                EnemySpawnConfig(
                    enemy_type=EnemyType.VARIABLE_X,
                    count=3,
                    health_modifier=1.0,
                    speed_modifier=1.0
                ),
            ],
            spawn_interval=1.8
        ),
        # Wave 3: Increased enemy count and health
        WaveConfig(
            wave_number=3,
            enemy_configs=[
                EnemySpawnConfig(
                    enemy_type=EnemyType.STUDENT,
                    count=10,
                    health_modifier=1.2,
                    speed_modifier=1.1
                ),
                EnemySpawnConfig(
                    enemy_type=EnemyType.VARIABLE_X,
                    count=5,
                    health_modifier=1.2,
                    speed_modifier=1.1
                ),
            ],
            spawn_interval=1.5
        ),
        # Wave 4: Higher difficulty with tougher enemies
        WaveConfig(
            wave_number=4,
            enemy_configs=[
                EnemySpawnConfig(
                    enemy_type=EnemyType.STUDENT,
                    count=12,
                    health_modifier=1.5,
                    speed_modifier=1.2
                ),
                EnemySpawnConfig(
                    enemy_type=EnemyType.VARIABLE_X,
                    count=8,
                    health_modifier=1.3,
                    speed_modifier=1.2
                ),
            ],
            spawn_interval=1.2
        ),
        # Wave 5: Final wave - hardest difficulty
        WaveConfig(
            wave_number=5,
            enemy_configs=[
                EnemySpawnConfig(
                    enemy_type=EnemyType.STUDENT,
                    count=15,
                    health_modifier=2.0,
                    speed_modifier=1.3
                ),
                EnemySpawnConfig(
                    enemy_type=EnemyType.VARIABLE_X,
                    count=10,
                    health_modifier=1.5,
                    speed_modifier=1.4
                ),
            ],
            spawn_interval=1.0
        ),
    ]
    return waves
