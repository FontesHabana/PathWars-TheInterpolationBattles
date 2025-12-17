"""
Wave Manager for PathWars - The Interpolation Battles.

This module implements the WaveManager class that controls enemy spawning
during the BATTLE phase of the game.
"""

from enum import Enum, auto
from typing import Callable, List, Optional, Tuple

from core.wave_data import EnemySpawnConfig, WaveConfig, get_predefined_waves
from entities.base import EntityState
from entities.enemy import Enemy
from entities.factory import EntityFactory


class WaveEvent(Enum):
    """Enumeration of wave-related events."""
    WAVE_START = auto()
    WAVE_COMPLETE = auto()


class WaveManager:
    """
    Manager for enemy wave spawning and progression.

    Uses the Observer pattern to notify subscribers when waves start or complete.
    Follows Single Responsibility Principle by only managing waves, not combat.

    Attributes:
        current_wave: The current wave number (0 if no wave active).
        is_active: Whether a wave is currently in progress.
    """

    def __init__(self) -> None:
        """Initialize the WaveManager with predefined waves."""
        self._waves: List[WaveConfig] = get_predefined_waves()
        self._current_wave: int = 0
        self._is_active: bool = False
        self._path: List[Tuple[float, float]] = []
        
        # Spawn queue management
        self._spawn_queue: List[EnemySpawnConfig] = []
        self._current_spawn_config_index: int = 0
        self._current_spawn_count: int = 0
        self._spawn_timer: float = 0.0
        self._spawn_interval: float = 0.0
        
        # Track spawned enemies for wave completion
        self._spawned_enemies: List[Enemy] = []
        self._total_enemies_to_spawn: int = 0
        self._total_enemies_spawned: int = 0
        
        # Observer pattern - wave event subscribers
        self._wave_start_subscribers: List[Callable[[int], None]] = []
        self._wave_complete_subscribers: List[Callable[[int], None]] = []

    @property
    def current_wave(self) -> int:
        """Get the current wave number."""
        return self._current_wave

    @property
    def is_active(self) -> bool:
        """Check if a wave is currently active."""
        return self._is_active

    @property
    def total_waves(self) -> int:
        """Get the total number of waves."""
        return len(self._waves)

    @property
    def spawned_enemies(self) -> List[Enemy]:
        """
        Get the list of enemies spawned in the current wave.

        Returns:
            A copy of the spawned enemies list.
        """
        return list(self._spawned_enemies)

    def subscribe_wave_start(self, callback: Callable[[int], None]) -> None:
        """
        Subscribe to wave start events.

        Args:
            callback: Function to call when a wave starts.
                      Receives the wave number as an argument.
        """
        if callback not in self._wave_start_subscribers:
            self._wave_start_subscribers.append(callback)

    def subscribe_wave_complete(self, callback: Callable[[int], None]) -> None:
        """
        Subscribe to wave complete events.

        Args:
            callback: Function to call when a wave completes.
                      Receives the wave number as an argument.
        """
        if callback not in self._wave_complete_subscribers:
            self._wave_complete_subscribers.append(callback)

    def unsubscribe_wave_start(self, callback: Callable[[int], None]) -> None:
        """
        Unsubscribe from wave start events.

        Args:
            callback: The callback function to remove.
        """
        if callback in self._wave_start_subscribers:
            self._wave_start_subscribers.remove(callback)

    def unsubscribe_wave_complete(self, callback: Callable[[int], None]) -> None:
        """
        Unsubscribe from wave complete events.

        Args:
            callback: The callback function to remove.
        """
        if callback in self._wave_complete_subscribers:
            self._wave_complete_subscribers.remove(callback)

    def _notify_wave_start(self, wave_number: int) -> None:
        """
        Notify all subscribers that a wave has started.

        Args:
            wave_number: The wave number that started.
        """
        for callback in self._wave_start_subscribers:
            callback(wave_number)

    def _notify_wave_complete(self, wave_number: int) -> None:
        """
        Notify all subscribers that a wave has completed.

        Args:
            wave_number: The wave number that completed.
        """
        for callback in self._wave_complete_subscribers:
            callback(wave_number)

    def start_wave(
        self,
        wave_number: int,
        path: List[Tuple[float, float]]
    ) -> bool:
        """
        Start a new wave of enemies.

        Args:
            wave_number: The wave number to start (1-indexed).
            path: The path that enemies will follow.

        Returns:
            True if wave started successfully, False otherwise.

        Raises:
            ValueError: If wave_number is invalid or path is empty.
        """
        if wave_number < 1 or wave_number > len(self._waves):
            raise ValueError(
                f"Invalid wave number: {wave_number}. "
                f"Must be between 1 and {len(self._waves)}."
            )

        if not path:
            raise ValueError("Path cannot be empty")

        if self._is_active:
            return False  # Can't start a new wave while one is in progress

        self._current_wave = wave_number
        self._path = path
        self._is_active = True

        # Get wave configuration
        wave_config = self._waves[wave_number - 1]
        self._spawn_queue = list(wave_config.enemy_configs)
        self._spawn_interval = wave_config.spawn_interval
        
        # Reset spawn state
        self._current_spawn_config_index = 0
        self._current_spawn_count = 0
        # Initialize timer at spawn_interval so the first enemy spawns immediately
        # when update() is called. The update loop spawns when timer >= interval.
        self._spawn_timer = wave_config.spawn_interval
        self._spawned_enemies = []
        
        # Calculate total enemies
        self._total_enemies_to_spawn = sum(
            config.count for config in wave_config.enemy_configs
        )
        self._total_enemies_spawned = 0

        # Notify subscribers
        self._notify_wave_start(wave_number)

        return True

    def update(self, dt: float) -> List[Enemy]:
        """
        Update the wave manager and spawn enemies as needed.

        Should be called each frame during the BATTLE phase.

        Args:
            dt: Delta time since last update in seconds.

        Returns:
            List of newly spawned enemies this frame.
        """
        if not self._is_active:
            return []

        newly_spawned: List[Enemy] = []

        # Update spawn timer
        self._spawn_timer += dt

        # Spawn enemies while timer exceeds interval
        while (
            self._spawn_timer >= self._spawn_interval
            and self._current_spawn_config_index < len(self._spawn_queue)
        ):
            self._spawn_timer -= self._spawn_interval
            
            # Get current spawn config
            config = self._spawn_queue[self._current_spawn_config_index]
            
            # Create the enemy
            enemy = self._create_enemy_from_config(config)
            newly_spawned.append(enemy)
            self._spawned_enemies.append(enemy)
            self._total_enemies_spawned += 1
            
            # Advance spawn count
            self._current_spawn_count += 1
            
            # Check if we've spawned all enemies of this config
            if self._current_spawn_count >= config.count:
                self._current_spawn_config_index += 1
                self._current_spawn_count = 0

        return newly_spawned

    def _create_enemy_from_config(
        self,
        config: EnemySpawnConfig
    ) -> Enemy:
        """
        Create an enemy from a spawn configuration.

        Args:
            config: The enemy spawn configuration.

        Returns:
            A new Enemy instance.
        """
        # Get base stats for enemy type from the Enemy class stats
        base_stats = Enemy._ENEMY_STATS[config.enemy_type]
        
        # Apply modifiers
        modified_health = int(base_stats["health"] * config.health_modifier)
        modified_speed = base_stats["speed"] * config.speed_modifier
        
        return EntityFactory.create_enemy(
            enemy_type=config.enemy_type,
            path=self._path,
            health=modified_health,
            speed=modified_speed,
        )

    def is_wave_complete(self) -> bool:
        """
        Check if the current wave is complete.

        A wave is complete when all enemies have been spawned AND
        all spawned enemies are dead.

        Returns:
            True if the wave is complete, False otherwise.
        """
        if not self._is_active:
            return False

        # Check if all enemies have been spawned
        all_spawned = self._total_enemies_spawned >= self._total_enemies_to_spawn

        if not all_spawned:
            return False

        # Check if all spawned enemies are dead
        all_dead = all(
            enemy.state == EntityState.DEAD
            for enemy in self._spawned_enemies
        )

        if all_spawned and all_dead:
            # Wave is complete - notify and reset
            wave_number = self._current_wave
            self._is_active = False
            self._notify_wave_complete(wave_number)
            return True

        return False

    def get_current_wave(self) -> int:
        """
        Get the current wave number.

        Returns:
            The current wave number (1-indexed), or 0 if no wave is active.
        """
        return self._current_wave

    def get_wave_config(self, wave_number: int) -> Optional[WaveConfig]:
        """
        Get the configuration for a specific wave.

        Args:
            wave_number: The wave number to get (1-indexed).

        Returns:
            The WaveConfig for the specified wave, or None if invalid.
        """
        if wave_number < 1 or wave_number > len(self._waves):
            return None
        return self._waves[wave_number - 1]

    def has_more_waves(self) -> bool:
        """
        Check if there are more waves after the current one.

        Returns:
            True if there are more waves, False otherwise.
        """
        return self._current_wave < len(self._waves)

    def reset(self) -> None:
        """Reset the wave manager to initial state."""
        self._current_wave = 0
        self._is_active = False
        self._spawn_queue = []
        self._current_spawn_config_index = 0
        self._current_spawn_count = 0
        self._spawn_timer = 0.0
        self._spawned_enemies = []
        self._total_enemies_to_spawn = 0
        self._total_enemies_spawned = 0
