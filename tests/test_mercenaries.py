"""
Unit tests for mercenary system in PathWars - The Interpolation Battles.

Tests cover mercenary creation, stats, factory pattern, damage, movement,
and purchase validation.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from entities.mercenaries import (
    BaseMercenary,
    MercenaryStats,
    MercenaryType,
    ReinforcedStudent,
    SpeedyVariableX,
    TankConstantPi,
    MercenaryFactory,
)


class TestMercenaryStats:
    """Tests for the MercenaryStats class."""

    def test_stats_creation(self):
        """Test creating mercenary stats."""
        stats = MercenaryStats(
            base_hp=100,
            base_speed=1.0,
            cost=100,
            display_name="Test Mercenary"
        )
        assert stats.base_hp == 100
        assert stats.base_speed == 1.0
        assert stats.cost == 100
        assert stats.display_name == "Test Mercenary"

    def test_get_modified_hp_default(self):
        """Test HP calculation with default modifier."""
        stats = MercenaryStats(
            base_hp=100,
            base_speed=1.0,
            cost=100,
            display_name="Test"
        )
        assert stats.get_modified_hp() == 100

    def test_get_modified_hp_with_modifier(self):
        """Test HP calculation with custom modifier."""
        stats = MercenaryStats(
            base_hp=100,
            base_speed=1.0,
            cost=100,
            display_name="Test"
        )
        assert stats.get_modified_hp(1.5) == 150
        assert stats.get_modified_hp(0.7) == 70
        assert stats.get_modified_hp(3.0) == 300

    def test_get_modified_speed_default(self):
        """Test speed calculation with default modifier."""
        stats = MercenaryStats(
            base_hp=100,
            base_speed=1.0,
            cost=100,
            display_name="Test"
        )
        assert stats.get_modified_speed() == 1.0

    def test_get_modified_speed_with_modifier(self):
        """Test speed calculation with custom modifier."""
        stats = MercenaryStats(
            base_hp=100,
            base_speed=1.0,
            cost=100,
            display_name="Test"
        )
        assert stats.get_modified_speed(2.0) == 2.0
        assert stats.get_modified_speed(0.5) == 0.5


class TestReinforcedStudent:
    """Tests for the ReinforcedStudent mercenary."""

    def test_creation(self):
        """Test creating a Reinforced Student."""
        merc = ReinforcedStudent("player1", "player2")
        assert merc.owner_player_id == "player1"
        assert merc.target_player_id == "player2"
        assert merc.is_alive is True

    def test_stats(self):
        """Test Reinforced Student stats."""
        merc = ReinforcedStudent("player1", "player2")
        assert merc.stats.base_hp == 100
        assert merc.stats.base_speed == 1.0
        assert merc.stats.cost == 100
        assert merc.stats.display_name == "Reinforced Student"

    def test_modifiers(self):
        """Test Reinforced Student modifiers (+50% HP, normal speed)."""
        merc = ReinforcedStudent("player1", "player2")
        assert merc.hp_modifier == 1.5
        assert merc.speed_modifier == 1.0
        assert merc.hp == 150  # 100 * 1.5
        assert merc.speed == 1.0  # 1.0 * 1.0


class TestSpeedyVariableX:
    """Tests for the SpeedyVariableX mercenary."""

    def test_creation(self):
        """Test creating a Speedy Variable X."""
        merc = SpeedyVariableX("player1", "player2")
        assert merc.owner_player_id == "player1"
        assert merc.target_player_id == "player2"
        assert merc.is_alive is True

    def test_stats(self):
        """Test Speedy Variable X stats."""
        merc = SpeedyVariableX("player1", "player2")
        assert merc.stats.base_hp == 100
        assert merc.stats.base_speed == 1.0
        assert merc.stats.cost == 75
        assert merc.stats.display_name == "Speedy Variable X"

    def test_modifiers(self):
        """Test Speedy Variable X modifiers (-30% HP, +100% speed)."""
        merc = SpeedyVariableX("player1", "player2")
        assert merc.hp_modifier == 0.7
        assert merc.speed_modifier == 2.0
        assert merc.hp == 70  # 100 * 0.7
        assert merc.speed == 2.0  # 1.0 * 2.0


class TestTankConstantPi:
    """Tests for the TankConstantPi mercenary."""

    def test_creation(self):
        """Test creating a Tank Constant Pi."""
        merc = TankConstantPi("player1", "player2")
        assert merc.owner_player_id == "player1"
        assert merc.target_player_id == "player2"
        assert merc.is_alive is True

    def test_stats(self):
        """Test Tank Constant Pi stats."""
        merc = TankConstantPi("player1", "player2")
        assert merc.stats.base_hp == 100
        assert merc.stats.base_speed == 1.0
        assert merc.stats.cost == 200
        assert merc.stats.display_name == "Tank Constant Pi"

    def test_modifiers(self):
        """Test Tank Constant Pi modifiers (+200% HP, -50% speed)."""
        merc = TankConstantPi("player1", "player2")
        assert merc.hp_modifier == 3.0
        assert merc.speed_modifier == 0.5
        assert merc.hp == 300  # 100 * 3.0
        assert merc.speed == 0.5  # 1.0 * 0.5


class TestMercenaryDamage:
    """Tests for mercenary damage mechanics."""

    def test_take_damage(self):
        """Test mercenary can take damage."""
        merc = ReinforcedStudent("player1", "player2")
        initial_hp = merc.hp
        merc.take_damage(30)
        assert merc.hp == initial_hp - 30
        assert merc.is_alive is True

    def test_death_on_zero_health(self):
        """Test mercenary dies when health reaches zero."""
        merc = ReinforcedStudent("player1", "player2")
        merc.take_damage(150)
        assert merc.hp == 0
        assert merc.is_alive is False

    def test_health_cannot_go_negative(self):
        """Test health is clamped at zero."""
        merc = ReinforcedStudent("player1", "player2")
        merc.take_damage(300)
        assert merc.hp == 0
        assert merc.is_alive is False


class TestMercenaryMovement:
    """Tests for mercenary movement mechanics."""

    def test_initial_position(self):
        """Test mercenary starts at origin."""
        merc = ReinforcedStudent("player1", "player2")
        assert merc.position == (0.0, 0.0)

    def test_set_position(self):
        """Test setting absolute position."""
        merc = ReinforcedStudent("player1", "player2")
        merc.set_position(5.0, 10.0)
        assert merc.position == (5.0, 10.0)

    def test_move_by_delta(self):
        """Test moving by delta."""
        merc = ReinforcedStudent("player1", "player2")
        merc.set_position(5.0, 5.0)
        merc.move(2.0, 3.0)
        assert merc.position == (7.0, 8.0)

    def test_move_multiple_times(self):
        """Test multiple movements accumulate."""
        merc = ReinforcedStudent("player1", "player2")
        merc.move(1.0, 1.0)
        merc.move(2.0, 2.0)
        merc.move(3.0, 3.0)
        assert merc.position == (6.0, 6.0)


class TestMercenaryFactory:
    """Tests for the MercenaryFactory class."""

    def test_create_reinforced_student(self):
        """Test factory creates Reinforced Student correctly."""
        merc = MercenaryFactory.create_mercenary(
            MercenaryType.REINFORCED_STUDENT,
            "player1",
            "player2"
        )
        assert isinstance(merc, ReinforcedStudent)
        assert merc.owner_player_id == "player1"
        assert merc.target_player_id == "player2"

    def test_create_speedy_variable_x(self):
        """Test factory creates Speedy Variable X correctly."""
        merc = MercenaryFactory.create_mercenary(
            MercenaryType.SPEEDY_VARIABLE_X,
            "player1",
            "player2"
        )
        assert isinstance(merc, SpeedyVariableX)
        assert merc.hp == 70
        assert merc.speed == 2.0

    def test_create_tank_constant_pi(self):
        """Test factory creates Tank Constant Pi correctly."""
        merc = MercenaryFactory.create_mercenary(
            MercenaryType.TANK_CONSTANT_PI,
            "player1",
            "player2"
        )
        assert isinstance(merc, TankConstantPi)
        assert merc.hp == 300
        assert merc.speed == 0.5

    def test_get_cost_reinforced_student(self):
        """Test getting cost of Reinforced Student."""
        cost = MercenaryFactory.get_cost(MercenaryType.REINFORCED_STUDENT)
        assert cost == 100

    def test_get_cost_speedy_variable_x(self):
        """Test getting cost of Speedy Variable X."""
        cost = MercenaryFactory.get_cost(MercenaryType.SPEEDY_VARIABLE_X)
        assert cost == 75

    def test_get_cost_tank_constant_pi(self):
        """Test getting cost of Tank Constant Pi."""
        cost = MercenaryFactory.get_cost(MercenaryType.TANK_CONSTANT_PI)
        assert cost == 200

    def test_get_available_types(self):
        """Test getting list of available mercenary types."""
        types = MercenaryFactory.get_available_types()
        assert len(types) == 3
        assert MercenaryType.REINFORCED_STUDENT in types
        assert MercenaryType.SPEEDY_VARIABLE_X in types
        assert MercenaryType.TANK_CONSTANT_PI in types

    def test_validate_purchase_can_afford(self):
        """Test purchase validation when player can afford."""
        can_buy = MercenaryFactory.validate_purchase(
            MercenaryType.REINFORCED_STUDENT,
            quantity=2,
            available_money=300
        )
        assert can_buy is True

    def test_validate_purchase_cannot_afford(self):
        """Test purchase validation when player cannot afford."""
        can_buy = MercenaryFactory.validate_purchase(
            MercenaryType.TANK_CONSTANT_PI,
            quantity=3,
            available_money=500
        )
        assert can_buy is False

    def test_validate_purchase_exact_amount(self):
        """Test purchase validation with exact amount."""
        can_buy = MercenaryFactory.validate_purchase(
            MercenaryType.SPEEDY_VARIABLE_X,
            quantity=4,
            available_money=300
        )
        assert can_buy is True

    def test_validate_purchase_invalid_quantity(self):
        """Test purchase validation raises error for invalid quantity."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            MercenaryFactory.validate_purchase(
                MercenaryType.REINFORCED_STUDENT,
                quantity=0,
                available_money=1000
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
