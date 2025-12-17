"""
Unit tests for game entities in PathWars - The Interpolation Battles.

Tests cover movement math, damage calculations, cooldowns, and factory methods.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from entities.base import Entity, EntityType, EntityState, Vector2
from entities.enemy import Enemy, EnemyType
from entities.tower import Tower, TowerType
from entities.factory import EntityFactory


class TestVector2:
    """Tests for the Vector2 class."""

    def test_vector2_creation(self):
        """Test basic vector creation."""
        v = Vector2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_vector2_addition(self):
        """Test vector addition."""
        v1 = Vector2(1.0, 2.0)
        v2 = Vector2(3.0, 4.0)
        result = v1 + v2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_vector2_subtraction(self):
        """Test vector subtraction."""
        v1 = Vector2(5.0, 7.0)
        v2 = Vector2(2.0, 3.0)
        result = v1 - v2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_vector2_scalar_multiplication(self):
        """Test scalar multiplication."""
        v = Vector2(2.0, 3.0)
        result = v * 2.0
        assert result.x == 4.0
        assert result.y == 6.0

    def test_vector2_scalar_right_multiplication(self):
        """Test scalar multiplication from the left (scalar * vector)."""
        v = Vector2(2.0, 3.0)
        result = 2.0 * v
        assert result.x == 4.0
        assert result.y == 6.0

    def test_vector2_distance(self):
        """Test distance calculation (3-4-5 triangle)."""
        v1 = Vector2(0.0, 0.0)
        v2 = Vector2(3.0, 4.0)
        assert v1.distance_to(v2) == 5.0

    def test_vector2_as_tuple(self):
        """Test tuple conversion."""
        v = Vector2(1.5, 2.5)
        assert v.as_tuple() == (1.5, 2.5)

    def test_vector2_from_tuple(self):
        """Test creation from tuple."""
        v = Vector2.from_tuple((3.0, 4.0))
        assert v.x == 3.0
        assert v.y == 4.0


class TestEnemy:
    """Tests for the Enemy class."""

    def test_enemy_creation_student(self):
        """Test creating a student enemy."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
        )
        assert enemy.enemy_type == EnemyType.STUDENT
        assert enemy.health == 100
        assert enemy.speed == 1.0
        assert enemy.state == EntityState.ACTIVE

    def test_enemy_creation_variable_x(self):
        """Test creating a Variable X enemy (fast type)."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.VARIABLE_X,
            path=path,
        )
        assert enemy.enemy_type == EnemyType.VARIABLE_X
        assert enemy.health == 50
        assert enemy.speed == 2.0

    def test_enemy_custom_stats(self):
        """Test creating an enemy with custom stats."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
            health=200,
            speed=1.5,
        )
        assert enemy.health == 200
        assert enemy.max_health == 200
        assert enemy.speed == 1.5

    def test_enemy_take_damage(self):
        """Test enemy damage calculation."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
        )
        enemy.take_damage(30)
        assert enemy.health == 70
        assert enemy.state == EntityState.ACTIVE

    def test_enemy_death_on_zero_health(self):
        """Test enemy dies when health reaches zero."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
        )
        enemy.take_damage(100)
        assert enemy.health == 0
        assert enemy.state == EntityState.DEAD

    def test_enemy_health_cannot_go_negative(self):
        """Test health is clamped at zero."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
        )
        enemy.take_damage(200)
        assert enemy.health == 0

    def test_enemy_movement_along_path(self):
        """Test enemy moves along its path."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
            speed=1.0,
        )

        # After 0.5 seconds at speed 1.0, should be at index 0.5
        enemy.update(0.5)
        assert pytest.approx(enemy.position.x, abs=0.01) == 5.0
        assert pytest.approx(enemy.position.y, abs=0.01) == 0.0

    def test_enemy_reaches_end_of_path(self):
        """Test enemy reaches the end of its path."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
            speed=1.0,
        )

        # Update for enough time to reach the end
        enemy.update(2.0)
        assert enemy.has_reached_end
        assert pytest.approx(enemy.position.x, abs=0.01) == 10.0
        assert pytest.approx(enemy.position.y, abs=0.01) == 0.0

    def test_enemy_path_progress(self):
        """Test path progress calculation."""
        path = [(0, 0), (5, 0), (10, 0)]  # 3 points, index 0 to 2
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
            speed=1.0,
        )

        assert enemy.path_progress == 0.0

        # After 1 second at speed 1.0, should be at index 1.0 (50% progress)
        enemy.update(1.0)
        assert pytest.approx(enemy.path_progress, abs=0.01) == 0.5

    def test_dead_enemy_does_not_move(self):
        """Test dead enemy doesn't update position."""
        path = [(0, 0), (10, 0)]
        enemy = Enemy(
            position=Vector2(0.0, 0.0),
            enemy_type=EnemyType.STUDENT,
            path=path,
        )
        enemy.take_damage(100)  # Kill enemy
        initial_pos = enemy.position

        enemy.update(1.0)
        assert enemy.position.x == initial_pos.x
        assert enemy.position.y == initial_pos.y


class TestTower:
    """Tests for the Tower class."""

    def test_tower_creation_dean(self):
        """Test creating a Dean tower."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.DEAN,
        )
        assert tower.tower_type == TowerType.DEAN
        assert tower.damage == 10
        assert tower.attack_range == 2.0
        assert tower.cooldown == 1.5
        assert tower.state == EntityState.ACTIVE

    def test_tower_creation_calculus(self):
        """Test creating a Calculus tower."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,
        )
        assert tower.tower_type == TowerType.CALCULUS
        assert tower.damage == 25
        assert tower.attack_range == 5.0
        assert tower.cooldown == 0.5

    def test_tower_creation_physics(self):
        """Test creating a Physics tower."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.PHYSICS,
        )
        assert tower.tower_type == TowerType.PHYSICS
        assert tower.damage == 50
        assert tower.attack_range == 4.0
        assert tower.cooldown == 2.0

    def test_tower_creation_statistics(self):
        """Test creating a Statistics tower."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.STATISTICS,
        )
        assert tower.tower_type == TowerType.STATISTICS
        assert tower.damage == 0  # Support tower deals no damage
        assert tower.attack_range == 3.5
        assert tower.cooldown == 1.0

    def test_tower_custom_stats(self):
        """Test creating a tower with custom stats."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.DEAN,
            damage=20,
            attack_range=5.0,
            cooldown=0.5,
        )
        assert tower.damage == 20
        assert tower.attack_range == 5.0
        assert tower.cooldown == 0.5

    def test_tower_cooldown_mechanics(self):
        """Test tower cooldown timing."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,
        )

        assert tower.can_attack
        assert tower.cooldown_remaining == 0

        # Simulate attacking
        path = [(4.0, 5.0), (6.0, 5.0)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        tower.attack(enemy)

        # After attack, cooldown should be reset
        assert not tower.can_attack
        assert tower.cooldown_remaining == 0.5

        # After partial cooldown
        tower.cooldown_check(0.3)
        assert not tower.can_attack
        assert pytest.approx(tower.cooldown_remaining, abs=0.01) == 0.2

        # After full cooldown
        tower.cooldown_check(0.3)
        assert tower.can_attack
        assert tower.cooldown_remaining == 0

    def test_tower_is_in_range(self):
        """Test range checking."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.DEAN,  # Range: 2.0
        )

        # In range
        assert tower.is_in_range(Vector2(5.0, 6.0))
        assert tower.is_in_range(Vector2(6.0, 5.0))

        # Out of range
        assert not tower.is_in_range(Vector2(5.0, 10.0))
        assert not tower.is_in_range(Vector2(10.0, 5.0))

    def test_tower_find_target_closest(self):
        """Test tower finds the closest target."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,  # Range: 5.0
        )

        path = [(0, 0), (10, 10)]
        enemy1 = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)  # Distance: 1.0
        enemy2 = Enemy(Vector2(2.0, 5.0), EnemyType.STUDENT, path)  # Distance: 3.0
        enemy3 = Enemy(Vector2(8.0, 5.0), EnemyType.STUDENT, path)  # Distance: 3.0

        target = tower.find_target([enemy1, enemy2, enemy3])
        assert target == enemy1

    def test_tower_find_target_ignores_dead(self):
        """Test tower ignores dead enemies."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,
        )

        path = [(0, 0), (10, 10)]
        enemy1 = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)
        enemy1.take_damage(100)  # Kill enemy1

        enemy2 = Enemy(Vector2(6.0, 5.0), EnemyType.STUDENT, path)

        target = tower.find_target([enemy1, enemy2])
        assert target == enemy2

    def test_tower_find_target_none_in_range(self):
        """Test tower returns None when no enemies in range."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.DEAN,  # Range: 2.0
        )

        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(20.0, 20.0), EnemyType.STUDENT, path)

        target = tower.find_target([enemy])
        assert target is None

    def test_tower_attack_deals_damage(self):
        """Test tower attack deals correct damage."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,  # Damage: 25
        )

        path = [(4.0, 5.0), (6.0, 5.0)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)

        damage_dealt = tower.attack(enemy)
        assert damage_dealt == 25
        assert enemy.health == 75

    def test_tower_attack_on_cooldown(self):
        """Test tower cannot attack while on cooldown."""
        tower = Tower(
            position=Vector2(5.0, 5.0),
            tower_type=TowerType.CALCULUS,
        )

        path = [(4.0, 5.0), (6.0, 5.0)]
        enemy = Enemy(Vector2(4.0, 5.0), EnemyType.STUDENT, path)

        # First attack works
        tower.attack(enemy)
        assert enemy.health == 75

        # Second attack should fail (on cooldown)
        damage = tower.attack(enemy)
        assert damage == 0
        assert enemy.health == 75  # No additional damage


class TestEntityFactory:
    """Tests for the EntityFactory class."""

    def test_factory_create_enemy(self):
        """Test factory creates enemies correctly."""
        path = [(0, 0), (10, 10)]
        enemy = EntityFactory.create_enemy(EnemyType.STUDENT, path)

        assert enemy.enemy_type == EnemyType.STUDENT
        assert enemy.position.x == 0
        assert enemy.position.y == 0
        assert enemy.health == 100

    def test_factory_create_enemy_custom_stats(self):
        """Test factory creates enemies with custom stats."""
        path = [(0, 0), (10, 10)]
        enemy = EntityFactory.create_enemy(
            EnemyType.STUDENT, path, health=200, speed=2.0
        )

        assert enemy.health == 200
        assert enemy.speed == 2.0

    def test_factory_create_enemy_empty_path_raises(self):
        """Test factory raises error for empty path."""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            EntityFactory.create_enemy(EnemyType.STUDENT, [])

    def test_factory_create_tower(self):
        """Test factory creates towers correctly."""
        tower = EntityFactory.create_tower(TowerType.CALCULUS, (5.0, 5.0))

        assert tower.tower_type == TowerType.CALCULUS
        assert tower.position.x == 5.0
        assert tower.position.y == 5.0
        assert tower.damage == 25

    def test_factory_create_tower_custom_stats(self):
        """Test factory creates towers with custom stats."""
        tower = EntityFactory.create_tower(
            TowerType.DEAN, (5.0, 5.0), damage=50, attack_range=10.0, cooldown=0.1
        )

        assert tower.damage == 50
        assert tower.attack_range == 10.0
        assert tower.cooldown == 0.1

    def test_factory_create_enemy_wave(self):
        """Test factory creates waves of enemies."""
        path = [(0, 0), (10, 10)]
        wave = EntityFactory.create_enemy_wave(EnemyType.VARIABLE_X, path, count=5)

        assert len(wave) == 5
        for enemy in wave:
            assert enemy.enemy_type == EnemyType.VARIABLE_X
            assert enemy.health == 50
            assert enemy.speed == 2.0


class TestEntityBase:
    """Tests for the base Entity class functionality."""

    def test_entity_has_unique_id(self):
        """Test each entity gets a unique ID."""
        path = [(0, 0), (10, 10)]
        enemy1 = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)
        enemy2 = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        assert enemy1.id != enemy2.id

    def test_entity_type_enemy(self):
        """Test enemy has correct entity type."""
        path = [(0, 0), (10, 10)]
        enemy = Enemy(Vector2(0, 0), EnemyType.STUDENT, path)

        assert enemy.entity_type == EntityType.ENEMY

    def test_entity_type_tower(self):
        """Test tower has correct entity type."""
        tower = Tower(Vector2(5, 5), TowerType.DEAN)

        assert tower.entity_type == EntityType.TOWER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
