"""
Unit tests for Tower Upgrade UI Integration.
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
from entities.tower import TowerType, TowerLevel
from ui.manager import UIManager


class TestTowerUpgradeUI:
    """Tests for tower upgrade UI integration."""
    
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
    
    def test_left_click_on_tower_shows_info_panel(self):
        """Click izquierdo en torre debe mostrar panel de info."""
        # Place a tower manually
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        self.grid.set_occupied(5, 5, True)
        
        # Simulate left click on the tower position
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.input_handler._handle_left_click(screen_pos)
        
        # Verify tower is selected
        assert self.input_handler.selected_tower is not None
        assert self.input_handler.selected_tower == tower
        
        # Verify info panel is visible
        assert self.ui_manager.tower_info_panel.visible
        assert self.ui_manager.tower_info_panel.selected_tower == tower
    
    def test_upgrade_button_visible_for_mastery_level(self):
        """Botón de upgrade visible para torres nivel MASTERY."""
        # Place a tower at MASTERY level
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        
        # Select the tower
        self.ui_manager.select_tower(tower)
        
        # Check that upgrade button exists
        assert self.ui_manager.tower_info_panel.visible
        assert tower.can_upgrade
        assert self.ui_manager.tower_info_panel._upgrade_button is not None
    
    def test_upgrade_button_hidden_for_doctorate_level(self):
        """Botón de upgrade oculto para torres nivel DOCTORATE."""
        # Place a tower and upgrade it to DOCTORATE
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        tower.upgrade()  # Upgrade to DOCTORATE
        self.game_state.add_entity('towers', tower)
        
        # Select the tower
        self.ui_manager.select_tower(tower)
        
        # Check that upgrade button doesn't exist
        assert self.ui_manager.tower_info_panel.visible
        assert not tower.can_upgrade
        assert self.ui_manager.tower_info_panel._upgrade_button is None
    
    def test_upgrade_deducts_correct_cost_from_money(self):
        """Upgrade debe deducir el costo correcto del dinero."""
        # Place a tower
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        self.game_state._money = 500
        
        # Get upgrade cost
        cost = tower.upgrade_cost
        initial_money = self.game_state.money
        
        # Trigger upgrade through UI manager
        success = self.ui_manager._on_tower_upgrade(tower)
        
        # Verify upgrade succeeded
        assert success
        assert tower.level == TowerLevel.DOCTORATE
        assert self.game_state.money == initial_money - cost
    
    def test_left_click_empty_area_does_not_show_panel(self):
        """Click en área vacía no debe mostrar panel."""
        # Simulate left click on empty position
        screen_pos = self.renderer.cart_to_iso(10, 10)
        self.input_handler._handle_left_click(screen_pos)
        
        # Verify no tower is selected
        assert self.input_handler.selected_tower is None
        
        # Verify info panel is not visible
        assert not self.ui_manager.tower_info_panel.visible
    
    def test_insufficient_funds_prevents_upgrade(self):
        """No se puede mejorar torre sin fondos suficientes."""
        # Place a tower
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        self.game_state._money = 10  # Not enough for upgrade
        
        initial_level = tower.level
        
        # Try to upgrade
        success = self.ui_manager._on_tower_upgrade(tower)
        
        # Verify upgrade failed
        assert not success
        assert tower.level == initial_level
        assert self.game_state.money == 10  # Money unchanged


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
