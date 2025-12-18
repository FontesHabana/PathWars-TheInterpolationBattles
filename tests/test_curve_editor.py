"""
Tests for the Curve Editor module.

Tests CurveState add/remove/move points, path generation,
and different interpolation methods.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from core.curve_state import CurveState


class TestCurveStateInitialization:
    """Tests for CurveState initialization."""

    def test_initial_state(self):
        """Test that CurveState initializes with empty points and linear method."""
        state = CurveState()
        assert state.control_points == []
        assert state.interpolation_method == 'linear'

    def test_get_point_count_empty(self):
        """Test point count for empty state."""
        state = CurveState()
        assert state.get_point_count() == 0


class TestCurveStateAddPoint:
    """Tests for adding control points."""

    def test_add_single_point(self):
        """Test adding a single control point."""
        state = CurveState()
        state.add_point(10.0, 20.0)
        assert state.get_point_count() == 1
        assert state.control_points[0] == (10.0, 20.0)

    def test_add_multiple_points(self):
        """Test adding multiple control points."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.add_point(20.0, 5.0)
        
        assert state.get_point_count() == 3
        assert state.control_points == [(0.0, 0.0), (10.0, 10.0), (20.0, 5.0)]

    def test_control_points_returns_copy(self):
        """Test that control_points property returns a copy."""
        state = CurveState()
        state.add_point(10.0, 20.0)
        
        points = state.control_points
        points.append((30.0, 40.0))
        
        # Original should not be modified
        assert state.get_point_count() == 1


class TestCurveStateRemovePoint:
    """Tests for removing control points."""

    def test_remove_point_valid_index(self):
        """Test removing a point at a valid index."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.add_point(20.0, 20.0)
        
        result = state.remove_point(1)
        
        assert result is True
        assert state.get_point_count() == 2
        assert state.control_points == [(0.0, 0.0), (20.0, 20.0)]

    def test_remove_point_first_index(self):
        """Test removing the first point when more than 2 points exist."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.add_point(20.0, 20.0)
        
        result = state.remove_point(0)
        
        assert result is True
        assert state.control_points == [(10.0, 10.0), (20.0, 20.0)]

    def test_remove_point_last_index(self):
        """Test removing the last point when more than 2 points exist."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.add_point(20.0, 20.0)
        
        result = state.remove_point(2)
        
        assert result is True
        assert state.control_points == [(0.0, 0.0), (10.0, 10.0)]

    def test_remove_point_invalid_index_negative(self):
        """Test removing a point at a negative index."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        
        result = state.remove_point(-1)
        
        assert result is False
        assert state.get_point_count() == 1

    def test_remove_point_invalid_index_out_of_bounds(self):
        """Test removing a point at an out-of-bounds index."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        
        result = state.remove_point(5)
        
        assert result is False
        assert state.get_point_count() == 1

    def test_remove_point_empty_state(self):
        """Test removing a point from empty state."""
        state = CurveState()
        
        result = state.remove_point(0)
        
        assert result is False


class TestCurveStateMovePoint:
    """Tests for moving control points."""

    def test_move_point_valid_index(self):
        """Test moving a point at a valid index."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        
        result = state.move_point(0, 5.0, 5.0)
        
        assert result is True
        assert state.control_points[0] == (5.0, 5.0)

    def test_move_point_invalid_index(self):
        """Test moving a point at an invalid index."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        
        result = state.move_point(5, 20.0, 20.0)
        
        assert result is False
        assert state.control_points[0] == (10.0, 10.0)

    def test_move_point_negative_index(self):
        """Test moving a point at a negative index."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        
        result = state.move_point(-1, 20.0, 20.0)
        
        assert result is False


class TestCurveStateSetMethod:
    """Tests for setting interpolation method."""

    def test_set_method_linear(self):
        """Test setting linear method."""
        state = CurveState()
        result = state.set_method('linear')
        
        assert result is True
        assert state.interpolation_method == 'linear'

    def test_set_method_lagrange(self):
        """Test setting lagrange method."""
        state = CurveState()
        result = state.set_method('lagrange')
        
        assert result is True
        assert state.interpolation_method == 'lagrange'

    def test_set_method_spline(self):
        """Test setting spline method."""
        state = CurveState()
        result = state.set_method('spline')
        
        assert result is True
        assert state.interpolation_method == 'spline'

    def test_set_method_invalid(self):
        """Test setting an invalid method."""
        state = CurveState()
        result = state.set_method('invalid_method')
        
        assert result is False
        assert state.interpolation_method == 'linear'  # Should remain unchanged


class TestCurveStateInterpolatedPath:
    """Tests for generating interpolated paths."""

    def test_interpolated_path_not_enough_points(self):
        """Test path generation with fewer than 2 points."""
        state = CurveState()
        state.add_point(10.0, 10.0)
        
        path = state.get_interpolated_path(resolution=50)
        
        assert path == [(10.0, 10.0)]

    def test_interpolated_path_empty(self):
        """Test path generation with no points."""
        state = CurveState()
        
        path = state.get_interpolated_path(resolution=50)
        
        assert path == []

    def test_interpolated_path_resolution(self):
        """Test that path generation returns correct number of points."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        
        path = state.get_interpolated_path(resolution=100)
        
        assert len(path) == 100

    def test_interpolated_path_custom_resolution(self):
        """Test path generation with custom resolution."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 5.0)
        state.add_point(10.0, 0.0)
        
        path = state.get_interpolated_path(resolution=50)
        
        assert len(path) == 50

    def test_interpolated_path_linear_endpoints(self):
        """Test that linear interpolation preserves endpoints."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.set_method('linear')
        
        path = state.get_interpolated_path(resolution=100)
        
        assert path[0] == (0.0, 0.0)
        assert path[-1] == (10.0, 10.0)

    def test_interpolated_path_spline_endpoints(self):
        """Test that spline interpolation preserves endpoints."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 10.0)
        state.add_point(10.0, 0.0)
        state.set_method('spline')
        
        path = state.get_interpolated_path(resolution=100)
        
        assert path[0] == (0.0, 0.0)
        assert path[-1] == (10.0, 0.0)

    def test_different_methods_produce_different_results(self):
        """Test that different interpolation methods produce different paths."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(5.0, 10.0)
        state.add_point(10.0, 0.0)
        
        state.set_method('linear')
        path_linear = state.get_interpolated_path(resolution=20)
        
        state.set_method('lagrange')
        path_lagrange = state.get_interpolated_path(resolution=20)
        
        state.set_method('spline')
        path_spline = state.get_interpolated_path(resolution=20)
        
        # Compare midpoints - they should be different for non-linear methods
        # since the curve approaches the control point differently
        mid_linear = path_linear[10]
        mid_lagrange = path_lagrange[10]
        mid_spline = path_spline[10]
        
        # At least one pair should be different
        # (linear vs lagrange or linear vs spline)
        differences = [
            abs(mid_linear[0] - mid_lagrange[0]) + abs(mid_linear[1] - mid_lagrange[1]),
            abs(mid_linear[0] - mid_spline[0]) + abs(mid_linear[1] - mid_spline[1]),
        ]
        
        # At least one comparison should show a difference
        assert any(d > 0.01 for d in differences)


class TestCurveStateClearPoints:
    """Tests for clearing control points."""

    def test_clear_points(self):
        """Test clearing all points."""
        state = CurveState()
        state.add_point(0.0, 0.0)
        state.add_point(10.0, 10.0)
        state.add_point(20.0, 20.0)
        
        state.clear_points()
        
        assert state.get_point_count() == 0
        assert state.control_points == []

    def test_clear_points_empty_state(self):
        """Test clearing already empty state."""
        state = CurveState()
        state.clear_points()
        
        assert state.get_point_count() == 0


class TestCurveStateValidMethods:
    """Tests for VALID_METHODS constant."""

    def test_valid_methods_contains_all_expected(self):
        """Test that VALID_METHODS contains all expected methods."""
        assert 'linear' in CurveState.VALID_METHODS
        assert 'lagrange' in CurveState.VALID_METHODS
        assert 'spline' in CurveState.VALID_METHODS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
