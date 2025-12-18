"""
Unit tests for MainMenu UI.
"""

import sys
import os
import pytest
import pygame

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

from ui.main_menu import MainMenu


class TestMainMenu:
    """Tests for MainMenu UI."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.screen_width = 1280
        self.screen_height = 720
        self.menu = MainMenu(self.screen_width, self.screen_height)
    
    def test_initial_state(self):
        """Test initial state of MainMenu."""
        assert self.menu.visible is True
        assert self.menu._selected_option is None
        assert self.menu._active_input is None
        assert self.menu._ip_input == "127.0.0.1"
        assert self.menu._port_input == "12345"
    
    def test_button_hover_state(self):
        """Test that hovering over buttons updates hover state."""
        # Get the position of the host button
        host_button = self.menu._buttons['host']
        center = host_button.center
        
        # Simulate mouse motion
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': center})
        self.menu.handle_event(event)
        
        assert self.menu._hovered_button == 'host'
    
    def test_host_button_shows_panel(self):
        """Test that clicking host button shows connection panel."""
        host_button = self.menu._buttons['host']
        center = host_button.center
        
        # Simulate click on host button
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.menu.handle_event(event)
        
        assert self.menu._selected_option == 'host'
        assert result is None  # Doesn't return action yet
    
    def test_join_button_shows_panel(self):
        """Test that clicking join button shows connection panel."""
        join_button = self.menu._buttons['join']
        center = join_button.center
        
        # Simulate click
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.menu.handle_event(event)
        
        assert self.menu._selected_option == 'join'
        assert result is None
    
    def test_ip_input_accepts_valid_chars(self):
        """Test that IP input accepts valid characters."""
        # Open join panel and activate IP input
        self.menu._selected_option = 'join'
        self.menu._active_input = 'ip'
        self.menu._ip_input = ""
        
        # Type valid IP characters
        for char in "192.168.1.1":
            event = pygame.event.Event(pygame.KEYDOWN, {'key': 0, 'unicode': char})
            self.menu.handle_event(event)
        
        assert self.menu._ip_input == "192.168.1.1"
    
    def test_ip_input_rejects_invalid_chars(self):
        """Test that IP input rejects invalid characters."""
        self.menu._selected_option = 'join'
        self.menu._active_input = 'ip'
        self.menu._ip_input = ""
        
        # Try to type invalid characters
        invalid_chars = "abcXYZ!@#"
        for char in invalid_chars:
            event = pygame.event.Event(pygame.KEYDOWN, {'key': 0, 'unicode': char})
            self.menu.handle_event(event)
        
        # IP should still be empty
        assert self.menu._ip_input == ""
    
    def test_port_input_accepts_digits(self):
        """Test that port input accepts digits."""
        self.menu._selected_option = 'host'
        self.menu._active_input = 'port'
        self.menu._port_input = ""
        
        # Type digits
        for char in "54321":
            event = pygame.event.Event(pygame.KEYDOWN, {'key': 0, 'unicode': char})
            self.menu.handle_event(event)
        
        assert self.menu._port_input == "54321"
    
    def test_port_input_rejects_letters(self):
        """Test that port input rejects non-digit characters."""
        self.menu._selected_option = 'host'
        self.menu._active_input = 'port'
        self.menu._port_input = ""
        
        # Try to type letters
        for char in "abc":
            event = pygame.event.Event(pygame.KEYDOWN, {'key': 0, 'unicode': char})
            self.menu.handle_event(event)
        
        # Port should still be empty
        assert self.menu._port_input == ""
    
    def test_escape_closes_panels(self):
        """Test that ESC closes connection panels."""
        # Open join panel
        self.menu._selected_option = 'join'
        
        # Press ESC
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE, 'unicode': ''})
        result = self.menu.handle_event(event)
        
        assert self.menu._selected_option is None
        assert result is None
    
    def test_escape_quits_from_main(self):
        """Test that ESC quits from main menu."""
        # Not in a panel
        self.menu._selected_option = None
        
        # Press ESC
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_ESCAPE, 'unicode': ''})
        result = self.menu.handle_event(event)
        
        assert result == 'quit'
    
    def test_get_connection_info(self):
        """Test getting connection info from input fields."""
        self.menu._ip_input = "192.168.1.100"
        self.menu._port_input = "9999"
        
        ip, port = self.menu.get_connection_info()
        
        assert ip == "192.168.1.100"
        assert port == 9999
    
    def test_get_connection_info_validates_port(self):
        """Test that get_connection_info validates port range."""
        self.menu._ip_input = "127.0.0.1"
        self.menu._port_input = "99999"  # Invalid port
        
        ip, port = self.menu.get_connection_info()
        
        # Should default to 12345
        assert port == 12345
    
    def test_get_connection_info_handles_empty_port(self):
        """Test that get_connection_info handles empty port."""
        self.menu._port_input = ""
        
        ip, port = self.menu.get_connection_info()
        
        # Should default to 12345
        assert port == 12345
    
    def test_set_status(self):
        """Test setting status messages."""
        self.menu.set_status("Connected!", is_error=False)
        
        assert self.menu._status_message == "Connected!"
        assert self.menu._status_color == (100, 255, 100)
    
    def test_set_status_error(self):
        """Test setting error status messages."""
        self.menu.set_status("Connection failed", is_error=True)
        
        assert self.menu._status_message == "Connection failed"
        assert self.menu._status_color == (255, 100, 100)
    
    def test_backspace_removes_chars(self):
        """Test that backspace removes characters from input."""
        self.menu._selected_option = 'join'
        self.menu._active_input = 'ip'
        self.menu._ip_input = "192.168"
        
        # Press backspace
        event = pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_BACKSPACE, 'unicode': ''})
        self.menu.handle_event(event)
        
        assert self.menu._ip_input == "192.16"
    
    def test_single_player_button(self):
        """Test clicking single player button."""
        single_button = self.menu._buttons['single']
        center = single_button.center
        
        # Simulate click
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.menu.handle_event(event)
        
        assert result == 'single'
    
    def test_quit_button(self):
        """Test clicking quit button."""
        quit_button = self.menu._buttons['quit']
        center = quit_button.center
        
        # Simulate click
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.menu.handle_event(event)
        
        assert result == 'quit'
    
    def test_codex_button_exists(self):
        """Test that the Codex button exists in the main menu."""
        assert 'codex' in self.menu._buttons
    
    def test_codex_button_opens_panel(self):
        """Test that clicking Codex button returns 'codex' action."""
        codex_button = self.menu._buttons['codex']
        center = codex_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': center})
        result = self.menu.handle_event(event)
        assert result == 'codex'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
