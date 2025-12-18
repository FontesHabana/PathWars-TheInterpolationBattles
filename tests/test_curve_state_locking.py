"""
Tests for CurveState locking mechanism and initialization.

Tests locking/unlocking functionality, default point initialization,
and minimum point enforcement.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.curve_state import CurveState, CurveLockedError


class TestCurveStateInitialization:
    """Tests for CurveState initialization with default points."""

    def test_initialize_default_points_creates_two_points(self):
        """Test that initialize_default_points creates exactly 2 points."""
        state = CurveState()
        state.initialize_default_points()
        
        assert state.get_point_count() == 2

    def test_initialize_default_points_start_and_end_positions(self):
        """Test that default points are at correct positions."""
        state = CurveState()
        state.initialize_default_points()
        
        points = state.control_points
        assert points[0] == (0.0, 10.0)
        assert points[1] == (19.0, 10.0)

    def test_initialize_default_points_clears_existing(self):
        """Test that initialize_default_points clears existing points."""
        state = CurveState()
        state.add_point(5.0, 5.0)
        state.add_point(10.0, 10.0)
        state.add_point(15.0, 15.0)
        
        state.initialize_default_points()
        
        assert state.get_point_count() == 2
        assert state.control_points[0] == (0.0, 10.0)
        assert state.control_points[1] == (19.0, 10.0)

    def test_initialize_default_points_unlocks_curve(self):
        """Test that initialize_default_points unlocks the curve."""
        state = CurveState()
        state.lock()
        
        state.initialize_default_points()
        
        assert state.locked is False

    def test_initialize_default_points_custom_values(self):
        """Test initialize_default_points with custom values."""
        state = CurveState()
        state.initialize_default_points(start_x=2.0, end_x=18.0, y=5.0)
        
        points = state.control_points
        assert len(points) == 2
        assert points[0] == (2.0, 5.0)
        assert points[1] == (18.0, 5.0)


class TestCurveStateLocking:
    """Tests for CurveState locking mechanism."""

    def test_initial_state_is_unlocked(self):
        """Test that curve starts unlocked."""
        state = CurveState()
        assert state.locked is False

    def test_lock_sets_locked_true(self):
        """Test that lock() sets locked to True."""
        state = CurveState()
        state.lock()
        assert state.locked is True

    def test_unlock_sets_locked_false(self):
        """Test that unlock() sets locked to False."""
        state = CurveState()
        state.lock()
        state.unlock()
        assert state.locked is False

    def test_add_point_raises_when_locked(self):
        """Test that add_point raises CurveLockedError when locked."""
        state = CurveState()
        state.lock()
        
        with pytest.raises(CurveLockedError) as exc_info:
            state.add_point(10.0, 10.0)
        
        assert "locked" in str(exc_info.value).lower()

    def test_remove_point_raises_when_locked(self):
        """Test that remove_point raises CurveLockedError when locked."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 5.0)
        state.add_point(10.0, 10.0)
        state.lock()
        
        with pytest.raises(CurveLockedError) as exc_info:
            state.remove_point(0)
        
        assert "locked" in str(exc_info.value).lower()

    def test_move_point_raises_when_locked(self):
        """Test that move_point raises CurveLockedError when locked."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        state.lock()
        
        with pytest.raises(CurveLockedError) as exc_info:
            state.move_point(0, 20.0, 20.0)
        
        assert "locked" in str(exc_info.value).lower()

    def test_clear_points_raises_when_locked(self):
        """Test that clear_points raises CurveLockedError when locked."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        state.lock()
        
        with pytest.raises(CurveLockedError) as exc_info:
            state.clear_points()
        
        assert "locked" in str(exc_info.value).lower()

    def test_set_method_allowed_when_locked(self):
        """Test that set_method works even when locked."""
        state = CurveState()
        state.lock()
        
        result = state.set_method('lagrange')
        
        assert result is True
        assert state.interpolation_method == 'lagrange'

    def test_get_interpolated_path_allowed_when_locked(self):
        """Test that get_interpolated_path works when locked."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.lock()
        
        path = state.get_interpolated_path(resolution=50)
        
        assert len(path) == 50


class TestCurveStateMinimumPoints:
    """Tests for minimum point enforcement."""

    def test_cannot_remove_below_two_points(self):
        """Test that cannot remove points when only 2 remain."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        
        result = state.remove_point(0)
        
        assert result is False
        assert state.get_point_count() == 2

    def test_can_remove_when_more_than_two_points(self):
        """Test that can remove points when more than 2 exist."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 5.0)
        state.add_point(10.0, 10.0)
        
        result = state.remove_point(1)
        
        assert result is True
        assert state.get_point_count() == 2

    def test_remove_stops_at_two_points(self):
        """Test that cannot remove past 2 points."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 5.0)
        state.add_point(10.0, 10.0)
        
        # Remove one point successfully
        state.remove_point(1)
        assert state.get_point_count() == 2
        
        # Try to remove another - should fail
        result = state.remove_point(0)
        assert result is False
        assert state.get_point_count() == 2


class TestCurveLockedError:
    """Tests for CurveLockedError exception."""

    def test_error_message_is_descriptive(self):
        """Test that error message is descriptive."""
        state = CurveState()
        state.lock()
        
        with pytest.raises(CurveLockedError) as exc_info:
            state.add_point(10.0, 10.0)
        
        message = str(exc_info.value)
        assert len(message) > 0
        assert "locked" in message.lower()

    def test_error_is_catchable(self):
        """Test that CurveLockedError can be caught and handled."""
        state = CurveState()
        state.lock()
        
        error_caught = False
        try:
            state.add_point(10.0, 10.0)
        except CurveLockedError:
            error_caught = True
        
        assert error_caught is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
