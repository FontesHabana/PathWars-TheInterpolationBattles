"""
Unit tests for game entities.

Tests the behavior of Entity, Enemy, Tower, and EntityFactory classes.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from entities.base import Entity, Vector2
from entities.enemy import Enemy, EnemyType, EnemyState
from entities.tower import Tower, TowerType
from entities.factory import EntityFactory


class TestVector2:
    """Tests for Vector2 class."""
    
    def test_vector_creation(self):
        """Test basic vector creation."""
        v = Vector2(3.0, 4.0)
        assert v.x == 3.0
        assert v.y == 4.0
    
    def test_vector_to_tuple(self):
        """Test conversion to tuple."""
        v = Vector2(5.0, 6.0)
        assert v.to_tuple() == (5.0, 6.0)
    
    def test_vector_distance(self):
        """Test distance calculation."""
        v1 = Vector2(0.0, 0.0)
        v2 = Vector2(3.0, 4.0)
        assert v1.distance_to(v2) == 5.0
    
    def test_vector_unpacking(self):
        """Test that vector can be unpacked."""
        v = Vector2(10.0, 20.0)
        x, y = v
        assert x == 10.0
        assert y == 20.0


class TestEnemy:
    """Tests for Enemy class."""
    
    def test_enemy_creation(self):
        """Test basic enemy creation."""
        path = [(0, 0), (100, 0), (100, 100)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            enemy_type=EnemyType.STUDENT
        )
        
        assert enemy.position.x == 0
        assert enemy.position.y == 0
        assert enemy.enemy_type == EnemyType.STUDENT
        assert enemy.is_alive()
        assert enemy.health == 100.0
    
    def test_enemy_movement(self):
        """Test that enemy moves along the path."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            speed=50.0
        )
        
        # After 1 second at 50 units/sec, should be at position 50,0
        enemy.update(1.0)
        
        assert enemy.position.x == pytest.approx(50.0, abs=1.0)
        assert enemy.position.y == pytest.approx(0.0, abs=1.0)
        assert enemy.is_alive()
    
    def test_enemy_reaches_end(self):
        """Test that enemy reaches end of path."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            speed=50.0
        )
        
        # After 3 seconds should have reached the end (100 units at 50 units/sec = 2 sec)
        enemy.update(3.0)
        
        assert enemy.has_reached_end()
        assert enemy.position.x == pytest.approx(100.0, abs=1.0)
    
    def test_enemy_takes_damage(self):
        """Test enemy damage mechanics."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            health=100.0
        )
        
        enemy.take_damage(30.0)
        assert enemy.health == 70.0
        assert enemy.is_alive()
        
        enemy.take_damage(80.0)
        assert enemy.health == 0.0
        assert not enemy.is_alive()
        assert enemy.state == EnemyState.DEAD
    
    def test_enemy_progress(self):
        """Test enemy progress calculation."""
        path = [(0, 0), (100, 0), (100, 100)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            speed=50.0
        )
        
        assert enemy.get_progress() == 0.0
        
        enemy.update(1.0)  # Should be partway
        progress = enemy.get_progress()
        assert 0.0 < progress < 1.0
        
        enemy.update(10.0)  # Should reach end
        assert enemy.get_progress() == 1.0
    
    def test_fast_enemy_type(self):
        """Test VARIABLE_X enemy has faster speed."""
        path = [(0, 0), (100, 0)]
        
        normal = Enemy(
            position=Vector2(0, 0),
            path=path,
            enemy_type=EnemyType.STUDENT,
            speed=50.0
        )
        
        fast = Enemy(
            position=Vector2(0, 0),
            path=path,
            enemy_type=EnemyType.VARIABLE_X,
            speed=50.0  # Will be multiplied by 1.5
        )
        
        normal.update(1.0)
        fast.update(1.0)
        
        # Fast enemy should travel further
        assert fast.position.x > normal.position.x
    
    def test_dead_enemy_doesnt_move(self):
        """Test that dead enemies don't move."""
        path = [(0, 0), (100, 0)]
        enemy = Enemy(
            position=Vector2(0, 0),
            path=path,
            speed=50.0
        )
        
        enemy.take_damage(150.0)  # Kill the enemy
        start_pos = enemy.position.x
        
        enemy.update(1.0)
        
        # Position shouldn't change
        assert enemy.position.x == start_pos


class TestTower:
    """Tests for Tower class."""
    
    def test_tower_creation(self):
        """Test basic tower creation."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        assert tower.position.x == 50
        assert tower.position.y == 50
        assert tower.tower_type == TowerType.CALCULO
        assert tower.level == 1
    
    def test_tower_cooldown(self):
        """Test tower cooldown mechanics."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        # Initially should be able to attack
        assert tower.can_attack()
        
        # Set cooldown
        tower.cooldown = 1.0
        assert not tower.can_attack()
        
        # After update, cooldown should decrease
        tower.update(0.5)
        assert tower.cooldown == pytest.approx(0.5)
        assert not tower.can_attack()
        
        tower.update(0.5)
        assert tower.can_attack()
    
    def test_tower_find_target(self):
        """Test tower targeting system."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        path = [(0, 0), (100, 50), (200, 50)]
        
        # Create enemies at different positions
        enemy1 = Enemy(Vector2(40, 50), path, speed=10.0)
        enemy2 = Enemy(Vector2(60, 50), path, speed=10.0)
        
        # Move enemy2 further along path
        enemy2.path_index = 1.5
        
        enemies = [enemy1, enemy2]
        target = tower.find_target(enemies)
        
        # Should target enemy2 as it's further along the path
        assert target == enemy2
    
    def test_tower_ignores_dead_enemies(self):
        """Test that towers don't target dead enemies."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(50, 50), path)
        enemy.take_damage(999.0)  # Kill it
        
        target = tower.find_target([enemy])
        assert target is None
    
    def test_tower_range_check(self):
        """Test that towers only target enemies in range."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        path = [(0, 0), (1000, 1000)]
        
        # Enemy out of range
        far_enemy = Enemy(Vector2(500, 500), path)
        
        # Enemy in range
        near_enemy = Enemy(Vector2(60, 60), path)
        
        enemies = [far_enemy, near_enemy]
        target = tower.find_target(enemies)
        
        assert target == near_enemy
    
    def test_tower_attack(self):
        """Test tower attack mechanics."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        path = [(0, 0), (100, 50)]
        enemy = Enemy(Vector2(50, 50), path, health=100.0)
        
        initial_health = enemy.health
        tower.find_target([enemy])
        
        # Attack should succeed
        assert tower.attack()
        
        # Enemy should take damage
        assert enemy.health < initial_health
        
        # Tower should be on cooldown
        assert not tower.can_attack()
        
        # Shouldn't be able to attack again immediately
        assert not tower.attack()
    
    def test_tower_upgrade(self):
        """Test tower upgrade system."""
        tower = Tower(
            position=Vector2(50, 50),
            tower_type=TowerType.CALCULO
        )
        
        initial_damage = tower.damage
        initial_level = tower.level
        
        tower.upgrade()
        
        assert tower.level == initial_level + 1
        assert tower.damage > initial_damage
    
    def test_different_tower_types(self):
        """Test that different tower types have different stats."""
        decano = Tower(Vector2(0, 0), TowerType.DECANO)
        calculo = Tower(Vector2(0, 0), TowerType.CALCULO)
        fisica = Tower(Vector2(0, 0), TowerType.FISICA)
        estadistica = Tower(Vector2(0, 0), TowerType.ESTADISTICA)
        
        # Physics tower should have highest damage
        assert fisica.damage > calculo.damage
        assert fisica.damage > decano.damage
        
        # Calc tower should have good range
        assert calculo.range > decano.range


class TestEntityFactory:
    """Tests for EntityFactory class."""
    
    def test_factory_create_enemy(self):
        """Test factory enemy creation."""
        path = [(0, 0), (100, 100)]
        enemy = EntityFactory.create_enemy(
            EnemyType.STUDENT,
            path
        )
        
        assert isinstance(enemy, Enemy)
        assert enemy.enemy_type == EnemyType.STUDENT
        assert enemy.position.x == 0
        assert enemy.position.y == 0
    
    def test_factory_create_tower(self):
        """Test factory tower creation."""
        tower = EntityFactory.create_tower(
            TowerType.CALCULO,
            (50, 50)
        )
        
        assert isinstance(tower, Tower)
        assert tower.tower_type == TowerType.CALCULO
        assert tower.position.x == 50
        assert tower.position.y == 50
    
    def test_factory_invalid_path(self):
        """Test that factory validates path."""
        with pytest.raises(ValueError):
            EntityFactory.create_enemy(EnemyType.STUDENT, [])
        
        with pytest.raises(ValueError):
            EntityFactory.create_enemy(EnemyType.STUDENT, [(0, 0)])
    
    def test_factory_invalid_level(self):
        """Test that factory validates tower level."""
        with pytest.raises(ValueError):
            EntityFactory.create_tower(TowerType.CALCULO, (0, 0), level=0)
    
    def test_factory_create_wave(self):
        """Test wave creation."""
        path = [(0, 0), (100, 100)]
        
        wave1 = EntityFactory.create_wave(1, path)
        wave2 = EntityFactory.create_wave(2, path)
        
        # Wave 2 should have more enemies
        assert len(wave2) > len(wave1)
        
        # All enemies should be valid
        for enemy in wave1:
            assert isinstance(enemy, Enemy)
            assert enemy.is_alive()
    
    def test_factory_custom_stats(self):
        """Test factory with custom stats."""
        path = [(0, 0), (100, 100)]
        enemy = EntityFactory.create_enemy(
            EnemyType.STUDENT,
            path,
            speed=999.0,
            health=500.0,
            reward=100
        )
        
        assert enemy.speed == 999.0
        assert enemy.health == 500.0
        assert enemy.reward == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
