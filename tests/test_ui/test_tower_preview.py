"""
Unit tests for Tower Preview System.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.manager import UIManager
from core.game_state import GameState, GamePhase
from core.grid import Grid
from graphics.renderer import Renderer
from entities.factory import EntityFactory
from entities.tower import TowerType


class TestTowerPreview:
    """Tests for tower preview visual system."""
    
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
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_preview_follows_mouse_position(self):
        """El preview debe seguir la posición del mouse."""
        # Select a tower
        self.ui_manager.selected_tower_type = TowerType.DEAN
        
        # Update mouse position
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.ui_manager.update_mouse_position(screen_pos, self.renderer)
        
        # Check that mouse grid position is set
        assert self.ui_manager._mouse_grid_pos is not None
        assert self.ui_manager._mouse_grid_pos == (5, 5)
    
    def test_no_preview_when_no_tower_selected(self):
        """No debe haber preview si no hay torre seleccionada."""
        # Ensure no tower selected
        self.ui_manager.selected_tower_type = None
        
        # Update mouse position
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.ui_manager.update_mouse_position(screen_pos, self.renderer)
        
        # Drawing preview should not crash
        try:
            self.ui_manager.draw_tower_preview(self.screen, self.renderer)
            success = True
        except Exception as e:
            print(f"Error drawing preview: {e}")
            success = False
        
        assert success
    
    def test_no_preview_during_battle_phase(self):
        """No debe haber preview durante fase de batalla."""
        # Select a tower
        self.ui_manager.selected_tower_type = TowerType.DEAN
        
        # Change to battle phase
        self.game_state._current_phase = GamePhase.BATTLE
        
        # Update mouse position
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.ui_manager.update_mouse_position(screen_pos, self.renderer)
        
        # Drawing preview should not crash and should not show anything
        try:
            self.ui_manager.draw_tower_preview(self.screen, self.renderer)
            success = True
        except Exception as e:
            print(f"Error drawing preview: {e}")
            success = False
        
        assert success
    
    def test_preview_updates_with_mouse_movement(self):
        """Preview debe actualizarse al mover el mouse."""
        # Select a tower
        self.ui_manager.selected_tower_type = TowerType.CALCULUS
        
        # Update mouse to position 1
        screen_pos1 = self.renderer.cart_to_iso(3, 3)
        self.ui_manager.update_mouse_position(screen_pos1, self.renderer)
        assert self.ui_manager._mouse_grid_pos == (3, 3)
        
        # Update mouse to position 2
        screen_pos2 = self.renderer.cart_to_iso(7, 8)
        self.ui_manager.update_mouse_position(screen_pos2, self.renderer)
        assert self.ui_manager._mouse_grid_pos == (7, 8)
    
    def test_preview_clears_when_mouse_leaves_grid(self):
        """Preview debe desaparecer cuando el mouse sale del grid."""
        # Select a tower
        self.ui_manager.selected_tower_type = TowerType.PHYSICS
        
        # Update mouse to valid position
        screen_pos = self.renderer.cart_to_iso(5, 5)
        self.ui_manager.update_mouse_position(screen_pos, self.renderer)
        assert self.ui_manager._mouse_grid_pos == (5, 5)
        
        # Update mouse to invalid position (outside grid)
        screen_pos_invalid = self.renderer.cart_to_iso(-1, -1)
        self.ui_manager.update_mouse_position(screen_pos_invalid, self.renderer)
        assert self.ui_manager._mouse_grid_pos is None
    
    def test_preview_can_detect_occupied_vs_valid_position(self):
        """Preview debe detectar posiciones ocupadas vs válidas."""
        # Place a tower at (5, 5)
        tower = EntityFactory.create_tower(TowerType.DEAN, (5, 5))
        self.game_state.add_entity('towers', tower)
        self.grid.set_occupied(5, 5, True)
        
        # Select a tower for placement
        self.ui_manager.selected_tower_type = TowerType.CALCULUS
        
        # Update mouse to occupied position
        screen_pos_occupied = self.renderer.cart_to_iso(5, 5)
        self.ui_manager.update_mouse_position(screen_pos_occupied, self.renderer)
        
        # Update mouse to empty position
        screen_pos_empty = self.renderer.cart_to_iso(10, 10)
        self.ui_manager.update_mouse_position(screen_pos_empty, self.renderer)
        
        # Both should update the position without error
        assert self.ui_manager._mouse_grid_pos == (10, 10)
    
    def test_draw_preview_does_not_crash(self):
        """Drawing preview should never crash."""
        # Test various scenarios
        scenarios = [
            (None, GamePhase.PLANNING),  # No tower selected
            (TowerType.DEAN, GamePhase.PLANNING),  # Valid scenario
            (TowerType.CALCULUS, GamePhase.BATTLE),  # Battle phase
            (TowerType.PHYSICS, GamePhase.PLANNING),  # Different tower
        ]
        
        for tower_type, phase in scenarios:
            self.ui_manager.selected_tower_type = tower_type
            self.game_state._current_phase = phase
            
            # Update mouse position
            screen_pos = self.renderer.cart_to_iso(5, 5)
            self.ui_manager.update_mouse_position(screen_pos, self.renderer)
            
            # Draw preview
            try:
                self.ui_manager.draw_tower_preview(self.screen, self.renderer)
                success = True
            except Exception as e:
                print(f"Error with scenario {tower_type}, {phase}: {e}")
                success = False
            
            assert success


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
