"""
Linear Interpolation Strategy

Implements linear interpolation by connecting control points with straight lines.
This is the default interpolation method, always available without research.
"""

import numpy as np
from typing import List, Tuple


class LinearInterpolation:
    """
    Linear interpolation strategy.
    
    Connects control points with straight lines using linear interpolation.
    This is the most basic and predictable interpolation method.
    Always available without requiring research.
    """
    
    @property
    def name(self) -> str:
        """Human-readable name of the interpolation method."""
        return "linear"
    
    @property
    def requires_research(self) -> bool:
        """Whether this method requires research to unlock."""
        return False
    
    def interpolate(
        self, 
        control_points: List[Tuple[float, float]], 
        resolution: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Interpolate between control points using linear interpolation.
        
        Connects points with straight lines, using chordal distance
        parameterization to space points evenly along the path.
        
        Args:
            control_points: List of (x, y) tuples defining control points.
            resolution: Number of points to generate in the path.
            
        Returns:
            List of (x, y) tuples representing the interpolated path.
            Returns the original points if fewer than 2 points are provided.
            
        Raises:
            ValueError: If control_points is empty or None.
        """
        if control_points is None:
            raise ValueError("control_points cannot be None")
        
        if len(control_points) == 0:
            raise ValueError("control_points cannot be empty")
        
        if len(control_points) < 2:
            return list(control_points)

        x = np.array([p[0] for p in control_points])
        y = np.array([p[1] for p in control_points])
        
        # Calculate cumulative distance to space points evenly along the path
        dist = np.cumsum(np.sqrt(np.ediff1d(x, to_begin=0)**2 + np.ediff1d(y, to_begin=0)**2))
        
        # Handle edge case: all points are the same (zero distance)
        if dist[-1] == 0:
            return list(control_points)
        
        dist = dist / dist[-1]  # Normalize 0 to 1
        
        interp_dist = np.linspace(0, 1, resolution)
        
        new_x = np.interp(interp_dist, dist, x)
        new_y = np.interp(interp_dist, dist, y)
        
        return list(zip(new_x, new_y))
