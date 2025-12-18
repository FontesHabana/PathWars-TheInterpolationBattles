"""
Lagrange Interpolation Strategy

Implements Lagrange polynomial interpolation for smooth curved paths.
Requires research to unlock (cost: 500$).
"""

import numpy as np
from scipy.interpolate import lagrange
from typing import List, Tuple


class LagrangeInterpolation:
    """
    Lagrange polynomial interpolation strategy.
    
    Uses Lagrange polynomial to create smooth curved paths through control points.
    WARNING: Prone to Runge's phenomenon (oscillations) at edges with many points.
    
    Requires research to unlock.
    Research cost: 500$
    """
    
    @property
    def name(self) -> str:
        """Human-readable name of the interpolation method."""
        return "lagrange"
    
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
        Interpolate between control points using Lagrange polynomial.
        
        Uses chordal distance parameterization for better smoothness.
        The polynomial passes exactly through all control points.
        
        Args:
            control_points: List of (x, y) tuples defining control points.
            resolution: Number of points to generate in the path.
            
        Returns:
            List of (x, y) tuples representing the interpolated path.
            Returns the original points if fewer than 2 points are provided.
            
        Raises:
            ValueError: If control_points is empty or None.
            
        Note:
            This method can produce oscillations (Runge's phenomenon) when
            using many control points. Consider using SplineInterpolation
            for smoother results with many points.
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
        
        # Create Lagrange polynomials for x and y separately
        poly_x = lagrange(dist, x)
        poly_y = lagrange(dist, y)
        
        # Generate new parameter values
        t_new = np.linspace(0, dist[-1], resolution)
        
        # Evaluate polynomials
        new_x = poly_x(t_new)
        new_y = poly_y(t_new)
        
        return list(zip(new_x, new_y))
