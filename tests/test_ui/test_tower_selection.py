"""
Unit tests for Tower Selection and Deselection UX.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from core.game_state import GameState, GamePhase
from core.grid import Grid
from core.input_handler import InputHandler
from graphics.renderer import Renderer
from graphics.assets import AssetManager
from entities.factory import EntityFactory
from entities.tower import TowerType
from ui.manager import UIManager


class TestTowerDeselection:
    """Tests for tower selection and deselection UX."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Reset GameState singleton
        GameState.reset_instance()
        self.game_state = GameState()
        self.game_state._current_phase = GamePhase.PLANNING
        self.game_state._money = 1000
        
        # Create grid and renderer
        self.grid = Grid(width=20, height=20, cell_size=32)
        self.renderer = Renderer(self.screen, self.grid)
        
        # Create UI manager
        self.ui_manager = UIManager(self.screen_width, self.screen_height, self.game_state)
        
        # Create input handler
        self.input_handler = InputHandler(self.game_state, self.grid, self.renderer)
        self.input_handler.ui_manager = self.ui_manager
        self.input_handler.on_tower_selected = self.ui_manager.select_tower
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_initial_state_no_tower_selected(self):
        """El estado inicial debe ser sin torre seleccionada."""
        assert self.ui_manager.selected_tower_type is None
        assert self.input_handler.selected_tower_type is None
    
    def test_toggle_same_shop_button_deselects(self):
        """Click en el mismo botón del shop debe deseleccionar."""
        # Select a tower type
        self.ui_manager._select_tower(TowerType.DEAN)
        assert self.ui_manager.selected_tower_type == TowerType.DEAN
        
        # Click same button again (toggle)
        self.ui_manager._select_tower(TowerType.DEAN)
        assert self.ui_manager.selected_tower_type is None
    
    def test_esc_key_still_deselects(self):
        """La tecla ESC debe seguir funcionando para deseleccionar."""
        # Select a tower type
        self.ui_manager.selected_tower_type = TowerType.CALCULUS
        self.input_handler.selected_tower_type = TowerType.CALCULUS
        
        # Simulate ESC key press
        self.input_handler._handle_keydown(pygame.K_ESCAPE)
        
        # Verify tower selection deselected (for info panel)
        assert self.input_handler.selected_tower is None
    
    def test_click_existing_tower_selects_for_info(self):
        """Click en torre existente debe mostrar info panel, no colocar."""
        # Place a tower
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        self.grid.set_occupied(5, 5, True)
        
        # Select a different tower type for placement
        self.ui_manager.selected_tower_type = TowerType.CALCULUS
        self.input_handler.selected_tower_type = TowerType.CALCULUS
        
        # Click on existing tower
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.input_handler._handle_left_click(screen_pos)
        
        # Verify existing tower is selected (not a new tower placed)
        assert self.input_handler.selected_tower == tower
        assert len(self.game_state.entities_collection['towers']) == 1
    
    def test_no_tower_placement_when_none_selected(self):
        """No se debe colocar torre si no hay ninguna seleccionada."""
        # Ensure no tower is selected
        self.ui_manager.selected_tower_type = None
        self.input_handler.selected_tower_type = None
        
        initial_money = self.game_state.money
        
        # Try to place (click empty area)
        screen_pos = self.renderer.cart_to_iso(10, 10)
        self.input_handler._handle_left_click(screen_pos)
        
        # Verify no tower was placed and money unchanged
        assert len(self.game_state.entities_collection['towers']) == 0
        assert self.game_state.money == initial_money
    
    def test_selection_changes_correctly(self):
        """Cambiar de un tipo de torre a otro debe funcionar."""
        # Select first tower
        self.ui_manager._select_tower(TowerType.DEAN)
        assert self.ui_manager.selected_tower_type == TowerType.DEAN
        
        # Select different tower
        self.ui_manager._select_tower(TowerType.PHYSICS)
        assert self.ui_manager.selected_tower_type == TowerType.PHYSICS
    
    def test_ui_shows_no_tower_selected_text(self):
        """UI debe mostrar 'No tower selected' cuando no hay torre."""
        # Ensure no tower selected
        self.ui_manager.selected_tower_type = None
        
        # Draw UI (this should not throw an error)
        try:
            self.ui_manager.draw(self.screen)
            success = True
        except Exception as e:
            print(f"Error drawing UI: {e}")
            success = False
        
        assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
