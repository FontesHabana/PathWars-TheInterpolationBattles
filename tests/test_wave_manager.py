"""
Unit tests for WaveManager in PathWars - The Interpolation Battles.

Tests cover wave starting, enemy spawning intervals, wave completion detection,
and wave progression.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.wave_data import EnemySpawnConfig, WaveConfig, get_predefined_waves
from core.wave_manager import WaveManager, WaveEvent
from entities.base import EntityState
from entities.enemy import Enemy, EnemyType


class TestEnemySpawnConfig:
    """Tests for the EnemySpawnConfig dataclass."""

    def test_enemy_spawn_config_creation(self):
        """Test basic EnemySpawnConfig creation."""
        config = EnemySpawnConfig(
            enemy_type=EnemyType.STUDENT,
            count=5
        )
        assert config.enemy_type == EnemyType.STUDENT
        assert config.count == 5
        assert config.health_modifier == 1.0
        assert config.speed_modifier == 1.0

    def test_enemy_spawn_config_with_modifiers(self):
        """Test EnemySpawnConfig with custom modifiers."""
        config = EnemySpawnConfig(
            enemy_type=EnemyType.VARIABLE_X,
            count=3,
            health_modifier=1.5,
            speed_modifier=1.2
        )
        assert config.enemy_type == EnemyType.VARIABLE_X
        assert config.count == 3
        assert config.health_modifier == 1.5
        assert config.speed_modifier == 1.2


class TestWaveConfig:
    """Tests for the WaveConfig dataclass."""

    def test_wave_config_creation(self):
        """Test basic WaveConfig creation."""
        enemy_configs = [
            EnemySpawnConfig(enemy_type=EnemyType.STUDENT, count=5)
        ]
        config = WaveConfig(
            wave_number=1,
            enemy_configs=enemy_configs,
            spawn_interval=2.0
        )
        assert config.wave_number == 1
        assert len(config.enemy_configs) == 1
        assert config.spawn_interval == 2.0


class TestPredefinedWaves:
    """Tests for predefined wave configurations."""

    def test_predefined_waves_count(self):
        """Test that there are exactly 5 predefined waves."""
        waves = get_predefined_waves()
        assert len(waves) == 5

    def test_predefined_waves_numbers(self):
        """Test that wave numbers are correct."""
        waves = get_predefined_waves()
        for i, wave in enumerate(waves):
            assert wave.wave_number == i + 1

    def test_predefined_waves_increasing_difficulty(self):
        """Test that waves have increasing enemy counts."""
        waves = get_predefined_waves()
        
        # Calculate total enemies per wave
        total_enemies = []
        for wave in waves:
            total = sum(config.count for config in wave.enemy_configs)
            total_enemies.append(total)
        
        # Each wave should have at least as many enemies as the previous
        for i in range(1, len(total_enemies)):
            assert total_enemies[i] >= total_enemies[i - 1], \
                f"Wave {i + 1} should have at least as many enemies as wave {i}"

    def test_predefined_waves_spawn_intervals(self):
        """Test that spawn intervals generally decrease (harder)."""
        waves = get_predefined_waves()
        
        # Later waves should have smaller or equal spawn intervals
        for i in range(1, len(waves)):
            assert waves[i].spawn_interval <= waves[i - 1].spawn_interval, \
                f"Wave {i + 1} spawn interval should be <= wave {i}"


class TestWaveManager:
    """Tests for the WaveManager class."""

    @pytest.fixture
    def wave_manager(self):
        """Create a fresh WaveManager for each test."""
        return WaveManager()

    @pytest.fixture
    def simple_path(self):
        """Create a simple path for testing."""
        return [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]

    def test_wave_manager_initialization(self, wave_manager):
        """Test WaveManager initializes correctly."""
        assert wave_manager.current_wave == 0
        assert not wave_manager.is_active
        assert wave_manager.total_waves == 5

    def test_start_wave_success(self, wave_manager, simple_path):
        """Test starting a wave successfully."""
        result = wave_manager.start_wave(1, simple_path)
        
        assert result is True
        assert wave_manager.current_wave == 1
        assert wave_manager.is_active

    def test_start_wave_invalid_number_too_low(self, wave_manager, simple_path):
        """Test starting an invalid wave number (too low)."""
        with pytest.raises(ValueError, match="Invalid wave number"):
            wave_manager.start_wave(0, simple_path)

    def test_start_wave_invalid_number_too_high(self, wave_manager, simple_path):
        """Test starting an invalid wave number (too high)."""
        with pytest.raises(ValueError, match="Invalid wave number"):
            wave_manager.start_wave(10, simple_path)

    def test_start_wave_empty_path(self, wave_manager):
        """Test starting a wave with empty path raises error."""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            wave_manager.start_wave(1, [])

    def test_start_wave_while_active(self, wave_manager, simple_path):
        """Test cannot start a new wave while one is active."""
        wave_manager.start_wave(1, simple_path)
        result = wave_manager.start_wave(2, simple_path)
        
        assert result is False
        assert wave_manager.current_wave == 1

    def test_get_current_wave(self, wave_manager, simple_path):
        """Test get_current_wave returns correct value."""
        assert wave_manager.get_current_wave() == 0
        
        wave_manager.start_wave(1, simple_path)
        assert wave_manager.get_current_wave() == 1

    def test_update_spawns_enemies(self, wave_manager, simple_path):
        """Test that update spawns enemies over time."""
        wave_manager.start_wave(1, simple_path)
        
        # First update should spawn an enemy immediately (timer starts at 0)
        enemies = wave_manager.update(0.0)
        assert len(enemies) == 1
        assert isinstance(enemies[0], Enemy)

    def test_update_respects_spawn_interval(self, wave_manager, simple_path):
        """Test that enemies spawn at correct intervals."""
        wave_manager.start_wave(1, simple_path)
        
        # Get wave config for spawn interval
        wave_config = wave_manager.get_wave_config(1)
        spawn_interval = wave_config.spawn_interval  # 2.0 seconds for wave 1
        
        # First spawn (immediate)
        enemies = wave_manager.update(0.0)
        assert len(enemies) == 1
        
        # Update with less than interval - no spawn
        enemies = wave_manager.update(spawn_interval * 0.5)
        assert len(enemies) == 0
        
        # Update to complete the interval - should spawn
        enemies = wave_manager.update(spawn_interval * 0.5)
        assert len(enemies) == 1

    def test_update_spawns_correct_enemy_types(self, wave_manager, simple_path):
        """Test that update spawns correct enemy types."""
        wave_manager.start_wave(1, simple_path)
        
        # Wave 1 should only have STUDENT enemies
        enemies = wave_manager.update(0.0)
        assert len(enemies) == 1
        assert enemies[0].enemy_type == EnemyType.STUDENT

    def test_update_when_not_active(self, wave_manager):
        """Test update returns empty list when wave not active."""
        enemies = wave_manager.update(1.0)
        assert len(enemies) == 0

    def test_spawned_enemies_list(self, wave_manager, simple_path):
        """Test that spawned enemies are tracked."""
        wave_manager.start_wave(1, simple_path)
        
        # Spawn first enemy
        wave_manager.update(0.0)
        
        spawned = wave_manager.spawned_enemies
        assert len(spawned) == 1

    def test_wave_complete_when_all_dead(self, wave_manager, simple_path):
        """Test wave is complete when all enemies spawned and dead."""
        wave_manager.start_wave(1, simple_path)
        
        # Get wave config to know how many enemies
        wave_config = wave_manager.get_wave_config(1)
        total_enemies = sum(c.count for c in wave_config.enemy_configs)
        spawn_interval = wave_config.spawn_interval
        
        # Spawn all enemies (more time than needed)
        total_time = spawn_interval * total_enemies * 2
        wave_manager.update(total_time)
        
        # Kill all enemies
        for enemy in wave_manager.spawned_enemies:
            enemy.take_damage(enemy.health)
        
        # Now wave should be complete
        assert wave_manager.is_wave_complete() is True
        assert wave_manager.is_active is False

    def test_wave_not_complete_enemies_alive(self, wave_manager, simple_path):
        """Test wave is not complete when enemies still alive."""
        wave_manager.start_wave(1, simple_path)
        
        # Spawn some enemies
        wave_config = wave_manager.get_wave_config(1)
        total_enemies = sum(c.count for c in wave_config.enemy_configs)
        spawn_interval = wave_config.spawn_interval
        
        # Spawn all enemies
        total_time = spawn_interval * total_enemies * 2
        wave_manager.update(total_time)
        
        # Don't kill any enemies
        assert wave_manager.is_wave_complete() is False
        assert wave_manager.is_active is True

    def test_wave_not_complete_not_all_spawned(self, wave_manager, simple_path):
        """Test wave is not complete when not all enemies spawned."""
        wave_manager.start_wave(1, simple_path)
        
        # Spawn only one enemy
        wave_manager.update(0.0)
        
        # Kill spawned enemy
        for enemy in wave_manager.spawned_enemies:
            enemy.take_damage(enemy.health)
        
        # Wave should not be complete (not all enemies spawned)
        assert wave_manager.is_wave_complete() is False

    def test_is_wave_complete_when_not_active(self, wave_manager):
        """Test is_wave_complete returns False when not active."""
        assert wave_manager.is_wave_complete() is False


class TestWaveManagerObserver:
    """Tests for WaveManager Observer pattern."""

    @pytest.fixture
    def wave_manager(self):
        """Create a fresh WaveManager for each test."""
        return WaveManager()

    @pytest.fixture
    def simple_path(self):
        """Create a simple path for testing."""
        return [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]

    def test_subscribe_wave_start(self, wave_manager, simple_path):
        """Test subscribing to wave start events."""
        received_events = []
        
        def on_wave_start(wave_num: int) -> None:
            received_events.append(("start", wave_num))
        
        wave_manager.subscribe_wave_start(on_wave_start)
        wave_manager.start_wave(1, simple_path)
        
        assert len(received_events) == 1
        assert received_events[0] == ("start", 1)

    def test_subscribe_wave_complete(self, wave_manager, simple_path):
        """Test subscribing to wave complete events."""
        received_events = []
        
        def on_wave_complete(wave_num: int) -> None:
            received_events.append(("complete", wave_num))
        
        wave_manager.subscribe_wave_complete(on_wave_complete)
        
        # Start and complete wave
        wave_manager.start_wave(1, simple_path)
        
        # Spawn all enemies
        wave_config = wave_manager.get_wave_config(1)
        total_enemies = sum(c.count for c in wave_config.enemy_configs)
        spawn_interval = wave_config.spawn_interval
        total_time = spawn_interval * total_enemies * 2
        wave_manager.update(total_time)
        
        # Kill all enemies
        for enemy in wave_manager.spawned_enemies:
            enemy.take_damage(enemy.health)
        
        # Check wave completion
        wave_manager.is_wave_complete()
        
        assert len(received_events) == 1
        assert received_events[0] == ("complete", 1)

    def test_unsubscribe_wave_start(self, wave_manager, simple_path):
        """Test unsubscribing from wave start events."""
        received_events = []
        
        def on_wave_start(wave_num: int) -> None:
            received_events.append(("start", wave_num))
        
        wave_manager.subscribe_wave_start(on_wave_start)
        wave_manager.unsubscribe_wave_start(on_wave_start)
        wave_manager.start_wave(1, simple_path)
        
        assert len(received_events) == 0

    def test_unsubscribe_wave_complete(self, wave_manager, simple_path):
        """Test unsubscribing from wave complete events."""
        received_events = []
        
        def on_wave_complete(wave_num: int) -> None:
            received_events.append(("complete", wave_num))
        
        wave_manager.subscribe_wave_complete(on_wave_complete)
        wave_manager.unsubscribe_wave_complete(on_wave_complete)
        
        # Start and complete wave
        wave_manager.start_wave(1, simple_path)
        wave_config = wave_manager.get_wave_config(1)
        total_enemies = sum(c.count for c in wave_config.enemy_configs)
        spawn_interval = wave_config.spawn_interval
        total_time = spawn_interval * total_enemies * 2
        wave_manager.update(total_time)
        
        for enemy in wave_manager.spawned_enemies:
            enemy.take_damage(enemy.health)
        
        wave_manager.is_wave_complete()
        
        assert len(received_events) == 0

    def test_multiple_subscribers(self, wave_manager, simple_path):
        """Test multiple subscribers receive events."""
        events1 = []
        events2 = []
        
        def callback1(wave_num: int) -> None:
            events1.append(wave_num)
        
        def callback2(wave_num: int) -> None:
            events2.append(wave_num)
        
        wave_manager.subscribe_wave_start(callback1)
        wave_manager.subscribe_wave_start(callback2)
        wave_manager.start_wave(1, simple_path)
        
        assert len(events1) == 1
        assert len(events2) == 1
        assert events1[0] == 1
        assert events2[0] == 1

    def test_duplicate_subscription_ignored(self, wave_manager, simple_path):
        """Test duplicate subscription is ignored."""
        events = []
        
        def callback(wave_num: int) -> None:
            events.append(wave_num)
        
        wave_manager.subscribe_wave_start(callback)
        wave_manager.subscribe_wave_start(callback)  # Duplicate
        wave_manager.start_wave(1, simple_path)
        
        assert len(events) == 1  # Should only fire once


class TestWaveProgression:
    """Tests for wave progression (wave 1 -> 2 -> etc)."""

    @pytest.fixture
    def wave_manager(self):
        """Create a fresh WaveManager for each test."""
        return WaveManager()

    @pytest.fixture
    def simple_path(self):
        """Create a simple path for testing."""
        return [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]

    def test_has_more_waves_initially(self, wave_manager):
        """Test has_more_waves when no waves started."""
        assert wave_manager.has_more_waves() is True

    def test_has_more_waves_during_game(self, wave_manager, simple_path):
        """Test has_more_waves during normal gameplay."""
        wave_manager.start_wave(1, simple_path)
        assert wave_manager.has_more_waves() is True

    def test_no_more_waves_after_last(self, wave_manager, simple_path):
        """Test has_more_waves returns False after last wave."""
        # Start wave 5 (last wave)
        wave_manager.start_wave(5, simple_path)
        
        # Complete the wave
        wave_config = wave_manager.get_wave_config(5)
        total_enemies = sum(c.count for c in wave_config.enemy_configs)
        spawn_interval = wave_config.spawn_interval
        total_time = spawn_interval * total_enemies * 2
        wave_manager.update(total_time)
        
        for enemy in wave_manager.spawned_enemies:
            enemy.take_damage(enemy.health)
        
        wave_manager.is_wave_complete()
        
        assert wave_manager.has_more_waves() is False

    def test_wave_progression(self, wave_manager, simple_path):
        """Test progressing through multiple waves."""
        start_events = []
        complete_events = []
        
        def on_start(wave_num: int) -> None:
            start_events.append(wave_num)
        
        def on_complete(wave_num: int) -> None:
            complete_events.append(wave_num)
        
        wave_manager.subscribe_wave_start(on_start)
        wave_manager.subscribe_wave_complete(on_complete)
        
        # Complete waves 1 and 2
        for wave_num in [1, 2]:
            wave_manager.start_wave(wave_num, simple_path)
            
            # Spawn all enemies
            wave_config = wave_manager.get_wave_config(wave_num)
            total_enemies = sum(c.count for c in wave_config.enemy_configs)
            spawn_interval = wave_config.spawn_interval
            total_time = spawn_interval * total_enemies * 2
            wave_manager.update(total_time)
            
            # Kill all enemies
            for enemy in wave_manager.spawned_enemies:
                enemy.take_damage(enemy.health)
            
            wave_manager.is_wave_complete()
        
        assert start_events == [1, 2]
        assert complete_events == [1, 2]

    def test_get_wave_config(self, wave_manager):
        """Test get_wave_config returns correct config."""
        config = wave_manager.get_wave_config(1)
        
        assert config is not None
        assert config.wave_number == 1

    def test_get_wave_config_invalid(self, wave_manager):
        """Test get_wave_config with invalid number returns None."""
        assert wave_manager.get_wave_config(0) is None
        assert wave_manager.get_wave_config(10) is None

    def test_reset_manager(self, wave_manager, simple_path):
        """Test resetting the wave manager."""
        wave_manager.start_wave(1, simple_path)
        wave_manager.update(0.0)
        
        wave_manager.reset()
        
        assert wave_manager.current_wave == 0
        assert wave_manager.is_active is False
        assert len(wave_manager.spawned_enemies) == 0


class TestEnemyModifiers:
    """Tests for enemy health and speed modifiers."""

    @pytest.fixture
    def wave_manager(self):
        """Create a fresh WaveManager for each test."""
        return WaveManager()

    @pytest.fixture
    def simple_path(self):
        """Create a simple path for testing."""
        return [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]

    def test_health_modifier_applied(self, wave_manager, simple_path):
        """Test that health modifiers are applied to spawned enemies."""
        # Wave 3 has health_modifier of 1.2 for students
        wave_manager.start_wave(3, simple_path)
        enemies = wave_manager.update(0.0)
        
        # Wave 3 first config is STUDENT with health_modifier=1.2
        # Base STUDENT health is 100, so modified should be 120
        assert len(enemies) == 1
        if enemies[0].enemy_type == EnemyType.STUDENT:
            assert enemies[0].max_health == 120

    def test_speed_modifier_applied(self, wave_manager, simple_path):
        """Test that speed modifiers are applied to spawned enemies."""
        # Wave 3 has speed_modifier of 1.1 for students
        wave_manager.start_wave(3, simple_path)
        enemies = wave_manager.update(0.0)
        
        # Wave 3 first config is STUDENT with speed_modifier=1.1
        # Base STUDENT speed is 1.0, so modified should be 1.1
        assert len(enemies) == 1
        if enemies[0].enemy_type == EnemyType.STUDENT:
            assert pytest.approx(enemies[0].speed, abs=0.01) == 1.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
