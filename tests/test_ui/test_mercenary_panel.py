"""
Unit tests for Mercenary Panel UI.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.mercenary_panel import MercenaryPanel
from ui.manager import UIManager
from core.game_state import GameState
from entities.mercenaries.mercenary_types import MercenaryType


class TestMercenaryPanel:
    """Tests for mercenary panel UI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        
        # Reset GameState singleton
        GameState.reset_instance()
        self.game_state = GameState()
        self.game_state._money = 1000
        
        # Create UI manager
        self.ui_manager = UIManager(self.screen_width, self.screen_height, self.game_state)
        
        # Create mercenary panel
        self.panel = MercenaryPanel(
            self.screen_width,
            self.screen_height,
            on_send_mercenary=self.ui_manager._on_send_mercenary
        )
    
    def teardown_method(self):
        """Clean up after tests."""
        GameState.reset_instance()
    
    def test_panel_hidden_in_singleplayer_mode(self):
        """El panel NO debe ser visible en modo single player."""
        self.ui_manager.set_multiplayer_mode(False)
        assert not self.ui_manager.mercenary_panel.visible
    
    def test_panel_visible_in_multiplayer_mode(self):
        """El panel debe ser visible en modo multiplayer."""
        self.ui_manager.set_multiplayer_mode(True)
        assert self.ui_manager.mercenary_panel.visible
    
    def test_send_mercenary_deducts_correct_cost(self):
        """Enviar mercenario debe deducir el costo correcto."""
        initial_money = self.game_state.money
        
        # Send Reinforced Student ($30)
        success = self.ui_manager._on_send_mercenary(MercenaryType.REINFORCED_STUDENT)
        assert success
        assert self.game_state.money == initial_money - 30
        
        # Send Speedy Variable X ($40)
        success = self.ui_manager._on_send_mercenary(MercenaryType.SPEEDY_VARIABLE_X)
        assert success
        assert self.game_state.money == initial_money - 30 - 40
        
        # Send Tank Constant Pi ($60)
        success = self.ui_manager._on_send_mercenary(MercenaryType.TANK_CONSTANT_PI)
        assert success
        assert self.game_state.money == initial_money - 30 - 40 - 60
    
    def test_send_mercenary_with_insufficient_funds_fails(self):
        """Enviar mercenario sin fondos debe fallar."""
        # Set money to less than cheapest mercenary
        self.game_state._money = 20
        
        # Try to send Reinforced Student ($30)
        success = self.ui_manager._on_send_mercenary(MercenaryType.REINFORCED_STUDENT)
        assert not success
        assert self.game_state.money == 20  # Money unchanged
    
    def test_mercenary_buttons_show_cost(self):
        """Los botones deben mostrar el costo de cada mercenario."""
        # Check button labels in the panel
        button_labels = []
        for child in self.panel.panel.children:
            if hasattr(child, 'text'):
                button_labels.append(child.text)
        
        # Check that costs are shown in labels
        assert "Reinforced Student ($30)" in button_labels
        assert "Speedy Variable X ($40)" in button_labels
        assert "Tank Constant Pi ($60)" in button_labels
    
    def test_panel_initial_state_hidden(self):
        """Panel debe iniciar oculto."""
        panel = MercenaryPanel(self.screen_width, self.screen_height)
        assert not panel.visible
    
    def test_panel_show_hide_methods(self):
        """Métodos show() y hide() deben funcionar."""
        panel = MercenaryPanel(self.screen_width, self.screen_height)
        
        # Initially hidden
        assert not panel.visible
        
        # Show
        panel.show()
        assert panel.visible
        
        # Hide
        panel.hide()
        assert not panel.visible
    
    def test_panel_handles_events_when_visible(self):
        """Panel debe manejar eventos cuando está visible."""
        self.panel.show()
        
        # Create a mouse click event
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)})
        
        # Panel should process the event (return True or False depending on hit)
        # The important thing is it doesn't crash
        try:
            result = self.panel.handle_event(event)
            success = True
        except Exception as e:
            print(f"Error handling event: {e}")
            success = False
        
        assert success
    
    def test_panel_ignores_events_when_hidden(self):
        """Panel debe ignorar eventos cuando está oculto."""
        self.panel.hide()
        
        # Create a mouse click event
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (100, 100)})
        
        # Panel should not handle event when hidden
        result = self.panel.handle_event(event)
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
