"""
Unit tests for game entities.

Tests for Entity, Enemy, Tower, and EntityFactory classes.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from entities.base import Vector2  # noqa: E402
from entities.enemy import Enemy, EnemyType, EnemyState  # noqa: E402
from entities.tower import Tower, TowerType, TowerState  # noqa: E402
from entities.factory import EntityFactory  # noqa: E402


class TestVector2:
    """Tests for Vector2 class."""

    def test_vector_creation(self):
        """Test vector creation and attributes."""
        v = Vector2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_vector_equality(self):
        """Test vector equality comparison."""
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(1.0, 2.0)
        v3 = Vector2(2.0, 1.0)
        assert v1 == v2
        assert v1 != v3

    def test_vector_distance(self):
        """Test distance calculation."""
        v1 = Vector2(0.0, 0.0)
        v2 = Vector2(3.0, 4.0)
        assert v1.distance_to(v2) == 5.0
        assert v2.distance_to(v1) == 5.0


class TestEnemy:
    """Tests for Enemy class."""

    def test_enemy_creation(self):
        """Test basic enemy creation."""
        path = [(0, 0), (10, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            health=100.0,
            speed=50.0
        )
        assert enemy.health == 100.0
        assert enemy.max_health == 100.0
        assert enemy.speed == 50.0
        assert enemy.state == EnemyState.MOVING
        assert enemy.is_alive()

    def test_enemy_movement_straight_line(self):
        """Test enemy movement along a straight line."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            speed=50.0
        )

        # Move for 1 second - should move 50 units
        enemy.update(1.0)
        assert pytest.approx(enemy.position.x, abs=0.1) == 50.0
        assert pytest.approx(enemy.position.y, abs=0.1) == 0.0
        assert enemy.state == EnemyState.MOVING

        # Move for another second - should reach end
        enemy.update(1.0)
        assert pytest.approx(enemy.position.x, abs=0.1) == 100.0
        assert pytest.approx(enemy.position.y, abs=0.1) == 0.0
        assert enemy.state == EnemyState.REACHED_END

    def test_enemy_movement_multiple_segments(self):
        """Test enemy movement through multiple path segments."""
        path = [(0, 0), (10, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            speed=10.0
        )

        # Move for 1 second - should reach first waypoint
        enemy.update(1.0)
        assert pytest.approx(enemy.position.x, abs=0.1) == 10.0
        assert pytest.approx(enemy.position.y, abs=0.1) == 0.0

        # Move for another 0.5 seconds - should be halfway to second waypoint
        enemy.update(0.5)
        assert pytest.approx(enemy.position.x, abs=0.1) == 10.0
        assert pytest.approx(enemy.position.y, abs=0.1) == 5.0
        assert enemy.state == EnemyState.MOVING

    def test_enemy_reaches_end(self):
        """Test that enemy correctly detects reaching the end."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            speed=100.0
        )

        enemy.update(1.0)
        assert enemy.has_reached_end()
        assert enemy.state == EnemyState.REACHED_END

    def test_enemy_take_damage(self):
        """Test enemy taking damage."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            health=100.0
        )

        # Take some damage
        killed = enemy.take_damage(30.0)
        assert not killed
        assert enemy.health == 70.0
        assert enemy.is_alive()

        # Take fatal damage
        killed = enemy.take_damage(80.0)
        assert killed
        assert enemy.health == 0.0
        assert not enemy.is_alive()
        assert enemy.state == EnemyState.DEAD

    def test_enemy_stops_when_dead(self):
        """Test that dead enemies don't move."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            enemy_type=EnemyType.BASIC,
            path=path,
            speed=50.0,
            health=10.0
        )

        enemy.take_damage(15.0)
        assert enemy.state == EnemyState.DEAD

        original_x = enemy.position.x
        enemy.update(1.0)
        assert enemy.position.x == original_x  # Should not have moved


class TestTower:
    """Tests for Tower class."""

    def test_tower_creation(self):
        """Test basic tower creation."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            damage=20.0,
            attack_range=100.0,
            cooldown=1.0
        )
        assert tower.damage == 20.0
        assert tower.range == 100.0
        assert tower.cooldown == 1.0
        assert tower.state == TowerState.IDLE
        assert tower.can_attack()

    def test_tower_find_target_in_range(self):
        """Test tower finding targets within range."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            attack_range=100.0
        )

        path = [(0, 0), (100, 50)]
        enemy1 = Enemy(Vector2(60, 50), EnemyType.BASIC, path)
        enemy1.path_index = 0.5

        enemy2 = Enemy(Vector2(200, 50), EnemyType.BASIC, path)
        enemy2.path_index = 0.8

        enemies = [enemy1, enemy2]
        target = tower.find_target(enemies)

        # Should target enemy1 since enemy2 is out of range (distance is 150)
        assert target == enemy1

    def test_tower_targets_closest_to_end(self):
        """Test tower prioritizes enemies closest to path end."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            attack_range=100.0
        )

        path = [(0, 0), (100, 50)]
        enemy1 = Enemy(Vector2(60, 50), EnemyType.BASIC, path)
        enemy1.path_index = 0.3

        enemy2 = Enemy(Vector2(80, 50), EnemyType.BASIC, path)
        enemy2.path_index = 0.8

        enemies = [enemy1, enemy2]
        target = tower.find_target(enemies)

        # Should target enemy2 since it's closer to end
        assert target == enemy2

    def test_tower_ignores_dead_enemies(self):
        """Test tower doesn't target dead enemies."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            attack_range=100.0
        )

        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(60, 50), EnemyType.BASIC, path, health=10.0)
        enemy.take_damage(20.0)

        enemies = [enemy]
        target = tower.find_target(enemies)

        assert target is None

    def test_tower_attack_cooldown(self):
        """Test tower cooldown mechanics."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            cooldown=1.0
        )

        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(60, 50), EnemyType.BASIC, path, health=100.0)

        # First attack should succeed
        assert tower.can_attack()
        success = tower.attack(enemy)
        assert success
        assert enemy.health == 80.0  # Default damage is 20

        # Should be on cooldown now
        assert not tower.can_attack()
        assert tower.cooldown_timer > 0

        # Second attack should fail
        success = tower.attack(enemy)
        assert not success
        assert enemy.health == 80.0  # No additional damage

        # After cooldown expires, should be able to attack again
        tower.update(1.5)
        assert tower.can_attack()
        success = tower.attack(enemy)
        assert success
        assert enemy.health == 60.0

    def test_tower_cooldown_progress(self):
        """Test cooldown progress calculation."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULUS,
            cooldown=2.0
        )

        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(60, 50), EnemyType.BASIC, path)

        tower.attack(enemy)
        assert pytest.approx(tower.get_cooldown_progress()) == 1.0

        tower.update(1.0)
        assert pytest.approx(tower.get_cooldown_progress()) == 0.5

        tower.update(1.0)
        assert pytest.approx(tower.get_cooldown_progress()) == 0.0

    def test_tower_damage_calculation(self):
        """Test that tower damage is correctly applied."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.PHYSICS,
            damage=50.0,
            attack_range=100.0
        )

        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(60, 50), EnemyType.BASIC, path, health=100.0)

        tower.attack(enemy)
        assert enemy.health == 50.0

        tower.update(2.0)  # Wait for cooldown
        killed = tower.attack(enemy)
        assert killed
        assert enemy.health == 0.0


class TestEntityFactory:
    """Tests for EntityFactory class."""

    def test_create_basic_enemy(self):
        """Test creating a basic enemy."""
        path = [(0, 0), (100, 0)]
        enemy = EntityFactory.create_enemy(EnemyType.BASIC, path)

        assert enemy.enemy_type == EnemyType.BASIC
        assert enemy.health == 100.0
        assert enemy.speed == 50.0
        assert enemy.reward == 10
        assert enemy.position.x == 0.0
        assert enemy.position.y == 0.0

    def test_create_fast_enemy(self):
        """Test creating a fast enemy."""
        path = [(5, 5), (100, 100)]
        enemy = EntityFactory.create_enemy(EnemyType.FAST, path)

        assert enemy.enemy_type == EnemyType.FAST
        assert enemy.health == 50.0
        assert enemy.speed == 100.0
        assert enemy.reward == 15
        assert enemy.position.x == 5.0
        assert enemy.position.y == 5.0

    def test_create_tank_enemy(self):
        """Test creating a tank enemy."""
        path = [(10, 10), (50, 50)]
        enemy = EntityFactory.create_enemy(EnemyType.TANK, path)

        assert enemy.enemy_type == EnemyType.TANK
        assert enemy.health == 200.0
        assert enemy.speed == 25.0
        assert enemy.reward == 20

    def test_create_calculus_tower(self):
        """Test creating a calculus tower."""
        tower = EntityFactory.create_tower(TowerType.CALCULUS, (50, 50))

        assert tower.tower_type == TowerType.CALCULUS
        assert tower.damage == 20.0
        assert tower.range == 120.0
        assert tower.cooldown == 0.8
        assert tower.position.x == 50.0
        assert tower.position.y == 50.0

    def test_create_physics_tower(self):
        """Test creating a physics tower."""
        tower = EntityFactory.create_tower(TowerType.PHYSICS, (100, 100))

        assert tower.tower_type == TowerType.PHYSICS
        assert tower.damage == 50.0
        assert tower.range == 150.0
        assert tower.cooldown == 2.5

    def test_create_dean_tower(self):
        """Test creating a dean tower."""
        tower = EntityFactory.create_tower(TowerType.DEAN, (25, 25))

        assert tower.tower_type == TowerType.DEAN
        assert tower.damage == 10.0
        assert tower.range == 80.0
        assert tower.cooldown == 2.0

    def test_create_statistics_tower(self):
        """Test creating a statistics tower (support)."""
        tower = EntityFactory.create_tower(TowerType.STATISTICS, (75, 75))

        assert tower.tower_type == TowerType.STATISTICS
        assert tower.damage == 0.0  # Support tower does no damage
        assert tower.range == 100.0
        assert tower.cooldown == 1.5

    def test_invalid_enemy_type(self):
        """Test that invalid enemy type raises error."""
        with pytest.raises(ValueError):
            EntityFactory.create_enemy("invalid_type", [(0, 0)])

    def test_invalid_tower_type(self):
        """Test that invalid tower type raises error."""
        with pytest.raises(ValueError):
            EntityFactory.create_tower("invalid_type", (0, 0))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
