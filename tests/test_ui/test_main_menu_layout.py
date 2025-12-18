import pytest
import pygame
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.main_menu import MainMenu


class TestMainMenuLayout:
    """Tests for MainMenu layout and button positioning."""
    
    def setup_method(self):
        """Set up test fixtures."""
        pygame.init()
        self.screen_width = 1280
        self.screen_height = 720
        self.menu = MainMenu(self.screen_width, self.screen_height)
        # Create a surface for drawing (needed for dynamic positioning)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
    
    def teardown_method(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_all_main_buttons_within_screen(self):
        """Test all main menu buttons fit within screen bounds."""
        for button_name, button_rect in self.menu._buttons.items():
            assert button_rect.top >= 0, f"Button {button_name} top is above screen"
            assert button_rect.bottom <= self.screen_height, f"Button {button_name} bottom is below screen"
            assert button_rect.left >= 0, f"Button {button_name} left is off screen"
            assert button_rect.right <= self.screen_width, f"Button {button_name} right is off screen"
    
    def test_confirm_button_within_screen_for_host(self):
        """Test confirm button fits within screen for host panel."""
        self.menu._selected_option = 'host'
        # Trigger drawing to recalculate positions
        self.menu._draw_connection_panel(self.screen)
        # Verify confirm button is within bounds
        assert self.menu._confirm_button.bottom <= self.screen_height, \
            f"Confirm button bottom ({self.menu._confirm_button.bottom}) exceeds screen height ({self.screen_height})"
        assert self.menu._confirm_button.top >= 0, \
            f"Confirm button top ({self.menu._confirm_button.top}) is above screen"
    
    def test_confirm_button_within_screen_for_join(self):
        """Test confirm button fits within screen for join panel."""
        self.menu._selected_option = 'join'
        # Trigger drawing to recalculate positions
        self.menu._draw_connection_panel(self.screen)
        # Verify confirm button is within bounds
        assert self.menu._confirm_button.bottom <= self.screen_height, \
            f"Confirm button bottom ({self.menu._confirm_button.bottom}) exceeds screen height ({self.screen_height})"
        assert self.menu._confirm_button.top >= 0, \
            f"Confirm button top ({self.menu._confirm_button.top}) is above screen"
    
    def test_input_fields_within_screen_for_host(self):
        """Test input fields fit within screen bounds for host mode."""
        self.menu._selected_option = 'host'
        self.menu._draw_connection_panel(self.screen)
        
        # Only port field should be present for host
        port_rect = self.menu._input_rects.get('port')
        assert port_rect is not None
        assert port_rect.bottom <= self.screen_height, \
            f"Port input bottom ({port_rect.bottom}) exceeds screen height"
        assert port_rect.top >= 0
    
    def test_input_fields_within_screen_for_join(self):
        """Test input fields fit within screen bounds for join mode."""
        self.menu._selected_option = 'join'
        self.menu._draw_connection_panel(self.screen)
        
        # Both IP and port fields should be present for join
        ip_rect = self.menu._input_rects.get('ip')
        port_rect = self.menu._input_rects.get('port')
        
        assert ip_rect is not None
        assert ip_rect.bottom <= self.screen_height, \
            f"IP input bottom ({ip_rect.bottom}) exceeds screen height"
        assert ip_rect.top >= 0
        
        assert port_rect is not None
        assert port_rect.bottom <= self.screen_height, \
            f"Port input bottom ({port_rect.bottom}) exceeds screen height"
        assert port_rect.top >= 0
