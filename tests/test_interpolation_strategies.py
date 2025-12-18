"""
Comprehensive tests for the Interpolation Strategy Pattern implementation.

Tests the strategy pattern refactoring for interpolation methods,
including individual strategies, registry functionality, and edge cases.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from math_engine.strategies import LinearInterpolation, LagrangeInterpolation, SplineInterpolation
from math_engine.interpolation_registry import InterpolationRegistry, get_registry
from math_engine.interpolator import Interpolator


class TestLinearStrategy:
    """Test the LinearInterpolation strategy."""
    
    def test_linear_basic_interpolation(self):
        """Test basic linear interpolation between two points."""
        strategy = LinearInterpolation()
        points = [(0, 0), (10, 10)]
        path = strategy.interpolate(points, resolution=11)
        
        assert len(path) == 11
        assert path[0] == pytest.approx((0, 0))
        assert path[-1] == pytest.approx((10, 10))
        # Midpoint should be at (5, 5)
        assert path[5][0] == pytest.approx(5.0)
        assert path[5][1] == pytest.approx(5.0)
    
    def test_linear_name_property(self):
        """Test that linear strategy has correct name."""
        strategy = LinearInterpolation()
        assert strategy.name == "linear"
    
    def test_linear_requires_no_research(self):
        """Test that linear strategy doesn't require research."""
        strategy = LinearInterpolation()
        assert strategy.requires_research is False
    
    def test_linear_single_point(self):
        """Test linear interpolation with single point returns the point."""
        strategy = LinearInterpolation()
        points = [(5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        assert len(path) == 1
        assert path[0] == (5, 5)
    
    def test_linear_empty_points_raises_error(self):
        """Test that empty points list raises ValueError."""
        strategy = LinearInterpolation()
        with pytest.raises(ValueError, match="cannot be empty"):
            strategy.interpolate([], resolution=10)
    
    def test_linear_none_points_raises_error(self):
        """Test that None points raises ValueError."""
        strategy = LinearInterpolation()
        with pytest.raises(ValueError, match="cannot be None"):
            strategy.interpolate(None, resolution=10)
    
    def test_linear_duplicate_points(self):
        """Test linear interpolation with duplicate points."""
        strategy = LinearInterpolation()
        points = [(5, 5), (5, 5), (5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        # Should return original points when all points are the same
        assert len(path) == 3
        assert all(p == (5, 5) for p in path)


class TestLagrangeStrategy:
    """Test the LagrangeInterpolation strategy."""
    
    def test_lagrange_basic_interpolation(self):
        """Test basic Lagrange interpolation."""
        strategy = LagrangeInterpolation()
        points = [(0, 0), (5, 5), (10, 10)]
        path = strategy.interpolate(points, resolution=10)
        
        assert len(path) == 10
        # First and last points should match
        assert path[0][0] == pytest.approx(0, abs=0.1)
        assert path[-1][0] == pytest.approx(10, abs=0.1)
    
    def test_lagrange_name_property(self):
        """Test that Lagrange strategy has correct name."""
        strategy = LagrangeInterpolation()
        assert strategy.name == "lagrange"
    
    def test_lagrange_requires_research(self):
        """Test that Lagrange strategy requires research."""
        strategy = LagrangeInterpolation()
        assert strategy.requires_research is True
    
    def test_lagrange_single_point(self):
        """Test Lagrange interpolation with single point."""
        strategy = LagrangeInterpolation()
        points = [(5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        assert len(path) == 1
        assert path[0] == (5, 5)
    
    def test_lagrange_empty_points_raises_error(self):
        """Test that empty points list raises ValueError."""
        strategy = LagrangeInterpolation()
        with pytest.raises(ValueError, match="cannot be empty"):
            strategy.interpolate([], resolution=10)
    
    def test_lagrange_duplicate_points(self):
        """Test Lagrange interpolation with duplicate points."""
        strategy = LagrangeInterpolation()
        points = [(5, 5), (5, 5), (5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        # Should return original points when all points are the same
        assert len(path) == 3


class TestSplineStrategy:
    """Test the SplineInterpolation strategy."""
    
    def test_spline_basic_interpolation(self):
        """Test basic spline interpolation."""
        strategy = SplineInterpolation()
        points = [(0, 0), (5, 10), (10, 0)]
        path = strategy.interpolate(points, resolution=20)
        
        assert len(path) == 20
        assert path[0] == pytest.approx((0, 0))
        assert path[-1] == pytest.approx((10, 0))
    
    def test_spline_name_property(self):
        """Test that spline strategy has correct name."""
        strategy = SplineInterpolation()
        assert strategy.name == "spline"
    
    def test_spline_requires_research(self):
        """Test that spline strategy requires research."""
        strategy = SplineInterpolation()
        assert strategy.requires_research is True
    
    def test_spline_single_point(self):
        """Test spline interpolation with single point."""
        strategy = SplineInterpolation()
        points = [(5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        assert len(path) == 1
        assert path[0] == (5, 5)
    
    def test_spline_empty_points_raises_error(self):
        """Test that empty points list raises ValueError."""
        strategy = SplineInterpolation()
        with pytest.raises(ValueError, match="cannot be empty"):
            strategy.interpolate([], resolution=10)
    
    def test_spline_duplicate_points(self):
        """Test spline interpolation with duplicate points."""
        strategy = SplineInterpolation()
        points = [(5, 5), (5, 5), (5, 5)]
        path = strategy.interpolate(points, resolution=10)
        
        # Should return original points when all points are the same
        assert len(path) == 3


class TestInterpolationRegistry:
    """Test the InterpolationRegistry singleton."""
    
    def test_registry_singleton(self):
        """Test that registry is a singleton."""
        registry1 = InterpolationRegistry()
        registry2 = InterpolationRegistry()
        assert registry1 is registry2
    
    def test_get_registry_function(self):
        """Test the get_registry convenience function."""
        registry1 = get_registry()
        registry2 = get_registry()
        assert registry1 is registry2
    
    def test_get_linear_strategy(self):
        """Test getting linear strategy from registry."""
        registry = get_registry()
        strategy = registry.get_strategy('linear')
        
        assert strategy.name == 'linear'
        assert isinstance(strategy, LinearInterpolation)
    
    def test_get_lagrange_strategy(self):
        """Test getting Lagrange strategy from registry."""
        registry = get_registry()
        strategy = registry.get_strategy('lagrange')
        
        assert strategy.name == 'lagrange'
        assert isinstance(strategy, LagrangeInterpolation)
    
    def test_get_spline_strategy(self):
        """Test getting spline strategy from registry."""
        registry = get_registry()
        strategy = registry.get_strategy('spline')
        
        assert strategy.name == 'spline'
        assert isinstance(strategy, SplineInterpolation)
    
    def test_get_invalid_strategy(self):
        """Test that getting invalid strategy raises KeyError."""
        registry = get_registry()
        
        with pytest.raises(KeyError, match="Unknown interpolation strategy"):
            registry.get_strategy('invalid')
    
    def test_get_available_strategies(self):
        """Test getting list of available strategies."""
        registry = get_registry()
        strategies = registry.get_available_strategies()
        
        assert 'linear' in strategies
        assert 'lagrange' in strategies
        assert 'spline' in strategies
        assert len(strategies) >= 3
    
    def test_is_unlocked_linear_always_unlocked(self):
        """Test that linear is always unlocked."""
        registry = get_registry()
        
        # Linear should be unlocked with any set of unlocked methods
        assert registry.is_unlocked('linear', set()) is True
        assert registry.is_unlocked('linear', {'lagrange'}) is True
    
    def test_is_unlocked_lagrange_requires_unlock(self):
        """Test that Lagrange requires unlock."""
        registry = get_registry()
        
        # Not unlocked without permission
        assert registry.is_unlocked('lagrange', set()) is False
        
        # Unlocked when in the set
        assert registry.is_unlocked('lagrange', {'lagrange'}) is True
    
    def test_is_unlocked_spline_requires_unlock(self):
        """Test that spline requires unlock."""
        registry = get_registry()
        
        # Not unlocked without permission
        assert registry.is_unlocked('spline', set()) is False
        
        # Unlocked when in the set
        assert registry.is_unlocked('spline', {'spline'}) is True


class TestInterpolatorNewMethod:
    """Test the new Interpolator.interpolate() method that uses strategies."""
    
    def test_interpolate_linear(self):
        """Test interpolate method with linear strategy."""
        points = [(0, 0), (10, 10)]
        path = Interpolator.interpolate(points, method='linear', num_points=11)
        
        assert len(path) == 11
        assert path[0] == pytest.approx((0, 0))
        assert path[-1] == pytest.approx((10, 10))
    
    def test_interpolate_lagrange(self):
        """Test interpolate method with Lagrange strategy."""
        points = [(0, 0), (5, 5), (10, 10)]
        path = Interpolator.interpolate(points, method='lagrange', num_points=10)
        
        assert len(path) == 10
    
    def test_interpolate_spline(self):
        """Test interpolate method with spline strategy."""
        points = [(0, 0), (5, 10), (10, 0)]
        path = Interpolator.interpolate(points, method='spline', num_points=20)
        
        assert len(path) == 20
    
    def test_interpolate_invalid_method(self):
        """Test that invalid method raises KeyError."""
        points = [(0, 0), (10, 10)]
        
        with pytest.raises(KeyError):
            Interpolator.interpolate(points, method='invalid')


class TestBackwardCompatibility:
    """Test backward compatibility with old static methods."""
    
    def test_linear_interpolate_still_works(self):
        """Test that old linear_interpolate still works."""
        points = [(0, 0), (10, 10)]
        
        # Suppress the deprecation warning for this test
        with pytest.warns(DeprecationWarning):
            path = Interpolator.linear_interpolate(points, num_points=11)
        
        assert len(path) == 11
        assert path[0] == (0, 0)
        assert path[-1] == (10, 10)
    
    def test_lagrange_interpolate_still_works(self):
        """Test that old lagrange_interpolate still works."""
        points = [(0, 0), (5, 5), (10, 10)]
        
        with pytest.warns(DeprecationWarning):
            path = Interpolator.lagrange_interpolate(points, num_points=10)
        
        assert len(path) == 10
    
    def test_cubic_spline_interpolate_still_works(self):
        """Test that old cubic_spline_interpolate still works."""
        points = [(0, 0), (5, 10), (10, 0)]
        
        with pytest.warns(DeprecationWarning):
            path = Interpolator.cubic_spline_interpolate(points, num_points=20)
        
        assert len(path) == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
