"""
Interpolation Strategy Protocol

Defines the interface for interpolation strategies following the Strategy Pattern.
Each strategy implements a different mathematical interpolation method.
"""

from typing import List, Tuple, Protocol


class InterpolationStrategy(Protocol):
    """Protocol for interpolation strategies following Strategy Pattern."""
    
    @property
    def name(self) -> str:
        """Human-readable name of the interpolation method."""
        ...
    
    @property
    def requires_research(self) -> bool:
        """Whether this method requires research to unlock."""
        ...
    
    def interpolate(
        self, 
        control_points: List[Tuple[float, float]], 
        resolution: int = 100
    ) -> List[Tuple[float, float]]:
        """
        Interpolate between control points.
        
        Args:
            control_points: List of (x, y) tuples defining control points.
            resolution: Number of points to generate in the path.
            
        Returns:
            List of (x, y) tuples representing the interpolated path.
        """
        ...
