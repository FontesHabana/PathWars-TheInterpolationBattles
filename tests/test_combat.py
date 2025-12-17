"""
Unit tests for the Combat Manager in PathWars - The Interpolation Battles.

Tests cover tower targeting, damage application, enemy death handling,
money rewards, and base damage mechanics.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.combat_manager import CombatManager, ENEMY_REWARDS
from core.game_state import GameState
from entities.base import EntityState, Vector2
from entities.enemy import Enemy, EnemyType
from entities.tower import Tower, TowerType


@pytest.fixture
def game_state():
    """Fixture providing a fresh GameState for each test."""
    GameState.reset_instance()
    gs = GameState()
    return gs


@pytest.fixture
def combat_manager():
    """Fixture providing a fresh CombatManager for each test."""
    return CombatManager()


class TestCombatManagerBasics:
    """Tests for basic CombatManager functionality."""

    def test_combat_manager_creation(self, combat_manager):
        """Test CombatManager can be created."""
        assert combat_manager is not None
        assert combat_manager.active_attacks == []

    def test_observer_registration_enemy_killed(self, combat_manager):
        """Test registering an enemy killed callback."""
        callback_called = []

        def callback(enemy, reward):
            callback_called.append((enemy, reward))

        combat_manager.on_enemy_killed(callback)

        # Manually notify to test registration
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        combat_manager._notify_enemy_killed(enemy, 10)

        assert len(callback_called) == 1
        assert callback_called[0][0] == enemy
        assert callback_called[0][1] == 10

    def test_observer_registration_base_damaged(self, combat_manager):
        """Test registering a base damaged callback."""
        callback_called = []

        def callback(enemy):
            callback_called.append(enemy)

        combat_manager.on_base_damaged(callback)

        # Manually notify to test registration
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        combat_manager._notify_base_damaged(enemy)

        assert len(callback_called) == 1
        assert callback_called[0] == enemy


class TestTowerTargeting:
    """Tests for tower targeting behavior."""

    def test_tower_targets_nearest_enemy(self, game_state, combat_manager):
        """Test tower targets the nearest enemy in range."""
        # Create tower at (5, 5) with range 5.0 (CALCULUS)
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        game_state.add_entity('towers', tower)

        # Create enemies at different distances
        path = [(0, 0), (10, 10)]
        enemy_close = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)  # Distance 1.0
        enemy_far = Enemy(Vector2(2.0, 5.0), EnemyType.STUDENT, path)    # Distance 3.0

        game_state.add_entity('enemies', enemy_close)
        game_state.add_entity('enemies', enemy_far)

        # Run one combat update
        combat_manager.update(0.1, game_state)

        # Tower should have attacked the closer enemy
        assert enemy_close.health < 100
        assert enemy_far.health == 100

    def test_tower_does_not_target_out_of_range(self, game_state, combat_manager):
        """Test tower does not attack enemies out of range."""
        # Create DEAN tower with range 2.0
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        game_state.add_entity('towers', tower)

        # Create enemy far away
        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(20.0, 20.0), EnemyType.STUDENT, path)
        game_state.add_entity('enemies', enemy)

        # Run one combat update
        combat_manager.update(0.1, game_state)

        # Enemy should not have been attacked
        assert enemy.health == 100

    def test_tower_does_not_target_dead_enemies(self, game_state, combat_manager):
        """Test tower ignores dead enemies."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        dead_enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        dead_enemy.take_damage(100)  # Kill enemy

        living_enemy = Enemy(Vector2(6.0, 5.0), EnemyType.STUDENT, path)

        game_state.add_entity('enemies', dead_enemy)
        game_state.add_entity('enemies', living_enemy)

        # Run update
        combat_manager.update(0.1, game_state)

        # Living enemy should be attacked
        assert living_enemy.health < 100


class TestDamageApplication:
    """Tests for damage application mechanics."""

    def test_damage_applied_correctly(self, game_state, combat_manager):
        """Test correct damage amount is applied."""
        # CALCULUS tower does 25 damage
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        game_state.add_entity('enemies', enemy)

        combat_manager.update(0.1, game_state)

        assert enemy.health == 75  # 100 - 25

    def test_enemy_dies_at_zero_hp(self, game_state, combat_manager):
        """Test enemy dies when health reaches zero."""
        # PHYSICS tower does 50 damage
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        # VARIABLE_X has 50 HP, will die in one hit
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.VARIABLE_X, path)
        game_state.add_entity('enemies', enemy)

        combat_manager.update(0.1, game_state)

        assert enemy.health == 0
        assert enemy.state == EntityState.DEAD

    def test_tower_respects_cooldown(self, game_state, combat_manager):
        """Test tower cannot attack during cooldown."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)  # 2.0s cooldown
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        game_state.add_entity('enemies', enemy)

        # First attack
        combat_manager.update(0.1, game_state)
        assert enemy.health == 50  # 100 - 50

        # Second attack should fail (cooldown)
        combat_manager.update(0.1, game_state)
        assert enemy.health == 50  # No additional damage


class TestEnemyDeathHandling:
    """Tests for enemy death and removal."""

    def test_dead_enemy_removed_from_game_state(self, game_state, combat_manager):
        """Test dead enemies are removed from game state."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.VARIABLE_X, path)  # 50 HP
        game_state.add_entity('enemies', enemy)

        # Verify enemy is in game state
        assert len(game_state.entities_collection['enemies']) == 1

        # Kill enemy
        combat_manager.update(0.1, game_state)

        # Enemy should be removed
        assert len(game_state.entities_collection['enemies']) == 0

    def test_enemy_killed_callback_invoked(self, game_state, combat_manager):
        """Test enemy killed callback is invoked with correct reward."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)
        game_state.add_entity('towers', tower)

        killed_enemies = []

        def on_kill(enemy, reward):
            killed_enemies.append((enemy, reward))

        combat_manager.on_enemy_killed(on_kill)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path, health=50)
        game_state.add_entity('enemies', enemy)

        combat_manager.update(0.1, game_state)

        assert len(killed_enemies) == 1
        assert killed_enemies[0][1] == ENEMY_REWARDS[EnemyType.STUDENT]


class TestMoneyRewards:
    """Tests for money reward mechanics."""

    def test_money_reward_student(self, combat_manager):
        """Test money reward for STUDENT enemy."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        reward = combat_manager._get_reward(enemy)
        assert reward == 10

    def test_money_reward_variable_x(self, combat_manager):
        """Test money reward for VARIABLE_X enemy."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.VARIABLE_X, path)
        reward = combat_manager._get_reward(enemy)
        assert reward == 15


class TestBaseDamage:
    """Tests for base damage mechanics."""

    def test_base_damaged_when_enemy_reaches_end(self, game_state, combat_manager):
        """Test base damaged callback is invoked when enemy reaches path end."""
        base_damaged_enemies = []

        def on_base_damage(enemy):
            base_damaged_enemies.append(enemy)

        combat_manager.on_base_damaged(on_base_damage)

        # Create enemy that has already reached the end
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        # Move enemy to end of path
        enemy.update(10.0)  # At speed 1.0, 10 seconds to move through index 0 to 1

        game_state.add_entity('enemies', enemy)

        combat_manager.update(0.1, game_state)

        assert len(base_damaged_enemies) == 1
        assert base_damaged_enemies[0] == enemy

    def test_enemy_removed_after_reaching_end(self, game_state, combat_manager):
        """Test enemy is removed after reaching path end."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        enemy.update(10.0)  # Move to end

        game_state.add_entity('enemies', enemy)

        # Verify enemy is there
        assert len(game_state.entities_collection['enemies']) == 1

        combat_manager.update(0.1, game_state)

        # Enemy should be removed
        assert len(game_state.entities_collection['enemies']) == 0


class TestActiveAttacks:
    """Tests for active attacks visualization data."""

    def test_active_attacks_recorded(self, game_state, combat_manager):
        """Test active attacks are recorded for visualization."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        game_state.add_entity('enemies', enemy)

        combat_manager.update(0.1, game_state)

        assert len(combat_manager.active_attacks) == 1
        assert combat_manager.active_attacks[0][0] == tower
        assert combat_manager.active_attacks[0][1] == enemy

    def test_active_attacks_cleared_each_frame(self, game_state, combat_manager):
        """Test active attacks are cleared at start of each frame."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)  # 0.5s cooldown
        game_state.add_entity('towers', tower)

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        game_state.add_entity('enemies', enemy)

        # First update - should attack
        combat_manager.update(0.1, game_state)
        assert len(combat_manager.active_attacks) == 1

        # Second update - on cooldown, no attack
        combat_manager.update(0.1, game_state)
        assert len(combat_manager.active_attacks) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
