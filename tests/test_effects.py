"""
Unit tests for status effects in PathWars - The Interpolation Battles.

Tests cover stun effects, slow effects, effect expiration, and tower special
abilities.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.effects import EffectType, StatusEffect, EffectManager
from entities.base import Vector2, EntityState
from entities.enemy import Enemy, EnemyType
from entities.tower import Tower, TowerType


class TestStatusEffect:
    """Tests for the StatusEffect dataclass."""

    def test_status_effect_creation(self):
        """Test basic status effect creation."""
        effect = StatusEffect(EffectType.STUN, 1.0)
        assert effect.effect_type == EffectType.STUN
        assert effect.duration == 1.0
        assert effect.value == 0.0

    def test_status_effect_with_value(self):
        """Test status effect creation with a value."""
        effect = StatusEffect(EffectType.SLOW, 2.0, 0.5)
        assert effect.effect_type == EffectType.SLOW
        assert effect.duration == 2.0
        assert effect.value == 0.5


class TestEffectManager:
    """Tests for the EffectManager class."""

    def test_effect_manager_apply_effect(self):
        """Test applying an effect through the manager."""
        manager = EffectManager()
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        effect = StatusEffect(EffectType.STUN, 1.0)
        manager.apply_effect(enemy, effect)

        assert len(enemy.active_effects) == 1
        assert enemy.is_stunned()

    def test_effect_manager_update(self):
        """Test updating effects through the manager."""
        manager = EffectManager()
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        effect = StatusEffect(EffectType.STUN, 0.5)
        manager.apply_effect(enemy, effect)
        assert enemy.is_stunned()

        # Update with 0.6 seconds - effect should expire
        manager.update(0.6, [enemy])
        assert not enemy.is_stunned()


class TestEnemyEffects:
    """Tests for enemy status effect handling."""

    def test_enemy_apply_stun_effect(self):
        """Test applying stun effect to enemy."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        effect = StatusEffect(EffectType.STUN, 1.0)
        enemy.apply_effect(effect)

        assert enemy.is_stunned()
        assert len(enemy.active_effects) == 1

    def test_enemy_apply_slow_effect(self):
        """Test applying slow effect to enemy."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        effect = StatusEffect(EffectType.SLOW, 2.0, 0.5)
        enemy.apply_effect(effect)

        assert not enemy.is_stunned()
        assert enemy.get_slow_multiplier() == 0.5
        assert len(enemy.active_effects) == 1

    def test_stun_prevents_movement(self):
        """Test that stun effect prevents enemy movement."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path, speed=1.0)

        # Apply stun effect
        effect = StatusEffect(EffectType.STUN, 1.0)
        enemy.apply_effect(effect)

        initial_pos = enemy.position.x

        # Update enemy - should not move while stunned
        enemy.update(0.5)

        assert enemy.position.x == initial_pos

    def test_slow_reduces_speed(self):
        """Test that slow effect reduces enemy movement speed."""
        path = [(0, 0), (10, 0)]
        # Use speed of 1.0 for easy calculation
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path, speed=1.0)

        # First, move without slow to see normal distance
        enemy.update(0.5)
        normal_distance = enemy.position.x

        # Reset enemy
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path, speed=1.0)

        # Apply 50% slow effect
        effect = StatusEffect(EffectType.SLOW, 2.0, 0.5)
        enemy.apply_effect(effect)

        # Move with slow
        enemy.update(0.5)
        slow_distance = enemy.position.x

        # Should move at half speed
        assert pytest.approx(slow_distance, abs=0.01) == normal_distance * 0.5

    def test_effects_expire_after_duration(self):
        """Test that effects expire correctly after their duration."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        # Apply stun for 1 second
        effect = StatusEffect(EffectType.STUN, 1.0)
        enemy.apply_effect(effect)

        assert enemy.is_stunned()

        # Update for 0.5 seconds - still stunned
        enemy.update_effects(0.5)
        assert enemy.is_stunned()

        # Update for another 0.6 seconds - should be expired
        enemy.update_effects(0.6)
        assert not enemy.is_stunned()
        assert len(enemy.active_effects) == 0

    def test_effect_refresh_extends_duration(self):
        """Test that reapplying an effect refreshes its duration."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        # Apply stun for 1 second
        effect1 = StatusEffect(EffectType.STUN, 1.0)
        enemy.apply_effect(effect1)

        # Wait 0.5 seconds
        enemy.update_effects(0.5)
        assert enemy.is_stunned()

        # Reapply stun for 2 seconds
        effect2 = StatusEffect(EffectType.STUN, 2.0)
        enemy.apply_effect(effect2)

        # Should still have only 1 effect
        assert len(enemy.active_effects) == 1

        # After 1.5 more seconds, should still be stunned (since we had 2s duration)
        enemy.update_effects(1.5)
        assert enemy.is_stunned()

    def test_multiple_effect_types(self):
        """Test that multiple different effect types can be active."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        stun = StatusEffect(EffectType.STUN, 1.0)
        slow = StatusEffect(EffectType.SLOW, 2.0, 0.5)

        enemy.apply_effect(stun)
        enemy.apply_effect(slow)

        assert len(enemy.active_effects) == 2
        assert enemy.is_stunned()
        assert enemy.get_slow_multiplier() == 0.5


class TestTowerSpecialEffects:
    """Tests for tower special effects."""

    def test_dean_tower_stuns_enemy(self):
        """Test that DEAN tower stuns enemies for 1 second."""
        tower = Tower(Vector2(5, 5), TowerType.DEAN)
        path = [(4, 5), (6, 5)]
        enemy = Enemy(Vector2(4, 5), EnemyType.STUDENT, path)

        assert tower.stun_duration == 1.0

        tower.attack(enemy)

        assert enemy.is_stunned()
        # Verify stun duration is approximately 1 second
        effect = enemy.active_effects[0]
        assert effect.duration == 1.0

    def test_physics_tower_aoe_damage(self):
        """Test that PHYSICS tower deals AoE damage."""
        tower = Tower(Vector2(5, 5), TowerType.PHYSICS)
        path = [(4, 5), (6, 5)]

        # Primary target
        enemy1 = Enemy(Vector2(4, 5), EnemyType.STUDENT, path)
        # Close enemy (within splash radius of 2.0)
        enemy2 = Enemy(Vector2(5, 5), EnemyType.STUDENT, path)
        # Far enemy (outside splash radius)
        enemy3 = Enemy(Vector2(10, 10), EnemyType.STUDENT, path)

        all_enemies = [enemy1, enemy2, enemy3]

        assert tower.splash_radius == 2.0

        # Attack primary target with AoE
        tower.attack(enemy1, all_enemies)

        # Primary target takes damage
        assert enemy1.health == 50  # 100 - 50

        # Nearby enemy also takes damage
        assert enemy2.health == 50  # 100 - 50

        # Far enemy is unaffected
        assert enemy3.health == 100

    def test_statistics_tower_slows_enemy(self):
        """Test that STATISTICS tower slows enemies by 50% for 2 seconds."""
        tower = Tower(Vector2(5, 5), TowerType.STATISTICS)
        path = [(4, 5), (6, 5)]
        enemy = Enemy(Vector2(4, 5), EnemyType.STUDENT, path)

        assert tower.slow_amount == 0.5
        assert tower.slow_duration == 2.0

        tower.attack(enemy)

        assert enemy.get_slow_multiplier() == 0.5
        # Verify slow duration is approximately 2 seconds
        effect = enemy.active_effects[0]
        assert effect.duration == 2.0

    def test_calculus_tower_no_special_effect(self):
        """Test that CALCULUS tower has no special effects."""
        tower = Tower(Vector2(5, 5), TowerType.CALCULUS)
        path = [(4, 5), (6, 5)]
        enemy = Enemy(Vector2(4, 5), EnemyType.STUDENT, path)

        assert tower.stun_duration == 0.0
        assert tower.splash_radius == 0.0
        assert tower.slow_amount == 0.0

        tower.attack(enemy)

        # No effects should be applied
        assert len(enemy.active_effects) == 0
        assert not enemy.is_stunned()
        assert enemy.get_slow_multiplier() == 1.0


class TestEffectsIntegration:
    """Integration tests for effects with enemy movement."""

    def test_stunned_enemy_moves_after_stun_expires(self):
        """Test that enemy resumes movement after stun expires."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path, speed=1.0)

        # Apply 0.5 second stun
        effect = StatusEffect(EffectType.STUN, 0.5)
        enemy.apply_effect(effect)

        # Update for 0.3 seconds - still stunned, no movement
        enemy.update(0.3)
        assert enemy.position.x == 0

        # Update for another 0.3 seconds - stun expires, should start moving
        enemy.update(0.3)
        assert enemy.position.x > 0

    def test_slowed_enemy_returns_to_normal_speed(self):
        """Test that enemy returns to normal speed after slow expires."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path, speed=1.0)

        # Apply 0.5 second slow
        effect = StatusEffect(EffectType.SLOW, 0.5, 0.5)
        enemy.apply_effect(effect)

        # Move while slowed (0.4 seconds)
        enemy.update(0.4)
        slowed_position = enemy.position.x

        # Slow expires (0.2 seconds more)
        enemy.update(0.2)
        # Now at normal speed for remaining 0.1 seconds

        # Take another step at normal speed
        enemy.update(0.5)
        final_position = enemy.position.x

        # Should have moved further in the last 0.5s than in the first 0.4s
        distance_slowed = slowed_position
        distance_after = final_position - slowed_position - 0.1  # Subtract transition period

        assert distance_after > distance_slowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
