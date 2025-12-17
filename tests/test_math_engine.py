
import pytest
import numpy as np
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from math_engine.interpolator import Interpolator

class TestInterpolator:
    def test_linear_basic(self):
        points = [(0, 0), (10, 10)]
        path = Interpolator.linear_interpolate(points, num_points=11)
        
        assert len(path) == 11
        assert path[0] == (0, 0)
        assert path[-1] == (10, 10)
        # Midpoint check
        assert pytest.approx(path[5][0]) == 5.0
        assert pytest.approx(path[5][1]) == 5.0

    def test_lagrange_basic(self):
        # 3 points in a line should still result roughly in a line or simple curve
        points = [(0, 0), (5, 5), (10, 10)]
        path = Interpolator.lagrange_interpolate(points, num_points=10)
        
        assert len(path) == 10
        assert pytest.approx(path[0][0]) == 0
        assert pytest.approx(path[-1][0]) == 10

    def test_cubic_spline_basic(self):
        points = [(0, 0), (5, 10), (10, 0)]
        path = Interpolator.cubic_spline_interpolate(points, num_points=20)
        
        assert len(path) == 20
        assert path[0] == (0, 0)
        assert path[-1] == (10, 0)
        
    def test_not_enough_points(self):
        points = [(0,0)]
        assert Interpolator.linear_interpolate(points) == points
        assert Interpolator.lagrange_interpolate(points) == points
        assert Interpolator.cubic_spline_interpolate(points) == points

if __name__ == "__main__":
    pytest.main()
