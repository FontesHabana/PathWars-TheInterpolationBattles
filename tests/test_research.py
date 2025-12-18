"""
Unit tests for Research System in PathWars - The Interpolation Battles.

Tests cover research unlocking, prerequisites, cost validation, serialization,
and integration with interpolation methods.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from core.research import (
    ResearchType,
    ResearchInfo,
    RESEARCH_INFO,
    ResearchManager,
    InsufficientFundsError,
    PrerequisiteNotMetError,
    AlreadyResearchedError
)


class TestResearchType:
    """Tests for ResearchType enum."""

    def test_research_types_exist(self):
        """Test that all expected research types exist."""
        assert hasattr(ResearchType, 'LAGRANGE_INTERPOLATION')
        assert hasattr(ResearchType, 'SPLINE_INTERPOLATION')
        assert hasattr(ResearchType, 'TANGENT_CONTROL')

    def test_research_types_are_unique(self):
        """Test that all research types have unique values."""
        types = [rt for rt in ResearchType]
        values = [rt.value for rt in types]
        assert len(values) == len(set(values))


class TestResearchInfo:
    """Tests for ResearchInfo dataclass and RESEARCH_INFO dictionary."""

    def test_all_research_have_info(self):
        """Test that all research types have corresponding info."""
        for rt in ResearchType:
            assert rt in RESEARCH_INFO

    def test_lagrange_info(self):
        """Test Lagrange research info."""
        info = RESEARCH_INFO[ResearchType.LAGRANGE_INTERPOLATION]
        assert info.cost == 500
        assert info.display_name == "Lagrange Polynomial"
        assert len(info.prerequisites) == 0

    def test_spline_info(self):
        """Test Spline research info."""
        info = RESEARCH_INFO[ResearchType.SPLINE_INTERPOLATION]
        assert info.cost == 1000
        assert info.display_name == "Cubic Spline"
        assert ResearchType.LAGRANGE_INTERPOLATION in info.prerequisites

    def test_tangent_control_info(self):
        """Test Tangent Control research info."""
        info = RESEARCH_INFO[ResearchType.TANGENT_CONTROL]
        assert info.cost == 750
        assert info.display_name == "Tangent Control"
        assert len(info.prerequisites) == 0

    def test_research_info_immutable(self):
        """Test that ResearchInfo is immutable (frozen)."""
        info = RESEARCH_INFO[ResearchType.LAGRANGE_INTERPOLATION]
        with pytest.raises(AttributeError):  # dataclasses.FrozenInstanceError is a subclass of AttributeError
            info.cost = 999


class TestResearchManagerInitialization:
    """Tests for ResearchManager initialization."""

    def test_manager_initialization(self):
        """Test basic ResearchManager initialization."""
        manager = ResearchManager("player1")
        assert manager.player_id == "player1"
        assert len(manager.unlocked_research) == 0

    def test_unlocked_research_returns_copy(self):
        """Test that unlocked_research returns a copy, not the internal set."""
        manager = ResearchManager("player1")
        unlocked = manager.unlocked_research
        unlocked.add(ResearchType.LAGRANGE_INTERPOLATION)
        assert len(manager.unlocked_research) == 0  # Should still be empty


class TestBasicUnlocking:
    """Tests for basic research unlocking."""

    def test_unlock_lagrange_success(self):
        """Test unlocking Lagrange interpolation."""
        manager = ResearchManager("player1")
        cost = manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        assert cost == 500
        assert manager.is_unlocked(ResearchType.LAGRANGE_INTERPOLATION)

    def test_unlock_tangent_control_success(self):
        """Test unlocking Tangent Control."""
        manager = ResearchManager("player1")
        cost = manager.unlock(ResearchType.TANGENT_CONTROL, 800)
        assert cost == 750
        assert manager.is_unlocked(ResearchType.TANGENT_CONTROL)

    def test_get_cost(self):
        """Test getting cost of research."""
        manager = ResearchManager("player1")
        assert manager.get_cost(ResearchType.LAGRANGE_INTERPOLATION) == 500
        assert manager.get_cost(ResearchType.SPLINE_INTERPOLATION) == 1000
        assert manager.get_cost(ResearchType.TANGENT_CONTROL) == 750


class TestInsufficientFunds:
    """Tests for insufficient funds errors."""

    def test_insufficient_funds_for_lagrange(self):
        """Test insufficient funds error for Lagrange."""
        manager = ResearchManager("player1")
        with pytest.raises(InsufficientFundsError) as exc_info:
            manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 400)
        assert "500" in str(exc_info.value)
        assert "400" in str(exc_info.value)

    def test_insufficient_funds_for_spline(self):
        """Test insufficient funds error for Spline."""
        manager = ResearchManager("player1")
        # First unlock Lagrange
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 500)
        
        with pytest.raises(InsufficientFundsError):
            manager.unlock(ResearchType.SPLINE_INTERPOLATION, 500)


class TestPrerequisites:
    """Tests for prerequisite validation."""

    def test_cannot_unlock_spline_without_lagrange(self):
        """Test that Spline requires Lagrange."""
        manager = ResearchManager("player1")
        with pytest.raises(PrerequisiteNotMetError) as exc_info:
            manager.unlock(ResearchType.SPLINE_INTERPOLATION, 2000)
        assert "Lagrange" in str(exc_info.value)

    def test_can_unlock_spline_after_lagrange(self):
        """Test that Spline can be unlocked after Lagrange."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 2000)
        cost = manager.unlock(ResearchType.SPLINE_INTERPOLATION, 1500)
        assert cost == 1000
        assert manager.is_unlocked(ResearchType.SPLINE_INTERPOLATION)

    def test_tangent_control_has_no_prerequisites(self):
        """Test that Tangent Control can be unlocked immediately."""
        manager = ResearchManager("player1")
        cost = manager.unlock(ResearchType.TANGENT_CONTROL, 800)
        assert cost == 750
        assert manager.is_unlocked(ResearchType.TANGENT_CONTROL)


class TestAlreadyResearched:
    """Tests for already researched errors."""

    def test_cannot_research_twice(self):
        """Test that research cannot be unlocked twice."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        
        with pytest.raises(AlreadyResearchedError) as exc_info:
            manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        assert "LAGRANGE_INTERPOLATION" in str(exc_info.value)


class TestCanUnlock:
    """Tests for can_unlock method."""

    def test_can_unlock_when_prerequisites_met(self):
        """Test can_unlock returns True when prerequisites are met."""
        manager = ResearchManager("player1")
        assert manager.can_unlock(ResearchType.LAGRANGE_INTERPOLATION) is True
        assert manager.can_unlock(ResearchType.TANGENT_CONTROL) is True
        assert manager.can_unlock(ResearchType.SPLINE_INTERPOLATION) is False

    def test_can_unlock_after_prerequisite_unlocked(self):
        """Test can_unlock updates after unlocking prerequisites."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        assert manager.can_unlock(ResearchType.SPLINE_INTERPOLATION) is True

    def test_cannot_unlock_already_unlocked(self):
        """Test can_unlock returns False for already unlocked research."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        assert manager.can_unlock(ResearchType.LAGRANGE_INTERPOLATION) is False


class TestGetAvailableResearch:
    """Tests for get_available_research method."""

    def test_initially_available_research(self):
        """Test initially available research."""
        manager = ResearchManager("player1")
        available = manager.get_available_research()
        assert ResearchType.LAGRANGE_INTERPOLATION in available
        assert ResearchType.TANGENT_CONTROL in available
        assert ResearchType.SPLINE_INTERPOLATION not in available

    def test_available_research_after_unlock(self):
        """Test available research updates after unlock."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        
        available = manager.get_available_research()
        assert ResearchType.LAGRANGE_INTERPOLATION not in available
        assert ResearchType.SPLINE_INTERPOLATION in available
        assert ResearchType.TANGENT_CONTROL in available

    def test_no_available_research_when_all_unlocked(self):
        """Test no available research when all are unlocked."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 2000)
        manager.unlock(ResearchType.SPLINE_INTERPOLATION, 1500)
        manager.unlock(ResearchType.TANGENT_CONTROL, 750)
        
        available = manager.get_available_research()
        assert len(available) == 0


class TestGetInterpolationMethods:
    """Tests for get_interpolation_methods method."""

    def test_linear_always_available(self):
        """Test that linear is always available."""
        manager = ResearchManager("player1")
        methods = manager.get_interpolation_methods()
        assert 'linear' in methods

    def test_lagrange_after_unlock(self):
        """Test lagrange available after unlock."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        methods = manager.get_interpolation_methods()
        assert 'linear' in methods
        assert 'lagrange' in methods
        assert 'spline' not in methods

    def test_spline_after_unlock(self):
        """Test spline available after unlock."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 2000)
        manager.unlock(ResearchType.SPLINE_INTERPOLATION, 1500)
        methods = manager.get_interpolation_methods()
        assert 'linear' in methods
        assert 'lagrange' in methods
        assert 'spline' in methods

    def test_tangent_control_not_in_methods(self):
        """Test that tangent control doesn't add interpolation methods."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.TANGENT_CONTROL, 1000)
        methods = manager.get_interpolation_methods()
        assert methods == {'linear'}  # Only linear


class TestReset:
    """Tests for reset method."""

    def test_reset_clears_all_research(self):
        """Test that reset clears all unlocked research."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 2000)
        manager.unlock(ResearchType.TANGENT_CONTROL, 1000)
        
        manager.reset()
        
        assert len(manager.unlocked_research) == 0
        assert not manager.is_unlocked(ResearchType.LAGRANGE_INTERPOLATION)
        assert not manager.is_unlocked(ResearchType.TANGENT_CONTROL)


class TestSerialization:
    """Tests for serialization and deserialization."""

    def test_to_dict_empty(self):
        """Test serialization with no research."""
        manager = ResearchManager("player1")
        data = manager.to_dict()
        assert data['player_id'] == "player1"
        assert data['unlocked'] == []

    def test_to_dict_with_research(self):
        """Test serialization with unlocked research."""
        manager = ResearchManager("player1")
        manager.unlock(ResearchType.LAGRANGE_INTERPOLATION, 1000)
        manager.unlock(ResearchType.TANGENT_CONTROL, 800)
        
        data = manager.to_dict()
        assert data['player_id'] == "player1"
        assert 'LAGRANGE_INTERPOLATION' in data['unlocked']
        assert 'TANGENT_CONTROL' in data['unlocked']

    def test_from_dict_empty(self):
        """Test deserialization with no research."""
        data = {'player_id': 'player2', 'unlocked': []}
        manager = ResearchManager.from_dict(data)
        
        assert manager.player_id == 'player2'
        assert len(manager.unlocked_research) == 0

    def test_from_dict_with_research(self):
        """Test deserialization with unlocked research."""
        data = {
            'player_id': 'player2',
            'unlocked': ['LAGRANGE_INTERPOLATION', 'TANGENT_CONTROL']
        }
        manager = ResearchManager.from_dict(data)
        
        assert manager.player_id == 'player2'
        assert manager.is_unlocked(ResearchType.LAGRANGE_INTERPOLATION)
        assert manager.is_unlocked(ResearchType.TANGENT_CONTROL)
        assert not manager.is_unlocked(ResearchType.SPLINE_INTERPOLATION)

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization are inverses."""
        manager1 = ResearchManager("player3")
        manager1.unlock(ResearchType.LAGRANGE_INTERPOLATION, 2000)
        manager1.unlock(ResearchType.SPLINE_INTERPOLATION, 1500)
        
        data = manager1.to_dict()
        manager2 = ResearchManager.from_dict(data)
        
        assert manager1.player_id == manager2.player_id
        assert manager1.unlocked_research == manager2.unlocked_research

    def test_from_dict_ignores_unknown_research(self):
        """Test that deserialization ignores unknown research types."""
        data = {
            'player_id': 'player4',
            'unlocked': ['LAGRANGE_INTERPOLATION', 'UNKNOWN_RESEARCH', 'TANGENT_CONTROL']
        }
        manager = ResearchManager.from_dict(data)
        
        # Should only have the valid research types
        assert len(manager.unlocked_research) == 2
        assert manager.is_unlocked(ResearchType.LAGRANGE_INTERPOLATION)
        assert manager.is_unlocked(ResearchType.TANGENT_CONTROL)
