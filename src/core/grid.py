"""
Grid module for managing the game grid and cell positions.
"""

from typing import Tuple, Set


class Grid:
    """
    Manages the game grid for tower placement and coordinate conversion.
    
    Attributes:
        width: Grid width in number of cells.
        height: Grid height in number of cells.
        cell_size: Size of each cell in pixels.
    """
    
    def __init__(self, width: int, height: int, cell_size: int) -> None:
        """
        Initialize the grid.
        
        Args:
            width: Number of cells horizontally.
            height: Number of cells vertically.
            cell_size: Size of each cell in pixels.
        """
        self._width = width
        self._height = height
        self._cell_size = cell_size
        self._occupied: Set[Tuple[int, int]] = set()
    
    @property
    def width(self) -> int:
        """Return grid width in cells."""
        return self._width
    
    @property
    def height(self) -> int:
        """Return grid height in cells."""
        return self._height
    
    @property
    def cell_size(self) -> int:
        """Return cell size in pixels."""
        return self._cell_size
    
    def to_grid_coords(self, screen_x: float, screen_y: float) -> Tuple[int, int]:
        """
        Convert screen coordinates to grid coordinates.
        
        Args:
            screen_x: X position on screen in pixels.
            screen_y: Y position on screen in pixels.
            
        Returns:
            Tuple of (grid_x, grid_y) cell coordinates.
        """
        grid_x = int(screen_x // self._cell_size)
        grid_y = int(screen_y // self._cell_size)
        return (grid_x, grid_y)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if grid coordinates are within bounds.
        
        Args:
            x: Grid x coordinate.
            y: Grid y coordinate.
            
        Returns:
            True if position is within grid bounds.
        """
        return 0 <= x < self._width and 0 <= y < self._height
    
    def is_occupied(self, x: int, y: int) -> bool:
        """
        Check if a grid cell is occupied.
        
        Args:
            x: Grid x coordinate.
            y: Grid y coordinate.
            
        Returns:
            True if the cell is occupied or out of bounds.
        """
        if not self.is_valid_position(x, y):
            return True  # Out of bounds is considered occupied
        return (x, y) in self._occupied
    
    def set_occupied(self, x: int, y: int, occupied: bool = True) -> bool:
        """
        Mark a grid cell as occupied or unoccupied.
        
        Args:
            x: Grid x coordinate.
            y: Grid y coordinate.
            occupied: True to mark as occupied, False to mark as free.
            
        Returns:
            True if the operation was successful.
        """
        if not self.is_valid_position(x, y):
            return False
        
        if occupied:
            self._occupied.add((x, y))
        else:
            self._occupied.discard((x, y))
        return True
    
    def get_occupied_cells(self) -> Set[Tuple[int, int]]:
        """
        Return a copy of all occupied cell positions.
        
        Returns:
            Set of (x, y) tuples representing occupied cells.
        """
        return self._occupied.copy()
