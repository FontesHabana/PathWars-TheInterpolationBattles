"""
Dual View Module.

Implements split-screen rendering for 1v1 multiplayer duels.
"""

import logging
from typing import Optional, Tuple
import pygame

logger = logging.getLogger(__name__)


class DualView:
    """
    Split-screen view manager for multiplayer duels.
    
    Divides the screen vertically into two viewports:
    - Left side: Local player's field
    - Right side: Remote player's field
    
    Attributes:
        screen_width: Total screen width in pixels.
        screen_height: Total screen height in pixels.
    """
    
    def __init__(self, screen_width: int, screen_height: int) -> None:
        """
        Initialize the DualView.
        
        Args:
            screen_width: Total width of the screen in pixels.
            screen_height: Total height of the screen in pixels.
        """
        self._screen_width = screen_width
        self._screen_height = screen_height
        
        # Split screen vertically
        self._viewport_width = screen_width // 2
        self._viewport_height = screen_height
        
        # Define viewports (x, y, width, height)
        self._local_viewport = pygame.Rect(0, 0, self._viewport_width, self._viewport_height)
        self._remote_viewport = pygame.Rect(self._viewport_width, 0, self._viewport_width, self._viewport_height)
        
        # Divider line position
        self._divider_x = self._viewport_width
    
    @property
    def local_viewport(self) -> pygame.Rect:
        """
        Get the local player's viewport rectangle.
        
        Returns:
            Pygame Rect defining the local viewport area.
        """
        return self._local_viewport.copy()
    
    @property
    def remote_viewport(self) -> pygame.Rect:
        """
        Get the remote player's viewport rectangle.
        
        Returns:
            Pygame Rect defining the remote viewport area.
        """
        return self._remote_viewport.copy()
    
    def screen_to_local_grid(self, screen_pos: Tuple[int, int], 
                            grid_width: int, grid_height: int, 
                            cell_size: int) -> Optional[Tuple[int, int]]:
        """
        Convert screen coordinates to local grid coordinates.
        
        Args:
            screen_pos: (x, y) screen position in pixels.
            grid_width: Width of the grid in cells.
            grid_height: Height of the grid in cells.
            cell_size: Size of each grid cell in pixels.
            
        Returns:
            (grid_x, grid_y) tuple if within local viewport, None otherwise.
        """
        screen_x, screen_y = screen_pos
        
        if not self._local_viewport.collidepoint(screen_x, screen_y):
            return None
        
        # Convert to viewport-relative coordinates
        viewport_x = screen_x - self._local_viewport.x
        viewport_y = screen_y - self._local_viewport.y
        
        # Convert to grid coordinates
        grid_x = viewport_x // cell_size
        grid_y = viewport_y // cell_size
        
        # Check bounds
        if 0 <= grid_x < grid_width and 0 <= grid_y < grid_height:
            return (grid_x, grid_y)
        
        return None
    
    def is_in_local_view(self, screen_pos: Tuple[int, int]) -> bool:
        """
        Check if screen position is within the local viewport.
        
        Args:
            screen_pos: (x, y) screen position in pixels.
            
        Returns:
            True if position is in local viewport, False otherwise.
        """
        return self._local_viewport.collidepoint(screen_pos[0], screen_pos[1])
    
    def is_in_remote_view(self, screen_pos: Tuple[int, int]) -> bool:
        """
        Check if screen position is within the remote viewport.
        
        Args:
            screen_pos: (x, y) screen position in pixels.
            
        Returns:
            True if position is in remote viewport, False otherwise.
        """
        return self._remote_viewport.collidepoint(screen_pos[0], screen_pos[1])
    
    def draw_divider(self, surface: pygame.Surface, color: Tuple[int, int, int] = (100, 100, 100)) -> None:
        """
        Draw the divider line between viewports.
        
        Args:
            surface: Pygame surface to draw on.
            color: RGB color tuple for the divider line.
        """
        pygame.draw.line(
            surface,
            color,
            (self._divider_x, 0),
            (self._divider_x, self._screen_height),
            3
        )
    
    def draw_labels(self, surface: pygame.Surface, 
                   local_label: str = "You",
                   remote_label: str = "Opponent",
                   font: Optional[pygame.font.Font] = None) -> None:
        """
        Draw labels for each viewport.
        
        Args:
            surface: Pygame surface to draw on.
            local_label: Text label for local viewport.
            remote_label: Text label for remote viewport.
            font: Pygame font to use. If None, uses default font.
        """
        if font is None:
            font = pygame.font.Font(None, 36)
        
        # Draw local label (top-left)
        local_text = font.render(local_label, True, (255, 255, 255))
        local_rect = local_text.get_rect()
        local_rect.topleft = (10, 10)
        
        # Draw background for better visibility
        bg_rect = local_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0, 128), bg_rect)
        surface.blit(local_text, local_rect)
        
        # Draw remote label (top of remote viewport)
        remote_text = font.render(remote_label, True, (255, 255, 255))
        remote_rect = remote_text.get_rect()
        remote_rect.topleft = (self._divider_x + 10, 10)
        
        # Draw background for better visibility
        bg_rect = remote_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0, 128), bg_rect)
        surface.blit(remote_text, remote_rect)
