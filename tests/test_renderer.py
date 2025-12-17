"""
Tests for the Renderer module.
"""

import pytest
import pygame
from core.grid import Grid
from graphics.renderer import Renderer

class MockScreen:
    def get_width(self): return 800
    def get_height(self): return 600

def test_iso_conversion():
    """Test cartesian to isometric and back conversion."""
    screen = MockScreen()
    grid = Grid(10, 10, 32)
    renderer = Renderer(screen, grid)
    
    # Test Origin
    cart_x, cart_y = 0, 0
    iso_x, iso_y = renderer.cart_to_iso(cart_x, cart_y)
    
    # Check inverse
    res_x, res_y = renderer.iso_to_cart(iso_x, iso_y)
    
    # Allow small rounding error
    assert abs(res_x - cart_x) <= 1
    assert abs(res_y - cart_y) <= 1
    
    # Test Arbitrary Point
    cart_x, cart_y = 5, 5
    iso_x, iso_y = renderer.cart_to_iso(cart_x, cart_y)
    res_x, res_y = renderer.iso_to_cart(iso_x, iso_y)
    
    assert abs(res_x - cart_x) <= 1
    assert abs(res_y - cart_y) <= 1

if __name__ == "__main__":
    test_iso_conversion()
