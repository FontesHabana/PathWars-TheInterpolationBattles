"""
Unit tests for tower upgrade system in PathWars - The Interpolation Battles.

Tests cover tower levels, upgrade costs, upgrade mechanics, and stat improvements.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from entities.base import Vector2
from entities.tower import Tower, TowerType, TowerLevel, TowerUpgradeError


class TestTowerLevel:
    """Tests for TowerLevel enum."""

    def test_mastery_is_level_1(self):
        """Test MASTERY level is 1."""
        assert TowerLevel.MASTERY.value == 1

    def test_doctorate_is_level_2(self):
        """Test DOCTORATE level is 2."""
        assert TowerLevel.DOCTORATE.value == 2


class TestTowerInitialization:
    """Tests for tower initialization with levels."""

    def test_default_level_is_mastery(self):
        """Test towers default to MASTERY level."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert tower.level == TowerLevel.MASTERY

    def test_can_create_at_doctorate_level(self):
        """Test creating tower directly at DOCTORATE level."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.CALCULUS,
            level=TowerLevel.DOCTORATE
        )
        assert tower.level == TowerLevel.DOCTORATE

    def test_doctorate_has_upgraded_stats(self):
        """Test DOCTORATE tower has upgraded stats."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.CALCULUS,
            level=TowerLevel.DOCTORATE
        )
        # CALCULUS base damage is 25, upgraded should be 25 * 1.5 = 37
        assert tower.damage == 37
        # CALCULUS base range is 5.0, upgraded should be 5.0 * 1.25 = 6.25
        assert pytest.approx(tower.attack_range, abs=0.01) == 6.25
        # CALCULUS base cooldown is 0.5, upgraded should be 0.5 * 0.8 = 0.4
        assert pytest.approx(tower.cooldown, abs=0.01) == 0.4


class TestTowerUpgradeCost:
    """Tests for tower upgrade costs."""

    def test_dean_upgrade_cost(self):
        """Test DEAN upgrade cost is 75."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert tower.upgrade_cost == 75

    def test_calculus_upgrade_cost(self):
        """Test CALCULUS upgrade cost is 100."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        assert tower.upgrade_cost == 100

    def test_physics_upgrade_cost(self):
        """Test PHYSICS upgrade cost is 150."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)
        assert tower.upgrade_cost == 150

    def test_statistics_upgrade_cost(self):
        """Test STATISTICS upgrade cost is 90."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.STATISTICS)
        assert tower.upgrade_cost == 90

    def test_doctorate_upgrade_cost_is_zero(self):
        """Test DOCTORATE towers have 0 upgrade cost."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.DEAN,
            level=TowerLevel.DOCTORATE
        )
        assert tower.upgrade_cost == 0


class TestTowerCanUpgrade:
    """Tests for can_upgrade property."""

    def test_mastery_can_upgrade(self):
        """Test MASTERY towers can upgrade."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert tower.can_upgrade is True

    def test_doctorate_cannot_upgrade(self):
        """Test DOCTORATE towers cannot upgrade."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.DEAN,
            level=TowerLevel.DOCTORATE
        )
        assert tower.can_upgrade is False


class TestTowerUpgrade:
    """Tests for tower upgrade mechanics."""

    def test_upgrade_changes_level(self):
        """Test upgrading changes level from MASTERY to DOCTORATE."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert tower.level == TowerLevel.MASTERY
        result = tower.upgrade()
        assert result is True
        assert tower.level == TowerLevel.DOCTORATE

    def test_upgrade_increases_damage(self):
        """Test upgrade increases damage by 1.5x."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        base_damage = tower.damage
        assert base_damage == 25
        tower.upgrade()
        assert tower.damage == 37  # 25 * 1.5 = 37.5, rounded to 37

    def test_upgrade_increases_range(self):
        """Test upgrade increases range by 1.25x."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        base_range = tower.attack_range
        assert base_range == 5.0
        tower.upgrade()
        assert pytest.approx(tower.attack_range, abs=0.01) == 6.25

    def test_upgrade_decreases_cooldown(self):
        """Test upgrade decreases cooldown by 0.8x (20% faster)."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        base_cooldown = tower.cooldown
        assert base_cooldown == 0.5
        tower.upgrade()
        assert pytest.approx(tower.cooldown, abs=0.01) == 0.4

    def test_upgrade_increases_stun_duration(self):
        """Test upgrade increases stun duration for DEAN by 1.5x."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        base_stun = tower.stun_duration
        assert base_stun == 1.0
        tower.upgrade()
        assert pytest.approx(tower.stun_duration, abs=0.01) == 1.5

    def test_upgrade_increases_splash_radius(self):
        """Test upgrade increases splash radius for PHYSICS by 1.3x."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.PHYSICS)
        base_splash = tower.splash_radius
        assert base_splash == 2.0
        tower.upgrade()
        assert pytest.approx(tower.splash_radius, abs=0.01) == 2.6

    def test_upgrade_increases_slow_amount(self):
        """Test upgrade increases slow amount for STATISTICS by 1.25x, capped at 1.0."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.STATISTICS)
        base_slow = tower.slow_amount
        assert base_slow == 0.5
        tower.upgrade()
        # 0.5 * 1.25 = 0.625, not capped
        assert pytest.approx(tower.slow_amount, abs=0.01) == 0.625

    def test_upgrade_returns_false_if_already_max(self):
        """Test upgrade returns False if already at DOCTORATE."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.DEAN,
            level=TowerLevel.DOCTORATE
        )
        result = tower.upgrade()
        assert result is False

    def test_cannot_upgrade_twice(self):
        """Test tower cannot be upgraded twice."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        first_result = tower.upgrade()
        assert first_result is True
        second_result = tower.upgrade()
        assert second_result is False
        assert tower.level == TowerLevel.DOCTORATE


class TestTowerUpgradePreview:
    """Tests for upgrade preview functionality."""

    def test_preview_shows_damage_increase(self):
        """Test preview shows correct damage increase."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        preview = tower.get_upgrade_preview()
        assert preview["current"]["damage"] == 25
        assert preview["upgraded"]["damage"] == 37

    def test_preview_shows_range_increase(self):
        """Test preview shows correct range increase."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        preview = tower.get_upgrade_preview()
        assert pytest.approx(preview["current"]["attack_range"], abs=0.01) == 5.0
        assert pytest.approx(preview["upgraded"]["attack_range"], abs=0.01) == 6.25

    def test_preview_shows_cooldown_decrease(self):
        """Test preview shows correct cooldown decrease."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.CALCULUS)
        preview = tower.get_upgrade_preview()
        assert pytest.approx(preview["current"]["cooldown"], abs=0.01) == 0.5
        assert pytest.approx(preview["upgraded"]["cooldown"], abs=0.01) == 0.4

    def test_preview_empty_if_already_max(self):
        """Test preview returns empty dict if already at DOCTORATE."""
        tower = Tower(
            Vector2(5.0, 5.0),
            TowerType.DEAN,
            level=TowerLevel.DOCTORATE
        )
        preview = tower.get_upgrade_preview()
        assert preview == {}


class TestTowerId:
    """Tests for tower unique ID."""

    def test_tower_has_unique_id(self):
        """Test each tower gets a unique ID."""
        tower1 = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        tower2 = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert tower1.id != tower2.id

    def test_id_is_string(self):
        """Test tower ID is a string."""
        tower = Tower(Vector2(5.0, 5.0), TowerType.DEAN)
        assert isinstance(tower.id, str)


class TestTowerUpgradeAllTypes:
    """Tests for upgrading all tower types."""

    @pytest.mark.parametrize("tower_type", [
        TowerType.DEAN,
        TowerType.CALCULUS,
        TowerType.PHYSICS,
        TowerType.STATISTICS,
    ])
    def test_all_types_can_upgrade(self, tower_type):
        """Test all tower types can be upgraded."""
        tower = Tower(Vector2(5.0, 5.0), tower_type)
        assert tower.can_upgrade is True
        result = tower.upgrade()
        assert result is True
        assert tower.level == TowerLevel.DOCTORATE

    @pytest.mark.parametrize("tower_type,expected_cost", [
        (TowerType.DEAN, 75),
        (TowerType.CALCULUS, 100),
        (TowerType.PHYSICS, 150),
        (TowerType.STATISTICS, 90),
    ])
    def test_all_types_have_upgrade_cost(self, tower_type, expected_cost):
        """Test all tower types have correct upgrade costs."""
        tower = Tower(Vector2(5.0, 5.0), tower_type)
        assert tower.upgrade_cost == expected_cost


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
