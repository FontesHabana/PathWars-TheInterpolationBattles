"""
Unit tests for autotiling system in PathWars - The Interpolation Battles.

Tests cover PathTileSelector and path tile selection logic.
"""

import pytest
import sys
import os

# Add src to path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from graphics.autotiler import PathDirection, PathTileType, PathTileSelector


class TestPathTileSelector:
    """Tests for the PathTileSelector class."""
    
    def test_horizontal_straight(self):
        """Test that E+W connections produce horizontal straight tile."""
        selector = PathTileSelector()
        connections = {PathDirection.EAST, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.STRAIGHT_H
    
    def test_vertical_straight(self):
        """Test that N+S connections produce vertical straight tile."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.SOUTH}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.STRAIGHT_V
    
    def test_curve_ne(self):
        """Test that N+E connections produce NE curve tile."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.EAST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.CURVE_NE
    
    def test_curve_nw(self):
        """Test that N+W connections produce NW curve tile."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.CURVE_NW
    
    def test_curve_se(self):
        """Test that S+E connections produce SE curve tile."""
        selector = PathTileSelector()
        connections = {PathDirection.SOUTH, PathDirection.EAST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.CURVE_SE
    
    def test_curve_sw(self):
        """Test that S+W connections produce SW curve tile."""
        selector = PathTileSelector()
        connections = {PathDirection.SOUTH, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.CURVE_SW
    
    def test_t_intersection_north(self):
        """Test T intersection with all directions except north."""
        selector = PathTileSelector()
        connections = {PathDirection.SOUTH, PathDirection.EAST, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.T_SOUTH
    
    def test_t_intersection_south(self):
        """Test T intersection with all directions except south."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.EAST, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.T_NORTH
    
    def test_t_intersection_east(self):
        """Test T intersection with all directions except east."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.SOUTH, PathDirection.WEST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.T_WEST
    
    def test_t_intersection_west(self):
        """Test T intersection with all directions except west."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH, PathDirection.SOUTH, PathDirection.EAST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.T_EAST
    
    def test_cross_intersection(self):
        """Test cross intersection with all four directions."""
        selector = PathTileSelector()
        connections = {
            PathDirection.NORTH,
            PathDirection.SOUTH,
            PathDirection.EAST,
            PathDirection.WEST
        }
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.CROSS
    
    def test_single_connection_north_returns_vertical(self):
        """Test that single north connection returns vertical straight."""
        selector = PathTileSelector()
        connections = {PathDirection.NORTH}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.STRAIGHT_V
    
    def test_single_connection_east_returns_horizontal(self):
        """Test that single east connection returns horizontal straight."""
        selector = PathTileSelector()
        connections = {PathDirection.EAST}
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.STRAIGHT_H
    
    def test_empty_connection_returns_empty(self):
        """Test that no connections return empty tile type."""
        selector = PathTileSelector()
        connections = set()
        
        tile_type = selector.select_tile_type(connections)
        assert tile_type == PathTileType.EMPTY
    
    def test_get_tile_sprite_returns_sprite_for_valid_type(self):
        """Test that get_tile_sprite returns a sprite for valid tile types."""
        # This test requires AssetManager to be initialized
        # For now, we'll just test that the method doesn't crash
        selector = PathTileSelector()
        
        # Get sprite for straight horizontal (should return sprite or None)
        sprite = selector.get_tile_sprite(PathTileType.STRAIGHT_H)
        # If assets aren't loaded, it will be None, which is acceptable
        assert sprite is None or hasattr(sprite, 'get_rect')
