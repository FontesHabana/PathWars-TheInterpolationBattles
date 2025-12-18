"""
Spline Interpolation Strategy

Implements cubic spline interpolation for the smoothest paths.
Requires research to unlock (cost: 1000$).
"""

import numpy as np
from scipy.interpolate import CubicSpline
from typing import List, Tuple


class SplineInterpolation:
    """
    Cubic spline interpolation strategy.
    
    Uses cubic splines to create the smoothest possible paths through control points.
    This is the best general-purpose interpolation method, avoiding the oscillations
    of Lagrange polynomials while maintaining smoothness.
    
    Requires research to unlock.
    Research cost: 1000$
    """
    
    @property
    def name(self) -> str:
        """Human-readable name of the interpolation method."""
        return "spline"
    
    @property
    def requires_research(self) -> bool:
        """Whether this method requires research to unlock."""
        return True
    
    def interpolate(
        self, 
        control_points: List[Tuple[float, float]], 
        resolution: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Interpolate between control points using cubic spline.
        
        Uses chordal distance parameterization for better smoothness.
        Creates a smooth C2-continuous curve through all control points.
        
        Args:
            control_points: List of (x, y) tuples defining control points.
            resolution: Number of points to generate in the path.
            
        Returns:
            List of (x, y) tuples representing the interpolated path.
            Returns the original points if fewer than 2 points are provided.
            
        Raises:
            ValueError: If control_points is empty or None.
            
        Note:
            This method provides the best smoothness and stability for
            general-purpose interpolation with multiple control points.
        """
        if control_points is None:
            raise ValueError("control_points cannot be None")
        
        if len(control_points) == 0:
            raise ValueError("control_points cannot be empty")
        
        if len(control_points) < 2:
            return list(control_points)

        x = np.array([p[0] for p in control_points])
        y = np.array([p[1] for p in control_points])
        
        # Chordal distance parameterization
        dist = np.cumsum(np.sqrt(np.ediff1d(x, to_begin=0)**2 + np.ediff1d(y, to_begin=0)**2))
        
        # Handle edge case: all points are the same (zero distance)
        if dist[-1] == 0:
            return list(control_points)
        
        # Create cubic splines for x and y separately
        cs_x = CubicSpline(dist, x)
        cs_y = CubicSpline(dist, y)
        
        # Generate new parameter values
        t_new = np.linspace(0, dist[-1], resolution)
        
        # Evaluate splines
        new_x = cs_x(t_new)
        new_y = cs_y(t_new)
        
        return list(zip(new_x, new_y))
