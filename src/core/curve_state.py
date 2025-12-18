"""
Curve State module for managing control points and interpolation.

Stores control points and the selected interpolation method,
and provides access to the interpolated path.
"""

from typing import List, Tuple

from math_engine.interpolator import Interpolator


class CurveLockedError(Exception):
    """Raised when attempting to modify a locked curve."""
    pass


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
        self._locked: bool = False

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

    @property
    def locked(self) -> bool:
        """
        Return whether the curve is locked.

        Returns:
            True if the curve is locked, False otherwise.
        """
        return self._locked

    def lock(self) -> None:
        """Lock the curve, preventing modifications to control points."""
        self._locked = True

    def unlock(self) -> None:
        """Unlock the curve, allowing modifications to control points."""
        self._locked = False

    def _check_locked(self) -> None:
        """
        Check if the curve is locked and raise an exception if it is.

        Raises:
            CurveLockedError: If the curve is locked.
        """
        if self._locked:
            raise CurveLockedError("Cannot modify control points while curve is locked")

    def add_point(self, x: float, y: float) -> bool:
        """
        Add a new control point at the specified coordinates.
        Ensures points are always sorted by X coordinate.
        Prevents adding points with duplicate X values.

        Args:
            x: The x coordinate of the new point.
            y: The y coordinate of the new point.
        
        Returns:
            True if point was added, False if X is duplicate.
            
        Raises:
            CurveLockedError: If the curve is locked.
        """
        self._check_locked()
        
        # Prevent exact duplicate X values to maintain function property
        for px, _ in self._control_points:
            if abs(px - x) < 0.01:
                return False
                
        self._control_points.append((x, y))
        self._control_points.sort(key=lambda p: p[0])
        return True

    def remove_point(self, index: int) -> bool:
        """
        Remove the control point at the specified index.
        Cannot remove points if only 2 points remain (minimum requirement).

        Args:
            index: The index of the point to remove.

        Returns:
            True if the point was removed, False if the index was invalid
            or if only 2 points remain.
            
        Raises:
            CurveLockedError: If the curve is locked.
        """
        self._check_locked()
        
        # Enforce minimum of 2 points
        if len(self._control_points) <= 2:
            return False
        
        if 0 <= index < len(self._control_points):
            self._control_points.pop(index)
            return True
        return False

    def move_point(self, index: int, x: float, y: float) -> bool:
        """
        Move the control point at the specified index to new coordinates.
        Resorts points after move to maintain X-order.

        Args:
            index: The index of the point to move.
            x: The new x coordinate.
            y: The new y coordinate.

        Returns:
            True if the point was moved, False if the index was invalid or X duplicate.
            
        Raises:
            CurveLockedError: If the curve is locked.
        """
        self._check_locked()
        
        if 0 <= index < len(self._control_points):
            # Check for duplicate X excluding the current point being moved
            for i, (px, _) in enumerate(self._control_points):
                if i != index and abs(px - x) < 0.01:
                    return False
            
            self._control_points[index] = (x, y)
            self._control_points.sort(key=lambda p: p[0])
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
        """
        Remove all control points.
        
        Raises:
            CurveLockedError: If the curve is locked.
        """
        self._check_locked()
        self._control_points.clear()

    def get_point_count(self) -> int:
        """
        Return the number of control points.

        Returns:
            The number of control points.
        """
        return len(self._control_points)

    def initialize_default_points(self, start_x: float = 0.0, end_x: float = 19.0, y: float = 10.0) -> None:
        """
        Initialize the curve with default start and end points.
        Clears any existing points, adds exactly 2 points at the specified positions,
        and unlocks the curve for editing.

        Args:
            start_x: X coordinate of the start point (default: 0.0).
            end_x: X coordinate of the end point (default: 19.0).
            y: Y coordinate for both points (default: 10.0).
        """
        # Temporarily unlock to clear and add points
        was_locked = self._locked
        self._locked = False
        
        self._control_points.clear()
        self._control_points.append((start_x, y))
        self._control_points.append((end_x, y))
        self._control_points.sort(key=lambda p: p[0])
        
        # Ensure curve is unlocked after initialization
        self._locked = False
