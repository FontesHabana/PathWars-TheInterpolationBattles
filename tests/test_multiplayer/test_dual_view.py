"""
Unit tests for DualView.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from multiplayer.dual_view import DualView


class TestDualView:
    """Tests for DualView split-screen rendering."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.screen_width = 1280
        self.screen_height = 720
        self.dual_view = DualView(self.screen_width, self.screen_height)
    
    def test_viewport_dimensions(self):
        """Test that viewports have correct dimensions."""
        local_vp = self.dual_view.local_viewport
        remote_vp = self.dual_view.remote_viewport
        
        # Each viewport should be half the screen width
        assert local_vp.width == self.screen_width // 2
        assert remote_vp.width == self.screen_width // 2
        
        # Both should be full height
        assert local_vp.height == self.screen_height
        assert remote_vp.height == self.screen_height
    
    def test_local_viewport_on_left(self):
        """Test that local viewport is on the left side."""
        local_vp = self.dual_view.local_viewport
        
        assert local_vp.x == 0
        assert local_vp.y == 0
    
    def test_remote_viewport_on_right(self):
        """Test that remote viewport is on the right side."""
        remote_vp = self.dual_view.remote_viewport
        
        assert remote_vp.x == self.screen_width // 2
        assert remote_vp.y == 0
    
    def test_screen_to_local_grid_conversion(self):
        """Test converting screen coordinates to grid coordinates."""
        # Cell size 32, grid 20x20
        cell_size = 32
        grid_width = 20
        grid_height = 20
        
        # Click at (64, 96) in local viewport
        # Should be grid (2, 3)
        result = self.dual_view.screen_to_local_grid((64, 96), grid_width, grid_height, cell_size)
        
        assert result == (2, 3)
    
    def test_is_in_local_view(self):
        """Test checking if position is in local viewport."""
        # Position in left half
        assert self.dual_view.is_in_local_view((100, 100)) is True
        assert self.dual_view.is_in_local_view((320, 360)) is True
        
        # Position in right half
        assert self.dual_view.is_in_local_view((800, 100)) is False
    
    def test_is_in_remote_view(self):
        """Test checking if position is in remote viewport."""
        # Position in right half
        assert self.dual_view.is_in_remote_view((800, 100)) is True
        assert self.dual_view.is_in_remote_view((1000, 360)) is True
        
        # Position in left half
        assert self.dual_view.is_in_remote_view((100, 100)) is False
    
    def test_click_outside_both_views(self):
        """Test that clicks outside screen bounds work correctly."""
        # Position outside screen
        assert self.dual_view.is_in_local_view((2000, 100)) is False
        assert self.dual_view.is_in_remote_view((2000, 100)) is False
    
    def test_screen_to_local_grid_out_of_bounds(self):
        """Test that out-of-bounds clicks return None."""
        cell_size = 32
        grid_width = 20
        grid_height = 20
        
        # Click outside grid bounds but inside viewport
        # 20x20 grid with 32px cells = 640px, so click at 641 should be out of bounds
        result = self.dual_view.screen_to_local_grid((641, 50), grid_width, grid_height, cell_size)
        assert result is None
        
        # Click in remote viewport
        result = self.dual_view.screen_to_local_grid((800, 100), grid_width, grid_height, cell_size)
        assert result is None
    
    def test_screen_to_local_grid_edge_cases(self):
        """Test edge cases for grid conversion."""
        cell_size = 32
        grid_width = 20
        grid_height = 20
        
        # Click at (0, 0) - top-left corner
        result = self.dual_view.screen_to_local_grid((0, 0), grid_width, grid_height, cell_size)
        assert result == (0, 0)
        
        # Click at last valid cell
        last_x = (grid_width - 1) * cell_size
        last_y = (grid_height - 1) * cell_size
        result = self.dual_view.screen_to_local_grid((last_x, last_y), grid_width, grid_height, cell_size)
        assert result == (grid_width - 1, grid_height - 1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
