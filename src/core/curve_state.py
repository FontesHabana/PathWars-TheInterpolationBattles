"""
Curve State module for managing control points and interpolation.

Stores control points and the selected interpolation method,
and provides access to the interpolated path.
"""

from typing import List, Tuple

from math_engine.interpolator import Interpolator


class CurveState:
    """
    Stores control points and interpolation method for path generation.

    Manages a list of control points that define the enemy path,
    and uses the selected interpolation method to generate a smooth path.

    Attributes:
        control_points: List of (x, y) tuples representing control points.
        interpolation_method: The interpolation method to use
            ('linear', 'lagrange', 'spline').
    """

    VALID_METHODS = ('linear', 'lagrange', 'spline')

    def __init__(self) -> None:
        """Initialize the CurveState with empty control points and linear interpolation."""
        self._control_points: List[Tuple[float, float]] = []
        self._interpolation_method: str = 'linear'

    @property
    def control_points(self) -> List[Tuple[float, float]]:
        """
        Return a copy of the control points list.

        Returns:
            List of (x, y) tuples representing control points.
        """
        return list(self._control_points)

    @property
    def interpolation_method(self) -> str:
        """
        Return the current interpolation method.

        Returns:
            The interpolation method string ('linear', 'lagrange', or 'spline').
        """
        return self._interpolation_method

    def add_point(self, x: float, y: float) -> None:
        """
        Add a new control point at the specified coordinates.

        Args:
            x: The x coordinate of the new point.
            y: The y coordinate of the new point.
        """
        self._control_points.append((x, y))

    def remove_point(self, index: int) -> bool:
        """
        Remove the control point at the specified index.

        Args:
            index: The index of the point to remove.

        Returns:
            True if the point was removed, False if the index was invalid.
        """
        if 0 <= index < len(self._control_points):
            self._control_points.pop(index)
            return True
        return False

    def move_point(self, index: int, x: float, y: float) -> bool:
        """
        Move the control point at the specified index to new coordinates.

        Args:
            index: The index of the point to move.
            x: The new x coordinate.
            y: The new y coordinate.

        Returns:
            True if the point was moved, False if the index was invalid.
        """
        if 0 <= index < len(self._control_points):
            self._control_points[index] = (x, y)
            return True
        return False

    def set_method(self, method: str) -> bool:
        """
        Set the interpolation method.

        Args:
            method: The interpolation method to use.
                Valid values: 'linear', 'lagrange', 'spline'.

        Returns:
            True if the method was set, False if the method was invalid.
        """
        if method in self.VALID_METHODS:
            self._interpolation_method = method
            return True
        return False

    def get_interpolated_path(
        self, resolution: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Generate the interpolated path from the control points.

        Uses the currently selected interpolation method to generate
        a smooth path through the control points.

        Args:
            resolution: The number of points to generate in the path.

        Returns:
            List of (x, y) tuples representing the interpolated path.
            Returns empty list if there are fewer than 2 control points.
        """
        if len(self._control_points) < 2:
            return list(self._control_points)

        if self._interpolation_method == 'linear':
            return Interpolator.linear_interpolate(
                self._control_points, num_points=resolution
            )
        elif self._interpolation_method == 'lagrange':
            return Interpolator.lagrange_interpolate(
                self._control_points, num_points=resolution
            )
        elif self._interpolation_method == 'spline':
            return Interpolator.cubic_spline_interpolate(
                self._control_points, num_points=resolution
            )
        else:
            # Fallback to linear
            return Interpolator.linear_interpolate(
                self._control_points, num_points=resolution
            )

    def clear_points(self) -> None:
        """Remove all control points."""
        self._control_points.clear()

    def get_point_count(self) -> int:
        """
        Return the number of control points.

        Returns:
            The number of control points.
        """
        return len(self._control_points)
