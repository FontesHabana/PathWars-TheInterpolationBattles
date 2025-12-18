"""
Unit tests for Interpolation Cost System in CurveEditorUI.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.curve_editor import CurveEditorUI
from core.curve_state import CurveState
from core.game_state import GameState
from core.grid import Grid
from graphics.renderer import Renderer


class TestInterpolationCost:
    """Tests for interpolation method cost system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Reset GameState singleton
        GameState.reset_instance()
        self.game_state = GameState()
        
        # Create grid and renderer
        self.grid = Grid(width=20, height=20, cell_size=32)
        self.renderer = Renderer(self.screen, self.grid)
        
        # Create curve state
        self.curve_state = CurveState()
        self.curve_state.initialize_default_points(start_x=0.0, end_x=19.0, y=10.0)
        
        # Create curve editor
        self.curve_editor = CurveEditorUI(
            self.screen_width,
            self.screen_height,
            self.renderer,
            self.game_state,
            self.curve_state
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_linear_method_is_free(self):
        """Cambiar a Linear no debe costar dinero."""
        initial_money = self.game_state.money
        
        # Change to lagrange first
        self.game_state._money = 1000  # Ensure we have money
        self.curve_state.set_method('lagrange')
        
        # Reset money to track linear change
        self.game_state._money = initial_money
        
        # Change to linear
        self.curve_editor._set_method('linear')
        
        # Check that money didn't change
        assert self.game_state.money == initial_money
        assert self.curve_state.interpolation_method == 'linear'
    
    def test_lagrange_method_costs_50(self):
        """Cambiar a Lagrange debe costar $50."""
        initial_money = 1000
        self.game_state._money = initial_money
        
        # Change to lagrange
        self.curve_editor._set_method('lagrange')
        
        # Check that $50 was deducted
        assert self.game_state.money == initial_money - 50
        assert self.curve_state.interpolation_method == 'lagrange'
    
    def test_spline_method_costs_100(self):
        """Cambiar a Spline debe costar $100."""
        initial_money = 1000
        self.game_state._money = initial_money
        
        # Change to spline
        self.curve_editor._set_method('spline')
        
        # Check that $100 was deducted
        assert self.game_state.money == initial_money - 100
        assert self.curve_state.interpolation_method == 'spline'
    
    def test_insufficient_funds_rejects_change(self):
        """Si no hay fondos suficientes, el método NO debe cambiar."""
        # Set money to less than lagrange cost
        self.game_state._money = 30
        initial_method = self.curve_state.interpolation_method
        
        # Try to change to lagrange (costs $50)
        self.curve_editor._set_method('lagrange')
        
        # Check that method didn't change
        assert self.curve_state.interpolation_method == initial_method
        assert self.game_state.money == 30  # Money unchanged
    
    def test_funds_deducted_on_successful_change(self):
        """El dinero debe deducirse al cambiar método exitosamente."""
        self.game_state._money = 150
        
        # Change to lagrange ($50)
        self.curve_editor._set_method('lagrange')
        assert self.game_state.money == 100
        
        # Change to spline ($100)
        self.curve_editor._set_method('spline')
        assert self.game_state.money == 0
    
    def test_button_labels_show_cost(self):
        """Los botones deben mostrar el costo: 'Lagrange ($50)'."""
        # Check button labels in the panel
        button_labels = []
        for child in self.curve_editor._panel.children:
            if hasattr(child, 'text'):
                button_labels.append(child.text)
        
        # Check that costs are shown in labels
        assert "Linear (Free)" in button_labels
        assert "Lagrange ($50)" in button_labels
        assert "Spline ($100)" in button_labels
    
    def test_no_charge_for_same_method(self):
        """Cambiar al método actual no debe cobrar."""
        self.game_state._money = 1000
        initial_method = self.curve_state.interpolation_method
        
        # Try to set the same method
        self.curve_editor._set_method(initial_method)
        
        # Money should not change
        assert self.game_state.money == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
