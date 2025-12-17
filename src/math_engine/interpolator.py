
import numpy as np
from scipy.interpolate import lagrange, CubicSpline
from typing import List, Tuple

class Interpolator:
    """
    Handles generation of paths based on control points and selected interpolation method.
    """
    
    @staticmethod
    def linear_interpolate(points: List[Tuple[float, float]], num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Connects points with straight lines.
        """
        if len(points) < 2:
            return points

        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        
        # Calculate cumulative distance to space points evenly along the path
        dist = np.cumsum(np.sqrt(np.ediff1d(x, to_begin=0)**2 + np.ediff1d(y, to_begin=0)**2))
        dist = dist / dist[-1] # Normalize 0 to 1
        
        interp_dist = np.linspace(0, 1, num_points)
        
        new_x = np.interp(interp_dist, dist, x)
        new_y = np.interp(interp_dist, dist, y)
        
        return list(zip(new_x, new_y))

    @staticmethod
    def lagrange_interpolate(points: List[Tuple[float, float]], num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Uses Lagrange polynomial. WARNING: Prone to Runge's phenomenon at edges.
        Uses chordal distance parameterization for better smoothness.
        """
        if len(points) < 2:
            return points
            
        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        
        # Chordal distance parameterization
        dist = np.cumsum(np.sqrt(np.ediff1d(x, to_begin=0)**2 + np.ediff1d(y, to_begin=0)**2))
        if dist[-1] == 0: return points
        
        poly_x = lagrange(dist, x)
        poly_y = lagrange(dist, y)
        
        t_new = np.linspace(0, dist[-1], num_points)
        
        new_x = poly_x(t_new)
        new_y = poly_y(t_new)
        
        return list(zip(new_x, new_y))

    @staticmethod
    def cubic_spline_interpolate(points: List[Tuple[float, float]], num_points: int = 100) -> List[Tuple[float, float]]:
        """
        Uses Cubic Spline for smooth paths. Best general purpose method.
        Uses chordal distance parameterization for better smoothness.
        """
        if len(points) < 2:
            return points

        x = np.array([p[0] for p in points])
        y = np.array([p[1] for p in points])
        
        # Chordal distance parameterization
        dist = np.cumsum(np.sqrt(np.ediff1d(x, to_begin=0)**2 + np.ediff1d(y, to_begin=0)**2))
        if dist[-1] == 0: return points
        
        cs_x = CubicSpline(dist, x)
        cs_y = CubicSpline(dist, y)
        
        t_new = np.linspace(0, dist[-1], num_points)
        
        new_x = cs_x(t_new)
        new_y = cs_y(t_new)
        
        return list(zip(new_x, new_y))

