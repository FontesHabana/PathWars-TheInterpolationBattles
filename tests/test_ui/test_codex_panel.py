"""
Unit tests for CodexPanel UI.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.codex_panel import CodexPanel
from entities.tower import TowerType
from entities.enemy import EnemyType


class TestCodexPanel:
    """Tests for CodexPanel UI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.screen_width = 1280
        self.screen_height = 720
        self.panel = CodexPanel(self.screen_width, self.screen_height)
    
    def test_codex_panel_initial_state(self):
        """Test that codex panel initializes with correct default state."""
        assert self.panel.visible is False
        assert self.panel.current_tab == 'torres'
        assert self.panel.current_index == 0
    
    def test_codex_panel_show(self):
        """Test showing the codex panel."""
        self.panel.show()
        assert self.panel.visible is True
        assert self.panel.current_tab == 'torres'
        assert self.panel.current_index == 0
    
    def test_codex_panel_hide(self):
        """Test hiding the codex panel."""
        self.panel.show()
        self.panel.hide()
        assert self.panel.visible is False
    
    def test_codex_panel_toggle_tabs(self):
        """Test switching between Torres and Enemigos tabs."""
        self.panel.show()
        
        # Initially on torres tab
        assert self.panel.current_tab == 'torres'
        
        # Click enemigos tab
        enemigos_button = self.panel._tab_buttons['enemigos']
        center = enemigos_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        self.panel.handle_event(event)
        
        assert self.panel.current_tab == 'enemigos'
        assert self.panel.current_index == 0  # Reset to first card
        
        # Click torres tab
        torres_button = self.panel._tab_buttons['torres']
        center = torres_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        self.panel.handle_event(event)
        
        assert self.panel.current_tab == 'torres'
        assert self.panel.current_index == 0  # Reset to first card
    
    def test_codex_displays_all_towers(self):
        """Test that all 4 tower types are displayed with correct lore."""
        self.panel.show()
        self.panel._current_tab = 'torres'
        
        # Verify all 4 towers are available
        assert len(self.panel._tower_types) == 4
        assert TowerType.DEAN in self.panel._tower_types
        assert TowerType.CALCULUS in self.panel._tower_types
        assert TowerType.PHYSICS in self.panel._tower_types
        assert TowerType.STATISTICS in self.panel._tower_types
    
    def test_codex_displays_all_enemies(self):
        """Test that all enemy types are displayed with correct lore."""
        self.panel.show()
        self.panel._current_tab = 'enemigos'
        
        # Verify all enemies are available
        assert len(self.panel._enemy_types) == 2
        assert EnemyType.STUDENT in self.panel._enemy_types
        assert EnemyType.VARIABLE_X in self.panel._enemy_types
    
    def test_card_navigation(self):
        """Test navigating between cards with arrows."""
        self.panel.show()
        
        # Start at index 0
        assert self.panel.current_index == 0
        
        # Navigate to next card
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT, 'unicode': ''})
        self.panel.handle_event(event)
        assert self.panel.current_index == 1
        
        # Navigate to next card again
        self.panel.handle_event(event)
        assert self.panel.current_index == 2
        
        # Navigate back
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT, 'unicode': ''})
        self.panel.handle_event(event)
        assert self.panel.current_index == 1
    
    def test_card_navigation_bounds(self):
        """Test that navigation respects bounds."""
        self.panel.show()
        self.panel._current_tab = 'torres'
        self.panel._current_index = 0
        
        # Try to go before first card
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT, 'unicode': ''})
        self.panel.handle_event(event)
        assert self.panel.current_index == 0  # Should stay at 0
        
        # Go to last card
        self.panel._current_index = 3  # Last tower
        
        # Try to go past last card
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT, 'unicode': ''})
        self.panel.handle_event(event)
        assert self.panel.current_index == 3  # Should stay at 3
    
    def test_close_button_returns_to_menu(self):
        """Test that close button hides the panel."""
        self.panel.show()
        
        # Click close button
        close_button = self.panel._close_button
        center = close_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.panel.handle_event(event)
        
        assert result == 'close'
    
    def test_escape_key_closes_panel(self):
        """Test that ESC key closes the panel."""
        self.panel.show()
        
        # Press ESC
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE, 'unicode': ''})
        result = self.panel.handle_event(event)
        
        assert result == 'close'
    
    def test_tab_key_switches_tabs(self):
        """Test that TAB key switches between tabs."""
        self.panel.show()
        assert self.panel.current_tab == 'torres'
        
        # Press TAB
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_TAB, 'unicode': ''})
        self.panel.handle_event(event)
        
        assert self.panel.current_tab == 'enemigos'
        assert self.panel.current_index == 0
        
        # Press TAB again
        self.panel.handle_event(event)
        
        assert self.panel.current_tab == 'torres'
        assert self.panel.current_index == 0
    
    def test_lore_text_displayed_correctly(self):
        """Test that lore text matches the defined lore data."""
        from data.lore import get_tower_lore, get_enemy_lore
        
        # Check tower lore
        for tower_type in self.panel._tower_types:
            lore = get_tower_lore(tower_type)
            assert lore != ""
            assert len(lore) > 0
        
        # Check enemy lore
        for enemy_type in self.panel._enemy_types:
            lore = get_enemy_lore(enemy_type)
            assert lore != ""
            assert len(lore) > 0
    
    def test_navigation_buttons_click(self):
        """Test clicking navigation buttons."""
        self.panel.show()
        assert self.panel.current_index == 0
        
        # Click next button
        next_button = self.panel._nav_buttons['next']
        center = next_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        self.panel.handle_event(event)
        
        assert self.panel.current_index == 1
        
        # Click prev button
        prev_button = self.panel._nav_buttons['prev']
        center = prev_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        self.panel.handle_event(event)
        
        assert self.panel.current_index == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
